"""Camada única de "paciente para documento" (12/08/2026, pedido do
Rafael) — cifra/decifra o `PatientProfile`, monta o snapshot congelado que
`GeneratedDocument` grava na emissão, e resolve o dicionário de variáveis
`{{paciente_...}}` que qualquer `DocumentTemplate` pode usar.

Ponto único de propósito: os quatro caminhos de geração de documento
(`gerar_documento`/modelo, `gerar-exames`, `gerar-atestado`, `gerar-livre`,
todos em `app/api/documents.py`) chamam só `resolver_paciente_documento()`
daqui — nenhum deles decifra `PatientProfile` por conta própria.
"""
from __future__ import annotations

import json
from datetime import date

from sqlalchemy.orm import Session

from app.models.patient_profile import PatientProfile
from app.services import cofre
from app.services.clinical_ownership import patient_profile_for_user

# Nomes de variável `{{...}}` que um `DocumentTemplate` pode usar para
# puxar dado do paciente selecionado. Fixo e documentado aqui — é a lista
# que a tela "Criar Modelo" mostra ao médico (Tarefa de 12/08/2026, item 10).
NOMES_VARIAVEIS_PACIENTE = (
    "paciente_nome", "paciente_cpf", "paciente_data_nascimento", "paciente_sexo",
    "paciente_telefone", "paciente_email",
    "paciente_endereco_logradouro", "paciente_endereco_numero",
    "paciente_endereco_complemento", "paciente_endereco_bairro",
    "paciente_endereco_cidade", "paciente_endereco_uf", "paciente_endereco_cep",
    "paciente_endereco_completo",
)


def _decifrar_opcional(dados: bytes | None, dono_id: int) -> str | None:
    return cofre.decifrar_campo(dados, dono_id) if dados else None


def snapshot_de(perfil: PatientProfile) -> dict:
    """Decifra um `PatientProfile` inteiro para um dict plano — usado tanto
    para montar o snapshot que vai congelado no documento quanto para a
    prévia ("Dados do paciente utilizados neste documento") antes de
    emitir. Campo ausente no cadastro vira `None`/`{}`, nunca levanta erro
    — é o cadastro real do médico, pode estar incompleto de propósito."""
    endereco = None
    if perfil.endereco_cifrado:
        endereco = json.loads(cofre.decifrar_campo(perfil.endereco_cifrado, perfil.id))
    return {
        "profile_id": perfil.id,
        "full_name": _decifrar_opcional(perfil.full_name_cifrado, perfil.id),
        "cpf": _decifrar_opcional(perfil.cpf_cifrado, perfil.id),
        "birth_date": perfil.birth_date.isoformat() if perfil.birth_date else None,
        "sex": perfil.sex,
        "phone": _decifrar_opcional(perfil.phone_cifrado, perfil.id),
        "email": _decifrar_opcional(perfil.email_cifrado, perfil.id),
        "endereco": endereco or {},
    }


def montar_endereco_completo(endereco: dict | None) -> str:
    """Concatena o endereço em uma linha só, pulando campo vazio sem deixar
    separador sobrando — ex.: "Rua X, 123 — Apto 45 — Bairro —
    Ribeirão Preto/SP — CEP 14000-000". Mesmo estilo de separador (" — ")
    já usado em `pdf_documento._endereco_linhas`, só que numa linha só em
    vez de três, porque aqui o destino é uma variável de texto de modelo,
    não o cabeçalho fixo do PDF."""
    endereco = endereco or {}
    logradouro = (endereco.get("logradouro") or "").strip()
    numero = (endereco.get("numero") or "").strip()
    complemento = (endereco.get("complemento") or "").strip()
    bairro = (endereco.get("bairro") or "").strip()
    cidade = (endereco.get("cidade") or "").strip()
    uf = (endereco.get("uf") or "").strip()
    cep = (endereco.get("cep") or "").strip()

    linha1 = logradouro
    if numero:
        linha1 = f"{linha1}, {numero}" if linha1 else numero
    if complemento:
        linha1 = f"{linha1} — {complemento}" if linha1 else complemento

    cidade_uf = f"{cidade}/{uf}" if cidade and uf else (cidade or uf)

    partes = [p for p in (linha1, bairro, cidade_uf) if p]
    if cep:
        partes.append(f"CEP {cep}")
    return " — ".join(partes)


def _fmt_data(iso: str | None) -> str:
    if not iso:
        return ""
    try:
        return date.fromisoformat(iso).strftime("%d/%m/%Y")
    except ValueError:
        return iso


def variaveis_paciente(snapshot: dict | None) -> dict[str, str]:
    """Dict `{{nome_variavel}}` -> valor em texto, sempre com as
    `NOMES_VARIAVEIS_PACIENTE` completas — campo vazio no cadastro (ou
    nenhum paciente selecionado) vira string vazia, nunca chave ausente:
    é o que permite ao chamador NUNCA marcar variável de paciente como
    "faltando" (ela sempre tem valor, mesmo que vazio)."""
    if not snapshot:
        return dict.fromkeys(NOMES_VARIAVEIS_PACIENTE, "")
    endereco = snapshot.get("endereco") or {}
    return {
        "paciente_nome": snapshot.get("full_name") or "",
        "paciente_cpf": snapshot.get("cpf") or "",
        "paciente_data_nascimento": _fmt_data(snapshot.get("birth_date")),
        "paciente_sexo": snapshot.get("sex") or "",
        "paciente_telefone": snapshot.get("phone") or "",
        "paciente_email": snapshot.get("email") or "",
        "paciente_endereco_logradouro": endereco.get("logradouro") or "",
        "paciente_endereco_numero": endereco.get("numero") or "",
        "paciente_endereco_complemento": endereco.get("complemento") or "",
        "paciente_endereco_bairro": endereco.get("bairro") or "",
        "paciente_endereco_cidade": endereco.get("cidade") or "",
        "paciente_endereco_uf": endereco.get("uf") or "",
        "paciente_endereco_cep": endereco.get("cep") or "",
        "paciente_endereco_completo": montar_endereco_completo(endereco),
    }


def resolver_paciente_documento(
    db: Session, user, *, patient_profile_id: int | None, patient_name_avulso: str | None,
) -> tuple[str | None, dict | None, int | None]:
    """Ponto único chamado pelos quatro caminhos de geração de documento.

    Devolve `(nome_para_exibicao, snapshot_ou_None, profile_id_ou_None)`.
    Quando `patient_profile_id` vem preenchido, a posse é checada por
    `patient_profile_for_user` (404 — nunca 403 — se o cadastro não existir
    ou pertencer a outro médico: é essa checagem, no backend, que impede
    um médico de alcançar paciente alheio por esta rota, qualquer que seja
    o que o frontend mostre ou esconda). Sem `patient_profile_id`, cai no
    comportamento anterior — nome digitado livre, sem cadastro nenhum
    (continua válido: paciente é sempre opcional)."""
    if patient_profile_id is None:
        nome = (patient_name_avulso or "").strip() or None
        return nome, None, None
    perfil = patient_profile_for_user(patient_profile_id, db, user)
    snap = snapshot_de(perfil)
    return snap.get("full_name"), snap, perfil.id


def cifrar_snapshot(snapshot: dict, documento_id: int) -> bytes:
    return cofre.cifrar_campo(json.dumps(snapshot, ensure_ascii=False), documento_id)


def decifrar_snapshot(dados: bytes | None, documento_id: int) -> dict | None:
    if not dados:
        return None
    return json.loads(cofre.decifrar_campo(dados, documento_id))
