"""`app.commands.kyc_retention_relatorio` — issue #52, hardening de segurança.

Cobre a garantia central deste comando: é SOMENTE LEITURA. Nunca apaga
arquivo nem altera registro, mesmo com dados reais de verificações em
estados diferentes.
"""
from datetime import datetime, timedelta, timezone

from app.core.config import settings
from app.models.kyc import KycVerification
from app.services import cofre
from app.services.kyc import verificacao
from app.commands import kyc_retention_relatorio


def _criar_usuario_kyc(db, criar_usuario, **kwargs):
    user, _token = criar_usuario(**kwargs)
    return user


def test_relatorio_nao_apaga_nenhum_arquivo(tmp_path, monkeypatch, db, criar_usuario):
    monkeypatch.setattr(settings, "kyc_dir", str(tmp_path))
    user = _criar_usuario_kyc(db, criar_usuario, email="kyc-retencao-1@teste.local")

    docs = verificacao.DocumentosSubmissao(
        doc_profissional_frente=b"\xff\xd8\xff" + b"frente" * 20,
        doc_profissional_verso=b"\xff\xd8\xff" + b"verso" * 20,
        selfie=b"\xff\xd8\xff" + b"selfie" * 20,
        doc_pessoal_frente=b"\xff\xd8\xff" + b"id-frente" * 20,
        doc_pessoal_verso=b"\xff\xd8\xff" + b"id-verso" * 20,
    )
    registro = verificacao.submeter(db, user, docs)
    db.commit()

    nomes_antes = {
        registro.doc_profissional_frente, registro.doc_profissional_verso,
        registro.selfie, registro.doc_pessoal_frente, registro.doc_pessoal_verso,
    }
    arquivos_no_disco_antes = {p.name for p in tmp_path.glob("*.bin")}
    assert nomes_antes <= arquivos_no_disco_antes

    linhas = kyc_retention_relatorio.gerar_relatorio()

    arquivos_no_disco_depois = {p.name for p in tmp_path.glob("*.bin")}
    assert arquivos_no_disco_antes == arquivos_no_disco_depois, (
        "o relatório apagou ou alterou arquivo(s) — ele tem que ser puramente leitura"
    )

    registro_depois = db.get(KycVerification, registro.id)
    assert registro_depois.status == registro.status
    assert registro_depois.doc_profissional_frente == registro.doc_profissional_frente

    linha = next(l for l in linhas if l["verification_id"] == registro.id)
    assert linha["status"] == "aguardando_revisao"
    assert linha["arquivos_ainda_presentes"] == 5
    assert linha["total_de_campos_possiveis"] == 6


def test_relatorio_conta_dias_desde_aprovacao(tmp_path, monkeypatch, db, criar_usuario):
    monkeypatch.setattr(settings, "kyc_dir", str(tmp_path))
    user = _criar_usuario_kyc(db, criar_usuario, email="kyc-retencao-2@teste.local")
    admin = _criar_usuario_kyc(db, criar_usuario, email="kyc-retencao-admin@teste.local", role="admin")

    docs = verificacao.DocumentosSubmissao(
        doc_profissional_frente=b"\xff\xd8\xff" + b"a" * 20,
        doc_profissional_verso=b"\xff\xd8\xff" + b"b" * 20,
        selfie=b"\xff\xd8\xff" + b"c" * 20,
        doc_pessoal_frente=b"\xff\xd8\xff" + b"d" * 20,
        doc_pessoal_verso=b"\xff\xd8\xff" + b"e" * 20,
    )
    registro = verificacao.submeter(db, user, docs)
    db.commit()

    verificacao.aprovar(db, registro, admin, "confere")
    registro.aprovado_em = datetime.now(timezone.utc) - timedelta(days=30)
    db.commit()

    linhas = kyc_retention_relatorio.gerar_relatorio()
    linha = next(l for l in linhas if l["verification_id"] == registro.id)
    assert linha["status"] == "aprovado"
    assert linha["dias_desde_ultima_atualizacao_de_status"] == 30


def test_relatorio_sem_nenhum_registro_nao_quebra():
    # Não usa fixture de banco populado — só confirma que gerar_relatorio()
    # lida com "nenhum registro" sem lançar exceção (mesma disciplina do
    # main(), que imprime uma mensagem específica nesse caso).
    linhas = kyc_retention_relatorio.gerar_relatorio()
    assert isinstance(linhas, list)
