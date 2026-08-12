"""Validações de documento brasileiro. Sem dependência externa."""

import re


def limpar_cpf(cpf: str) -> str:
    return re.sub(r"\D", "", cpf or "")


def cpf_valido(cpf: str) -> bool:
    """Confere os dígitos verificadores do CPF (algoritmo público, Receita Federal)."""
    d = limpar_cpf(cpf)
    if len(d) != 11 or d == d[0] * 11:
        return False

    def digito(base: str, pesos: range) -> str:
        soma = sum(int(n) * p for n, p in zip(base, pesos))
        resto = (soma * 10) % 11
        return "0" if resto == 10 else str(resto)

    d1 = digito(d[:9], range(10, 1, -1))
    d2 = digito(d[:9] + d1, range(11, 1, -1))
    return d[-2:] == d1 + d2


UFS = {
    "AC", "AL", "AP", "AM", "BA", "CE", "DF", "ES", "GO", "MA", "MT", "MS", "MG",
    "PA", "PB", "PR", "PE", "PI", "RJ", "RN", "RS", "RO", "RR", "SC", "SP", "SE", "TO",
}


def cpf_mascarado(cpf: str | None) -> str | None:
    """Só os quatro últimos dígitos ficam legíveis — o suficiente pro titular
    reconhecer o próprio cadastro sem expor o documento inteiro na tela.
    Movida de `app/api/auth.py` (11/08/2026, ficha administrativa do
    assinante) para ser a única fonte de mascaramento de CPF do sistema —
    reaproveitada tanto na listagem/detalhe de `GET /admin/usuarios*` quanto
    em `GET /auth/me`, em vez de duas implementações idênticas divergindo
    com o tempo."""
    if not cpf:
        return None
    digitos = limpar_cpf(cpf)
    if len(digitos) != 11:
        return None
    return f"***.***.{digitos[6:9]}-{digitos[9:]}"
