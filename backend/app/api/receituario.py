# -*- coding: utf-8 -*-
"""Receituário (Tarefa 27) — da intenção clínica aos documentos a emitir.

O desenho está em `controlados/DESENHO.md`. O que estas rotas fazem, e o que
deliberadamente **não** fazem:

- **Fazem** classificar o que foi prescrito, agrupar por tipo exigido e criar um
  `PrescriptionDocument` por grupo, com as pendências à vista.
- **Não** emitem nada. Numeração depende do cadastro do prescritor no SNCR, e
  assinatura depende da credencial VIDAAS — as duas pendentes. Nenhuma das duas
  é simulada aqui; a rota de emissão recusa e diz por quê.

O médico **não escolhe** o tipo de receituário. Ele revisa a classificação e, se
discordar, corrige com motivo registrado — que é o que permite descobrir depois
que uma regra está errada.
"""
from fastapi import APIRouter, Depends, HTTPException, Query
from fastapi.responses import Response
from datetime import datetime, timedelta, timezone
from pydantic import BaseModel, Field
from sqlalchemy.orm import Session

from app.core.config import settings
from app.core.db import get_db
from app.core.security import current_user
from app.models.audit import AuditLog
from app.models.clinical_docs import Prescription
from app.models.compartilhamento import DocumentShareLink
from app.models.drug import Drug
from app.models.receituario import (
    ControlledSubstance, PrescriptionDocument, PrescriptionRecipient,
    PrescriptionRule, PrescriptionType,
)
from app.services import cofre
from app.services.assinatura import emissao as assinatura_emissao
from app.services.classificacao_receituario import (
    ItemPrescrito, Regra, Substancia, classificar, normalizar,
)
from app.services.notificar import tentar_enviar_email
from app.services.professional_profile import document_identity, professional_name

router = APIRouter(prefix="/api/receituario", tags=["receituário"])

# Validade do link enviado ao paciente. Não é uso único de propósito (ver
# DocumentShareLink) — só a janela de tempo controla o acesso.
VALIDADE_LINK_DIAS = 7


# ------------------------------------------------------------------ schemas --
class ItemIn(BaseModel):
    """`drug_slug` é o caminho correto: ele resolve a substância na base
    estruturada. `descricao` livre é aceita para não travar o médico, mas cai
    em pendência — texto livre não é classificável, e chutar aqui emitiria o
    documento errado.

    Os seis campos abaixo são a Tarefa B (CLAUDE.md): escolha de marca via
    CMED, sempre opcional e sempre explícita do médico — nunca preenchida
    sozinha aqui. `pmc_snapshot`/`uf`/`cmed_version` gravam o preço vigente
    NO MOMENTO da prescrição, porque a lista da CMED muda todo mês e um
    relatório antigo não pode recalcular com preço novo. Ausência dos seis
    (genérico puro, sem marca) continua sendo o caminho padrão e válido."""
    drug_slug: str | None = None
    descricao: str = ""
    apresentacao: str = ""
    posologia: str = ""
    orientacao: str = ""
    brand_name: str | None = None
    manufacturer: str | None = None
    ggrem: str | None = None
    pmc_snapshot: float | None = None
    uf: str | None = None
    cmed_version: str | None = None


class DestinatarioIn(BaseModel):
    nome: str = Field(min_length=3, max_length=200)
    endereco: str | None = None
    documento: str | None = None


class ReceituarioIn(BaseModel):
    patient_id: int | None = None
    destinatario: DestinatarioIn
    itens: list[ItemIn] = Field(min_length=1)
    observacoes: str = ""


class RevisaoIn(BaseModel):
    confirmar: bool = True
    corrigir_para: str | None = None
    motivo: str | None = None


