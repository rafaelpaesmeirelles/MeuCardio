"""Licensed acquired originals are bibliographic sources, never clinical approvals.

One eligibility predicate is shared by search, reader and favorites. No writes,
provider requests, decryption or inference occur while discovering an original.
"""
from types import SimpleNamespace
import re
from sqlalchemy import text
from app.models.scientific_publication_asset import ScientificPublicationAsset as Asset
from app.services.guideline_source_trust import TRUSTED_OFFICIAL_HOSTS
from app.services.calculators import REGISTRY as CALCULATORS

DOI_PATTERN = r'10\.[0-9]{4,9}/[-._;()/A-Z0-9:]+'
LICENSE_PATTERN = r'^https?://creativecommons\.org/(licenses/by/(1\.0|2\.0|2\.5|3\.0|4\.0)|publicdomain/zero/1\.0)/?$'


def _quoted(value):
    return "'" + value.replace("'", "''").replace(":", "\\:") + "'"


def _references_sql(alias, fields):
    # Only dedicated source metadata; never serialize clinical bodies through
    # to_jsonb(row) just to extract one reference field.
    return " || ' ' || ".join(f"coalesce({alias}.{field}::text, '')" for field in fields)


def doi_rows_sql(reference_sql):
    # Every DOI is extracted independently. Preserve balanced DOI parentheses;
    # discard only unmatched closing punctuation from a bibliographic citation.
    return f"""SELECT base || repeat(')', least(length(clean) - length(base), greatest(
      length(base) - length(replace(base, '(', '')) - length(base) + length(replace(base, ')', '')), 0))) AS doi
      FROM regexp_matches({reference_sql}, {_quoted(DOI_PATTERN)}, 'gi') token
      CROSS JOIN LATERAL (SELECT rtrim(lower(token[1]), '.,;') AS clean) d0
      CROSS JOIN LATERAL (SELECT rtrim(clean, ')') AS base) d1"""


def doi_matches_sql(reference_sql, doi_sql):
    return f"EXISTS (SELECT 1 FROM ({doi_rows_sql(reference_sql)}) extracted WHERE extracted.doi = lower({doi_sql}))"


# Published objects can expose their acquired references; quarantined/private
# objects cannot establish a public source. This is a reference check, not a
# text scan or a change to the objects' clinical/editorial classification.
PUBLIC_TABLES = (
    ('documents', '', ('source_refs',)),
    ('scientific_studies', " AND src.review_status = 'revisado'", ('doi', 'url')),
    ('evidence_records', '', ('reference', 'source_url', 'doi')),
    ('specialty_diseases', '', ('source_refs', 'source_urls')),
    ('symptom_triage_guides', '', ('source_refs', 'source_urls')),
    ('drugs', '', ('references',)), ('lab_tests', '', ('source_refs',)),
    ('clinical_cases', '', ('source_refs',)), ('patient_materials', '', ('fontes',)),
    ('gallery_images', '', ('source_url',)), ('discharge_checklists', '', ('source_refs',)),
)
# Study tracks and emergency protocols reference these same public objects;
# they do not carry a separate direct bibliographic source column.



def _trusted_guideline_sql():
    # Mirrors the source registry without promoting acquisition to guideline
    # review. A DOI is mandatory for this acquired-original path.
    host = "lower(substring(coalesce(g.url, '') from '^https?://([^/:?#@]+)(?:[:/?#]|$)'))"
    pairs = ' OR '.join(
        "(upper(trim(g.org)) = " + _quoted(org) + " AND " + host + " IN (" +
        ', '.join(_quoted(h) for h in sorted(hosts)) + "))"
        for org, hosts in sorted(TRUSTED_OFFICIAL_HOSTS.items()))
    orgs = ', '.join(_quoted(org) for org in sorted(TRUSTED_OFFICIAL_HOSTS))
    return f"(upper(trim(g.org)) IN ({orgs}) AND (upper(trim(g.org)) = 'CROSSREF' OR nullif(trim(coalesce(g.url, '')), '') IS NULL OR {host} = 'doi.org' OR {pairs}))"


