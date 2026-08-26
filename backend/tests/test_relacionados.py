"""`GET /api/relacionados` — "Tudo sobre este tema" (pedido do Rafael, 08/08/2026).

Cobre os quatro casos exigidos pela tarefa:
1. mesmo tema devolve itens relacionados de tipos diferentes;
2. item não publicado nunca aparece;
3. o próprio item consultado nunca aparece na própria lista de relacionados;
4. tema sem nenhum item relacionado devolve lista vazia sem erro.

Tabelas de conteúdo não são limpas pelo `_banco_limpo` autouse do conftest
(de propósito — essa fixture cobre só as tabelas da suíte do CorvIA Mail), daí
o TRUNCATE explícito aqui, mesmo padrão de `test_library_catalog.py`.
"""

from sqlalchemy import text

from app.models.checklist import DischargeChecklist
from app.models.clinical_case import ClinicalCase
from app.models.content import Document
from app.models.drug import Drug
from app.models.emergency import EmergencyProtocol
from app.models.evidence import EvidenceRecord
from app.models.gallery import GalleryImage
from app.models.lab_test import LabTest
from app.models.patient_material import PatientMaterial
from app.models.study import ScientificStudy
from app.models.study_track import StudyTrack

TEMA = "Insuficiência cardíaca"

TABELAS = (
    "document_revisions", "documents", "evidence_records", "scientific_studies",
    "drugs", "clinical_cases", "study_tracks", "gallery_images", "lab_tests",
    "emergency_protocols", "discharge_checklists", "patient_materials",
)


def _limpar(db):
    db.execute(text(f"TRUNCATE {', '.join(TABELAS)} RESTART IDENTITY CASCADE"))
    db.commit()


def _headers(criar_usuario):
    _, token = criar_usuario(role="admin")
    return {"Authorization": f"Bearer {token}"}


def test_mesmo_tema_devolve_tipos_diferentes(client, db, criar_usuario):
    _limpar(db)
    db.add(Document(
        slug="ic-doc-1", title="Manejo da IC crônica", kind="modulo", theme=TEMA,
        body_md="conteúdo", source_tier="A", review_status="revisado", published=True,
    ))
    db.add(EvidenceRecord(
        slug="ic-ev-1", statement="Sacubitril-valsartana reduz mortalidade na ICFEr.",
        recommendation_class="I", evidence_level="A", society="ESC", year=2021,
        guideline_title="ESC 2021 Heart Failure", reference="ESC 2021, ref completa",
        theme=TEMA, review_status="revisado", published=True,
    ))
    db.add(ScientificStudy(
        slug="ic-est-1", title="PARADIGM-HF", study_type="ensaio_clinico",
        journal="NEJM", year=2014, summary="resumo", key_findings="achados",
        clinical_implications="implicação", theme=TEMA,
        review_status="revisado", published=True,
    ))
    db.add(ClinicalCase(
        slug="ic-caso-1", titulo="Caso de IC descompensada", tema=TEMA,
        enunciado="enunciado", pergunta="pergunta?", opcoes=["a", "b"],
        resposta_correta=0, explicacao="explicação",
        review_status="revisado", published=True,
    ))
    db.commit()

    r = client.get(f"/api/relacionados?tema={TEMA}", headers=_headers(criar_usuario))
    assert r.status_code == 200
    body = r.json()
    assert body["tema"] == TEMA

    por_tipo = {g["tipo"]: g["itens"] for g in body["grupos"]}
    assert [i["slug"] for i in por_tipo["documento"]] == ["ic-doc-1"]
    assert [i["slug"] for i in por_tipo["evidencia"]] == ["ic-ev-1"]
    assert [i["slug"] for i in por_tipo["estudo"]] == ["ic-est-1"]
    assert [i["slug"] for i in por_tipo["caso_clinico"]] == ["ic-caso-1"]
    assert body["total"] >= 4


