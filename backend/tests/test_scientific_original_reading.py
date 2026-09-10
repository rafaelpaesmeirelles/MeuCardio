"""Original reading boundaries; no application database, network, or paid AI."""
import ast
import hashlib
import importlib.util
from pathlib import Path
from types import SimpleNamespace
import sys
import pytest

BASE = Path(__file__).parents[1]
sys.path.insert(0, str(BASE))
from app.services.scientific_original_reading import parse_original_fulltext, OriginalReadError

DOI = "10.36660/abc.20250621"
LICENSE = "https://creativecommons.org/licenses/by/4.0/"

def article(body=None, license_xml=None, extra="", language="pt"):
    body = body or ("Texto clínico original 123 mg. " * 20)
    license_xml = license_xml if license_xml is not None else '<ali:license_ref>'+LICENSE+'</ali:license_ref>'
    return ('<article xmlns:ali="http://www.niso.org/schemas/ali/1.0/" xml:lang="'+language+'"><front><article-meta><article-id pub-id-type="doi">'+DOI+'</article-id><title-group><article-title>Título original</article-title></title-group><permissions><license>'+license_xml+'</license></permissions></article-meta></front><body><p>'+body+'</p></body>'+extra+'</article>').encode()


def test_native_pt_long_original_is_read_without_concatenating_translation():
    xml = article(body="Texto português completo. " * 16000, extra='<sub-article article-type="translation" xml:lang="en"><body><p>DO NOT INCLUDE ENGLISH TRANSLATION</p></body></sub-article>')
    result = parse_original_fulltext(xml, DOI)
    assert len(result["text"]) > 300000
    assert "DO NOT INCLUDE" not in result["text"]
    assert result["language"] == "pt"
    assert result["coverage"]["excluded_translated_subarticles"] == 1
    assert "complete_text" not in result["coverage"]
    assert "translated_storage_key" not in result


def test_formula_text_keeps_fraction_power_and_subscript_operators():
    body = 'Texto clínico. ' * 40 + '<inline-formula><math xmlns="http://www.w3.org/1998/Math/MathML"><mfrac><msup><mi>x</mi><mn>2</mn></msup><msub><mi>y</mi><mn>1</mn></msub></mfrac></math></inline-formula>'
    result = parse_original_fulltext(article(body), DOI)
    assert "((x)^(2))/((y)_(1))" in result["text"]
    assert result["coverage"]["formulas"] == "text_representation_only"


def test_generic_license_uses_only_matching_verified_bytes():
    xml = article(license_xml='<license-p>Creative Commons Attribution License</license-p>')
    proof = {"verified_license_url": LICENSE, "verified_source_sha256": hashlib.sha256(xml).hexdigest()}
    assert parse_original_fulltext(xml, DOI, **proof)["license_url"] == LICENSE
    with pytest.raises(OriginalReadError, match="Licença"):
        parse_original_fulltext(xml, DOI)
    with pytest.raises(OriginalReadError, match="Licença"):
        parse_original_fulltext(xml+b" ", DOI, **proof)


@pytest.mark.parametrize("license_xml", [
    '<ali:license_ref>https://creativecommons.org/licenses/by-nc/4.0/</ali:license_ref>',
    '<ali:license_ref start_date="2999-01-01">'+LICENSE+'</ali:license_ref>',
    '<license-p xmlns:xlink="http://www.w3.org/1999/xlink" xlink:href="https://example.org/restricted-license">Restricted</license-p>',
])
def test_external_proof_cannot_override_explicit_license(license_xml):
    xml = article(license_xml=license_xml)
    with pytest.raises(OriginalReadError, match="Licença"):
        parse_original_fulltext(xml, DOI, verified_license_url=LICENSE, verified_source_sha256=hashlib.sha256(xml).hexdigest())


@pytest.mark.parametrize("xml", [
    b'<!DOCTYPE article [<!ENTITY secret "abc">]><article/>',
    b'<article xmlns:other="http://www.w3.org/2001/XInclude"><other:include href="file:///etc/passwd"/></article>',
    b'\xff\xfeinvalid', b'\x00invalid', b'<article>',
    b'x' * (8 * 1024 * 1024 + 1),
])
def test_unsafe_or_oversized_xml_is_rejected(xml):
    with pytest.raises(OriginalReadError): parse_original_fulltext(xml, DOI)


def test_doi_mismatch_is_not_licensed_identity():
    with pytest.raises(OriginalReadError) as error: parse_original_fulltext(article(), '10.1000/other')
    assert error.value.status == 'blocked_identity'


def test_text_over_limit_is_rejected_without_truncation():
    with pytest.raises(OriginalReadError, match="nenhum trecho foi truncado"):
        parse_original_fulltext(article(body='x' * 2000001), DOI)


def test_nested_depth_and_abstract_only_are_rejected():
    with pytest.raises(OriginalReadError): parse_original_fulltext(article(body='<x>'*130+'text'+'</x>'*130), DOI)
    with pytest.raises(OriginalReadError): parse_original_fulltext(article(body='Only abstract'), DOI)


# Exercise the real endpoint body in isolation: imports/dependencies intentionally
# omitted so the production database and paid services are never initialized.
class HttpError(Exception):
    def __init__(self, status_code, detail): self.status_code, self.detail = status_code, detail

class Reply:
    def __init__(self, **kwargs): self.__dict__.update(kwargs)


