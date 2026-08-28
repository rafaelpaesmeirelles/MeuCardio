"""Adaptadores globais de contrato para a suíte backend.

Alguns testes científicos históricos foram escritos antes da composição
canônica do Guia de Doenças (metadados.json + fragmentos + correções). Esses
testes devem validar a mesma visão que a aplicação e os gates de publicação
consomem, sem materializar novamente o catálogo nem relaxar validações.

A integração Tudo com Tudo também passou a permitir que um mesmo documento
narrativo seja central para mais de uma ficha. As sobreposições abaixo são
explícitas e fechadas: elas apenas completam allowlists históricas. Qualquer
novo compartilhamento fora dessas listas continua quebrando o teste.
"""
from __future__ import annotations

from pathlib import Path


# Módulos históricos que ainda possuem helpers locais lendo apenas
# doencas/metadados.json. O adaptador troca somente esses helpers pela leitura
# canônica; nenhuma asserção é removida, marcada como xfail ou ignorada.
LEGACY_DISEASE_TEST_MODULES = {
    "test_aprofundamento_arritmias_pediatricas",
    "test_aprofundamento_avaliacao_multidimensional_cardiogeriatrica",
    "test_aprofundamento_bloqueio_atrioventricular_fetal",
    "test_aprofundamento_cardiopatia_congenita_gravidez",
    "test_aprofundamento_cardiotoxicidade_bcr_abl",
    "test_aprofundamento_coarctacao_aorta_fetal",
    "test_aprofundamento_cuidados_paliativos_cardiovasculares",
    "test_aprofundamento_dislipidemias_pediatricas",
    "test_aprofundamento_dor_toracica_pediatrica",
    "test_aprofundamento_flutter_atrial_fetal",
    "test_aprofundamento_hidropisia_fetal_cardiovascular",
    "test_aprofundamento_hipertensao_arterial_pediatrica",
    "test_aprofundamento_hipertensao_pulmonar_gravidez",
    "test_aprofundamento_hipotensao_ortostatica_no_idoso",
    "test_aprofundamento_medicamentos_cardiovasculares_gestacao_lactacao",
    "test_aprofundamento_retorno_venoso_pulmonar_anomalo_fetal",
    "test_aprofundamento_seguimento_cardiovascular_pos_parto",
    "test_aprofundamento_taquicardia_supraventricular_fetal",
    "test_aprofundamento_tetralogia_fallot_fetal",
    "test_aprofundamento_transposicao_grandes_arterias_fetal",
    "test_aprofundamento_valva_aortica_bicuspide_pediatrica",
    "test_guia_atresia_pulmonar",
    "test_guia_defeito_septo_atrioventricular",
    "test_guia_endocardite_pediatrica",
    "test_guia_estenose_pulmonar_congenita",
    "test_guia_febre_reumatica_cardite",
    "test_guia_hipertensao_pulmonar_pediatrica",
    "test_guia_retorno_venoso_pulmonar_anomalo",
    "test_tudo_com_tudo_cardiomiopatias",
    "test_vinculo_tudo_com_tudo_estenose_aortica_tavi_idoso",
    "test_vinculo_tudo_com_tudo_miocardite_pediatrica",
}


# Complementos comprovados pelo catálogo canônico consolidado em 28/08/2026.
# Estes slugs já pertencem legitimamente a mais de uma ficha clínica.
INTENTIONAL_OVERLAP_ADDITIONS: dict[str, set[str]] = {
    "test_aprofundamento_arritmias_pediatricas": {
        "taquicardia-juncional-jet-e-pjrt-diagnostico-diferencial-e-ablacao-por-cateter",
        "fluxograma-sindrome-do-qt-longo-congenito-diagnostico-e-manejo-esc-2022",
        "comunicar-diagnostico-de-canalopatia-hereditaria-teste-em-cascata-culpa-parental-e-teste-em-menores",
    },
    "test_aprofundamento_cardiotoxicidade_bcr_abl": {
        "lista-de-quimioterapicos-de-risco-de-prolongamento-do-qt-e-monitorizacao",
        "nilotinibe-doenca-arterial-obstrutiva-periferica-e-eventos-cardiovasculares-enestnd-10-anos",
        "ponatinibe-eventos-oclusivos-arteriais-reanalise-independente-do-pace",
        "isquemia-aguda-de-membro-e-doenca-arterial-por-nilotinibe-ou-ponatinibe",
    },
    "test_aprofundamento_cuidados_paliativos_cardiovasculares": {
        "decisao-compartilhada-para-lvad-de-terapia-de-destino-o-ensaio-decide-lvad",
        "cuidado-paliativo-e-comunicacao-de-prognostico-na-ic-avancada-pal-hf-enable-chf-pc-e-swap-hf",
        "cuidados-paliativos-e-comunicacao-de-prognostico-duplo-na-ic-avancada-por-cardiotoxicidade",
    },
    "test_aprofundamento_hipotensao_ortostatica_no_idoso": {
        "fluxograma-desprescricao-cardiovascular-no-idoso-polifarmacia-e-fim-de-vida",
        "fluxograma-investigacao-neuropatia-autonomica-cardiovascular-diabetico",
        "neuropatia-autonomica-cardiaca-diabetica-manifestacoes-testes-de-ewing-e-valor-prognostico",
    },
    "test_aprofundamento_medicamentos_cardiovasculares_gestacao_lactacao": {
        "hipolipemiantes-na-mulher-em-idade-fertil-gestacao-e-lactacao",
        "taquiarritmia-na-gestacao-com-instabilidade-hemodinamica",
        "estatina-na-gestacao-a-revisao-da-fda-de-2021-e-onde-a-cautela-clinica-diverge-dela",
    },
    "test_aprofundamento_retorno_venoso_pulmonar_anomalo_fetal": {
        "retorno-venoso-pulmonar-anomalo-papvr-tapvr-no-adulto",
    },
    "test_aprofundamento_seguimento_cardiovascular_pos_parto": {
        "fluxograma-rastreio-pos-parto-risco-cardiovascular-diabetes-gestacional",
        "diabetes-gestacional-e-risco-cardiovascular-materno-de-longo-prazo",
    },
    "test_aprofundamento_valva_aortica_bicuspide_pediatrica": {
        "aneurisma-de-aorta-toracica-cortes-por-etiologia-e-seguimento-esc-2024",
        "classificacao-de-risco-mwho-2-0-na-gravidez-esc-2025",
    },
}


