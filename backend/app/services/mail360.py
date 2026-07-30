"""Cliente da API do Zoho Mail360 — caixa de e-mail do assinante (Tarefa 28).

Referência verificada em 30/07/2026 direto na documentação pública
(zoho.com/mail360/help/api/*), sem conta de parceiro ainda ativa — os
endpoints e formatos abaixo batem com o que está documentado publicamente,
mas não foram testados contra a API real. Confirmar contra uma chamada de
verdade assim que o Rafael tiver as credenciais de parceiro, especialmente:
o formato exato da resposta de `criar_conta` (qual campo é a account_key) e
o formato exato de `listar_mensagens`/`obter_mensagem` — a documentação
pública não detalha o corpo das respostas, só os endpoints e os campos de
entrada.

Autenticação: OAuth de três camadas do Zoho. O client_id/secret/refresh_token
são fixos, gerados uma vez no console de developer do Mail360 e guardados no
`.env` (nunca commitados) — o access_token, sim, é de curta duração (3600s) e
renovado aqui, em memória, sem persistir em banco.
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
# mesma vida do processo. Ver ressalva no topo do arquivo: TTL de 3600s vem
# da documentação, não de teste real.
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
        resp = cliente.post(TOKEN_URL, data={
            "client_id": settings.mail360_client_id,
            "client_secret": settings.mail360_client_secret,
            "refresh_token": settings.mail360_refresh_token,
        })
        resp.raise_for_status()
        dados = resp.json()

    token = dados.get("access_token")
    if not token:
        raise Mail360Error("Mail360 não devolveu access_token na troca do refresh_token.")
    # Margem de 60s antes do vencimento real (3600s), para não correr risco de
    # usar um token que expira no meio de uma chamada em andamento.
    _token_cache["token"] = token
    _token_cache["expira_em"] = agora + 3600 - 60
    return token


def _cabecalho() -> dict[str, str]:
    return {"Authorization": f"Zoho-oauthtoken {_obter_access_token()}"}


def _chamar(metodo: str, caminho: str, headers_extra: dict[str, str] | None = None, **kwargs) -> dict:
    headers = {**_cabecalho(), **(headers_extra or {})}
    try:
        with httpx.Client(timeout=TIMEOUT) as cliente:
            resp = cliente.request(metodo, f"{BASE}{caminho}", headers=headers, **kwargs)
            resp.raise_for_status()
            return resp.json() if resp.content else {}
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
    provedor externo) — não confundir os dois no futuro."""
    dados = _chamar("POST", "/accounts", json={
        "emailid": email_address,
        "accountType": "1",
        "displayName": nome_exibicao,
    })
    # Nome do campo da account_key não confirmado contra resposta real — most
    # likely "accountId"/"account_key" conforme o padrão do restante da API
    # (accounts/{account_key}/...). Ajustar aqui assim que houver acesso real.
    account_key = dados.get("accountKey") or dados.get("account_key") or dados.get("accountId")
    if not account_key:
        raise Mail360Error("Mail360 criou a conta mas não devolveu a account_key esperada — conferir payload real.")
    return str(account_key)


def listar_pastas(account_key: str) -> list[dict]:
    dados = _chamar("GET", f"/accounts/{account_key}/folders")
    return dados.get("data", dados.get("folders", []))


def listar_mensagens(account_key: str, pasta: str | None = None, limite: int = 50) -> list[dict]:
    params = {"limit": limite}
    if pasta:
        params["folder"] = pasta
    dados = _chamar("GET", f"/accounts/{account_key}/messages", params=params)
    return dados.get("data", dados.get("messages", []))


def obter_mensagem(account_key: str, message_id: str) -> dict:
    return _chamar("GET", f"/accounts/{account_key}/messages/{message_id}")


def upload_anexo(account_key: str, nome_arquivo: str, conteudo: bytes) -> str:
    """Sobe o arquivo pro Mail360 e devolve o `fileId` — é ele, não o
    binário, que entra no envio da mensagem. Confirmado em 30/07/2026 direto
    na documentação oficial (zoho.com/mail360/help/api/upload-attachment.html):
    upload é POST separado, corpo é o binário puro (`application/octet-stream`,
    sem multipart), a URL leva o nome do arquivo em query string, e a
    resposta traz o id em `data.fileId`. Não testado contra a API real —
    mesma ressalva do resto do arquivo, ver cabeçalho."""
    dados = _chamar(
        "POST", f"/accounts/{account_key}/attachments",
        params={"fileName": nome_arquivo},
        headers_extra={"Content-Type": "application/octet-stream"},
        content=conteudo,
    )
    file_id = (dados.get("data") or {}).get("fileId")
    if not file_id:
        raise Mail360Error("Mail360 fez upload do anexo mas não devolveu o fileId esperado.")
    return str(file_id)


def enviar_mensagem(
    account_key: str, para: str, assunto: str, corpo_html: str, anexos: list[str] | None = None,
) -> dict:
    corpo: dict = {
        "toAddress": para,
        "subject": assunto,
        "content": corpo_html,
    }
    if anexos:
        # Cada item é o fileId devolvido por upload_anexo — a API não aceita
        # o binário direto aqui, só a referência ao upload já feito.
        corpo["attachments"] = [{"fileId": file_id} for file_id in anexos]
    return _chamar("POST", f"/accounts/{account_key}/messages", json=corpo)


def excluir_mensagem(account_key: str, message_id: str) -> None:
    _chamar("DELETE", f"/accounts/{account_key}/messages/{message_id}")
