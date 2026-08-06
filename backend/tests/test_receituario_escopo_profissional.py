"""Escopo legal de prescrição por profissão, pela rota HTTP real
(`POST /api/receituario` e `/api/receituario/classificar`) — Trabalho 11,
ampliação de 06/08/2026. Complementa `test_escopo_profissional.py` (que
testa `escopo_profissional.py` isolado) exercitando o caminho completo:
resolução do item → classificação por lista da 344/98 → gate por profissão.
"""
import pytest
from sqlalchemy import text

from app.models.cmed import CmedApresentacao, CmedVersao
from app.models.drug import Drug
from app.models.receituario import ControlledSubstance, PrescriptionType
from app.models.subscription import Subscription
from app.services.classificacao_receituario import normalizar

_TABELAS = (
    "documentos_emitidos", "prescription_documents", "prescription_recipients",
    "prescriptions", "controlled_substances", "prescription_rules", "prescription_types",
    "cmed_apresentacoes", "cmed_versoes", "drugs",
)


def _headers(token: str) -> dict[str, str]:
    return {"Authorization": f"Bearer {token}"}


def _subscribe(db, user_id: int) -> None:
    db.add(Subscription(user_id=user_id, kind="meucardio", plano="basico", status="ativo"))
    db.commit()


@pytest.fixture(autouse=True)
def _seed(db):
    db.execute(text(f"TRUNCATE {', '.join(_TABELAS)} RESTART IDENTITY CASCADE"))
    db.add(PrescriptionType(codigo="COMUM", nome="Receituário comum", ativo=True))
    db.add(ControlledSubstance(
        nome="Isotretinoína", nome_normalizado=normalizar("Isotretinoína"),
        lista="C4", tipo_sncr=None, proscrita=False,
        fonte_norma="Portaria 344/98", fonte_versao="teste-v1",
    ))
    db.commit()
    yield


def _versao(db) -> CmedVersao:
    v = CmedVersao(publicado_em="20260721", arquivo_url="https://exemplo.gov.br/x.xlsx",
                    sha256="abc", linhas=1)
    db.add(v)
    db.commit()
    db.refresh(v)
    return v


def _drug_isento(db) -> Drug:
    d = Drug(slug="amoxicilina-isenta-teste", generic_name="Amoxicilina",
             drug_class="antibiótico", published=True)
    db.add(d)
    db.commit()
    db.refresh(d)
    db.add(CmedApresentacao(
        cmed_versao_id=_versao(db).id, drug_id=d.id, substancia_cmed="AMOXICILINA",
        laboratorio="Genérica", produto="Amoxil", apresentacao="500 MG CAP CT BL AL X 21",
        ggrem="1", tarja="Tarja Sem Tarja",
    ))
    db.commit()
    return d


def _drug_nao_isento(db) -> Drug:
    d = Drug(slug="losartana-nao-isenta-teste", generic_name="Losartana potássica",
             drug_class="BRA", published=True)
    db.add(d)
    db.commit()
    db.refresh(d)
    db.add(CmedApresentacao(
        cmed_versao_id=_versao(db).id, drug_id=d.id, substancia_cmed="LOSARTANA POTASSICA",
        laboratorio="Genérica", produto="Cozaar", apresentacao="50 MG COM CT BL AL X 30",
        ggrem="2", tarja="Tarja Vermelha",
    ))
    db.commit()
    return d


def _drug_c4(db) -> Drug:
    d = Drug(slug="isotretinoina-teste", generic_name="Isotretinoína",
             drug_class="retinoide", published=True)
    db.add(d)
    db.commit()
    db.refresh(d)
    return d


def _payload(drug: Drug) -> dict:
    return {
        "destinatario": {"nome": "Paciente de Teste"},
        "itens": [{
            "drug_slug": drug.slug, "descricao": drug.generic_name,
            "posologia": "conforme orientação", "apresentacao": "1 cp",
        }],
    }


class TestNaoMedicoRestritoAIsentos:
    def test_pode_prescrever_item_isento(self, client, db, criar_usuario):
        user, token = criar_usuario()
        user.council_name = "CREFITO"
        db.commit()
        _subscribe(db, user.id)
        item = _drug_isento(db)

        r = client.post("/api/receituario", headers=_headers(token), json=_payload(item))
        assert r.status_code == 201, r.text

    def test_e_bloqueado_em_item_que_exige_prescricao(self, client, db, criar_usuario):
        user, token = criar_usuario()
        user.council_name = "CRP"
        db.commit()
        _subscribe(db, user.id)
        item = _drug_nao_isento(db)

        r = client.post("/api/receituario", headers=_headers(token), json=_payload(item))
        assert r.status_code == 422, r.text
        assert "escopo legal" in r.json()["detail"]["erro"]

    def test_previa_de_classificacao_sinaliza_bloqueio_sem_recusar(self, client, db, criar_usuario):
        """`/classificar` é preview — nunca levanta 422, só informa."""
        user, token = criar_usuario()
        user.council_name = "CRESS"
        db.commit()
        _subscribe(db, user.id)
        item = _drug_nao_isento(db)

        r = client.post("/api/receituario/classificar", headers=_headers(token), json=_payload(item))
        assert r.status_code == 200, r.text
        assert len(r.json()["bloqueados_por_escopo"]) == 1


class TestDentistaRestritoNaListaC4:
    def test_bloqueado_em_c4(self, client, db, criar_usuario):
        user, token = criar_usuario()
        user.council_name = "CRO"
        db.commit()
        _subscribe(db, user.id)
        item = _drug_c4(db)

        r = client.post("/api/receituario", headers=_headers(token), json=_payload(item))
        assert r.status_code == 422, r.text
        assert "escopo legal" in r.json()["detail"]["erro"]

    def test_liberado_fora_da_c4(self, client, db, criar_usuario):
        user, token = criar_usuario()
        user.council_name = "CRO"
        db.commit()
        _subscribe(db, user.id)
        item = _drug_isento(db)

        r = client.post("/api/receituario", headers=_headers(token), json=_payload(item))
        assert r.status_code == 201, r.text


class TestMedicoSemRestricaoAdicional:
    def test_medico_prescreve_item_nao_isento_sem_bloqueio(self, client, db, criar_usuario):
        user, token = criar_usuario()
        user.council_name = "CRM"
        db.commit()
        _subscribe(db, user.id)
        item = _drug_nao_isento(db)

        r = client.post("/api/receituario", headers=_headers(token), json=_payload(item))
        assert r.status_code == 201, r.text
