"""E-mails transacionais do assinante Corvia (02/08/2026).

Um único módulo, uma função por e-mail — ver `emails-transacionais-spec.md`
(pedido do Rafael, texto aprovado palavra por palavra, não reescrito aqui).

Duas decisões que atravessam todo o módulo, e o motivo de cada uma:

1. **Senha nunca é enviada por e-mail.** Toda função de "ativação"/"nova
   senha" manda um link de uso único (`PasswordResetToken`, reaproveitado com
   `alvo="ativacao"` — ver `app/api/password_reset.py`), nunca um valor de
   senha em texto.
2. **Cada função pública abre e fecha a própria sessão de banco**
   (`SessionLocal()`), em vez de receber `db` de fora. É o mesmo padrão já
   adotado para o streaming do assistente de IA (ver CLAUDE.md, "DOIS BUGS DE
   PRODUÇÃO"): quando a rota que dispara o e-mail devolve a resposta antes do
   envio terminar (`BackgroundTasks`), a sessão do `Depends(get_db)` da rota
   já pode ter sido encerrada — usar uma sessão própria evita
   `DetachedInstanceError` e não depende da ordem exata de finalização das
   dependências do FastAPI.

Envio é sempre best-effort e não bloqueante: se o SMTP não estiver
configurado ou a tentativa falhar, a função grava o resultado em `EmailLog`
e retorna `False` — nunca derruba quem chamou. Não existe fila de
retentativa automática nesta primeira versão (não há Celery/RQ/APScheduler
implantado no projeto); falhas ficam visíveis em `EmailLog` para
investigação manual, mesmo padrão que `password_reset.py` já usa para o
painel `/api/auth/reset-pendentes`.
"""

from __future__ import annotations

import logging
import smtplib
from datetime import datetime, timedelta, timezone
from email.message import EmailMessage
from pathlib import Path

from jinja2 import Environment, FileSystemLoader, select_autoescape

from app.core.config import settings
from app.core.db import SessionLocal
from app.models.email_log import EmailLog
from app.models.password_reset import PasswordResetToken
from app.models.subscription import PLANO_BASICO, PLANO_COMPLETO
from app.models.user import User
from app.services.pdf.marca import LOGO, logo_disponivel
from app.services.pdf_documento import EMPRESA

log = logging.getLogger("meucardio.emails")

_TEMPLATES_DIR = Path(__file__).resolve().parent.parent / "templates" / "emails"
_env_html = Environment(loader=FileSystemLoader(_TEMPLATES_DIR), autoescape=select_autoescape(["html"]))
_env_txt = Environment(loader=FileSystemLoader(_TEMPLATES_DIR), autoescape=False)

RETENCAO_DIAS_APOS_CANCELAMENTO = 30
PRAZO_ATIVACAO_HORAS = 48
PRAZO_RECUPERACAO_HORAS = 1

PLANOS = {
    PLANO_BASICO: {
        "nome": "Assinatura Básica",
        "descricao": "Acesso ao site",
        "preco_formatado": "R$ 49,90",
    },
    PLANO_COMPLETO: {
        "nome": "Assinatura Completa",
        "descricao": "Acesso ao site + CorvIA Mail",
        "preco_formatado": "R$ 59,90",
    },
}


def _fmt_data(dt: datetime | None) -> str:
    if dt is None:
        return "—"
    return dt.astimezone(_fuso()).strftime("%d/%m/%Y")


def _fmt_data_hora(dt: datetime | None) -> str:
    if dt is None:
        return "—"
    return dt.astimezone(_fuso()).strftime("%d/%m/%Y às %H:%M")


def _fuso():
    from zoneinfo import ZoneInfo

    return ZoneInfo(settings.fuso_operacao)


def _fmt_centavos(centavos: int) -> str:
    return f"R$ {centavos / 100:,.2f}".replace(",", "X").replace(".", ",").replace("X", ".")


# --------------------------------------------------------------------------
# Núcleo: renderização, montagem MIME, envio, log
# --------------------------------------------------------------------------


def _renderizar(nome_template: str, contexto: dict) -> tuple[str, str]:
    ctx = {
        **contexto,
        "public_url": settings.public_url,
        "empresa": EMPRESA,
    }
    html = _env_html.get_template(f"{nome_template}.html").render(**ctx)
    corpo_txt = _env_txt.get_template(f"{nome_template}.txt").render(**ctx).rstrip()
    rodape_txt = (
        "\n\n--\n"
        "Corvia — O caminho do coração\n"
        f"{EMPRESA['razao_social']} — CNPJ {EMPRESA['cnpj']}\n"
        f"Política de privacidade: {settings.public_url}/privacidade\n"
        "Você recebeu este e-mail porque tem uma assinatura ativa no Corvia."
    )
    return html, corpo_txt + rodape_txt


