"""Custo por requisição do "Tudo com Tudo" e equivalência dos rótulos históricos.

Medido no corpus real (12/09/2026) antes desta correção: abrir UM documento de
"Terapia intensiva" disparava **82 consultas** e ~205 ms só para desenhar o
painel lateral. A causa não era o volume de conteúdo: `theme_variants` devolve
o tema canônico mais seus rótulos históricos, e cada rótulo era consultado
separadamente em cada uma das doze frentes. **28 dos 30 aliases não casam com
nenhuma linha do acervo** — a maior parte dessas consultas era garantidamente
vazia, repetida em toda abertura de página.

A correção consulta os rótulos juntos (`IN (...)`), uma vez por frente. Estes
testes travam as duas propriedades que isso não pode quebrar:

1. **o custo não cresce com o número de rótulos** — um tema com vários aliases
   custa o mesmo que um tema sem nenhum;
2. **o resultado é idêntico ao do fan-out anterior** — item gravado sob rótulo
   histórico continua aparecendo, e o tema canônico continua preenchendo as
   vagas antes de um alias quando o limite corta.

Mesmo TRUNCATE explícito de `test_relacionados.py`: o `_banco_limpo` autouse do
conftest cobre só as tabelas do CorvIA Mail, não as de conteúdo clínico.
"""

from sqlalchemy import event, text

from app.core.db import SessionLocal, engine
from app.models.clinical_case import ClinicalCase
from app.models.content import Document
from app.models.drug import Drug
from app.services.connected_content import buscar_relacionados_contextuais
from app.services.related_content import buscar_relacionados
from app.services.topic_relevance import (
    SUPPORTED_DRUG_TOPICS,
    THEME_ALIASES,
    theme_variants,
)

TABELAS = (
    "knowledge_relations", "knowledge_entities", "symptom_triage_guides",
    "specialty_diseases", "document_revisions", "documents",
    "evidence_records", "scientific_studies",
    "drugs", "clinical_cases", "study_tracks", "gallery_images", "lab_tests",
    "emergency_protocols", "discharge_checklists", "patient_materials",
)

# "Geral" reúne quatro rótulos históricos; "Endocardite" não tem nenhum.
# Os dois ficam fora de DRUG_TOPIC_PHRASES, então só o número de rótulos difere.
TEMA_COM_ALIASES = "Geral"
ALIAS_VIVO = "Populações especiais"
TEMA_SEM_ALIAS = "Endocardite"


def _limpar(db):
    db.execute(text(f"TRUNCATE {', '.join(TABELAS)} RESTART IDENTITY CASCADE"))
    db.commit()


class _ContadorDeConsultas:
    """Conta consultas emitidas no bloco — o custo que o assinante paga."""

    def __init__(self):
        self.total = 0

    def __enter__(self):
        event.listen(engine, "before_cursor_execute", self._registrar)
        return self

    def __exit__(self, *_):
        event.remove(engine, "before_cursor_execute", self._registrar)

    def _registrar(self, *_args, **_kwargs):
        self.total += 1


def _documento(slug: str, tema: str) -> Document:
    return Document(
        slug=slug, title=f"Documento {slug}", kind="modulo", theme=tema,
        body_md="conteúdo", source_tier="A", review_status="revisado",
        published=True,
    )


def test_alias_historico_nao_multiplica_consultas(db):
    """Um tema com quatro rótulos históricos custa o mesmo que um sem nenhum."""
    _limpar(db)
    db.add(_documento("tct-geral-1", TEMA_COM_ALIASES))
    db.add(_documento("tct-hp-1", TEMA_SEM_ALIAS))
    db.commit()

    assert len(theme_variants(TEMA_COM_ALIASES)) > 1
    assert len(theme_variants(TEMA_SEM_ALIAS)) == 1

    sessao = SessionLocal()
    try:
        with _ContadorDeConsultas() as com_alias:
            buscar_relacionados_contextuais(
                sessao, TEMA_COM_ALIASES,
                excluir_tipo="documento", excluir_slug="tct-geral-1",
                assunto="tct-geral-1",
            )
        with _ContadorDeConsultas() as sem_alias:
            buscar_relacionados_contextuais(
                sessao, TEMA_SEM_ALIAS,
                excluir_tipo="documento", excluir_slug="tct-hp-1",
                assunto="tct-hp-1",
            )
    finally:
        sessao.close()

    assert com_alias.total == sem_alias.total, (
        "o número de consultas voltou a crescer com a quantidade de rótulos "
        f"históricos ({com_alias.total} contra {sem_alias.total})"
    )


def test_item_gravado_sob_rotulo_historico_continua_aparecendo(db):
    """Agrupar os rótulos numa consulta não pode perder o conteúdo antigo."""
    _limpar(db)
    db.add(_documento("tct-origem", TEMA_COM_ALIASES))
    db.add(ClinicalCase(
        slug="tct-origem-caso-antigo", titulo="Caso sob rótulo histórico",
        tema=ALIAS_VIVO, nivel="intermediario", enunciado="enunciado",
        pergunta="pergunta?", opcoes=["a", "b"], resposta_correta=0,
        explicacao="explicação", review_status="revisado", published=True,
    ))
    db.commit()

    assert THEME_ALIASES[ALIAS_VIVO] == TEMA_COM_ALIASES

    resposta = buscar_relacionados_contextuais(db, TEMA_COM_ALIASES)
    casos = next(g for g in resposta["grupos"] if g["tipo"] == "caso_clinico")
    assert [i["slug"] for i in casos["itens"]] == ["tct-origem-caso-antigo"]


