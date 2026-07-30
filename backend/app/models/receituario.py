# -*- coding: utf-8 -*-
"""Modelo do receituário (Tarefa 27) — Portaria SVS/MS 344/98 e RDC 1.000/2025.

O desenho e o porquê de cada entidade estão em `controlados/DESENHO.md`. O
resumo que importa para ler este arquivo:

**O tipo de documento não é função da substância — é função da substância mais a
apresentação.** O adendo da Lista A1 manda oxicodona em comprimido de liberação
controlada até 40 mg para Receita de Controle Especial, embora oxicodona seja
A1, cujo receituário é a Notificação A. Por isso existe `PrescriptionRule`
separada de `ControlledSubstance`: a lista dá o tipo padrão, a regra sobrepõe.

E por isso `Prescription` (intenção clínica) é separada de
`PrescriptionDocument` (documento emitido): uma receita com clonazepam e
amoxicilina produz dois documentos, um NRB e um comum, por consequência do
modelo — não por caso especial no código.
"""
from datetime import datetime, timezone

from sqlalchemy import (
    ARRAY, Boolean, DateTime, ForeignKey, Integer, LargeBinary, String, Text, UniqueConstraint,
)
from sqlalchemy.dialects.postgresql import JSONB
from sqlalchemy.orm import Mapped, mapped_column

from app.core.db import Base


class ControlledSubstance(Base):
    """Substância da 344/98 e a lista em que ela está.

    Dado de referência versionado: as listas mudam por RDC, e uma receita
    emitida precisa poder dizer qual versão a classificou. Mesma lógica do
    `cmed_versions` desenhado na Tarefa A.
    """

    __tablename__ = "controlled_substances"
    __table_args__ = (UniqueConstraint("nome_normalizado", "fonte_versao",
                                       name="uq_substancia_por_versao"),)

    id: Mapped[int] = mapped_column(primary_key=True)
    nome: Mapped[str] = mapped_column(String(300))
    # Sem acento, minúsculo, sem sal entre parênteses — é por ele que casamos
    # com a base de medicamentos, pelo mesmo normalizador usado no casamento
    # com a CMED ("Anlodipino (besilato)" x "BESILATO DE ANLODIPINO").
    nome_normalizado: Mapped[str] = mapped_column(String(300), index=True)
    sinonimos: Mapped[list[str]] = mapped_column(ARRAY(String), default=list)

    lista: Mapped[str] = mapped_column(String(4), index=True)   # A1, B1, C1, F2...
    # Tipo padrão do receituário para a lista, lido do subtítulo literal da
    # norma. Nulo quando a lista não gera receituário médico (D2, E, F).
    tipo_sncr: Mapped[str | None] = mapped_column(String(8), nullable=True)
    proscrita: Mapped[bool] = mapped_column(Boolean, default=False)

    fonte_norma: Mapped[str] = mapped_column(String(200))
    fonte_versao: Mapped[str] = mapped_column(String(60), index=True)


class PrescriptionType(Base):
    """Tipo de documento — tabela de referência, **não `enum` no código**.

    O que difere entre os tipos é muito mais que rótulo: cor, número de vias e
    destinação de cada uma, se exige numeração do SNCR e por qual endpoint,
    tamanho do lote, validade, retenção na farmácia. E o conjunto muda por
    norma — a RDC 1.000/2025 já o alterou uma vez, e o SNCR entra em operação
    em 30/09/2026. Regime que muda por norma não vira constante de código.
    """

    __tablename__ = "prescription_types"

    id: Mapped[int] = mapped_column(primary_key=True)
    codigo: Mapped[str] = mapped_column(String(8), unique=True, index=True)  # NRA, RCE, COMUM...
    nome: Mapped[str] = mapped_column(String(160))
    cor: Mapped[str | None] = mapped_column(String(30), nullable=True)  # amarela|azul|branca

    vias: Mapped[int] = mapped_column(Integer, default=1)
    # Destinação declarada de cada via, na ordem. A norma exige o dizer impresso:
    # ["1ª via — retenção da farmácia", "2ª via — orientação ao paciente"].
    destinacao_vias: Mapped[list[str]] = mapped_column(ARRAY(String), default=list)

    exige_numeracao_sncr: Mapped[bool] = mapped_column(Boolean, default=False)
    endpoint_sncr: Mapped[str | None] = mapped_column(String(80), nullable=True)
    lote_min: Mapped[int | None] = mapped_column(Integer, nullable=True)
    lote_max: Mapped[int | None] = mapped_column(Integer, nullable=True)

    validade_dias: Mapped[int | None] = mapped_column(Integer, nullable=True)
    exige_retencao: Mapped[bool] = mapped_column(Boolean, default=False)
    campos_obrigatorios: Mapped[list[str]] = mapped_column(ARRAY(String), default=list)

    # Desligado enquanto o SNCR não abrir e a assinatura digital não existir.
    # É a flag que mantém o controle especial fora do ar sem remover o código.
    ativo: Mapped[bool] = mapped_column(Boolean, default=False, index=True)


