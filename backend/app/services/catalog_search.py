"""Catálogo léxico transversal das 13 frentes científicas + calculadoras.

Extraído de `app/api/search.py` (Parte 2 da correção coordenada de
02/09/2026) para ser reaproveitado também pela busca léxica da IA
(`app/services/rag.py`/`rag_multi.py`), sem duplicar a consulta SQL — o
endpoint `GET /api/search` e a recuperação da IA agora usam exatamente o
mesmo `SQL`/`LITERAL_SQL`/`CATALOG_SQL`, só a camada de cima muda.

Nenhuma mudança de comportamento nesta extração: mesmo texto de SQL, mesmas
funções, mesmo contrato — só de arquivo. `app/api/search.py` importa tudo
daqui.
"""
from __future__ import annotations

import re
import unicodedata

from sqlalchemy import text

from app.services import calculators as calc

# O corpus científico canônico possui 13 frentes persistidas. As calculadoras
# clínicas vivem num registro validado em memória e entram como uma 14ª frente
# funcional, sem fingir que são registros científicos do banco. A versão antiga
# deste endpoint unia somente cinco delas e deixava milhares de registros
# publicados estruturalmente invisíveis ao Tudo com Tudo. Este catálogo mantém
# o contrato histórico da resposta, mas normaliza todas as frentes para uma
# única superfície pesquisável. As cinco coleções com `search_vector` usam o
# índice GIN existente; as demais (pouco mais de três mil itens) calculam o
# vetor durante a consulta, evitando uma migração arriscada neste hotfix.
#
# `published = true` é obrigatório em cada braço: conteúdo em quarentena nunca
# pode aparecer por uma busca transversal.

