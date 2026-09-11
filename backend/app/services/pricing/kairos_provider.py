"""K@iros licensed market-intelligence provider.

The regulatory source of truth remains CMED/ANVISA. K@iros is intentionally
kept in a separate source layer (`market_intelligence`) so a published price
snapshot can corroborate presentation/market context without silently
replacing the official CMED ceiling used by CorVIA.

The August/2026 snapshot retains the reviewed cardiovascular baseline and the
validated, non-ambiguous price rows from the issue supplied by the product
owner. Adding a new issue means adding a new reviewed snapshot; no scraping
or inferred prices are allowed. Source coverage is not clinical-catalogue
coverage: prescription options still require a matching Drug and published PMC.
"""
from __future__ import annotations

import json
import re
import unicodedata
from datetime import datetime, timezone
from decimal import Decimal
from pathlib import Path

from sqlalchemy.orm import Session

from app.models.drug import Drug
from app.services.pricing.base import PriceObservation

# Operational price data travels with the backend image. The older file under
# /medicamentos is immutable evidence for the authorized clinical corpus, not
# a fallback: preferring that mounted directory would silently undo expansion.
SNAPSHOT_PATH = Path(__file__).resolve().parents[2] / "data" / "pricing" / "kairos-453-2026-08.json"
OBSERVED_AT = datetime(2026, 8, 1, tzinfo=timezone.utc)
PRICE_FIELDS = {
    "pf20": ("pf", "ICMS 20%"),
    "pmc20": ("pmc", "ICMS 20%"),
    "pf18": ("pf", "ICMS 18%"),
    "pmc18": ("pmc", "ICMS 18%"),
    "pf17": ("pf", "ICMS 17%"),
    "pmc17": ("pmc", "ICMS 17%"),
    "pf12": ("pf", "ICMS 12%"),
    "pmc12": ("pmc", "ICMS 12%"),
}

# Salt/hydrate descriptors used by this scoped snapshot and the corresponding
# reviewed catalogue names. They are not additional active ingredients. Keep
# this explicit: dropping arbitrary parenthetical text or using token subsets
# can attach a fixed-dose combination to a single-ingredient prescription.
SUBSTANCE_DESCRIPTORS = frozenset({
    "arginina", "erbumina", "besilato", "cloridrato", "dicloridrato",
    "sodico", "sodica", "hidratada", "de",
})


def _normalize(value: str | None) -> str:
    raw = unicodedata.normalize("NFKD", value or "").encode("ascii", "ignore").decode().lower()
    return " ".join(re.sub(r"[^a-z0-9]+", " ", raw).split())


def _decimal_br(value: str) -> Decimal:
    # Never stringify a JSON number: 1234.56 would otherwise become 123456.
    # Missing cells are handled by callers, not fabricated as zero here.
    if not isinstance(value, str) or len(value) > 64 or not re.fullmatch(
        r"(?:0|[1-9][0-9]*|[1-9][0-9]{0,2}(?:\.[0-9]{3})+),[0-9]{2}", value
    ):
        raise ValueError("Preço K@iros deve ser uma string monetária pt-BR.")
    price = Decimal(value.replace(".", "").replace(",", "."))
    if not price.is_finite() or price <= 0:
        raise ValueError("Preço K@iros deve ser finito e maior que zero.")
    return price


def _unique_json_keys(pairs: list[tuple[str, object]]) -> dict:
    result = {}
    for key, value in pairs:
        if key in result:
            raise ValueError("Snapshot K@iros contém chave JSON duplicada.")
        result[key] = value
    return result


