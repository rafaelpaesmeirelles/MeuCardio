"""Dado sintético do CorvIA Mail para o modo demonstração do investidor —
issue #52, complemento "INVESTIDOR NO CORVIA MAIL".

Nenhum campo aqui é PII real: remetente, assunto e corpo são fictícios,
escritos para esta finalidade, nunca copiados de mensagem, médico ou
paciente real. Serve só para o investidor conhecer a INTERFACE (lista,
leitura, layout) — nunca para operar e-mail de verdade.

Datas fixas em epoch-ms (não `datetime.now()`): a lista de demonstração
precisa ser estável e reproduzível entre chamadas, não mudar a cada dia.

Mesmo formato de campo que `app/services/mail360.py` devolve
(`folderId`/`folderName`, `messageId`/`subject`/`fromAddress`/
`receivedTime`/`summary`/`status`) — o frontend reaproveita a mesma
renderização da caixa real sem ramificação de formato; só a ORIGEM dos
dados muda (estático aqui, Mail360 real lá).
"""
from __future__ import annotations

EMAIL_DEMO = "investidor.demo@corvia.med.br"

PASTAS_DEMO: list[dict] = [
    {"folderId": "demo-inbox", "folderName": "Entrada", "folderType": "inbox"},
    {"folderId": "demo-sent", "folderName": "Enviados", "folderType": "sent"},
    {"folderId": "demo-drafts", "folderName": "Rascunhos", "folderType": "drafts"},
]

_MENSAGENS: list[dict] = [
    {
        "messageId": "demo-1",
        "subject": "Bem-vindo ao CorvIA Mail — modo demonstração",
        "fromAddress": "equipe.demo@corvia.med.br",
        "summary": (
            "Esta é uma mensagem de demonstração. Esta conta não envia nem "
            "recebe e-mail real — é só para conhecer a interface."
        ),
        "receivedTime": "1754784000000",
        "status": "1",
        "folderId": "demo-inbox",
    },
    {
        "messageId": "demo-2",
        "subject": "Exemplo: solicitação de reagendamento",
        "fromAddress": "paciente.exemplo@example.com",
        "summary": "Mensagem fictícia, sem dado real de paciente — ilustra o layout da lista de mensagens.",
        "receivedTime": "1754697600000",
        "status": "0",
        "folderId": "demo-inbox",
    },
    {
        "messageId": "demo-3",
        "subject": "Exemplo: retorno de laboratório parceiro",
        "fromAddress": "laboratorio.exemplo@example.com",
        "summary": "Segunda mensagem fictícia, para mostrar a caixa com mais de um remetente.",
        "receivedTime": "1754611200000",
        "status": "1",
        "folderId": "demo-inbox",
    },
    {
        "messageId": "demo-4",
        "subject": "Exemplo: convite para evento da especialidade",
        "fromAddress": "eventos.exemplo@example.com",
        "summary": "Terceira mensagem fictícia — a lista de demonstração tem mais de uma entrada de propósito.",
        "receivedTime": "1754524800000",
        "status": "1",
        "folderId": "demo-inbox",
    },
]

_CONTEUDO: dict[str, str] = {
    "demo-1": (
        "<p>Bem-vindo ao <strong>CorvIA Mail</strong>.</p>"
        "<p>Esta é uma conta de demonstração para avaliação do produto. "
        "Nenhuma mensagem aqui é real, e não é possível enviar ou receber "
        "e-mail de verdade nesta conta — funções como enviar, responder, "
        "encaminhar, conectar uma conta externa e sincronizar ficam "
        "indisponíveis no modo investidor.</p>"
    ),
    "demo-2": "<p>Mensagem de exemplo, sem paciente ou dado clínico real — só para ilustrar a leitura de uma mensagem no CorvIA Mail.</p>",
    "demo-3": "<p>Segunda mensagem de exemplo do modo demonstração.</p>",
    "demo-4": "<p>Terceira mensagem de exemplo do modo demonstração.</p>",
}


def pastas_demo() -> list[dict]:
    return [dict(p) for p in PASTAS_DEMO]


def mensagens_demo() -> list[dict]:
    return [dict(m) for m in _MENSAGENS]


def mensagem_demo(message_id: str) -> dict | None:
    base = next((m for m in _MENSAGENS if m["messageId"] == message_id), None)
    if base is None:
        return None
    return {**base, "content": _CONTEUDO.get(message_id, "")}
