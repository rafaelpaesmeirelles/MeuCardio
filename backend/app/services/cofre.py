"""Guarda cifrada de arquivo de exame de paciente.

O que esta cifragem protege e o que não protege, para não haver ilusão:

- **Protege** contra vazamento do volume, do backup ou do disco: sem a chave,
  o conteúdo é ininteligível.
- **Não protege** contra quem tem acesso ao processo do backend, porque o
  backend precisa da chave para exibir o exame a quem vai laudar. Contra isso
  o que vale é controle de acesso e trilha de auditoria — ver as rotas em
  app/api/telediagnostico.py, que registram cada leitura em AuditLog.

Formato do arquivo em disco: nonce de 12 bytes + ciphertext com tag do
AES-256-GCM. O GCM é autenticado, então adulteração do arquivo é detectada na
leitura em vez de devolver lixo silenciosamente.
"""

import base64
import secrets
import uuid
from pathlib import Path

from cryptography.exceptions import InvalidTag
from cryptography.hazmat.primitives.ciphers.aead import AESGCM

from app.core.config import settings

TAMANHO_NONCE = 12


class CofreIndisponivel(RuntimeError):
    """Chave ausente ou malformada. Falha alto de propósito: guardar exame de
    paciente sem cifrar é pior do que recusar o upload."""


def _chave() -> bytes:
    bruta = (settings.storage_encryption_key or "").strip()
    if not bruta:
        raise CofreIndisponivel("STORAGE_ENCRYPTION_KEY não configurada.")
    try:
        chave = base64.urlsafe_b64decode(bruta)
    except Exception as e:  # noqa: BLE001
        raise CofreIndisponivel("STORAGE_ENCRYPTION_KEY não é base64url válida.") from e
    if len(chave) != 32:
        raise CofreIndisponivel("STORAGE_ENCRYPTION_KEY precisa ter 32 bytes (AES-256).")
    return chave


def _raiz(raiz: Path | None = None) -> Path:
    return raiz if raiz is not None else Path(settings.exames_dir)


def guardar(conteudo: bytes, dono_id: int, raiz: Path | None = None) -> str:
    """Cifra e grava. Devolve o nome do arquivo, que é um UUID aleatório —
    nunca nome, CPF ou qualquer dado do paciente.

    `raiz` deixa outro chamador usar este mesmo cofre com outro volume —
    ver `app/services/assinatura/`, que guarda PDF emitido em
    `settings.documentos_dir` em vez de `exames_dir`. Sem isso, um segundo
    tipo de arquivo cifrado exigiria reimplementar AES-256-GCM do zero,
    contra a decisão do Rafael de 29/07/2026 de reaproveitar este cofre."""
    aesgcm = AESGCM(_chave())
    nonce = secrets.token_bytes(TAMANHO_NONCE)
    # O id do dono entra como dado autenticado: um arquivo movido para outro
    # pedido não decifra, em vez de decifrar para o paciente errado.
    cifrado = aesgcm.encrypt(nonce, conteudo, str(dono_id).encode())

    destino = _raiz(raiz)
    destino.mkdir(parents=True, exist_ok=True)
    nome = f"{uuid.uuid4().hex}.bin"
    (destino / nome).write_bytes(nonce + cifrado)
    return nome


def ler(nome: str, dono_id: int, raiz: Path | None = None) -> bytes:
    base = _raiz(raiz)
    caminho = base / nome
    # Impede que um nome manipulado ("../../etc/passwd") escape da pasta.
    if not caminho.resolve().is_relative_to(base.resolve()):
        raise FileNotFoundError(nome)
    if not caminho.exists():
        raise FileNotFoundError(nome)

    dados = caminho.read_bytes()
    aesgcm = AESGCM(_chave())
    try:
        return aesgcm.decrypt(dados[:TAMANHO_NONCE], dados[TAMANHO_NONCE:], str(dono_id).encode())
    except InvalidTag as e:
        raise CofreIndisponivel(
            "Arquivo não pôde ser decifrado: chave trocada ou arquivo adulterado."
        ) from e


def apagar(nome: str, raiz: Path | None = None) -> None:
    base = _raiz(raiz)
    caminho = base / nome
    if caminho.resolve().is_relative_to(base.resolve()):
        caminho.unlink(missing_ok=True)


# --------------------------------------------------------------- em memória --
# O receituário (Tarefa 27) precisa cifrar campo de banco, não arquivo: nome e
# endereço do paciente exigidos pela Portaria 344/98. A decisão do Rafael em
# 29/07/2026 foi reaproveitar ESTE cofre em vez de criar esquema novo — então as
# duas funções abaixo usam a mesma chave, o mesmo AES-256-GCM e o mesmo padrão
# de dado autenticado. O que muda é só o destino: bytes de volta, em vez de
# arquivo em disco.


def cifrar_campo(texto: str, dono_id: int) -> bytes:
    """Cifra um valor para guardar em coluna. `dono_id` entra como dado
    autenticado: valor copiado para outra linha não decifra, em vez de decifrar
    para o paciente errado — mesma garantia que o arquivo já tinha."""
    aesgcm = AESGCM(_chave())
    nonce = secrets.token_bytes(TAMANHO_NONCE)
    return nonce + aesgcm.encrypt(nonce, texto.encode("utf-8"), str(dono_id).encode())


def decifrar_campo(dados: bytes, dono_id: int) -> str:
    aesgcm = AESGCM(_chave())
    try:
        claro = aesgcm.decrypt(dados[:TAMANHO_NONCE], dados[TAMANHO_NONCE:], str(dono_id).encode())
    except InvalidTag as e:
        raise CofreIndisponivel(
            "Campo não pôde ser decifrado: chave trocada ou registro adulterado."
        ) from e
    return claro.decode("utf-8")
