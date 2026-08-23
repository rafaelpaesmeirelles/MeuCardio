"""Matriz de onboarding por tipo de conta criada diretamente pelo admin
(13/08/2026, pedido do Rafael) — três tipos claramente selecionáveis em
`POST /api/admin/users` (`tipo_acesso`), cada um com regra própria de
cobrança e de KYC:

- normal: fluxo de cobrança/Stripe normal, KYC normal (documento
  profissional + documento pessoal + selfie, aprovação manual do admin
  quando a checagem automática de conselho não confirma).
- convidado: nunca cobra (`User.convidado`), KYC COMPLETO (documento
  profissional + documento pessoal + selfie), aprovação SEMPRE automática
  assim que a submissão é tecnicamente válida — nunca depende de revisão
  do admin, nunca aparece na fila.
- investidor: conta global de demonstração somente leitura, sem perfil,
  CPF/nascimento, dados profissionais, documentos, selfie ou KYC; senha fixa
  CorVIAOS; vai diretamente ao tour e nunca executa operações persistentes.

Reutiliza User.convidado/User.investidor e `app/services/entitlement.py`
(fonte central de entitlement) já existentes — nenhum mecanismo de
cobrança novo. Backend tocado: `app/api/admin.py` (NovoUsuario.tipo_acesso,
criar_usuario), `app/api/auth.py` (_kyc_required, _perfil_completo,
atualizar_me com preenchimento único de CPF/data de nascimento),
`app/api/kyc.py` (documento profissional opcional na assinatura HTTP),
`app/services/kyc/verificacao.py` (submeter, listar_pendentes).
"""
import io
from unittest.mock import patch

import pytest
from PIL import Image

from app.models.audit import AuditLog
from app.models.kyc import KycVerification
from app.models.kyc_waiver import KycRequirementWaiver
from app.models.subscription import Subscription
from app.models.user import User


@pytest.fixture(autouse=True)
def _diretorio_kyc(tmp_path, monkeypatch):
    from app.core.config import settings

    monkeypatch.setattr(settings, "kyc_dir", str(tmp_path))


def _headers(token: str) -> dict[str, str]:
    return {"Authorization": f"Bearer {token}"}


def _jpeg(cor: tuple[int, int, int]) -> bytes:
    buf = io.BytesIO()
    Image.new("RGB", (10, 10), color=cor).save(buf, format="JPEG")
    return buf.getvalue()


def _arquivos_completos(**overrides):
    base = {
        "doc_profissional_frente": ("frente.jpg", _jpeg((255, 0, 0)), "image/jpeg"),
        "doc_profissional_verso": ("verso.jpg", _jpeg((0, 255, 0)), "image/jpeg"),
        "selfie": ("selfie.jpg", _jpeg((0, 0, 255)), "image/jpeg"),
        "doc_pessoal_frente": ("id-frente.jpg", _jpeg((255, 255, 0)), "image/jpeg"),
        "doc_pessoal_verso": ("id-verso.jpg", _jpeg((255, 0, 255)), "image/jpeg"),
    }
    base.update(overrides)
    return base


@pytest.fixture
def admin(criar_usuario):
    user, token = criar_usuario(email="admin-onboarding@teste.local", role="admin")
    return user, token


CAMPOS_MINIMOS = {
    "email": "novo@teste.local", "full_name": "Novo Titular da Silva",
    "role": "medico", "password": "senha12345",
}


# --------------------------------------------------------------------- CRIAÇÃO --


