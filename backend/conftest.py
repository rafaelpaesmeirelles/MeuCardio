"""Adaptadores globais de contrato para a suíte backend.

Alguns testes científicos históricos foram escritos antes da composição
canônica do Guia de Doenças (metadados.json + fragmentos + correções). Esses
testes devem validar a mesma visão que a aplicação e os gates de publicação
consomem, sem materializar novamente o catálogo nem relaxar validações.
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


def _canonical_disease_map() -> dict[str, dict]:
    # Import tardio: backend/tests/conftest.py configura o ambiente de teste
    # antes de qualquer import de app.*.
    from app.services.disease_manifest import load_disease_records

    repository_root = Path(__file__).resolve().parents[1]
    manifest = repository_root / "doencas" / "metadados.json"
    return {record["slug"]: record for record in load_disease_records(manifest)}


def pytest_collection_modifyitems(items):
    """Alinha helpers legados à fonte canônica sem alterar suas asserções."""
    adapted_modules: set[int] = set()
    for item in items:
        module = item.module
        module_name = module.__name__.rsplit(".", 1)[-1]
        if module_name not in LEGACY_DISEASE_TEST_MODULES:
            continue
        identity = id(module)
        if identity in adapted_modules:
            continue
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