# ------------------------------------------------------------------ apoio --
def _carregar_regras(db: Session) -> tuple[dict[str, Substancia], list[Regra], str | None]:
    """Lê a versão mais recente das listas. Uma receita precisa poder dizer qual
    versão a classificou, por isso a versão volta junto e é gravada no documento."""
    versao = db.query(ControlledSubstance.fonte_versao).order_by(
        ControlledSubstance.id.desc()).limit(1).scalar()
    subs = {
        s.nome_normalizado: Substancia(s.nome, s.lista, s.tipo_sncr, s.proscrita)
        for s in db.query(ControlledSubstance).filter(
            ControlledSubstance.fonte_versao == versao).all()
    }
    regras = [
        Regra(r.lista, r.texto_normativo, r.tipo_resultante, r.codificada, r.condicao or {})
        for r in db.query(PrescriptionRule).filter(PrescriptionRule.fonte_versao == versao).all()
    ]
    return subs, regras, versao


def _resolver(db: Session, itens: list[ItemIn]) -> list[ItemPrescrito]:
    """Traduz o pedido em itens classificáveis. A substância vem do cadastro do
    medicamento, nunca do que foi digitado."""
    fora = []
    for i in itens:
        substancia = None
        apresentacao = i.apresentacao
        if i.drug_slug:
            d = db.query(Drug).filter(Drug.slug == i.drug_slug).first()
            if d:
                substancia = d.generic_name
                if not apresentacao and d.presentations:
                    apresentacao = d.presentations[0]
        fora.append(ItemPrescrito(
            descricao=i.descricao or (substancia or i.drug_slug or "item sem descrição"),
            substancia=substancia, apresentacao=apresentacao or None,
            posologia=i.posologia or None,
        ))
    return fora


def _tipos(db: Session) -> dict[str, PrescriptionType]:
    return {t.codigo: t for t in db.query(PrescriptionType).all()}


def _doc_json(doc: PrescriptionDocument, tipo: PrescriptionType | None) -> dict:
    return {
        "id": doc.id, "tipo": doc.tipo_codigo,
        "tipo_nome": tipo.nome if tipo else None,
        "cor": tipo.cor if tipo else None,
        "vias": tipo.vias if tipo else None,
        "exige_retencao": tipo.exige_retencao if tipo else None,
        "tipo_ativo": tipo.ativo if tipo else False,
        "numeracao": doc.numeracao, "status": doc.status,
        "itens": doc.itens, "pendencias": doc.pendencias,
        "classificacao_corrigida_de": doc.classificacao_corrigida_de,
        "motivo_correcao": doc.motivo_correcao,
        "fonte_versao_listas": doc.fonte_versao_listas,
    }


# ------------------------------------------------------------------ rotas --
@router.get("/tipos")
def listar_tipos(db: Session = Depends(get_db), _=Depends(current_user)):
    """`ativo` falso não é erro: é o controle especial esperando o SNCR abrir e
    a assinatura digital existir. A interface deve mostrar, não esconder."""
    return [{
        "codigo": t.codigo, "nome": t.nome, "cor": t.cor, "vias": t.vias,
        "destinacao_vias": t.destinacao_vias, "exige_retencao": t.exige_retencao,
        "exige_numeracao_sncr": t.exige_numeracao_sncr, "ativo": t.ativo,
    } for t in db.query(PrescriptionType).order_by(PrescriptionType.id).all()]


@router.post("/classificar")
def classificar_previa(dados: ReceituarioIn, db: Session = Depends(get_db),
                       _=Depends(current_user)):
    """Prévia sem gravar nada. Existe para a tela mostrar, enquanto o médico
    monta a receita, quantos documentos vão sair e o que ficou pendente — antes
    de ele descobrir isso no fim."""
    subs, regras, versao = _carregar_regras(db)
    r = classificar(_resolver(db, dados.itens), subs, regras)
    tipos = _tipos(db)
    return {
        "versao_listas": versao,
        "exige_revisao": r.exige_revisao,
        "documentos": [{
            "tipo": d.tipo,
            "tipo_nome": tipos[d.tipo].nome if d.tipo in tipos else None,
            "tipo_ativo": tipos[d.tipo].ativo if d.tipo in tipos else False,
            "itens": [i.descricao for i in d.itens],
            "pendencias": d.pendencias,
        } for d in r.documentos],
        "recusados": [{"item": x.item.descricao, "motivo": x.motivo} for x in r.recusados],
    }


