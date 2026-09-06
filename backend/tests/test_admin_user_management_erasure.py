from types import SimpleNamespace

from app.api.admin_user_management import _anonimizar_usuario_excluido


def _target():
    return SimpleNamespace(
        id=42, email="pessoa@example.com", full_name="Pessoa Real", password_hash="hash-antigo",
        role="medico", is_active=True, status="aprovado", sessions_valid_after=None, active_session_id="sessao",
        convidado=True, investidor=False, profile_completion_required=True, boas_vindas_pendente=True, onboarding_visto=False,
        birth_date="1980-01-01", cpf="123", profession="Médico", council_name="CRM", council_number="1", council_state="SP",
        council_name_other=None, council_state_other=None, specialty="Cardiologia", rqe="1", professional_title="Dr.",
        workplace_name="Clínica", workplace_department="Cardio", workplace_role="Médico", workplace_notes="nota",
        photo_url="/foto", crm="CRM1", document_logo_url="/logo", home_street="Rua", home_number="1", home_complement=None,
        home_neighborhood="Bairro", home_city="Cidade", home_state="SP", home_zip="00000", practice_street="Rua",
        practice_number="2", practice_complement=None, practice_neighborhood="B", practice_city="C", practice_state="SP",
        practice_zip="000", practice_phone="1", reviewed_by=1, reviewed_at="x", rejection_note="x",
        convidado_plano_preferido="completo", last_seen_at="x", assinatura_metodo_preferido="a1",
        ia_ferramentas_consent_em="x", ia_ferramentas_consent_versao="v1", email_conta_padrao_envio="corvia",
        instagram_handle="pessoa", instagram_photo_url="x", include_workplace_on_documents=True, show_online_status=True,
        email_assinatura_ativa=True, email_assinatura_digital_ativa=True, email_assinatura_incluir_telefone=True,
        email_assinatura_incluir_endereco=True,
    )


def test_exclusao_transforma_usuario_em_tombstone_sem_pii_ou_acesso():
    alvo = _target()
    _anonimizar_usuario_excluido(alvo)
    assert alvo.status == "excluido"
    assert alvo.is_active is False
    assert alvo.role == "leitor"
    assert alvo.email == "excluido-42@deleted.corvia.invalid"
    assert alvo.full_name == "Conta excluída"
    assert alvo.password_hash != "hash-antigo"
    assert alvo.active_session_id is None
    assert alvo.cpf is None
    assert alvo.council_number is None
    assert alvo.workplace_name is None
    assert alvo.home_street is None
    assert alvo.practice_street is None
    assert alvo.instagram_handle is None
    assert alvo.email_assinatura_ativa is False
    assert alvo.convidado is False
    assert alvo.investidor is False


def test_listas_administrativas_ocultam_tombstones():
    source = __import__('pathlib').Path(__file__).resolve().parents[1] / 'app' / 'api' / 'admin.py'
    text = source.read_text(encoding='utf-8')
    assert 'q = db.query(User).filter(User.status != "excluido")' in text
    assert 'query = db.query(User).filter(User.status != "excluido")' in text


def test_exclusao_definitiva_e_restrita_ao_owner_admin():
    source = __import__('pathlib').Path(__file__).resolve().parents[1] / 'app' / 'api' / 'admin_user_management.py'
    text = source.read_text(encoding='utf-8')
    route = text[text.index('@router.delete("/{user_id}")'):]
    assert 'owner=Depends(require_owner_admin)' in route
    assert 'db.delete(alvo)' not in route
    assert '_anonimizar_usuario_excluido(alvo)' in route
