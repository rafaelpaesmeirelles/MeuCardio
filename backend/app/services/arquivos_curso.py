"""Armazenamento do material de apoio dos cursos parceiros.

Mesma decisão de topologia do cofre de exames: volume próprio, **não montado no
Caddy**, servido só por rota autenticada. Apostila de curso pago não pode ter URL
alcançável de fora — se estiver no volume que o Caddy publica, basta adivinhar o
nome do arquivo para baixar sem assinar.

Sem a cifragem em repouso do cofre, que existe lá porque aquilo é exame de
paciente. Aqui é material didático: o controle que importa é de acesso, não de
sigilo médico.
"""

import re
import unicodedata
import uuid
from pathlib import Path

DIRETORIO = Path("/materiais-curso")
TAMANHO_MAXIMO = 40 * 1024 * 1024  # 40 MB — apostila em PDF cabe folgado

# Validação por assinatura de arquivo, não por extensão nem por Content-Type,
# pelo mesmo motivo da foto de perfil: os dois são texto que o cliente escreve.
ASSINATURAS = {
    b"%PDF-": ".pdf",
    b"\x50\x4b\x03\x04": ".docx",   # também .pptx e .xlsx — todos são zip
    b"\xff\xd8\xff": ".jpg",
    b"\x89PNG\r\n\x1a\n": ".png",
}


class ArquivoRecusado(Exception):
    pass


def _extensao_por_assinatura(conteudo: bytes) -> str:
    for assinatura, extensao in ASSINATURAS.items():
        if conteudo.startswith(assinatura):
            return extensao
    raise ArquivoRecusado(
        "Formato não reconhecido. Aceitos: PDF, DOCX/PPTX/XLSX, JPG e PNG."
    )


def _nome_seguro(nome: str) -> str:
    """Sanitiza o nome original só para exibição. O nome em disco nunca vem do
    cliente — é um uuid —, então isto não é a defesa contra travessia de
    caminho; é só para o rótulo não carregar lixo."""
    nome = unicodedata.normalize("NFKD", nome).encode("ascii", "ignore").decode()
    nome = re.sub(r"[^\w\s.\-]", "", nome).strip()
    return (nome or "material")[:120]


def guardar(conteudo: bytes, nome_original: str, curso_id: int) -> dict:
    if not conteudo:
        raise ArquivoRecusado("Arquivo vazio.")
    if len(conteudo) > TAMANHO_MAXIMO:
        raise ArquivoRecusado(
            f"Arquivo acima do limite de {TAMANHO_MAXIMO // (1024 * 1024)} MB."
        )

    extensao = _extensao_por_assinatura(conteudo)
    pasta = DIRETORIO / str(curso_id)
    pasta.mkdir(parents=True, exist_ok=True)

    caminho = pasta / f"{uuid.uuid4().hex}{extensao}"
    caminho.write_bytes(conteudo)

    return {
        "caminho": str(caminho),
        "nome_arquivo": _nome_seguro(nome_original),
        "tamanho_bytes": len(conteudo),
        "extensao": extensao,
    }


def ler(caminho: str) -> bytes:
    alvo = Path(caminho).resolve()
    # Um `caminho` vindo do banco deveria ser sempre confiável, mas conferir a
    # raiz custa uma linha e fecha a porta para o caso em que ele deixe de ser.
    if not str(alvo).startswith(str(DIRETORIO.resolve())):
        raise ArquivoRecusado("Caminho fora do diretório de materiais.")
    if not alvo.exists():
        raise ArquivoRecusado("Arquivo não encontrado no armazenamento.")
    return alvo.read_bytes()


def apagar(caminho: str) -> None:
    try:
        alvo = Path(caminho).resolve()
        if str(alvo).startswith(str(DIRETORIO.resolve())) and alvo.exists():
            alvo.unlink()
    except OSError:
        # Falha ao remover o arquivo não pode impedir a remoção do registro:
        # deixar a linha no banco apontando para arquivo que o usuário mandou
        # apagar é pior do que deixar um órfão em disco.
        pass
