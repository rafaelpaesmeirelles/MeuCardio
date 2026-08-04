import re
from datetime import datetime, timedelta, timezone

from fastapi import APIRouter, Depends, HTTPException, Query
from fastapi.responses import Response
from pydantic import BaseModel, Field
from sqlalchemy.orm import Session

from app.core.config import settings
from app.core.db import get_db
from app.core.security import current_user
from app.models.audit import AuditLog
from app.models.clinical_docs import DocumentTemplate, GeneratedDocument
from app.models.compartilhamento import DocumentShareLink
from app.models.round import Patient
from app.services import cofre
from app.services.assinatura import emissao as assinatura_emissao
from app.services.notificar import tentar_enviar_email
from app.services.professional_profile import (
    document_identity, normalize_search_text, professional_name,
)

router = APIRouter(prefix="/api/document-templates", tags=["documentos"])

VALIDADE_LINK_DIAS = 7


class TemplateIn(BaseModel):
    title: str
    doc_type: str  # atestado | laudo | outro
    body: str


def _dump_template(t: DocumentTemplate) -> dict:
    return {"id": t.id, "title": t.title, "doc_type": t.doc_type, "body": t.body}


@router.get("")
def listar_templates(db: Session = Depends(get_db), user=Depends(current_user)):
    rows = db.query(DocumentTemplate).filter(DocumentTemplate.owner_id == user.id).order_by(DocumentTemplate.title).all()
    return [_dump_template(t) for t in rows]


@router.post("", status_code=201)
def criar_template(dados: TemplateIn, db: Session = Depends(get_db), user=Depends(current_user)):
    if dados.doc_type not in {"atestado", "laudo", "outro"}:
        raise HTTPException(status_code=422, detail="Tipo inválido.")
    t = DocumentTemplate(owner_id=user.id, title=dados.title, doc_type=dados.doc_type, body=dados.body)
    db.add(t)
    db.commit()
    db.refresh(t)
    return _dump_template(t)


@router.put("/{tid}")
def editar_template(tid: int, dados: TemplateIn, db: Session = Depends(get_db), user=Depends(current_user)):
    t = db.get(DocumentTemplate, tid)
    if not t or t.owner_id != user.id:
        raise HTTPException(status_code=404, detail="Template não encontrado.")
    t.title, t.doc_type, t.body = dados.title, dados.doc_type, dados.body
    db.commit()
    return _dump_template(t)


@router.delete("/{tid}", status_code=204)
def apagar_template(tid: int, db: Session = Depends(get_db), user=Depends(current_user)):
    db.query(DocumentTemplate).filter(DocumentTemplate.id == tid, DocumentTemplate.owner_id == user.id).delete()
    db.commit()


class GerarDocumentoIn(BaseModel):
    template_id: int
    patient_id: int | None = None
    variables: dict[str, str] = {}
    patient_name: str | None = None
    # 'residencial' | 'profissional' | None — mesma escolha do receituário
    # (Tarefa 29), gravada aqui porque o PDF é gerado sob demanda depois
    # (GET .../pdf, ou pelo link público) e precisa sair sempre igual.
    #
    # Método de assinatura (Tarefa 4) NÃO entra aqui: `GeneratedDocument`
    # nasce só como texto renderizado — quem usa `PatientDocumentos.tsx`
    # nem chega a baixar PDF, só imprime `rendered_body` pelo navegador. O
    # método é escolhido em `GET .../pdf`, no primeiro download de fato, que
    # é quando o documento passa a existir como PDF.
    endereco: str | None = None


