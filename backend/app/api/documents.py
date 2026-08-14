import asyncio
import re
from datetime import date, datetime, timedelta, timezone
from typing import Literal

from fastapi import APIRouter, Depends, File, HTTPException, Query, UploadFile
from fastapi.responses import Response
from pydantic import BaseModel, Field, model_validator
from sqlalchemy.orm import Session

from app.core.config import settings
from app.core.db import get_db
from app.core.security import assinatura_email_ativa, current_user
from app.core.uploads import UploadRejected, validate_file
from app.models.audit import AuditLog
from app.models.clinical_docs import DocumentTemplate, GeneratedDocument
from app.models.compartilhamento import DocumentShareLink
from app.models.email_account import EmailAccount
from app.models.patient_document_email_send import (
    CANAL_AUTO_CONTATO_CORVIA, CANAL_PROPRIO_CORVIA_MAIL, TIPO_DOCUMENTO_GERADO,
    PatientDocumentEmailSend,
)
from app.services import anexo_email_proprio, cofre, documentos_avulsos, emails, envio_documento_email
from app.services import patient_profile_service
from app.services.assinatura import divulgacao_email
from app.services.clinical_ownership import patient_for_user
from app.services.assinatura import emissao as assinatura_emissao
from app.services.professional_profile import (
    document_identity, normalize_search_text, professional_name,
)

router = APIRouter(prefix="/api/document-templates", tags=["documentos"])
VALIDADE_LINK_DIAS = 7

# Tipos de `GeneratedDocument.doc_type` que NÃO vêm de um `DocumentTemplate`
# (12/08/2026 — Solicitar exames / Documento em branco). "atestado" para o
# atalho rápido de atestado continua usando o mesmo valor que os modelos já
# usavam (`DOC_TYPE_ATESTADO`) — o que diferencia um atestado emitido por
# modelo de um emitido pelo atalho é `template_id` ser `None`, não o tipo.
DOC_TYPE_ATESTADO = "atestado"
DOC_TYPE_SOLICITACAO_EXAMES = "solicitacao_exames"
DOC_TYPE_DOCUMENTO_LIVRE = "documento_livre"

# Título impresso no PDF (cabeçalho central, ver `_cabecalho` em
# `pdf_documento.py`) por `doc_type` — documento sem entrada aqui usa
# `g.title` (é o caso do documento em branco, cujo título É o corpo do
# título escolhido pelo médico na hora de emitir).
_TITULOS_DOC_TYPE = {
    "atestado": "Atestado",
    "laudo": "Laudo",
    DOC_TYPE_SOLICITACAO_EXAMES: documentos_avulsos.TITULO_SOLICITACAO_EXAMES,
}


class TemplateIn(BaseModel):
    title: str
    doc_type: str
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
    endereco: str | None = None
    # Acrescentados em 12/08/2026 (seleção de paciente universal + "modelo
    # é ponto de partida editável, nunca documento final imutável"):
    # `patient_profile_id` puxa o cadastro reutilizável (ver
    # `app.services.patient_profile_service`); `corpo_final`, quando
    # presente e não vazio, é o texto que o médico efetivamente revisou/
    # editou na tela antes de gerar — substitui por inteiro o resultado da
    # substituição de `{{variavel}}` no corpo do MODELO salvo. O modelo em
    # si (`DocumentTemplate.body`) nunca é alterado por este campo — é
    # só o que vai para ESTE documento gerado.
    patient_profile_id: int | None = None
    corpo_final: str | None = None


