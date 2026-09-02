"""Contrato da busca agregada usada pela experiência “Tudo com Tudo”."""

import pytest
from sqlalchemy import text

from app.models.checklist import DischargeChecklist
from app.models.clinical_case import ClinicalCase
from app.models.cmed import CmedApresentacao, CmedVersao
from app.models.content import Document
from app.models.drug import Drug
from app.models.emergency import EmergencyProtocol
from app.models.evidence import EvidenceRecord
from app.models.gallery import GalleryImage
from app.models.lab_test import LabTest
from app.models.patient_material import PatientMaterial
from app.models.specialty_guide import SpecialtyDisease, SymptomTriageGuide
from app.models.study import ScientificStudy
from app.models.study_track import StudyTrack
from app.services.clinical_text import clinical_text_without_internal_overrides


TABELAS_DA_BUSCA = (
    "document_revisions",
    "documents",
    "gallery_images",
    "lab_tests",
    "evidence_records",
    "scientific_studies",
    "drugs",
    "clinical_cases",
    "study_tracks",
    "discharge_checklists",
    "patient_materials",
    "emergency_protocols",
    "specialty_diseases",
    "symptom_triage_guides",
    "cmed_apresentacoes",
    "cmed_versoes",
)


@pytest.fixture(autouse=True)
def _conteudo_de_busca_limpo(db):
    db.execute(text(f"TRUNCATE {', '.join(TABELAS_DA_BUSCA)} RESTART IDENTITY CASCADE"))
    db.commit()
    yield
    db.execute(text(f"TRUNCATE {', '.join(TABELAS_DA_BUSCA)} RESTART IDENTITY CASCADE"))
    db.commit()


def _headers(criar_usuario):
    _, token = criar_usuario(role="admin")
    return {"Authorization": f"Bearer {token}"}


def _documento(slug: str, title: str, *, published: bool = True) -> Document:
    return Document(
        slug=slug,
        title=title,
        kind="farmacologia",
        theme="Hipertensão arterial",
        summary="Conteúdo clínico sobre olmesartana.",
        body_md="Características, indicações e posologia.",
        review_status="revisado" if published else "pendente_revisao",
        published=published,
    )


def test_busca_preserva_frentes_ano_e_oculta_nao_publicado(client, db, criar_usuario):
    db.add_all([
        _documento("olmesartana-caracteristicas-teste", "Olmesartana: características"),
        _documento(
            "olmesartana-rascunho-teste",
            "Olmesartana: conteúdo ainda não publicado",
            published=False,
        ),
        EvidenceRecord(
            slug="olmesartana-evidencia-teste",
            statement="Olmesartana é uma opção terapêutica para hipertensão arterial.",
            recommendation_class="I",
            evidence_level="A",
            society="Sociedade de teste",
            year=2024,
            guideline_title="Diretriz de teste sobre olmesartana",
            reference="Referência de teste",
            theme="Hipertensão arterial",
            review_status="revisado",
            published=True,
        ),
        ScientificStudy(
            slug="olmesartana-estudo-teste",
            title="Estudo clínico de olmesartana",
            study_type="ensaio_clinico",
            journal="Periódico de teste",
            year=2022,
            summary="Avaliação da olmesartana.",
            key_findings="Achados clínicos da olmesartana.",
            clinical_implications="Implicações terapêuticas.",
            theme="Hipertensão arterial",
            review_status="revisado",
            published=True,
        ),
    ])
    db.commit()

    resposta = client.get(
        "/api/search",
        params={"q": "olmesartana"},
        headers=_headers(criar_usuario),
    )

    assert resposta.status_code == 200
    corpo = resposta.json()
    por_slug = {item["slug"]: item for item in corpo["results"]}
    assert set(por_slug) == {
        "olmesartana-caracteristicas-teste",
        "olmesartana-evidencia-teste",
        "olmesartana-estudo-teste",
    }
    assert por_slug["olmesartana-caracteristicas-teste"]["frente"] == "documento"
    assert por_slug["olmesartana-caracteristicas-teste"]["ano"] is None
    assert por_slug["olmesartana-evidencia-teste"]["frente"] == "evidencia"
    assert por_slug["olmesartana-evidencia-teste"]["ano"] == 2024
    assert por_slug["olmesartana-estudo-teste"]["frente"] == "estudo"
    assert por_slug["olmesartana-estudo-teste"]["ano"] == 2022
    assert corpo["por_frente"] == {"documento": 1, "evidencia": 1, "estudo": 1}
    assert corpo["total"] == 3