@router.post("", status_code=201)
def criar(dados: ReceituarioIn, db: Session = Depends(get_db), user=Depends(current_user)):
    subs, regras, versao = _carregar_regras(db)
    resultado = classificar(_resolver(db, dados.itens), subs, regras)

    if resultado.recusados:
        # Substância proscrita não gera receita nenhuma, nem parcial.
        raise HTTPException(status_code=422, detail={
            "erro": "A receita contém substância proscrita e não pode ser criada.",
            "itens": [{"item": x.item.descricao, "motivo": x.motivo} for x in resultado.recusados],
        })

    presc = Prescription(
        patient_id=dados.patient_id, created_by=user.id, notes=dados.observacoes,
        items=[i.model_dump() for i in dados.itens],
    )
    db.add(presc)
    db.flush()

    d = dados.destinatario
    db.add(PrescriptionRecipient(
        prescription_id=presc.id,
        nome_cifrado=cofre.cifrar_campo(d.nome, presc.id),
        endereco_cifrado=cofre.cifrar_campo(d.endereco, presc.id) if d.endereco else None,
        documento_cifrado=cofre.cifrar_campo(d.documento, presc.id) if d.documento else None,
    ))

    criados = []
    for plano in resultado.documentos:
        doc = PrescriptionDocument(
            prescription_id=presc.id, tipo_codigo=plano.tipo,
            itens=[{"descricao": i.descricao, "substancia": i.substancia,
                    "apresentacao": i.apresentacao, "posologia": i.posologia,
                    # `lista` (ex.: "C5") não é usado hoje — a emissão de RCE
                    # continua bloqueada — mas é dado que já existe em
                    # `ItemClassificado` sem custo de consulta extra, e vai
                    # ser exatamente o que a Lei 9.965/2000 (anabolizantes)
                    # precisa pra saber quando exigir CPF/telefone/CID do
                    # prescritor. Ver CLAUDE.md/DESENHO.md.
                    "lista": i.lista}
                   for i in plano.itens],
            pendencias=plano.pendencias, fonte_versao_listas=versao,
        )
        db.add(doc)
        criados.append(doc)

    db.add(AuditLog(user_id=user.id, action="criar_receituario", entity="prescription",
                    entity_id=str(presc.id),
                    detail={"documentos": [d_.tipo_codigo for d_ in criados],
                            "exige_revisao": resultado.exige_revisao,
                            "versao_listas": versao}))
    db.commit()

    tipos = _tipos(db)
    return {"prescricao_id": presc.id, "exige_revisao": resultado.exige_revisao,
            "documentos": [_doc_json(x, tipos.get(x.tipo_codigo)) for x in criados]}


@router.get("")
def listar(
    nome: str | None = Query(None, max_length=120),
    tipo: str | None = Query(None, max_length=20),
    db: Session = Depends(get_db), user=Depends(current_user),
):
    prescricoes = (
        db.query(Prescription)
        .filter(Prescription.created_by == user.id)
        .order_by(Prescription.created_at.desc())
        .limit(500)
        .all()
    )
    busca = (nome or "").strip().casefold()
    tipos = _tipos(db)
    resultado = []
    for presc in prescricoes:
        dest = db.query(PrescriptionRecipient).filter(
            PrescriptionRecipient.prescription_id == presc.id).first()
        patient_name = cofre.decifrar_campo(dest.nome_cifrado, presc.id) if dest else None
        if busca and busca not in (patient_name or "").casefold():
            continue
        docs = db.query(PrescriptionDocument).filter(
            PrescriptionDocument.prescription_id == presc.id).all()
        if tipo and not any(d.tipo_codigo == tipo for d in docs):
            continue
        resultado.append({
            "prescricao_id": presc.id, "criado_em": presc.created_at,
            "paciente_nome": patient_name,
            "documentos": [{"tipo": d.tipo_codigo, "tipo_nome": tipos[d.tipo_codigo].nome
                            if d.tipo_codigo in tipos else None, "status": d.status}
                           for d in docs],
        })
    if resultado:
        db.add(AuditLog(user_id=user.id, action="listar_receituarios", entity="prescription",
                        detail={"count": len(resultado), "filtro_nome": bool(nome), "filtro_tipo": tipo}))
        db.commit()
    return resultado


