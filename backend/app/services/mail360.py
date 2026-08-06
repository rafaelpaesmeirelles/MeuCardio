"""Cliente da API do Zoho Mail360 — caixa de e-mail do assinante (Tarefa 28).

**Testado de ponta a ponta contra a API real em 30/07/2026**, com credencial
do Rafael e domínio `corvia.med.br` já verificado dentro do Mail360 (o
bloqueio de "Local domain does not exists", registrado antes nesta mesma
sessão, foi resolvido do lado da Zoho — Domains → Add domain → verificar).
Conta de teste criada (`teste-api@corvia.med.br`), e todas as sete funções
deste módulo confirmadas: criar conta, listar pastas, enviar mensagem com e
sem anexo, listar mensagens, ler mensagem (metadado + conteúdo), subir
anexo, excluir mensagem. Quatro coisas que só a resposta real revelou, e que
a documentação pública não deixava claro:

1. **Toda resposta vem embrulhada em `{"status": {...}, "data": ...}`** —
   inclusive listas. `_chamar()` desembrulha isso na origem, então quem
   chama não repete essa checagem.
2. **`/access-token` exige corpo em JSON**, não form-encoded como um endpoint
   OAuth comum — mandar `data=` (form) devolve 400 `JSON_PARSE_ERROR`.
3. **`expires_in` não é uma duração em segundos** (como a doc pública sugere)
   — é um timestamp absoluto em milissegundos. Não dá pra confiar nesse
   valor literal para calcular o cache; ver `_obter_access_token`.
4. **`POST /messages` exige `fromAddress`** — sem ele, devolve 500 `"Given
   FromAddress not exists!"`. A API não deriva o remetente do `account_key`
   sozinha; `enviar_mensagem()` agora recebe o endereço da caixa como
   parâmetro explícito.

`obter_mensagem` chama dois endpoints e funde o resultado: metadado
(`/messages/{id}` — subject/fromAddress/receivedTime, sem `content`) e
conteúdo (`/messages/{id}/content` — só `messageId` e `content`),
confirmado com uma mensagem real enviada e lida de volta.

Autenticação: OAuth de três camadas do Zoho. O client_id/secret/refresh_token
são fixos, gerados uma vez no painel do próprio Mail360 (Authentication, não
o console genérico de developer da Zoho) e guardados no `.env` (nunca
commitados) — o access_token, sim, é de curta duração (~1h) e renovado aqui,
em memória, sem persistir em banco.
"""
from __future__ import annotations

import logging
import time

import httpx

from app.core.config import settings

log = logging.getLogger("meucardio.mail360")

BASE = "https://mail360.zoho.com/api"
TOKEN_URL = f"{BASE}/access-token"
TIMEOUT = 10.0

# Cache do access token em memória do processo — não precisa sobreviver a um
# restart do backend, só evitar pedir token novo a cada chamada dentro da
# mesma vida do processo. TTL fixo de 55min por decisão deliberada, não pelo
# `expires_in` da resposta: esse campo veio, na prática, como timestamp
# absoluto em milissegundos (época Unix), não como duração em segundos — não
# dá pra converter isso num prazo relativo a `time.monotonic()` com confiança,
# e o comportamento real da Zoho pode mudar. 55min fica com margem folgada
# sobre a validade observada (~59min).
_TTL_TOKEN_SEGUNDOS = 55 * 60
_token_cache: dict[str, float | str] = {"token": "", "expira_em": 0.0}


class Mail360Error(Exception):
    """Erro de comunicação com o Mail360 — nunca deve derrubar a rota que a
    chamou sem tradução: quem chama decide se isso vira 502 ou mensagem
    amigável ao assinante."""


