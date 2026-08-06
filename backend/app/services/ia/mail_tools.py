"""Tools de e-mail (SOMENTE LEITURA) para o assistente de IA clínico.

Dá ao assistente (ver `app/services/ia/provedor.py`, `app/services/rag.py`,
`app/api/ai.py`) a capacidade de consultar o CorvIA Mail do próprio usuário
autenticado durante uma conversa — listar pastas/mensagens, ler o corpo de
uma mensagem, ver o resumo de não lidas. Escopo fechado a leitura: nenhuma
tool aqui envia, responde ou exclui e-mail.

Duas peças:
- `MAIL_TOOLS_SCHEMA` — a lista de definições de tool no formato de
  tool-calling da Anthropic (`name`/`description`/`input_schema`), pronta
  para entrar no parâmetro `tools=[...]` de `client.messages.create(...)`.
- `executar_tool_mail(nome, argumentos, db, user)` — o despachante, chamado
  pelo loop de tool-use quando o modelo pede uma dessas tools. Devolve
  sempre um dict JSON-serializável, **nunca levanta exceção**: o retorno
  alimenta diretamente um bloco `tool_result`, e uma exceção não tratada
  aqui derrubaria a resposta inteira do assistente no meio da conversa.

Reaproveita os serviços já existentes em vez de reimplementar chamada HTTP:
`app/services/mail360.py` (caixa nativa, Zoho Mail360) e
`app/services/external_mail.py` (Gmail/Outlook via proxy OAuth) — são os
mesmos dois módulos que `app/api/email.py` chama nas rotas de pastas e
mensagens. O padrão de resolução da conta do usuário (`EmailAccount` +
`assinatura_email_ativa`) também é o mesmo já usado em `email.py`
(`_obter_conta`), reproduzido aqui em vez de importado do módulo de rotas
para não acoplar um serviço de IA à camada de API HTTP.

Escopo implicitamente travado ao usuário autenticado: nenhuma tool aqui
recebe parâmetro de "de quem" — toda consulta usa `EmailAccount` resolvida
a partir do próprio `user` passado pelo chamador (o backend, nunca o
modelo). Não há como a IA, por nenhum argumento, ler a caixa de outro
usuário.
"""
from __future__ import annotations

import logging
import re
from html.parser import HTMLParser
from typing import Callable

from sqlalchemy.orm import Session

from app.core.config import settings
from app.core.security import assinatura_email_ativa
from app.models.agenda import CalendarIntegration
from app.models.email_account import EmailAccount
from app.models.user import User
from app.services import external_mail, mail360

log = logging.getLogger("meucardio.ia.mail_tools")

LIMITE_MAXIMO_MENSAGENS = 25
LIMITE_PADRAO_MENSAGENS = 10
LIMITE_CORPO_CARACTERES = 4000

# "google"/"microsoft" são os nomes que o modelo usa; internamente o valor
# de `CalendarIntegration.provider` é o mesmo já usado em `email.py`
# (`_integracao_email`, `contas_da_caixa_unificada`) — não inventar um
# terceiro vocabulário para a mesma coisa.
_PROVEDOR_EXTERNO = {"google": "google_calendar", "microsoft": "microsoft_365"}


# ---------------------------------------------------------------------------
# Schema de tool-calling (formato Anthropic)
# ---------------------------------------------------------------------------

