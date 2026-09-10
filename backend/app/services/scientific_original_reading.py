"""Read licensed original JATS without invoking or relaxing translation processing.

The root article remains in its original language; translated sub-articles are
excluded from the textual reading view, while downloaded original bytes stay intact.
"""
import hashlib
import re
import xml.etree.ElementTree as ET
from app.services.scientific_xml_license import extract_article_license, ALLOWED_LICENSE_URL

MAX_ORIGINAL_BYTES = 8 * 1024 * 1024
MAX_ORIGINAL_TEXT_CHARS = 2_000_000
XML_LANG = "{http://www.w3.org/XML/1998/namespace}lang"
DOI = re.compile(r"10\.\d{4,9}/[-._;()/:A-Z0-9]+", re.I)

class OriginalReadError(ValueError):
    def __init__(self, status, reason):
        self.status, self.reason = status, reason
        super().__init__(reason)


def _doi(value):
    match = DOI.search(str(value or ""))
    if not match:
        return None
    result = match.group(0).rstrip(".,;").lower()
    while result.endswith(")") and result.count(")") > result.count("("):
        result = result[:-1]
    return result


def _tag(node):
    return node.tag.rsplit("}", 1)[-1]


def _render(node):
    """Readable text, including explicit operators for common MathML structures."""
    if node is None or _tag(node) == "sub-article":
        return ""
    tag = _tag(node)
    # MathML semantics can contain duplicated alternate serializations.
    if tag == "semantics":
        primary = next((child for child in node if _tag(child) not in ("annotation", "annotation-xml")), None)
        return _render(primary)
    children = [_render(child) for child in node]
    if tag == "mfrac" and len(children) == 2:
        return "(" + children[0] + ")/(" + children[1] + ")"
    if tag in ("msup", "msub") and len(children) == 2:
        return "(" + children[0] + ")" + ("^(" if tag == "msup" else "_(") + children[1] + ")"
    if tag == "msubsup" and len(children) == 3:
        return "(" + children[0] + ")_(" + children[1] + ")^(" + children[2] + ")"
    if tag == "msqrt":
        return "sqrt(" + "".join(children) + ")"
    if tag == "mroot" and len(children) == 2:
        return "root(" + children[1] + ", " + children[0] + ")"
    value = node.text or ""
    for child, child_text in zip(node, children):
        child_tag = _tag(child)
        if child_tag == "sup": child_text = "^(" + child_text + ")"
        elif child_tag == "sub": child_text = "_(" + child_text + ")"
        elif child_tag in ("td", "th", "mtd"): child_text = "\t" + child_text + "\t"
        elif child_tag in ("tr", "mtr"): child_text = "\n" + child_text + "\n"
        value += child_text + (child.tail or "")
    return value.strip()


def parse_original_fulltext(xml, expected_doi, *, verified_license_url=None, verified_source_sha256=None):
    """Read only. Optional licence proof comes from a curated server-side import.

    A supplied licence never changes the original XML and is accepted only when
    its exact bytes match the separately verified source hash. Public requests
    must not supply these arguments; the API uses matching persisted provenance.
    """
    if not isinstance(xml, bytes) or len(xml) > MAX_ORIGINAL_BYTES:
        raise OriginalReadError("blocked_fulltext", "Original ultrapassa o limite seguro de leitura.")
    if b"\x00" in xml or xml.startswith((b"\xff\xfe", b"\xfe\xff")) or re.search(br"<!ENTITY|<!DOCTYPE[^>]*\[|<xi:include", xml, re.I):
        raise OriginalReadError("blocked_fulltext", "XML original não pôde ser validado com segurança.")
    try:
        root = ET.fromstring(xml)
    except ET.ParseError as exc:
        raise OriginalReadError("blocked_fulltext", "Arquivo não contém XML científico válido.") from exc
    if any(node.tag.startswith("{http://www.w3.org/2001/XInclude}") for node in root.iter()):
        raise OriginalReadError("blocked_fulltext", "Inclusão externa não permitida no original.")
    stack = [(root, 0)]
    while stack:
        node, depth = stack.pop()
        if depth > 128:
            raise OriginalReadError("blocked_fulltext", "Estrutura XML excede o limite seguro de leitura.")
        stack.extend((child, depth + 1) for child in node)
    meta = root.find("./front/article-meta")
    if root.tag != "article" or meta is None:
        raise OriginalReadError("blocked_fulltext", "Arquivo não contém artigo científico integral.")
    canonical_doi = _doi(expected_doi)
    if not canonical_doi or canonical_doi not in {_doi(node.text) for node in meta.findall("./article-id") if node.get("pub-id-type") == "doi"}:
        raise OriginalReadError("blocked_identity", "DOI do original difere da identidade registrada.")
    license_url = extract_article_license(meta)
    # External proof can resolve omitted machine-readable metadata, but must
    # never override an explicit restricted, inactive, or conflicting license.
    explicit_license = any(
        child.tag == "{http://www.niso.org/schemas/ali/1.0/}license_ref" or
        any(value.startswith(("http://", "https://")) for value in child.attrib.values())
        for license_node in meta.findall("./permissions/license") for child in license_node.iter()
    )
    if not license_url and not explicit_license and isinstance(verified_license_url, str) and ALLOWED_LICENSE_URL.fullmatch(verified_license_url):
        if isinstance(verified_source_sha256, str) and re.fullmatch(r"[0-9a-f]{64}", verified_source_sha256) and hashlib.sha256(xml).hexdigest() == verified_source_sha256:
            license_url = verified_license_url
    if not license_url:
        raise OriginalReadError("blocked_license", "Licença de reutilização do original não confirmada.")
    body = root.find("./body")
    if body is None or len(_render(body)) < 300:
        raise OriginalReadError("blocked_fulltext", "Corpo integral do original não confirmado.")
    blocks = []
    block_tags = {"p", "title", "article-title", "subtitle", "ref", "tr", "contrib", "label", "license-p", "disp-formula", "inline-formula", "math"}
    def walk(node):
        tag = _tag(node)
        if tag == "sub-article": return
        if tag in block_tags:
            value = _render(node)
            if value: blocks.append(value)
            return
        if node.text and node.text.strip(): blocks.append(node.text.strip())
        for child in node:
            walk(child)
            if child.tail and child.tail.strip(): blocks.append(child.tail.strip())
    try:
        walk(root)
    except RecursionError as exc:
        raise OriginalReadError("blocked_fulltext", "Estrutura XML excede o limite seguro de leitura.") from exc
    fulltext = "\n\n".join(blocks)
    if len(fulltext) > MAX_ORIGINAL_TEXT_CHARS:
        raise OriginalReadError("blocked_fulltext", "Texto original ultrapassa o limite seguro; nenhum trecho foi truncado.")
    title = _render(meta.find("./title-group/article-title"))
    authors = [_render(node) for node in meta.findall("./contrib-group/contrib") if node.get("contrib-type") == "author"]
    language = root.get(XML_LANG, "und").lower()
    attribution = f"{title}. Autores: {'; '.join(authors) or 'Consulte autoria no original'}. Fonte: https://doi.org/{canonical_doi}. Licença: {license_url}."
    return {"text": fulltext, "title": title, "authors": authors, "attribution": attribution,
            "license_url": license_url, "language": language,
            "coverage": {"source_format": "jats_xml", "scope": "root_article_text", "original_text_complete": True,
                         "figures": "captions_only", "formulas": "text_representation_only", "tables": "text", "supplements": "not_included",
                         "excluded_translated_subarticles": len(root.findall("./sub-article"))}}
