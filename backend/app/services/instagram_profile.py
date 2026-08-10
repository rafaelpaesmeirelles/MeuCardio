"""Foto de perfil pública do Instagram, a partir do handle que o médico
digitou no cadastro (tarefa #43, 08/08/2026).

Decisão já tomada com o Rafael, não reabrir: o handle é só o que o médico
digita — nunca buscado/adivinhado por nome ou e-mail. Correlação automática
por nome/e-mail foi rejeitada por questão de privacidade/LGPD e pelos Termos
de Uso da plataforma. Esta função busca UM handle específico, exatamente o
texto digitado — nunca uma lista, nunca um resultado de busca.

LIMITAÇÃO REAL, verificada nesta sessão (08/08/2026) — leia antes de mexer:
não existe hoje nenhuma API oficial e gratuita para "ler a foto pública de
um handle qualquer que o médico digitou". A Instagram Graph API (a via
oficial) exige que o app seja revisado pela Meta e, para ler o perfil de
OUTRA conta que não a do próprio dono do app, exige parceria comercial de
Business Discovery — inviável para este caso de uso e fora de escopo aqui.

O que foi usado no lugar é o endpoint interno, NÃO documentado e SEM
contrato de estabilidade, que o próprio instagram.com chama para montar a
página pública de perfil (`i.instagram.com/api/v1/users/web_profile_info`).
Testado manualmente nesta sessão contra perfis públicos reais: devolveu
`profile_pic_url_hd` corretamente (HTTP 200 + JSON), 404 em handle
inexistente, e nenhum bloqueio percebido em rajada curta de chamadas — mas:
- a Meta pode mudar o formato da resposta, exigir cabeçalho novo, ou
  bloquear por IP/região a qualquer momento, sem aviso prévio nenhum;
- não é a forma "oficial" de acessar o dado — é a mais confiável
  disponível sem custo e sem parceria comercial, dado o que já foi
  decidido para este recurso;
- por isso o FALLBACK (avatar genérico, já implementado no frontend) é o
  caminho principal e testado — a foto do Instagram é sempre um extra
  opcional, nunca uma dependência de nenhuma tela.

Qualquer falha (perfil inexistente, privado, formato de resposta mudou,
bloqueio, timeout, erro de rede) é tratada em silêncio aqui: best-effort,
nunca deve derrubar o cadastro nem travar o carregamento de tela nenhuma.
"""

import logging
import secrets
from pathlib import Path
from urllib.parse import urlparse

import httpx

from app.core.config import settings
from app.core.uploads import UploadRejected, atomic_write_bytes, validate_file

log = logging.getLogger("meucardio.instagram")

# Achado de auditoria (issue #52, subfase 8): `url_foto`, usada para a
# segunda chamada de rede abaixo, vem do CORPO da resposta do Instagram, não
# de um valor fixo nosso — em condição normal é sempre um domínio de CDN da
# Meta, mas nada no código validava isso antes de buscar. Defesa em
# profundidade contra a resposta um dia trazer um destino inesperado (ex.:
# endpoint comprometido, formato mudado): só busca se o host for um dos
# domínios de CDN conhecidos da Meta, sempre por HTTPS. Severidade baixa na
# prática — o conteúdo baixado já passa por `validate_file` antes de
# persistir, e nada da resposta é devolvido ao cliente —, mas o custo da
# checagem é mínimo.
_HOSTS_CDN_PERMITIDOS = ("cdninstagram.com", "fbcdn.net")


def _host_de_cdn_confiavel(url: str) -> bool:
    try:
        partes = urlparse(url)
    except ValueError:
        return False
    if partes.scheme != "https" or not partes.hostname:
        return False
    host = partes.hostname.lower()
    return any(host == dominio or host.endswith(f".{dominio}") for dominio in _HOSTS_CDN_PERMITIDOS)


