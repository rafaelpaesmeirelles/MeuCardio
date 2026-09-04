from fastapi import APIRouter, Depends
from pydantic import BaseModel, field_validator
from sqlalchemy.orm import Session

from app.core.db import get_db
from app.core.security import current_user
from app.models.user import User
from app.services.professional_profile import normalize_sex

router = APIRouter(prefix="/api/auth", tags=["auth"])


class SexoCadastral(BaseModel):
    sex: str

    @field_validator("sex")
    @classmethod
    def _sexo(cls, value: str) -> str:
        normalized = normalize_sex(value)
        if normalized is None:
            raise ValueError("Selecione Masculino ou Feminino.")
        return normalized


@router.patch("/me/sex")
def atualizar_sexo_cadastral(
    dados: SexoCadastral,
    db: Session = Depends(get_db),
    user: User = Depends(current_user),
):
    """Atualiza somente o sexo cadastral usado na concordância de tratamento.

    A rota é separada do PATCH histórico /auth/me para manter compatibilidade
    com clientes antigos e permitir que contas legadas preencham esse dado sem
    regravar o restante do perfil profissional.
    """
    user.sex = dados.sex
    db.commit()
    db.refresh(user)
    return {"sex": user.sex}
