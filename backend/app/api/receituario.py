# -*- coding: utf-8 -*-
"""Receituário — classificação, persistência, revisão e emissão."""
import asyncio
from collections import defaultdict
from datetime import datetime, timedelta, timezone
from typing import Literal

from fastapi import APIRouter, Depends, File, HTTPException, Query, UploadFile
from fastapi.responses import Response
from pydantic import BaseModel, Field
from sqlalchemy.orm import Session

from app.core.config import settings
from app.core.db import get_db
from app.core.security import assinatura_email_ativa, current_user
from app.core.uploads import UploadRejected, validate_file
from app.models.audit import AuditLog
from app.models.assinatura import DocumentoEmitido
from app.models.clinical_docs import Prescription
from app.models.cmed import CmedApresentacao
from app.models.compartilhamento import DocumentShareLink
from app.models.drug import Drug
from app.models.email_account import EmailAccount
from app.models.patient_document_email_send import (
    CANAL_AUTO_CONTATO_CORVIA, CANAL_PROPRIO_CORVIA_MAIL, TIPO_RECEITA as TIPO_ORIGEM_RECEITA,
    PatientDocumentEmailSend,
)
from app.models.receituario import (
    ControlledSubstance, PrescriptionDocument, PrescriptionRecipient,
    PrescriptionRule, PrescriptionType,
)
from app.services import anexo_email_proprio, cmed_precos, cofre
from app.services.assinatura import emissao as assinatura_emissao
from app.services.assinatura.provedor import _MANUAL_EXTERNO
from app.services.classificacao_receituario import (
    ItemPrescrito, Regra, Substancia, classificar, normalizar,
)
from app.services.kyc import escopo_profissional
from app.services import emails, envio_documento_email
from app.services.assinatura import divulgacao_email
from app.services.professional_profile import (
    document_identity, normalize_search_text, professional_name,
)

router = APIRouter(prefix="/api/receituario", tags=["receituário"])
VALIDADE_LINK_DIAS = 7


class ItemIn(BaseModel):
    drug_slug: str | None = None
    # Item do catálogo prescritivo amplo (CMED) SEM `Drug` clínico
    # correspondente — id de `cmed_apresentacoes`, nunca texto livre. É a
    # única forma de resolver `substancia` para um item sem `drug_slug`: o
    # cliente nunca manda a substância diretamente (ver `_resolver`), porque
    # texto livre não pode decidir se um item é controlado ou não.
    cmed_apresentacao_id: int | None = None
    descricao: str = ""
    apresentacao: str = ""
    quantidade: str = ""
    quantidade_extenso: str = ""
    posologia: str = ""
    orientacao: str = ""
    uso_continuo: bool = False
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
    cid: str | None = Field(default=None, max_length=10)


class RevisaoIn(BaseModel):
    confirmar: bool = True
    corrigir_para: str | None = None
    motivo: str | None = None


