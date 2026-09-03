"""Contrato auditável do cockpit de Cardiologia Intensiva e UCO."""

import json
from pathlib import Path


ROOT = Path(__file__).resolve().parents[2]
FRONTEND = ROOT / "frontend" / "src"
CONTENT = ROOT / "content" / "Terapia_intensiva"
VALID_REVIEW_STATUSES = {"revisado", "pendente_revisao"}


def _texto(caminho: str) -> str:
    return (FRONTEND / caminho).read_text(encoding="utf-8")


def _assert_markdown_editorial_status(documento: str) -> None:
    assert any(f"review_status: {status}" in documento for status in VALID_REVIEW_STATUSES)


def test_rota_e_lazy_loading_estao_registrados():
    app = _texto("App.tsx")

    assert 'lazy(() => import("./pages/CardiologiaIntensiva"))' in app
    assert 'path="cardiologia-intensiva"' in app


def test_modulo_esta_nas_navegacoes_canonicas():
    arquivos = [
        "components/ClinicalDesktopNav.tsx",
        "components/ClinicalMobileNav.tsx",
        "components/ShellClinicalOSLaunch.tsx",
        "pages/PainelClinicalOS.tsx",
    ]

    for arquivo in arquivos:
        conteudo = _texto(arquivo)
        assert "/cardiologia-intensiva" in conteudo, arquivo
        assert "Cardiologia Intensiva & UCO" in conteudo, arquivo


def test_cockpit_carrega_colecoes_em_paralelo_com_falha_parcial_tolerada_e_usa_tema_canonico():
    pagina = _texto("pages/CardiologiaIntensiva.tsx")

    assert 'const TEMA = "Terapia intensiva"' in pagina
    assert "Promise.allSettled([" in pagina
    assert 'resultadoDocumentos.status === "rejected"' in pagina
    assert 'resultadoCalculadoras.status === "fulfilled"' in pagina
    assert 'resultadoChecklists.status === "fulfilled"' in pagina
    assert "/library/documents?theme=" in pagina
    assert 'api.get<Calculadora[]>("/calculators")' in pagina
    assert 'api.get<PaginaDe<Checklist>>("/checklists?limit=500")' in pagina
    assert "<TudoSobreEsteTema tema={TEMA}" in pagina


def test_cockpit_preserva_gates_humanos_e_nao_promete_prescricao_automatica():
    pagina = _texto("pages/CardiologiaIntensiva.tsx")

    assert "nenhuma estação substitui protocolo local" in pagina
    assert "ainda não há prescrição automática de antibióticos" in pagina
    assert "decisão final preservada pelo médico" in pagina


def test_cockpit_expoe_dupla_conferencia_sem_confundir_com_prescricao():
    pagina = _texto("pages/CardiologiaIntensiva.tsx")

    assert '"conferencia-bomba-infusao-uco"' in pagina
    assert '/calculadoras/conferencia-bomba-infusao-uco' in pagina
    assert "Dose prescrita × concentração × velocidade programada" in pagina
    assert "Concentração, compatibilidade" in pagina


def test_formulario_generico_respeita_campos_numericos_opcionais():
    pagina = _texto("pages/Calculadora.tsx")

    assert "f.required !== false" in pagina
    assert "(opcional)" in pagina


def test_cockpit_expoe_estadiamento_scai_seriado():
    pagina = _texto("pages/CardiologiaIntensiva.tsx")

    assert '"estadiamento-scai-choque-cardiogenico"' in pagina
    assert '/calculadoras/estadiamento-scai-choque-cardiogenico' in pagina
    assert "modificador de parada e reavaliação seriada" in pagina


def test_cockpit_expoe_acidose_metabolica_com_escopo_explicito():
    pagina = _texto("pages/CardiologiaIntensiva.tsx")

    assert '"acidose-metabolica-winter-anion-gap-uco"' in pagina
    assert '/calculadoras/acidose-metabolica-winter-anion-gap-uco' in pagina
    assert "Winter, ânion gap e correção opcional por albumina" in pagina