CATALOG_SQL = """
  SELECT 'documento'::text AS frente, slug::text, title::text, kind::text,
         theme::text, source_tier::text, NULL::integer AS ano,
         coalesce(summary, left(body_md, 1200), '')::text AS corpo,
         search_vector AS v,
         (coalesce(title, '') || ' ' || coalesce(theme, '') || ' ' ||
          coalesce(summary, '') || ' ' || coalesce(tags::text, '') || ' ' ||
          coalesce(body_md, '') || ' ' || slug)::text AS pesquisavel
  FROM documents WHERE published = true

  UNION ALL
  SELECT 'galeria', slug::text, title::text, modality::text, theme::text,
         NULL::text, NULL::integer, coalesce(findings, teaching_points, '')::text,
         search_vector,
         (coalesce(title, '') || ' ' || coalesce(theme, '') || ' ' ||
          coalesce(modality, '') || ' ' || coalesce(findings, '') || ' ' ||
          coalesce(teaching_points, '') || ' ' || coalesce(tags::text, '') || ' ' || slug)::text
  FROM gallery_images WHERE published = true

  UNION ALL
  SELECT 'exame', slug::text, name::text, category::text, theme::text,
         NULL::text, NULL::integer,
         (coalesce(what_it_measures, '') || ' ' || coalesce(interpretation, ''))::text,
         search_vector,
         (coalesce(name, '') || ' ' || coalesce(theme, '') || ' ' ||
          coalesce(category, '') || ' ' || coalesce(what_it_measures, '') || ' ' ||
          coalesce(indications, '') || ' ' || coalesce(interpretation, '') || ' ' ||
          coalesce(tags::text, '') || ' ' || slug)::text
  FROM lab_tests WHERE published = true

  UNION ALL
  -- Evidências não possuem título editorial separado. O statement truncado é
  -- apenas o rótulo da lista; a declaração completa permanece no snippet.
  SELECT 'evidencia', slug::text, left(statement, 180)::text,
         ('Classe ' || recommendation_class || ' · nível ' || evidence_level)::text,
         theme::text, NULL::text, year, coalesce(summary, statement, '')::text,
         search_vector,
         (coalesce(statement, '') || ' ' || coalesce(summary, '') || ' ' ||
          coalesce(theme, '') || ' ' || coalesce(society, '') || ' ' ||
          coalesce(guideline_title, '') || ' ' || coalesce(tags::text, '') || ' ' || slug)::text
  FROM evidence_records WHERE published = true

  UNION ALL
  SELECT 'estudo', slug::text, title::text, study_type::text, theme::text,
         NULL::text, year,
         (coalesce(summary, '') || ' ' || coalesce(key_findings, ''))::text,
         search_vector,
         (coalesce(title, '') || ' ' || coalesce(theme, '') || ' ' ||
          coalesce(study_type, '') || ' ' || coalesce(authors, '') || ' ' ||
          coalesce(journal, '') || ' ' || coalesce(summary, '') || ' ' ||
          coalesce(key_findings, '') || ' ' || coalesce(clinical_implications, '') || ' ' ||
          coalesce(tags::text, '') || ' ' || slug)::text
  FROM scientific_studies WHERE published = true

  UNION ALL
  SELECT 'medicamento', drugs.slug::text, generic_name::text, drug_class::text,
         'Farmacologia'::text, NULL::text, NULL::integer,
         (coalesce(brand_names::text, '') || ' ' ||
          coalesce(cmed.marcas, '') || ' ' || coalesce(mechanism, '') || ' ' ||
          coalesce(indications::text, ''))::text,
         to_tsvector('portuguese',
           coalesce(generic_name, '') || ' ' || coalesce(brand_names::text, '') || ' ' ||
           coalesce(cmed.marcas, '') || ' ' ||
           coalesce(drug_class, '') || ' ' || coalesce(mechanism, '') || ' ' ||
           coalesce(indications::text, '') || ' ' || coalesce(interactions::text, '')
         ),
         (coalesce(generic_name, '') || ' ' || coalesce(brand_names::text, '') || ' ' ||
          coalesce(cmed.marcas, '') || ' ' ||
          coalesce(drug_class, '') || ' ' || coalesce(mechanism, '') || ' ' ||
          coalesce(indications::text, '') || ' ' || coalesce(interactions::text, '') || ' ' || drugs.slug)::text
  FROM drugs
  LEFT JOIN cmed_atual cmed ON cmed.drug_id = drugs.id
  WHERE drugs.published = true

  UNION ALL
  SELECT 'caso_clinico', slug::text, titulo::text, coalesce(nivel, 'caso clínico')::text,
         tema::text, NULL::text, NULL::integer,
         (coalesce(enunciado, '') || ' ' || coalesce(pergunta, '') || ' ' || coalesce(explicacao, ''))::text,
         to_tsvector('portuguese',
           coalesce(titulo, '') || ' ' || coalesce(tema, '') || ' ' ||
           coalesce(enunciado, '') || ' ' || coalesce(pergunta, '') || ' ' || coalesce(explicacao, '')
         ),
         (coalesce(titulo, '') || ' ' || coalesce(tema, '') || ' ' ||
          coalesce(enunciado, '') || ' ' || coalesce(pergunta, '') || ' ' ||
          coalesce(explicacao, '') || ' ' || slug)::text
  FROM clinical_cases WHERE published = true

  UNION ALL
  SELECT 'trilha', slug::text, titulo::text, coalesce(nivel, 'trilha')::text,
         tema::text, NULL::text, NULL::integer, coalesce(objetivo, '')::text,
         to_tsvector('portuguese',
           coalesce(titulo, '') || ' ' || coalesce(tema, '') || ' ' ||
           coalesce(objetivo, '') || ' ' || coalesce(etapas::text, '')
         ),
         (coalesce(titulo, '') || ' ' || coalesce(tema, '') || ' ' ||
          coalesce(objetivo, '') || ' ' || coalesce(etapas::text, '') || ' ' || slug)::text
  FROM study_tracks WHERE published = true

  UNION ALL
  SELECT 'checklist', slug::text, condicao::text, coalesce(scope_type, 'checklist')::text,
         theme::text, NULL::text, NULL::integer, coalesce(resumo, '')::text,
         to_tsvector('portuguese',
           coalesce(condicao, '') || ' ' || coalesce(theme, '') || ' ' ||
           coalesce(resumo, '') || ' ' || coalesce(itens::text, '')
         ),
         (coalesce(condicao, '') || ' ' || coalesce(theme, '') || ' ' ||
          coalesce(resumo, '') || ' ' || coalesce(itens::text, '') || ' ' || slug)::text
  FROM discharge_checklists WHERE published = true

  UNION ALL
  SELECT 'material_paciente', slug::text, titulo::text, 'material para paciente'::text,
         tema::text, NULL::text, NULL::integer,
         (coalesce(subtitulo, '') || ' ' || coalesce(resumo, ''))::text,
         to_tsvector('portuguese',
           coalesce(titulo, '') || ' ' || coalesce(subtitulo, '') || ' ' ||
           coalesce(tema, '') || ' ' || coalesce(resumo, '') || ' ' ||
           coalesce(secoes::text, '') || ' ' || coalesce(sinais_de_alerta::text, '')
         ),
         (coalesce(titulo, '') || ' ' || coalesce(subtitulo, '') || ' ' ||
          coalesce(tema, '') || ' ' || coalesce(resumo, '') || ' ' ||
          coalesce(secoes::text, '') || ' ' || coalesce(sinais_de_alerta::text, '') || ' ' || slug)::text
  FROM patient_materials WHERE published = true

  UNION ALL
  SELECT 'emergencia', slug::text, titulo::text, 'protocolo de emergência'::text,
         NULL::text, NULL::text, NULL::integer, coalesce(gatilho, '')::text,
         to_tsvector('portuguese',
           coalesce(titulo, '') || ' ' || coalesce(gatilho, '') || ' ' ||
           coalesce(documento_slug, '') || ' ' || coalesce(relacionados::text, '')
         ),
         (coalesce(titulo, '') || ' ' || coalesce(gatilho, '') || ' ' ||
          coalesce(documento_slug, '') || ' ' || coalesce(relacionados::text, '') || ' ' || slug)::text
  FROM emergency_protocols WHERE published = true

  UNION ALL
  SELECT 'doenca', slug::text, name::text, category::text, area::text,
         NULL::text, NULL::integer, coalesce(summary, '')::text,
         to_tsvector('portuguese',
           coalesce(name, '') || ' ' || coalesce(aliases::text, '') || ' ' ||
           coalesce(area, '') || ' ' || coalesce(category, '') || ' ' ||
           coalesce(summary, '') || ' ' || coalesce(presentation::text, '') || ' ' ||
           coalesce(differentials::text, '') || ' ' || coalesce(tags::text, '')
         ),
         (coalesce(name, '') || ' ' || coalesce(aliases::text, '') || ' ' ||
          coalesce(area, '') || ' ' || coalesce(category, '') || ' ' ||
          coalesce(summary, '') || ' ' || coalesce(presentation::text, '') || ' ' ||
          coalesce(differentials::text, '') || ' ' || coalesce(tags::text, '') || ' ' || slug)::text
  FROM specialty_diseases WHERE published = true

  UNION ALL
  SELECT 'triagem_sintoma', slug::text, name::text, 'triagem por sintomas'::text,
         array_to_string(coalesce(areas, ARRAY[]::varchar[]), ' · ')::text,
         NULL::text, NULL::integer, coalesce(summary, '')::text,
         to_tsvector('portuguese',
           coalesce(name, '') || ' ' || coalesce(aliases::text, '') || ' ' ||
           coalesce(areas::text, '') || ' ' || coalesce(summary, '') || ' ' ||
           coalesce(questions::text, '') || ' ' || coalesce(differentials::text, '') || ' ' ||
           coalesce(tags::text, '')
         ),
         (coalesce(name, '') || ' ' || coalesce(aliases::text, '') || ' ' ||
          coalesce(areas::text, '') || ' ' || coalesce(summary, '') || ' ' ||
          coalesce(questions::text, '') || ' ' || coalesce(differentials::text, '') || ' ' ||
          coalesce(tags::text, '') || ' ' || slug)::text
  FROM symptom_triage_guides WHERE published = true
"""