@router.post("/gerar", status_code=201)
def gerar_documento(dados: GerarDocumentoIn, db: Session = Depends(get_db), user=Depends(current_user)):
    t = db.get(DocumentTemplate, dados.template_id)
    if not t or t.owner_id != user.id:
        raise HTTPException(status_code=404, detail="Template não encontrado.")

    if dados.patient_id is not None:
        patient_for_user(dados.patient_id, db, user)

    if dados.endereco not in (None, "residencial", "profissional"):
        raise HTTPException(status_code=422, detail="endereco precisa ser 'residencial', 'profissional' ou omitido.")

    nome_paciente_perfil, snapshot, profile_id = patient_profile_service.resolver_paciente_documento(
        db, user, patient_profile_id=dados.patient_profile_id, patient_name_avulso=dados.patient_name,
    )

    if dados.corpo_final is not None and dados.corpo_final.strip():
        # O médico já revisou/editou o texto na tela (Tarefa de 12/08/2026,
        # "modelo é ponto de partida, nunca documento final imutável") —
        # este é o texto que vale, sem passar pela substituição de
        # `{{variavel}}` de novo (ela já rodou no cliente para montar a
        # prévia editável). O modelo salvo nunca é tocado aqui.
        corpo = dados.corpo_final
    else:
        variaveis_disponiveis = {
            **patient_profile_service.variaveis_paciente(snapshot),
            **{k: v for k, v in dados.variables.items() if v not in (None, "")},
        }
        corpo = t.body
        faltando = []
        for variavel in set(re.findall(r"\{\{(\w+)\}\}", corpo)):
            valor = variaveis_disponiveis.get(variavel)
            # Variável `paciente_*` nunca bloqueia a geração por estar
            # vazia — o cadastro do paciente pode genuinamente não ter
            # aquele dado (ex.: sem CPF cadastrado); ela só entra "faltando"
            # se não for uma variável de paciente reconhecida.
            if (valor is None or valor == "") and variavel not in patient_profile_service.NOMES_VARIAVEIS_PACIENTE:
                faltando.append(variavel)
            else:
                corpo = corpo.replace(f"{{{{{variavel}}}}}", valor or "")
        if faltando:
            raise HTTPException(status_code=422, detail=f"Faltam variáveis: {', '.join(faltando)}")

    gerado = GeneratedDocument(
        patient_id=dados.patient_id, template_id=t.id, created_by=user.id,
        doc_type=t.doc_type, title=t.title, rendered_body=corpo,
        endereco_exibido=dados.endereco, variables=dados.variables,
        patient_profile_id=profile_id,
    )
    db.add(gerado)
    db.flush()
    nome_paciente = (nome_paciente_perfil or dados.patient_name or dados.variables.get("nome_paciente") or
                     dados.variables.get("paciente") or dados.variables.get("nome") or "").strip()
    if nome_paciente:
        gerado.patient_name_cifrado = cofre.cifrar_campo(nome_paciente, gerado.id)
    if snapshot:
        gerado.patient_snapshot_cifrado = patient_profile_service.cifrar_snapshot(snapshot, gerado.id)
    db.commit()
    db.refresh(gerado)
    return {
        "id": gerado.id, "title": gerado.title, "doc_type": gerado.doc_type,
        "rendered_body": gerado.rendered_body, "created_at": gerado.created_at,
        "patient_name": nome_paciente or None,
        "patient_profile_id": profile_id,
        "medico": document_identity(user),
    }


