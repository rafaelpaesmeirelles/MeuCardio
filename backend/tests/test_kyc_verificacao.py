"""app/services/kyc/verificacao.py — submissão, checagem de CRM (melhor
esforço, sem credencial configurada nos testes) e ciclo de revisão.
"""
import pytest

from app.core.config import settings
from app.models.kyc import KycVerification
from app.services.kyc import council_check, crm_check, verificacao


@pytest.fixture(autouse=True)
def _diretorio_kyc(tmp_path, monkeypatch):
    monkeypatch.setattr(settings, "kyc_dir", str(tmp_path))


def _docs(**overrides) -> verificacao.DocumentosSubmissao:
    base = dict(
        doc_profissional_frente=b"frente-profissional",
        doc_profissional_verso=b"verso-profissional",
        selfie=b"selfie-ao-vivo",
        doc_pessoal_frente=b"frente-pessoal",
        doc_pessoal_verso=b"verso-pessoal",
    )
    base.update(overrides)
    return verificacao.DocumentosSubmissao(**base)


def test_submeter_sem_documento_pessoal_nem_digital_falha(db, criar_usuario):
    user, _ = criar_usuario()
    docs = _docs(doc_pessoal_frente=None, doc_pessoal_verso=None)
    with pytest.raises(verificacao.DocumentoPessoalIncompleto):
        verificacao.submeter(db, user, docs)


def test_submeter_com_par_de_fotos_pessoal_funciona(db, criar_usuario):
    user, _ = criar_usuario()
    registro = verificacao.submeter(db, user, _docs())
    db.commit()
    assert registro.doc_pessoal_frente is not None
    assert registro.doc_pessoal_digital is None


def test_submeter_com_documento_digital_funciona_sem_fotos(db, criar_usuario):
    user, _ = criar_usuario()
    docs = _docs(doc_pessoal_frente=None, doc_pessoal_verso=None, doc_pessoal_digital=b"%PDF-1.4 conteudo")
    registro = verificacao.submeter(db, user, docs)
    db.commit()
    assert registro.doc_pessoal_digital is not None
    assert registro.doc_pessoal_frente is None


def test_sem_credencial_cfm_configurada_vai_para_revisao_manual(db, criar_usuario):
    """CRM continua exigindo checagem confirmada OU aprovação manual —
    sem credencial do CFM, a submissão fica bloqueada. Comportamento
    inalterado pela generalização a outros conselhos (06/08/2026)."""
    user, _ = criar_usuario()
    user.council_name = "CRM"
    user.council_number = "123456"
    user.council_state = "SP"
    db.commit()
    registro = verificacao.submeter(db, user, _docs())
    db.commit()
    assert registro.status == "aguardando_revisao"
    assert registro.conselho_check_status == crm_check.STATUS_ERRO_CHECAGEM
    assert verificacao.liberado_para_uso(registro) is False


def test_convidado_com_crm_e_aprovado_automaticamente(db, criar_usuario):
    """Médico convidado (08/08/2026): mesmo cenário do teste acima (CRM sem
    credencial do CFM, cairia em 'aguardando_revisao') — mas com
    `user.convidado = True`, a submissão já sai como 'aprovado', sem passar
    pela fila de revisão manual."""
    user, _ = criar_usuario()
    user.council_name = "CRM"
    user.council_number = "123456"
    user.council_state = "SP"
    user.convidado = True
    db.commit()
    registro = verificacao.submeter(db, user, _docs())
    db.commit()
    assert registro.status == "aprovado"
    assert registro.aprovado_em is not None
    assert registro.aprovado_por is None
    assert "convidado" in (registro.nota_revisao or "")
    assert verificacao.liberado_para_uso(registro) is True
    # Aprovação definitiva não entra mais na fila do admin.
    assert registro not in verificacao.listar_pendentes(db)


def test_convidado_aprova_mesmo_quando_checagem_ja_liberou_por_outro_caminho(db, criar_usuario):
    """Corrigido em 13/08/2026 (pedido do Rafael: "toda submissão válida
    deve terminar definitivamente em aprovado, independentemente do
    resultado informativo da checagem automática do conselho") — antes, o
    atalho do convidado só agia sobre 'aguardando_revisao': se a checagem
    de conselho já tivesse liberado por outro caminho (ex.: profissão sem
    checagem automática, como aqui), o convidado ficava parado em
    'liberado_sem_checagem', que `listar_pendentes()` inclui na fila do
    admin — exatamente a dependência de revisão humana que devia ter sido
    eliminada. Agora sempre termina em 'aprovado', qualquer que seja o
    resultado (só informativo) da checagem."""
    user, _ = criar_usuario()
    user.council_name = "CREFITO"
    user.council_number = "98765"
    user.council_state = "RJ"
    user.convidado = True
    db.commit()
    registro = verificacao.submeter(db, user, _docs())
    db.commit()
    assert registro.status == "aprovado"
    assert registro.aprovado_por is None
    assert registro not in verificacao.listar_pendentes(db)


