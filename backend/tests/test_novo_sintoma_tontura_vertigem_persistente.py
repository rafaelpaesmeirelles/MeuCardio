"""Contrato do registro NOVO "tontura-vertigem-persistente" em
triagem-sintomas/metadados.json, criado em 29/08/2026 por edição direta do
manifesto (não existe mecanismo de fragmentos para triagem-sintomas).

Distinto do registro já existente "sincope-e-pre-sincope" (que exige perda
completa de consciência ou sensação iminente dela): este registro cobre
tontura/vertigem crônica ou recorrente SEM perda de consciência, com
diferencial entre causa vestibular, ortostática/hipotensiva (mais prevalente
e mais perigosa no idoso), cardiovascular, metabólica e medicamentosa.

Nota sobre o gate de review_status: este registro fica
review_status="pendente_revisao" (pendente de revisão médica humana). O
teste test_canonical_content_review_status.py::
test_manifestos_canonicos_so_tem_pendencias_explicitamente_aprovadas_para_rc
FALHA para este slug — esperado e documentado, não contornado. Não existe,
para triagem-sintomas/metadados.json, um teste secundário análogo a
test_disease_fragments_canonical.py (que consome
PENDENTES_LOTES_TUDO_COM_TUDO com uma checagem que não exige
review_status="revisado"); a checagem do gate principal só consulta essa
allowlist para registros já com status="revisado", então adicionar uma
entrada nela não teria nenhum efeito sobre a falha esperada abaixo — por
isso nenhuma allowlist foi adicionada a test_canonical_content_review_status.py
(ver test_gate_de_review_status_falha_como_esperado_e_documentado).
"""

from __future__ import annotations

import json
import re
from pathlib import Path
from urllib.parse import urlparse

from app.services.clinical_rule_engine import (
    evaluate_rules,
    validate_question_definitions,
    validate_rule_definitions,
)

REPOSITORY_ROOT = Path(__file__).resolve().parents[2]
TRIAGE_PATH = REPOSITORY_ROOT / "triagem-sintomas/metadados.json"
SLUG = "tontura-vertigem-persistente"

ALLOWED_ADD_KEYS = {
    "risk", "red_flags", "supporting", "opposing", "missing_information",
    "suggested_tests", "differentials", "ambulatory_flow", "emergency_flow", "messages",
}
ALLOWED_OPERATORS = {
    "eq", "neq", "in", "not_in", "gt", "gte", "lt", "lte",
    "truthy", "falsy", "contains", "exists", "missing",
}
ALLOWED_RISKS = {"informativo", "rotina", "prioritario", "urgente", "emergencia"}

DOSE_PATTERNS = (
    r"\d+[\.,]?\d*\s*mg(?!/d[lL])\b",
    r"\d+[\.,]?\d*\s*mg/kg",
    r"\d+[\.,]?\d*\s*mcg",
)


def _load_all() -> list[dict]:
    data = json.loads(TRIAGE_PATH.read_text(encoding="utf-8"))
    assert isinstance(data, list)
    return data


def _load() -> dict:
    items = {item["slug"]: item for item in _load_all()}
    assert SLUG in items, f"{SLUG} não encontrado em triagem-sintomas/metadados.json"
    return items[SLUG]


def test_registro_existe_no_final_do_manifesto_e_slug_e_unico():
    items = _load_all()
    slugs = [item["slug"] for item in items]
    assert slugs.count(SLUG) == 1
    assert slugs[-1] == SLUG, "registro deveria estar no final do array (minimiza colisão de merge)"


def test_distinto_do_registro_de_sincope():
    items = {item["slug"]: item for item in _load_all()}
    assert "sincope-e-pre-sincope" in items, "registro de referência não deveria ter sido removido"
    tontura = items[SLUG]
    sincope = items["sincope-e-pre-sincope"]
    assert tontura["slug"] != sincope["slug"]
    # A pergunta de perda de consciência existe nos dois, mas com propósitos
    # diferentes: em síncope ela caracteriza o quadro; aqui ela existe para
    # DETECTAR quando o caso não é desta triagem e redirecionar.
    assert "true_loss_of_consciousness" in {q["id"] for q in tontura["questions"]}
    regra = next(r for r in tontura["rules"] if r["id"] == "perda-consciencia-associada")
    mensagens = " ".join(regra["add"].get("messages", []))
    assert "sincope-e-pre-sincope" in mensagens or "Síncope e pré-síncope" in mensagens


