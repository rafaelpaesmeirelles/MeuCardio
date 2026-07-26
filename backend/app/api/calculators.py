from dataclasses import asdict

from fastapi import APIRouter, Depends, HTTPException

from app.core.security import current_user
from app.services import calculators as calc

router = APIRouter(prefix="/api/calculators", tags=["calculadoras"])


@router.get("")
def list_calculators(_=Depends(current_user)):
    return [
        {
            "slug": c.slug,
            "name": c.name,
            "theme": c.theme,
            "purpose": c.purpose,
            "status": c.status,
        }
        for c in calc.REGISTRY.values()
    ]


@router.get("/{slug}")
def get_calculator(slug: str, _=Depends(current_user)):
    c = calc.REGISTRY.get(slug)
    if not c:
        raise HTTPException(status_code=404, detail="Calculadora não encontrada.")
    return {
        "slug": c.slug,
        "name": c.name,
        "theme": c.theme,
        "purpose": c.purpose,
        "status": c.status,
        "reference": c.reference,
        "limitations": c.limitations,
        "fields": [asdict(f) for f in c.fields],
    }


@router.post("/{slug}/run")
def run_calculator(slug: str, payload: dict, _=Depends(current_user)):
    try:
        return calc.run(slug, payload)
    except KeyError:
        raise HTTPException(status_code=404, detail="Calculadora não encontrada.")
    except ValueError as e:
        raise HTTPException(status_code=409, detail=str(e))
    except (TypeError, ZeroDivisionError):
        raise HTTPException(status_code=422, detail="Revise os valores informados.")