def test_profissao_sem_conselho_com_checagem_e_liberada_mesmo_sem_confirmar(db, criar_usuario):
    """Não-médico (ou CRM não informado): nenhum conselho fora do CRM tem
    checagem automática hoje, então a submissão libera acesso e assinatura
    de imediato, com o registro marcado como não verificado para a fila de
    revisão manual do Rafael — decisão dele em 06/08/2026."""
    user, _ = criar_usuario()
    user.council_name = "CREFITO"
    user.council_number = "98765"
    user.council_state = "RJ"
    db.commit()
    registro = verificacao.submeter(db, user, _docs())
    db.commit()
    assert registro.status == "liberado_sem_checagem"
    assert registro.conselho_check_status == council_check.STATUS_INDISPONIVEL_PARA_CONSELHO
    assert verificacao.liberado_para_uso(registro) is True
    # E ainda assim entra na fila do admin — liberado não é a mesma coisa
    # que aprovado definitivamente.
    assert registro in verificacao.listar_pendentes(db)


def test_submeter_de_novo_substitui_e_apaga_arquivos_antigos(db, criar_usuario):
    from app.services import cofre

    user, _ = criar_usuario()
    r1 = verificacao.submeter(db, user, _docs())
    db.commit()
    nome_antigo = r1.doc_profissional_frente

    verificacao.submeter(db, user, _docs(doc_profissional_frente=b"nova-frente"))
    db.commit()

    assert db.query(KycVerification).filter(KycVerification.owner_id == user.id).count() == 1
    with pytest.raises(FileNotFoundError):
        cofre.ler(nome_antigo, user.id, raiz=verificacao._raiz())


def test_liberado_para_uso_none_e_false():
    assert verificacao.liberado_para_uso(None) is False


def test_listar_pendentes_inclui_aguardando_e_liberado_crm_mas_nao_aprovado(db, criar_usuario):
    user1, _ = criar_usuario()
    user2, _ = criar_usuario(email="pendente2@teste.local")
    user3, _ = criar_usuario(email="pendente3@teste.local")

    r1 = verificacao.submeter(db, user1, _docs())  # aguardando_revisao
    r2 = verificacao.submeter(db, user2, _docs())
    r2.status = "liberado_conselho_ok"
    r3 = verificacao.submeter(db, user3, _docs())
    db.commit()
    verificacao.aprovar(db, r3, user1, "ok")  # aprovado — some da fila
    db.commit()

    pendentes = {r.owner_id for r in verificacao.listar_pendentes(db)}
    assert pendentes == {user1.id, user2.id}


def test_aprovar_marca_status_e_quem_aprovou(db, criar_usuario):
    user, _ = criar_usuario()
    admin, _ = criar_usuario(email="admin-kyc@teste.local", role="admin")
    registro = verificacao.submeter(db, user, _docs())
    db.commit()

    verificacao.aprovar(db, registro, admin, "documentos conferem")
    db.commit()
    assert registro.status == "aprovado"
    assert registro.aprovado_por == admin.id
    assert verificacao.liberado_para_uso(registro) is True


def test_rejeitar_marca_status_e_nota(db, criar_usuario):
    user, _ = criar_usuario()
    admin, _ = criar_usuario(email="admin-kyc2@teste.local", role="admin")
    registro = verificacao.submeter(db, user, _docs())
    db.commit()

    verificacao.rejeitar(db, registro, admin, "foto do documento ilegível")
    db.commit()
    assert registro.status == "rejeitado"
    assert registro.nota_revisao == "foto do documento ilegível"
    assert verificacao.liberado_para_uso(registro) is False


def test_ler_documento_isola_por_owner_id(db, criar_usuario):
    user1, _ = criar_usuario()
    user2, _ = criar_usuario(email="outro-kyc@teste.local")
    registro = verificacao.submeter(db, user1, _docs())
    db.commit()

    with pytest.raises(Exception):  # cofre detecta dado autenticado errado (InvalidTag → CofreIndisponivel)
        verificacao.ler_documento(registro, "doc_profissional_frente", user2.id)

    conteudo = verificacao.ler_documento(registro, "doc_profissional_frente", user1.id)
    assert conteudo == b"frente-profissional"