def test_busca_tudo_com_tudo_encontra_as_treze_frentes_publicadas(client, db, criar_usuario):
    sentinela = "cardioconexao"
    db.add_all([
        _documento(f"{sentinela}-documento", f"{sentinela} documento"),
        GalleryImage(
            slug=f"{sentinela}-galeria", title=f"{sentinela} galeria",
            modality="ecocardiograma", theme="Tema sentinela", findings="Achado sentinela",
            file_path="teste.png", source_name="Fonte de teste", source_url="https://example.test",
            license="CC0", attribution="Teste", review_status="revisado", published=True,
        ),
        LabTest(
            slug=f"{sentinela}-exame", name=f"{sentinela} exame", category="laboratorial",
            what_it_measures="Medida sentinela", indications="Indicação sentinela",
            interpretation="Interpretação sentinela", theme="Tema sentinela",
            review_status="revisado", published=True,
        ),
        EvidenceRecord(
            slug=f"{sentinela}-evidencia", statement=f"{sentinela} evidência",
            recommendation_class="I", evidence_level="A", society="Sociedade de teste",
            year=2026, guideline_title="Diretriz sentinela", reference="Referência sentinela",
            theme="Tema sentinela", review_status="revisado", published=True,
        ),
        ScientificStudy(
            slug=f"{sentinela}-estudo", title=f"{sentinela} estudo", study_type="ensaio_clinico",
            journal="Periódico de teste", year=2026, summary="Resumo sentinela",
            key_findings="Achado sentinela", clinical_implications="Implicação sentinela",
            theme="Tema sentinela", review_status="revisado", published=True,
        ),
        Drug(
            slug=f"{sentinela}-medicamento", generic_name=f"{sentinela} medicamento",
            drug_class="Classe sentinela", review_status="revisado", published=True,
        ),
        ClinicalCase(
            slug=f"{sentinela}-caso", titulo=f"{sentinela} caso", tema="Tema sentinela",
            nivel="intermediario", enunciado="Enunciado sentinela", pergunta="Pergunta sentinela?",
            opcoes=["A", "B"], resposta_correta=0, explicacao="Explicação sentinela",
            review_status="revisado", published=True,
        ),
        StudyTrack(
            slug=f"{sentinela}-trilha", titulo=f"{sentinela} trilha", tema="Tema sentinela",
            objetivo="Objetivo sentinela", etapas=[], review_status="revisado", published=True,
        ),
        DischargeChecklist(
            slug=f"{sentinela}-checklist", condicao=f"{sentinela} checklist",
            resumo="Resumo sentinela", theme="Tema sentinela", itens=[],
            review_status="revisado", published=True,
        ),
        PatientMaterial(
            slug=f"{sentinela}-material", titulo=f"{sentinela} material",
            tema="Tema sentinela", resumo="Resumo sentinela", secoes=[],
            review_status="revisado", published=True,
        ),
        EmergencyProtocol(
            slug=f"{sentinela}-emergencia", titulo=f"{sentinela} emergência",
            gatilho="Gatilho sentinela", documento_slug=f"{sentinela}-documento",
            review_status="revisado", published=True,
        ),
        SpecialtyDisease(
            slug=f"{sentinela}-doenca", name=f"{sentinela} doença", area="cardiologia",
            category="categoria sentinela", summary="Resumo sentinela", completeness="completo",
            review_status="revisado", published=True,
        ),
        SymptomTriageGuide(
            slug=f"{sentinela}-triagem", name=f"{sentinela} triagem",
            areas=["cardiologia"], summary="Resumo sentinela", questions=[],
            review_status="revisado", published=True,
        ),
    ])
    db.commit()

    resposta = client.get(
        "/api/search", params={"q": sentinela, "limit": 100}, headers=_headers(criar_usuario),
    )

    assert resposta.status_code == 200
    corpo = resposta.json()
    assert corpo["total"] == 13
    assert corpo["count"] == 13
    assert set(corpo["por_frente"]) == {
        "documento", "galeria", "exame", "evidencia", "estudo", "medicamento",
        "caso_clinico", "trilha", "checklist", "material_paciente", "emergencia",
        "doenca", "triagem_sintoma",
    }


