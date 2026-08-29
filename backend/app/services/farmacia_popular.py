"""Carrega e casa o elenco do Programa Farmácia Popular do Brasil (PFPB) —
gap encontrado por sessão externa em 29/08/2026, ver CLAUDE.md e
`app/models/farmacia_popular.py` para o desenho completo e o aviso de
segurança sobre `elegivel_confirmado`.

Reaproveita DELIBERADAMENTE a normalização de substância já usada e testada
pela CMED (`app/services/cmed_precos.py::palavras_normalizadas`/`eh_match`)
em vez de reimplementar — é a mesma classe de problema (nome de substância
com sal/hidrato variando entre fonte oficial e catálogo local, ex. "besilato
de anlodipino" × "Anlodipino (besilato)") e a mesma solução já resolve os
dois lados.

Não existe hoje, nesta sessão, um caminho automatizado de download do
elenco/EAN vigente do PFPB (ver módulo/manifesto) — diferente da CMED, cuja
página e padrão de URL de planilha já foram verificados em sessão com
acesso real ao servidor. Por isso `carregar_manifesto()` lê um arquivo local
versionado (`app/data/farmacia_popular_manifesto.json`), não raspa uma
página do gov.br. Quando alguém confirmar a URL vigente do arquivo de EAN,
o padrão certo é *acrescentar* uma função de download aqui, no mesmo
espírito de `cmed_precos.localizar_url_planilha()`, não substituir esta.
"""
from __future__ import annotations

import json
import logging
from pathlib import Path

from sqlalchemy.orm import Session

from app.models.drug import Drug
from app.models.farmacia_popular import FarmaciaPopularItem, FarmaciaPopularVersao
from app.services.cmed_precos import eh_match, palavras_normalizadas

log = logging.getLogger("meucardio.farmacia_popular")

MANIFESTO_PADRAO = Path(__file__).resolve().parent.parent / "data" / "farmacia_popular_manifesto.json"

CATEGORIAS_VALIDAS = {"hipertensao", "diabetes", "diabetes_cardiovascular", "dislipidemia"}


def _casar_substancia(nome_pfpb: str, farmacos_normalizados: list[tuple[int, frozenset[str]]]) -> int | None:
    """Mesma regra assimétrica da CMED: candidato local pode ter glosa a
    mais, PFPB com palavra a mais não casa. Em empate, prefere igualdade
    exata — mesmo critério de desempate já usado e documentado em
    `cmed_precos.casar_substancia`.

    `farmacos_normalizados` já vem SEM combinação de dose fixa (ver
    `carregar_manifesto`) — sem esse filtro, um item do PFPB que é
    princípio isolado (ex. "Glibenclamida") casaria com um `Drug` de
    combinação (ex. "Metformina (cloridrato) + Glibenclamida") sempre que
    não existir Drug isolado equivalente no catálogo, porque o conjunto de
    palavras do isolado é subconjunto do da combinação — atribuindo o
    subsídio à página errada. Mesma regra já documentada no CLAUDE.md:
    "combinação não empresta [preço] ao princípio isolado", pelo lado
    oposto (aqui: isolado não pode roubar de combinação nem o inverso)."""
    palavras_pfpb = palavras_normalizadas(nome_pfpb)
    candidatos = [
        (drug_id, local_p) for drug_id, local_p in farmacos_normalizados
        if eh_match(palavras_pfpb, local_p)
    ]
    if not candidatos:
        return None
    exatos = [drug_id for drug_id, local_p in candidatos if local_p == palavras_pfpb]
    if exatos:
        return exatos[0]
    return candidatos[0][0]


def carregar_manifesto(db: Session, caminho: Path | None = None) -> dict:
    """Importa o manifesto local em uma transação única. Não apaga versões
    anteriores (histórico de conferência fica preservado, mesma disciplina
    de nunca apagar preço/elenco em silêncio)."""
    caminho = caminho or MANIFESTO_PADRAO
    manifesto = json.loads(caminho.read_text(encoding="utf-8"))

    itens_brutos = manifesto.get("itens") or []
    erros: list[str] = []
    for item in itens_brutos:
        if item.get("categoria") not in CATEGORIAS_VALIDAS:
            erros.append(f"{item.get('substancia_pfpb', '?')}: categoria inválida")
    if erros:
        return {"carregado": False, "erros": erros}

    # Só fármaco publicado entra na disputa de casamento — mesma guarda já
    # aplicada em `cmed_precos.atualizar()`, pelo mesmo motivo: slug órfão
    # com nome mais "limpo" não pode roubar o match do fármaco que o médico
    # de fato vê na tela. E só fármaco ISOLADO (sem "+" no nome) — o elenco
    # do PFPB lista substância isolada, nunca combinação de dose fixa; sem
    # este filtro um princípio isolado sem Drug próprio no catálogo casaria
    # por engano com uma combinação que o contém (ver docstring de
    # `_casar_substancia`).
    farmacos = db.query(Drug.id, Drug.generic_name).filter(Drug.published.is_(True)).all()
    farmacos_normalizados = [
        (drug_id, palavras_normalizadas(nome)) for drug_id, nome in farmacos if "+" not in nome
    ]

    versao = FarmaciaPopularVersao(
        conferido_em=manifesto["conferido_em"],
        fontes=manifesto["fontes"],
        observacao=manifesto.get("observacao"),
        itens=len(itens_brutos),
    )
    db.add(versao)
    db.flush()

    casados = 0
    for item in itens_brutos:
        drug_id = _casar_substancia(item["substancia_pfpb"], farmacos_normalizados)
        if drug_id:
            casados += 1
        db.add(FarmaciaPopularItem(
            farmacia_popular_versao_id=versao.id,
            drug_id=drug_id,
            substancia_pfpb=item["substancia_pfpb"],
            dose_referencia=item["dose_referencia"],
            categoria=item["categoria"],
            indicacao=item["indicacao"],
            criterio_acesso=item["criterio_acesso"],
            ean=item.get("ean"),  # ausente em toda a carga inicial — ver aviso de segurança
            fonte_refs=item["fonte_refs"],
        ))

    db.commit()
    log.info(
        "Farmácia Popular %s importada: %d itens, %d casados com Drug",
        manifesto["conferido_em"], len(itens_brutos), casados,
    )
    return {
        "carregado": True, "conferido_em": manifesto["conferido_em"],
        "itens": len(itens_brutos), "casados_com_drug": casados,
        "farmacia_popular_versao_id": versao.id,
    }


def montar_exposicao(item: FarmaciaPopularItem | None) -> dict | None:
    """Formato exposto em `GET /drugs/{slug}/apresentacoes`. Regra de
    segurança inegociável (ver módulo/model): `elegivel_confirmado` só é
    `True` quando o item tem EAN carregado — nunca por match de substância
    isolado. Sem isso, a tela mostraria "gratuito" ao médico com base só em
    nome batendo, que não é garantia suficiente de que aquela apresentação
    específica está de fato no elenco vigente."""
    if item is None or not item.ativo:
        return None
    confirmado = bool(item.ean)
    return {
        "elegivel_confirmado": confirmado,
        "indicacao": item.indicacao,
        "dose_referencia": item.dose_referencia,
        "categoria": item.categoria,
        "criterio_acesso": item.criterio_acesso,
        "aviso": None if confirmado else (
            "Substância consta no elenco do Programa Farmácia Popular do Brasil, mas a "
            "elegibilidade desta apresentação específica ainda não foi confirmada por código "
            "de barras (EAN) contra a lista vigente do Ministério da Saúde — não afirmar "
            "'gratuito' ao paciente sem essa confirmação."
        ),
    }