def test_tema_canonico_ocupa_as_vagas_antes_do_rotulo_historico(db):
    """Ordem preservada: o limite corta o alias primeiro, nunca o canônico."""
    _limpar(db)
    limite = 2
    for indice in range(limite):
        db.add(ClinicalCase(
            slug=f"tct-canonico-{indice}", titulo=f"Canônico {indice}",
            tema=TEMA_COM_ALIASES, nivel="intermediario", enunciado="e",
            pergunta="p?", opcoes=["a", "b"], resposta_correta=0,
            explicacao="e", review_status="revisado", published=True,
        ))
    db.add(ClinicalCase(
        slug="tct-alias-0", titulo="Rótulo histórico", tema=ALIAS_VIVO,
        nivel="intermediario", enunciado="e", pergunta="p?",
        opcoes=["a", "b"], resposta_correta=0, explicacao="e",
        review_status="revisado", published=True,
    ))
    db.commit()

    resposta = buscar_relacionados(
        db, theme_variants(TEMA_COM_ALIASES), limite_por_categoria=limite,
    )
    casos = next(g for g in resposta["grupos"] if g["tipo"] == "caso_clinico")
    slugs = [item["slug"] for item in casos["itens"]]
    assert len(slugs) == limite
    assert "tct-alias-0" not in slugs, (
        "um item de rótulo histórico tomou a vaga de um item do tema canônico"
    )


def test_tema_sem_farmaco_possivel_nao_varre_o_catalogo(db):
    """Só Farmacologia e tópicos com indicação declarada admitem fármaco."""
    _limpar(db)
    db.add(Drug(
        slug="tct-farmaco", generic_name="Fármaco de teste",
        drug_class="classe", indications=["insuficiencia cardiaca"],
        review_status="revisado", published=True,
    ))
    db.add(_documento("tct-sem-farmaco", TEMA_SEM_ALIAS))
    db.commit()

    assert TEMA_SEM_ALIAS not in SUPPORTED_DRUG_TOPICS

    sessao = SessionLocal()
    try:
        with _ContadorDeConsultas() as contador:
            resposta = buscar_relacionados_contextuais(
                sessao, TEMA_SEM_ALIAS,
                excluir_tipo="documento", excluir_slug="tct-sem-farmaco",
                assunto="tct-sem-farmaco",
            )
        consultas_do_tema = contador.total
        with _ContadorDeConsultas() as contador_farmacologia:
            buscar_relacionados_contextuais(
                sessao, "Farmacologia",
                excluir_tipo="documento", excluir_slug="tct-sem-farmaco",
                assunto="tct-sem-farmaco",
            )
    finally:
        sessao.close()

    medicamentos = next(g for g in resposta["grupos"] if g["tipo"] == "medicamento")
    assert medicamentos["itens"] == []
    assert consultas_do_tema < contador_farmacologia.total, (
        "o catálogo de medicamentos continua sendo varrido num tema que não "
        "pode conter nenhum fármaco"
    )


def test_nenhuma_rota_gerada_leva_a_pagina_inexistente(db):
    """Todo link do painel precisa existir no React Router — 404 é inaceitável.

    O painel é navegação: cada item vira um `<Link to=...>`. Uma rota gerada sem
    página correspondente manda o assinante para uma tela em branco a partir de
    um conteúdo que existe. Medido no corpus real em 12/09/2026: 1.762 rotas
    distintas, nenhuma quebrada — este teste impede que a próxima frente nasça
    com um padrão de rota que o frontend não registra.
    """
    import re
    from pathlib import Path

    _limpar(db)
    db.add(_documento("tct-rota-doc", TEMA_SEM_ALIAS))
    db.add(ClinicalCase(
        slug="tct-rota-caso", titulo="Caso", tema=TEMA_SEM_ALIAS,
        nivel="intermediario", enunciado="e", pergunta="p?", opcoes=["a", "b"],
        resposta_correta=0, explicacao="e", review_status="revisado",
        published=True,
    ))
    db.commit()

    app_tsx = Path(__file__).resolve().parents[2] / "frontend" / "src" / "App.tsx"
    padroes = [
        re.compile("^" + re.sub(r":[A-Za-z_]+", "[^/]+", re.escape(
            rota if rota.startswith("/") else f"/{rota}"
        ).replace(r"\:", ":")) + "$")
        for rota in re.findall(r'path="([^"]+)"', app_tsx.read_text(encoding="utf-8"))
        if rota != "*"
    ]

    resposta = buscar_relacionados_contextuais(db, TEMA_SEM_ALIAS)
    caminhos = {
        valor
        for grupo in resposta["grupos"]
        for valor in [grupo["rota_lista"], *(i["rota"] for i in grupo["itens"])]
        if valor
    }
    assert caminhos, "o painel não gerou nenhuma rota para conferir"
    quebradas = [
        caminho for caminho in sorted(caminhos)
        if not any(p.match(caminho.split("?")[0]) for p in padroes)
    ]
    assert not quebradas, f"rotas sem página no React Router: {quebradas}"