def test_filtro_de_frente_e_aplicado_antes_do_limite(client, db, criar_usuario):
    db.add_all([
        _documento(
            f"olmesartana-documento-dominante-{indice}",
            "Olmesartana olmesartana olmesartana",
        )
        for indice in range(3)
    ])
    db.add(ScientificStudy(
        slug="olmesartana-unico-estudo",
        title="Olmesartana em estudo",
        study_type="coorte",
        journal="Periódico de teste",
        year=2023,
        summary="Olmesartana.",
        key_findings="Achado clínico.",
        clinical_implications="Implicação clínica.",
        theme="Hipertensão arterial",
        review_status="revisado",
        published=True,
    ))
    db.commit()

    resposta = client.get(
        "/api/search",
        params={"q": "olmesartana", "frente": "estudo", "limit": 1},
        headers=_headers(criar_usuario),
    )

    assert resposta.status_code == 200
    resultados = resposta.json()["results"]
    assert len(resultados) == 1
    assert resultados[0]["frente"] == "estudo"
    assert resultados[0]["slug"] == "olmesartana-unico-estudo"
    assert resultados[0]["ano"] == 2023


def test_busca_inclui_calculadoras_e_nao_trata_curingas_como_conteudo(client, db, criar_usuario):
    db.add(_documento("documento-sem-coringa", "Conteúdo clínico comum"))
    db.commit()
    headers = _headers(criar_usuario)

    calculadora = client.get(
        "/api/search", params={"q": "CHA2DS2-VASc"}, headers=headers,
    )
    assert calculadora.status_code == 200
    itens = calculadora.json()["results"]
    assert any(item["frente"] == "calculadora" and item["slug"] == "cha2ds2-vasc" for item in itens)

    curingas = client.get("/api/search", params={"q": "%%"}, headers=headers)
    assert curingas.status_code == 200
    assert curingas.json()["count"] == 0


def test_calculadoras_respeitam_limite_offset_e_nao_duplicam_paginas(
    client, db, criar_usuario,
):
    db.add(_documento("score-clinico-documento", "Score clínico publicado"))
    db.commit()
    headers = _headers(criar_usuario)
    primeira = client.get(
        "/api/search",
        params={"q": "score", "frente": "calculadora", "limit": 1},
        headers=headers,
    )
    assert primeira.status_code == 200
    corpo_1 = primeira.json()
    assert corpo_1["count"] == 1
    assert corpo_1["total"] >= 2
    assert corpo_1["next_offset"] == 1

    segunda = client.get(
        "/api/search",
        params={
            "q": "score", "frente": "calculadora", "limit": 1,
            "offset": corpo_1["next_offset"],
        },
        headers=headers,
    )
    assert segunda.status_code == 200
    corpo_2 = segunda.json()
    assert corpo_2["count"] == 1
    assert corpo_2["results"][0]["slug"] != corpo_1["results"][0]["slug"]

    transversal = client.get(
        "/api/search", params={"q": "score", "limit": 1}, headers=headers,
    )
    assert transversal.status_code == 200
    assert transversal.json()["count"] == 1
    assert len(transversal.json()["results"]) == 1


def test_busca_literal_e_fallback_apenas_para_fragmento_sem_lexema(
    client, db, criar_usuario,
):
    db.add(_documento("sentinelaomega-documento", "Sentinelaomega cardiovascular"))
    db.commit()

    resposta = client.get(
        "/api/search", params={"q": "nelaome"}, headers=_headers(criar_usuario),
    )

    assert resposta.status_code == 200
    assert [item["slug"] for item in resposta.json()["results"]] == [
        "sentinelaomega-documento"
    ]