class TestCriacaoDiretaPeloAdmin:
    def test_tipo_acesso_normal_nao_marca_convidado_nem_investidor(self, client, db, admin):
        _, token_admin = admin
        resp = client.post("/api/admin/users", json={**CAMPOS_MINIMOS, "tipo_acesso": "normal"},
                            headers=_headers(token_admin))
        assert resp.status_code == 201, resp.text
        assert resp.json()["convidado"] is False
        assert resp.json()["investidor"] is False

        criado = db.query(User).filter(User.email == "novo@teste.local").first()
        assert criado.convidado is False
        assert criado.investidor is False

    def test_tipo_acesso_omitido_equivale_a_normal(self, client, db, admin):
        """`tipo_acesso` tem default "normal" — não altera o fluxo de quem
        já criava conta sem esse campo (compatibilidade com o formulário
        antigo, que nunca soube desse campo)."""
        _, token_admin = admin
        corpo = dict(CAMPOS_MINIMOS)
        resp = client.post("/api/admin/users", json=corpo, headers=_headers(token_admin))
        assert resp.status_code == 201, resp.text
        criado = db.query(User).filter(User.email == "novo@teste.local").first()
        assert criado.convidado is False
        assert criado.investidor is False

    def test_tipo_acesso_convidado_marca_convidado_e_so_convidado(self, client, db, admin):
        _, token_admin = admin
        resp = client.post("/api/admin/users", json={**CAMPOS_MINIMOS, "tipo_acesso": "convidado"},
                            headers=_headers(token_admin))
        assert resp.status_code == 201, resp.text
        criado = db.query(User).filter(User.email == "novo@teste.local").first()
        assert criado.convidado is True
        assert criado.investidor is False
        # A conta nasce precisando completar o perfil — admin não colhe
        # CPF/data de nascimento na criação direta.
        assert criado.profile_completion_required is True

    def test_tipo_acesso_investidor_marca_investidor_e_so_investidor(self, client, db, admin):
        _, token_admin = admin
        resp = client.post("/api/admin/users", json={**CAMPOS_MINIMOS, "tipo_acesso": "investidor"},
                            headers=_headers(token_admin))
        assert resp.status_code == 201, resp.text
        criado = db.query(User).filter(User.email == "novo@teste.local").first()
        assert criado.convidado is False
        assert criado.investidor is True
        assert criado.profile_completion_required is False
        assert criado.status == "aprovado"
        assert criado.onboarding_visto is False

    def test_tipo_acesso_invalido_e_422_nunca_cria_combinacao_invalida(self, client, db, admin):
        """Não existe forma de mandar convidado=true + investidor=true — um
        único campo de três valores garante isso por construção, e qualquer
        quarto valor é rejeitado antes de tocar o banco."""
        _, token_admin = admin
        resp = client.post("/api/admin/users", json={**CAMPOS_MINIMOS, "tipo_acesso": "convidado-e-investidor"},
                            headers=_headers(token_admin))
        assert resp.status_code == 422
        assert db.query(User).filter(User.email == "novo@teste.local").first() is None


# ------------------------------------------------------------------------ STRIPE --


class TestNuncaChamaStripe:
    def test_convidado_criado_pelo_admin_checkout_nao_chama_stripe(self, client, db, admin):
        _, token_admin = admin
        client.post("/api/admin/users", json={**CAMPOS_MINIMOS, "tipo_acesso": "convidado"},
                    headers=_headers(token_admin))
        criado = db.query(User).filter(User.email == "novo@teste.local").first()
        token_criado = _token_para(criado)

        with patch("app.api.billing.stripe.checkout.Session.create") as criar_sessao, \
             patch("app.api.billing.stripe.Customer.create") as criar_cliente:
            resp = client.post("/api/billing/checkout?plano=basico", headers=_headers(token_criado))
            criar_sessao.assert_not_called()
            criar_cliente.assert_not_called()
        assert resp.status_code == 200
        assert resp.json()["checkout_url"] is None

    def test_investidor_criado_pelo_admin_checkout_nao_chama_stripe(self, client, db, admin):
        _, token_admin = admin
        client.post("/api/admin/users", json={**CAMPOS_MINIMOS, "tipo_acesso": "investidor"},
                    headers=_headers(token_admin))
        criado = db.query(User).filter(User.email == "novo@teste.local").first()
        token_criado = _token_para(criado)

        with patch("app.api.billing.stripe.checkout.Session.create") as criar_sessao, \
             patch("app.api.billing.stripe.Customer.create") as criar_cliente:
            resp = client.post("/api/billing/checkout?plano=completo", headers=_headers(token_criado))
            criar_sessao.assert_not_called()
            criar_cliente.assert_not_called()
        assert resp.status_code == 403
        assert db.query(Subscription).filter(Subscription.user_id == criado.id).first() is None

    def test_normal_criado_pelo_admin_continua_chamando_stripe(self, client, db, admin):
        _, token_admin = admin
        client.post("/api/admin/users", json={**CAMPOS_MINIMOS, "tipo_acesso": "normal"},
                    headers=_headers(token_admin))
        criado = db.query(User).filter(User.email == "novo@teste.local").first()
        token_criado = _token_para(criado)

        with patch("app.api.billing.stripe.checkout.Session.create") as criar_sessao, \
             patch("app.api.billing.stripe.Customer.create") as criar_cliente:
            criar_cliente.return_value = {"id": "cus_teste_normal"}
            criar_sessao.return_value = {"url": "https://checkout.stripe.com/fake"}
            resp = client.post("/api/billing/checkout?plano=basico", headers=_headers(token_criado))
        assert resp.status_code == 200
        assert resp.json()["checkout_url"] == "https://checkout.stripe.com/fake"
        criar_sessao.assert_called_once()