# Remova envelopes internos antes de o PostgreSQL produzir fragmentos. Se a
# limpeza acontecesse depois de `ts_headline`, o fragmento poderia conter só o
# marcador inicial ou receber `<mark>` dentro do próprio token, tornando o
# bloco impossível de reconhecer com segurança. A backreference exige que os
# marcadores inicial e final pertençam à mesma diretriz.
INTERNAL_OVERRIDE_SQL_PATTERN = (
    r"<!--[[:space:]]*corvia-intelligence:([^>:[:space:]]+):plain:start"
    r"[[:space:]]*-->.*?<!--[[:space:]]*corvia-intelligence:\1:plain:end"
    r"[[:space:]]*-->[[:space:]]*"
)
INTERNAL_MARKER_SQL_PATTERN = (
    r"<!--[[:space:]]*corvia-intelligence:[^>]*:plain:(start|end)"
    r"[[:space:]]*-->[[:space:]]*"
)


def _search_sql(match_predicate: str):
    return text(f"""
WITH cmed_atual AS (
  SELECT apresentacao.drug_id,
         string_agg(DISTINCT apresentacao.produto, ' ') AS marcas
  FROM cmed_apresentacoes apresentacao
  WHERE apresentacao.cmed_versao_id = (SELECT max(id) FROM cmed_versoes)
    AND apresentacao.drug_id IS NOT NULL
  GROUP BY apresentacao.drug_id
), achados AS (
{CATALOG_SQL}
), consulta AS (
  SELECT plainto_tsquery('portuguese', CAST(:q AS text)) AS tsq,
         '%' || CAST(:q_like AS text) || '%' AS trecho
), filtrados AS (
  SELECT achados.*,
         coalesce(ts_rank(v, consulta.tsq), 0)
           + CASE WHEN unaccent(lower(title)) = unaccent(lower(CAST(:q AS text))) THEN 3.0
                  WHEN unaccent(lower(title)) LIKE unaccent(lower(CAST(:q AS text))) || '%' THEN 1.2
                  ELSE 0.0 END AS rank
  FROM achados CROSS JOIN consulta
  WHERE (CAST(:frente AS text) IS NULL OR frente = CAST(:frente AS text))
    AND ({match_predicate})
)
SELECT frente, slug, title, kind, theme, source_tier, ano,
       ts_headline(
                   'portuguese',
                   regexp_replace(
                     regexp_replace(
                       corpo,
                       CAST(:internal_override_pattern AS text),
                       '',
                       'gis'
                     ),
                     CAST(:internal_marker_pattern AS text),
                     '',
                     'gi'
                   ),
                   plainto_tsquery('portuguese', CAST(:q AS text)),
                   'StartSel=<mark>,StopSel=</mark>,MaxFragments=2,FragmentDelimiter= … ') AS snippet,
       rank
FROM filtrados
ORDER BY rank DESC, title, slug
LIMIT :limit OFFSET :offset
""")