def test_limite_padrao_e_validado_pela_api(client, db, criar_usuario):
    db.add_all([
        _documento(
            f"olmesartana-limite-{indice:02d}",
            f"Olmesartana item {indice:02d}",
        )
        for indice in range(61)
    ])
    db.commit()
    headers = _headers(criar_usuario)

    resposta_padrao = client.get(
        "/api/search", params={"q": "olmesartana"}, headers=headers,
    )
    assert resposta_padrao.status_code == 200
    assert resposta_padrao.json()["count"] == 60
    assert resposta_padrao.json()["next_offset"] == 60

    segunda_pagina = client.get(
        "/api/search", params={"q": "olmesartana", "offset": 60}, headers=headers,
    )
    assert segunda_pagina.status_code == 200
    assert segunda_pagina.json()["count"] == 1
    assert segunda_pagina.json()["next_offset"] is None
    primeira_pagina_slugs = {item["slug"] for item in resposta_padrao.json()["results"]}
    assert segunda_pagina.json()["results"][0]["slug"] not in primeira_pagina_slugs

    assert client.get(
        "/api/search", params={"q": "olmesartana", "limit": 0}, headers=headers,
    ).status_code == 422
    assert client.get(
        "/api/search", params={"q": "olmesartana", "limit": 101}, headers=headers,
    ).status_code == 422


def test_estudos_e_exames_buscam_sem_acento_e_paginam_sem_ocultar_itens(
    client, db, criar_usuario,
):
    db.add_all([
        ScientificStudy(
            slug="insuficiencia-cardiaca-estudo-a",
            title="Insuficiência cardíaca — estudo A",
            study_type="ensaio_clinico",
            journal="Periódico de teste",
            year=2025,
            summary="Estudo sentinela A.",
            key_findings="Achado A.",
            clinical_implications="Implicação A.",
            theme="Insuficiência cardíaca",
            review_status="revisado",
            published=True,
        ),
        ScientificStudy(
            slug="insuficiencia-cardiaca-estudo-b",
            title="Insuficiência cardíaca — estudo B",
            study_type="metanalise",
            journal="Periódico de teste",
            year=2026,
            summary="Estudo sentinela B.",
            key_findings="Achado B.",
            clinical_implications="Implicação B.",
            theme="Insuficiência cardíaca",
            review_status="revisado",
            published=True,
        ),
        LabTest(
            slug="acido-urico-exame-a",
            name="Ácido úrico — exame A",
            category="laboratorial",
            what_it_measures="Concentração de ácido úrico.",
            indications="Avaliação metabólica.",
            interpretation="Interpretação A.",
            theme="Metabolismo",
            review_status="revisado",
            published=True,
        ),
        LabTest(
            slug="acido-urico-exame-b",
            name="Ácido úrico — exame B",
            category="laboratorial",
            what_it_measures="Concentração de ácido úrico.",
            indications="Avaliação metabólica.",
            interpretation="Interpretação B.",
            theme="Metabolismo",
            review_status="revisado",
            published=True,
        ),
    ])
    db.commit()
    headers = _headers(criar_usuario)

    estudos_1 = client.get(
        "/api/studies",
        params={"q": "insuficiencia", "limit": 1, "offset": 0},
        headers=headers,
    )
    estudos_2 = client.get(
        "/api/studies",
        params={"q": "insuficiencia", "limit": 1, "offset": 1},
        headers=headers,
    )
    assert estudos_1.status_code == estudos_2.status_code == 200
    assert estudos_1.json()["total"] == estudos_2.json()["total"] == 2
    assert estudos_1.json()["items"][0]["slug"] != estudos_2.json()["items"][0]["slug"]

    exames_1 = client.get(
        "/api/lab-tests",
        params={"q": "acido urico", "limit": 1, "offset": 0},
        headers=headers,
    )
    exames_2 = client.get(
        "/api/lab-tests",
        params={"q": "acido urico", "limit": 1, "offset": 1},
        headers=headers,
    )
    assert exames_1.status_code == exames_2.status_code == 200
    assert exames_1.json()["total"] == exames_2.json()["total"] == 2
    assert exames_1.json()["next_offset"] == 1
    assert exames_2.json()["next_offset"] is None
    assert exames_1.json()["items"][0]["slug"] != exames_2.json()["items"][0]["slug"]

    assert client.get(
        "/api/studies", params={"q": "%%"}, headers=headers,
    ).json()["total"] == 0
    assert client.get(
        "/api/lab-tests", params={"q": "__"}, headers=headers,
    ).json()["total"] == 0