def _logo_bytes() -> bytes | None:
    if not logo_disponivel():
        return None
    return LOGO.read_bytes()


def _montar_mensagem(destinatario: str, assunto: str, html: str, texto: str) -> EmailMessage:
    msg = EmailMessage()
    msg["Subject"] = assunto
    msg["From"] = settings.smtp_from
    msg["To"] = destinatario
    msg["Reply-To"] = _reply_to_da_plataforma()
    msg.set_content(texto)
    msg.add_alternative(html, subtype="html")

    logo = _logo_bytes()
    if logo:
        # A parte HTML acabou de ser adicionada como a alternativa mais
        # recente do payload — anexar a imagem A ELA (não à mensagem
        # inteira) transforma só essa alternativa em multipart/related,
        # que é o que faz `cid:corvia-logo` resolver dentro do HTML sem
        # aparecer como anexo separado.
        parte_html = msg.get_payload()[-1]
        parte_html.add_related(logo, maintype="image", subtype="png", cid="<corvia-logo>")
    return msg


def _reply_to_da_plataforma() -> str:
    # O `smtp_from` já é "Corvia <contato@corvia.med.br>" (aprovado pelo
    # Rafael, 02/08/2026); reply-to é o mesmo endereço, sem o nome de exibição.
    de = settings.smtp_from
    if "<" in de and ">" in de:
        return de.split("<", 1)[1].split(">", 1)[0]
    return de


def _smtp_enviar(msg: EmailMessage) -> tuple[bool, str | None]:
    try:
        with smtplib.SMTP(settings.smtp_host, settings.smtp_port, timeout=15) as servidor:
            servidor.starttls()
            servidor.login(settings.smtp_user, settings.smtp_password)
            servidor.send_message(msg)
        return True, None
    except Exception as e:  # noqa: BLE001
        log.exception("Falha ao enviar e-mail transacional para %s", msg["To"])
        return False, str(e)


def _ja_enviado(db, tipo: str, chave_idempotencia: str | None) -> bool:
    if not chave_idempotencia:
        return False
    return (
        db.query(EmailLog)
        .filter(
            EmailLog.tipo == tipo,
            EmailLog.chave_idempotencia == chave_idempotencia,
            EmailLog.sucesso.is_(True),
        )
        .first()
        is not None
    )


def _registrar_log(db, tipo, destinatario, user_id, chave_idempotencia, sucesso, erro) -> None:
    db.add(
        EmailLog(
            tipo=tipo, destinatario=destinatario, user_id=user_id,
            chave_idempotencia=chave_idempotencia, sucesso=sucesso, erro=erro,
        )
    )
    db.commit()


def _enviar(
    db, *, tipo: str, destinatario: str, assunto: str, template: str, contexto: dict,
    user_id: int | None = None, chave_idempotencia: str | None = None,
) -> bool:
    if _ja_enviado(db, tipo, chave_idempotencia):
        log.info("E-mail %s já enviado antes (chave=%s) — não duplicado", tipo, chave_idempotencia)
        return True
    if not settings.smtp_configurado:
        log.info("SMTP não configurado — e-mail %s para %s não enviado", tipo, destinatario)
        _registrar_log(db, tipo, destinatario, user_id, chave_idempotencia, False, "SMTP não configurado")
        return False
    try:
        html, texto = _renderizar(template, {**contexto, "assunto": assunto})
    except Exception as e:  # noqa: BLE001
        log.exception("Falha ao renderizar template de e-mail %s", template)
        _registrar_log(db, tipo, destinatario, user_id, chave_idempotencia, False, f"erro de template: {e}")
        return False
    msg = _montar_mensagem(destinatario, assunto, html, texto)
    sucesso, erro = _smtp_enviar(msg)
    _registrar_log(db, tipo, destinatario, user_id, chave_idempotencia, sucesso, erro)
    return sucesso