def _token_para(user: User) -> str:
    from app.core.security import create_access_token

    return create_access_token(user.email, scope="app")


# --------------------------------------------------------------------------- KYC --


class TestKycConvidado:
    def test_convidado_exige_documentacao_profissional(self, client, db, admin):
        _, token_admin = admin
        client.post("/api/admin/users", json={**CAMPOS_MINIMOS, "tipo_acesso": "convidado"},
                    headers=_headers(token_admin))
        criado = db.query(User).filter(User.email == "novo@teste.local").first()
        token_criado = _token_para(criado)

        arquivos = _arquivos_completos()
        del arquivos["doc_profissional_frente"]
        resp = client.post("/api/kyc/submeter", files=arquivos, headers=_headers(token_criado))
        assert resp.status_code == 422

    def test_convidado_submissao_completa_aprova_automaticamente_sem_admin(self, client, db, admin):
        _, token_admin = admin
        client.post("/api/admin/users", json={**CAMPOS_MINIMOS, "tipo_acesso": "convidado"},
                    headers=_headers(token_admin))
        criado = db.query(User).filter(User.email == "novo@teste.local").first()
        token_criado = _token_para(criado)

        resp = client.post("/api/kyc/submeter", files=_arquivos_completos(), headers=_headers(token_criado))
        assert resp.status_code == 201, resp.text
        corpo = resp.json()
        assert corpo["status"] == "aprovado"
        assert corpo["liberado"] is True

        registro = db.query(KycVerification).filter(KycVerification.owner_id == criado.id).first()
        assert registro.aprovado_por is None
        assert registro.status == "aprovado"

    def test_socio_tem_acesso_integral_kyc_somente_selfie_e_depois_tour(self, client, db, criar_usuario):
        socio, token = criar_usuario(email="socio-onboarding@teste.local", role="admin")
        socio.convidado = True
        socio.investidor = False
        socio.profile_completion_required = False
        socio.onboarding_visto = False
        db.add(KycRequirementWaiver(
            owner_id=socio.id,
            professional_front=True,
            professional_back=True,
            personal_front=True,
            personal_back=True,
            personal_digital=True,
            selfie=False,
        ))
        db.commit()

        antes = client.get("/api/auth/me", headers=_headers(token))
        assert antes.status_code == 200
        assert antes.json()["socio"] is True
        assert antes.json()["kyc_required"] is True
        assert antes.json()["onboarding_pendente"] is False

        somente_selfie = {
            "selfie": ("selfie.jpg", _jpeg((30, 60, 90)), "image/jpeg"),
        }
        submissao = client.post("/api/kyc/submeter", files=somente_selfie, headers=_headers(token))
        assert submissao.status_code == 201, submissao.text
        assert submissao.json()["status"] == "aprovado"
        assert submissao.json()["liberado"] is True

        depois = client.get("/api/auth/me", headers=_headers(token)).json()
        assert depois["kyc_required"] is False
        assert depois["onboarding_pendente"] is True

    def test_convidado_nao_aparece_na_fila_de_kyc_pendente(self, client, db, admin):
        _, token_admin = admin
        client.post("/api/admin/users", json={**CAMPOS_MINIMOS, "tipo_acesso": "convidado"},
                    headers=_headers(token_admin))
        criado = db.query(User).filter(User.email == "novo@teste.local").first()
        token_criado = _token_para(criado)
        client.post("/api/kyc/submeter", files=_arquivos_completos(), headers=_headers(token_criado))

        resp = client.get("/api/admin/kyc", headers=_headers(token_admin))
        assert resp.status_code == 200
        assert criado.id not in {item["user_id"] for item in resp.json()}

    def test_convidado_gera_auditlog_de_aprovacao_automatica(self, client, db, admin):
        _, token_admin = admin
        client.post("/api/admin/users", json={**CAMPOS_MINIMOS, "tipo_acesso": "convidado"},
                    headers=_headers(token_admin))
        criado = db.query(User).filter(User.email == "novo@teste.local").first()
        token_criado = _token_para(criado)
        client.post("/api/kyc/submeter", files=_arquivos_completos(), headers=_headers(token_criado))

        registros = db.query(AuditLog).filter(AuditLog.action == "aprovacao_automatica_convidado").all()
        assert len(registros) == 1
        assert registros[0].user_id == criado.id

    def test_convidado_nunca_passa_por_admin_kyc_aprovar(self, client, db, admin):
        """A aprovação nasce definitiva na própria submissão — o endpoint
        POST /admin/kyc/{id}/aprovar nunca precisa ser chamado."""
        _, token_admin = admin
        client.post("/api/admin/users", json={**CAMPOS_MINIMOS, "tipo_acesso": "convidado"},
                    headers=_headers(token_admin))
        criado = db.query(User).filter(User.email == "novo@teste.local").first()
        token_criado = _token_para(criado)
        client.post("/api/kyc/submeter", files=_arquivos_completos(), headers=_headers(token_criado))

        registro = db.query(KycVerification).filter(KycVerification.owner_id == criado.id).first()
        assert registro.status == "aprovado"
        assert not db.query(AuditLog).filter(AuditLog.action == "kyc_aprovado").count()


