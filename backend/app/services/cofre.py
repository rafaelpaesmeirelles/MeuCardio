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


def _raiz() -> Path:
    return Path(settings.exames_dir)


def guardar(conteudo: bytes, dono_id: int) -> str:
    """Cifra e grava. Devolve o nome do arquivo, que é um UUID aleatório —
    nunca nome, CPF ou qualquer dado do paciente."""
    aesgcm = AESGCM(_chave())
    nonce = secrets.token_bytes(TAMANHO_NONCE)
    # O id do dono entra como dado autenticado: um arquivo movido para outro
    # pedido não decifra, em vez de decifrar para o paciente errado.
    cifrado = aesgcm.encrypt(nonce, conteudo, str(dono_id).encode())

    destino = _raiz()
    destino.mkdir(parents=True, exist_ok=True)
    nome = f"{uuid.uuid4().hex}.bin"
    (destino / nome).write_bytes(nonce + cifrado)
    return nome


def ler(nome: str, dono_id: int) -> bytes:
    caminho = _raiz() / nome
    # Impede que um nome manipulado ("../../etc/passwd") escape da pasta.
    if not caminho.resolve().is_relative_to(_raiz().resolve()):
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


def apagar(nome: str) -> None:
    caminho = _raiz() / nome
    if caminho.resolve().is_relative_to(_raiz().resolve()):
        caminho.unlink(missing_ok=True)