MAIL_TOOLS_SCHEMA: list[dict] = [
    {
        "name": "mail_resumo_caixa",
        "description": (
            "Devolve um resumo mínimo da caixa de e-mail (CorvIA Mail) do usuário autenticado: "
            "se a caixa está ativa e quantas mensagens não lidas existem na pasta de entrada. "
            "Não lista mensagens nem lê conteúdo — use mail_listar_mensagens ou mail_ler_mensagem "
            "para isso. Use esta tool quando o usuário perguntar algo como 'tenho e-mail novo?' "
            "ou 'como está minha caixa de entrada?'."
        ),
        "input_schema": {
            "type": "object",
            "properties": {},
            "required": [],
        },
    },
    {
        "name": "mail_listar_pastas",
        "description": (
            "Lista as pastas da caixa de e-mail nativa do CorvIA Mail (Mail360) e, se o usuário "
            "tiver contas externas conectadas com permissão de leitura, também as pastas do "
            "Gmail e/ou Outlook. Não lê mensagens."
        ),
        "input_schema": {
            "type": "object",
            "properties": {},
            "required": [],
        },
    },
    {
        "name": "mail_listar_mensagens",
        "description": (
            "Lista mensagens de uma pasta da caixa de e-mail do usuário, em forma resumida: "
            "remetente, assunto, data, se está lida e se tem anexo. NUNCA devolve o corpo "
            "completo da mensagem — para ler o conteúdo de uma mensagem específica, use "
            "mail_ler_mensagem com o id devolvido aqui."
        ),
        "input_schema": {
            "type": "object",
            "properties": {
                "pasta": {
                    "type": "string",
                    "description": (
                        "Identificador ou nome da pasta a consultar. Se omitido, usa a pasta de "
                        "entrada (inbox)."
                    ),
                },
                "limite": {
                    "type": "integer",
                    "description": "Quantidade máxima de mensagens a devolver. Padrão 10, máximo 25.",
                },
                "apenas_nao_lidas": {
                    "type": "boolean",
                    "description": "Se verdadeiro, devolve só as mensagens não lidas. Padrão falso.",
                },
                "provedor": {
                    "type": "string",
                    "enum": ["nativo", "google", "microsoft"],
                    "description": (
                        "Qual caixa consultar: 'nativo' é o CorvIA Mail (Mail360); 'google' e "
                        "'microsoft' são contas externas conectadas pelo usuário. Se omitido, "
                        "usa a caixa nativa."
                    ),
                },
            },
            "required": [],
        },
    },
    {
        "name": "mail_ler_mensagem",
        "description": (
            "Lê o conteúdo de UMA mensagem específica da caixa de e-mail do usuário: assunto, "
            "remetente, data, corpo em texto plano (truncado em 4000 caracteres, com aviso "
            "quando truncado) e os nomes dos anexos, se houver — nunca o conteúdo dos anexos. "
            "Marca a mensagem como lida ao abri-la."
        ),
        "input_schema": {
            "type": "object",
            "properties": {
                "message_id": {
                    "type": "string",
                    "description": "Identificador da mensagem, obtido em uma chamada anterior a mail_listar_mensagens.",
                },
                "provedor": {
                    "type": "string",
                    "enum": ["nativo", "google", "microsoft"],
                    "description": (
                        "De qual caixa a mensagem veio: 'nativo' (CorvIA Mail), 'google' ou "
                        "'microsoft'. Se omitido, usa a caixa nativa."
                    ),
                },
            },
            "required": ["message_id"],
        },
    },
]


# ---------------------------------------------------------------------------
# Resolução da conta e erros tratados — nunca levanta exceção
# ---------------------------------------------------------------------------

def _resolver_conta(db: Session, user: User) -> tuple[EmailAccount | None, dict | None]:
    """Resolve a conta de e-mail do usuário autenticado.

    Devolve `(conta, None)` no caminho feliz, ou `(None, erro)` com um dict
    de erro já pronto para virar `tool_result` — nunca levanta `HTTPException`
    nem qualquer outra exceção (isto não é uma rota HTTP, é uma função
    chamada de dentro do loop de tool-calling).
    """
    if not settings.mail360_configurado:
        return None, {
            "erro": "mail_indisponivel",
            "mensagem": "A caixa de e-mail está temporariamente indisponível. Tente novamente mais tarde.",
        }
    conta = db.query(EmailAccount).filter(EmailAccount.user_id == user.id).first()
    if not conta or not assinatura_email_ativa(db, user):
        return None, {
            "erro": "sem_caixa_ativa",
            "mensagem": "Você ainda não tem uma caixa de e-mail CorvIA Mail ativa.",
        }
    if conta.status != "ativa":
        return None, {
            "erro": "caixa_suspensa",
            "mensagem": "Sua caixa de e-mail está suspensa no momento.",
        }
    return conta, None


