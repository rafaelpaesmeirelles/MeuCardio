"""Validação fail-fast da configuração usada para iniciar a aplicação.

Desenvolvimento e testes continuam aceitando valores convenientes. Em produção,
a aplicação se recusa a iniciar com credenciais previsíveis, sem a chave que
protege arquivos clínicos ou sem o canal transacional necessário para recuperar
acesso. Um Clinical OS que responde 202 ao "esqueci a senha" mas não consegue
enviar o e-mail não está pronto para produção.
"""

from __future__ import annotations

import os

from cryptography.fernet import Fernet
from sqlalchemy.engine import make_url

AMBIENTES_VALIDOS = {"development", "test", "production"}
PROVEDORES_EMAIL_TRANSACIONAL = {"auto", "smtp", "mail360"}
SEGREDOS_JWT_INSEGUROS = {"", "dev-only-change-me", "gere-com-openssl-rand-hex-32"}
SENHAS_ADMIN_INSEGURAS = {"", "troque-esta-senha", "admin", "password"}
SENHAS_BANCO_INSEGURAS = {"", "meucardio", "troque-esta-senha", "postgres", "password"}
EMAIL_TRANSACIONAL_CANONICO = "contato@corvia.med.br"


def ambiente_atual() -> str:
    ambiente = os.getenv("ENVIRONMENT", "development").strip().lower()
    if ambiente not in AMBIENTES_VALIDOS:
        permitidos = ", ".join(sorted(AMBIENTES_VALIDOS))
        raise RuntimeError(
            f"ENVIRONMENT inválido: {ambiente!r}. Valores permitidos: {permitidos}."
        )
    return ambiente


def _provider_email_efetivo(settings) -> tuple[str, str]:
    """Resolve o transporte sem consultar rede nem expor credenciais.

    Retorna ``(provider_solicitado, provider_efetivo)``. Em ``auto`` o
    Mail360 Native institucional tem precedência porque é o provedor real do
    domínio CorVIA; SMTP permanece fallback compatível.
    """
    solicitado = (getattr(settings, "email_transacional_provider", "auto") or "auto").strip().lower()
    smtp_ok = bool(getattr(settings, "smtp_configurado", False))
    mail360_ok = bool(getattr(settings, "mail360_transacional_configurado", False))
    if solicitado == "mail360":
        return solicitado, "mail360" if mail360_ok else ""
    if solicitado == "smtp":
        return solicitado, "smtp" if smtp_ok else ""
    if solicitado == "auto":
        if mail360_ok:
            return solicitado, "mail360"
        if smtp_ok:
            return solicitado, "smtp"
    return solicitado, ""


def validar_configuracao_de_execucao(settings) -> None:
    """Recusa inicialização insegura/incompleta quando ``ENVIRONMENT=production``.

    A mensagem enumera somente os nomes dos campos problemáticos; nenhum
    segredo é incluído em logs ou exceções.
    """
    if ambiente_atual() != "production":
        return

    erros: list[str] = []

    jwt_secret = (settings.jwt_secret or "").strip()
    if jwt_secret in SEGREDOS_JWT_INSEGUROS or len(jwt_secret) < 32:
        erros.append("JWT_SECRET deve ser aleatório e ter ao menos 32 caracteres")

    admin_password = settings.admin_password or ""
    if admin_password.lower() in SENHAS_ADMIN_INSEGURAS or len(admin_password) < 12:
        erros.append("ADMIN_PASSWORD deve ser exclusiva e ter ao menos 12 caracteres")

    if (settings.admin_email or "").lower().endswith(".local"):
        erros.append("ADMIN_EMAIL não pode usar o domínio local padrão")

    try:
        senha_banco = make_url(settings.database_url).password or ""
    except Exception:
        erros.append("DATABASE_URL é inválida")
    else:
        if senha_banco.lower() in SENHAS_BANCO_INSEGURAS:
            erros.append("a senha do PostgreSQL não pode usar valor padrão")

    chave = (settings.storage_encryption_key or "").strip()
    if not chave:
        erros.append("STORAGE_ENCRYPTION_KEY é obrigatória para arquivos clínicos")
    else:
        try:
            Fernet(chave.encode("ascii"))
        except (ValueError, TypeError):
            erros.append("STORAGE_ENCRYPTION_KEY não é uma chave Fernet válida")

    # Recuperação de senha, confirmação de acesso e avisos de segurança são
    # críticos. O transporte pode ser o Mail360 Native institucional ou SMTP,
    # mas nunca pode existir um falso sucesso sem um provider configurado.
    solicitado, efetivo = _provider_email_efetivo(settings)
    if solicitado not in PROVEDORES_EMAIL_TRANSACIONAL:
        erros.append("EMAIL_TRANSACIONAL_PROVIDER deve ser auto, mail360 ou smtp")
    elif not efetivo:
        if solicitado == "mail360":
            erros.append(
                "MAIL360_CLIENT_ID/MAIL360_CLIENT_SECRET/MAIL360_REFRESH_TOKEN/"
                "MAIL360_TRANSACTIONAL_ACCOUNT_KEY são obrigatórios para e-mail transacional via Mail360"
            )
        elif solicitado == "smtp":
            erros.append("SMTP_HOST/SMTP_USER/SMTP_PASSWORD são obrigatórios para e-mail transacional via SMTP")
        else:
            erros.append(
                "SMTP_HOST/SMTP_USER/SMTP_PASSWORD ou Mail360 transacional configurado são obrigatórios em produção"
            )

    smtp_from = (getattr(settings, "smtp_from", "") or "").lower()
    smtp_host = (getattr(settings, "smtp_host", "") or "").strip().lower()
    smtp_user = (getattr(settings, "smtp_user", "") or "").strip().lower()
    if EMAIL_TRANSACIONAL_CANONICO not in smtp_from:
        erros.append("SMTP_FROM deve usar contato@corvia.med.br")

    # Esta regra só se aplica quando SMTP é o transporte efetivamente usado.
    # Assim uma configuração Resend antiga/incompleta não bloqueia o Mail360
    # explicitamente selecionado e validado.
    if efetivo == "smtp" and smtp_host == "smtp.resend.com" and smtp_user != "resend":
        erros.append("SMTP_USER deve ser resend quando SMTP_HOST=smtp.resend.com")

    if erros:
        detalhes = "\n".join(f"- {erro}" for erro in erros)
        raise RuntimeError(
            "Configuração insegura/incompleta de produção; inicialização recusada:\n" + detalhes
        )