def _persistir_gerado(
    db: Session, user, *, doc_type: str, title: str, corpo: str,
    endereco: str | None, patient_name: str | None, patient_profile_id: int | None, variables: dict,
    audit_action: str, audit_detail: dict,
) -> dict:
    """Ponto único de gravação dos três caminhos de entrada SEM modelo
    (solicitação de exames, atestado rápido, documento em branco) — mesma
    forma de resposta de `gerar_documento`, `template_id=None` é o que
    distingue estes de um documento gerado a partir de `DocumentTemplate`.
    Resolve o paciente (cadastro reutilizável OU nome avulso) pelo mesmo
    ponto único que o fluxo de modelo usa — ver
    `patient_profile_service.resolver_paciente_documento`."""
    if endereco not in (None, "residencial", "profissional"):
        raise HTTPException(status_code=422, detail="endereco precisa ser 'residencial', 'profissional' ou omitido.")

    nome_paciente_resolvido, snapshot, profile_id = patient_profile_service.resolver_paciente_documento(
        db, user, patient_profile_id=patient_profile_id, patient_name_avulso=patient_name,
    )

    gerado = GeneratedDocument(
        patient_id=None, template_id=None, created_by=user.id,
        doc_type=doc_type, title=title, rendered_body=corpo,
        endereco_exibido=endereco, variables=variables,
        patient_profile_id=profile_id,
    )
    db.add(gerado)
    db.flush()
    nome_paciente = (nome_paciente_resolvido or "").strip()
    if nome_paciente:
        gerado.patient_name_cifrado = cofre.cifrar_campo(nome_paciente, gerado.id)
    if snapshot:
        gerado.patient_snapshot_cifrado = patient_profile_service.cifrar_snapshot(snapshot, gerado.id)
    db.add(AuditLog(
        user_id=user.id, action=audit_action, entity="generated_document",
        entity_id=str(gerado.id), detail=audit_detail,
    ))
    db.commit()
    db.refresh(gerado)
    return {
        "id": gerado.id, "title": gerado.title, "doc_type": gerado.doc_type,
        "rendered_body": gerado.rendered_body, "created_at": gerado.created_at,
        "patient_name": nome_paciente or None,
        "patient_profile_id": profile_id,
        "medico": document_identity(user),
    }


@router.get("/exames-sugeridos")
def exames_sugeridos(user=Depends(current_user)):
    """Lista estática de sugestão para o campo de exame da solicitação —
    NUNCA um catálogo fechado, ver `app.services.documentos_avulsos`. O
    campo sempre aceita texto livre além destas opções."""
    return documentos_avulsos.EXAMES_SUGERIDOS


class SolicitacaoExamesIn(BaseModel):
    patient_name: str | None = None
    patient_profile_id: int | None = None
    exames: list[str] = Field(min_length=1)
    indicacao: str | None = None
    cid: str | None = None
    prioridade: Literal["rotina", "urgente"] = "rotina"
    observacoes: str | None = None
    endereco: str | None = None
    # Texto que o médico revisou/editou na tela antes de gerar (mesma ideia
    # de `GerarDocumentoIn.corpo_final`) — quando presente, substitui o
    # corpo composto automaticamente a partir dos campos estruturados
    # acima. Os campos estruturados continuam sendo gravados em
    # `variables`, para "recriar baseado neste" reabrir o formulário certo.
    corpo_final: str | None = None


@router.post("/gerar-exames", status_code=201)
def gerar_solicitacao_exames(
    dados: SolicitacaoExamesIn, db: Session = Depends(get_db), user=Depends(current_user),
):
    """Solicitação de exames avulsa — sem exigir `DocumentTemplate` prévio
    (pedido do Rafael, 12/08/2026). `exames` sempre aceita item digitado
    livremente, além da lista de sugestão de `/exames-sugeridos`."""
    exames = [e.strip() for e in dados.exames if e and e.strip()]
    if not exames:
        raise HTTPException(status_code=422, detail="Informe ao menos um exame.")

    indicacao = (dados.indicacao or "").strip() or None
    cid = (dados.cid or "").strip() or None
    observacoes = (dados.observacoes or "").strip() or None
    patient_name = (dados.patient_name or "").strip() or None

    corpo = documentos_avulsos.montar_corpo_solicitacao_exames(
        exames=exames, indicacao=indicacao, cid=cid,
        prioridade=dados.prioridade, observacoes=observacoes, patient_name=patient_name,
    )
    if dados.corpo_final is not None and dados.corpo_final.strip():
        corpo = dados.corpo_final
    return _persistir_gerado(
        db, user, doc_type=DOC_TYPE_SOLICITACAO_EXAMES, title=documentos_avulsos.TITULO_SOLICITACAO_EXAMES,
        corpo=corpo, endereco=dados.endereco, patient_name=patient_name,
        patient_profile_id=dados.patient_profile_id,
        variables={
            "exames": exames, "indicacao": indicacao, "cid": cid,
            "prioridade": dados.prioridade, "observacoes": observacoes,
            "patient_name": patient_name,
        },
        audit_action="gerar_solicitacao_exames",
        audit_detail={"quantidade_exames": len(exames), "prioridade": dados.prioridade},
    )


