"""PDF clínico efetivamente emitido — Tarefa 4 (assinatura digital).

Por que existe: até aqui, nenhum PDF era persistido — os 4 pontos de emissão
(`api/receituario.py`, `api/documents.py`, `api/documentos_publicos.py` × 2)
geravam bytes na hora e descartavam, e o render nem era determinístico
(`pdf_documento.py` carimbava `datetime.now()` a cada chamada). Assinatura
PAdES se liga a um artefato de bytes estável; sem persistir, não há o que
assinar. Este modelo é esse artefato.

`tipo`/`referencia_id` seguem o mesmo padrão genérico de
`DocumentShareLink` (`models/compartilhamento.py`) em vez de duas FKs
opcionais — evita reabrir a discussão de referência polimórfica que o
próprio projeto já registrou como decisão cara. Mesmo vocabulário de `tipo`:
"prescription_document" ou "generated_document".

Os bytes do PDF **não ficam em coluna nem em `settings.uploads_dir`** — vão
cifrados no cofre já existente (`services/cofre.py`, AES-256-GCM), num
volume próprio (`settings.documentos_dir`) não montado no Caddy, na mesma
filosofia do `exames_dir`. `arquivo_nome` é o nome que `cofre.guardar()`
devolve (UUID aleatório, nunca dado do paciente). `sha256` existe para
verificação de integridade independente da decifragem, e para o teste de
determinismo do render (o mesmo documento, gerado duas vezes, tem que
produzir o mesmo hash).
"""
from datetime import datetime, timezone

from sqlalchemy import DateTime, ForeignKey, Integer, LargeBinary, String
from sqlalchemy.orm import Mapped, mapped_column

from app.core.db import Base


def _agora() -> datetime:
    return datetime.now(timezone.utc)


class DocumentoEmitido(Base):
    __tablename__ = "documentos_emitidos"

    id: Mapped[int] = mapped_column(primary_key=True)
    tipo: Mapped[str] = mapped_column(String(30), index=True)
    referencia_id: Mapped[int] = mapped_column(Integer, index=True)

    # Código do catálogo (`services/assinatura/catalogo.py`) e o nível
    # jurídico daquele código NO MOMENTO da emissão — guardado aqui, e não só
    # resolvido de novo pelo catálogo, porque o catálogo pode mudar de nível
    # depois (ex.: um provedor reclassificado) sem que isso deva reescrever
    # a história do que já foi emitido.
    metodo: Mapped[str] = mapped_column(String(20))
    nivel: Mapped[str] = mapped_column(String(20))

    arquivo_nome: Mapped[str] = mapped_column(String(120))
    sha256: Mapped[str] = mapped_column(String(64))
    bytes_tam: Mapped[int] = mapped_column(Integer)

    # Nula quando metodo == "MANUAL" (não houve assinatura, só emissão).
    assinado_em: Mapped[datetime | None] = mapped_column(DateTime(timezone=True), nullable=True)

    criado_por: Mapped[int] = mapped_column(ForeignKey("users.id"), index=True)
    criado_em: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), default=lambda: datetime.now(timezone.utc)
    )


class DigitalCertificate(Base):
    """Certificado A1 (.pfx/.p12) do próprio médico — provedor `A1_ARQUIVO`
    do catálogo (Trabalho 7, 06/08/2026). Um por médico: reenviar substitui
    o anterior (o arquivo velho é apagado do cofre, não fica órfão).

    O arquivo cifrado não fica em coluna — vai pro cofre já existente
    (`services/cofre.py`, AES-256-GCM), volume próprio
    (`settings.certificados_dir`), mesma filosofia do PDF emitido em
    `DocumentoEmitido` e do exame em `exames_dir`. A SENHA do .pfx também é
    guardada cifrada (`cofre.cifrar_campo`, não é arquivo) porque é exigida
    a cada assinatura — pedir de novo a cada receita inviabilizaria o fluxo,
    e o precedente de reter senha cifrada e reutilizável já existe no
    projeto (senha de app do Yahoo/iCloud, em `CalendarIntegration.
    credentials_cipher`).

    A Corvia NÃO valida a cadeia até a raiz ICP-Brasil — isso é trabalho de
    quem verifica a assinatura depois (Adobe Reader, o validador do ITI, o
    futuro SNCR), o mesmo modelo de confiança de qualquer verificador de
    PAdES. O que este módulo garante é que a chave privada enviada
    realmente assina o PDF; não que o certificado é genuíno ICP-Brasil —
    isso é responsabilidade de quem emitiu (a AC escolhida pelo médico) e de
    quem verifica.
    """

    __tablename__ = "digital_certificates"

    id: Mapped[int] = mapped_column(primary_key=True)
    owner_id: Mapped[int] = mapped_column(ForeignKey("users.id", ondelete="CASCADE"), unique=True, index=True)

    arquivo_nome: Mapped[str] = mapped_column(String(120))
    senha_cifrada: Mapped[bytes] = mapped_column(LargeBinary)

    titular_cn: Mapped[str] = mapped_column(String(255))
    numero_serie: Mapped[str] = mapped_column(String(80))
    valido_ate: Mapped[datetime] = mapped_column(DateTime(timezone=True))
    certificadora: Mapped[str | None] = mapped_column(String(120), nullable=True)

    criado_em: Mapped[datetime] = mapped_column(DateTime(timezone=True), default=_agora)
    atualizado_em: Mapped[datetime] = mapped_column(DateTime(timezone=True), default=_agora, onupdate=_agora)