def test_nome_comercial_cmed_encontra_medicamento_canonico_em_todas_as_buscas(
    client, db, criar_usuario,
):
    drug = Drug(
        slug="anlodipino-marca-cmed-teste",
        generic_name="Anlodipino",
        brand_names=["Norvasc"],
        drug_class="Bloqueador do canal de cálcio",
        review_status="revisado",
        published=True,
    )
    db.add(drug)
    db.flush()
    version = CmedVersao(
        publicado_em="20260901",
        arquivo_url="https://example.test/cmed.xlsx",
        sha256="a" * 64,
        linhas=2,
    )
    db.add(version)
    db.flush()
    db.add(CmedApresentacao(
        cmed_versao_id=version.id,
        drug_id=drug.id,
        substancia_cmed="BESILATO DE ANLODIPINO",
        laboratorio="Laboratório de teste",
        produto="Pressat XR",
        apresentacao="5 MG COM CT BL AL PLAS TRANS X 30",
        ggrem="0000000000000",
        pmc_por_aliquota={},
    ))
    db.add(CmedApresentacao(
        cmed_versao_id=version.id,
        drug_id=drug.id,
        substancia_cmed="BESILATO DE ANLODIPINO",
        laboratorio="Outro laboratório de teste",
        produto="NORVASC",
        apresentacao="5 MG COM CT BL AL PLAS TRANS X 60",
        ggrem="0000000000001",
        pmc_por_aliquota={},
    ))
    db.commit()
    headers = _headers(criar_usuario)

    for termo in ("Norvasc", "pressat", "PRESSAT XR"):
        global_response = client.get(
            "/api/search", params={"q": termo}, headers=headers,
        )
        assert global_response.status_code == 200
        assert [item["slug"] for item in global_response.json()["results"]] == [drug.slug]

        catalog_response = client.get(
            "/api/drugs", params={"q": termo}, headers=headers,
        )
        assert catalog_response.status_code == 200
        assert [item["slug"] for item in catalog_response.json()["items"]] == [drug.slug]
        assert {"Norvasc", "Pressat XR"}.issubset(
            set(catalog_response.json()["items"][0]["commercial_names"])
        )
        assert sum(
            nome.casefold() == "norvasc"
            for nome in catalog_response.json()["items"][0]["commercial_names"]
        ) == 1


def test_doenca_exata_ou_alias_inequivoco_abre_pela_definicao(
    client, db, criar_usuario,
):
    disease = SpecialtyDisease(
        slug="fibrilacao-atrial-teste",
        name="Fibrilação atrial",
        aliases=["FA"],
        area="arritmias",
        category="taquiarritmia supraventricular",
        summary="Taquiarritmia supraventricular caracterizada por ativação atrial desorganizada.",
        completeness="completo",
        review_status="revisado",
        published=True,
    )
    db.add(disease)
    db.commit()
    headers = _headers(criar_usuario)

    for termo in ("fibrilacao atrial", "FA"):
        response = client.get("/api/search", params={"q": termo}, headers=headers)
        assert response.status_code == 200
        primary = response.json()["primary_disease"]
        assert primary["slug"] == disease.slug
        assert primary["name"] == disease.name
        assert primary["summary"].startswith("Taquiarritmia supraventricular")


