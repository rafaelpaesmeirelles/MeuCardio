"""Instagram opcional no cadastro (tarefa #43, 08/08/2026).

Cobre: o campo é opcional e normalizado em `POST /auth/solicitar-acesso`; a
busca best-effort da foto pública (`app/services/instagram_profile.py`)
nunca sai para a rede de verdade nos testes (monkeypatch), e cobre os
caminhos de sucesso, perfil privado/inexistente e falha de rede — em nenhum
deles o cadastro é afetado.
"""
from app.models.user import User
from app.services import instagram_profile


def _payload(**overrides):
    base = dict(
        full_name="Ana Paula Souza", birth_date="1985-03-20", cpf="111.444.777-35",
        profession="Médica", council_name="CRM", council_number="55555", council_state="SP",
        email="ana@teste.local", password="senha-forte-123",
    )
    base.update(overrides)
    return base


def test_instagram_handle_e_opcional(client, db):
    resp = client.post("/api/auth/solicitar-acesso", json=_payload())
    assert resp.status_code == 201, resp.text
    user = db.query(User).filter(User.email == "ana@teste.local").first()
    assert user.instagram_handle is None
    assert user.instagram_photo_url is None


def test_instagram_handle_normaliza_arroba_e_espacos(client, db, monkeypatch):
    monkeypatch.setattr(instagram_profile, "_baixar_foto_publica", lambda handle: None)
    resp = client.post("/api/auth/solicitar-acesso", json=_payload(
        instagram_handle="  @dra.ana_paula  ", email="ana2@teste.local",
    ))
    assert resp.status_code == 201, resp.text
    user = db.query(User).filter(User.email == "ana2@teste.local").first()
    assert user.instagram_handle == "dra.ana_paula"


def test_instagram_handle_com_caractere_invalido_e_rejeitado(client):
    resp = client.post("/api/auth/solicitar-acesso", json=_payload(
        instagram_handle="usuario com espaço", email="ana3@teste.local",
    ))
    assert resp.status_code == 422


def test_instagram_handle_muito_longo_e_rejeitado(client):
    resp = client.post("/api/auth/solicitar-acesso", json=_payload(
        instagram_handle="a" * 31, email="ana4@teste.local",
    ))
    assert resp.status_code == 422


def test_cadastro_com_handle_busca_foto_em_segundo_plano_e_salva(client, db, monkeypatch, tmp_path):
    """TestClient roda BackgroundTasks de forma síncrona antes de devolver a
    resposta — por isso o monkeypatch abaixo troca só a chamada de rede
    (`_baixar_foto_publica`), nunca `buscar_e_salvar_foto` em si, garantindo
    que o resto do pipeline real (validação de imagem, escrita em disco,
    persistência no banco) é exercitado de verdade."""
    monkeypatch.setattr(instagram_profile.settings, "uploads_dir", str(tmp_path))

    pixel_jpeg = bytes.fromhex(
        "ffd8ffe000104a46494600010100000100010000ffdb004300030202020202"
        "03020202030303030406040404040408060605070907080808070808090b0e"
        "0c090a0d0a0808090c110b0d0e0f0f10100a0c1214121013111211ffc9000b"
        "080001000101011100ffcc00060010100005ffda0008010100003f00d2cff9"
        "00ffd9"
    )
    monkeypatch.setattr(instagram_profile, "_baixar_foto_publica", lambda handle: pixel_jpeg)

    resp = client.post("/api/auth/solicitar-acesso", json=_payload(
        instagram_handle="dra.ana", email="ana5@teste.local",
    ))
    assert resp.status_code == 201, resp.text

    user = db.query(User).filter(User.email == "ana5@teste.local").first()
    assert user.instagram_handle == "dra.ana"
    assert user.instagram_photo_url is not None
    assert user.instagram_photo_url.startswith(f"/fotos/ig-{user.id}-")

    caminho_arquivo = tmp_path / "fotos" / user.instagram_photo_url.rsplit("/", 1)[-1]
    assert caminho_arquivo.exists()


def test_cadastro_com_handle_e_busca_falhando_nao_afeta_cadastro(client, db, monkeypatch, tmp_path):
    """Perfil privado, inexistente, endpoint fora do ar — qualquer falha da
    busca best-effort não pode derrubar o cadastro nem deixar `photo_url`
    inconsistente."""
    monkeypatch.setattr(instagram_profile.settings, "uploads_dir", str(tmp_path))
    monkeypatch.setattr(instagram_profile, "_baixar_foto_publica", lambda handle: None)

    resp = client.post("/api/auth/solicitar-acesso", json=_payload(
        instagram_handle="perfil_privado_ou_inexistente", email="ana6@teste.local",
    ))
    assert resp.status_code == 201, resp.text

    user = db.query(User).filter(User.email == "ana6@teste.local").first()
    assert user.instagram_handle == "perfil_privado_ou_inexistente"
    assert user.instagram_photo_url is None


