"""K@iros licensed market-intelligence provider.

The regulatory source of truth remains CMED/ANVISA. K@iros is intentionally
kept in a separate source layer (`market_intelligence`) so a published price
snapshot can corroborate presentation/market context without silently
replacing the official CMED ceiling used by CorVIA.

The August/2026 snapshot is a deliberately scoped cardiovascular extract from
the licensed issue supplied by the product owner. Adding a new issue means
adding a new reviewed snapshot; no scraping or inferred prices are allowed.
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

SNAPSHOT_PATH = Path("/medicamentos/kairos-453-2026-08.json")
REPOSITORY_FALLBACK = Path(__file__).resolve().parents[4] / "medicamentos" / "kairos-453-2026-08.json"
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


def _normalize(value: str | None) -> str:
    raw = unicodedata.normalize("NFKD", value or "").encode("ascii", "ignore").decode().lower()
    return " ".join(re.sub(r"[^a-z0-9]+", " ", raw).split())


def _decimal_br(value: str) -> Decimal:
    return Decimal(value.replace(".", "").replace(",", "."))


def _source_path(path: Path | None = None) -> Path:
    if path is not None:
        return path
    if SNAPSHOT_PATH.exists():
        return SNAPSHOT_PATH
    return REPOSITORY_FALLBACK


def load_snapshot(path: Path | None = None) -> dict:
    source = _source_path(path)
    data = json.loads(source.read_text(encoding="utf-8"))
    if data.get("source_type") != "market_intelligence" or not data.get("licensed_use"):
        raise ValueError("Snapshot K@iros sem classificação/licença esperada.")
    return data


def _record_matches(drug: Drug, record: dict) -> bool:
    generic = _normalize(drug.generic_name)
    substance = _normalize(record.get("substance"))
    product = _normalize(record.get("product"))
    brands = {_normalize(brand) for brand in (drug.brand_names or []) if brand}

    if product and product in brands:
        return True
    if not generic or not substance:
        return False

    generic_tokens = [token for token in generic.split() if len(token) >= 4]
    substance_tokens = set(substance.split())
    if not generic_tokens:
        return False

    # Conservative structured matching: every clinically meaningful token in
    # the CorVIA generic name must occur in the published substance string.
    # This handles salts/hydrates (e.g. sacubitril/valsartana sódica hidratada)
    # without fuzzy edit distance that could join unrelated drugs.
    return all(token in substance_tokens for token in generic_tokens)


def records_for_drug(
    drug: Drug,
    path: Path | None = None,
    *,
    snapshot: dict | None = None,
) -> tuple[dict, list[dict]]:
    snapshot = snapshot or load_snapshot(path)
    records = [record for record in snapshot.get("records", []) if _record_matches(drug, record)]
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
                        price=_decimal_br(str(raw)),
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
                region: _decimal_br(str(presentation[field]))
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