def test_campos_obrigatorios_do_schema_presentes():
    item = _load()
    campos = {
        "slug", "name", "aliases", "areas", "summary", "questions", "rules",
        "default_tests", "differentials", "red_flags", "ambulatory_flow",
        "emergency_flow", "tags", "source_refs", "source_urls", "review_status",
        "review_note", "version",
    }
    faltando = campos - set(item.keys())
    assert faltando == set(), f"campos ausentes: {faltando}"
    assert item["name"] == "Tontura/vertigem persistente"
    assert item["version"] == 1
    assert item["review_status"] == "pendente_revisao"
    assert item["review_note"], "review_note é obrigatório quando review_status != revisado"


def test_areas_incluem_geral_e_cardiogeriatria():
    item = _load()
    areas_validas = {"geral", "cardiopediatria", "cardiogeriatria", "cardiooncologia", "gravidez"}
    assert set(item["areas"]) <= areas_validas
    assert {"geral", "cardiogeriatria"} <= set(item["areas"]), (
        "hipotensão ortostática é mais prevalente e mais perigosa no idoso — "
        "'cardiogeriatria' precisa estar presente"
    )


def test_aliases_cobrem_termos_leigos():
    item = _load()
    aliases = set(item["aliases"])
    for termo in ("tontura", "vertigem"):
        assert termo in aliases
    assert any("desmaiar" in a for a in aliases), "alias leigo de pré-síncope sem desmaio ausente"


def test_perguntas_usam_label_e_nao_a_chave_legada_text():
    item = _load()
    for question in item["questions"]:
        assert "label" in question, f"pergunta {question.get('id')} não usa a chave 'label'"
        assert "text" not in question, f"pergunta {question.get('id')} usa a chave legada 'text'"
    ids = [q["id"] for q in item["questions"]]
    assert len(ids) == len(set(ids)), "ids de pergunta repetidos"


def test_perguntas_e_regras_sao_validas_pelo_motor_de_regras():
    item = _load()
    q_errors, q_ids = validate_question_definitions(SLUG, item["questions"])
    assert q_errors == []

    r_errors = validate_rule_definitions(SLUG, item["rules"], q_ids)
    assert r_errors == []

    for rule in item["rules"]:
        assert 0 <= rule["priority"] <= 100
        for group_name in ("all", "any", "none"):
            for condition in rule["when"].get(group_name, []):
                assert condition["field"] in q_ids
                assert condition.get("op", "eq") in ALLOWED_OPERATORS
        add = rule["add"]
        bad_keys = set(add.keys()) - ALLOWED_ADD_KEYS
        assert bad_keys == set(), f"regra {rule['id']} usa chaves não permitidas em add: {bad_keys}"
        if "risk" in add:
            assert add["risk"] in ALLOWED_RISKS
        for field in ("red_flags", "supporting", "opposing", "missing_information",
                      "suggested_tests", "differentials", "ambulatory_flow",
                      "emergency_flow", "messages"):
            if field in add:
                assert isinstance(add[field], list)


def test_red_flags_e_emergency_flow_presentes_e_nao_vazios():
    item = _load()
    assert item["red_flags"], "red_flags documentacional vazio"
    assert item["emergency_flow"], "emergency_flow é obrigatório e não pode ser vazio"
    assert item["ambulatory_flow"], "ambulatory_flow é obrigatório e não pode ser vazio"
    # Toda regra que adiciona red_flags deve, no motor de regras, elevar o
    # risco para pelo menos "urgente" automaticamente — não é preciso
    # duplicar isso na regra, mas confirmamos que pelo menos uma regra usa
    # red_flags de fato (o mecanismo de segurança tem o que acionar).
    assert any(rule["add"].get("red_flags") for rule in item["rules"])


def test_regras_de_red_flag_cobrem_os_diferenciais_de_alarme_pedidos():
    item = _load()
    rule_ids = {r["id"] for r in item["rules"]}
    esperadas = {
        "deficit-neurologico-focal",  # possível AVC/AIT
        "dor-toracica-ou-dispneia",   # possível síndrome coronariana
        "perda-consciencia-associada",  # redireciona ao protocolo de síncope
        "arritmia-ou-palpitacao",     # arritmia conhecida/palpitações
    }
    assert esperadas <= rule_ids


