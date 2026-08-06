"""Escopo legal de prescrição por profissão — Trabalho 11, ampliação de
06/08/2026 (app/services/kyc/escopo_profissional.py).
"""
import pytest
from sqlalchemy import text

from app.models.cmed import CmedApresentacao, CmedVersao
from app.models.drug import Drug
from app.services.kyc import escopo_profissional as ep


@pytest.fixture(autouse=True)
def _limpar(db):
    db.execute(text("TRUNCATE cmed_apresentacoes, cmed_versoes, drugs RESTART IDENTITY CASCADE"))
    db.commit()
    yield


def _versao(db) -> CmedVersao:
    v = CmedVersao(publicado_em="20260721", arquivo_url="https://exemplo.gov.br/x.xlsx",
                    sha256="abc", linhas=1)
    db.add(v)
    db.commit()
    db.refresh(v)
    return v


def _drug(db, slug="losartana-teste") -> Drug:
    d = Drug(slug=slug, generic_name="Losartana potássica", drug_class="BRA", published=True)
    db.add(d)
    db.commit()
    db.refresh(d)
    return d


class TestEscopoDe:
    def test_crm_e_completo(self):
        assert ep.escopo_de("CRM") == ep.ESCOPO_COMPLETO

    def test_cro_e_restrito_odonto(self):
        assert ep.escopo_de("CRO") == ep.ESCOPO_RESTRITO_ODONTO

    @pytest.mark.parametrize("conselho", [
        "COREN", "CRF", "CRN", "CREFITO", "CRP", "CREF", "CRESS", "CRBM", "OUTRO",
    ])
    def test_demais_conselhos_sao_apenas_isentos(self, conselho):
        assert ep.escopo_de(conselho) == ep.ESCOPO_APENAS_ISENTOS

    def test_em_branco_e_tratado_como_completo(self):
        """Cadastro sem council_name preenchido não acontece em produção —
        `_perfil_profissional_completo()` já bloqueia o primeiro acesso sem
        ele — mas onde aparecer (dado legado/teste) o padrão é o histórico
        real da base: só médico, até esta ampliação."""
        assert ep.escopo_de(None) == ep.ESCOPO_COMPLETO
        assert ep.escopo_de("") == ep.ESCOPO_COMPLETO

    def test_minusculo_e_normalizado(self):
        assert ep.escopo_de("cro") == ep.ESCOPO_RESTRITO_ODONTO


class TestEhIsentoDePrescricao:
    def test_sem_casamento_na_cmed_e_nao_isento(self, db):
        assert ep.eh_isento_de_prescricao(db, None) is False

    def test_drug_id_sem_nenhuma_apresentacao_e_nao_isento(self, db):
        d = _drug(db)
        assert ep.eh_isento_de_prescricao(db, d.id) is False

    def test_todas_apresentacoes_sem_tarja_e_isento(self, db):
        v = _versao(db)
        d = _drug(db, slug="dipirona-teste")
        db.add(CmedApresentacao(
            cmed_versao_id=v.id, drug_id=d.id, substancia_cmed="DIPIRONA SODICA",
            laboratorio="Genérica", produto="Novalgina", apresentacao="500 MG COM CT BL AL X 10",
            ggrem="1", tarja="Tarja Sem Tarja",
        ))
        db.commit()
        assert ep.eh_isento_de_prescricao(db, d.id) is True

    def test_uma_apresentacao_com_tarja_vermelha_torna_nao_isento(self, db):
        v = _versao(db)
        d = _drug(db, slug="losartana-mista-teste")
        db.add(CmedApresentacao(
            cmed_versao_id=v.id, drug_id=d.id, substancia_cmed="LOSARTANA POTASSICA",
            laboratorio="A", produto="X", apresentacao="50 MG COM CT BL AL X 30",
            ggrem="1", tarja="Tarja Sem Tarja",
        ))
        db.add(CmedApresentacao(
            cmed_versao_id=v.id, drug_id=d.id, substancia_cmed="LOSARTANA POTASSICA",
            laboratorio="A", produto="X", apresentacao="100 MG COM CT BL AL X 30",
            ggrem="2", tarja="Tarja Vermelha",
        ))
        db.commit()
        assert ep.eh_isento_de_prescricao(db, d.id) is False


class TestAvaliarItem:
    def test_escopo_completo_libera_qualquer_lista(self, db):
        assert ep.avaliar_item(db, ep.ESCOPO_COMPLETO, "C4", None).permitido is True
        assert ep.avaliar_item(db, ep.ESCOPO_COMPLETO, None, None).permitido is True

    def test_odonto_bloqueia_so_lista_c4(self, db):
        bloqueado = ep.avaliar_item(db, ep.ESCOPO_RESTRITO_ODONTO, "C4", None)
        assert bloqueado.permitido is False
        assert "cirurgião-dentista" in bloqueado.motivo

        liberado = ep.avaliar_item(db, ep.ESCOPO_RESTRITO_ODONTO, "C1", None)
        assert liberado.permitido is True

    def test_apenas_isentos_libera_so_medicamento_isento(self, db):
        v = _versao(db)
        isento = _drug(db, slug="isento-teste")
        db.add(CmedApresentacao(
            cmed_versao_id=v.id, drug_id=isento.id, substancia_cmed="X",
            laboratorio="A", produto="X", apresentacao="1", ggrem="1",
            tarja="Tarja Sem Tarja",
        ))
        nao_isento = _drug(db, slug="nao-isento-teste")
        db.add(CmedApresentacao(
            cmed_versao_id=v.id, drug_id=nao_isento.id, substancia_cmed="Y",
            laboratorio="A", produto="Y", apresentacao="1", ggrem="2",
            tarja="Tarja Vermelha",
        ))
        db.commit()

        assert ep.avaliar_item(db, ep.ESCOPO_APENAS_ISENTOS, None, isento.id).permitido is True
        bloqueado = ep.avaliar_item(db, ep.ESCOPO_APENAS_ISENTOS, None, nao_isento.id)
        assert bloqueado.permitido is False
        assert bloqueado.motivo