def _carregar_regras(db: Session) -> tuple[dict[str, Substancia], list[Regra], str | None]:
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
    """Resolve substância para regras e mantém intacto o produto escolhido.

    `substancia` é o campo que decide se um item é controlado (Portaria
    344/98) — por isso ela NUNCA vem de texto livre do cliente, só de duas
    fontes resolvidas aqui, no servidor, contra o banco:

    1. `drug_slug` — catálogo clínico (176 fármacos), via `Drug.generic_name`.
    2. `cmed_apresentacao_id` — catálogo prescritivo amplo (qualquer
       apresentação real da CMED, com ou sem `Drug` clínico correspondente),
       via `CmedApresentacao.substancia_cmed`.

    `ItemIn` não tem (e nunca deve ganhar) um campo `substancia` de texto
    livre: se um cliente mandasse isso, bastaria escrever qualquer nome pra
    escapar da classificação de um item que na verdade é controlado. Um item
    sem `drug_slug` válido e sem `cmed_apresentacao_id` válido fica sem
    substância resolvida — `classificar()` já trata isso como pendência de
    revisão humana (recusa/ignora o texto livre), nunca como "não
    controlado" por omissão.
    """
    resolvidos: list[ItemPrescrito] = []
    for i in itens:
        substancia = None
        drug_id = None
        cmed_apresentacao_id = None
        apresentacao = i.apresentacao
        if i.drug_slug:
            d = db.query(Drug).filter(Drug.slug == i.drug_slug).first()
            if d:
                substancia = d.generic_name
                drug_id = d.id
                if not apresentacao and d.presentations:
                    apresentacao = d.presentations[0]
        elif i.cmed_apresentacao_id is not None:
            linha = db.query(CmedApresentacao).filter(
                CmedApresentacao.id == i.cmed_apresentacao_id
            ).first()
            if linha:
                substancia = linha.substancia_cmed
                cmed_apresentacao_id = linha.id
                if not apresentacao:
                    apresentacao = cmed_precos.apresentacao_legivel(linha.apresentacao)
        quantidade = "" if i.uso_continuo else (i.quantidade or "").strip()
        quantidade_extenso = "" if i.uso_continuo else (i.quantidade_extenso or "").strip()
        quantidade_impressa = quantidade
        if quantidade_extenso:
            quantidade_impressa = f"{quantidade} ({quantidade_extenso})" if quantidade else quantidade_extenso
        resolvidos.append(ItemPrescrito(
            descricao=(i.brand_name or i.descricao or (substancia or i.drug_slug or "item sem descrição")),
            substancia=substancia,
            apresentacao=apresentacao or None,
            quantidade=quantidade_impressa or None,
            posologia=i.posologia or None,
            uso_continuo=i.uso_continuo,
            brand_name=(i.brand_name or "").strip() or None,
            manufacturer=(i.manufacturer or "").strip() or None,
            ggrem=(i.ggrem or "").strip() or None,
            pmc_snapshot=i.pmc_snapshot,
            uf=(i.uf or "").strip().upper() or None,
            cmed_version=(i.cmed_version or "").strip() or None,
            drug_id=drug_id,
            cmed_apresentacao_id=cmed_apresentacao_id,
        ))
    return resolvidos


def _bloqueios_de_escopo(db: Session, user, resultado) -> list[dict]:
    """Escopo legal de prescrição por profissão (Tarefa 11, ampliação de
    06/08/2026) — ver `app/services/kyc/escopo_profissional.py`. Roda
    depois da classificação por lista da Portaria 344/98, item a item."""
    escopo = escopo_profissional.escopo_de(user.council_name)
    if escopo == escopo_profissional.ESCOPO_COMPLETO:
        return []
    bloqueios = []
    for plano in resultado.documentos:
        for item in plano.itens:
            avaliado = escopo_profissional.avaliar_item(db, escopo, item.lista, item.drug_id)
            if not avaliado.permitido:
                bloqueios.append({"item": item.descricao, "motivo": avaliado.motivo})
    return bloqueios


def _tipos(db: Session) -> dict[str, PrescriptionType]:
    return {t.codigo: t for t in db.query(PrescriptionType).all()}


def _item_snapshot(item: ItemPrescrito) -> dict:
    snapshot = {
        "descricao": item.descricao,
        "substancia": item.substancia,
        "apresentacao": item.apresentacao,
        "quantidade": item.quantidade,
        "posologia": item.posologia,
        "uso_continuo": item.uso_continuo,
        "lista": item.lista,
        "brand_name": item.brand_name,
        "manufacturer": item.manufacturer,
        "ggrem": item.ggrem,
        "pmc_snapshot": item.pmc_snapshot,
        "uf": item.uf,
        "cmed_version": item.cmed_version,
        # Rastreabilidade da origem: qual dos dois catálogos resolveu a
        # substância deste item. Nunca os dois ao mesmo tempo (`_resolver`
        # só preenche um). Snapshot puro — reimportar a CMED ou editar o
        # `Drug` depois não muda o que já foi impresso/assinado.
        "drug_id": item.drug_id,
        "cmed_apresentacao_id": item.cmed_apresentacao_id,
        "tem_conteudo_clinico": item.drug_id is not None,
    }
    if any((item.brand_name, item.manufacturer, item.ggrem, item.cmed_version, item.pmc_snapshot)):
        snapshot["cmed_snapshot"] = {
            "produto": item.brand_name,
            "apresentacao": item.apresentacao,
            "laboratorio": item.manufacturer,
            "ggrem": item.ggrem,
            "pmc": item.pmc_snapshot,
            "uf": item.uf,
            "versao": item.cmed_version,
        }
    return snapshot


