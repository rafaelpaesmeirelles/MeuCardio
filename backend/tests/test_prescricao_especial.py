from app.api import prescricao_especial
from app.models.email_account import EmailAccount


def test_natalia_lenira_podem_propria_e_rafael_wladmir_somente_rafael(db, criar_usuario):
    natalia, _ = criar_usuario(email="login-natalia@teste.local", full_name="Natalia")
    lenira, _ = criar_usuario(email="login-lenira@teste.local", full_name="Lenira")
    wladmir, _ = criar_usuario(email="login-wladmir@teste.local", full_name="Wladmir")
    for user, endereco in (
        (natalia, "natalia@corvia.med.br"),
        (lenira, "lenira@corvia.med.br"),
        (wladmir, "wladmir@corvia.med.br"),
    ):
        db.add(EmailAccount(
            user_id=user.id,
            email_address=endereco,
            mail360_account_key=f"key-{user.id}",
            status="ativa",
        ))
    db.commit()

    assert prescricao_especial._perfil_especial(db, natalia)["permite_propria"] is True
    assert prescricao_especial._perfil_especial(db, lenira)["permite_propria"] is True
    assert prescricao_especial._perfil_especial(db, wladmir)["permite_propria"] is False


def test_rafael_resolve_somente_admin_com_identidade_profissional(db, criar_usuario):
    rafael, _ = criar_usuario(
        email="rafael@teste.local",
        full_name="Rafael Paes Meirelles",
        role="admin",
    )
    rafael.council_name = "CRM"
    rafael.council_number = "138266"
    rafael.council_state = "SP"
    db.commit()

    outro, _ = criar_usuario(email="outro-admin@teste.local", full_name="Outro Admin", role="admin")
    assert prescricao_especial._eh_rafael(rafael) is True
    assert prescricao_especial._eh_rafael(outro) is False
    assert prescricao_especial._rafael(db).id == rafael.id


def test_documento_delegado_e_propriedade_do_rafael_e_origem_fica_auditavel(db, criar_usuario):
    rafael, _ = criar_usuario(
        email="rafael@teste.local", full_name="Rafael Paes Meirelles", role="admin"
    )
    rafael.council_number = "138266"
    rafael.council_state = "SP"
    lenira, _ = criar_usuario(email="lenira-login@teste.local", full_name="Lenira")
    db.add(EmailAccount(
        user_id=lenira.id,
        email_address="lenira@corvia.med.br",
        mail360_account_key="mail-lenira",
        status="ativa",
    ))
    db.commit()

    criado = prescricao_especial.criar(
        prescricao_especial.CriarIn(
            patient_name="Paciente Teste",
            body="Medicamento X\nTomar conforme orientação.",
            mode="rafael",
        ),
        db=db,
        user=lenira,
    )

    assert criado["originator_id"] == lenira.id
    assert criado["signer_id"] == rafael.id
    assert criado["status"] == "pendente_assinatura"
    assert criado["mode"] == "rafael"


def test_wladmir_nao_pode_criar_para_assinatura_propria(db, criar_usuario):
    from fastapi import HTTPException

    wladmir, _ = criar_usuario(email="wladmir-login@teste.local", full_name="Wladmir")
    db.add(EmailAccount(
        user_id=wladmir.id,
        email_address="wladmir@corvia.med.br",
        mail360_account_key="mail-wladmir",
        status="ativa",
    ))
    db.commit()

    try:
        prescricao_especial.criar(
            prescricao_especial.CriarIn(
                patient_name="Paciente Teste",
                body="Texto livre",
                mode="propria",
            ),
            db=db,
            user=wladmir,
        )
    except HTTPException as exc:
        assert exc.status_code == 403
    else:
        raise AssertionError("Wladmir não pode emitir com credenciais próprias")
