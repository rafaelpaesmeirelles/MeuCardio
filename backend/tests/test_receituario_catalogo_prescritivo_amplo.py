"""Catálogo prescritivo amplo do Receituário — qualquer apresentação real da
CMED pode ser prescrita, com ou sem `Drug` clínico correspondente.

Bug de lançamento reportado pelo Rafael: `GET /api/drugs/sugestoes` só
considerava o catálogo clínico (176 fármacos, escopo cardiologia) e excluía
explicitamente qualquer apresentação CMED sem `drug_id` vinculado — mesmo a
CMED tendo o dado real (Nebido/testosterona, Bup XL/bupropiona, sertralina
genérica, nenhum tem `Drug` clínico). Esta suíte cobre:

1. `/drugs/sugestoes` encontra candidato só-CMED (sem `Drug`), por princípio
   ativo OU marca, ignorando acento/maiúscula-minúscula.
2. O candidato só-CMED é distinguível do clínico (`tem_conteudo_clinico`).
3. `_resolver()`/`classificar()` resolvem e classificam corretamente um item
   vindo só de `cmed_apresentacao_id` — inclusive como controlado (Lista
   C5) — sem depender de `Drug`.
4. O servidor NUNCA aceita substância de texto livre do cliente: um campo
   `substancia` mandado no payload é ignorado pelo schema (Pydantic
   `extra="ignore"` por padrão), e o item fica sem classificação — nunca
   "não controlado" por omissão silenciosa.
5. `POST /api/receituario` cria a receita de ponta a ponta para um item sem
   `Drug` clínico (catálogo prescritivo amplo), inclusive com o snapshot
   preservando marca/laboratório/apresentação/preço no momento da emissão.

Mesmo padrão de `test_receituario_escopo_profissional.py`: dado sintético,
sem depender da planilha real da CMED (102k+ linhas) — mais rápido,
determinístico e sem risco de a fonte mudar de mês a mês.
"""
import pytest
from sqlalchemy import text

from app.api.drugs import sugerir_medicamentos
from app.api.receituario import ItemIn, _resolver, _carregar_regras, _item_snapshot
from app.models.cmed import CmedApresentacao, CmedVersao
from app.models.drug import Drug
from app.models.receituario import ControlledSubstance, PrescriptionType
from app.models.subscription import Subscription
from app.services.classificacao_receituario import classificar, normalizar

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
    db.add(PrescriptionType(codigo="RCE", nome="Receita de Controle Especial", ativo=True))
    # Testosterona — Lista C5 (Lei nº 9.965/2000, anabolizantes/hormônios).
    db.add(ControlledSubstance(
        nome="Testosterona", nome_normalizado=normalizar("Testosterona"),
        lista="C5", tipo_sncr="RCE", proscrita=False,
        fonte_norma="Portaria 344/98", fonte_versao="teste-v1",
    ))
    db.commit()
    yield


def _versao(db, publicado_em="20260810") -> CmedVersao:
    v = CmedVersao(publicado_em=publicado_em, arquivo_url="https://exemplo.gov.br/x.xlsx",
                    sha256="abc", linhas=3)
    db.add(v)
    db.commit()
    db.refresh(v)
    return v


def _linha_cmed(db, versao_id, *, substancia, produto, laboratorio, apresentacao,
                 drug_id=None, ggrem="1", registro=None) -> CmedApresentacao:
    linha = CmedApresentacao(
        cmed_versao_id=versao_id, drug_id=drug_id, substancia_cmed=substancia,
        laboratorio=laboratorio, produto=produto, apresentacao=apresentacao,
        ggrem=ggrem, registro=registro, tarja="Tarja Vermelha",
        pmc_por_aliquota={"PMC 18%": 42.10},
    )
    db.add(linha)
    db.commit()
    db.refresh(linha)
    return linha