def test_cockpit_expoe_oxigenacao_com_gate_cardiogenico():
    pagina = _texto("pages/CardiologiaIntensiva.tsx")

    assert '"oxigenacao-pao2-fio2-sdra-uco"' in pagina
    assert '/calculadoras/oxigenacao-pao2-fio2-sdra-uco' in pagina


def test_cockpit_expoe_lra_kdigo_sem_prescricao_automatica():
    pagina = _texto("pages/CardiologiaIntensiva.tsx")

    assert '"lesao-renal-aguda-kdigo-uco"' in pagina
    assert '/calculadoras/lesao-renal-aguda-kdigo-uco' in pagina
    assert "PaO₂/FiO₂, suporte e gate de edema cardiogênico" in pagina


def test_auditoria_descobre_calculadoras_de_registros_modulares():
    auditoria = (ROOT / "scripts" / "audit_tudo_com_tudo.py").read_text(encoding="utf-8")

    assert 'glob("*calculators*.py")' in auditoria


def test_lote_acido_base_preserva_gates_editoriais_e_conexoes_bidirecionais():
    slug = "acidose-metabolica-compensacao-respiratoria-e-anion-gap-na-uco"
    documento = (CONTENT / f"{slug}.md").read_text(encoding="utf-8")
    mala = (CONTENT / "acidose-latica-associada-a-metformina-mala-no-paciente-critico-cardiovascular.md").read_text(
        encoding="utf-8"
    )
    ceto = (
        ROOT
        / "content"
        / "Diabetes_e_cardiologia"
        / "cetoacidose-euglicemica-associada-a-inibidores-de-sglt2.md"
    ).read_text(encoding="utf-8")
    trilhas = json.loads((ROOT / "trilhas" / "metadados.json").read_text(encoding="utf-8"))
    trilha = next(item for item in trilhas if item["slug"] == "trilha-uco-acidose-metabolica-compensacao-e-anion-gap")

    _assert_markdown_editorial_status(documento)
    assert "Vínculo clínico direto" in documento
    assert "Proximidade temática, sem vínculo causal automático" in documento
    assert "/calculadoras/acidose-metabolica-winter-anion-gap-uco" in mala
    assert "/calculadoras/acidose-metabolica-winter-anion-gap-uco" in ceto
    assert trilha["review_status"] in VALID_REVIEW_STATUSES
    assert any(
        etapa["item_type"] == "calculadora"
        and etapa["item_slug"] == "acidose-metabolica-winter-anion-gap-uco"
        for etapa in trilha["etapas"]
    )


def test_lote_oxigenacao_preserva_gates_editoriais_e_diferencial_bidirecional():
    slug = "oxigenacao-pao2-fio2-e-criterios-de-sdra-na-uco"
    documento = (CONTENT / f"{slug}.md").read_text(encoding="utf-8")
    edema = (
        CONTENT
        / "ventilacao-nao-invasiva-no-edema-agudo-de-pulmao-cardiogenico-cpap-versus-bipap.md"
    ).read_text(encoding="utf-8")
    vd = (
        CONTENT
        / "falencia-aguda-do-ventriculo-direito-cor-pulmonale-agudo-consenso-acvc-esc-2024.md"
    ).read_text(encoding="utf-8")
    trilhas = json.loads((ROOT / "trilhas" / "metadados.json").read_text(encoding="utf-8"))
    trilha = next(item for item in trilhas if item["slug"] == "trilha-uco-oxigenacao-pao2-fio2-e-sdra")

    _assert_markdown_editorial_status(documento)
    assert "Vínculo clínico direto" in documento
    assert "Vínculo diferencial explícito" in documento
    assert "P/F corrigida = P/F observada × (pressão barométrica local ÷ 760)" in documento
    assert "marcos temporais alternativos" in documento
    assert "nenhum deles elimina" in documento
    assert "/calculadoras/oxigenacao-pao2-fio2-sdra-uco" in edema
    assert "/calculadoras/oxigenacao-pao2-fio2-sdra-uco" in vd
    assert "\\[" not in documento
    assert trilha["review_status"] in VALID_REVIEW_STATUSES
    assert any(
        etapa["item_type"] == "calculadora"
        and etapa["item_slug"] == "oxigenacao-pao2-fio2-sdra-uco"
        for etapa in trilha["etapas"]
    )