def _erro_provedor(detalhe_interno: str) -> dict:
    """Falha honesta de provedor externo (rede, credencial expirada, rate
    limit): nunca inventa dado nem finge sucesso. O detalhe técnico vai só
    para o log — a mensagem devolvida ao modelo é genérica de propósito,
    para não vazar informação interna de infraestrutura."""
    log.warning("mail_tools: falha ao falar com o provedor de e-mail: %s", detalhe_interno)
    return {
        "erro": "provedor_indisponivel",
        "mensagem": "Não foi possível falar com o provedor de e-mail agora. Tente novamente em instantes.",
    }


def _erro_mensagem_nao_encontrada(detalhe_interno: str) -> dict:
    log.info("mail_tools: mensagem não encontrada ou inacessível: %s", detalhe_interno)
    return {
        "erro": "mensagem_nao_encontrada",
        "mensagem": "Não foi possível encontrar ou abrir essa mensagem.",
    }


def _erro_provedor_nao_conectado(provedor: str) -> dict:
    nome = {"google": "Google", "microsoft": "Microsoft"}.get(provedor, provedor)
    return {
        "erro": "provedor_nao_conectado",
        "mensagem": f"Nenhuma conta {nome} conectada com permissão de leitura de e-mail.",
    }


def _erro_provedor_invalido() -> dict:
    return {
        "erro": "provedor_invalido",
        "mensagem": "O provedor precisa ser 'nativo', 'google' ou 'microsoft'.",
    }


def _integracao_externa(db: Session, user_id: int, provedor: str) -> CalendarIntegration | None:
    """Conta externa conectada do usuário para o provedor pedido, com
    permissão de leitura de e-mail — mesmo critério de
    `app/api/email.py::_integracao_email`, sem exigir `integration_id`
    explícito (a tool não recebe esse parâmetro): pega a primeira conta
    conectada e habilitada daquele provedor."""
    provider_interno = _PROVEDOR_EXTERNO.get(provedor)
    if not provider_interno:
        return None
    integracao = (
        db.query(CalendarIntegration)
        .filter(
            CalendarIntegration.owner_id == user_id,
            CalendarIntegration.provider == provider_interno,
            CalendarIntegration.enabled.is_(True),
            CalendarIntegration.status == "connected",
        )
        .order_by(CalendarIntegration.id.asc())
        .first()
    )
    if not integracao:
        return None
    capacidades = integracao.capabilities or {}
    if not capacidades.get("read_mail"):
        return None
    return integracao


# ---------------------------------------------------------------------------
# Helpers de mensagem — resumo e sanitização de corpo
# ---------------------------------------------------------------------------

def _nao_lida(mensagem: dict) -> bool:
    """Mesmo critério usado em `app/api/email.py::_nao_lida`: tanto o
    Mail360 quanto os mapeadores de Gmail/Outlook em `external_mail.py`
    usam `status == '0'` para não lida."""
    return str(mensagem.get("status", "")).lower() in {"0", "unread", "nao_lida"}


def _achar_pasta_entrada(pastas: list[dict]) -> str | None:
    entrada = next(
        (
            pasta for pasta in pastas
            if str(
                pasta.get("folderType") or pasta.get("folderName") or pasta.get("name") or ""
            ).lower() in {"inbox", "entrada"}
        ),
        None,
    )
    if not entrada:
        return None
    valor = entrada.get("folderId") or entrada.get("id")
    return str(valor) if valor is not None else None


def _resumo_mensagem(mensagem: dict) -> dict:
    """Lista resumida — NUNCA o corpo completo aqui, só o que basta para o
    modelo escolher qual mensagem pedir com mail_ler_mensagem."""
    message_id = mensagem.get("messageId") or mensagem.get("id") or ""
    remetente = mensagem.get("fromAddress") or mensagem.get("sender") or ""
    assunto = mensagem.get("subject") or "(sem assunto)"
    data = mensagem.get("receivedTime") or mensagem.get("sentDateInGMT") or mensagem.get("date") or ""
    return {
        "id": str(message_id),
        "remetente": str(remetente),
        "assunto": str(assunto),
        "data": str(data),
        "lida": not _nao_lida(mensagem),
        "anexo": bool(mensagem.get("hasAttachment")),
    }


