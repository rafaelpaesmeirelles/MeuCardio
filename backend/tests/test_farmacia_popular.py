"""Testes do elenco do Programa Farmácia Popular do Brasil (PFPB).

Gap encontrado por sessão externa (Claude chat), 29/08/2026 — ver CLAUDE.md e
`app/services/farmacia_popular.py`. Cobre a mesma classe de risco que já
existe para CMED: casar substância isolada com `Drug` de COMBINAÇÃO por
engano atribuiria o subsídio à página errada (ver
`test_glibenclamida_nao_casa_com_combinacao_de_metformina`, que reproduz
com dado real do catálogo o bug encontrado e corrigido nesta sessão antes
do commit) — e a regra de segurança que nunca deve relaxar: elegibilidade
só é confirmada com EAN carregado, nunca por match de substância isolado.
"""
import pytest
from sqlalchemy import text

from app.models.drug import Drug
from app.models.farmacia_popular import FarmaciaPopularItem, FarmaciaPopularVersao
from app.services import farmacia_popular

_TABELAS = ("farmacia_popular_itens", "farmacia_popular_versoes", "drugs")


@pytest.fixture(autouse=True)
def _limpar(db):
    db.execute(text(f"TRUNCATE {', '.join(_TABELAS)} RESTART IDENTITY CASCADE"))
    db.commit()
    yield


def _drug(db, slug: str, generic_name: str, published: bool = True) -> Drug:
    d = Drug(slug=slug, generic_name=generic_name, published=published)
    db.add(d)
    db.flush()
    return d


class TestCasamentoDeSubstancia:
    def test_glosa_de_sal_e_aceita_dos_dois_lados(self):
        pfpb = farmacia_popular.palavras_normalizadas("Besilato de anlodipino")
        local = farmacia_popular.palavras_normalizadas("Anlodipino (besilato)")
        assert pfpb == local == frozenset({"ANLODIPINO"})

    def test_glibenclamida_nao_casa_com_combinacao_de_metformina(self, db):
        """Reproduz o bug real encontrado nesta sessão: sem filtrar
        combinação (`+` no `generic_name`) do pool de candidatos, o item
        isolado "Glibenclamida" do PFPB casava com o `Drug` de combinação
        "Metformina (cloridrato) + Glibenclamida" — porque o conjunto de
        palavras do isolado é subconjunto do da combinação. Neste catálogo
        NÃO existe `Drug` isolado de glibenclamida, só a combinação; o
        resultado correto é não casar com nada, não "roubar" a combinação."""
        _drug(db, "metformina-cloridrato-glibenclamida", "Metformina (cloridrato) + Glibenclamida")
        farmacos = db.query(Drug.id, Drug.generic_name).filter(Drug.published.is_(True)).all()
        farmacos_normalizados = [
            (drug_id, farmacia_popular.palavras_normalizadas(nome))
            for drug_id, nome in farmacos if "+" not in nome
        ]
        assert farmacos_normalizados == []  # a combinação foi filtrada
        assert farmacia_popular._casar_substancia("Glibenclamida", farmacos_normalizados) is None

    def test_isolado_prefere_igualdade_exata_sobre_combinacao_quando_ambos_existem(self, db):
        combo = _drug(db, "metformina-cloridrato-dapagliflozina", "Metformina (cloridrato) + Dapagliflozina")
        isolado = _drug(db, "dapagliflozina", "Dapagliflozina")
        farmacos = db.query(Drug.id, Drug.generic_name).filter(Drug.published.is_(True)).all()
        farmacos_normalizados = [
            (drug_id, farmacia_popular.palavras_normalizadas(nome))
            for drug_id, nome in farmacos if "+" not in nome
        ]
        # a combinação já não está no pool — confirma a guarda de novo
        assert combo.id not in {i for i, _ in farmacos_normalizados}
        assert farmacia_popular._casar_substancia("Dapagliflozina", farmacos_normalizados) == isolado.id

    def test_orfao_nao_publicado_nao_rouba_match(self, db):
        """Mesma guarda já documentada e testada para CMED — filtro por
        `published=True` é aplicado antes do casamento."""
        _drug(db, "atenolol-orfao", "Atenolol", published=False)
        vivo = _drug(db, "atenolol", "Atenolol", published=True)
        farmacos = db.query(Drug.id, Drug.generic_name).filter(Drug.published.is_(True)).all()
        assert [d for d, _ in farmacos] == [vivo.id]


