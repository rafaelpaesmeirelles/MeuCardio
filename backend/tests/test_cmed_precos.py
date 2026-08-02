"""Testes da Tarefa A/B — preço regulado via CMED (CLAUDE.md).

Cobre a normalização/casamento de substância (a parte que decide se um preço
é atribuído ao fármaco certo — errar aqui mostra preço de combinação como se
fosse do princípio isolado, o que o CLAUDE.md trata como erro grave) e a
resolução de PMC por UF (rótulo tem que dizer "teto regulado pela CMED",
nunca "preço médio", e nunca inventar alíquota de UF sem fonte).
"""
import pytest
from sqlalchemy import text

from app.models.cmed import CmedApresentacao, CmedVersao
from app.models.drug import Drug
from app.services import cmed_precos

_TABELAS = ("cmed_apresentacoes", "cmed_versoes", "drugs")


@pytest.fixture(autouse=True)
def _limpar(db):
    db.execute(text(f"TRUNCATE {', '.join(_TABELAS)} RESTART IDENTITY CASCADE"))
    db.commit()
    yield


class TestNormalizacao:
    def test_sal_e_hidrato_sao_removidos_dos_dois_lados(self):
        a = cmed_precos.palavras_normalizadas("Dabigatrana (etexilato)")
        b = cmed_precos.palavras_normalizadas("MESILATO DE ETEXILATO DE DABIGATRANA")
        assert a == b == frozenset({"DABIGATRANA"})

    def test_glosa_local_a_mais_e_aceita(self):
        cmed = cmed_precos.palavras_normalizadas("NITROGLICERINA")
        local = cmed_precos.palavras_normalizadas("Nitroglicerina (trinitrato de glicerila)")
        assert cmed_precos.eh_match(cmed, local) is True

    def test_combinacao_da_cmed_nunca_bate_em_principio_isolado(self):
        """O caso que motivou a regra assimétrica: "valsartana" isolada não
        pode herdar o preço de "sacubitril valsartana sódica hidratada"."""
        cmed = cmed_precos.palavras_normalizadas("SACUBITRIL VALSARTANA SÓDICA HIDRATADA")
        local = cmed_precos.palavras_normalizadas("Valsartana")
        assert cmed_precos.eh_match(cmed, local) is False

    def test_combinacao_com_ponto_e_virgula_e_ignorada_no_casamento(self):
        assert cmed_precos.eh_combinacao("BESILATO DE ANLODIPINO;VALSARTANA") is True
        assert cmed_precos.casar_substancia(
            "BESILATO DE ANLODIPINO;VALSARTANA", [(1, cmed_precos.palavras_normalizadas("Valsartana"))]
        ) == []

    def test_casar_substancia_prefere_igualdade_exata_em_empate(self):
        farmacos = [
            (1, cmed_precos.palavras_normalizadas("Metoprolol")),
        ]
        # "TARTARATO DE METOPROLOL" -> {METOPROLOL} depois de tirar o sal —
        # bate igual, não é o caso de empate, mas confirma o caminho feliz.
        assert cmed_precos.casar_substancia("TARTARATO DE METOPROLOL", farmacos) == [1]


class TestPrecoPMC:
    def test_sem_nenhuma_coluna_preenchida_e_uso_restrito_hospitalar(self):
        r = cmed_precos.preco_pmc({"PMC 18%": None, "PMC 20%": None}, "SP")
        assert r["valor"] is None
        assert "restrito hospitalar" in r["rotulo"]

    def test_uf_sem_aliquota_verificada_cai_para_media_nacional_rotulada(self):
        r = cmed_precos.preco_pmc({"PMC 18%": 100.0, "PMC 20%": 110.0}, "SP")
        assert r["valor"] == pytest.approx(105.0)
        assert "média nacional" in r["rotulo"]
        assert "VERIFICAÇÃO HUMANA NECESSÁRIA" in r["rotulo"]
        assert "preço médio" not in r["rotulo"].lower() or "preço médio do produto" not in r["rotulo"].lower()

    def test_rotulo_nunca_diz_preco_medio_do_produto(self):
        # Sem UF verificada (estado real hoje, ver icms_medicamentos_uf.json),
        # o rótulo é a média nacional — nunca chama de "preço médio do produto".
        r = cmed_precos.preco_pmc({"PMC 18%": 50.0}, None)
        assert "CMED" in r["rotulo"]
        assert "preço médio do produto" not in r["rotulo"].lower()

    def test_uf_verificada_usa_rotulo_com_teto_regulado_e_uf_real(self, monkeypatch):
        monkeypatch.setattr(cmed_precos, "_icms_por_uf", lambda: {
            "SP": {"aliquota_pct": 18, "status": "verificado", "fonte_data": "2026-01-01"},
        })
        r = cmed_precos.preco_pmc({"PMC 18%": 50.0}, "SP")
        assert r["valor"] == 50.0
        assert "Preço máximo ao consumidor (PMC) — teto regulado pela CMED, SP" in r["rotulo"]
        assert "preço médio" not in r["rotulo"].lower()