class _TextoDeHTML(HTMLParser):
    """Extrai texto legível de um corpo HTML de e-mail, descartando tags,
    `<script>`/`<style>` e convertendo quebras de bloco em quebra de linha.

    Não precisa ser perfeito — só não pode devolver marcação bruta para o
    modelo (o e-mail já é renderizado isolado/sanitizado no frontend; aqui
    o consumidor é o LLM, que precisa de texto legível, não HTML cru — ver
    o histórico de correção de "corpo do e-mail aparecia como texto bruto
    com tags" no CLAUDE.md do projeto)."""

    _QUEBRA_DE_BLOCO = {
        "p", "div", "br", "li", "tr", "h1", "h2", "h3", "h4", "h5", "h6", "table",
    }
    _IGNORAR = {"script", "style", "head", "title"}

    def __init__(self) -> None:
        super().__init__(convert_charrefs=True)
        self._partes: list[str] = []
        self._profundidade_ignorada = 0

    def handle_starttag(self, tag: str, attrs) -> None:  # noqa: ANN001
        tag = tag.lower()
        if tag in self._IGNORAR:
            self._profundidade_ignorada += 1
        elif tag in self._QUEBRA_DE_BLOCO:
            self._partes.append("\n")

    def handle_startendtag(self, tag: str, attrs) -> None:  # noqa: ANN001
        if tag.lower() == "br":
            self._partes.append("\n")

    def handle_endtag(self, tag: str) -> None:
        tag = tag.lower()
        if tag in self._IGNORAR:
            if self._profundidade_ignorada > 0:
                self._profundidade_ignorada -= 1
        elif tag in self._QUEBRA_DE_BLOCO:
            self._partes.append("\n")

    def handle_data(self, data: str) -> None:
        if not self._profundidade_ignorada:
            self._partes.append(data)

    def texto(self) -> str:
        bruto = "".join(self._partes)
        linhas = [linha.strip() for linha in bruto.splitlines()]
        resultado: list[str] = []
        linha_vazia_anterior = True  # evita linhas em branco no começo
        for linha in linhas:
            if linha:
                resultado.append(linha)
                linha_vazia_anterior = False
            elif not linha_vazia_anterior:
                resultado.append("")
                linha_vazia_anterior = True
        while resultado and resultado[-1] == "":
            resultado.pop()
        return "\n".join(resultado)


def _html_para_texto(bruto: str | None) -> str:
    if not bruto:
        return ""
    if "<" not in bruto:
        # Já é texto puro (ou o provedor não devolveu HTML) — nada a
        # remover, e passar pelo parser à toa só arriscaria alterar o texto.
        return bruto.strip()
    parser = _TextoDeHTML()
    try:
        parser.feed(bruto)
        parser.close()
        texto = parser.texto()
    except Exception:  # noqa: BLE001 — parser malformado não pode derrubar a leitura
        log.warning("mail_tools: falha ao sanitizar HTML do corpo da mensagem, caindo para extração grosseira.")
        texto = re.sub(r"<[^>]+>", " ", bruto)
        texto = re.sub(r"[ \t]+", " ", texto).strip()
    return texto


def _truncar(texto: str, limite: int = LIMITE_CORPO_CARACTERES) -> tuple[str, bool]:
    if len(texto) <= limite:
        return texto, False
    return texto[:limite], True


# ---------------------------------------------------------------------------
# Implementação de cada tool
# ---------------------------------------------------------------------------

def _tool_resumo_caixa(db: Session, user: User, argumentos: dict) -> dict:
    conta, erro = _resolver_conta(db, user)
    if erro:
        return erro
    try:
        pastas = mail360.listar_pastas(conta.mail360_account_key)
        pasta_entrada = _achar_pasta_entrada(pastas)
        mensagens = mail360.listar_mensagens(
            conta.mail360_account_key, pasta=pasta_entrada, limite=50, inicio=1,
        )
    except mail360.Mail360Error as e:
        return _erro_provedor(str(e))
    nao_lidas = sum(1 for m in mensagens if _nao_lida(m))
    return {
        "ativa": True,
        "email_address": conta.email_address,
        "nao_lidas": nao_lidas,
        # Se a pasta tiver mais mensagens do que o lote consultado, a
        # contagem é um piso, não o total exato — melhor sinalizar isso do
        # que devolver um número que parece definitivo e não é.
        "aproximado": len(mensagens) >= 50,
    }