class TestKycInvestidor:
    def _criar(self, client, db, admin):
        _, token_admin = admin
        resp = client.post(
            "/api/admin/users",
            json={**CAMPOS_MINIMOS, "tipo_acesso": "investidor"},
            headers=_headers(token_admin),
        )
        assert resp.status_code == 201, resp.text
        criado = db.query(User).filter(User.email == "novo@teste.local").first()
        return criado, _token_para(criado), token_admin

    def test_investidor_e_isento_de_kyc_e_vai_direto_ao_tour(self, client, db, admin):
        criado, token_criado, _ = self._criar(client, db, admin)

        me = client.get("/api/auth/me", headers=_headers(token_criado))
        assert me.status_code == 200
        corpo = me.json()
        assert corpo["profile_completion_required"] is False
        assert corpo["kyc_required"] is False
        assert corpo["onboarding_pendente"] is True
        assert db.query(KycVerification).filter(KycVerification.owner_id == criado.id).first() is None

    def test_investidor_nao_pode_submeter_kyc_mesmo_com_arquivos_completos(self, client, db, admin):
        criado, token_criado, _ = self._criar(client, db, admin)

        resp = client.post(
            "/api/kyc/submeter",
            files=_arquivos_completos(),
            headers=_headers(token_criado),
        )
        assert resp.status_code == 403
        assert db.query(KycVerification).filter(KycVerification.owner_id == criado.id).first() is None

    def test_investidor_nao_pode_submeter_selfie_ou_documento_parcial(self, client, db, admin):
        criado, token_criado, _ = self._criar(client, db, admin)
        resp = client.post(
            "/api/kyc/submeter",
            files={"selfie": ("selfie.jpg", _jpeg((0, 0, 255)), "image/jpeg")},
            headers=_headers(token_criado),
        )
        assert resp.status_code == 403
        assert db.query(KycVerification).filter(KycVerification.owner_id == criado.id).first() is None

    def test_investidor_nunca_aparece_na_fila_de_kyc(self, client, db, admin):
        criado, _, token_admin = self._criar(client, db, admin)
        fila = client.get("/api/admin/kyc", headers=_headers(token_admin))
        assert fila.status_code == 200
        assert criado.id not in {item["user_id"] for item in fila.json()}

    def test_investidor_nao_gera_audit_de_aprovacao_automatica_kyc(self, client, db, admin):
        criado, token_criado, _ = self._criar(client, db, admin)
        client.post("/api/kyc/submeter", files=_arquivos_completos(), headers=_headers(token_criado))

        assert db.query(AuditLog).filter(
            AuditLog.user_id == criado.id,
            AuditLog.action.in_(("aprovacao_automatica_investidor", "kyc_aprovado")),
        ).count() == 0