def _doc_json(db: Session, doc: PrescriptionDocument, tipo: PrescriptionType | None) -> dict:
    emitido = (
        db.query(DocumentoEmitido)
        .filter(
            DocumentoEmitido.tipo == assinatura_emissao.TIPO_RECEITA,
            DocumentoEmitido.referencia_id == doc.id,
        )
        .first()
    )
    pode_enviar_email = bool(
        emitido and emitido.assinado_em is not None and emitido.nivel == "qualificada"
    )
    # Trabalho 14: documento emitido por GOVBR/VIDAAS/BIRDID/SAFEID/NEOID/
    # REMOTEID nunca assina nada em `/emitir` (fica "nao_assinado" de
    # propósito) — o médico ainda precisa passar pelo Assinador ITI e
    # reenviar o arquivo. Expor isso aqui, e não só no retorno síncrono do
    # `/emitir`, é o que permite ao frontend mostrar de novo o painel de
    # instruções depois de um F5/nova sessão, em vez de perder o estado.
    aguardando_assinatura_externa = bool(
        emitido and emitido.metodo in _MANUAL_EXTERNO and emitido.assinado_em is None
    )
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
        "cid": doc.cid,
        "pode_enviar_email": pode_enviar_email,
        "aguardando_assinatura_externa": aguardando_assinatura_externa,
        "metodo_emitido": emitido.metodo if emitido else None,
    }


@router.get("/tipos")
def listar_tipos(db: Session = Depends(get_db), _=Depends(current_user)):
    return [{
        "codigo": t.codigo, "nome": t.nome, "cor": t.cor, "vias": t.vias,
        "destinacao_vias": t.destinacao_vias, "exige_retencao": t.exige_retencao,
        "exige_numeracao_sncr": t.exige_numeracao_sncr, "ativo": t.ativo,
    } for t in db.query(PrescriptionType).order_by(PrescriptionType.id).all()]


@router.post("/classificar")
def classificar_previa(dados: ReceituarioIn, db: Session = Depends(get_db),
                       user=Depends(current_user)):
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
        "bloqueados_por_escopo": _bloqueios_de_escopo(db, user, r),
    }