class AtestadoRapidoIn(BaseModel):
    patient_name: str | None = None
    patient_profile_id: int | None = None
    dias_afastamento: int | None = Field(default=None, ge=1, le=365)
    data_inicio: date | None = None
    data_fim: date | None = None
    cid: str | None = None
    observacoes: str | None = None
    endereco: str | None = None
    corpo_final: str | None = None

    @model_validator(mode="after")
    def _valida_periodo(self):
        if not self.dias_afastamento and not (self.data_inicio and self.data_fim):
            raise ValueError(
                "Informe a quantidade de dias de afastamento (com data de início opcional) "
                "ou um período completo (data de início e data de fim)."
            )
        if self.data_inicio and self.data_fim and self.data_fim < self.data_inicio:
            raise ValueError("A data final não pode ser anterior à data inicial.")
        return self


@router.post("/gerar-atestado", status_code=201)
def gerar_atestado_rapido(
    dados: AtestadoRapidoIn, db: Session = Depends(get_db), user=Depends(current_user),
):
    """Atalho de "Emitir atestado médico" — o mesmo documento que um modelo
    de atestado geraria, sem exigir que o médico crie o modelo antes. Usa o
    mesmo `doc_type` ("atestado") dos modelos; `template_id=None` é o que
    diferencia este caminho na hora de "recriar baseado neste"."""
    cid = (dados.cid or "").strip() or None
    observacoes = (dados.observacoes or "").strip() or None
    patient_name = (dados.patient_name or "").strip() or None

    corpo = documentos_avulsos.montar_corpo_atestado(
        patient_name=patient_name, dias_afastamento=dados.dias_afastamento,
        data_inicio=dados.data_inicio, data_fim=dados.data_fim,
        cid=cid, observacoes=observacoes,
    )
    if dados.corpo_final is not None and dados.corpo_final.strip():
        corpo = dados.corpo_final
    return _persistir_gerado(
        db, user, doc_type=DOC_TYPE_ATESTADO, title="Atestado médico",
        corpo=corpo, endereco=dados.endereco, patient_name=patient_name,
        patient_profile_id=dados.patient_profile_id,
        variables={
            "dias_afastamento": dados.dias_afastamento,
            "data_inicio": dados.data_inicio.isoformat() if dados.data_inicio else None,
            "data_fim": dados.data_fim.isoformat() if dados.data_fim else None,
            "cid": cid, "observacoes": observacoes, "patient_name": patient_name,
        },
        audit_action="gerar_atestado_rapido",
        audit_detail={"dias_afastamento": dados.dias_afastamento},
    )


class DocumentoLivreIn(BaseModel):
    titulo: str = Field(min_length=1, max_length=200)
    corpo: str = Field(min_length=1)
    patient_name: str | None = None
    patient_profile_id: int | None = None
    endereco: str | None = None


@router.post("/gerar-livre", status_code=201)
def gerar_documento_livre(
    dados: DocumentoLivreIn, db: Session = Depends(get_db), user=Depends(current_user),
):
    """Documento em branco — só título + corpo em texto livre (o campo
    `corpo` JÁ É o "conteúdo final editável": não há builder automático
    a sobrepor, o médico controla o texto por inteiro desde o início).
    Paciente opcional. Não cria `DocumentTemplate` nenhum (é emissão
    avulsa e imediata; "salvar como modelo" fica para uma rodada futura)."""
    patient_name = (dados.patient_name or "").strip() or None
    return _persistir_gerado(
        db, user, doc_type=DOC_TYPE_DOCUMENTO_LIVRE, title=dados.titulo.strip(),
        corpo=dados.corpo, endereco=dados.endereco, patient_name=patient_name,
        patient_profile_id=dados.patient_profile_id,
        variables={"titulo": dados.titulo.strip(), "corpo": dados.corpo, "patient_name": patient_name},
        audit_action="gerar_documento_livre",
        audit_detail={"titulo": dados.titulo.strip()},
    )