@router.get("/{prescricao_id}")
def obter(prescricao_id: int, db: Session = Depends(get_db), user=Depends(current_user)):
    presc = db.get(Prescription, prescricao_id)
    if not presc or presc.created_by != user.id:
        raise HTTPException(status_code=404, detail="Prescrição não encontrada.")

    dest = db.query(PrescriptionRecipient).filter(
        PrescriptionRecipient.prescription_id == presc.id).first()
    # Toda leitura de dado identificável de paciente vai para a auditoria, do
    # mesmo jeito que a leitura de exame no Cofre.
    destinatario = {"nome": None, "endereco": None, "documento": None}
    if dest:
        destinatario["nome"] = cofre.decifrar_campo(dest.nome_cifrado, presc.id)
        if dest.endereco_cifrado:
            destinatario["endereco"] = cofre.decifrar_campo(dest.endereco_cifrado, presc.id)
        if dest.documento_cifrado:
            destinatario["documento"] = cofre.decifrar_campo(dest.documento_cifrado, presc.id)
        db.add(AuditLog(user_id=user.id, action="ler_destinatario_receita",
                        entity="prescription", entity_id=str(presc.id)))
        db.commit()

    docs = db.query(PrescriptionDocument).filter(
        PrescriptionDocument.prescription_id == presc.id).all()
    tipos = _tipos(db)
    return {"prescricao_id": presc.id, "destinatario": destinatario,
            "observacoes": presc.notes,
            # Formato cru de `ItemIn` (Tarefa 4) — usado pelo frontend pra
            # "recriar baseado nesta": melhor fonte que os `itens` já
            # classificados por documento, porque uma receita com listas
            # diferentes vira mais de um `PrescriptionDocument` e o cru é
            # um só, no formato exato que `POST ""` espera de volta.
            "itens_originais": presc.items,
            "documentos": [_doc_json(x, tipos.get(x.tipo_codigo)) for x in docs]}


@router.post("/documentos/{documento_id}/revisar")
def revisar(documento_id: int, dados: RevisaoIn, db: Session = Depends(get_db),
            user=Depends(current_user)):
    """O checkpoint humano. Confirmar não muda o tipo; corrigir muda, e exige
    motivo — sem o motivo não há como descobrir depois que uma regra de adendo
    está mal codificada."""
    doc = db.get(PrescriptionDocument, documento_id)
    if not doc:
        raise HTTPException(status_code=404, detail="Documento não encontrado.")
    presc = db.get(Prescription, doc.prescription_id)
    if not presc or presc.created_by != user.id:
        raise HTTPException(status_code=404, detail="Documento não encontrado.")
    if doc.status == "emitido":
        raise HTTPException(status_code=409, detail="Documento já emitido não pode ser revisado.")

    if dados.corrigir_para:
        if not dados.motivo:
            raise HTTPException(status_code=422,
                                detail="Corrigir a classificação exige motivo.")
        if not db.query(PrescriptionType).filter(
                PrescriptionType.codigo == dados.corrigir_para).first():
            raise HTTPException(status_code=422,
                                detail=f"Tipo desconhecido: {dados.corrigir_para}")
        doc.classificacao_corrigida_de = doc.tipo_codigo
        doc.tipo_codigo = dados.corrigir_para
        doc.motivo_correcao = dados.motivo

    doc.status = "revisado"
    doc.pendencias = []
    db.add(AuditLog(user_id=user.id, action="revisar_documento_receita",
                    entity="prescription_document", entity_id=str(doc.id),
                    detail={"corrigido_de": doc.classificacao_corrigida_de,
                            "para": doc.tipo_codigo, "motivo": doc.motivo_correcao}))
    db.commit()
    return _doc_json(doc, _tipos(db).get(doc.tipo_codigo))


