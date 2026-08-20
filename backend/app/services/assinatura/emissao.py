"""Ponto único de "assinar e persistir" um documento clínico (Tarefa 4).

Os quatro pontos de emissão (`api/receituario.py`, `api/documents.py` × 2,
`api/documentos_publicos.py` × 2) compartilham a mesma necessidade: validar
o método escolhido, pedir ao provedor (`assinatura/provedor.py`) para
assinar (ou não) o PDF já renderizado, e gravar o resultado — cifrado no
cofre, referenciado por `DocumentoEmitido` — para que o link público reabra
exatamente os mesmos bytes depois, em vez de regerar.

`tipo` segue o mesmo vocabulário que `DocumentShareLink` já usa (ver
`models/compartilhamento.py`): "prescription_document" para receita,
"generated_document" para atestado/laudo.
"""
from __future__ import annotations

import hashlib
from dataclasses import dataclass
from datetime import datetime, timezone
from pathlib import Path
from typing import Callable

from sqlalchemy.orm import Session

from app.core.config import settings
from app.models.assinatura import DocumentoEmitido
from app.services import cofre
from app.services.assinatura import catalogo
from app.services.assinatura.provedor import _MANUAL_EXTERNO, ProvedorAssinatura, obter_provedor

TIPO_RECEITA = "prescription_document"
TIPO_DOCUMENTO = "generated_document"


class MetodoInvalido(ValueError):
    """Código de método que não existe no catálogo — vira 422, não 500."""


class FluxoAssinaturaExternaInvalido(ValueError):
    """Documento não está no estado certo para receber o upload de volta
    do Assinador ITI — outro método, já assinado, ou não existe."""


class AssinaturaNaoDetectada(ValueError):
    """O arquivo enviado não contém uma assinatura digital real e íntegra
    — nunca aceita um PDF qualquer como se fosse o assinado (regra do
    projeto: nunca simular assinatura)."""


def _raiz() -> Path:
    return Path(settings.documentos_dir)


def preparar(metodo: str, *, db: Session | None = None, user=None) -> tuple[ProvedorAssinatura, catalogo.ProvedorInfo]:
    """Resolve o provedor e a info do catálogo, ou recusa com `MetodoInvalido`
    — quem chama decide se isso é 422 (parâmetro errado) ou outra coisa.
    `db`/`user` só são exigidos por `A1_ARQUIVO` (provedor por usuário, ver
    `provedor.py`) — os demais ignoram."""
    info = catalogo.info(metodo)
    if info is None:
        raise MetodoInvalido(f"Método de assinatura desconhecido: {metodo}")
    return obter_provedor(metodo, db=db, user=user), info


@dataclass
class Emitido:
    pdf: bytes
    registro: DocumentoEmitido


def assinar_e_persistir(
    db: Session, *, tipo: str, referencia_id: int, metodo: str,
    provedor: ProvedorAssinatura, info: catalogo.ProvedorInfo,
    pdf_visual: bytes, medico: dict, criado_por: int, data_emissao: datetime,
    layout: str | None = None,
) -> Emitido:
    """Chama `provedor.assinar()` sobre o PDF já renderizado (com a legenda e
    o aviso já corretos para `metodo` — ver `pdf_documento._assinatura_
    rodape`) e persiste o resultado. Só chame depois de confirmar
    `provedor.disponivel()` — esta função não repete a checagem, porque cada
    chamador já monta sua própria lista de `bloqueios` a partir dela."""
    from app.services.assinatura import validacao_publica

    codigo_validacao = validacao_publica.codigo_documento(
        tipo=tipo, referencia_id=referencia_id, criado_por=criado_por,
    )
    url_validacao = validacao_publica.url_documento(
        tipo=tipo, referencia_id=referencia_id, criado_por=criado_por,
    )
    resultado = provedor.assinar(
        pdf_visual,
        medico,
        {
            "tipo": tipo, "referencia_id": referencia_id, "layout": layout,
            "codigo_validacao": codigo_validacao, "url_validacao": url_validacao,
        },
    )
    if resultado.estado == "indisponivel":
        # Defensivo: não deveria acontecer se o chamador checou disponivel()
        # antes, mas nada aqui pode arriscar persistir um PDF de mentira.
        raise RuntimeError(resultado.motivo or f"{metodo} recusou assinar sem motivo.")

    pdf_final = resultado.pdf if resultado.pdf is not None else pdf_visual
    if resultado.estado == "assinado":
        from app.services.assinatura import verificacao_pdf

        assinatura = verificacao_pdf.verificar(pdf_final)
        if assinatura is None:
            raise AssinaturaNaoDetectada(
                "O provedor informou sucesso, mas o PDF não contém assinatura digital embutida."
            )
        if not (
            assinatura.intacta
            and assinatura.estrutura_valida
            and assinatura.cobre_documento_inteiro
        ):
            raise AssinaturaNaoDetectada(
                "A assinatura gerada não cobre o documento inteiro ou falhou na validação de integridade."
            )
    sha256 = hashlib.sha256(pdf_final).hexdigest()
    nome_arquivo = cofre.guardar(pdf_final, criado_por, raiz=_raiz())

    registro = DocumentoEmitido(
        tipo=tipo, referencia_id=referencia_id, metodo=metodo, nivel=info.nivel,
        arquivo_nome=nome_arquivo, sha256=sha256, bytes_tam=len(pdf_final),
        assinado_em=data_emissao if resultado.estado == "assinado" else None,
        criado_por=criado_por,
    )
    db.add(registro)
    return Emitido(pdf=pdf_final, registro=registro)