def _dar_assinatura_ativa(db, user_id: int) -> None:
    """KYC só se aplica a quem já tem acesso ao produto (`_kyc_required`
    consulta `tem_acesso_ao_produto`) — assinante "normal" precisa de uma
    Subscription ativa antes de `/api/kyc/submeter` responder qualquer coisa
    além de 402. Convidado tem acesso pelo próprio flag; Investidor também
    tem entitlement de leitura, mas mutações permanecem barradas globalmente."""
    db.add(Subscription(user_id=user_id, kind="meucardio", plano="basico", status="ativo"))
    db.commit()


class TestNormalPreservaFluxoAtual:
    def test_normal_continua_exigindo_documento_profissional(self, client, db, admin):
        _, token_admin = admin
        client.post("/api/admin/users", json={**CAMPOS_MINIMOS, "tipo_acesso": "normal"},
                    headers=_headers(token_admin))
        criado = db.query(User).filter(User.email == "novo@teste.local").first()
        _dar_assinatura_ativa(db, criado.id)
        token_criado = _token_para(criado)

        arquivos = _arquivos_completos()
        del arquivos["doc_profissional_frente"]
        resp = client.post("/api/kyc/submeter", files=arquivos, headers=_headers(token_criado))
        assert resp.status_code == 422

    def test_normal_sem_credencial_de_conselho_configurada_fica_aguardando_revisao(self, client, db, admin):
        """Sem checagem automática confirmada, assinante normal continua
        indo para a fila do admin — comportamento intacto, ao contrário de
        convidado, que é aprovado de qualquer forma."""
        _, token_admin = admin
        client.post("/api/admin/users", json={**CAMPOS_MINIMOS, "tipo_acesso": "normal",
                                               "council_name": "CRM", "council_number": "123456",
                                               "council_state": "SP"},
                    headers=_headers(token_admin))
        criado = db.query(User).filter(User.email == "novo@teste.local").first()
        _dar_assinatura_ativa(db, criado.id)
        token_criado = _token_para(criado)

        resp = client.post("/api/kyc/submeter", files=_arquivos_completos(), headers=_headers(token_criado))
        assert resp.status_code == 201, resp.text
        assert resp.json()["status"] == "aguardando_revisao"

        fila = client.get("/api/admin/kyc", headers=_headers(token_admin))
        assert criado.id in {item["user_id"] for item in fila.json()}

    def test_normal_admin_criado_sem_cpf_nem_nascimento_nao_e_bloqueado_por_isso(self, db, admin):
        """CPF/data de nascimento NUNCA foram exigência do assinante normal
        — não é a regra nova pedida para ele, só para convidado/investidor.
        Confere diretamente `_perfil_completo` (a mesma função que decide
        `profile_completion_required`), sem depender do valor default do
        formulário do admin."""
        from app.api.auth import _perfil_completo

        _, token_admin = admin
        u = User(
            email="normal.sem.cpf@teste.local", full_name="Normal Sem CPF",
            role="medico", password_hash="x", is_active=True,
            profession="Cardiologista", council_name="CRM", council_number="1",
            council_state="SP",
        )
        assert u.cpf is None
        assert u.birth_date is None
        assert _perfil_completo(u) is True


# ---------------------------------------------------------- _PERFIL_COMPLETO --


class TestPerfilCompletoPorTipoDeConta:
    def test_investidor_e_considerado_completo_sem_dados_pessoais_ou_profissionais(self):
        from app.api.auth import _perfil_completo

        u = User(
            email="i@teste.local", full_name="Investidor Demonstração", role="leitor",
            password_hash="x", investidor=True,
        )
        assert _perfil_completo(u) is True

    def test_investidor_nao_reabre_gate_mesmo_com_dados_legados_parciais(self):
        from app.api.auth import _perfil_completo
        from datetime import date

        u = User(
            email="i2@teste.local", full_name="Investidor Legado", role="medico",
            password_hash="x", investidor=True, birth_date=date(1990, 1, 1),
        )
        assert _perfil_completo(u) is True

    def test_convidado_precisa_de_pessoal_e_profissional(self):
        from app.api.auth import _perfil_completo
        from datetime import date

        base = dict(
            email="c@teste.local", full_name="Convidado Completo", role="medico",
            password_hash="x", convidado=True, cpf="12345678900", birth_date=date(1990, 1, 1),
        )
        sem_profissional = User(**base)
        assert _perfil_completo(sem_profissional) is False  # falta profissão/conselho

        completo = User(
            **base, profession="Cardiologista", council_name="CRM",
            council_number="123456", council_state="SP",
        )
        assert _perfil_completo(completo) is True

    def test_convidado_com_profissional_mas_sem_pessoal_nao_esta_completo(self):
        from app.api.auth import _perfil_completo

        u = User(
            email="c2@teste.local", full_name="Convidado Sem CPF", role="medico",
            password_hash="x", convidado=True,
            profession="Cardiologista", council_name="CRM", council_number="123456", council_state="SP",
        )
        assert _perfil_completo(u) is False  # falta cpf/data de nascimento