def _criar_token_ativacao(db, user_id: int) -> str:
    """Invalida tokens de ativação anteriores ainda não usados (reenvio deve
    tornar o link antigo inerte, como pede o item 2 do spec) e cria um novo."""
    db.query(PasswordResetToken).filter(
        PasswordResetToken.user_id == user_id,
        PasswordResetToken.alvo == "ativacao",
        PasswordResetToken.used.is_(False),
    ).update({"used": True})
    token = PasswordResetToken(
        user_id=user_id, alvo="ativacao",
        expires_at=datetime.now(timezone.utc) + timedelta(hours=PRAZO_ATIVACAO_HORAS),
    )
    db.add(token)
    db.commit()
    db.refresh(token)
    return token.token


# --------------------------------------------------------------------------
# 1. Boas-vindas e ativação da conta
# --------------------------------------------------------------------------


def enviar_boas_vindas(user_id: int, plano_codigo: str, valor_centavos: int, proxima_cobranca: datetime | None) -> bool:
    db = SessionLocal()
    try:
        user = db.get(User, user_id)
        if not user:
            return False
        token = _criar_token_ativacao(db, user_id)
        plano_info = PLANOS.get(plano_codigo, PLANOS[PLANO_BASICO])
        contexto = {
            "nome": user.full_name,
            "email": user.email,
            "plano": {**plano_info, "preco_formatado": _fmt_centavos(valor_centavos)},
            "proxima_cobranca": _fmt_data(proxima_cobranca),
            "link_ativacao": f"{settings.public_url}/ativar-conta?token={token}",
        }
        return _enviar(
            db, tipo="boas_vindas", destinatario=user.email,
            assunto="Bem-vindo à Corvia — ative sua conta",
            template="boas_vindas", contexto=contexto, user_id=user.id,
            chave_idempotencia=f"boas_vindas:{user.id}",
        )
    finally:
        db.close()


# --------------------------------------------------------------------------
# 2. Reenvio do link de ativação
# --------------------------------------------------------------------------


def enviar_reenvio_ativacao(user_id: int) -> bool:
    db = SessionLocal()
    try:
        user = db.get(User, user_id)
        if not user:
            return False
        token = _criar_token_ativacao(db, user_id)
        contexto = {
            "nome": user.full_name,
            "link_ativacao": f"{settings.public_url}/ativar-conta?token={token}",
        }
        return _enviar(
            db, tipo="reenvio_ativacao", destinatario=user.email,
            assunto="Corvia — novo link de ativação",
            template="reenvio_ativacao", contexto=contexto, user_id=user.id,
        )
    finally:
        db.close()


# --------------------------------------------------------------------------
# 3. Recuperação de senha
# --------------------------------------------------------------------------


def enviar_recuperar_senha(user_id: int) -> bool:
    db = SessionLocal()
    try:
        user = db.get(User, user_id)
        if not user:
            return False
        token = PasswordResetToken(
            user_id=user.id, alvo="conta",
            expires_at=datetime.now(timezone.utc) + timedelta(hours=PRAZO_RECUPERACAO_HORAS),
        )
        db.add(token)
        db.commit()
        contexto = {"link": f"{settings.public_url}/redefinir-senha?token={token.token}"}
        return _enviar(
            db, tipo="recuperar_senha", destinatario=user.email,
            assunto="Corvia — redefinição de senha",
            template="recuperar_senha", contexto=contexto, user_id=user.id,
        )
    finally:
        db.close()


# --------------------------------------------------------------------------
# 4. Senha alterada — confirmação
# --------------------------------------------------------------------------


def enviar_senha_alterada(user_id: int, cidade: str | None = None) -> bool:
    db = SessionLocal()
    try:
        user = db.get(User, user_id)
        if not user:
            return False
        contexto = {
            "nome": user.full_name,
            "quando": _fmt_data_hora(datetime.now(timezone.utc)),
            "cidade": cidade,
            "link_suporte": f"{settings.public_url}/minha-conta?suporte=senha",
        }
        return _enviar(
            db, tipo="senha_alterada", destinatario=user.email,
            assunto="Corvia — sua senha foi alterada",
            template="senha_alterada", contexto=contexto, user_id=user.id,
        )
    finally:
        db.close()


# --------------------------------------------------------------------------
# 5. Alteração de plano
# --------------------------------------------------------------------------