def test_lote_lra_preserva_componentes_gates_editoriais_e_backlinks_diretos():
    slug = "lesao-renal-aguda-na-uco-criterios-kdigo-creatinina-e-diurese"
    documento = (CONTENT / f"{slug}.md").read_text(encoding="utf-8")
    choque = (CONTENT / "choque-cardiogenico-diagnostico-e-manejo-com-drogas-vasoativas.md").read_text(
        encoding="utf-8"
    )
    vd = (
        CONTENT
        / "falencia-aguda-do-ventriculo-direito-cor-pulmonale-agudo-consenso-acvc-esc-2024.md"
    ).read_text(encoding="utf-8")
    acidose = (
        CONTENT / "acidose-metabolica-compensacao-respiratoria-e-anion-gap-na-uco.md"
    ).read_text(encoding="utf-8")
    trilhas = json.loads((ROOT / "trilhas" / "metadados.json").read_text(encoding="utf-8"))
    trilha = next(item for item in trilhas if item["slug"] == "trilha-uco-lesao-renal-aguda-kdigo")

    _assert_markdown_editorial_status(documento)
    assert "C1/U2 → estágio 2" in documento
    assert "rascunho KDIGO 2026" in documento
    assert "/calculadoras/lesao-renal-aguda-kdigo-uco" in choque
    assert "/calculadoras/lesao-renal-aguda-kdigo-uco" in vd
    assert "/calculadoras/lesao-renal-aguda-kdigo-uco" in acidose
    assert trilha["review_status"] in VALID_REVIEW_STATUSES
    assert any(
        etapa["item_type"] == "calculadora"
        and etapa["item_slug"] == "lesao-renal-aguda-kdigo-uco"
        for etapa in trilha["etapas"]
    )


def test_modificador_scai_a_foi_corrigido_no_documento_e_checklist():
    documento = (CONTENT / "classificacao-scai-de-estagios-do-choque-cardiogenico.md").read_text(
        encoding="utf-8"
    )
    checklists = json.loads((ROOT / "checklists" / "metadados.json").read_text(encoding="utf-8"))
    registro = next(
        item
        for item in checklists
        if item["slug"] == "reconhecimento-e-manejo-inicial-do-choque-cardiogenico"
    )
    item_parada = next(item for item in registro["itens"] if item["id"] == "chc-modificador-a-parada")
    alta = next(item for item in checklists if item["slug"] == "alta-pos-choque-cardiogenico")
    item_alta = next(item for item in alta["itens"] if item["id"] == "cs-scai-estagio")

    assert "coma/GCS <9 ou ausência de resposta a comandos após RCE" in documento
    assert "ainda não constituía consenso final" in documento
    assert "Parada breve com recuperação neurológica" in item_parada["texto"]
    assert "independentemente da duração do episódio" not in item_parada["texto"]
    assert "potencial lesão cerebral anóxica" in item_alta["texto"]
    assert "não por qualquer parada breve" in item_alta["texto"]


def test_avaliacao_estruturada_nao_e_catalogada_como_dose():
    detalhe = _texto("pages/Calculadora.tsx")
    catalogo = _texto("pages/Calculadoras.tsx")

    assert 'new Set(["dose", "assessment"])' in detalhe
    assert 'c.kind === "dose"' in catalogo
    assert 'c.kind !== "dose"' in catalogo
    assert "Escores e avaliações" in catalogo