# ------------------------------------------------------- CPF/NASCIMENTO ÚNICO --


class TestPreenchimentoUnicoCpfNascimento:
    def test_preenche_cpf_quando_ausente(self, client, db, admin):
        _, token_admin = admin
        client.post("/api/admin/users", json={**CAMPOS_MINIMOS, "tipo_acesso": "convidado"},
                    headers=_headers(token_admin))
        criado = db.query(User).filter(User.email == "novo@teste.local").first()
        token_criado = _token_para(criado)

        resp = client.patch("/api/auth/me", json={"full_name": "Novo Titular da Silva", "cpf": "39053344705"},
                             headers=_headers(token_criado))
        assert resp.status_code == 200, resp.text
        db.refresh(criado)
        assert criado.cpf == "39053344705"

    def test_rejeita_mudar_cpf_ja_preenchido(self, client, db, admin):
        _, token_admin = admin
        client.post("/api/admin/users", json={**CAMPOS_MINIMOS, "tipo_acesso": "convidado"},
                    headers=_headers(token_admin))
        criado = db.query(User).filter(User.email == "novo@teste.local").first()
        token_criado = _token_para(criado)
        client.patch("/api/auth/me", json={"full_name": "Novo Titular da Silva", "cpf": "39053344705"},
                     headers=_headers(token_criado))

        resp = client.patch("/api/auth/me", json={"full_name": "Novo Titular da Silva", "cpf": "11144477735"},
                             headers=_headers(token_criado))
        assert resp.status_code == 422
        db.refresh(criado)
        assert criado.cpf == "39053344705"

    def test_reenviar_o_mesmo_cpf_ja_preenchido_nao_e_erro(self, client, db, admin):
        _, token_admin = admin
        client.post("/api/admin/users", json={**CAMPOS_MINIMOS, "tipo_acesso": "convidado"},
                    headers=_headers(token_admin))
        criado = db.query(User).filter(User.email == "novo@teste.local").first()
        token_criado = _token_para(criado)
        client.patch("/api/auth/me", json={"full_name": "Novo Titular da Silva", "cpf": "39053344705"},
                     headers=_headers(token_criado))

        resp = client.patch("/api/auth/me", json={"full_name": "Novo Titular da Silva", "cpf": "39053344705"},
                             headers=_headers(token_criado))
        assert resp.status_code == 200

    def test_cpf_invalido_e_422(self, client, db, admin):
        _, token_admin = admin
        client.post("/api/admin/users", json={**CAMPOS_MINIMOS, "tipo_acesso": "convidado"},
                    headers=_headers(token_admin))
        criado = db.query(User).filter(User.email == "novo@teste.local").first()
        token_criado = _token_para(criado)

        resp = client.patch("/api/auth/me", json={"full_name": "Novo Titular da Silva", "cpf": "00000000000"},
                             headers=_headers(token_criado))
        assert resp.status_code == 422

    def test_data_de_nascimento_futura_e_422(self, client, db, admin):
        _, token_admin = admin
        client.post("/api/admin/users", json={**CAMPOS_MINIMOS, "tipo_acesso": "convidado"},
                    headers=_headers(token_admin))
        criado = db.query(User).filter(User.email == "novo@teste.local").first()
        token_criado = _token_para(criado)

        resp = client.patch(
            "/api/auth/me", json={"full_name": "Novo Titular da Silva", "birth_date": "2999-01-01"},
            headers=_headers(token_criado),
        )
        assert resp.status_code == 422