class EmitirIn(BaseModel):
    # 'residencial' | 'profissional' | None (nenhum endereço no PDF) —
    # escolha do médico a cada emissão (Tarefa 29, decisão do Rafael em
    # 30/07/2026: privacidade, nem todo médico quer endereço de casa
    # impresso num papel que o paciente leva embora).
    endereco: str | None = None
    # Código do catálogo em `services/assinatura/catalogo.py` (Tarefa 4).
    # "MANUAL" (carimbo e assinatura do próprio punho) é o único que funciona
    # de verdade hoje — os demais existem no catálogo e recusam com motivo.
    metodo: str = "MANUAL"


@router.post("/documentos/{documento_id}/emitir")
def emitir(documento_id: int, dados: EmitirIn = EmitirIn(), db: Session = Depends(get_db),
          user=Depends(current_user)):
    """Recusa e explica, em vez de simular.

    Emitir exige o tipo ligado e, se o tipo exigir, numeração do SNCR — as
    duas ainda pendentes para tudo que não é receituário comum. Assinatura
    digital (Tarefa 4) já é uma escolha real: `dados.metodo` no catálogo de
    `services/assinatura/catalogo.py`, com "MANUAL" (carimbo e assinatura do
    próprio punho) sendo o único que funciona hoje — qualquer outro método
    recusa aqui, com motivo, exatamente como SNCR/RCE.
    """
    doc = db.get(PrescriptionDocument, documento_id)
    if not doc:
        raise HTTPException(status_code=404, detail="Documento não encontrado.")
    presc = db.get(Prescription, doc.prescription_id)
    if not presc or presc.created_by != user.id:
        raise HTTPException(status_code=404, detail="Documento não encontrado.")

    try:
        provedor, info_metodo = assinatura_emissao.preparar(dados.metodo)
    except assinatura_emissao.MetodoInvalido as e:
        raise HTTPException(status_code=422, detail=str(e)) from e

    tipo = _tipos(db).get(doc.tipo_codigo)
    bloqueios = []
    if doc.status != "revisado":
        bloqueios.append("O documento precisa ser revisado antes de emitido.")
    if not tipo or not tipo.ativo:
        bloqueios.append(
            f"O tipo {doc.tipo_codigo} está desligado: depende da integração com o "
            f"SNCR, que a Anvisa disponibiliza até 30/09/2026, e do layout oficial "
            f"(fixo, publicado pela Anvisa) ainda não reproduzido. Não depende mais "
            f"da assinatura digital — o método MANUAL já funciona para qualquer tipo."
        )
    if tipo and tipo.exige_numeracao_sncr and not doc.numeracao:
        bloqueios.append(
            "Este tipo exige numeração do SNCR, e o prescritor precisa estar "
            "cadastrado no sistema da Anvisa para obtê-la."
        )
    disponivel, motivo_indisponivel = provedor.disponivel()
    if not disponivel:
        bloqueios.append(motivo_indisponivel)
    if bloqueios:
        raise HTTPException(status_code=409, detail={
            "erro": "Emissão indisponível.", "bloqueios": bloqueios,
            "nada_foi_simulado": True,
        })

    # Só o receituário comum é desenhado. Notificação de Receita e Receita de
    # Controle Especial têm modelo oficial de layout fixo publicado pela Anvisa,
    # e reproduzi-lo de memória geraria formulário parecido e inválido.
    if doc.tipo_codigo != "COMUM":
        raise HTTPException(status_code=501, detail={
            "erro": f"O modelo oficial do tipo {doc.tipo_codigo} ainda não foi reproduzido.",
            "motivo": "Layout fixo publicado pela Anvisa; desenhar de memória "
                      "produziria documento inválido com aparência de válido.",
        })

    if dados.endereco not in (None, "residencial", "profissional"):
        raise HTTPException(status_code=422, detail="endereco precisa ser 'residencial', 'profissional' ou omitido.")

    from app.services.pdf_documento import receituario_comum, resolver_endereco

    dest = db.query(PrescriptionRecipient).filter(
        PrescriptionRecipient.prescription_id == presc.id).first()
    destinatario = {}
    if dest:
        destinatario["nome"] = cofre.decifrar_campo(dest.nome_cifrado, presc.id)
        if dest.endereco_cifrado:
            destinatario["endereco"] = cofre.decifrar_campo(dest.endereco_cifrado, presc.id)

    endereco_medico = resolver_endereco(user, dados.endereco)
    medico = document_identity(user)
    data_emissao = datetime.now(timezone.utc)
    pdf_visual = receituario_comum(
        destinatario=destinatario, itens=doc.itens, observacoes=presc.notes or "",
        medico=medico, endereco=endereco_medico, data_emissao=data_emissao,
        metodo_assinatura=dados.metodo, provedor_nome=info_metodo.nome,
    )
    emitido = assinatura_emissao.assinar_e_persistir(
        db, tipo=assinatura_emissao.TIPO_RECEITA, referencia_id=doc.id, metodo=dados.metodo,
        provedor=provedor, info=info_metodo, pdf_visual=pdf_visual, medico=medico,
        criado_por=user.id, data_emissao=data_emissao,
    )

    doc.status = "emitido"
    doc.emitido_em = data_emissao
    doc.endereco_exibido = dados.endereco if endereco_medico else None
    db.add(AuditLog(user_id=user.id, action="emitir_documento_receita",
                    entity="prescription_document", entity_id=str(doc.id),
                    detail={"tipo": doc.tipo_codigo, "bytes": len(emitido.pdf),
                            "metodo": dados.metodo, "sha256": emitido.registro.sha256}))
    db.commit()
    return Response(content=emitido.pdf, media_type="application/pdf", headers={
        "Content-Disposition": f'inline; filename="receituario-{doc.id}.pdf"'})