class PrescriptionRule(Base):
    """Regra condicional vinda de adendo da norma, que **sobrepõe** o tipo da lista.

    `texto_normativo` é verbatim, de propósito: transformar "não mais que 40
    miligramas por unidade posológica" em condição de máquina é trabalho humano,
    e enquanto `codificada` for falso a classificação **cai para revisão** em vez
    de assumir o tipo da lista. Falhar para o lado do médico decidir é a única
    falha aceitável aqui.
    """

    __tablename__ = "prescription_rules"

    id: Mapped[int] = mapped_column(primary_key=True)
    lista: Mapped[str] = mapped_column(String(4), index=True)
    texto_normativo: Mapped[str] = mapped_column(Text)
    tipo_resultante: Mapped[str | None] = mapped_column(String(8), nullable=True)

    codificada: Mapped[bool] = mapped_column(Boolean, default=False)
    # Só preenchido quando `codificada` — ex.: {"substancia": "oxicodona",
    # "forma": "comprimido de liberação controlada", "mg_por_unidade_max": 40}
    condicao: Mapped[dict] = mapped_column(JSONB, default=dict)

    fonte_versao: Mapped[str] = mapped_column(String(60))


class PrescriptionRecipient(Base):
    """Identificação do paciente exigida pelo receituário, cifrada em repouso.

    Existe separada do `Patient` do round por decisão do Rafael em 29/07/2026: o
    paciente do round **continua anonimizado**, com iniciais e prontuário. Nome,
    endereço e documento só existem aqui, no contexto da receita, cifrados com o
    mesmo cofre do telediagnóstico — AES-256-GCM com o id como dado autenticado.
    """

    __tablename__ = "prescription_recipients"

    id: Mapped[int] = mapped_column(primary_key=True)
    prescription_id: Mapped[int] = mapped_column(
        ForeignKey("prescriptions.id", ondelete="CASCADE"), index=True, unique=True
    )

    nome_cifrado: Mapped[bytes] = mapped_column(LargeBinary)
    endereco_cifrado: Mapped[bytes | None] = mapped_column(LargeBinary, nullable=True)
    documento_cifrado: Mapped[bytes | None] = mapped_column(LargeBinary, nullable=True)
    # Acrescentado em 30/07/2026 (Tarefa 29 — enviar receita por e-mail).
    # Opcional: só existe se o médico decidir enviar a receita por e-mail; a
    # receita em si não exige e-mail do paciente.
    email_cifrado: Mapped[bytes | None] = mapped_column(LargeBinary, nullable=True)

    created_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), default=lambda: datetime.now(timezone.utc)
    )


class PrescriptionDocument(Base):
    """Documento efetivamente emitido a partir de uma prescrição.

    Um por tipo exigido. É esta separação que faz receita com medicamentos de
    listas diferentes gerar documentos separados sem caso especial no código, e
    é aqui que mora a numeração — que é por documento, nunca por prescrição.

    `itens` é snapshot: o documento preserva o que foi impresso mesmo que o
    cadastro do medicamento mude depois. Mesmo princípio do `pmc_snapshot` da
    Tarefa B.
    """

    __tablename__ = "prescription_documents"

    id: Mapped[int] = mapped_column(primary_key=True)
    prescription_id: Mapped[int] = mapped_column(
        ForeignKey("prescriptions.id", ondelete="CASCADE"), index=True
    )
    tipo_codigo: Mapped[str] = mapped_column(String(8), index=True)

    # Nulo até o SNCR fornecer. Formato "2411.1-00.0000001".
    numeracao: Mapped[str | None] = mapped_column(String(30), nullable=True, index=True)
    itens: Mapped[list] = mapped_column(JSONB, default=list)

    # rascunho -> revisado -> emitido. `revisado` é o checkpoint humano: o médico
    # não escolhe o tipo, mas confirma a classificação antes de emitir.
    status: Mapped[str] = mapped_column(String(20), default="rascunho", index=True)
    # Preenchido quando o médico corrige a classificação automática. Guardar o
    # motivo é o que permite descobrir depois que uma regra está errada.
    classificacao_corrigida_de: Mapped[str | None] = mapped_column(String(8), nullable=True)
    motivo_correcao: Mapped[str | None] = mapped_column(Text, nullable=True)

    # Itens que a classificação não conseguiu decidir sozinha, por causa de
    # regra de adendo ainda não codificada. Não vazio = exige revisão humana.
    pendencias: Mapped[list] = mapped_column(JSONB, default=list)

    fonte_versao_listas: Mapped[str | None] = mapped_column(String(60), nullable=True)
    created_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), default=lambda: datetime.now(timezone.utc)
    )
    emitido_em: Mapped[datetime | None] = mapped_column(DateTime(timezone=True), nullable=True)
    # Acrescentado em 30/07/2026 (Tarefa 29 — letterhead). 'residencial' |
    # 'profissional' | nulo (nenhum endereço no PDF). Gravado na emissão, não
    # recalculado depois: o link público reabre este PDF mais tarde e ele
    # precisa sair idêntico, mesmo que o médico troque o cadastro entretanto.
    endereco_exibido: Mapped[str | None] = mapped_column(String(20), nullable=True)
    # Acrescentado em 30/07/2026 — exigido por lei especificamente para
    # anabolizantes/hormônios (Lei nº 9.965/2000, art. 1º, parágrafo único),
    # verificado direto na fonte: "...o número do Código Internacional de
    # Doenças (CID)...". Opcional aqui porque nem todo PrescriptionDocument
    # é desse grupo — ver `itens[].lista == "C5"`. A EMISSÃO de RCE segue
    # bloqueada (layout oficial não reproduzido); este campo só existe para
    # não perder o requisito quando ela for desbloqueada.
    cid: Mapped[str | None] = mapped_column(String(10), nullable=True)