_ENDPOINT = "https://i.instagram.com/api/v1/users/web_profile_info/"
# Id de aplicação público que o próprio site instagram.com usa para montar a
# página de perfil no navegador — não é credencial nossa, não é segredo.
_APP_ID = "936619743392459"
_TIMEOUT = 6.0
_USER_AGENT = (
    "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 "
    "(KHTML, like Gecko) Chrome/124.0 Safari/537.36"
)

_EXTENSAO_POR_MIME = {"image/jpeg": ".jpg", "image/png": ".png", "image/webp": ".webp"}


def _baixar_foto_publica(handle: str) -> bytes | None:
    """Best-effort: devolve os bytes da foto pública do handle informado, ou
    `None` em qualquer situação que não seja "perfil público existente com
    foto" (inexistente, privado, erro, timeout, formato inesperado)."""
    handle = (handle or "").strip().lstrip("@")
    if not handle:
        return None
    try:
        resposta = httpx.get(
            _ENDPOINT,
            params={"username": handle},
            headers={"User-Agent": _USER_AGENT, "x-ig-app-id": _APP_ID, "Accept": "application/json"},
            timeout=_TIMEOUT,
            follow_redirects=True,
        )
        if resposta.status_code != 200:
            return None
        dados = resposta.json()
        usuario = ((dados or {}).get("data") or {}).get("user") or {}
        if not usuario or usuario.get("is_private"):
            return None
        url_foto = usuario.get("profile_pic_url_hd") or usuario.get("profile_pic_url")
        if not url_foto or not _host_de_cdn_confiavel(url_foto):
            return None

        imagem = httpx.get(url_foto, headers={"User-Agent": _USER_AGENT}, timeout=_TIMEOUT, follow_redirects=False)
        if imagem.status_code != 200 or not imagem.content:
            return None
        return imagem.content
    except Exception:
        log.warning(
            "Falha ao buscar foto pública do Instagram (best-effort, sem impacto no cadastro)",
            exc_info=True,
        )
        return None


def buscar_e_salvar_foto(user_id: int, handle: str) -> None:
    """Chamado via `BackgroundTasks` a partir do cadastro. Abre a própria
    sessão de banco — a sessão de `Depends(get_db)` da rota que agendou esta
    chamada já fechou quando este código roda (mesmo cuidado já documentado
    neste projeto para toda função disparada em segundo plano)."""
    from app.core.db import SessionLocal
    from app.models.user import User

    conteudo = _baixar_foto_publica(handle)
    if conteudo is None:
        return

    try:
        mime = validate_file(conteudo, f"{handle}.jpg", "image")
    except UploadRejected:
        return

    # Grava dentro do MESMO diretório que já serve `/fotos/*` no Caddy —
    # evita infraestrutura nova (rota/volume) só para isto. O prefixo "ig-"
    # (em vez de "{user_id}-" como a foto enviada pelo próprio médico) é o
    # que impede a limpeza de foto de perfil (`_remover_arquivos_antigos`,
    # em app/api/auth.py, que apaga por `glob(f"{user_id}-*")`) de remover
    # esta foto por engano, e vice-versa — os dois arquivos coexistem sem
    # se enxergar.
    diretorio = Path(settings.uploads_dir) / "fotos"
    nome = f"ig-{user_id}-{secrets.token_hex(8)}{_EXTENSAO_POR_MIME.get(mime, '.jpg')}"
    try:
        atomic_write_bytes(diretorio, nome, conteudo, mode=0o644)
    except OSError:
        log.warning("Não foi possível gravar a foto do Instagram no disco (user_id=%s)", user_id)
        return

    db = SessionLocal()
    try:
        user = db.get(User, user_id)
        if user is None:
            return
        url_antiga = user.instagram_photo_url
        user.instagram_photo_url = f"/fotos/{nome}"
        db.commit()
    finally:
        db.close()

    if url_antiga and url_antiga.startswith("/fotos/ig-"):
        # Handle trocado, ou nova tentativa — remove o arquivo anterior para
        # não acumular lixo no volume compartilhado.
        try:
            (diretorio / url_antiga.rsplit("/", 1)[-1]).unlink(missing_ok=True)
        except OSError:
            pass
