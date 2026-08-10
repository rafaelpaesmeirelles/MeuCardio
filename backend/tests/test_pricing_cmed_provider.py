"""app/services/pricing/cmed_provider.py — adaptador CMED sobre a
arquitetura multi-fonte de preços (issue #52, nova fase).

Não duplica a lógica de download/parsing/casamento (já testada em
test_cmed_precos.py) — só confere que dados já persistidos em
CmedApresentacao/CmedVersao são corretamente traduzidos para o contrato
comum PriceObservation.

`drugs`/`cmed_apresentacoes`/`cmed_versoes` são tabelas de conteúdo, não
cobertas pelo `_banco_limpo` autouse do conftest (de propósito — essa
fixture cobre só as tabelas da suíte do CorvIA Mail), daí o TRUNCATE
explícito aqui, mesmo padrão de `test_relacionados.py`/`test_library_catalog.py`.
"""
from decimal import Decimal

from sqlalchemy import text

from app.models.cmed import CmedApresentacao, CmedVersao
from app.models.drug import Drug
from app.services.pricing.cmed_provider import CMEDProvider

TABELAS = ("cmed_apresentacoes", "cmed_versoes", "drugs")


def _limpar(db):
    db.execute(text(f"TRUNCATE {', '.join(TABELAS)} RESTART IDENTITY CASCADE"))
    db.commit()


def _drug(db, slug="metoprolol-teste-preco") -> Drug:
    d = Drug(slug=slug, generic_name="Metoprolol", drug_class="beta-bloqueador", published=True)
    db.add(d)
    db.commit()
    db.refresh(d)
    return d


def test_sem_nenhuma_versao_cmed_importada_devolve_lista_vazia(db):
    _limpar(db)
    d = _drug(db)
    provider = CMEDProvider(db)
    assert provider.observations_for(d.id) == []


def test_traduz_apresentacao_cmed_para_price_observation(db):
    _limpar(db)
    d = _drug(db)
    versao = CmedVersao(
        publicado_em="20260721", arquivo_url="https://exemplo.gov.br/x.xlsx",
        sha256="abc", linhas=1,
    )
    db.add(versao)
    db.commit()
    db.refresh(versao)

    db.add(CmedApresentacao(
        cmed_versao_id=versao.id, drug_id=d.id, substancia_cmed="TARTARATO DE METOPROLOL",
        laboratorio="AstraZeneca", produto="Seloken", apresentacao="100 MG COM CT BL AL X 30",
        ggrem="123456789", restricao_hospitalar=False,
        pmc_por_aliquota={"PMC 18%": 45.5, "PMC 20%": 46.8, "PMC Sem Impostos": None},
    ))
    db.commit()

    observacoes = CMEDProvider(db).observations_for(d.id)

    # Uma observação por alíquota com valor real — a alíquota nula (PMC Sem
    # Impostos, None) é descartada, não vira um preço "zero" fabricado.
    assert len(observacoes) == 2
    for obs in observacoes:
        assert obs.source == "cmed"
        assert obs.source_type == "regulatory"
        assert obs.price_type == "pmc"
        assert obs.confidence == "official"
        assert obs.currency == "BRL"
        assert obs.drug_id == d.id
        assert obs.presentation_ref == "123456789"
        assert obs.metadata["produto"] == "Seloken"
        assert obs.metadata["cmed_versao_publicado_em"] == "20260721"

    regioes = {obs.region for obs in observacoes}
    assert regioes == {"PMC 18%", "PMC 20%"}
    precos = {obs.region: obs.price for obs in observacoes}
    assert precos["PMC 18%"] == Decimal("45.5")
    assert precos["PMC 20%"] == Decimal("46.8")


def test_usa_apenas_a_versao_cmed_mais_recente(db):
    """Duas competências importadas (histórico preservado, nunca apagado) —
    o provider só expõe a mais recente, não soma preços de versões antigas
    como se fossem observações simultâneas."""
    _limpar(db)
    d = _drug(db)
    v1 = CmedVersao(publicado_em="20260621", arquivo_url="https://x", sha256="v1", linhas=1)
    db.add(v1); db.commit(); db.refresh(v1)
    db.add(CmedApresentacao(
        cmed_versao_id=v1.id, drug_id=d.id, substancia_cmed="TARTARATO DE METOPROLOL",
        laboratorio="AstraZeneca", produto="Seloken", apresentacao="X",
        ggrem="OLD", restricao_hospitalar=False, pmc_por_aliquota={"PMC 18%": 40.0},
    ))
    db.commit()

    v2 = CmedVersao(publicado_em="20260721", arquivo_url="https://x", sha256="v2", linhas=1)
    db.add(v2); db.commit(); db.refresh(v2)
    db.add(CmedApresentacao(
        cmed_versao_id=v2.id, drug_id=d.id, substancia_cmed="TARTARATO DE METOPROLOL",
        laboratorio="AstraZeneca", produto="Seloken", apresentacao="X",
        ggrem="NEW", restricao_hospitalar=False, pmc_por_aliquota={"PMC 18%": 45.5},
    ))
    db.commit()

    observacoes = CMEDProvider(db).observations_for(d.id)
    assert len(observacoes) == 1
    assert observacoes[0].presentation_ref == "NEW"
    assert observacoes[0].price == Decimal("45.5")


def test_farmaco_sem_apresentacao_casada_devolve_lista_vazia(db):
    _limpar(db)
    d = _drug(db, slug="sem-preco-teste")
    versao = CmedVersao(publicado_em="20260721", arquivo_url="https://x", sha256="v", linhas=0)
    db.add(versao)
    db.commit()
    assert CMEDProvider(db).observations_for(d.id) == []