def public_source_dois_sql():
    # Uncorrelated source metadata scan: each corpus front is visited once,
    # regardless of how many acquired originals await discovery. No bodies.
    references = [f"SELECT {_references_sql('src', fields)} AS reference FROM {table} src WHERE src.published = true{extra}" for table, extra, fields in PUBLIC_TABLES]
    references.append(f"SELECT coalesce(g.doi, '') FROM guidelines g WHERE {_trusted_guideline_sql()}")
    calculator_dois = set()
    for calculator in CALCULATORS.values():
        for doi in re.findall(DOI_PATTERN, str(calculator.reference or ''), flags=re.I):
            doi = doi.rstrip('.,;').lower()
            while doi.endswith(')') and doi.count(')') > doi.count('('): doi = doi[:-1]
            calculator_dois.add(doi)
    if calculator_dois:
        references.append('SELECT reference FROM (VALUES ' + ', '.join('(' + _quoted(doi) + ')' for doi in sorted(calculator_dois)) + ') calculator_sources(reference)')
    return "WITH public_source_references AS MATERIALIZED (" + ' UNION ALL '.join(references) + ") SELECT DISTINCT extracted.doi FROM public_source_references public_source CROSS JOIN LATERAL (" + doi_rows_sql('public_source.reference') + ') extracted'


def public_source_sql(alias):
    return f"lower({alias}.doi) IN ({public_source_dois_sql()})"


def public_asset_sql(alias='scientific_publication_assets'):
    if not alias.replace('_', '').isalnum():
        raise ValueError('Invalid internal asset alias')
    return rf"""(
      {alias}.source_key ~ '^[0-9a-f]{{64}}$'
      AND {alias}.source_sha256 ~ '^[0-9a-f]{{64}}$'
      AND nullif(trim({alias}.original_storage_key), '') IS NOT NULL
      AND {alias}.license_url ~ {_quoted(LICENSE_PATTERN)}
      AND {alias}.doi ~ '^10\.[0-9]{{4,9}}/[^[:space:]]+$'
      AND {alias}.source_key = encode(sha256(convert_to('doi:' || lower({alias}.doi), 'UTF8')), 'hex')
      AND {alias}.status NOT IN ('blocked_identity', 'blocked_license')
      AND {public_source_sql(alias)}
    )"""


def public_asset_query(db):
    return db.query(Asset).filter(text(public_asset_sql()))


def public_asset_entity(asset):
    """Reader adapter only: no fabricated Document/review/publication state."""
    return SimpleNamespace(id=asset.id, slug=asset.source_key,
        title=(asset.progress or {}).get('title') or asset.doi,
        doi=asset.doi, url=asset.source_url, summary=None)


# Representation requires an article identity, not a citation in a guide.
# Normalize each canonical identity once and reuse it for deduplication and
# original-title discovery through the existing public document/study route.
CANONICAL_ORIGINAL_RELATIONS_SQL = f"""
  SELECT 'documento'::text AS frente, represented.slug, identified.doi
  FROM documents represented
  JOIN guideline_links gl ON gl.item_id = represented.id
    AND gl.item_type = 'intelligence_document' AND gl.confirmado = true
  JOIN guidelines g ON g.id = gl.guideline_id
  CROSS JOIN LATERAL ({doi_rows_sql("coalesce(g.doi, '')")}) identified
  WHERE represented.published = true
    AND {doi_matches_sql(_references_sql('represented', ('source_refs',)), 'identified.doi')}
  UNION ALL
  SELECT 'estudo'::text, represented.slug, identified.doi
  FROM scientific_studies represented
  CROSS JOIN LATERAL ({doi_rows_sql("coalesce(represented.doi, '')")}) identified
  WHERE represented.published = true AND represented.review_status = 'revisado'
"""

ELIGIBLE_ORIGINALS_SQL = f"""
  SELECT a.id, a.source_key, a.doi, a.source_url, a.progress
  FROM scientific_publication_assets a WHERE {public_asset_sql('a')}
"""

ORIGINAL_BRIDGES_SQL = """
  SELECT represented.frente, represented.slug,
    (coalesce(a.progress->>'title', '') || ' ' || coalesce(a.progress->>'authors', '') || ' ' || a.doi) AS metadata
  FROM eligible_publication_originals a
  JOIN canonical_original_relations represented ON represented.doi = lower(a.doi)
"""


ORIGINAL_CATALOG_SQL = f"""
  SELECT 'publicacao_original'::text AS frente, a.source_key::text AS slug,
    coalesce(nullif(a.progress->>'title', ''), a.doi)::text AS title,
    'original científico'::text AS kind, NULL::text AS theme,
    NULL::text AS source_tier, NULL::integer AS ano,
    ('Original científico · DOI: ' || a.doi || ' · ' || coalesce(a.progress->>'authors', ''))::text AS corpo,
    to_tsvector('portuguese', coalesce(a.progress->>'title', '') || ' ' || coalesce(a.progress->>'authors', '') || ' ' || a.doi) AS v,
    (coalesce(a.progress->>'title', '') || ' ' || coalesce(a.progress->>'authors', '') || ' ' || a.doi)::text AS pesquisavel
  FROM eligible_publication_originals a
  WHERE NOT EXISTS (SELECT 1 FROM canonical_original_relations represented WHERE represented.doi = lower(a.doi))
"""