def _validate_snapshot(data: dict) -> None:
    if not isinstance(data, dict):
        raise ValueError("Snapshot K@iros deve ser um objeto.")
    if data.get("source_type") != "market_intelligence" or data.get("licensed_use") is not True:
        raise ValueError("Snapshot K@iros sem classificação/licença esperada.")
    if type(data.get("schema_version")) is not int or data["schema_version"] != 1:
        raise ValueError("Versão de schema K@iros não suportada.")
    if type(data.get("issue")) is not int or data["issue"] <= 0:
        raise ValueError("Edição K@iros inválida.")
    if not isinstance(data.get("competence"), str) or not re.fullmatch(
        r"[0-9]{4}-(?:0[1-9]|1[0-2])", data["competence"]
    ):
        raise ValueError("Competência K@iros inválida.")
    for field in ("source", "regulatory_authority", "regulatory_note"):
        if not isinstance(data.get(field), str) or not data[field].strip():
            raise ValueError(f"Metadado K@iros obrigatório: {field}.")
    if not isinstance(data.get("records"), list):
        raise ValueError("Registros K@iros devem ser uma lista.")

    # Keep dose punctuation: unlike ingredient matching, presentation identity
    # must not collapse decimal separators, release forms or package details.
    def identity(value: str) -> str:
        return " ".join(unicodedata.normalize("NFKC", value).casefold().split())

    seen: dict[tuple[str, str, str], tuple[str | None, dict[str, Decimal]]] = {}
    for record_index, record in enumerate(data["records"]):
        location = f"registro {record_index + 1}"
        if not isinstance(record, dict):
            raise ValueError(f"K@iros {location}: objeto esperado.")
        for field in ("product", "laboratory"):
            if not isinstance(record.get(field), str) or not record[field].strip():
                raise ValueError(f"K@iros {location}: {field} obrigatório.")
        substance = record.get("substance")
        if substance is not None and (not isinstance(substance, str) or not substance.strip()):
            raise ValueError(f"K@iros {location}: substância inválida; ausência deve ser null.")
        if type(record.get("page")) is not int or record["page"] <= 0:
            raise ValueError(f"K@iros {location}: página inválida.")
        presentations = record.get("presentations")
        if not isinstance(presentations, list) or not presentations:
            raise ValueError(f"K@iros {location}: apresentações obrigatórias.")
        for presentation in presentations:
            if not isinstance(presentation, dict) or not isinstance(presentation.get("presentation"), str) or not presentation["presentation"].strip():
                raise ValueError(f"K@iros {location}: apresentação inválida.")
            prices = {}
            for field, raw in presentation.items():
                if field.lower().startswith(("pf", "pmc")) and field not in PRICE_FIELDS:
                    raise ValueError(f"K@iros {location}: coluna de preço não suportada: {field}.")
                if field not in PRICE_FIELDS or raw is None or raw == "":
                    continue
                try:
                    prices[field] = _decimal_br(raw)
                except ValueError as exc:
                    raise ValueError(f"K@iros {location}, {field}: {exc}") from exc
            key = (identity(record["product"]), identity(record["laboratory"]), identity(presentation["presentation"]))
            canonical_substance = identity(substance) if substance is not None else None
            if key in seen:
                prior_substance, prior_prices = seen[key]
                if prior_substance != canonical_substance or any(
                    field in prior_prices and prior_prices[field] != value
                    for field, value in prices.items()
                ):
                    raise ValueError(f"K@iros {location}: apresentação duplicada conflitante.")
                # Check a third duplicate against every previously seen cell,
                # including rates absent from the first occurrence.
                prior_prices.update(prices)
            else:
                seen[key] = (canonical_substance, prices)


class _IndexedSnapshot(dict):
    """Read-only-by-convention snapshot; indices never become API/JSON keys.

    Build once per load, with no process/file cache that could retain old data.
    Plain caller-supplied dictionaries keep the original linear matching path.
    """

    def __init__(self, data: dict) -> None:
        super().__init__(data)
        self._by_brand: dict[str, list[int]] = {}
        self._by_substance: dict[frozenset[str], list[int]] = {}
        for index, record in enumerate(self["records"]):
            product = _normalize(record.get("product"))
            if product:
                self._by_brand.setdefault(product, []).append(index)
            tokens = frozenset(_normalize(record.get("substance")).split()) - SUBSTANCE_DESCRIPTORS
            if tokens and product != "acertanlo":
                self._by_substance.setdefault(tokens, []).append(index)

    def candidates_for(self, drug: Drug) -> list[dict]:
        indices: set[int] = set()
        for brand in drug.brand_names or []:
            if brand:
                indices.update(self._by_brand.get(_normalize(brand), ()))
        tokens = frozenset(_normalize(drug.generic_name).split()) - SUBSTANCE_DESCRIPTORS
        if tokens:
            indices.update(self._by_substance.get(tokens, ()))
        return [self["records"][index] for index in sorted(indices)]


def _source_path(path: Path | None = None) -> Path:
    if path is not None:
        return path
    return SNAPSHOT_PATH


def load_snapshot(path: Path | None = None) -> dict:
    source = _source_path(path)
    data = json.loads(source.read_text(encoding="utf-8"), object_pairs_hook=_unique_json_keys)
    _validate_snapshot(data)
    return _IndexedSnapshot(data)


def _record_matches(drug: Drug, record: dict) -> bool:
    generic = _normalize(drug.generic_name)
    substance = _normalize(record.get("substance"))
    product = _normalize(record.get("product"))
    brands = {_normalize(brand) for brand in (drug.brand_names or []) if brand}

    if product and product in brands:
        return True
    if not generic or not substance:
        return False
    # The reviewed issue spells this fixed-dose combination's heading only
    # "ARGININA + ANLODIPINO" (omitting perindopril). Its exact catalogue
    # brand remains usable above, but that incomplete heading cannot prove
    # an ingredient match, especially after removing the salt descriptor.
    if product == "acertanlo":
        return False

    generic_tokens = set(generic.split()) - SUBSTANCE_DESCRIPTORS
    substance_tokens = set(substance.split()) - SUBSTANCE_DESCRIPTORS
    if not generic_tokens:
        return False

    # Both sides must describe the same active ingredients, not merely share
    # one. For example, valsartana must not select sacubitril + valsartana,
    # nor indapamida select perindopril + indapamida. Exact brand matching
    # above remains available for a literal, audited publication brand whose
    # substance heading is abbreviated (ACERTANLO in issue 453).
    return generic_tokens == substance_tokens