def _tool_listar_pastas(db: Session, user: User, argumentos: dict) -> dict:
    conta, erro = _resolver_conta(db, user)
    if erro:
        return erro

    try:
        pastas_nativas = mail360.listar_pastas(conta.mail360_account_key)
        nativo: dict = {
            "erro": None,
            "pastas": [
                {
                    "id": str(p.get("folderId") or p.get("id") or ""),
                    "nome": str(p.get("folderName") or p.get("name") or ""),
                }
                for p in pastas_nativas
            ],
        }
    except mail360.Mail360Error as e:
        log.warning("mail_tools: falha ao listar pastas nativas: %s", e)
        nativo = {
            "erro": "provedor_indisponivel",
            "mensagem": "Não foi possível listar as pastas da caixa nativa agora.",
            "pastas": [],
        }

    externas: list[dict] = []
    integracoes = (
        db.query(CalendarIntegration)
        .filter(
            CalendarIntegration.owner_id == user.id,
            CalendarIntegration.enabled.is_(True),
            CalendarIntegration.status == "connected",
            CalendarIntegration.provider.in_(list(_PROVEDOR_EXTERNO.values())),
        )
        .order_by(CalendarIntegration.id.asc())
        .all()
    )
    provedor_por_valor_interno = {v: k for k, v in _PROVEDOR_EXTERNO.items()}
    for integracao in integracoes:
        capacidades = integracao.capabilities or {}
        if not capacidades.get("read_mail"):
            continue
        provedor_nome = provedor_por_valor_interno.get(integracao.provider, integracao.provider)
        try:
            pastas_ext = external_mail.list_folders(db, integracao)
            externas.append({
                "provedor": provedor_nome,
                "conta": integracao.display_name,
                "erro": None,
                "pastas": [
                    {
                        "id": str(p.get("folderId") or p.get("id") or ""),
                        "nome": str(p.get("folderName") or ""),
                    }
                    for p in pastas_ext
                ],
            })
        except external_mail.ExternalMailError as e:
            log.warning("mail_tools: falha ao listar pastas de %s: %s", provedor_nome, e)
            externas.append({
                "provedor": provedor_nome,
                "conta": integracao.display_name,
                "erro": "provedor_indisponivel",
                "mensagem": "Não foi possível listar as pastas dessa conta agora.",
                "pastas": [],
            })

    return {"nativo": nativo, "externas": externas}


def _tool_listar_mensagens(db: Session, user: User, argumentos: dict) -> dict:
    conta, erro = _resolver_conta(db, user)
    if erro:
        return erro

    pasta = argumentos.get("pasta")
    if pasta is not None:
        pasta = str(pasta)

    try:
        limite = int(argumentos.get("limite", LIMITE_PADRAO_MENSAGENS))
    except (TypeError, ValueError):
        limite = LIMITE_PADRAO_MENSAGENS
    # Clamp, nunca erro: limite fora da faixa é corrigido em silêncio, não
    # motivo para recusar a chamada.
    limite = max(1, min(limite, LIMITE_MAXIMO_MENSAGENS))

    apenas_nao_lidas = bool(argumentos.get("apenas_nao_lidas", False))
    provedor = str(argumentos.get("provedor") or "nativo").strip().lower()

    if provedor == "nativo":
        try:
            mensagens = mail360.listar_mensagens(
                conta.mail360_account_key, pasta=pasta, limite=limite, inicio=1,
            )
        except mail360.Mail360Error as e:
            return _erro_provedor(str(e))
    elif provedor in _PROVEDOR_EXTERNO:
        integracao = _integracao_externa(db, user.id, provedor)
        if integracao is None:
            return _erro_provedor_nao_conectado(provedor)
        try:
            mensagens = external_mail.list_messages(
                db, integracao, folder=pasta, limit=limite, start=1,
            )
        except external_mail.ExternalMailError as e:
            return _erro_provedor(str(e))
    else:
        return _erro_provedor_invalido()

    if apenas_nao_lidas:
        mensagens = [m for m in mensagens if _nao_lida(m)]

    return {
        "provedor": provedor,
        "pasta": pasta,
        "mensagens": [_resumo_mensagem(m) for m in mensagens[:limite]],
    }