class EnviarEmailIn(BaseModel):
    email: str = Field(min_length=5)


@router.post("/documentos/{documento_id}/enviar-email")
def enviar_email(documento_id: int, dados: EnviarEmailIn, db: Session = Depends(get_db),
                 user=Depends(current_user)):
    """Manda ao paciente um LINK, nunca o PDF anexado — decisão do Rafael em
    30/07/2026: a receita é dado clínico, e a caixa de e-mail (CorvIA Mail)
    tem termo LGPD que proíbe justamente isso. O link é servido por
    `app/api/documentos_publicos.py`, sem passar pela Zoho em nenhum ponto.
    """
    doc = db.get(PrescriptionDocument, documento_id)
    if not doc:
        raise HTTPException(status_code=404, detail="Documento não encontrado.")
    presc = db.get(Prescription, doc.prescription_id)
    if not presc or presc.created_by != user.id:
        raise HTTPException(status_code=404, detail="Documento não encontrado.")
    if doc.status != "emitido":
        raise HTTPException(status_code=409, detail="Só é possível enviar um documento já emitido.")

    dest = db.query(PrescriptionRecipient).filter(
        PrescriptionRecipient.prescription_id == presc.id).first()
    if not dest:
        raise HTTPException(status_code=409, detail="Destinatário da receita não encontrado.")
    dest.email_cifrado = cofre.cifrar_campo(dados.email, presc.id)

    link = DocumentShareLink(
        tipo="prescription_document", referencia_id=doc.id, criado_por=user.id,
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

    db.add(AuditLog(user_id=user.id, action="enviar_email_documento_receita",
                    entity="prescription_document", entity_id=str(doc.id),
                    detail={"enviado": enviado}))
    db.commit()

    # Sem SMTP configurado, `enviado` vem falso — mesma situação já tratada
    # em `esqueci_senha` (password_reset.py). Ali um admin repassa o link de
    # reset manualmente; aqui é o próprio médico quem tem essa autoridade
    # sobre o paciente dele, então devolvemos o link pra ele copiar e mandar
    # por outro canal (WhatsApp, telefone), em vez de só um erro sem saída.
    return {"enviado": enviado, "link": None if enviado else url}