def records_for_drug(
    drug: Drug,
    path: Path | None = None,
    *,
    snapshot: dict | None = None,
) -> tuple[dict, list[dict]]:
    snapshot = snapshot or load_snapshot(path)
    candidates = snapshot.candidates_for(drug) if isinstance(snapshot, _IndexedSnapshot) else snapshot.get("records", [])
    records = [record for record in candidates if _record_matches(drug, record)]
    return snapshot, records


class KairosProvider:
    source = "kairos"
    source_type = "market_intelligence"

    def __init__(self, db: Session, path: Path | None = None) -> None:
        self._db = db
        self._path = path

    def observations_for(self, drug_id: int) -> list[PriceObservation]:
        drug = self._db.get(Drug, drug_id)
        if drug is None:
            return []
        snapshot, records = records_for_drug(drug, self._path)
        observations: list[PriceObservation] = []
        for record in records:
            for index, presentation in enumerate(record.get("presentations", []), start=1):
                if record.get("source_origin") == "pdf_literal_selected_original_row":
                    page = presentation.get("source_page")
                    side = presentation.get("source_side")
                    line = presentation.get("source_line")
                    if (
                        type(page) is not int or page <= 0 or page != record.get("page")
                        or side not in ("left", "right")
                        or type(line) is not int or line <= 0
                    ):
                        raise ValueError("Apresentação K@iros curada sem coordenadas de origem válidas.")
                    # Curated rows retain the unique printed page/column/line.
                    # Unlike a per-record index, this cannot collide across
                    # laboratories or change when presentation order changes.
                    presentation_ref = f"kairos-{snapshot['issue']}:source:{page}:{side}:{line}"
                else:
                    # Keep the historical 13-record extract references intact.
                    presentation_ref = (
                        f"kairos-{snapshot['issue']}:{record.get('page')}:{_normalize(record.get('product')).replace(' ', '-')}:{index}"
                    )
                for field, (price_type, region) in PRICE_FIELDS.items():
                    raw = presentation.get(field)
                    if raw in (None, ""):
                        continue
                    observations.append(PriceObservation(
                        source=self.source,
                        source_type=self.source_type,
                        price_type=price_type,
                        observed_at=OBSERVED_AT,
                        price=_decimal_br(raw),
                        presentation_ref=presentation_ref,
                        drug_id=drug.id,
                        region=region,
                        confidence="high",
                        metadata={
                            "issue": snapshot.get("issue"),
                            "competence": snapshot.get("competence"),
                            "licensed_use": True,
                            "product": record.get("product"),
                            "laboratory": record.get("laboratory"),
                            "substance": record.get("substance"),
                            "presentation": presentation.get("presentation"),
                            "source_page": record.get("page"),
                            "regulatory_authority": snapshot.get("regulatory_authority"),
                        },
                    ))
        return observations


def api_snapshot_for(drug: Drug, path: Path | None = None) -> dict:
    """UI/API-safe grouped representation; never merges a K@iros value into CMED."""
    snapshot, records = records_for_drug(drug, path)
    return {
        "source": "K@iros",
        "source_type": "market_intelligence",
        "issue": snapshot.get("issue"),
        "competence": snapshot.get("competence"),
        "licensed_use": bool(snapshot.get("licensed_use")),
        "regulatory_note": snapshot.get("regulatory_note"),
        "records": records,
    }


def prescription_options_for(
    drug: Drug,
    path: Path | None = None,
    *,
    snapshot: dict | None = None,
) -> dict:
    """Return audited K@iros presentations for the prescribing UI.

    K@iros publishes PMC by ICMS bracket.  Until CorVIA has a verified tax
    mapping for every UF, the UI receives the literal minimum/maximum across
    the published brackets instead of attributing an unverified rate to a
    state.  This remains market intelligence and never overwrites CMED data.
    """
    snapshot, records = records_for_drug(drug, path, snapshot=snapshot)
    options: list[dict] = []
    for record in records:
        for presentation in record.get("presentations", []):
            prices = {
                region: _decimal_br(presentation[field])
                for field, (price_type, region) in PRICE_FIELDS.items()
                if price_type == "pmc" and presentation.get(field) not in (None, "")
            }
            if not prices:
                continue
            minimum = min(prices.values())
            maximum = max(prices.values())
            options.append({
                "produto": record.get("product"),
                "laboratorio": record.get("laboratory"),
                "apresentacao": presentation.get("presentation"),
                "preco_minimo": float(minimum),
                "preco_maximo": float(maximum),
                "precos_por_icms": {region: float(value) for region, value in prices.items()},
                "pagina_fonte": record.get("page"),
            })
    return {
        "fonte": "K@iros",
        "tipo_fonte": "inteligencia_de_mercado",
        "edicao": snapshot.get("issue"),
        "competencia": snapshot.get("competence"),
        "opcoes": options,
    }