def _obter_gerado(gid: int, db: Session, user) -> GeneratedDocument:
    g = db.get(GeneratedDocument, gid)
    if not g or g.created_by != user.id:
        raise HTTPException(status_code=404, detail="Documento não encontrado.")
    return g


@router.get("/gerados")
def listar_gerados(
    nome: str | None = Query(None, max_length=120),
    tipo: str | None = Query(None, max_length=30),
    page: int = Query(1, ge=1),
    page_size: int = Query(20, ge=1, le=100),
    db: Session = Depends(get_db), user=Depends(current_user),
):
    """Pesquisa o acervo cifrado completo do titular e só então pagina."""
    rows = (
        db.query(GeneratedDocument)
        .filter(GeneratedDocument.created_by == user.id)
        .order_by(GeneratedDocument.created_at.desc())
        .all()
    )
    busca = normalize_search_text(nome)
    filtrados = []
    for g in rows:
        patient_name = None
        if g.patient_name_cifrado:
            patient_name = cofre.decifrar_campo(g.patient_name_cifrado, g.id)
        if busca and busca not in normalize_search_text(patient_name):
            continue
        if tipo and g.doc_type != tipo:
            continue
        filtrados.append({
            "id": g.id, "title": g.title, "doc_type": g.doc_type,
            "created_at": g.created_at, "patient_name": patient_name,
        })

    inicio = (page - 1) * page_size
    items = filtrados[inicio:inicio + page_size]
    has_more = inicio + page_size < len(filtrados)
    if not getattr(user, "investidor", False):
        db.add(AuditLog(
            user_id=user.id, action="listar_documentos_gerados", entity="generated_document",
            detail={
                "count": len(items), "total_filtrado": len(filtrados),
                "filtro_nome": bool(nome), "filtro_tipo": tipo,
                "page": page, "page_size": page_size,
            },
        ))
        db.commit()
    return {
        "items": items,
        "page": page,
        "page_size": page_size,
        "has_more": has_more,
        "total": len(filtrados),
    }


@router.get("/gerados/{gid}")
def obter_gerado(gid: int, db: Session = Depends(get_db), user=Depends(current_user)):
    g = _obter_gerado(gid, db, user)
    return {
        "id": g.id, "title": g.title, "doc_type": g.doc_type,
        "rendered_body": g.rendered_body, "created_at": g.created_at,
        "tem_email_destinatario": g.destinatario_email_cifrado is not None,
        "template_id": g.template_id, "variables": g.variables,
        "patient_name": cofre.decifrar_campo(g.patient_name_cifrado, g.id) if g.patient_name_cifrado else None,
        # Acrescentados em 12/08/2026: `patient_profile_id` é o atalho de
        # navegação (nulo se o cadastro foi apagado depois, ou se o
        # documento nunca teve paciente cadastrado). `patient_snapshot` é
        # o dado CONGELADO no momento da emissão — nunca uma releitura
        # ao vivo de `PatientProfile` — usado tanto na prévia "Dados do
        # paciente utilizados neste documento" quanto em "recriar baseado
        # neste".
        "patient_profile_id": g.patient_profile_id,
        "patient_snapshot": patient_profile_service.decifrar_snapshot(g.patient_snapshot_cifrado, g.id),
    }