def _obter_access_token() -> str:
    agora = time.monotonic()
    if _token_cache["token"] and agora < float(_token_cache["expira_em"]):
        return str(_token_cache["token"])

    with httpx.Client(timeout=TIMEOUT) as cliente:
        # JSON, não form-encoded — `/access-token` devolve 400
        # `JSON_PARSE_ERROR` com `data=` (confirmado em 30/07/2026 contra a
        # API real). Diferente da maioria dos endpoints OAuth por aí.
        resp = cliente.post(TOKEN_URL, json={
            "client_id": settings.mail360_client_id,
            "client_secret": settings.mail360_client_secret,
            "refresh_token": settings.mail360_refresh_token,
        })
        resp.raise_for_status()
        dados = (resp.json() or {}).get("data") or {}

    token = dados.get("access_token")
    if not token:
        raise Mail360Error("Mail360 não devolveu access_token na troca do refresh_token.")
    _token_cache["token"] = token
    _token_cache["expira_em"] = agora + _TTL_TOKEN_SEGUNDOS
    return token


def _cabecalho() -> dict[str, str]:
    return {"Authorization": f"Zoho-oauthtoken {_obter_access_token()}"}


def _chamar(metodo: str, caminho: str, headers_extra: dict[str, str] | None = None, **kwargs):
    """Desembrulha `{"status": {...}, "data": ...}` — confirmado em
    30/07/2026 contra a API real que TODA resposta do Mail360 tem esse
    envelope, inclusive as que devolvem lista (a lista fica em `data`
    diretamente, não `data.items` nem nada aninhado). Quem chama recebe já
    o conteúdo útil: um dict para endpoint de objeto único, uma lista para
    endpoint de coleção."""
    headers = {**_cabecalho(), **(headers_extra or {})}
    try:
        with httpx.Client(timeout=TIMEOUT) as cliente:
            resp = cliente.request(metodo, f"{BASE}{caminho}", headers=headers, **kwargs)
            resp.raise_for_status()
            corpo = resp.json() if resp.content else {}
            return corpo.get("data", corpo) if isinstance(corpo, dict) else corpo
    except httpx.HTTPStatusError as e:
        log.error("Mail360 %s %s devolveu %s: %s", metodo, caminho, e.response.status_code, e.response.text[:300])
        raise Mail360Error(f"Mail360 devolveu erro {e.response.status_code}.") from e
    except httpx.HTTPError as e:
        log.error("Mail360 %s %s falhou: %s", metodo, caminho, e)
        raise Mail360Error("Não foi possível falar com o Mail360.") from e


def criar_conta_nativa(email_address: str, nome_exibicao: str) -> str:
    """Cria a caixa nativa no domínio configurado e devolve a account_key.

    `accountType: "1"` é o valor documentado para conta nativa (hospedada
    pelo próprio Mail360), em oposição a conta de sincronização (linkar
    provedor externo) — não confundir os dois no futuro.

    Campo confirmado contra a doc oficial com exemplo de resposta real
    (zoho.com/mail360/help/api/add-native-account-api.html) em 30/07/2026:
    é `account_key`, snake_case — os outros dois nomes ficam como
    salvaguarda barata, não como suposição igualmente provável."""
    dados = _chamar("POST", "/accounts", json={
        "emailid": email_address,
        "accountType": "1",
        "displayName": nome_exibicao,
    })
    account_key = dados.get("account_key") or dados.get("accountKey") or dados.get("accountId")
    if not account_key:
        raise Mail360Error("Mail360 criou a conta mas não devolveu a account_key esperada — conferir payload real.")
    return str(account_key)


def listar_pastas(account_key: str) -> list[dict]:
    """Campos confirmados contra a doc oficial com exemplo de resposta real
    (get-all-folders-api.html) em 30/07/2026: `folderId`, `folderName`."""
    return _chamar("GET", f"/accounts/{account_key}/folders")


def listar_mensagens(
    account_key: str, pasta: str | None = None, limite: int = 50, inicio: int = 1,
) -> list[dict]:
    """Campos confirmados contra a doc oficial com exemplo de resposta real
    (list-emails-messages-api.html) em 30/07/2026: `messageId`, `subject`,
    `fromAddress`, `receivedTime` (epoch ms), `summary` — batem com o que
    `frontend/src/pages/CaixaDeEmail.tsx` já espera, sem mudança lá."""
    params = {"limit": max(1, min(limite, 200)), "start": max(1, inicio)}
    if pasta:
        # A API real rejeita `folder` com MA_9018 EXTRA_PARAM_FOUND. O nome
        # documentado e aceito é `folderId`.
        params["folderId"] = pasta
    return _chamar("GET", f"/accounts/{account_key}/messages", params=params)