def test_definicao_remove_blocos_internos_legados_do_intelligence(
    client, db, criar_usuario,
):
    definicao = "Fibrilação atrial é uma arritmia supraventricular com ativação atrial desorganizada."
    blocos = """<!-- corvia-intelligence:diretriz-a:plain:start -->
**Atualização CorVIA Intelligence:** conteúdo terapêutico que não é definição.
<!-- corvia-intelligence:diretriz-a:plain:end -->

<!-- corvia-intelligence:diretriz-b:plain:start -->
**Atualização CorVIA Intelligence:** outra recomendação clínica.
<!-- corvia-intelligence:diretriz-b:plain:end -->"""
    db.add(SpecialtyDisease(
        slug="fibrilacao-atrial-legado-intelligence",
        name="Fibrilação atrial",
        aliases=["FA"],
        area="arritmias",
        category="taquiarritmia supraventricular",
        summary=f"{blocos}\n\n{definicao}",
        review_status="revisado",
        published=True,
    ))
    db.commit()

    response = client.get(
        "/api/search", params={"q": "fibrilacao atrial"},
        headers=_headers(criar_usuario),
    )

    assert response.status_code == 200
    summary = response.json()["primary_disease"]["summary"]
    assert summary == definicao
    assert "corvia-intelligence" not in summary
    assert "<!--" not in summary
    assert "**" not in summary
    disease_result = next(
        item for item in response.json()["results"]
        if item["frente"] == "doenca" and item["slug"] == "fibrilacao-atrial-legado-intelligence"
    )
    assert "corvia-intelligence" not in disease_result["snippet"]
    assert "Atualização CorVIA Intelligence" not in disease_result["snippet"]
    assert "arritmia supraventricular" in disease_result["snippet"].casefold()


def test_higiene_clinica_preserva_nulo_e_texto_de_envelope_corrompido():
    malformed = """<!-- corvia-intelligence:g1:plain:start -->
Definição clínica que não pode ser apagada.
<!-- corvia-intelligence:g2:plain:end -->"""

    assert clinical_text_without_internal_overrides(None) is None
    assert clinical_text_without_internal_overrides(malformed) == (
        "Definição clínica que não pode ser apagada."
    )


def test_doenca_principal_respeita_filtro_de_outra_frente(
    client, db, criar_usuario,
):
    db.add(SpecialtyDisease(
        slug="fibrilacao-atrial-filtrada",
        name="Fibrilação atrial",
        aliases=["FA"],
        area="arritmias",
        category="taquiarritmia supraventricular",
        summary="Definição que não pode atravessar um filtro explícito de frente.",
        review_status="revisado",
        published=True,
    ))
    db.commit()

    response = client.get(
        "/api/search",
        params={"q": "fibrilacao atrial", "frente": "estudo"},
        headers=_headers(criar_usuario),
    )

    assert response.status_code == 200
    assert response.json()["primary_disease"] is None


def test_alias_ambiguo_nao_e_promovido_a_doenca_principal(client, db, criar_usuario):
    db.add_all([
        SpecialtyDisease(
            slug=f"doenca-alias-ambiguo-{index}",
            name=f"Doença ambígua {index}",
            aliases=["DA"],
            area="cardiologia",
            category="teste",
            summary=f"Definição {index}.",
            review_status="revisado",
            published=True,
        )
        for index in (1, 2)
    ])
    db.commit()

    response = client.get(
        "/api/search", params={"q": "DA"}, headers=_headers(criar_usuario),
    )
    assert response.status_code == 200
    assert response.json()["primary_disease"] is None


def test_nome_exato_tem_precedencia_sobre_alias_de_outra_doenca(
    client, db, criar_usuario,
):
    db.add_all([
        SpecialtyDisease(
            slug="fibrilacao-atrial-principal",
            name="Fibrilação atrial",
            aliases=["FA"],
            area="arritmias",
            category="taquiarritmia supraventricular",
            summary="Ativação atrial desorganizada com resposta ventricular variável.",
            review_status="revisado",
            published=True,
        ),
        SpecialtyDisease(
            slug="doenca-com-alias-colidente",
            name="Doença com nomenclatura histórica",
            aliases=["Fibrilação atrial"],
            area="cardiologia",
            category="teste de resolução",
            summary="Registro usado para garantir a prioridade do nome canônico.",
            review_status="revisado",
            published=True,
        ),
    ])
    db.commit()

    response = client.get(
        "/api/search",
        params={"q": "fibrilacao atrial"},
        headers=_headers(criar_usuario),
    )

    assert response.status_code == 200
    assert response.json()["primary_disease"]["slug"] == "fibrilacao-atrial-principal"