def _count_sql(match_predicate: str):
    return text(f"""
WITH cmed_atual AS (
  SELECT apresentacao.drug_id,
         string_agg(DISTINCT apresentacao.produto, ' ') AS marcas
  FROM cmed_apresentacoes apresentacao
  WHERE apresentacao.cmed_versao_id = (SELECT max(id) FROM cmed_versoes)
    AND apresentacao.drug_id IS NOT NULL
  GROUP BY apresentacao.drug_id
), achados AS (
{CATALOG_SQL}
), consulta AS (
  SELECT plainto_tsquery('portuguese', CAST(:q AS text)) AS tsq,
         '%' || CAST(:q_like AS text) || '%' AS trecho
)
SELECT frente, count(*) AS total
FROM achados CROSS JOIN consulta
WHERE (CAST(:frente AS text) IS NULL OR frente = CAST(:frente AS text))
  AND ({match_predicate})
GROUP BY frente
ORDER BY frente
""")


# O caminho normal usa somente full-text search. Assim, as cinco coleções com
# `search_vector` preservam os índices GIN e a consulta não força um
# `LIKE '%...%'` sobre todos os corpos. A busca literal — necessária para
# fragmentos, fórmulas e grafias parciais — só é executada quando a consulta
# indexada não encontra nenhum item.
FULL_TEXT_MATCH = "v @@ consulta.tsq"
LITERAL_MATCH = (
    "unaccent(lower(translate(pesquisavel, '₀₁₂₃₄₅₆₇₈₉', "
    "'0123456789'))) LIKE consulta.trecho ESCAPE '!'"
)
SQL = _search_sql(FULL_TEXT_MATCH)
COUNT_SQL = _count_sql(FULL_TEXT_MATCH)
LITERAL_SQL = _search_sql(LITERAL_MATCH)
LITERAL_COUNT_SQL = _count_sql(LITERAL_MATCH)