def obter_mensagem(account_key: str, message_id: str) -> dict:
    """Metadado e conteúdo são DOIS endpoints diferentes na API real —
    confirmado em 30/07/2026 contra a doc oficial com exemplo de resposta:
    `/messages/{id}` traz `subject`/`fromAddress`/`receivedTime`/etc. mas
    NÃO `content`; `/messages/{id}/content` traz só `messageId` e `content`
    (HTML). Sem essa segunda chamada, a mensagem abria sem corpo nenhum."""
    metadado = _chamar("GET", f"/accounts/{account_key}/messages/{message_id}")
    try:
        conteudo = _chamar("GET", f"/accounts/{account_key}/messages/{message_id}/content")
    except Mail360Error:
        # Falha ao buscar o corpo não deve esconder o resto da mensagem —
        # o assunto/remetente ainda são úteis mesmo sem o texto.
        log.warning("Mail360: metadado da mensagem %s ok, conteúdo falhou.", message_id)
        conteudo = {}
    return {**metadado, "content": conteudo.get("content")}


def alterar_mensagens(
    account_key: str,
    message_ids: list[str],
    acao: str,
    *,
    pasta_destino: str | None = None,
    sinalizador: str | None = None,
) -> None:
    """Aplica ações em lote usando o único endpoint de atualização do Mail360.

    Os nomes de `mode` e dos campos são os documentados pelo provedor. Manter
    essa tradução no cliente impede que a API HTTP da Corvia aceite payloads
    arbitrários e os repasse ao Mail360.
    """
    ids = [str(message_id) for message_id in message_ids if str(message_id).strip()]
    if not ids:
        raise Mail360Error("Nenhuma mensagem foi selecionada.")

    modos = {
        "lida": "markAsRead",
        "nao_lida": "markAsUnread",
        "mover": "moveMessage",
        "sinalizar": "setFlag",
    }
    modo = modos.get(acao)
    if not modo:
        raise Mail360Error("Ação de mensagem inválida.")

    corpo: dict[str, object] = {"mode": modo, "messageId": ids}
    if acao == "mover":
        if not pasta_destino:
            raise Mail360Error("Informe a pasta de destino.")
        corpo["destfolderId"] = str(pasta_destino)
    if acao == "sinalizar":
        sinalizadores = {"info", "important", "followup", "flag_not_set"}
        if sinalizador not in sinalizadores:
            raise Mail360Error("Sinalizador inválido.")
        corpo["flagid"] = sinalizador

    _chamar("PUT", f"/accounts/{account_key}/messages", json=corpo)


def responder_mensagem(
    account_key: str,
    message_id: str,
    remetente: str,
    acao: str,
    assunto: str,
    conteudo: str,
    *,
    para: str | None = None,
    cc: str | None = None,
    cco: str | None = None,
    anexos: list[str] | None = None,
    mail_format: str = "plaintext",
) -> dict:
    """Responde, responde a todos ou encaminha preservando a conversa real.
    `mail_format` — ver a nota em `enviar_mensagem`, mesma regra."""
    if acao not in {"reply", "replyall", "forward"}:
        raise Mail360Error("Ação de resposta inválida.")
    if acao == "forward" and not para:
        raise Mail360Error("Informe o destinatário do encaminhamento.")
    if mail_format not in ("html", "plaintext"):
        raise Mail360Error(f"mail_format inválido: {mail_format!r}.")

    corpo: dict[str, object] = {
        "fromAddress": remetente,
        "action": acao,
        "subject": assunto,
        "content": conteudo,
        "mailFormat": mail_format,
    }
    if para:
        corpo["toAddress"] = para
    if cc:
        corpo["ccAddress"] = cc
    if cco:
        corpo["bccAddress"] = cco
    if anexos:
        corpo["attachments"] = [{"fileId": file_id} for file_id in anexos]
    return _chamar(
        "POST", f"/accounts/{account_key}/messages/{message_id}", json=corpo,
    )