def test_nenhuma_dose_de_farmaco_em_nenhum_campo():
    item = _load()
    serialized = json.dumps(item, ensure_ascii=False)
    for pattern in DOSE_PATTERNS:
        matches = re.findall(pattern, serialized)
        assert matches == [], f"padrão de dose encontrado ({pattern}): {matches}"


def test_texto_com_acentuacao_correta_do_portugues():
    item = _load()
    serialized = json.dumps(item, ensure_ascii=False)
    for palavra in ("tontura", "vertigem", "não ", "síncope", "cardíaca", "hipotensão"):
        assert palavra in serialized, f"acentuação/termo ausente: {palavra!r} não encontrada"


def test_urls_sao_http_ou_https_e_validas():
    item = _load()
    for url in item["source_urls"]:
        parsed = urlparse(url)
        assert parsed.scheme in {"http", "https"}
        assert parsed.netloc
    assert item["source_refs"], "source_refs é obrigatório e não pode ser vazio"


def test_regras_deterministicas_sao_seguras_em_cenarios_simulados():
    item = _load()

    def run(answers: dict) -> dict:
        return evaluate_rules(
            questions=item["questions"],
            rules=item["rules"],
            answers=answers,
            base_tests=item["default_tests"],
            base_differentials=item["differentials"],
            base_ambulatory_flow=item["ambulatory_flow"],
            base_emergency_flow=item["emergency_flow"],
        )

    # Déficit neurológico focal -> emergência (possível AVC, não vertigem benigna)
    result = run({"focal_neuro_deficit": True, "chest_pain_or_dyspnea": False, "true_loss_of_consciousness": False})
    assert result["risk"] == "emergencia"
    assert "deficit-neurologico-focal" in result["matched_rules"]

    # Dor torácica/dispneia associada -> emergência (possível SCA)
    result = run({"chest_pain_or_dyspnea": True, "focal_neuro_deficit": False, "true_loss_of_consciousness": False})
    assert result["risk"] == "emergencia"

    # Perda de consciência relatada -> emergência + mensagem de redirecionamento
    result = run({"true_loss_of_consciousness": True, "focal_neuro_deficit": False, "chest_pain_or_dyspnea": False})
    assert result["risk"] == "emergencia"
    assert result["messages"]

    # Palpitações -> pelo menos urgente (suspeita arrítmica)
    result = run({"palpitations": True, "focal_neuro_deficit": False, "chest_pain_or_dyspnea": False,
                  "true_loss_of_consciousness": False})
    assert result["risk"] == "urgente"

    # Idoso com tontura postural e uso de anti-hipertensivo -> prioritário
    result = run({
        "focal_neuro_deficit": False, "chest_pain_or_dyspnea": False, "true_loss_of_consciousness": False,
        "worse_on_standing": True, "age_years": 78, "antihypertensive_or_hypotensive_drug": True,
    })
    assert result["risk"] == "prioritario"
    assert "ortostatica-idoso" in result["matched_rules"]

    # Quadro posicional isolado, sem sinal de alarme -> rotina (vestibular periférico benigno)
    result = run({
        "focal_neuro_deficit": False, "chest_pain_or_dyspnea": False, "true_loss_of_consciousness": False,
        "position_head_movement_trigger": True,
    })
    assert result["risk"] == "rotina"

    # Nenhuma resposta -> apenas as respostas obrigatórias faltando, sem regra disparada
    result = run({})
    assert result["risk"] == "informativo"
    assert set(result["missing_information"]) == {
        "true_loss_of_consciousness", "chest_pain_or_dyspnea", "focal_neuro_deficit",
    }

    # emergency_flow deve ser usado quando o risco é urgente/emergência
    result = run({"chest_pain_or_dyspnea": True, "focal_neuro_deficit": False, "true_loss_of_consciousness": False})
    assert result["recommended_flow"] == result["emergency_flow"]


def test_gate_de_review_status_falha_como_esperado_e_documentado():
    """Este registro é review_status="pendente_revisao": o gate canônico
    (test_canonical_content_review_status.py::
    test_manifestos_canonicos_so_tem_pendencias_explicitamente_aprovadas_para_rc)
    deve continuar falhando para este slug até revisão médica humana. Este
    teste apenas documenta e trava essa expectativa — não a contorna.
    """
    item = _load()
    assert item["review_status"] == "pendente_revisao"
    assert item["review_status"] != "revisado"
