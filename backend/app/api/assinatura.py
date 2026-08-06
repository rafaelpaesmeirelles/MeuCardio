"""Catálogo de métodos de assinatura de documento clínico (Tarefa 4).

Rota só de leitura — a escolha em si é feita a cada emissão, nos endpoints
de `receituario.py` e `documents.py`. Existe separada para o frontend
popular o `<select>` de método sem duplicar a lista de provedores em duas
telas (`Receituario.tsx` e `Templates.tsx`).

As rotas de `/certificado-a1` (Trabalho 7, 06/08/2026) fazem a gestão do
certificado A1 do próprio médico — upload, status, remoção. `/certificadoras`
é só informativo: lista as Autoridades Certificadoras ICP-Brasil que vendem
certificado A1 pra pessoa física, pra quem ainda não tem um saber onde
comprar. Nomes e domínios conferidos em 06/08/2026 contra a lista oficial
de credenciadas do ITI (dadosabertos.iti.gov.br) e busca pelos sites
próprios de cada uma — nunca inventados.
"""
from fastapi import APIRouter, Depends, File, Form, HTTPException, UploadFile
from sqlalchemy.orm import Session

from app.core.db import get_db
from app.core.security import current_user
from app.models.user import User
from app.services.assinatura import catalogo, certificado_a1
from app.services.assinatura.provedor import obter_provedor

router = APIRouter(prefix="/api/assinatura", tags=["assinatura"])


@router.get("/provedores")
def listar_provedores(db: Session = Depends(get_db), user=Depends(current_user)):
    """`disponivel=False` não é erro de configuração da tela: é o mesmo
    "recusa e explica" que `receituario.py` já faz para SNCR/RCE — o
    catálogo inteiro aparece, cada provedor sem credencial mostra o motivo.
    `A1_ARQUIVO` é o único cuja disponibilidade depende de QUEM está
    perguntando (se este usuário tem certificado conectado), por isso
    `db`/`user` são passados a todo provedor — os demais ignoram."""
    itens = []
    for p in catalogo.PROVEDORES:
        disponivel, motivo = obter_provedor(p.codigo, db=db, user=user).disponivel()
        itens.append({
            "codigo": p.codigo, "nome": p.nome, "nivel": p.nivel, "familia": p.familia,
            "disponivel": disponivel, "motivo": motivo,
        })
    return itens


# Só as ACs credenciadas pela ICP-Brasil que vendem e-CPF/A1 diretamente ao
# público em geral (existem dezenas de outras, de 2º nível, regionais ou
# corporativas — ver dadosabertos.iti.gov.br/.../PCertsCredenciados.csv —
# mas essas cinco são as de alcance nacional e venda direta ao público,
# conferidas em 06/08/2026).
CERTIFICADORAS_RECOMENDADAS = [
    {"nome": "Certisign", "site": "https://certisign.com.br"},
    {"nome": "Serasa", "site": "https://serasaexperian.com.br"},
    {"nome": "Soluti", "site": "https://soluti.com.br/certificado-digital/"},
    {"nome": "Valid Certificadora", "site": "https://validcertificadora.com.br"},
    {"nome": "Safeweb", "site": "https://www.safeweb.com.br"},
]


@router.get("/certificadoras")
def listar_certificadoras():
    return CERTIFICADORAS_RECOMENDADAS


TAMANHO_MAXIMO_CERTIFICADO = 64 * 1024  # PKCS#12 típico tem poucos KB; 64 KB já é folgado


@router.get("/certificado-a1")
def status_certificado_a1(db: Session = Depends(get_db), user: User = Depends(current_user)):
    registro = certificado_a1.obter(db, user)
    if registro is None:
        return {"conectado": False}
    return {
        "conectado": True,
        "titular_cn": registro.titular_cn,
        "numero_serie": registro.numero_serie,
        "valido_ate": registro.valido_ate,
        "certificadora": registro.certificadora,
        "criado_em": registro.criado_em,
    }


@router.post("/certificado-a1", status_code=201)
async def conectar_certificado_a1(
    arquivo: UploadFile = File(...),
    senha: str = Form(...),
    certificadora: str | None = Form(None),
    db: Session = Depends(get_db),
    user: User = Depends(current_user),
):
    conteudo = await arquivo.read(TAMANHO_MAXIMO_CERTIFICADO + 1)
    if len(conteudo) > TAMANHO_MAXIMO_CERTIFICADO:
        raise HTTPException(status_code=413, detail="Arquivo de certificado maior que o esperado — confira se é mesmo o .pfx/.p12.")
    if not conteudo:
        raise HTTPException(status_code=422, detail="Arquivo vazio.")
    if not senha:
        raise HTTPException(status_code=422, detail="Informe a senha do certificado.")

    try:
        registro = certificado_a1.salvar(db, user, conteudo, senha, certificadora or None)
    except certificado_a1.CertificadoInvalido as exc:
        db.rollback()
        raise HTTPException(status_code=422, detail=str(exc)) from exc
    db.commit()
    return {
        "conectado": True,
        "titular_cn": registro.titular_cn,
        "numero_serie": registro.numero_serie,
        "valido_ate": registro.valido_ate,
        "certificadora": registro.certificadora,
    }


@router.delete("/certificado-a1", status_code=204)
def remover_certificado_a1(db: Session = Depends(get_db), user: User = Depends(current_user)):
    certificado_a1.remover(db, user)
    db.commit()