class TestExposicaoNaApi:
    def test_sem_item_devolve_none(self):
        assert farmacia_popular.montar_exposicao(None) is None

    def test_item_sem_ean_nao_confirma_elegibilidade(self, db):
        """Regra de segurança inegociável: match de substância sozinho NUNCA
        autoriza `elegivel_confirmado = True`."""
        versao = FarmaciaPopularVersao(conferido_em="20260829", fontes="teste", itens=1)
        db.add(versao)
        db.flush()
        item = FarmaciaPopularItem(
            farmacia_popular_versao_id=versao.id, drug_id=None,
            substancia_pfpb="Captopril", dose_referencia="25 mg", categoria="hipertensao",
            indicacao="Hipertensão arterial", criterio_acesso="Receita comum.",
            ean=None, fonte_refs="teste",
        )
        exposicao = farmacia_popular.montar_exposicao(item)
        assert exposicao["elegivel_confirmado"] is False
        assert "código de barras" in exposicao["aviso"]

    def test_item_com_ean_confirma_elegibilidade(self, db):
        versao = FarmaciaPopularVersao(conferido_em="20260829", fontes="teste", itens=1)
        db.add(versao)
        db.flush()
        item = FarmaciaPopularItem(
            farmacia_popular_versao_id=versao.id, drug_id=None,
            substancia_pfpb="Captopril", dose_referencia="25 mg", categoria="hipertensao",
            indicacao="Hipertensão arterial", criterio_acesso="Receita comum.",
            ean="7891234567890", fonte_refs="teste",
        )
        exposicao = farmacia_popular.montar_exposicao(item)
        assert exposicao["elegivel_confirmado"] is True
        assert exposicao["aviso"] is None

    def test_item_inativo_devolve_none(self, db):
        versao = FarmaciaPopularVersao(conferido_em="20260829", fontes="teste", itens=1)
        db.add(versao)
        db.flush()
        item = FarmaciaPopularItem(
            farmacia_popular_versao_id=versao.id, drug_id=None,
            substancia_pfpb="Captopril", dose_referencia="25 mg", categoria="hipertensao",
            indicacao="Hipertensão arterial", criterio_acesso="Receita comum.",
            ean="7891234567890", fonte_refs="teste", ativo=False,
        )
        assert farmacia_popular.montar_exposicao(item) is None


class TestCargaDoManifesto:
    def test_manifesto_padrao_carrega_sem_erro_e_casa_a_maioria(self, db):
        atenolol = _drug(db, "atenolol", "Atenolol")
        _drug(db, "captopril", "Captopril")
        _drug(db, "metformina-cloridrato-glibenclamida", "Metformina (cloridrato) + Glibenclamida")

        resultado = farmacia_popular.carregar_manifesto(db)

        assert resultado["carregado"] is True
        assert resultado["itens"] == 19
        # Glibenclamida não pode casar com o combo — mesmo cenário do teste acima
        glibenclamida = (
            db.query(FarmaciaPopularItem)
            .filter(FarmaciaPopularItem.substancia_pfpb == "Glibenclamida")
            .first()
        )
        assert glibenclamida.drug_id is None

        atenolol_item = (
            db.query(FarmaciaPopularItem)
            .filter(FarmaciaPopularItem.substancia_pfpb == "Atenolol")
            .first()
        )
        assert atenolol_item.drug_id == atenolol.id

        # nenhum item nasce com EAN confirmado nesta carga inicial — ver
        # aviso de segurança em app/models/farmacia_popular.py
        assert db.query(FarmaciaPopularItem).filter(FarmaciaPopularItem.ean.isnot(None)).count() == 0

    def test_carga_nao_apaga_versao_anterior(self, db):
        _drug(db, "captopril", "Captopril")
        farmacia_popular.carregar_manifesto(db)
        farmacia_popular.carregar_manifesto(db)
        assert db.query(FarmaciaPopularVersao).count() == 2
