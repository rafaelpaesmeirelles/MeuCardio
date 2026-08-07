from dataclasses import asdict

from fastapi import APIRouter, Depends, HTTPException

from app.core.security import current_user
from app.services import calculators as calc
from app.services.perioperative_calculators import PERIOPERATIVE_REGISTRY

# Calculadoras perioperatórias produzidas pelo ChatGPT são registradas no mesmo
# catálogo usado pelo frontend genérico e pela avaliação pré-operatória.
# A atualização ocorre após `calculators` estar completamente importado, evitando
# duplicar as dataclasses/infraestrutura existentes.
calc.REGISTRY.update(PERIOPERATIVE_REGISTRY)

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
            "kind": c.kind,
        }
        for c in sorted(calc.REGISTRY.values(), key=lambda c: c.name)
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
        "kind": c.kind,
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