class TestSugestoesCatalogoPrescritivoAmplo:
    """`GET /api/drugs/sugestoes` (chamado direto — função pura de FastAPI,
    `Depends` não avaliados fora da rota) encontra candidato real da CMED
    mesmo sem `Drug` clínico, e não confunde os dois tipos."""

    def test_sertralina_generico_sem_drug_clinico(self, db, criar_usuario):
        user, _ = criar_usuario()
        versao = _versao(db)
        _linha_cmed(db, versao.id, substancia="CLORIDRATO DE SERTRALINA",
                    produto="ZOLOFT", laboratorio="PFIZER",
                    apresentacao="50 MG COM REV CT BL AL PLAS INC X 30")

        resultado = sugerir_medicamentos(q="sertralina", db=db, user=user)

        assert len(resultado) >= 1
        item = resultado[0]
        assert item["slug"] is None
        assert item["tem_conteudo_clinico"] is False
        assert item["cmed_apresentacao_id"] is not None
        assert item["brand_name"] == "ZOLOFT"
        assert item["manufacturer"] == "PFIZER"
        assert "sertralina" in item["substancia"].lower()

    def test_bup_xl_por_marca(self, db, criar_usuario):
        user, _ = criar_usuario()
        versao = _versao(db)
        _linha_cmed(db, versao.id, substancia="CLORIDRATO DE BUPROPIONA",
                    produto="BUP XL", laboratorio="EUROFARMA",
                    apresentacao="150 MG COM REV LIB PROL CT BL AL AL X 30")

        resultado = sugerir_medicamentos(q="Bup XL", db=db, user=user)

        assert any(r["brand_name"] == "BUP XL" for r in resultado)

    @pytest.mark.parametrize("termo", [
        "bupropiona", "BUPROPIONA", "Bupropiona", "cloridrato de bupropiona",
        "bupropióna",  # acento errado de propósito — precisa achar mesmo assim
    ])
    def test_bupropiona_generico_ignora_acento_e_caixa(self, db, criar_usuario, termo):
        user, _ = criar_usuario()
        versao = _versao(db)
        _linha_cmed(db, versao.id, substancia="CLORIDRATO DE BUPROPIONA",
                    produto="BUP XL", laboratorio="EUROFARMA",
                    apresentacao="150 MG COM REV LIB PROL CT BL AL AL X 30")

        resultado = sugerir_medicamentos(q=termo, db=db, user=user)

        assert any("bupropiona" in r["substancia"].lower() for r in resultado), (termo, resultado)

    def test_nebido_por_marca(self, db, criar_usuario):
        user, _ = criar_usuario()
        versao = _versao(db)
        _linha_cmed(db, versao.id, substancia="UNDECILATO DE TESTOSTERONA",
                    produto="NEBIDO", laboratorio="GRÜNENTHAL",
                    apresentacao="1000 MG SOL INJ CT FA VD TRANS X 4 ML")

        resultado = sugerir_medicamentos(q="Nebido", db=db, user=user)

        assert any(r["brand_name"] == "NEBIDO" for r in resultado)

    def test_testosterona_generico(self, db, criar_usuario):
        user, _ = criar_usuario()
        versao = _versao(db)
        _linha_cmed(db, versao.id, substancia="TESTOSTERONA",
                    produto="ANDROGEL", laboratorio="BESINS",
                    apresentacao="50 MG GEL CT SACHE AL X 30 X 5 G")
        _linha_cmed(db, versao.id, substancia="UNDECILATO DE TESTOSTERONA",
                    produto="NEBIDO", laboratorio="GRÜNENTHAL",
                    apresentacao="1000 MG SOL INJ CT FA VD TRANS X 4 ML")

        resultado = sugerir_medicamentos(q="testosterona", db=db, user=user)

        nomes = {r["brand_name"] for r in resultado}
        assert "ANDROGEL" in nomes
        assert "NEBIDO" in nomes

    def test_undecilato_de_testosterona_generico_completo(self, db, criar_usuario):
        user, _ = criar_usuario()
        versao = _versao(db)
        _linha_cmed(db, versao.id, substancia="UNDECILATO DE TESTOSTERONA",
                    produto="NEBIDO", laboratorio="GRÜNENTHAL",
                    apresentacao="1000 MG SOL INJ CT FA VD TRANS X 4 ML")

        resultado = sugerir_medicamentos(q="undecilato de testosterona", db=db, user=user)

        assert any(r["brand_name"] == "NEBIDO" for r in resultado)

    def test_combinacao_de_dose_fixa_sem_drug_clinico_nao_aparece_como_sugestao(self, db, criar_usuario):
        """Item multi-substância (";" na CMED) sem `Drug` clínico não pode
        virar sugestão prescritível: `classificar()` só lê UMA substância
        por item, e uma combinação com componente controlado classificaria
        como "comum" em silêncio. Mesma exclusão que `cmed_precos.
        casar_substancia` já aplica do lado do casamento com `Drug`."""
        user, _ = criar_usuario()
        versao = _versao(db)
        _linha_cmed(db, versao.id, substancia="CODEINA;PARACETAMOL",
                    produto="COMBO TESTE", laboratorio="LAB TESTE",
                    apresentacao="30 MG COM CT BL AL X 20")

        resultado = sugerir_medicamentos(q="combo teste", db=db, user=user)

        assert resultado == []

    def test_candidato_clinico_continua_distinguivel_do_so_cmed(self, db, criar_usuario):
        """Regressão: fármaco com `Drug` clínico continua vindo com
        `tem_conteudo_clinico=True` e `slug` preenchido — a ampliação não
        derruba o catálogo aprofundado existente."""
        user, _ = criar_usuario()
        d = Drug(slug="losartana-potassica-teste", generic_name="Losartana potássica",
                 drug_class="BRA", published=True)
        db.add(d)
        db.commit()
        db.refresh(d)
        versao = _versao(db)
        _linha_cmed(db, versao.id, substancia="LOSARTANA POTASSICA",
                    produto="COZAAR", laboratorio="MSD",
                    apresentacao="50 MG COM CT BL AL X 30", drug_id=d.id)

        resultado = sugerir_medicamentos(q="losartana", db=db, user=user)

        clinico = next(r for r in resultado if r["brand_name"] == "COZAAR")
        assert clinico["tem_conteudo_clinico"] is True
        assert clinico["slug"] == d.slug