def test_estudos_exigem_relacao_com_assunto_e_nao_apenas_mesmo_tema(
    client, db, criar_usuario,
):
    _limpar(db)
    db.add(Document(
        slug="olmesartana-hipertensao", title="Olmesartana na hipertensão",
        kind="modulo", theme="Hipertensão", body_md="conteúdo",
        source_tier="A", review_status="revisado", published=True,
    ))
    db.add_all([
        ScientificStudy(
            slug="olmesartana-potencia-anti-hipertensiva", title="Potência anti-hipertensiva da olmesartana",
            study_type="ensaio_clinico", journal="Hypertension", year=2024,
            summary="resumo", key_findings="achados", clinical_implications="implicação",
            theme="Hipertensão", tags=["olmesartana"], review_status="revisado", published=True,
        ),
        ScientificStudy(
            slug="sprint-controle-intensivo", title="SPRINT — controle intensivo da pressão",
            study_type="ensaio_clinico", journal="NEJM", year=2015,
            summary="resumo", key_findings="achados", clinical_implications="implicação",
            theme="Hipertensão", tags=["pressão arterial"], review_status="revisado", published=True,
        ),
    ])
    db.commit()

    headers = _headers(criar_usuario)
    relacionado = client.get(
        "/api/relacionados?tema=Hipertens%C3%A3o&assunto=olmesartana-hipertensao&excluir_tipo=documento&excluir_slug=olmesartana-hipertensao",
        headers=headers,
    )
    assert relacionado.status_code == 200
    por_tipo = {g["tipo"]: g["itens"] for g in relacionado.json()["grupos"]}
    assert [item["slug"] for item in por_tipo["estudo"]] == [
        "olmesartana-potencia-anti-hipertensiva"
    ]

    sem_relacao = client.get(
        "/api/relacionados?tema=Hipertens%C3%A3o&assunto=tema-sem-correspondencia",
        headers=headers,
    )
    assert sem_relacao.status_code == 200
    por_tipo_sem_relacao = {g["tipo"]: g["itens"] for g in sem_relacao.json()["grupos"]}
    assert por_tipo_sem_relacao["estudo"] == []


def test_item_nao_publicado_nunca_aparece(client, db, criar_usuario):
    _limpar(db)
    db.add(Document(
        slug="ic-doc-pendente", title="Rascunho ainda não revisado", kind="modulo",
        theme=TEMA, body_md="conteúdo", source_tier="A",
        review_status="pendente_revisao", published=False,
    ))
    db.commit()

    r = client.get(f"/api/relacionados?tema={TEMA}", headers=_headers(criar_usuario))
    assert r.status_code == 200
    por_tipo = {g["tipo"]: g["itens"] for g in r.json()["grupos"]}
    assert por_tipo["documento"] == []


def test_proprio_item_nunca_aparece_na_propria_lista(client, db, criar_usuario):
    _limpar(db)
    db.add(Document(
        slug="ic-doc-origem", title="Documento de origem", kind="modulo", theme=TEMA,
        body_md="conteúdo", source_tier="A", review_status="revisado", published=True,
    ))
    db.add(Document(
        slug="ic-doc-outro", title="Outro documento do mesmo tema", kind="modulo",
        theme=TEMA, body_md="conteúdo", source_tier="A",
        review_status="revisado", published=True,
    ))
    db.commit()

    r = client.get(
        f"/api/relacionados?tema={TEMA}&excluir_tipo=documento&excluir_slug=ic-doc-origem",
        headers=_headers(criar_usuario),
    )
    assert r.status_code == 200
    por_tipo = {g["tipo"]: g["itens"] for g in r.json()["grupos"]}
    slugs = [i["slug"] for i in por_tipo["documento"]]
    assert "ic-doc-origem" not in slugs
    assert "ic-doc-outro" in slugs


def test_tema_sem_item_relacionado_devolve_lista_vazia_sem_erro(client, db, criar_usuario):
    _limpar(db)
    r = client.get("/api/relacionados?tema=Tema+Sem+Nenhum+Conteudo", headers=_headers(criar_usuario))
    assert r.status_code == 200
    body = r.json()
    assert body["total"] == 0
    assert all(g["itens"] == [] for g in body["grupos"])
    # nenhuma categoria some da resposta, mesmo vazia — o frontend depende
    # da lista completa de grupos para desenhar a seção correta.
    tipos = {g["tipo"] for g in body["grupos"]}
    assert tipos == {
        "documento", "fluxograma", "evidencia", "estudo", "medicamento", "exame",
        "caso_clinico", "trilha", "galeria", "calculadora", "protocolo_emergencia",
        "checklist", "material_paciente",
    }


def test_medicamentos_entram_so_no_tema_farmacologia(client, db, criar_usuario):
    """Achado de auditoria (issue #52, subfase 8): duas chamadas a
    `_headers(criar_usuario)` no mesmo teste criavam DOIS usuários com o
    mesmo e-mail padrão (`criar_usuario(role="admin")` sem argumento) —
    violação de unicidade determinística a cada execução, não uma
    intermitência. O `_banco_limpo` autouse só trunca uma vez por teste, não
    entre as duas chamadas dentro do mesmo corpo. Corrigido reaproveitando o
    mesmo cabeçalho para as duas requisições (mesma sessão admin nas duas,
    de qualquer forma)."""
    _limpar(db)
    db.add(Drug(
        slug="losartana", generic_name="Losartana", drug_class="BRA",
        review_status="revisado", published=True,
    ))
    db.commit()
    headers = _headers(criar_usuario)

    r_farma = client.get("/api/relacionados?tema=Farmacologia", headers=headers)
    por_tipo = {g["tipo"]: g["itens"] for g in r_farma.json()["grupos"]}
    assert [i["slug"] for i in por_tipo["medicamento"]] == ["losartana"]

    r_outro = client.get(f"/api/relacionados?tema={TEMA}", headers=headers)
    por_tipo_outro = {g["tipo"]: g["itens"] for g in r_outro.json()["grupos"]}
    assert por_tipo_outro["medicamento"] == []


