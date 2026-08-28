from pathlib import Path

from app.services.disease_manifest import load_disease_records


ROOT = Path(__file__).resolve().parents[2]
BASE = ROOT / "doencas/metadados.json"


def _hub():
    return next(item for item in load_disease_records(BASE) if item["slug"] == "cuidados-paliativos-cardiovasculares")


def _strings(value):
    if isinstance(value, str):
        yield value
    elif isinstance(value, dict):
        for item in value.values():
            yield from _strings(item)
    elif isinstance(value, list):
        for item in value:
            yield from _strings(item)


def test_enable_chf_pc_nao_e_descrito_como_beneficio_comprovado():
    text = " ".join(_strings(_hub())).casefold()
    assert "confirmou melhora sustentada de qualidade de vida e humor" not in text
    assert "não demonstrou diferença estatisticamente significativa" in text


def test_aine_sistemico_nao_e_degrau_analgesico_usual_na_ic():
    text = " ".join(_strings(_hub())).casefold()
    assert "anti-inflamatórios (com cautela" not in text
    assert "aine sistêmico deve ser evitado" in text


def test_internacoes_sao_gatilho_e_nao_criterio_isolado_de_hospice():
    text = " ".join(_strings(_hub())).casefold()
    assert "trajetória compatível com critérios de elegibilidade para hospice" not in text
    assert "o número de internações isoladamente não estabelece elegibilidade" in text


def test_alta_necessidade_paliativa_nao_rotula_automaticamente_fim_de_vida():
    text = " ".join(_strings(_hub())).casefold()
    assert "trajetória de fim de vida não reconhecida" not in text
    assert "alta necessidade paliativa" in text


def test_cied_distingue_consequencia_fisiologica_sem_hierarquia_etica():
    text = " ".join(_strings(_hub())).casefold()
    assert "eticamente distinta da desativação de choques do cdi" not in text
    assert "eticamente mais controverso" not in text
    assert "não cria status ético ou legal distinto" in text
    assert "nenhuma terapia cied possui status ético ou legal único" in text
