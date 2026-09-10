"""Read machine-readable licenses only from the original article permissions.

NISO ALI license_ref stores its URL as text, unlike xlink attributes.
No license is inferred from generic prose, citations or translated subarticles.
"""
import re
from datetime import date, datetime, timezone

ALLOWED_LICENSE_URL = re.compile(r"https?://creativecommons\.org/(licenses/by/(1\.0|2\.0|2\.5|3\.0|4\.0)|publicdomain/zero/1\.0)/?")
ALI_LICENSE_REF = "{http://www.niso.org/schemas/ali/1.0/}license_ref"


def extract_article_license(article_meta, *, as_of=None):
    as_of = as_of or datetime.now(timezone.utc).date()
    found = None
    for element in article_meta.findall('./permissions/license'):
        candidates = list(element.attrib.values())
        for child in element.iter():
            candidates.extend(child.attrib.values())
            if child.tag == ALI_LICENSE_REF and child.text:
                start = child.get("start_date")
                if start:
                    try:
                        if not re.fullmatch(r"[0-9]{4}-[0-9]{2}-[0-9]{2}", start) or date.fromisoformat(start) > as_of:
                            continue
                    except ValueError:
                        continue
                candidates.append(child.text.strip())
        for candidate in candidates:
            if ALLOWED_LICENSE_URL.fullmatch(candidate):
                found = candidate
    return found
