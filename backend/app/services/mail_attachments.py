"""Anexos binários gerados no servidor, compartilhados pelos transportes de e-mail."""
from dataclasses import dataclass
from email.message import EmailMessage


@dataclass(frozen=True)
class MailAttachment:
    filename: str
    content: bytes
    content_type: str = "application/octet-stream"


def add_attachments(message: EmailMessage, attachments: list[MailAttachment] | None) -> None:
    for attachment in attachments or []:
        maintype, _, subtype = attachment.content_type.partition("/")
        message.add_attachment(
            attachment.content, maintype=maintype or "application", subtype=subtype or "octet-stream",
            filename=attachment.filename,
        )