class TestResolucaoEClassificacaoSemDrugClinico:
    """`_resolver()`/`classificar()` — o núcleo que destrava a classificação
    de controlados pra qualquer item do catálogo prescritivo amplo."""

    def test_item_so_cmed_resolve_substancia_e_classifica_controlado(self, db):
        versao = _versao(db)
        linha = _linha_cmed(db, versao.id, substancia="TESTOSTERONA",
                             produto="ANDROGEL", laboratorio="BESINS",
                             apresentacao="50 MG GEL CT SACHE AL X 30 X 5 G")

        item_in = ItemIn(cmed_apresentacao_id=linha.id, descricao="ANDROGEL",
                          brand_name="ANDROGEL", manufacturer="BESINS")
        resolvidos = _resolver(db, [item_in])
        assert resolvidos[0].substancia == "TESTOSTERONA"
        assert resolvidos[0].drug_id is None
        assert resolvidos[0].cmed_apresentacao_id == linha.id

        subs, regras, _versao_listas = _carregar_regras(db)
        resultado = classificar(resolvidos, subs, regras)

        assert not resultado.recusados
        assert len(resultado.documentos) == 1
        doc = resultado.documentos[0]
        assert doc.tipo == "RCE"
        assert doc.itens[0].lista == "C5"

    def test_undecilato_de_testosterona_nebido_classifica_como_c5_rce(self, db):
        """Bug real reproduzido em 09/08/2026: a linha CMED real de Nebido
        ("UNDECILATO DE TESTOSTERONA") não normalizava para "testosterona" —
        o éster não estava na lista de prefixos removidos por `normalizar()`
        — e caía silenciosamente em TIPO_COMUM, sem exigir Receita de
        Controle Especial (Lista C5, Lei nº 9.965/2000, anabolizante).
        Nebido é um dos 3 medicamentos de teste de aceitação pedidos pelo
        Rafael; esta é a cobertura de ponta a ponta que faltava — as demais
        (`test_nebido_por_marca` etc.) só cobriam a sugestão por nome, nunca
        a classificação regulatória."""
        versao = _versao(db)
        linha = _linha_cmed(db, versao.id, substancia="UNDECILATO DE TESTOSTERONA",
                             produto="NEBIDO", laboratorio="GRÜNENTHAL",
                             apresentacao="1000 MG SOL INJ CT FA VD TRANS X 4 ML")

        item_in = ItemIn(cmed_apresentacao_id=linha.id, descricao="NEBIDO",
                          brand_name="NEBIDO", manufacturer="GRÜNENTHAL")
        resolvidos = _resolver(db, [item_in])
        assert resolvidos[0].substancia == "UNDECILATO DE TESTOSTERONA"

        subs, regras, _versao_listas = _carregar_regras(db)
        resultado = classificar(resolvidos, subs, regras)

        assert not resultado.recusados
        assert len(resultado.documentos) == 1
        doc = resultado.documentos[0]
        assert doc.tipo == "RCE", (
            "Nebido (undecilato de testosterona, Lista C5) precisa exigir "
            "Receita de Controle Especial — caiu em "
            f"{doc.tipo!r} em vez de RCE"
        )
        assert doc.itens[0].lista == "C5"

    def test_item_so_cmed_nao_controlado_vira_comum(self, db):
        versao = _versao(db)
        linha = _linha_cmed(db, versao.id, substancia="CLORIDRATO DE SERTRALINA",
                             produto="ZOLOFT", laboratorio="PFIZER",
                             apresentacao="50 MG COM REV CT BL AL PLAS INC X 30")

        item_in = ItemIn(cmed_apresentacao_id=linha.id, descricao="ZOLOFT")
        resolvidos = _resolver(db, [item_in])
        subs, regras, _ = _carregar_regras(db)
        resultado = classificar(resolvidos, subs, regras)

        assert not resultado.recusados
        assert resultado.documentos[0].tipo == "COMUM"

    def test_cmed_apresentacao_id_inexistente_nao_resolve_substancia(self, db):
        """id que não existe no banco — nunca vira classificação inventada."""
        item_in = ItemIn(cmed_apresentacao_id=999999, descricao="Item fantasma")
        resolvidos = _resolver(db, [item_in])
        assert resolvidos[0].substancia is None
        assert resolvidos[0].cmed_apresentacao_id is None

    def test_substancia_de_texto_livre_do_cliente_e_ignorada_pelo_schema(self, db):
        """Regra de segurança central: `ItemIn` não declara campo `substancia`
        — qualquer coisa que o cliente mande com esse nome é descartada pelo
        Pydantic antes de chegar em `_resolver`. Nunca vira "não controlado"
        por omissão: o item fica sem substância resolvida, o que força
        pendência de revisão humana, não uma classificação silenciosa."""
        item_in = ItemIn(**{
            "descricao": "Item suspeito", "apresentacao": "1 cp",
            "substancia": "Testosterona",  # tentativa de burlar a classificação
            "lista": "COMUM",              # idem — também não existe no schema
        })
        assert "substancia" not in item_in.model_dump()
        assert "lista" not in item_in.model_dump()

        resolvidos = _resolver(db, [item_in])
        assert resolvidos[0].substancia is None

        subs, regras, _ = _carregar_regras(db)
        resultado = classificar(resolvidos, subs, regras)

        assert resultado.exige_revisao is True
        assert resultado.documentos[0].pendencias, "item sem substância precisa gerar pendência, não passar silencioso"
        assert not resultado.documentos[0].itens[0].lista, "nunca herda lista sem substância resolvida de verdade"

    def test_snapshot_preserva_dados_do_catalogo_prescritivo_amplo(self, db):
        """Item 4: o que foi impresso não muda se a CMED for reimportada
        depois — `_item_snapshot` grava os valores no momento da resolução,
        não uma referência viva à linha da CMED."""
        versao = _versao(db)
        linha = _linha_cmed(db, versao.id, substancia="TESTOSTERONA",
                             produto="ANDROGEL", laboratorio="BESINS",
                             apresentacao="50 MG GEL CT SACHE AL X 30 X 5 G")
        item_in = ItemIn(
            cmed_apresentacao_id=linha.id, descricao="ANDROGEL",
            brand_name="ANDROGEL", manufacturer="BESINS", ggrem="1",
            pmc_snapshot=99.90, uf="SP", cmed_version=versao.publicado_em,
        )
        resolvido = _resolver(db, [item_in])[0]
        snapshot = _item_snapshot(resolvido)

        assert snapshot["substancia"] == "TESTOSTERONA"
        assert snapshot["brand_name"] == "ANDROGEL"
        assert snapshot["manufacturer"] == "BESINS"
        assert snapshot["pmc_snapshot"] == 99.90
        assert snapshot["cmed_apresentacao_id"] == linha.id
        assert snapshot["drug_id"] is None
        assert snapshot["tem_conteudo_clinico"] is False
        assert snapshot["cmed_snapshot"]["produto"] == "ANDROGEL"

        # Reimportar a CMED (mudar a linha original) não pode alterar o
        # snapshot já gravado.
        linha.produto = "OUTRO PRODUTO DEPOIS DE REIMPORTAR"
        linha.pmc_por_aliquota = {"PMC 18%": 1.0}
        db.commit()
        assert snapshot["brand_name"] == "ANDROGEL"
        assert snapshot["pmc_snapshot"] == 99.90


