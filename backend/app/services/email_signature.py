"""Assinatura de e-mail (logo Corvia + logo/dados profissionais), anexada ao
final do e-mail quando o médico ativa a opção em Minha Conta — opt-in, nunca
ligada por padrão.

Reaproveita os mesmos campos e a mesma regra de `professional_profile.py`
(nome com forma de tratamento, dados do local de trabalho só se
`include_workplace_on_documents`, logo servido por `/logos/*`) já usados nos
documentos/receitas — não duplica a fonte da verdade da identidade
profissional, só monta outro formato (HTML de e-mail) a partir dela.

Telefone e endereço profissional são OPT-IN À PARTE de `email_assinatura_
ativa`: o médico pode querer nome/CRM/logo na assinatura sem publicar o
telefone ou o endereço do consultório em todo e-mail que manda.
"""
from __future__ import annotations

import html as _html
from typing import Any

from app.core.config import settings
from app.services.professional_profile import professional_name, workplace_lines

LOGO_CORVIA_URL = "https://corvia.med.br/corvia-logo-compacta.png"


def _endereco_profissional(user: Any) -> str | None:
    partes = [
        f"{(user.practice_street or '').strip()}, {(user.practice_number or '').strip()}".strip(", "),
        (user.practice_city or "").strip(),
        (user.practice_state or "").strip(),
    ]
    linha = " · ".join(p for p in partes if p)
    return linha or None


def _conselho(user: Any) -> str | None:
    if not user.council_name:
        return None
    partes = [f"{user.council_name}-{user.council_state or ''}".rstrip("-"), (user.council_number or "").strip()]
    return " ".join(p for p in partes if p) or None


def montar_assinatura_html(user: Any) -> str | None:
    """`None` quando a assinatura está desligada — quem chama deve manter o
    comportamento atual (corpo enviado como o médico digitou, sem anexar
    nada) nesse caso, não um bloco vazio."""
    if not getattr(user, "email_assinatura_ativa", False):
        return None

    nome = _html.escape(professional_name(user))
    linhas_identidade: list[str] = []
    especialidade = (user.specialty or "").strip()
    if especialidade:
        linhas_identidade.append(_html.escape(especialidade))
    conselho = _conselho(user)
    if conselho:
        linhas_identidade.append(_html.escape(conselho))
    for linha in workplace_lines(user):
        linhas_identidade.append(_html.escape(linha))
    if user.email_assinatura_incluir_telefone and (user.practice_phone or "").strip():
        linhas_identidade.append(f"Tel.: {_html.escape(user.practice_phone.strip())}")
    if user.email_assinatura_incluir_endereco:
        endereco = _endereco_profissional(user)
        if endereco:
            linhas_identidade.append(_html.escape(endereco))

    logo_profissional = ""
    if user.document_logo_url and user.document_logo_url.startswith("/logos/"):
        url_logo = f"{settings.public_url.rstrip('/')}{user.document_logo_url}"
        logo_profissional = (
            f'<img src="{_html.escape(url_logo)}" alt="" '
            f'style="max-height:48px;max-width:160px;display:block;margin-bottom:6px;">'
        )

    linhas_html = "<br>".join(linhas_identidade)
    return f"""
<table role="presentation" style="margin-top:24px;padding-top:12px;border-top:1px solid #dbe2e6;font-family:Arial,Helvetica,sans-serif;font-size:12.5px;color:#3a4750;">
  <tr>
    <td style="vertical-align:top;padding-right:14px;">{logo_profissional}
      <img src="{_html.escape(LOGO_CORVIA_URL)}" alt="Corvia" style="height:22px;display:block;">
    </td>
    <td style="vertical-align:top;">
      <strong style="color:#0b2e45;">{nome}</strong><br>
      {linhas_html}
    </td>
  </tr>
</table>
""".strip()


def montar_corpo_com_assinatura(corpo_texto: str, assinatura_html: str | None) -> tuple[str, str]:
    """Devolve `(corpo, mailFormat)`. Sem assinatura, devolve o texto
    IDÊNTICO ao que entrou e `"plaintext"` — comportamento atual, inalterado,
    para quem não ligou a opção. Com assinatura, escapa o texto do médico
    (ele foi digitado como texto puro, nunca HTML) antes de combinar com o
    HTML da assinatura, para não interpretar por engano um `<`/`>` digitado
    como marcação nem permitir injeção de HTML pelo próprio remetente."""
    if assinatura_html is None:
        return corpo_texto, "plaintext"
    corpo_html = _html.escape(corpo_texto).replace("\n", "<br>")
    return f"{corpo_html}<br><br>{assinatura_html}", "html"