@router.post("", status_code=201)
def criar(dados: ReceituarioIn, db: Session = Depends(get_db), user=Depends(current_user)):
    subs, regras, versao = _carregar_regras(db)
    resultado = classificar(_resolver(db, dados.itens), subs, regras)

    if resultado.recusados:
        raise HTTPException(status_code=422, detail={
            "erro": "A receita contém substância proscrita e não pode ser criada.",
            "itens": [{"item": x.item.descricao, "motivo": x.motivo} for x in resultado.recusados],
        })

    bloqueios_escopo = _bloqueios_de_escopo(db, user, resultado)
    if bloqueios_escopo:
        raise HTTPException(status_code=422, detail={
            "erro": "Um ou mais itens estão fora do escopo legal de prescrição da sua profissão na Corvia.",
            "itens": bloqueios_escopo,
        })

    rce_itens = [
        item for plano in resultado.documentos if plano.tipo == "RCE" for item in plano.itens
    ]
    if rce_itens:
        from app.services.pdf_documento import resolver_endereco
        from app.services.receita_controle_especial import validar_requisitos_rce

        medico_rce = document_identity(user)
        medico_rce["cpf"] = user.cpf
        requisitos = validar_requisitos_rce(
            medico=medico_rce,
            destinatario={
                "nome": dados.destinatario.nome,
                "endereco": dados.destinatario.endereco,
                "documento": dados.destinatario.documento,
            },
            itens=[_item_snapshot(item) for item in rce_itens],
            endereco_profissional=resolver_endereco(user, "profissional"),
            cid=dados.cid,
        )
        if requisitos:
            raise HTTPException(status_code=422, detail={
                "erro": "Complete os campos obrigatórios antes de criar a Receita de Controle Especial.",
                "campos": requisitos,
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
            itens=[_item_snapshot(i) for i in plano.itens],
            pendencias=plano.pendencias, fonte_versao_listas=versao,
            cid=(dados.cid or "").strip() or None,
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
            "documentos": [_doc_json(db, x, tipos.get(x.tipo_codigo)) for x in criados]}


@router.get("")
def listar(
    nome: str | None = Query(None, max_length=120),
    tipo: str | None = Query(None, max_length=20),
    page: int = Query(1, ge=1),
    page_size: int = Query(20, ge=1, le=100),
    db: Session = Depends(get_db), user=Depends(current_user),
):
    """Filtra todo o acervo cifrado do usuário antes de aplicar paginação."""
    prescricoes = (
        db.query(Prescription)
        .filter(Prescription.created_by == user.id)
        .order_by(Prescription.created_at.desc())
        .all()
    )
    ids = [presc.id for presc in prescricoes]
    destinatarios = {
        dest.prescription_id: dest
        for dest in (
            db.query(PrescriptionRecipient)
            .filter(PrescriptionRecipient.prescription_id.in_(ids))
            .all() if ids else []
        )
    }
    documentos_por_prescricao: dict[int, list[PrescriptionDocument]] = defaultdict(list)
    if ids:
        for documento in db.query(PrescriptionDocument).filter(
                PrescriptionDocument.prescription_id.in_(ids)).all():
            documentos_por_prescricao[documento.prescription_id].append(documento)

    busca = normalize_search_text(nome)
    tipos = _tipos(db)
    filtrados = []
    for presc in prescricoes:
        dest = destinatarios.get(presc.id)
        patient_name = cofre.decifrar_campo(dest.nome_cifrado, presc.id) if dest else None
        if busca and busca not in normalize_search_text(patient_name):
            continue
        docs = documentos_por_prescricao.get(presc.id, [])
        if tipo and not any(documento.tipo_codigo == tipo for documento in docs):
            continue
        filtrados.append({
            "prescricao_id": presc.id, "criado_em": presc.created_at,
            "paciente_nome": patient_name,
            "documentos": [{
                "tipo": documento.tipo_codigo,
                "tipo_nome": tipos[documento.tipo_codigo].nome if documento.tipo_codigo in tipos else None,
                "status": documento.status,
            } for documento in docs],
        })

    inicio = (page - 1) * page_size
    items = filtrados[inicio:inicio + page_size]
    has_more = inicio + page_size < len(filtrados)
    # Leitura da conta Investidor deve ser realmente passiva: não persiste
    # telemetria/auditoria. Demais contas mantêm o trilho de auditoria normal.
    if not getattr(user, "investidor", False):
        db.add(AuditLog(
            user_id=user.id, action="listar_receituarios", entity="prescription",
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


@router.get("/{prescricao_id}")
def obter(prescricao_id: int, db: Session = Depends(get_db), user=Depends(current_user)):
    presc = db.get(Prescription, prescricao_id)
    if not presc or presc.created_by != user.id:
        raise HTTPException(status_code=404, detail="Prescrição não encontrada.")

    dest = db.query(PrescriptionRecipient).filter(
        PrescriptionRecipient.prescription_id == presc.id).first()
    destinatario = {"nome": None, "endereco": None, "documento": None}
    if dest:
        destinatario["nome"] = cofre.decifrar_campo(dest.nome_cifrado, presc.id)
        if dest.endereco_cifrado:
            destinatario["endereco"] = cofre.decifrar_campo(dest.endereco_cifrado, presc.id)
        if dest.documento_cifrado:
            destinatario["documento"] = cofre.decifrar_campo(dest.documento_cifrado, presc.id)
        if not getattr(user, "investidor", False):
            db.add(AuditLog(user_id=user.id, action="ler_destinatario_receita",
                            entity="prescription", entity_id=str(presc.id)))
            db.commit()

    docs = db.query(PrescriptionDocument).filter(
        PrescriptionDocument.prescription_id == presc.id).all()
    tipos = _tipos(db)
    return {"prescricao_id": presc.id, "destinatario": destinatario,
            "observacoes": presc.notes,
            "itens_originais": presc.items,
            "documentos": [_doc_json(db, x, tipos.get(x.tipo_codigo)) for x in docs]}


@router.post("/documentos/{documento_id}/revisar")
def revisar(documento_id: int, dados: RevisaoIn, db: Session = Depends(get_db),
            user=Depends(current_user)):
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
            raise HTTPException(status_code=422, detail="Corrigir a classificação exige motivo.")
        if not db.query(PrescriptionType).filter(
                PrescriptionType.codigo == dados.corrigir_para).first():
            raise HTTPException(status_code=422, detail=f"Tipo desconhecido: {dados.corrigir_para}")
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
    return _doc_json(db, doc, _tipos(db).get(doc.tipo_codigo))


class EmitirIn(BaseModel):
    endereco: str | None = None
    metodo: str = "MANUAL"


@router.post("/documentos/{documento_id}/emitir")
def emitir(documento_id: int, dados: EmitirIn = EmitirIn(), db: Session = Depends(get_db),
          user=Depends(current_user)):
    doc = db.get(PrescriptionDocument, documento_id)
    if not doc:
        raise HTTPException(status_code=404, detail="Documento não encontrado.")
    presc = db.get(Prescription, doc.prescription_id)
    if not presc or presc.created_by != user.id:
        raise HTTPException(status_code=404, detail="Documento não encontrado.")

    if dados.endereco not in (None, "residencial", "profissional"):
        raise HTTPException(
            status_code=422,
            detail="endereco precisa ser 'residencial', 'profissional' ou omitido.",
        )

    try:
        provedor, info_metodo = assinatura_emissao.preparar(dados.metodo, db=db, user=user)
    except assinatura_emissao.MetodoInvalido as e:
        raise HTTPException(status_code=422, detail=str(e)) from e

    tipo = _tipos(db).get(doc.tipo_codigo)
    bloqueios: list[str] = []
    if doc.status != "revisado":
        bloqueios.append("O documento precisa ser revisado antes de emitido.")
    if not tipo:
        bloqueios.append(f"Tipo de receita desconhecido: {doc.tipo_codigo}.")
    elif not tipo.ativo:
        bloqueios.append(
            f"O tipo {doc.tipo_codigo} permanece indisponível sem numeração oficial "
            "ou integração SNCR aplicável; nenhum número será simulado."
        )
    if tipo and tipo.exige_numeracao_sncr and not doc.numeracao:
        bloqueios.append(
            "Este tipo exige numeração oficial do SNCR/Vigilância Sanitária; "
            "nenhuma numeração foi atribuída ao documento."
        )
    if doc.tipo_codigo not in {"COMUM", "RCE"}:
        bloqueios.append(
            "A geração deste modelo numerado só será liberada após integração "
            "oficial e validação do número atribuído ao prescritor."
        )
    if doc.tipo_codigo == "RCE" and dados.metodo not in {"MANUAL", "A1_ARQUIVO"}:
        bloqueios.append(
            "A RCE aceita assinatura manual ou assinatura eletrônica qualificada "
            "ICP-Brasil com o certificado A1 conectado à conta."
        )

    disponivel, motivo_indisponivel = provedor.disponivel()
    if not disponivel:
        bloqueios.append(motivo_indisponivel)

    from app.services.pdf_documento import receituario_comum, resolver_endereco

    dest = db.query(PrescriptionRecipient).filter(
        PrescriptionRecipient.prescription_id == presc.id).first()
    destinatario = {"nome": "", "endereco": "", "documento": ""}
    if dest:
        destinatario["nome"] = cofre.decifrar_campo(dest.nome_cifrado, presc.id)
        if dest.endereco_cifrado:
            destinatario["endereco"] = cofre.decifrar_campo(dest.endereco_cifrado, presc.id)
        if dest.documento_cifrado:
            destinatario["documento"] = cofre.decifrar_campo(dest.documento_cifrado, presc.id)

    endereco_medico = resolver_endereco(
        user, "profissional" if doc.tipo_codigo == "RCE" else dados.endereco
    )
    medico = document_identity(user)
    data_emissao = datetime.now(timezone.utc)

    if doc.tipo_codigo == "RCE":
        from app.services.receita_controle_especial import (
            MODELO_VERSAO, receita_controle_especial, validar_requisitos_rce,
        )
        medico_rce = dict(medico)
        medico_rce["cpf"] = user.cpf
        requisitos = validar_requisitos_rce(
            medico=medico_rce, destinatario=destinatario, itens=doc.itens,
            endereco_profissional=endereco_medico, cid=doc.cid,
        )
        bloqueios.extend(requisitos)
    else:
        MODELO_VERSAO = "CORVIA-RECEITUARIO-COMUM"
        medico_rce = medico

    if bloqueios:
        raise HTTPException(status_code=409, detail={
            "erro": "Emissão indisponível.",
            "bloqueios": list(dict.fromkeys(bloqueios)),
            "nada_foi_simulado": True,
        })

    if doc.tipo_codigo == "RCE":
        try:
            pdf_visual = receita_controle_especial(
                destinatario=destinatario, itens=doc.itens,
                observacoes=presc.notes or "", medico=medico_rce,
                endereco_profissional=endereco_medico,
                data_emissao=data_emissao, cid=doc.cid,
            )
        except ValueError as e:
            raise HTTPException(status_code=409, detail={
                "erro": "RCE incompleta.", "bloqueios": str(e).split(" | "),
                "nada_foi_simulado": True,
            }) from e
    else:
        pdf_visual = receituario_comum(
            destinatario=destinatario, itens=doc.itens,
            observacoes=presc.notes or "", medico=medico,
            endereco=endereco_medico, data_emissao=data_emissao,
            metodo_assinatura=dados.metodo, provedor_nome=info_metodo.nome,
        )

    emitido = assinatura_emissao.assinar_e_persistir(
        db, tipo=assinatura_emissao.TIPO_RECEITA, referencia_id=doc.id,
        metodo=dados.metodo, provedor=provedor, info=info_metodo,
        pdf_visual=pdf_visual, medico=medico_rce,
        criado_por=user.id, data_emissao=data_emissao,
    )

    doc.status = "emitido"
    doc.emitido_em = data_emissao
    doc.endereco_exibido = "profissional" if doc.tipo_codigo == "RCE" else (
        dados.endereco if endereco_medico else None
    )
    db.add(AuditLog(
        user_id=user.id, action="emitir_documento_receita",
        entity="prescription_document", entity_id=str(doc.id),
        detail={
            "tipo": doc.tipo_codigo, "bytes": len(emitido.pdf),
            "metodo": dados.metodo, "sha256": emitido.registro.sha256,
            "modelo": MODELO_VERSAO,
            "lista_c5": any(str(i.get("lista") or "").upper() == "C5" for i in doc.itens),
        },
    ))
    db.commit()
    nome_arquivo = (
        f"receita-controle-especial-{doc.id}.pdf"
        if doc.tipo_codigo == "RCE" else f"receituario-{doc.id}.pdf"
    )
    return Response(content=emitido.pdf, media_type="application/pdf", headers={
        "Content-Disposition": f'inline; filename="{nome_arquivo}"',
    })


TAMANHO_MAXIMO_PDF_ASSINADO = 15 * 1024 * 1024  # 15 MB — PDF assinado, folga sobre o original


@router.post("/documentos/{documento_id}/assinatura-externa")
async def enviar_assinatura_externa(
    documento_id: int, arquivo: UploadFile = File(...),
    db: Session = Depends(get_db), user=Depends(current_user),
):
    """Fecha o fluxo do Assinador ITI/gov.br (Trabalho 14): o documento já
    foi emitido com `metodo="GOVBR"` (via `/emitir`, sem assinar nada de
    verdade) e o médico volta aqui com o PDF que assinou fora da Corvia,
    em assinador.iti.br. Nunca aceita o arquivo sem conferir que existe
    uma assinatura real embutida — ver `emissao.concluir_assinatura_
    externa`."""
    doc = db.get(PrescriptionDocument, documento_id)
    if not doc:
        raise HTTPException(status_code=404, detail="Documento não encontrado.")
    presc = db.get(Prescription, doc.prescription_id)
    if not presc or presc.created_by != user.id:
        raise HTTPException(status_code=404, detail="Documento não encontrado.")

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
        # `verificacao_pdf.verificar()` chama `pyhanko.validate_pdf_signature`,
        # que por dentro faz `asyncio.run()` — trava com "cannot be called
        # from a running event loop" se rodar direto numa rota `async def`
        # (Starlette já tem um loop rodando aqui). `to_thread` isola a
        # chamada síncrona inteira numa thread própria, sem loop ambiente.
        emitido = await asyncio.to_thread(
            assinatura_emissao.concluir_assinatura_externa,
            db, tipo=assinatura_emissao.TIPO_RECEITA, referencia_id=doc.id,
            pdf_assinado=conteudo, criado_por=user.id,
        )
    except assinatura_emissao.AssinaturaNaoDetectada as e:
        raise HTTPException(status_code=422, detail=str(e)) from e
    except assinatura_emissao.FluxoAssinaturaExternaInvalido as e:
        raise HTTPException(status_code=409, detail=str(e)) from e

    db.add(AuditLog(
        user_id=user.id, action="concluir_assinatura_externa_receita",
        entity="prescription_document", entity_id=str(doc.id),
        detail={"sha256": emitido.registro.sha256, "bytes": len(emitido.pdf)},
    ))
    db.commit()
    return {"assinado": True, "assinado_em": emitido.registro.assinado_em}


class EnviarEmailIn(BaseModel):
    email: str = Field(min_length=5)
    assinar_smime: bool = False


@router.post("/documentos/{documento_id}/enviar-email")
def enviar_email(documento_id: int, dados: EnviarEmailIn, db: Session = Depends(get_db),
                 user=Depends(current_user)):
    doc = db.get(PrescriptionDocument, documento_id)
    if not doc:
        raise HTTPException(status_code=404, detail="Documento não encontrado.")
    presc = db.get(Prescription, doc.prescription_id)
    if not presc or presc.created_by != user.id:
        raise HTTPException(status_code=404, detail="Documento não encontrado.")
    if doc.status != "emitido":
        raise HTTPException(status_code=409, detail="Só é possível enviar um documento já emitido.")

    registro = assinatura_emissao.buscar(
        db, tipo=assinatura_emissao.TIPO_RECEITA, referencia_id=doc.id,
    )
    if not registro or registro.assinado_em is None or registro.nivel != "qualificada":
        raise HTTPException(
            status_code=409,
            detail=(
                "O envio por e-mail só é liberado para receita assinada digitalmente "
                "com assinatura qualificada ICP-Brasil."
            ),
        )

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
    html = emails.montar_html_documento_disponivel(
        nome_medico=professional_name(user), url=url, dias_validade=VALIDADE_LINK_DIAS,
        divulgacao_assinatura=divulgacao_email.texto_divulgacao(assinatura_emissao.ler_bytes(registro)),
    )
    resultado = envio_documento_email.enviar(
        db, user, destinatario=dados.email, assunto=emails.ASSUNTO_DOCUMENTO_DISPONIVEL,
        corpo_html=html, assinar_smime=dados.assinar_smime,
    )

    db.add(AuditLog(user_id=user.id, action="enviar_email_documento_receita",
                    entity="prescription_document", entity_id=str(doc.id),
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


@router.post("/documentos/{documento_id}/envio-paciente")
def envio_paciente_receita(
    documento_id: int, dados: EnvioPacienteIn, db: Session = Depends(get_db),
    user=Depends(current_user),
):
    """Oferta de envio ao paciente por e-mail ao concluir a assinatura
    digital da receita (pedido do Rafael, 08/08/2026) — mesmos dois canais
    de `documents.py::envio_paciente_gerado`, mesma exigência que já valia
    para `enviar_email` acima: só libera com assinatura qualificada
    ICP-Brasil (regra do receituário, mais estrita que documento genérico)."""
    doc = db.get(PrescriptionDocument, documento_id)
    if not doc:
        raise HTTPException(status_code=404, detail="Documento não encontrado.")
    presc = db.get(Prescription, doc.prescription_id)
    if not presc or presc.created_by != user.id:
        raise HTTPException(status_code=404, detail="Documento não encontrado.")
    if doc.status != "emitido":
        raise HTTPException(status_code=409, detail="Só é possível enviar um documento já emitido.")

    if not assinatura_email_ativa(db, user):
        raise HTTPException(status_code=409, detail="Este recurso exige CorvIA Mail ativo.")
    conta = db.query(EmailAccount).filter(EmailAccount.user_id == user.id).first()
    if not conta or conta.status != "ativa":
        raise HTTPException(status_code=409, detail="Sua caixa do CorvIA Mail não está ativa.")

    registro = assinatura_emissao.buscar(db, tipo=assinatura_emissao.TIPO_RECEITA, referencia_id=doc.id)
    if not registro or registro.assinado_em is None or registro.nivel != "qualificada":
        raise HTTPException(
            status_code=409,
            detail=(
                "O envio ao paciente só é liberado para receita assinada digitalmente "
                "com assinatura qualificada ICP-Brasil."
            ),
        )
    divulgacao = divulgacao_email.texto_divulgacao(assinatura_emissao.ler_bytes(registro))

    dest = db.query(PrescriptionRecipient).filter(
        PrescriptionRecipient.prescription_id == presc.id).first()
    if not dest:
        raise HTTPException(status_code=409, detail="Destinatário da receita não encontrado.")
    dest.email_cifrado = cofre.cifrar_campo(dados.email_paciente, presc.id)

    nome_tipo = "Receita de Controle Especial" if doc.tipo_codigo == "RCE" else "Receituário"

    if dados.canal == CANAL_AUTO_CONTATO_CORVIA:
        link = DocumentShareLink(
            tipo="prescription_document", referencia_id=doc.id, criado_por=user.id,
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
            tipo_origem=TIPO_ORIGEM_RECEITA, referencia_id=doc.id, canal=dados.canal,
            share_link_id=link.id, enviado_por=user.id,
            paciente_email_cifrado=cofre.cifrar_campo(dados.email_paciente, doc.id),
            assinatura_confirmada=divulgacao is not None, sucesso=resultado.enviado,
        ))
        db.add(AuditLog(
            user_id=user.id, action="envio_paciente_documento_receita", entity="prescription_document",
            entity_id=str(doc.id),
            detail={"canal": dados.canal, "enviado": resultado.enviado, "erro": resultado.erro},
        ))
        db.commit()
        return {
            "canal": dados.canal, "enviado": resultado.enviado, "erro": resultado.erro,
            "anexo": None, "assunto_sugerido": None, "corpo_sugerido": None,
        }

    assert dados.canal == CANAL_PROPRIO_CORVIA_MAIL  # só resta este valor no Literal
    nome_arquivo = (
        f"receita-controle-especial-{doc.id}.pdf" if doc.tipo_codigo == "RCE"
        else f"receituario-{doc.id}.pdf"
    )
    try:
        anexo = anexo_email_proprio.preparar(
            db, user, nome_arquivo=nome_arquivo, conteudo=assinatura_emissao.ler_bytes(registro),
        )
    except anexo_email_proprio.AnexoIndisponivel as e:
        raise HTTPException(status_code=502, detail=str(e)) from e

    db.add(PatientDocumentEmailSend(
        tipo_origem=TIPO_ORIGEM_RECEITA, referencia_id=doc.id, canal=dados.canal,
        share_link_id=None, enviado_por=user.id,
        paciente_email_cifrado=cofre.cifrar_campo(dados.email_paciente, doc.id),
        assinatura_confirmada=divulgacao is not None, sucesso=True,
    ))
    db.add(AuditLog(
        user_id=user.id, action="envio_paciente_documento_receita", entity="prescription_document",
        entity_id=str(doc.id), detail={"canal": dados.canal, "anexo_file_id": anexo.file_id},
    ))
    db.commit()
    return {
        "canal": dados.canal, "enviado": None, "erro": None,
        "anexo": {"file_id": anexo.file_id, "nome": anexo.nome},
        "assunto_sugerido": f"{nome_tipo} do seu médico — Corvia",
        "corpo_sugerido": divulgacao or "",
    }