PRIMARY_DISEASE_SQL = text("""
WITH candidatas AS (
  SELECT slug, name, summary, area, category, prevalence_rank,
         CASE
           WHEN unaccent(lower(name)) = unaccent(lower(CAST(:q AS text))) THEN 0
           WHEN unaccent(lower(replace(slug, '-', ' '))) = unaccent(lower(CAST(:q AS text))) THEN 1
           ELSE 2
         END AS match_priority
  FROM specialty_diseases
  WHERE published = true
    AND (
      unaccent(lower(name)) = unaccent(lower(CAST(:q AS text)))
      OR unaccent(lower(replace(slug, '-', ' '))) = unaccent(lower(CAST(:q AS text)))
      OR EXISTS (
        SELECT 1
        FROM unnest(coalesce(aliases, ARRAY[]::varchar[])) AS alias
        WHERE unaccent(lower(alias)) = unaccent(lower(CAST(:q AS text)))
      )
    )
), melhor_nivel AS (
  SELECT min(match_priority) AS match_priority
  FROM candidatas
)
SELECT slug, name, summary, area, category
FROM candidatas
WHERE match_priority = (SELECT match_priority FROM melhor_nivel)
ORDER BY prevalence_rank, name
LIMIT 2
""")


def normalizar(valor: str) -> str:
    valor = valor.translate(str.maketrans("₀₁₂₃₄₅₆₇₈₉", "0123456789"))
    sem_acentos = "".join(
        char for char in unicodedata.normalize("NFD", valor)
        if unicodedata.category(char) != "Mn"
    )
    return re.sub(r"[^a-z0-9]+", " ", sem_acentos.casefold()).strip()


def literal_like(valor: str) -> str:
    valor = valor.translate(str.maketrans("₀₁₂₃₄₅₆₇₈₉", "0123456789"))
    sem_acentos = "".join(
        char for char in unicodedata.normalize("NFD", valor)
        if unicodedata.category(char) != "Mn"
    ).casefold()
    return sem_acentos.replace("!", "!!").replace("%", "!%").replace("_", "!_")


def calculadoras_encontradas(q: str) -> list[dict]:
    consulta = normalizar(q)
    if not consulta:
        return []
    termos = consulta.split()
    encontrados: list[tuple[int, str, dict]] = []
    for calculator in calc.REGISTRY.values():
        pesquisavel = normalizar(
            " ".join((
                calculator.slug, calculator.name, calculator.theme,
                calculator.purpose, calculator.reference,
            ))
        )
        if not all(termo in pesquisavel for termo in termos):
            continue
        nome = normalizar(calculator.name)
        slug = normalizar(calculator.slug)
        prioridade = 0 if consulta in {nome, slug} else (1 if nome.startswith(consulta) else 2)
        encontrados.append((prioridade, calculator.name.casefold(), {
            "frente": "calculadora",
            "slug": calculator.slug,
            "title": calculator.name,
            "kind": calculator.kind,
            "theme": calculator.theme,
            "source_tier": None,
            "ano": None,
            "snippet": calculator.purpose,
            "rank": 4.0 if prioridade == 0 else (2.0 if prioridade == 1 else 1.0),
        }))
    return [item for _, _, item in sorted(encontrados, key=lambda x: (x[0], x[1]))]
