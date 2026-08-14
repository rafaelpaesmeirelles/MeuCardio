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
    # funcionalidade crítica. Em produção não aceitamos modo best-effort
    # silenciosamente desconfigurado.
    if not bool(getattr(settings, "smtp_configurado", False)):
        erros.append("SMTP_HOST/SMTP_USER/SMTP_PASSWORD são obrigatórios em produção")

    smtp_from = (getattr(settings, "smtp_from", "") or "").lower()
    smtp_host = (getattr(settings, "smtp_host", "") or "").strip().lower()
    smtp_user = (getattr(settings, "smtp_user", "") or "").strip().lower()
    if EMAIL_TRANSACIONAL_CANONICO not in smtp_from:
        erros.append("SMTP_FROM deve usar contato@corvia.med.br")

    # O endereço visível/remetente e a identidade usada para autenticar no
    # servidor SMTP são conceitos diferentes. Provedores de relay podem exigir
    # um usuário técnico. A Resend, por exemplo, autentica com usuário literal
    # ``resend`` e a API key como senha; o remetente continua sendo a conta
    # verificada ``contato@corvia.med.br`` via SMTP_FROM.
    if smtp_host == "smtp.resend.com" and smtp_user != "resend":
        erros.append("SMTP_USER deve ser resend quando SMTP_HOST=smtp.resend.com")

    if erros:
        detalhes = "\n".join(f"- {erro}" for erro in erros)
        raise RuntimeError(
            "Configuração insegura/incompleta de produção; inicialização recusada:\n" + detalhes
        )