def _tool_ler_mensagem(db: Session, user: User, argumentos: dict) -> dict:
    conta, erro = _resolver_conta(db, user)
    if erro:
        return erro

    message_id = str(argumentos.get("message_id") or "").strip()
    if not message_id:
        return {
            "erro": "parametro_invalido",
            "mensagem": "Informe o identificador da mensagem (message_id).",
        }
    provedor = str(argumentos.get("provedor") or "nativo").strip().lower()

    anexos: list[str] = []
    if provedor == "nativo":
        try:
            mensagem = mail360.obter_mensagem(conta.mail360_account_key, message_id)
        except mail360.Mail360Error as e:
            return _erro_mensagem_nao_encontrada(str(e))
        # Marcar como lida é efeito colateral esperado de abrir a mensagem
        # (mesmo comportamento de `GET /api/email/mensagens/{id}` em
        # `email.py`) — falha nisso não pode esconder um corpo já obtido.
        try:
            mail360.alterar_mensagens(conta.mail360_account_key, [message_id], "lida")
        except mail360.Mail360Error:
            pass
        try:
            lista_anexos = mail360.listar_anexos(conta.mail360_account_key, message_id)
            anexos = [
                str(a.get("attachmentName") or a.get("fileName") or a.get("name") or "anexo")
                for a in lista_anexos
            ]
        except mail360.Mail360Error:
            anexos = []
        corpo_bruto = mensagem.get("content")
    elif provedor in _PROVEDOR_EXTERNO:
        integracao = _integracao_externa(db, user.id, provedor)
        if integracao is None:
            return _erro_provedor_nao_conectado(provedor)
        try:
            mensagem = external_mail.get_message(db, integracao, message_id)
        except external_mail.ExternalMailError as e:
            return _erro_mensagem_nao_encontrada(str(e))
        # `external_mail.py` não expõe listagem de nomes de anexo hoje — não
        # inventar um endpoint que o serviço não tem; lista vazia é honesto.
        anexos = []
        corpo_bruto = mensagem.get("content") or mensagem.get("htmlContent")
    else:
        return _erro_provedor_invalido()

    texto = _html_para_texto(corpo_bruto)
    corpo, truncado = _truncar(texto)

    return {
        "provedor": provedor,
        "id": str(mensagem.get("messageId") or mensagem.get("id") or message_id),
        "assunto": str(mensagem.get("subject") or "(sem assunto)"),
        "remetente": str(mensagem.get("fromAddress") or mensagem.get("sender") or ""),
        "data": str(
            mensagem.get("receivedTime") or mensagem.get("sentDateInGMT") or mensagem.get("date") or ""
        ),
        "corpo": corpo,
        "truncado": truncado,
        "anexos": anexos,
    }


# ---------------------------------------------------------------------------
# Despachante
# ---------------------------------------------------------------------------

_HANDLERS: dict[str, Callable[[Session, User, dict], dict]] = {
    "mail_resumo_caixa": _tool_resumo_caixa,
    "mail_listar_pastas": _tool_listar_pastas,
    "mail_listar_mensagens": _tool_listar_mensagens,
    "mail_ler_mensagem": _tool_ler_mensagem,
}


def executar_tool_mail(nome: str, argumentos: dict, db: Session, user: User) -> dict:
    """Despacha uma chamada de tool de e-mail para a função correspondente.

    Sempre devolve um dict JSON-serializável — **nunca levanta exceção**,
    inclusive diante de falha totalmente inesperada (bug em algum dos
    serviços, formato de resposta imprevisto do provedor, etc.): o retorno
    vira `tool_result` dentro do loop de tool-calling do assistente, e uma
    exceção não tratada aqui interromperia a resposta inteira no meio da
    conversa em vez de deixar o modelo lidar com uma falha.
    """
    handler = _HANDLERS.get(nome)
    if handler is None:
        return {
            "erro": "tool_desconhecida",
            "mensagem": f"Tool de e-mail desconhecida: {nome}.",
        }
    try:
        return handler(db, user, argumentos or {})
    except Exception:  # noqa: BLE001 — última rede de segurança, de propósito ampla
        log.exception("mail_tools: falha inesperada executando %s", nome)
        return {
            "erro": "falha_interna",
            "mensagem": "Não foi possível concluir essa operação na caixa de e-mail agora.",
        }
