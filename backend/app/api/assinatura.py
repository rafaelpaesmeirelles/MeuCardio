"""Catálogo de métodos de assinatura de documento clínico (Tarefa 4).

Rota só de leitura — a escolha em si é feita a cada emissão, nos endpoints
de `receituario.py` e `documents.py`. Existe separada para o frontend
popular o `<select>` de método sem duplicar a lista de provedores em duas
telas (`Receituario.tsx` e `Templates.tsx`).
"""
from fastapi import APIRouter, Depends

from app.core.security import current_user
from app.services.assinatura import catalogo
from app.services.assinatura.provedor import obter_provedor

router = APIRouter(prefix="/api/assinatura", tags=["assinatura"])


@router.get("/provedores")
def listar_provedores(_=Depends(current_user)):
    """`disponivel=False` não é erro de configuração da tela: é o mesmo
    "recusa e explica" que `receituario.py` já faz para SNCR/RCE — o
    catálogo inteiro aparece, cada provedor sem credencial mostra o motivo."""
    itens = []
    for p in catalogo.PROVEDORES:
        disponivel, motivo = obter_provedor(p.codigo).disponivel()
        itens.append({
            "codigo": p.codigo, "nome": p.nome, "nivel": p.nivel, "familia": p.familia,
            "disponivel": disponivel, "motivo": motivo,
        })
    return itens