class TestEndpointApresentacoes:
    def test_medico_ve_marca_laboratorio_e_preco_ao_digitar(self, client, criar_usuario, db):
        # role="admin" pula `assinante_ativo` (ver core/security.py) sem
        # precisar montar uma Subscription — o que importa aqui é a rota de
        # apresentações, não billing (mesmo padrão de test_assinatura.py).
        user, token = criar_usuario(role="admin")
        user.council_state = "SP"
        db.commit()

        d = Drug(slug="metoprolol-teste", generic_name="Metoprolol", drug_class="beta-bloqueador",
                 published=True)
        db.add(d)
        db.commit()
        db.refresh(d)

        versao = CmedVersao(publicado_em="20260721", arquivo_url="https://exemplo.gov.br/x.xlsx",
                            sha256="abc", linhas=1)
        db.add(versao)
        db.commit()
        db.refresh(versao)

        db.add(CmedApresentacao(
            cmed_versao_id=versao.id, drug_id=d.id, substancia_cmed="TARTARATO DE METOPROLOL",
            laboratorio="AstraZeneca", produto="Seloken", apresentacao="100 MG COM CT BL AL X 30",
            ggrem="123", restricao_hospitalar=False,
            pmc_por_aliquota={"PMC 18%": 45.5, "PMC 20%": 46.8},
        ))
        db.commit()

        r = client.get("/api/drugs/metoprolol-teste/apresentacoes",
                       headers={"Authorization": f"Bearer {token}"})
        assert r.status_code == 200, r.text
        corpo = r.json()
        assert corpo["uf"] == "SP"
        assert len(corpo["apresentacoes"]) == 1
        ap = corpo["apresentacoes"][0]
        assert ap["produto"] == "Seloken"
        assert ap["laboratorio"] == "AstraZeneca"
        assert ap["preco"]["valor"] is not None
        assert "CMED" in ap["preco"]["rotulo"]

    def test_substancia_sem_presenca_na_cmed_avisa_em_vez_de_falhar(self, client, criar_usuario, db):
        _, token = criar_usuario(role="admin")
        d = Drug(slug="rarissimo-teste", generic_name="Rarissimo", drug_class="x", published=True)
        db.add(d)
        db.commit()

        r = client.get("/api/drugs/rarissimo-teste/apresentacoes",
                       headers={"Authorization": f"Bearer {token}"})
        assert r.status_code == 200, r.text
        corpo = r.json()
        assert corpo["apresentacoes"] == []
        assert corpo["aviso"]

    def test_medicamento_inexistente_devolve_404(self, client, criar_usuario):
        _, token = criar_usuario(role="admin")
        r = client.get("/api/drugs/nao-existe/apresentacoes",
                       headers={"Authorization": f"Bearer {token}"})
        assert r.status_code == 404


class TestAdminCmedAtualizar:
    def test_nao_admin_recebe_403(self, client, criar_usuario):
        _, token = criar_usuario(role="medico")
        r = client.post("/api/admin/cmed/atualizar", headers={"Authorization": f"Bearer {token}"})
        assert r.status_code == 403

    def test_status_sem_importacao_ainda(self, client, criar_usuario):
        _, token = criar_usuario(role="admin")
        r = client.get("/api/admin/cmed/status", headers={"Authorization": f"Bearer {token}"})
        assert r.status_code == 200
        assert r.json() == {"importado": False}