def listar_anexos(account_key: str, message_id: str) -> list[dict]:
    dados = _chamar(
        "GET",
        f"/accounts/{account_key}/messages/{message_id}/attachments",
        params={"includeInline": "false"},
    )
    if isinstance(dados, list):
        return dados
    if isinstance(dados, dict):
        anexos = dados.get("attachments") or []
        return anexos if isinstance(anexos, list) else []
    return []


def baixar_anexo(account_key: str, message_id: str, attachment_id: str) -> tuple[bytes, str]:
    """Baixa bytes sem passar por `_chamar`, que pressupõe resposta JSON."""
    try:
        with httpx.Client(timeout=TIMEOUT) as cliente:
            resp = cliente.get(
                f"{BASE}/accounts/{account_key}/messages/{message_id}/attachments/{attachment_id}",
                headers={**_cabecalho(), "Accept": "application/octet-stream"},
            )
            resp.raise_for_status()
            return resp.content, resp.headers.get("content-type", "application/octet-stream")
    except httpx.HTTPError as e:
        log.error("Mail360 falhou ao baixar anexo: %s", e)
        raise Mail360Error("Não foi possível baixar o anexo.") from e


def upload_anexo(account_key: str, nome_arquivo: str, conteudo: bytes) -> str:
    """Sobe o arquivo pro Mail360 e devolve o `fileId` — é ele, não o
    binário, que entra no envio da mensagem. Confirmado em 30/07/2026 direto
    na documentação oficial (zoho.com/mail360/help/api/upload-attachment.html):
    upload é POST separado, corpo é o binário puro (`application/octet-stream`,
    sem multipart), a URL leva o nome do arquivo em query string, e a
    resposta traz o id em `data.fileId` — já desembrulhado por `_chamar`.
    Testado contra a API real em 30/07/2026 (ver cabeçalho do módulo)."""
    dados = _chamar(
        "POST", f"/accounts/{account_key}/attachments",
        params={"fileName": nome_arquivo},
        headers_extra={"Content-Type": "application/octet-stream"},
        content=conteudo,
    )
    file_id = dados.get("fileId")
    if not file_id:
        raise Mail360Error("Mail360 fez upload do anexo mas não devolveu o fileId esperado.")
    return str(file_id)


def enviar_mensagem(
    account_key: str, remetente: str, para: str, assunto: str, corpo_html: str,
    anexos: list[str] | None = None, cc: str | None = None, cco: str | None = None,
    mail_format: str = "plaintext",
) -> dict:
    """`fromAddress` é obrigatório — confirmado em 30/07/2026 contra a API
    real: sem ele, `/messages` devolve 500 "Given FromAddress not exists!".
    A API não deriva o remetente do `account_key` sozinha, então quem chama
    precisa passar o endereço da própria caixa (`conta.email_address`).

    `mail_format`: "plaintext" (padrão, igual ao comportamento de sempre —
    hoje o compositor do CorvIA Mail é um `<textarea>` puro, não um editor
    rico, então o texto do médico nunca contém HTML de verdade) ou "html"
    (usado quando a assinatura de e-mail está ligada — ver
    `app/services/email_signature.py` — porque ela precisa renderizar um
    `<img>`, não aparecer como tag literal). Confirmado contra a doc oficial
    do Mail360 em 06/08/2026: `mailFormat` aceita `html`/`plaintext`."""
    if mail_format not in ("html", "plaintext"):
        raise Mail360Error(f"mail_format inválido: {mail_format!r}.")
    corpo: dict = {
        "fromAddress": remetente,
        "toAddress": para,
        "subject": assunto,
        "content": corpo_html,
        "mailFormat": mail_format,
    }
    if cc:
        corpo["ccAddress"] = cc
    if cco:
        corpo["bccAddress"] = cco
    if anexos:
        # Cada item é o fileId devolvido por upload_anexo — a API não aceita
        # o binário direto aqui, só a referência ao upload já feito.
        corpo["attachments"] = [{"fileId": file_id} for file_id in anexos]
    return _chamar("POST", f"/accounts/{account_key}/messages", json=corpo)


def excluir_mensagem(account_key: str, message_id: str) -> None:
    _chamar("DELETE", f"/accounts/{account_key}/messages/{message_id}")