def concluir_assinatura_externa(
    db: Session, *, tipo: str, referencia_id: int, pdf_assinado: bytes, criado_por: int,
) -> Emitido:
    """Fecha o fluxo do Assinador ITI (Trabalho 14): o médico baixou o PDF
    emitido com `metodo` em GOVBR/VIDAAS/BIRDID/SAFEID/NEOID/REMOTEID (estado
    "nao_assinado"), assinou em assinador.iti.br — fora da Corvia, sem API —
    e reenvia o arquivo assinado aqui.

    Nunca aceita o upload só porque "parece" um PDF: confere que ele é a
    revisão incremental exata do PDF original e que existe uma assinatura
    digital REAL e íntegra embutida
    (`verificacao_pdf.verificar()`), a mesma checagem já usada para
    divulgar a assinatura por e-mail (Trabalho 11). Sem isso, levanta
    `AssinaturaNaoDetectada` — nunca marca como assinado por engano."""
    from app.services.assinatura import verificacao_pdf

    registro = buscar(db, tipo=tipo, referencia_id=referencia_id)
    if registro is None:
        raise FluxoAssinaturaExternaInvalido("Documento não encontrado.")
    if registro.criado_por != criado_por:
        raise FluxoAssinaturaExternaInvalido("Documento não encontrado.")
    if registro.metodo not in _MANUAL_EXTERNO:
        raise FluxoAssinaturaExternaInvalido(
            "Este documento não foi emitido pelo fluxo do Assinador ITI."
        )
    if registro.assinado_em is not None:
        raise FluxoAssinaturaExternaInvalido("Este documento já está assinado.")

    pdf_original = ler_bytes(registro)
    if not pdf_assinado.startswith(pdf_original):
        raise AssinaturaNaoDetectada(
            "O PDF assinado não corresponde exatamente ao documento original "
            "emitido pela CorVIA. Baixe novamente o original e assine esse arquivo "
            "sem editar ou reexportar."
        )

    resultado = verificacao_pdf.verificar(pdf_assinado)
    if resultado is None:
        raise AssinaturaNaoDetectada(
            "O arquivo enviado não contém nenhuma assinatura digital embutida — "
            "assine o PDF no Assinador gov.br (assinador.iti.br) e envie o arquivo "
            "resultante, não o original."
        )
    if not resultado.intacta:
        raise AssinaturaNaoDetectada(
            "A assinatura encontrada no arquivo não confere com o conteúdo — envie "
            "o PDF exatamente como saiu do Assinador gov.br, sem editar ou reexportar."
        )
    if not resultado.estrutura_valida or not resultado.cobre_documento_inteiro:
        raise AssinaturaNaoDetectada(
            "A assinatura não cobre integralmente o documento ou tem estrutura inválida."
        )
    if registro.nivel == catalogo.NIVEL_QUALIFICADA and not resultado.qualificada_icp_brasil:
        raise AssinaturaNaoDetectada(
            "O certificado usado não apresenta política A1, A2, A3 ou A4 ICP-Brasil. "
            "Receitas controladas exigem assinatura eletrônica qualificada."
        )

    sha256 = hashlib.sha256(pdf_assinado).hexdigest()
    nome_arquivo_novo = cofre.guardar(pdf_assinado, criado_por, raiz=_raiz())
    nome_arquivo_antigo = registro.arquivo_nome

    registro.arquivo_nome = nome_arquivo_novo
    registro.sha256 = sha256
    registro.bytes_tam = len(pdf_assinado)
    registro.assinado_em = datetime.now(timezone.utc)

    cofre.apagar(nome_arquivo_antigo, raiz=_raiz())
    return Emitido(pdf=pdf_assinado, registro=registro)


def buscar(db: Session, *, tipo: str, referencia_id: int) -> DocumentoEmitido | None:
    return (
        db.query(DocumentoEmitido)
        .filter(DocumentoEmitido.tipo == tipo, DocumentoEmitido.referencia_id == referencia_id)
        .first()
    )


def ler_bytes(registro: DocumentoEmitido) -> bytes:
    return cofre.ler(registro.arquivo_nome, registro.criado_por, raiz=_raiz())


def servir_ou_regerar(db: Session, *, tipo: str, referencia_id: int,
                      regerar: Callable[[], bytes]) -> bytes:
    """Usado pelos pontos de LEITURA (`GET .../pdf`, link público): se o
    documento já foi emitido depois da Tarefa 4, serve os bytes exatos que o
    médico assinou/viu, lendo do cofre. Documento emitido ANTES da migração
    não tem `DocumentoEmitido` — regera como sempre foi feito, via a
    função `regerar` que o chamador já tinha."""
    registro = buscar(db, tipo=tipo, referencia_id=referencia_id)
    if registro is None:
        return regerar()
    return ler_bytes(registro)