@router.post("/gerar", status_code=201)
def gerar_documento(dados: GerarDocumentoIn, db: Session = Depends(get_db), user=Depends(current_user)):
    t = db.get(DocumentTemplate, dados.template_id)
    if not t or t.owner_id != user.id:
        raise HTTPException(status_code=404, detail="Template não encontrado.")

    if dados.patient_id is not None:
        p = db.get(Patient, dados.patient_id)
        if not p or p.created_by != user.id:
            raise HTTPException(status_code=404, detail="Paciente não encontrado.")

    if dados.endereco not in (None, "residencial", "profissional"):
        raise HTTPException(status_code=422, detail="endereco precisa ser 'residencial', 'profissional' ou omitido.")

    corpo = t.body
    faltando = []
    for variavel in set(re.findall(r"\{\{(\w+)\}\}", corpo)):
        valor = dados.variables.get(variavel)
        if valor is None or valor == "":
            faltando.append(variavel)
        else:
            corpo = corpo.replace(f"{{{{{variavel}}}}}", valor)
    if faltando:
        raise HTTPException(status_code=422, detail=f"Faltam variáveis: {', '.join(faltando)}")

    gerado = GeneratedDocument(
        patient_id=dados.patient_id, template_id=t.id, created_by=user.id,
        doc_type=t.doc_type, title=t.title, rendered_body=corpo,
        endereco_exibido=dados.endereco, variables=dados.variables,
    )
    db.add(gerado)
    db.flush()
    nome_paciente = (dados.patient_name or dados.variables.get("nome_paciente") or
                     dados.variables.get("paciente") or dados.variables.get("nome") or "").strip()
    if nome_paciente:
        gerado.patient_name_cifrado = cofre.cifrar_campo(nome_paciente, gerado.id)
    db.commit()
    db.refresh(gerado)
    return {
        "id": gerado.id, "title": gerado.title, "doc_type": gerado.doc_type,
        "rendered_body": gerado.rendered_body, "created_at": gerado.created_at,
        # `document_logo_url` — mesmo par logo pessoal + logo Corvia que o
        # PDF do backend já desenha (`pdf_documento.py`), agora também no
        # cabeçalho de impressão pelo navegador (`CabecalhoDocumento.tsx`).
        "patient_name": nome_paciente or None,
        "medico": document_identity(user),
    }


def _obter_gerado(gid: int, db: Session, user) -> GeneratedDocument:
    """Resolve documento clínico sem bypass administrativo entre locatários."""
    g = db.get(GeneratedDocument, gid)
    if not g or g.created_by != user.id:
        raise HTTPException(status_code=404, detail="Documento não encontrado.")
    return g


@router.get("/gerados")
def listar_gerados(
    nome: str | None = Query(None, max_length=120),
    tipo: str | None = Query(None, max_length=30),
    db: Session = Depends(get_db), user=Depends(current_user),
):
    rows = (
        db.query(GeneratedDocument)
        .filter(GeneratedDocument.created_by == user.id)
        .order_by(GeneratedDocument.created_at.desc())
        .limit(500)
        .all()
    )
    busca = normalize_search_text(nome)
    resultado = []
    for g in rows:
        patient_name = None
        if g.patient_name_cifrado:
            patient_name = cofre.decifrar_campo(g.patient_name_cifrado, g.id)
        if busca and busca not in normalize_search_text(patient_name):
            continue
        if tipo and g.doc_type != tipo:
            continue
        resultado.append({
            "id": g.id, "title": g.title, "doc_type": g.doc_type,
            "created_at": g.created_at, "patient_name": patient_name,
        })
    return resultado


@router.get("/gerados/{gid}")
def obter_gerado(gid: int, db: Session = Depends(get_db), user=Depends(current_user)):
    g = _obter_gerado(gid, db, user)
    return {
        "id": g.id, "title": g.title, "doc_type": g.doc_type,
        "rendered_body": g.rendered_body, "created_at": g.created_at,
        "tem_email_destinatario": g.destinatario_email_cifrado is not None,
        # `template_id`/`variables` (Tarefa 4) — pra "recriar baseado neste":
        # o frontend reabre o MESMO modelo com os MESMOS valores pré-
        # preenchidos, em vez de começar do zero. `variables` só existe pra
        # documento gerado depois desta tarefa; nulo pros anteriores.
        "template_id": g.template_id, "variables": g.variables,
        "patient_name": cofre.decifrar_campo(g.patient_name_cifrado, g.id) if g.patient_name_cifrado else None,
    }