def test_fluxograma_e_documento_comum_ficam_em_categorias_separadas(client, db, criar_usuario):
    _limpar(db)
    db.add(Document(
        slug="ic-fluxo-1", title="Árvore de decisão IC", kind="fluxograma", theme=TEMA,
        body_md="```mermaid\nflowchart TD\n```", source_tier="A",
        review_status="revisado", published=True,
    ))
    db.add(Document(
        slug="ic-doc-comum", title="Protocolo comum", kind="modulo", theme=TEMA,
        body_md="conteúdo", source_tier="A", review_status="revisado", published=True,
    ))
    db.commit()

    r = client.get(f"/api/relacionados?tema={TEMA}", headers=_headers(criar_usuario))
    por_tipo = {g["tipo"]: g["itens"] for g in r.json()["grupos"]}
    assert [i["slug"] for i in por_tipo["fluxograma"]] == ["ic-fluxo-1"]
    assert [i["slug"] for i in por_tipo["documento"]] == ["ic-doc-comum"]


def test_protocolo_emergencia_herda_tema_do_documento(client, db, criar_usuario):
    _limpar(db)
    db.add(Document(
        slug="ic-doc-emerg", title="Choque cardiogênico agudo", kind="protocolo",
        theme=TEMA, body_md="conteúdo", source_tier="A",
        review_status="revisado", published=True,
    ))
    db.commit()
    db.add(EmergencyProtocol(
        slug="protocolo-choque", titulo="Choque cardiogênico", gatilho="Hipotensão + má perfusão",
        documento_slug="ic-doc-emerg", review_status="revisado", published=True,
    ))
    db.commit()

    r = client.get(f"/api/relacionados?tema={TEMA}", headers=_headers(criar_usuario))
    por_tipo = {g["tipo"]: g["itens"] for g in r.json()["grupos"]}
    assert [i["slug"] for i in por_tipo["protocolo_emergencia"]] == ["protocolo-choque"]


def test_checklist_e_material_paciente_por_tema(client, db, criar_usuario):
    _limpar(db)
    db.add(DischargeChecklist(
        slug="alta-ic", condicao="Alta de insuficiência cardíaca descompensada",
        theme=TEMA, itens=[{"texto": "item 1", "obrigatorio": True}],
        review_status="revisado", published=True,
    ))
    db.add(PatientMaterial(
        slug="entenda-ic", titulo="Entendendo a insuficiência cardíaca", tema=TEMA,
        secoes=[{"titulo": "O que é", "paragrafos": ["texto"], "itens": []}],
        review_status="revisado", published=True,
    ))
    db.add(StudyTrack(
        slug="trilha-ic", titulo="Trilha de IC", tema=TEMA, etapas=[],
        review_status="revisado", published=True,
    ))
    db.add(GalleryImage(
        slug="eco-ic", title="Eco de IC com FE reduzida", modality="Ecocardiograma",
        theme=TEMA, findings="achados", file_path="/static/galeria/x.jpg",
        source_name="PMC", source_url="https://example.org", license="CC BY 4.0",
        attribution="Fonte X", review_status="revisado", published=True,
    ))
    db.add(LabTest(
        slug="bnp", name="BNP", category="laboratorial", theme=TEMA,
        what_it_measures="peptídeo natriurético", indications="dispneia",
        interpretation="valores altos sugerem IC",
        review_status="revisado", published=True,
    ))
    db.commit()

    r = client.get(f"/api/relacionados?tema={TEMA}", headers=_headers(criar_usuario))
    por_tipo = {g["tipo"]: g["itens"] for g in r.json()["grupos"]}
    assert [i["slug"] for i in por_tipo["checklist"]] == ["alta-ic"]
    assert [i["slug"] for i in por_tipo["material_paciente"]] == ["entenda-ic"]
    assert [i["slug"] for i in por_tipo["trilha"]] == ["trilha-ic"]
    assert [i["slug"] for i in por_tipo["galeria"]] == ["eco-ic"]
    assert [i["slug"] for i in por_tipo["exame"]] == ["bnp"]