class TestFluxoHttpDePontaAPonta:
    """`POST /api/receituario/classificar` e `POST /api/receituario` pela
    rota real, com token/assinatura — prova que a rota HTTP (não só a
    função interna) aceita o catálogo prescritivo amplo."""

    def test_classificar_previa_via_http_para_item_so_cmed_controlado(self, client, db, criar_usuario):
        user, token = criar_usuario()
        user.council_name = "CRM"
        db.commit()
        _subscribe(db, user.id)
        versao = _versao(db)
        linha = _linha_cmed(db, versao.id, substancia="TESTOSTERONA",
                             produto="ANDROGEL", laboratorio="BESINS",
                             apresentacao="50 MG GEL CT SACHE AL X 30 X 5 G")

        payload = {
            "destinatario": {"nome": "Paciente de Teste"},
            "itens": [{
                "cmed_apresentacao_id": linha.id, "descricao": "ANDROGEL",
                "brand_name": "ANDROGEL", "manufacturer": "BESINS",
                "posologia": "conforme orientação", "apresentacao": "1 aplicação/dia",
            }],
        }
        r = client.post("/api/receituario/classificar", headers=_headers(token), json=payload)
        assert r.status_code == 200, r.text
        corpo = r.json()
        assert corpo["documentos"][0]["tipo"] == "RCE"
        assert not corpo["recusados"]

    def test_criar_receita_completa_sem_drug_clinico_medicamento_comum(self, client, db, criar_usuario):
        """Medicamento sem `Drug` clínico e não controlado pode ser
        prescrito de ponta a ponta (201), sem passar pelas exigências extras
        de Receita de Controle Especial (fora do escopo desta tarefa)."""
        user, token = criar_usuario()
        user.council_name = "CRM"
        db.commit()
        _subscribe(db, user.id)
        versao = _versao(db)
        linha = _linha_cmed(db, versao.id, substancia="CLORIDRATO DE SERTRALINA",
                             produto="ZOLOFT", laboratorio="PFIZER",
                             apresentacao="50 MG COM REV CT BL AL PLAS INC X 30")

        payload = {
            "destinatario": {"nome": "Paciente de Teste"},
            "itens": [{
                "cmed_apresentacao_id": linha.id, "descricao": "ZOLOFT",
                "brand_name": "ZOLOFT", "manufacturer": "PFIZER",
                "posologia": "1 cp ao dia", "apresentacao": "50 mg — comprimido",
                "quantidade": "30 comprimidos", "quantidade_extenso": "trinta comprimidos",
            }],
        }
        r = client.post("/api/receituario", headers=_headers(token), json=payload)
        assert r.status_code == 201, r.text
        corpo = r.json()
        assert corpo["documentos"][0]["tipo"] == "COMUM"

        # Confere no histórico que o item veio sem `Drug` clínico e com o
        # snapshot correto — não é só a resposta síncrona que precisa bater.
        r2 = client.get(f"/api/receituario/{corpo['prescricao_id']}", headers=_headers(token))
        assert r2.status_code == 200, r2.text
        original = r2.json()["itens_originais"][0]
        assert original["drug_slug"] is None
        assert original["cmed_apresentacao_id"] == linha.id

    def test_criar_receita_completa_controlada_c5_sem_drug_clinico(self, client, db, criar_usuario):
        """Fim a fim real: Lista C5 (testosterona) sem `Drug` clínico,
        cumprindo os requisitos extra de Receita de Controle Especial
        (Lei nº 9.965/2000) — prova que a classificação de controlado
        funciona de verdade para o catálogo prescritivo amplo, não só a
        função pura isolada."""
        user, token = criar_usuario()
        user.council_name = "CRM"
        user.council_number = "123456"
        user.council_state = "SP"
        user.cpf = "11144477735"
        user.practice_street = "Rua Teste"
        user.practice_number = "100"
        user.practice_city = "São Paulo"
        user.practice_state = "SP"
        user.practice_phone = "11999999999"
        db.commit()
        _subscribe(db, user.id)
        versao = _versao(db)
        linha = _linha_cmed(db, versao.id, substancia="TESTOSTERONA",
                             produto="ANDROGEL", laboratorio="BESINS",
                             apresentacao="50 MG GEL CT SACHE AL X 30 X 5 G")

        payload = {
            "destinatario": {
                "nome": "Paciente de Teste", "endereco": "Rua do Paciente, 50, São Paulo/SP",
                "documento": "22233344456",
            },
            "cid": "E29.1",
            "itens": [{
                "cmed_apresentacao_id": linha.id, "descricao": "ANDROGEL",
                "brand_name": "ANDROGEL", "manufacturer": "BESINS",
                "posologia": "1 sachê ao dia", "apresentacao": "50 mg — gel",
                "quantidade": "30 sachês", "quantidade_extenso": "trinta sachês",
            }],
        }
        r = client.post("/api/receituario", headers=_headers(token), json=payload)
        assert r.status_code == 201, r.text
        corpo = r.json()
        assert corpo["documentos"][0]["tipo"] == "RCE"
