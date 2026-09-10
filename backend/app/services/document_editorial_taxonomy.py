"""Editorial sections derive from declared type, never words in a title.

A section is a presentation facet: a Document remains a Document and keeps
its /biblioteca URL even when displayed alongside ScientificStudy records.
"""

DOCUMENT_KIND_SECTIONS = {
    "estudo": "estudo", "study": "estudo", "artigo": "estudo",
    "ensaio_clinico": "estudo", "estudo_observacional": "estudo",
    "revisao": "estudo", "revisão": "estudo", "revisao_sistematica": "estudo",
    "revisao_narrativa": "estudo", "meta_analise": "estudo", "metanalise": "estudo",
    "diretriz": "diretriz", "guideline": "diretriz", "consenso": "diretriz",
    "consensus": "diretriz", "posicionamento": "diretriz",
    "fluxograma": "fluxo", "flowchart": "fluxo", "algoritmo": "fluxo",
    "protocolo": "conduta", "conduta": "conduta",
    "trilha": "trilha", "calculadora": "calculadora",
    "documento": "geral", "modulo": "geral", "farmacologia": "geral",
    "errata": "geral", "preprint": "estudo",
}
DOCUMENT_SECTIONS = frozenset(DOCUMENT_KIND_SECTIONS.values())


def document_section(kind: str | None) -> str:
    return DOCUMENT_KIND_SECTIONS.get(str(kind or "").strip().lower(), "geral")


def document_section_sql(kind_column: str = "kind") -> str:
    # Column names are internal constants, never request input.
    if not kind_column.replace("_", "").replace(".", "").isalnum():
        raise ValueError("Invalid internal kind column")
    clauses = " ".join(f"WHEN '{kind}' THEN '{section}'" for kind, section in DOCUMENT_KIND_SECTIONS.items())
    return f"CASE lower(trim(coalesce({kind_column}, ''))) {clauses} ELSE 'geral' END"


def document_section_expression(column):
    from sqlalchemy import case, func
    return case(DOCUMENT_KIND_SECTIONS, value=func.lower(func.trim(func.coalesce(column, ""))), else_="geral")


def study_section(kind: str | None) -> str:
    return "diretriz" if document_section(kind) == "diretriz" else "estudo"


def study_section_sql(kind_column: str = "kind") -> str:
    return f"CASE WHEN ({document_section_sql(kind_column)}) = 'diretriz' THEN 'diretriz' ELSE 'estudo' END"


def study_section_expression(column):
    from sqlalchemy import case
    return case((document_section_expression(column) == "diretriz", "diretriz"), else_="estudo")
