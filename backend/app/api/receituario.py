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
from fastapi import APIRouter, Depends, HTTPException
from pydantic import BaseModel, Field
from sqlalchemy.orm import Session

from app.core.db import get_db
from app.core.security import current_user
from app.models.audit import AuditLog
from app.models.clinical_docs import Prescription
from app.models.drug import Drug
from app.models.receituario import (
    ControlledSubstance, PrescriptionDocument, PrescriptionRecipient, PrescriptionRule,
    PrescriptionType,
)
from app.services import cofre
from app.services.classificacao_receituario import (
    ItemPrescrito, Regra, Substancia, classificar, normalizar,
)

router = APIRouter(prefix="/api/receituario", tags=["receituário"])


# ------------------------------------------------------------------ schemas --
class ItemIn(BaseModel):
    """`drug_slug` é o caminho correto: ele resolve a substância na base
    estruturada. `descricao` livre é aceita para não travar o médico, mas cai
    em pendência — texto livre não é classificável, e chutar aqui emitiria o
    documento errado."""
    drug_slug: str | None = None
    descricao: str = ""
    apresentacao: str = ""
    posologia: str = ""
    orientacao: str = ""


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
                    "apresentacao": i.apresentacao, "posologia": i.posologia}
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


@router.get("/{prescricao_id}")
def obter(prescricao_id: int, db: Session = Depends(get_db), user=Depends(current_user)):
    presc = db.get(Prescription, prescricao_id)
    if not presc or presc.created_by != user.id:
        raise HTTPException(status_code=404, detail="Prescrição não encontrada.")

    dest = db.query(PrescriptionRecipient).filter(
        PrescriptionRecipient.prescription_id == presc.id).first()
    # Toda leitura de dado identificável de paciente vai para a auditoria, do
    # mesmo jeito que a leitura de exame no Cofre.
    nome = None
    if dest:
        nome = cofre.decifrar_campo(dest.nome_cifrado, presc.id)
        db.add(AuditLog(user_id=user.id, action="ler_destinatario_receita",
                        entity="prescription", entity_id=str(presc.id)))
        db.commit()

    docs = db.query(PrescriptionDocument).filter(
        PrescriptionDocument.prescription_id == presc.id).all()
    tipos = _tipos(db)
    return {"prescricao_id": presc.id, "destinatario": {"nome": nome},
            "observacoes": presc.notes,
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


@router.post("/documentos/{documento_id}/emitir")
def emitir(documento_id: int, db: Session = Depends(get_db), user=Depends(current_user)):
    """Recusa e explica, em vez de simular.

    Emitir exige três coisas que ainda não existem: o tipo ligado, a numeração
    do SNCR e a assinatura digital. Devolver um documento sem elas seria entregar
    ao médico um papel que a farmácia recusa — e pior, com aparência de válido.
    """
    doc = db.get(PrescriptionDocument, documento_id)
    if not doc:
        raise HTTPException(status_code=404, detail="Documento não encontrado.")
    presc = db.get(Prescription, doc.prescription_id)
    if not presc or presc.created_by != user.id:
        raise HTTPException(status_code=404, detail="Documento não encontrado.")

    tipo = _tipos(db).get(doc.tipo_codigo)
    bloqueios = []
    if doc.status != "revisado":
        bloqueios.append("O documento precisa ser revisado antes de emitido.")
    if not tipo or not tipo.ativo:
        bloqueios.append(
            f"O tipo {doc.tipo_codigo} está desligado: depende da integração com o "
            f"SNCR, que a Anvisa disponibiliza até 30/09/2026, e da assinatura digital."
        )
    if tipo and tipo.exige_numeracao_sncr and not doc.numeracao:
        bloqueios.append(
            "Este tipo exige numeração do SNCR, e o prescritor precisa estar "
            "cadastrado no sistema da Anvisa para obtê-la."
        )
    if bloqueios:
        raise HTTPException(status_code=409, detail={
            "erro": "Emissão indisponível.", "bloqueios": bloqueios,
            "nada_foi_simulado": True,
        })

    # Caminho ainda não alcançável — geração do PDF em ReportLab é a próxima fase.
    raise HTTPException(status_code=501, detail={
        "erro": "Geração do documento ainda não implementada.",
        "proxima_fase": "PDF em ReportLab, decidido em 29/07/2026.",
    })
