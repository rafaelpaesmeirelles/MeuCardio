"""NISO ALI parsing, independently exercising the original article scope."""
import importlib.util
from pathlib import Path
import xml.etree.ElementTree as ET
import pytest
spec = importlib.util.spec_from_file_location("license_reader", Path(__file__).parents[1]/"app/services/scientific_xml_license.py")
mod=importlib.util.module_from_spec(spec)
spec.loader.exec_module(mod)

def meta(inner):
    return ET.fromstring('<article-meta xmlns:ali="http://www.niso.org/schemas/ali/1.0/" xmlns:xlink="http://www.w3.org/1999/xlink">'+inner+'</article-meta>')

@pytest.mark.parametrize('url', ['https://creativecommons.org/licenses/by/4.0/', 'http://creativecommons.org/licenses/by/3.0/', 'https://creativecommons.org/publicdomain/zero/1.0/'])
def test_niso_license_ref_text_is_supported(url):
    m=meta('<permissions><license><ali:license_ref content-type="ccbylicense" specific-use="textmining">'+url+'</ali:license_ref></license></permissions>')
    assert mod.extract_article_license(m)==url

@pytest.mark.parametrize('url', ['https://creativecommons.org/licenses/by-nc/4.0/', 'https://creativecommons.org/licenses/by-nd/4.0/', 'https://creativecommons.org/licenses/by-sa/4.0/', 'https://creativecommons.org.evil.test/licenses/by/4.0/', 'https://evil.test/?license=https://creativecommons.org/licenses/by/4.0/', 'https://creativecommons.org/licenses/by/4.0/?fake=1'])
def test_restricted_or_spoofed_license_is_rejected(url):
    m=meta('<permissions><license><ali:license_ref>'+url+'</ali:license_ref></license></permissions>')
    assert mod.extract_article_license(m) is None

@pytest.mark.parametrize('inner', [
    '<permissions><license><license-p>Creative Commons Attribution License</license-p></license></permissions>',
    '<permissions><license><license_ref>https://creativecommons.org/licenses/by/4.0/</license_ref></license></permissions>',
    '<permissions><license><license-p>https://creativecommons.org/licenses/by/4.0/</license-p></license></permissions>',
    '<ref-list><ref><ali:license_ref>https://creativecommons.org/licenses/by/4.0/</ali:license_ref></ref></ref-list>',
    '<sub-article><permissions><license><ali:license_ref>https://creativecommons.org/licenses/by/4.0/</ali:license_ref></license></permissions></sub-article>',
])
def test_no_inference_from_prose_citations_or_other_namespaces(inner):
    assert mod.extract_article_license(meta(inner)) is None

def test_existing_xlink_license_still_supported():
    assert mod.extract_article_license(meta('<permissions><license xlink:href="https://creativecommons.org/licenses/by/4.0/"/></permissions>'))=='https://creativecommons.org/licenses/by/4.0/'

@pytest.mark.parametrize('start,accepted', [('2026-09-09',True),('2026-09-10',True),('2026-09-11',False),('tomorrow',False),('2026-02-30',False)])
def test_ali_start_date_not_active_or_malformed_is_not_permission(start, accepted):
    from datetime import date
    m=meta('<permissions><license><ali:license_ref start_date="'+start+'">https://creativecommons.org/licenses/by/4.0/</ali:license_ref></license></permissions>')
    assert bool(mod.extract_article_license(m,as_of=date(2026,9,10))) is accepted