@router.get("/gerados/{gid}/pdf")
def baixar_pdf_gerado(gid: int, metodo: str = "MANUAL", db: Session = Depends(get_db),
                      user=Depends(current_user)):
    from app.services.pdf_documento import documento_generico, resolver_endereco

    g = _obter_gerado(gid, db, user)
    existente = assinatura_emissao.buscar(db, tipo=assinatura_emissao.TIPO_DOCUMENTO, referencia_id=g.id)
    if existente is not None:
        pdf = assinatura_emissao.ler_bytes(existente)
        return Response(content=pdf, media_type="application/pdf", headers={
            "Content-Disposition": f'inline; filename="documento-{g.id}.pdf"'})

    try:
        provedor, info_metodo = assinatura_emissao.preparar(metodo, db=db, user=user)
    except assinatura_emissao.MetodoInvalido as e:
        raise HTTPException(status_code=422, detail=str(e)) from e

    disponivel, motivo = provedor.disponivel()
    if not disponivel:
        raise HTTPException(status_code=409, detail={
            "erro": "Emissão indisponível.", "bloqueios": [motivo], "nada_foi_simulado": True,
        })

    emissor = user
    medico = document_identity(emissor)
    titulo = _TITULOS_DOC_TYPE.get(g.doc_type, g.title)
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
    db.add(AuditLog(user_id=user.id, action="emitir_documento_gerado",
                    entity="generated_document", entity_id=str(g.id),
                    detail={"doc_type": g.doc_type, "bytes": len(emitido.pdf),
                            "metodo": metodo, "sha256": emitido.registro.sha256}))
    db.commit()
    return Response(content=emitido.pdf, media_type="application/pdf", headers={
        "Content-Disposition": f'inline; filename="documento-{g.id}.pdf"'})


TAMANHO_MAXIMO_PDF_ASSINADO = 15 * 1024 * 1024  # 15 MB — PDF assinado, folga sobre o original


@router.post("/gerados/{gid}/assinatura-externa")
async def enviar_assinatura_externa(
    gid: int, arquivo: UploadFile = File(...),
    db: Session = Depends(get_db), user=Depends(current_user),
):
    """Fecha o fluxo do Assinador ITI/gov.br (Trabalho 14) para documento
    gerado por modelo (atestado/laudo) — mesma lógica de
    `receituario.py::enviar_assinatura_externa`."""
    g = _obter_gerado(gid, db, user)

    conteudo = await arquivo.read(TAMANHO_MAXIMO_PDF_ASSINADO + 1)
    if len(conteudo) > TAMANHO_MAXIMO_PDF_ASSINADO:
        raise HTTPException(status_code=413, detail="O arquivo assinado precisa ter no máximo 15 MB.")
    if not conteudo:
        raise HTTPException(status_code=422, detail="Envie o arquivo assinado.")
    try:
        validate_file(conteudo, arquivo.filename or "documento-assinado.pdf", "exam")
    except UploadRejected as erro:
        raise HTTPException(status_code=erro.status_code, detail=erro.detail) from None
    if not conteudo.startswith(b"%PDF-"):
        raise HTTPException(
            status_code=422,
            detail="O Assinador gov.br devolve um PDF assinado — envie esse arquivo, não uma imagem.",
        )

    try:
        # Ver o comentário equivalente em receituario.py: `verificacao_pdf.
        # verificar()` chama `asyncio.run()` por dentro (pyhanko) — precisa
        # rodar numa thread própria quando a rota é `async def`.
        emitido = await asyncio.to_thread(
            assinatura_emissao.concluir_assinatura_externa,
            db, tipo=assinatura_emissao.TIPO_DOCUMENTO, referencia_id=g.id,
            pdf_assinado=conteudo, criado_por=user.id,
        )
    except assinatura_emissao.AssinaturaNaoDetectada as e:
        raise HTTPException(status_code=422, detail=str(e)) from e
    except assinatura_emissao.FluxoAssinaturaExternaInvalido as e:
        raise HTTPException(status_code=409, detail=str(e)) from e

    db.add(AuditLog(
        user_id=user.id, action="concluir_assinatura_externa_documento_gerado",
        entity="generated_document", entity_id=str(g.id),
        detail={"sha256": emitido.registro.sha256, "bytes": len(emitido.pdf)},
    ))
    db.commit()
    return {"assinado": True, "assinado_em": emitido.registro.assinado_em}


class EnviarEmailIn(BaseModel):
    email: str = Field(min_length=5)
    assinar_smime: bool = False