@router.get("/gerados/{gid}/pdf")
def baixar_pdf_gerado(gid: int, metodo: str = "MANUAL", db: Session = Depends(get_db),
                      user=Depends(current_user)):
    """Primeiro download de fato EMITE o documento (Tarefa 4): escolhe o
    método de assinatura, gera o PDF e persiste — downloads seguintes servem
    exatamente os mesmos bytes, ignorando `metodo`, porque o documento já
    foi emitido (mesma semântica de uma vez só que a receita tem via
    `status`, só que aqui não existe esse campo — quem marca "já emitido" é
    a própria existência do `DocumentoEmitido`)."""
    from app.services.pdf_documento import documento_generico, resolver_endereco

    g = _obter_gerado(gid, db, user)

    existente = assinatura_emissao.buscar(db, tipo=assinatura_emissao.TIPO_DOCUMENTO, referencia_id=g.id)
    if existente is not None:
        pdf = assinatura_emissao.ler_bytes(existente)
        return Response(content=pdf, media_type="application/pdf", headers={
            "Content-Disposition": f'inline; filename="documento-{g.id}.pdf"'})

    try:
        provedor, info_metodo = assinatura_emissao.preparar(metodo)
    except assinatura_emissao.MetodoInvalido as e:
        raise HTTPException(status_code=422, detail=str(e)) from e

    disponivel, motivo = provedor.disponivel()
    if not disponivel:
        raise HTTPException(status_code=409, detail={
            "erro": "Emissão indisponível.", "bloqueios": [motivo], "nada_foi_simulado": True,
        })

    # A resolução de propriedade acima garante que o emissor é o próprio
    # usuário autenticado. Não existe mais leitura administrativa transversal
    # de documentos clínicos entre médicos.
    emissor = user
    medico = document_identity(emissor)
    titulo = {"atestado": "Atestado", "laudo": "Laudo"}.get(g.doc_type, g.title)
    # `g.created_at`, não `datetime.now()`: se esta rota for chamada mais de
    # uma vez antes de conseguir persistir (ex.: primeira tentativa recusada
    # por provedor indisponível), o PDF ainda sai determinístico.
    pdf_visual = documento_generico(
        titulo=titulo, corpo=g.rendered_body, medico=medico,
        endereco=resolver_endereco(emissor, g.endereco_exibido),
        data_emissao=g.created_at, metodo_assinatura=metodo, provedor_nome=info_metodo.nome,
    )
    emitido = assinatura_emissao.assinar_e_persistir(
        db, tipo=assinatura_emissao.TIPO_DOCUMENTO, referencia_id=g.id, metodo=metodo,
        provedor=provedor, info=info_metodo, pdf_visual=pdf_visual, medico=medico,
        criado_por=g.created_by, data_emissao=g.created_at,
    )
    # `documents.py` não auditava emissão nenhuma até aqui — assimetria com
    # `receituario.py`, corrigida junto da Tarefa 4.
    db.add(AuditLog(user_id=user.id, action="emitir_documento_gerado",
                    entity="generated_document", entity_id=str(g.id),
                    detail={"doc_type": g.doc_type, "bytes": len(emitido.pdf),
                            "metodo": metodo, "sha256": emitido.registro.sha256}))
    db.commit()
    return Response(content=emitido.pdf, media_type="application/pdf", headers={
        "Content-Disposition": f'inline; filename="documento-{g.id}.pdf"'})


class EnviarEmailIn(BaseModel):
    email: str = Field(min_length=5)


@router.post("/gerados/{gid}/enviar-email")
def enviar_email_gerado(gid: int, dados: EnviarEmailIn, db: Session = Depends(get_db), user=Depends(current_user)):
    """Manda ao paciente um link, nunca o PDF anexado. A rota exige ser o
    próprio autor do documento e não admite bypass administrativo."""
    g = db.get(GeneratedDocument, gid)
    if not g or g.created_by != user.id:
        raise HTTPException(status_code=404, detail="Documento não encontrado.")

    g.destinatario_email_cifrado = cofre.cifrar_campo(dados.email, g.id)

    link = DocumentShareLink(
        tipo="generated_document", referencia_id=g.id, criado_por=user.id,
        expires_at=datetime.now(timezone.utc) + timedelta(days=VALIDADE_LINK_DIAS),
    )
    db.add(link)
    db.commit()
    db.refresh(link)

    url = f"{settings.public_url}/api/documentos-publicos/{link.token}"
    enviado = tentar_enviar_email(
        destinatario=dados.email,
        assunto="Corvia — documento do seu médico disponível",
        corpo=(
            f"{professional_name(user)} disponibilizou um documento para você na Corvia.\n\n"
            f"Acesse pelo link abaixo (válido por {VALIDADE_LINK_DIAS} dias): {url}\n\n"
            f"Este link é pessoal — não compartilhe."
        ),
    )
    return {"enviado": enviado, "link": None if enviado else url}