def endpoint(asset, content, allowed=True, stored=None):
    path = BASE / 'app/api/scientific_reading.py'
    node = next(n for n in ast.parse(path.read_text()).body if isinstance(n, ast.FunctionDef) and n.name == 'artifact')
    node.decorator_list = []
    for arg in node.args.args: arg.annotation = None
    node.args.defaults = [ast.Constant(None)] * len(node.args.defaults)
    ns = dict(hashlib=hashlib, HTTPException=HttpError, Response=Reply, ScientificPublicationAsset=object,
              get_entity=lambda *a: object(), entity_sources=lambda *a: [{'key': asset.source_key}] if allowed else [],
              cofre=SimpleNamespace(ler=lambda *a, **kw: (stored or {}).get(a[0], content), CofreIndisponivel=OSError), library_root=lambda: None,
              parse_original_fulltext=parse_original_fulltext, OriginalReadError=OriginalReadError)
    exec(compile(ast.fix_missing_locations(ast.Module(body=[node], type_ignores=[])), str(path), 'exec'), ns)
    query = SimpleNamespace(filter_by=lambda **kw: SimpleNamespace(first=lambda: asset))
    return lambda variant: ns['artifact']('publicacao_original', asset.source_key, asset.source_key, variant, SimpleNamespace(query=lambda *a: query))


def asset_for(content, source_format='jats_xml'):
    return SimpleNamespace(id=12, source_key='b'*64, source_sha256=hashlib.sha256(content).hexdigest(), doi=DOI,
        original_storage_key='original.bin', translated_storage_key=None, license_url=LICENSE, status='original_ready',
        coverage={'source_format': source_format}, progress={})


def test_pdf_original_is_served_as_pdf_without_xml_extraction():
    content = b'%PDF-1.7 test original'
    call = endpoint(asset_for(content,'pdf'), content)
    reply = call('original')
    assert reply.media_type == 'application/pdf' and reply.content == content
    assert '.pdf"' in reply.headers['Content-Disposition']
    with pytest.raises(HttpError) as error: call('original-text')
    assert error.value.status_code == 404


def test_original_scope_hash_and_pdf_signature_remain_required():
    content = b'%PDF-1.7 test original'
    with pytest.raises(HttpError) as error: endpoint(asset_for(content,'pdf'), content, False)('original')
    assert error.value.status_code == 404
    with pytest.raises(HttpError) as error: endpoint(asset_for(content,'pdf'), content+b'changed')('original')
    assert error.value.status_code == 503
    with pytest.raises(HttpError) as error: endpoint(asset_for(b'notpdf','pdf'), b'notpdf')('original')
    assert error.value.status_code == 503


def test_endpoint_external_license_requires_persisted_provenance_matching_asset():
    xml = article(license_xml='<license-p>Creative Commons Attribution License</license-p>')
    asset = asset_for(xml)
    with pytest.raises(HttpError) as error: endpoint(asset, xml)('original-text')
    assert error.value.status_code == 503
    asset.progress = {'import_provenance': {'source_sha256': asset.source_sha256, 'license_url': LICENSE}}
    assert endpoint(asset, xml)('original-text').media_type.startswith('text/plain')
    asset.progress['import_provenance']['source_sha256'] = '0'*64
    with pytest.raises(HttpError) as error: endpoint(asset, xml)('original-text')
    assert error.value.status_code == 503


def test_original_ready_cannot_be_served_as_complete_translation():
    xml=article()
    with pytest.raises(HttpError) as error: endpoint(asset_for(xml),xml)('translation')
    assert error.value.status_code == 404


def test_pdf_extracted_original_text_requires_matching_provenance_and_text_hash():
    content = b'%PDF-1.7 original erratum'
    extracted = 'Texto editorial integral da errata.'.encode()
    asset = asset_for(content, 'pdf')
    for text_proof, status in [
        ({}, 404),
        ({'storage_key': 'text.bin', 'sha256': hashlib.sha256(extracted).hexdigest(), 'source_sha256': '0'*64, 'source_format': 'pdf'}, 404),
        ({'storage_key': 'text.bin', 'sha256': '0'*64, 'source_sha256': asset.source_sha256, 'source_format': 'pdf'}, 503),
    ]:
        asset.progress = {'original_text': text_proof}
        with pytest.raises(HttpError) as error:
            endpoint(asset, content, stored={'text.bin': extracted})('original-text')
        assert error.value.status_code == status


def test_pdf_extracted_original_text_is_readable_without_claiming_translation():
    content = b'%PDF-1.7 original erratum'
    extracted = 'ERRATA\nCorreção editorial completa publicada pelos autores.'.encode('utf-8')
    asset = asset_for(content, 'pdf')
    asset.progress = {'original_text': {'storage_key': 'text.bin', 'sha256': hashlib.sha256(extracted).hexdigest(),
                                      'source_sha256': asset.source_sha256, 'source_format': 'pdf'}}
    call = endpoint(asset, content, stored={'text.bin': extracted})
    reply = call('original-text')
    assert reply.media_type == 'text/plain; charset=utf-8'
    assert reply.content.endswith(extracted)
    assert 'Original em PDF — texto extraído; diagramação no arquivo original.' in reply.content.decode()
    assert 'Nenhuma tradução por IA foi realizada.' in reply.content.decode()
    assert call('original').content == content
    with pytest.raises(HttpError) as error: call('translation')
    assert error.value.status_code == 404