@router.post("/gerados/{gid}/enviar-email")
def enviar_email_gerado(gid: int, dados: EnviarEmailIn, db: Session = Depends(get_db), user=Depends(current_user)):
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

    # Divulgação da assinatura só aparece se o documento FOI assinado com
    # certificado A1 (nível "qualificada") — diferente do receituário, esta
    # rota não exige isso: `GeneratedDocument` também aceita o método
    # MANUAL (sem assinatura), e continuar permitindo enviá-lo por e-mail é
    # o comportamento já existente, não alterado aqui.
    emitido = assinatura_emissao.buscar(db, tipo=assinatura_emissao.TIPO_DOCUMENTO, referencia_id=g.id)
    divulgacao = None
    if emitido and emitido.assinado_em is not None and emitido.nivel == "qualificada":
        divulgacao = divulgacao_email.texto_divulgacao(assinatura_emissao.ler_bytes(emitido))

    url = f"{settings.public_url}/api/documentos-publicos/{link.token}"
    html = emails.montar_html_documento_disponivel(
        nome_medico=professional_name(user), url=url, dias_validade=VALIDADE_LINK_DIAS,
        divulgacao_assinatura=divulgacao,
    )
    resultado = envio_documento_email.enviar(
        db, user, destinatario=dados.email, assunto=emails.ASSUNTO_DOCUMENTO_DISPONIVEL,
        corpo_html=html, assinar_smime=dados.assinar_smime,
    )
    db.add(AuditLog(user_id=user.id, action="enviar_email_documento_gerado",
                    entity="generated_document", entity_id=str(g.id),
                    detail={"enviado": resultado.enviado, "erro": resultado.erro,
                            "assinado_smime": resultado.assinado_smime}))
    db.commit()
    # Nunca joga fora o link em caso de falha de envio — o médico sem
    # CorvIA Mail ativo (nem outra conta conectada como padrão) esbarra
    # aqui direto, e precisa de um jeito de mandar o documento por fora
    # (WhatsApp, SMS...). Comportamento restaurado do que já existia antes
    # desta ampliação; `resultado.erro` some do payload de sucesso.
    return {
        "enviado": resultado.enviado,
        "link": None if resultado.enviado else url,
        "erro": None if resultado.enviado else resultado.erro,
        "assinado_smime": resultado.assinado_smime,
    }


class EnvioPacienteIn(BaseModel):
    email_paciente: str = Field(min_length=5)
    canal: Literal["auto_contato_corvia", "proprio_corvia_mail"]


def _checar_corvia_mail_ativo(db: Session, user) -> EmailAccount:
    if not assinatura_email_ativa(db, user):
        raise HTTPException(status_code=409, detail="Este recurso exige CorvIA Mail ativo.")
    conta = db.query(EmailAccount).filter(EmailAccount.user_id == user.id).first()
    if not conta or conta.status != "ativa":
        raise HTTPException(status_code=409, detail="Sua caixa do CorvIA Mail não está ativa.")
    return conta