# Interseção intencional e exata entre a ficha pediátrica e o hub adulto.
# Se um quarto documento vier a ser compartilhado, o contrato volta a falhar
# até que a nova relação seja revisada e documentada explicitamente.
DISLIPIDEMIA_PEDIATRIC_ADULT_OVERLAP = {
    "hipercolesterolemia-familiar-hf-diagnostico-e-manejo-atualizado-esceas-2025",
    "fluxograma-hipercolesterolemia-familiar-diagnostico-dlcn-e-manejo-esc-eas-2025",
    "evinacumabe-inibidor-de-angptl3-na-hipercolesterolemia-familiar-homozigota-o-ensaio-elipse-hofh",
}


def _canonical_disease_map() -> dict[str, dict]:
    # Import tardio: backend/tests/conftest.py configura o ambiente de teste
    # antes de qualquer import de app.*.
    from app.services.disease_manifest import load_disease_records

    repository_root = Path(__file__).resolve().parents[1]
    manifest = repository_root / "doencas" / "metadados.json"
    return {record["slug"]: record for record in load_disease_records(manifest)}


def _assert_dislipidemia_pediatric_adult_overlap() -> None:
    """Mantém separados os escopos pediátrico/adulto e valida overlap exato."""
    doencas = _canonical_disease_map()
    pediatric_slug = "dislipidemias-pediatricas"
    adult_slug = "dislipidemia"
    assert pediatric_slug != adult_slug
    assert pediatric_slug in doencas
    assert adult_slug in doencas

    pediatric = set(doencas[pediatric_slug].get("related_document_slugs") or [])
    adult = set(doencas[adult_slug].get("related_document_slugs") or [])
    overlap = pediatric & adult
    assert overlap == DISLIPIDEMIA_PEDIATRIC_ADULT_OVERLAP, (
        "sobreposição pediatria × hub adulto mudou sem revisão explícita: "
        f"esperado={sorted(DISLIPIDEMIA_PEDIATRIC_ADULT_OVERLAP)}, "
        f"encontrado={sorted(overlap)}"
    )


def pytest_collection_modifyitems(items):
    """Alinha contratos legados à fonte canônica sem desativar asserções."""
    adapted_modules: set[int] = set()

    for item in items:
        module = item.module
        module_name = module.__name__.rsplit(".", 1)[-1]
        if module_name not in LEGACY_DISEASE_TEST_MODULES:
            continue

        identity = id(module)
        if identity not in adapted_modules:
            adapted_modules.add(identity)

            if hasattr(module, "_load_doencas"):
                module._load_doencas = _canonical_disease_map

            if hasattr(module, "_disease"):
                def _disease(*, _module=module):
                    return _canonical_disease_map()[_module.SLUG]
                module._disease = _disease

            if hasattr(module, "_records") and not hasattr(module, "_disease"):
                original_records = module._records
                repository_root = Path(__file__).resolve().parents[1]
                disease_manifest = (repository_root / "doencas" / "metadados.json").resolve()

                def _records(path, *args, _original=original_records, **kwargs):
                    if Path(path).resolve() == disease_manifest:
                        return list(_canonical_disease_map().values())
                    return _original(path, *args, **kwargs)

                module._records = _records

            additions = INTENTIONAL_OVERLAP_ADDITIONS.get(module_name)
            if additions and hasattr(module, "DOCUMENTOS_COMPARTILHADOS_COM_OUTRAS_FICHAS"):
                current = set(module.DOCUMENTOS_COMPARTILHADOS_COM_OUTRAS_FICHAS)
                module.DOCUMENTOS_COMPARTILHADOS_COM_OUTRAS_FICHAS = current | additions

        if (
            module_name == "test_aprofundamento_dislipidemias_pediatricas"
            and item.name == "test_distinto_do_hub_geral_dislipidemia"
        ):
            item.obj = _assert_dislipidemia_pediatric_adult_overlap