def test_baixar_foto_publica_devolve_none_em_erro_de_rede(monkeypatch):
    """`_baixar_foto_publica` de verdade (não mockada) precisa engolir
    qualquer exceção de rede — é o contrato que faz o resto do pipeline
    poder tratar 'sem foto' e 'erro de rede' da mesma forma."""
    import httpx

    def _explode(*args, **kwargs):
        raise httpx.ConnectError("simulado")

    monkeypatch.setattr(instagram_profile.httpx, "get", _explode)
    assert instagram_profile._baixar_foto_publica("qualquer_handle") is None


def test_baixar_foto_publica_ignora_perfil_privado(monkeypatch):
    class _RespostaFalsa:
        status_code = 200

        def json(self):
            return {"data": {"user": {"is_private": True, "profile_pic_url_hd": "https://x/y.jpg"}}}

    monkeypatch.setattr(instagram_profile.httpx, "get", lambda *a, **k: _RespostaFalsa())
    assert instagram_profile._baixar_foto_publica("perfil_privado") is None


def test_host_de_cdn_confiavel_aceita_dominios_da_meta():
    assert instagram_profile._host_de_cdn_confiavel(
        "https://scontent-gru2-1.cdninstagram.com/v/foto.jpg"
    )
    assert instagram_profile._host_de_cdn_confiavel("https://instagram.fbcdn.net/foto.jpg")
    assert instagram_profile._host_de_cdn_confiavel("https://cdninstagram.com/foto.jpg")


def test_host_de_cdn_confiavel_rejeita_dominio_arbitrario_ou_nao_https():
    """Achado de auditoria (issue #52, subfase 8, defesa em profundidade):
    `url_foto` vem do corpo da resposta do Instagram, não de um valor fixo
    nosso — sem esta checagem, uma resposta inesperada (endpoint mudado,
    comprometido) faria o servidor buscar QUALQUER destino que a resposta
    contivesse."""
    assert not instagram_profile._host_de_cdn_confiavel("https://cdninstagram.com.attacker.test/x.jpg")
    assert not instagram_profile._host_de_cdn_confiavel("https://169.254.169.254/latest/meta-data/")
    assert not instagram_profile._host_de_cdn_confiavel("http://cdninstagram.com/x.jpg")  # http, não https
    assert not instagram_profile._host_de_cdn_confiavel("not-a-url")
    assert not instagram_profile._host_de_cdn_confiavel("")


def test_baixar_foto_publica_nao_busca_url_de_host_nao_confiavel(monkeypatch):
    chamadas = []

    class _RespostaPerfil:
        status_code = 200

        def json(self):
            return {"data": {"user": {
                "is_private": False,
                "profile_pic_url_hd": "https://evil.example/x.jpg",
            }}}

    def _get(url, *args, **kwargs):
        chamadas.append(url)
        return _RespostaPerfil()

    monkeypatch.setattr(instagram_profile.httpx, "get", _get)
    assert instagram_profile._baixar_foto_publica("handle_qualquer") is None
    # Só a chamada ao endpoint fixo do Instagram — a segunda chamada (buscar
    # a própria imagem) nunca acontece contra um host não confiável.
    assert chamadas == [instagram_profile._ENDPOINT]


def test_baixar_foto_publica_busca_imagem_de_host_confiavel(monkeypatch):
    chamadas = []

    class _RespostaPerfil:
        status_code = 200

        def json(self):
            return {"data": {"user": {
                "is_private": False,
                "profile_pic_url_hd": "https://scontent.cdninstagram.com/v/foto.jpg",
            }}}

    class _RespostaImagem:
        status_code = 200
        content = b"conteudo-da-imagem"

    def _get(url, *args, **kwargs):
        chamadas.append(url)
        return _RespostaImagem() if "cdninstagram.com" in url else _RespostaPerfil()

    monkeypatch.setattr(instagram_profile.httpx, "get", _get)
    assert instagram_profile._baixar_foto_publica("handle_qualquer") == b"conteudo-da-imagem"
    assert chamadas == [instagram_profile._ENDPOINT, "https://scontent.cdninstagram.com/v/foto.jpg"]


def test_perfil_expoe_instagram_handle_e_foto(client, db):
    resp = client.post("/api/auth/solicitar-acesso", json=_payload(email="ana7@teste.local"))
    assert resp.status_code == 201

    from app.core.security import create_access_token
    user = db.query(User).filter(User.email == "ana7@teste.local").first()
    user.status = "aprovado"
    user.is_active = True
    db.commit()
    token = create_access_token(user.email)

    resp = client.get("/api/auth/me", headers={"Authorization": f"Bearer {token}"})
    assert resp.status_code == 200
    corpo = resp.json()
    assert "instagram_handle" in corpo
    assert "instagram_photo_url" in corpo