@router.post("/gerados/{gid}/envio-paciente")
def envio_paciente_gerado(
    gid: int, dados: EnvioPacienteIn, db: Session = Depends(get_db), user=Depends(current_user),
):
    """Oferta de envio ao paciente por e-mail ao concluir a assinatura
    digital (pedido do Rafael, 08/08/2026) — dois canais, ver
    `app/models/patient_document_email_send.py`:

    - `auto_contato_corvia`: a Corvia manda sozinha, pela conta institucional
      (SMTP, link seguro de `VALIDADE_LINK_DIAS`, nunca o PDF anexado).
    - `proprio_corvia_mail`: sobe o PDF assinado como anexo na caixa nativa
      do próprio médico (Mail360) e devolve o `file_id` — o frontend navega
      para o compositor do CorvIA Mail já com o anexo, destinatário e uma
      sugestão de corpo (a confirmação da assinatura, quando aplicável)."""
    g = _obter_gerado(gid, db, user)
    _checar_corvia_mail_ativo(db, user)

    registro = assinatura_emissao.buscar(db, tipo=assinatura_emissao.TIPO_DOCUMENTO, referencia_id=g.id)
    if not registro or registro.assinado_em is None:
        raise HTTPException(
            status_code=409,
            detail="Conclua a emissão/assinatura do documento antes de enviá-lo ao paciente.",
        )
    divulgacao = None
    if registro.nivel == "qualificada":
        divulgacao = divulgacao_email.texto_divulgacao(assinatura_emissao.ler_bytes(registro))

    g.destinatario_email_cifrado = cofre.cifrar_campo(dados.email_paciente, g.id)
    titulo = _TITULOS_DOC_TYPE.get(g.doc_type, g.title)

    if dados.canal == CANAL_AUTO_CONTATO_CORVIA:
        link = DocumentShareLink(
            tipo="generated_document", referencia_id=g.id, criado_por=user.id,
            expires_at=datetime.now(timezone.utc) + timedelta(days=VALIDADE_LINK_DIAS),
        )
        db.add(link)
        db.commit()
        db.refresh(link)

        url = f"{settings.public_url}/api/documentos-publicos/{link.token}"
        html = emails.montar_html_documento_disponivel(
            nome_medico=professional_name(user), url=url, dias_validade=VALIDADE_LINK_DIAS,
            divulgacao_assinatura=divulgacao,
        )
        resultado = emails.enviar_institucional_paciente(
            db, user_id=user.id, destinatario=dados.email_paciente,
            assunto=emails.ASSUNTO_DOCUMENTO_DISPONIVEL, html=html,
            tipo_log="documento_paciente_auto",
        )
        db.add(PatientDocumentEmailSend(
            tipo_origem=TIPO_DOCUMENTO_GERADO, referencia_id=g.id, canal=dados.canal,
            share_link_id=link.id, enviado_por=user.id,
            paciente_email_cifrado=cofre.cifrar_campo(dados.email_paciente, g.id),
            assinatura_confirmada=divulgacao is not None, sucesso=resultado.enviado,
        ))
        db.add(AuditLog(
            user_id=user.id, action="envio_paciente_documento_gerado", entity="generated_document",
            entity_id=str(g.id),
            detail={"canal": dados.canal, "enviado": resultado.enviado, "erro": resultado.erro},
        ))
        db.commit()
        return {
            "canal": dados.canal, "enviado": resultado.enviado, "erro": resultado.erro,
            "anexo": None, "assunto_sugerido": None, "corpo_sugerido": None,
        }

    assert dados.canal == CANAL_PROPRIO_CORVIA_MAIL  # só resta este valor no Literal
    nome_arquivo = f"{normalize_search_text(titulo).replace(' ', '-')}-{g.id}.pdf"
    try:
        anexo = anexo_email_proprio.preparar(
            db, user, nome_arquivo=nome_arquivo, conteudo=assinatura_emissao.ler_bytes(registro),
        )
    except anexo_email_proprio.AnexoIndisponivel as e:
        raise HTTPException(status_code=502, detail=str(e)) from e

    db.add(PatientDocumentEmailSend(
        tipo_origem=TIPO_DOCUMENTO_GERADO, referencia_id=g.id, canal=dados.canal,
        share_link_id=None, enviado_por=user.id,
        paciente_email_cifrado=cofre.cifrar_campo(dados.email_paciente, g.id),
        assinatura_confirmada=divulgacao is not None, sucesso=True,
    ))
    db.add(AuditLog(
        user_id=user.id, action="envio_paciente_documento_gerado", entity="generated_document",
        entity_id=str(g.id), detail={"canal": dados.canal, "anexo_file_id": anexo.file_id},
    ))
    db.commit()
    return {
        "canal": dados.canal, "enviado": None, "erro": None,
        "anexo": {"file_id": anexo.file_id, "nome": anexo.nome},
        "assunto_sugerido": f"{titulo} do seu médico — Corvia",
        "corpo_sugerido": divulgacao or "",
    }