def enviar_alteracao_plano(
    user_id: int, plano_anterior_codigo: str, plano_novo_codigo: str,
    valor_novo_centavos: int, vigencia_desde: datetime,
) -> bool:
    db = SessionLocal()
    try:
        user = db.get(User, user_id)
        if not user:
            return False
        anterior = PLANOS.get(plano_anterior_codigo, PLANOS[PLANO_BASICO])
        novo = PLANOS.get(plano_novo_codigo, PLANOS[PLANO_BASICO])

        ganha_perde = []
        aviso_mail = None
        if plano_anterior_codigo == PLANO_BASICO and plano_novo_codigo == PLANO_COMPLETO:
            ganha_perde.append("Você passa a ter acesso ao CorvIA Mail (caixa de e-mail profissional).")
        elif plano_anterior_codigo == PLANO_COMPLETO and plano_novo_codigo == PLANO_BASICO:
            ganha_perde.append("O CorvIA Mail deixa de estar incluído no plano.")
            aviso_mail = (
                "Sua caixa do CorvIA Mail e as mensagens nela seguem acessíveis até o fim do período "
                f"já pago ({_fmt_data(vigencia_desde)}). Depois disso, o acesso à caixa é suspenso, a menos "
                "que você assine o CorvIA Mail separadamente."
            )

        contexto = {
            "nome": user.full_name,
            "plano_anterior": anterior["nome"],
            "plano_novo": novo["nome"],
            "valor_novo": _fmt_centavos(valor_novo_centavos),
            "vigencia_desde": _fmt_data(vigencia_desde),
            "ganha_perde": ganha_perde,
            "aviso_mail": aviso_mail,
        }
        return _enviar(
            db, tipo="alteracao_plano", destinatario=user.email,
            assunto="Corvia — seu plano foi alterado",
            template="alteracao_plano", contexto=contexto, user_id=user.id,
        )
    finally:
        db.close()


# --------------------------------------------------------------------------
# 6. Alteração de cadastro (+ troca de e-mail, caso à parte)
# --------------------------------------------------------------------------


def enviar_alteracao_cadastro(user_id: int, mudancas: list[dict]) -> bool:
    """`mudancas`: [{"campo": "Nome", "antigo": "...", "novo": "..."}, ...].
    Não inclui e-mail — isso é `enviar_troca_email`, disparado à parte."""
    if not mudancas:
        return True
    db = SessionLocal()
    try:
        user = db.get(User, user_id)
        if not user:
            return False
        contexto = {
            "nome": user.full_name, "mudancas": mudancas,
            "quando": _fmt_data_hora(datetime.now(timezone.utc)),
        }
        return _enviar(
            db, tipo="alteracao_cadastro", destinatario=user.email,
            assunto="Corvia — seu cadastro foi alterado",
            template="alteracao_cadastro", contexto=contexto, user_id=user.id,
        )
    finally:
        db.close()


def _mascarar_email(email: str) -> str:
    usuario, _, dominio = email.partition("@")
    if len(usuario) <= 1:
        visivel = usuario
    else:
        visivel = usuario[0]
    return f"{visivel}***@{dominio}"


def enviar_troca_email(user_id: int, email_antigo: str, email_novo: str) -> bool:
    """Dispara os DOIS avisos exigidos pelo spec: confirmação para o novo
    endereço e alerta de segurança para o antigo. A troca em si já aconteceu
    antes desta chamada (ver `POST /api/auth/trocar-email`) — este par de
    e-mails é só notificação, não é o que efetiva a mudança."""
    db = SessionLocal()
    try:
        user = db.get(User, user_id)
        if not user:
            return False
        quando = _fmt_data_hora(datetime.now(timezone.utc))

        ok_novo = _enviar(
            db, tipo="troca_email_novo", destinatario=email_novo,
            assunto="Corvia — confirmação de novo e-mail de acesso",
            template="troca_email_novo",
            contexto={
                "nome": user.full_name, "quando": quando,
                "link_conta": f"{settings.public_url}/minha-conta",
            },
            user_id=user.id,
        )
        ok_antigo = _enviar(
            db, tipo="troca_email_antigo", destinatario=email_antigo,
            assunto="Corvia — o e-mail da sua conta foi alterado",
            template="troca_email_antigo",
            contexto={
                "nome": user.full_name, "quando": quando,
                "novo_email_mascarado": _mascarar_email(email_novo),
                "link_nao_fui_eu": f"{settings.public_url}/minha-conta?suporte=email",
            },
            user_id=user.id,
        )
        return ok_novo and ok_antigo
    finally:
        db.close()


# --------------------------------------------------------------------------
# 7. Pagamento confirmado / recibo
# --------------------------------------------------------------------------


def enviar_pagamento_confirmado(
    user_id: int, valor_centavos: int, data: datetime, plano_nome: str,
    periodo_inicio: datetime, periodo_fim: datetime, ultimos4: str, link_fatura: str,
    chave_idempotencia: str | None = None,
) -> bool:
    """`plano_nome` já vem resolvido de quem chama (billing.py) — cobre tanto
    a assinatura da plataforma (`PLANOS[...]["nome"]`) quanto o CorvIA Mail
    ("CorvIA Mail"), que não usa os códigos `basico`/`completo`."""
    db = SessionLocal()
    try:
        user = db.get(User, user_id)
        if not user:
            return False
        contexto = {
            "nome": user.full_name,
            "valor": _fmt_centavos(valor_centavos),
            "data": _fmt_data(data),
            "plano": plano_nome,
            "periodo_inicio": _fmt_data(periodo_inicio),
            "periodo_fim": _fmt_data(periodo_fim),
            "ultimos4": ultimos4 or "----",
            "link_fatura": link_fatura or f"{settings.public_url}/minha-conta",
        }
        return _enviar(
            db, tipo="pagamento_confirmado", destinatario=user.email,
            assunto="Corvia — pagamento confirmado",
            template="pagamento_confirmado", contexto=contexto, user_id=user.id,
            chave_idempotencia=chave_idempotencia,
        )
    finally:
        db.close()


# --------------------------------------------------------------------------
# 8. Falha no pagamento
# --------------------------------------------------------------------------

PRAZO_TENTATIVAS_DIAS = 7


def enviar_pagamento_falhou(
    user_id: int, dias_restantes: int, data_limite: datetime, link_atualizar_cartao: str,
    chave_idempotencia: str | None = None,
) -> bool:
    db = SessionLocal()
    try:
        user = db.get(User, user_id)
        if not user:
            return False
        contexto = {
            "nome": user.full_name,
            "dias_restantes": max(dias_restantes, 0),
            "data_limite": _fmt_data(data_limite),
            "link_atualizar_cartao": link_atualizar_cartao or f"{settings.public_url}/minha-conta",
        }
        return _enviar(
            db, tipo="pagamento_falhou", destinatario=user.email,
            assunto="Corvia — não conseguimos processar seu pagamento",
            template="pagamento_falhou", contexto=contexto, user_id=user.id,
            chave_idempotencia=chave_idempotencia,
        )
    finally:
        db.close()


# --------------------------------------------------------------------------
# 9. Assinatura cancelada
# --------------------------------------------------------------------------


def enviar_assinatura_cancelada(user_id: int, acesso_ate: datetime, tinha_mail: bool) -> bool:
    db = SessionLocal()
    try:
        user = db.get(User, user_id)
        if not user:
            return False
        contexto = {
            "nome": user.full_name,
            "acesso_ate": _fmt_data(acesso_ate),
            "tinha_mail": tinha_mail,
            "dias_retencao": RETENCAO_DIAS_APOS_CANCELAMENTO,
            "link_reativar": f"{settings.public_url}/assinatura",
        }
        return _enviar(
            db, tipo="assinatura_cancelada", destinatario=user.email,
            assunto="Corvia — assinatura cancelada",
            template="assinatura_cancelada", contexto=contexto, user_id=user.id,
        )
    finally:
        db.close()


# --------------------------------------------------------------------------
# 10. Assinatura suspensa por falta de pagamento (+ aviso de exclusão)
# --------------------------------------------------------------------------


def enviar_assinatura_suspensa(user_id: int, dados_ate: datetime, chave_idempotencia: str | None = None) -> bool:
    db = SessionLocal()
    try:
        user = db.get(User, user_id)
        if not user:
            return False
        contexto = {
            "nome": user.full_name,
            "dados_ate": _fmt_data(dados_ate),
            "link_regularizar": f"{settings.public_url}/assinatura",
        }
        return _enviar(
            db, tipo="assinatura_suspensa", destinatario=user.email,
            assunto="Corvia — acesso suspenso por falta de pagamento",
            template="assinatura_suspensa", contexto=contexto, user_id=user.id,
            chave_idempotencia=chave_idempotencia,
        )
    finally:
        db.close()


def enviar_assinatura_suspensa_aviso_exclusao(
    user_id: int, dias_restantes: int, chave_idempotencia: str,
) -> bool:
    """Disparado no 25º dia de retenção (ver `POST /api/admin/emails/
    verificar-retencao`, chamável por cron diário — não há agendador
    embutido no projeto, mesmo padrão da atualização CMED já documentado
    no CLAUDE.md: um endpoint só, manual e automático convergem nele).
    `chave_idempotencia` inclui o ciclo de suspensão (não só o usuário),
    porque a mesma pessoa pode ser suspensa mais de uma vez ao longo do
    tempo — sem isso, o segundo ciclo nunca mandaria o aviso de novo."""
    db = SessionLocal()
    try:
        user = db.get(User, user_id)
        if not user:
            return False
        contexto = {
            "nome": user.full_name, "dias_restantes": dias_restantes,
            "link_regularizar": f"{settings.public_url}/assinatura",
        }
        return _enviar(
            db, tipo="assinatura_suspensa_aviso_exclusao", destinatario=user.email,
            assunto="Corvia — últimos dias antes da exclusão dos seus dados",
            template="assinatura_suspensa_aviso_exclusao", contexto=contexto, user_id=user.id,
            chave_idempotencia=chave_idempotencia,
        )
    finally:
        db.close()


# --------------------------------------------------------------------------
# 11. CorvIA Mail ativado
# --------------------------------------------------------------------------


def enviar_google_teste_liberado(user_id: int, google_email: str) -> bool:
    """Contraparte do pré-cadastro em GoogleTestUserRequest (app/api/
    agenda_integrada.py) — disparado pelo admin ao marcar o pedido como
    liberado, depois de adicionar o e-mail como testador no Google Cloud."""
    db = SessionLocal()
    try:
        user = db.get(User, user_id)
        if not user:
            return False
        contexto = {
            "nome": user.full_name, "google_email": google_email,
            "link_agenda": f"{settings.public_url}/agenda",
        }
        return _enviar(
            db, tipo="google_teste_liberado", destinatario=user.email,
            assunto="Corvia — sua conexão com o Google já está liberada",
            template="google_teste_liberado", contexto=contexto, user_id=user.id,
            chave_idempotencia=f"google_teste_liberado:{user.id}:{google_email}",
        )
    finally:
        db.close()


def enviar_corvia_mail_ativado(user_id: int, endereco: str) -> bool:
    db = SessionLocal()
    try:
        user = db.get(User, user_id)
        if not user:
            return False
        contexto = {
            "nome": user.full_name, "endereco": endereco,
            "link_painel": f"{settings.public_url}/corvia-mail",
        }
        return _enviar(
            db, tipo="corvia_mail_ativado", destinatario=user.email,
            assunto="Corvia — sua caixa do CorvIA Mail está pronta",
            template="corvia_mail_ativado", contexto=contexto, user_id=user.id,
            chave_idempotencia=f"corvia_mail_ativado:{user.id}",
        )
    finally:
        db.close()


# --------------------------------------------------------------------------
# Material do paciente por e-mail (material-paciente-por-email-spec.md) —
# enviado do endereço do MÉDICO via Mail360, não pelo SMTP da Corvia. Por
# isso não usa `_enviar`/`_montar_mensagem` (esse par é só para e-mails que
# saem como "Corvia", com o logo institucional embutido por CID). Aqui só se
# monta o HTML; quem efetivamente envia é `app/api/exportacao.py`, chamando
# `mail360.enviar_mensagem` com a conta do próprio médico.
# --------------------------------------------------------------------------

ASSUNTO_MATERIAL_PACIENTE = "Material do seu médico — Corvia"


def montar_html_material_paciente(
    nome_paciente: str, nome_medico: str, recado: str | None, url: str, dias_validade: int,
) -> str:
    template = _env_html.get_template("material_paciente.html")
    return template.render(
        nome_paciente=nome_paciente, nome_medico=nome_medico, recado=(recado or "").strip() or None,
        url=url, dias=dias_validade,
    )


# Mesmo padrão do bloco acima (e-mail em nome do médico, não da Corvia) —
# usado por `/api/receituario/documentos/{id}/enviar-email` e
# `/api/document-templates/gerados/{id}/enviar-email`, Trabalho 11
# (ampliação de 06/08/2026), via `services/envio_documento_email.py`.

ASSUNTO_DOCUMENTO_DISPONIVEL = "Corvia — documento do seu médico disponível"


def montar_html_documento_disponivel(
    nome_medico: str, url: str, dias_validade: int, divulgacao_assinatura: str | None = None,
) -> str:
    template = _env_html.get_template("documento_disponivel.html")
    return template.render(
        nome_medico=nome_medico, url=url, dias=dias_validade,
        divulgacao_assinatura=divulgacao_assinatura,
    )
