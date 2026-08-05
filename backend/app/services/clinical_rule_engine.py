from __future__ import annotations

import math
from collections.abc import Iterable
from typing import Any

RISK_ORDER = {
    "informativo": 0,
    "rotina": 1,
    "prioritario": 2,
    "urgente": 3,
    "emergencia": 4,
}

ALLOWED_OPERATORS = {
    "eq", "neq", "in", "not_in", "gt", "gte", "lt", "lte",
    "truthy", "falsy", "contains", "exists", "missing",
}

RESULT_LIST_FIELDS = {
    "red_flags", "supporting", "opposing", "missing_information",
    "suggested_tests", "differentials", "ambulatory_flow",
    "emergency_flow", "messages",
}
ALLOWED_ADDITION_FIELDS = RESULT_LIST_FIELDS | {"risk"}
MAX_ANSWERS = 120
MAX_RULES = 500
MAX_TEXT_LENGTH = 2000
MAX_MULTISELECT_ITEMS = 50
QUESTION_TYPES = {"boolean", "number", "select", "multiselect", "text"}


def validate_question_definitions(
    slug: str,
    questions: Any,
) -> tuple[list[str], set[str]]:
    errors: list[str] = []
    ids: list[str] = []
    if not isinstance(questions, list):
        return [f"{slug}: perguntas devem ser uma lista"], set()

    for index, question in enumerate(questions):
        if not isinstance(question, dict):
            errors.append(f"{slug}: pergunta {index} não é objeto")
            continue
        question_id = question.get("id")
        if not isinstance(question_id, str) or not question_id.strip():
            errors.append(f"{slug}: pergunta {index} sem id")
            continue
        ids.append(question_id)
        question_type = question.get("type")
        if question_type not in QUESTION_TYPES:
            errors.append(f"{slug}: pergunta {question_id} com tipo inválido")
            continue
        if question_type in {"select", "multiselect"}:
            options = question.get("options")
            if not isinstance(options, list) or not options:
                errors.append(f"{slug}: pergunta {question_id} precisa de opções")
                continue
            values = [
                option.get("value")
                for option in options
                if isinstance(option, dict) and option.get("value") is not None
            ]
            if len(values) != len(options) or len(values) != len(set(map(str, values))):
                errors.append(f"{slug}: pergunta {question_id} tem opções inválidas ou repetidas")
        if question_type == "number":
            try:
                minimum = float(question["min"]) if question.get("min") is not None else None
                maximum = float(question["max"]) if question.get("max") is not None else None
            except (TypeError, ValueError):
                errors.append(f"{slug}: pergunta {question_id} tem limite numérico inválido")
                continue
            if (
                (minimum is not None and not math.isfinite(minimum))
                or (maximum is not None and not math.isfinite(maximum))
                or (minimum is not None and maximum is not None and minimum > maximum)
            ):
                errors.append(f"{slug}: pergunta {question_id} tem intervalo numérico inválido")

    if len(ids) != len(set(ids)):
        errors.append(f"{slug}: ids de pergunta repetidos")
    return errors, set(ids)


def validate_rule_definitions(
    slug: str,
    rules: Any,
    question_ids: set[str],
) -> list[str]:
    errors: list[str] = []
    rule_ids: list[str] = []
    if not isinstance(rules, list):
        return [f"{slug}: regras devem ser uma lista"]

    for index, rule in enumerate(rules):
        if not isinstance(rule, dict):
            errors.append(f"{slug}: regra {index} não é objeto")
            continue
        rule_id = str(rule.get("id") or "")
        if not rule_id:
            errors.append(f"{slug}: regra {index} sem id")
            continue
        rule_ids.append(rule_id)
        condition = rule.get("when")
        if not isinstance(condition, dict):
            errors.append(f"{slug}: regra {rule_id} tem condição inválida")
            continue
        has_condition = False
        for group_name in ("all", "any", "none"):
            group = condition.get(group_name, [])
            if not isinstance(group, list):
                errors.append(f"{slug}: regra {rule_id} tem grupo {group_name} inválido")
                continue
            has_condition = has_condition or bool(group)
            for condition_item in group:
                if not isinstance(condition_item, dict):
                    errors.append(f"{slug}: regra {rule_id} contém condição inválida")
                    continue
                field = condition_item.get("field")
                operator = condition_item.get("op", "eq")
                if field not in question_ids:
                    errors.append(f"{slug}: regra {rule_id} usa campo desconhecido {field}")
                if operator not in ALLOWED_OPERATORS:
                    errors.append(f"{slug}: regra {rule_id} usa operador inválido {operator}")
        if not has_condition:
            errors.append(f"{slug}: regra {rule_id} não possui condição")

        additions = rule.get("add")
        if not isinstance(additions, dict):
            errors.append(f"{slug}: regra {rule_id} tem resultado inválido")
            continue
        unknown = sorted(set(additions) - ALLOWED_ADDITION_FIELDS)
        if unknown:
            errors.append(f"{slug}: regra {rule_id} adiciona campos não permitidos {unknown}")
        risk = additions.get("risk")
        if risk is not None and risk not in RISK_ORDER:
            errors.append(f"{slug}: regra {rule_id} usa risco inválido {risk}")
        for field in RESULT_LIST_FIELDS:
            if field in additions and not isinstance(additions[field], list):
                errors.append(f"{slug}: regra {rule_id} exige lista em {field}")

    if len(rule_ids) != len(set(rule_ids)):
        errors.append(f"{slug}: ids de regra repetidos")
    return errors


def _as_iterable(value: Any) -> list[Any]:
    if value is None:
        return []
    if isinstance(value, (list, tuple, set)):
        return list(value)
    return [value]


def _compare(actual: Any, operator: str, expected: Any = None) -> bool:
    if operator not in ALLOWED_OPERATORS:
        return False
    if operator == "exists":
        return actual is not None and actual != ""
    if operator == "missing":
        return actual is None or actual == ""
    if operator == "truthy":
        return actual is True
    if operator == "falsy":
        return actual is False
    if operator == "eq":
        return actual == expected
    if operator == "neq":
        return actual != expected
    if operator == "in":
        return actual in _as_iterable(expected)
    if operator == "not_in":
        return actual not in _as_iterable(expected)
    if operator == "contains":
        if isinstance(actual, str):
            return str(expected).casefold() in actual.casefold()
        return expected in _as_iterable(actual)
    try:
        if isinstance(actual, bool) or isinstance(expected, bool):
            return False
        left = float(actual)
        right = float(expected)
    except (TypeError, ValueError):
        return False
    if not math.isfinite(left) or not math.isfinite(right):
        return False
    if operator == "gt":
        return left > right
    if operator == "gte":
        return left >= right
    if operator == "lt":
        return left < right
    if operator == "lte":
        return left <= right
    return False


def _condition_matches(condition: dict[str, Any], answers: dict[str, Any]) -> bool:
    field = str(condition.get("field") or "")
    if not field:
        return False
    operator = str(condition.get("op") or "eq")
    return _compare(answers.get(field), operator, condition.get("value"))


def _group_matches(group: dict[str, Any], answers: dict[str, Any]) -> bool:
    all_conditions = group.get("all") or []
    any_conditions = group.get("any") or []
    none_conditions = group.get("none") or []

    if all_conditions and not all(_condition_matches(item, answers) for item in all_conditions):
        return False
    if any_conditions and not any(_condition_matches(item, answers) for item in any_conditions):
        return False
    if none_conditions and any(_condition_matches(item, answers) for item in none_conditions):
        return False
    return bool(all_conditions or any_conditions or none_conditions)


def _append_unique(target: list[Any], values: Iterable[Any]) -> None:
    for value in values:
        if value not in target:
            target.append(value)


def _question_map(questions: list[dict[str, Any]]) -> dict[str, dict[str, Any]]:
    return {
        str(question.get("id")): question
        for question in questions
        if isinstance(question, dict) and question.get("id")
    }


def _is_missing_answer(value: Any) -> bool:
    if value is None:
        return True
    if isinstance(value, str):
        return not value.strip()
    if isinstance(value, (list, tuple, set, dict)):
        return not value
    return False


def validate_answers(
    questions: list[dict[str, Any]],
    answers: dict[str, Any],
) -> tuple[list[str], list[str]]:
    known = _question_map(questions)
    missing_required: list[str] = []
    invalid_fields: list[str] = []

    for field, question in known.items():
        value = answers.get(field)
        if question.get("required") and _is_missing_answer(value):
            missing_required.append(field)
            continue
        if _is_missing_answer(value):
            continue
        question_type = question.get("type")
        if question_type == "boolean":
            if not isinstance(value, bool):
                invalid_fields.append(field)
        elif question_type == "number":
            if isinstance(value, bool):
                invalid_fields.append(field)
                continue
            try:
                number = float(value)
            except (TypeError, ValueError):
                invalid_fields.append(field)
                continue
            if not math.isfinite(number):
                invalid_fields.append(field)
                continue
            minimum = question.get("min")
            maximum = question.get("max")
            if minimum is not None and number < float(minimum):
                invalid_fields.append(field)
            if maximum is not None and number > float(maximum):
                invalid_fields.append(field)
        elif question_type == "select":
            options = {
                option.get("value")
                for option in question.get("options", [])
                if isinstance(option, dict)
            }
            if options and value not in options:
                invalid_fields.append(field)
        elif question_type == "multiselect":
            options = {
                option.get("value")
                for option in question.get("options", [])
                if isinstance(option, dict)
            }
            if (
                not isinstance(value, list)
                or len(value) > MAX_MULTISELECT_ITEMS
                or len(value) != len(set(map(str, value)))
                or (options and any(item not in options for item in value))
            ):
                invalid_fields.append(field)
        elif question_type == "text":
            if not isinstance(value, str) or len(value) > MAX_TEXT_LENGTH:
                invalid_fields.append(field)
        else:
            invalid_fields.append(field)

    unknown = set(answers) - set(known)
    invalid_fields.extend(sorted(unknown))
    return sorted(set(missing_required)), sorted(set(invalid_fields))


def _priority(rule: dict[str, Any]) -> int:
    try:
        return max(-1000, min(1000, int(rule.get("priority", 0))))
    except (TypeError, ValueError):
        return 0


def evaluate_rules(
    *,
    questions: list[dict[str, Any]],
    rules: list[dict[str, Any]],
    answers: dict[str, Any],
    base_tests: list[Any] | None = None,
    base_differentials: list[Any] | None = None,
    base_ambulatory_flow: list[Any] | None = None,
    base_emergency_flow: list[Any] | None = None,
    context: str = "ambulatorio",
) -> dict[str, Any]:
    if len(answers) > MAX_ANSWERS:
        raise ValueError("Quantidade de respostas acima do limite permitido.")
    if len(rules) > MAX_RULES:
        raise ValueError("Quantidade de regras acima do limite permitido.")
    if context not in {"ambulatorio", "emergencia"}:
        raise ValueError("Contexto de atendimento inválido.")

    missing_required, invalid_fields = validate_answers(questions, answers)
    result: dict[str, Any] = {
        "risk": "informativo",
        "red_flags": [],
        "supporting": [],
        "opposing": [],
        "missing_information": missing_required.copy(),
        "suggested_tests": list(base_tests or []),
        "differentials": list(base_differentials or []),
        "ambulatory_flow": list(base_ambulatory_flow or []),
        "emergency_flow": list(base_emergency_flow or []),
        "messages": [],
        "matched_rules": [],
        "invalid_fields": invalid_fields,
        "context": context,
    }

    if not invalid_fields:
        for rule in sorted(
            (item for item in rules if isinstance(item, dict)),
            key=_priority,
            reverse=True,
        ):
            condition = rule.get("when") or {}
            if not _group_matches(condition, answers):
                continue
            additions = rule.get("add") or {}
            if not isinstance(additions, dict):
                continue
            rule_id = str(rule.get("id") or f"regra-{len(result['matched_rules']) + 1}")
            result["matched_rules"].append(rule_id)

            candidate_risk = str(additions.get("risk") or "")
            if (
                candidate_risk in RISK_ORDER
                and RISK_ORDER[candidate_risk] > RISK_ORDER[result["risk"]]
            ):
                result["risk"] = candidate_risk

            for key in RESULT_LIST_FIELDS:
                values = additions.get(key)
                if values:
                    _append_unique(result[key], _as_iterable(values))

    if result["red_flags"] and RISK_ORDER[result["risk"]] < RISK_ORDER["urgente"]:
        result["risk"] = "urgente"

    result["recommended_flow"] = (
        result["emergency_flow"]
        if context == "emergencia" or result["risk"] in {"urgente", "emergencia"}
        else result["ambulatory_flow"]
    )
    result["disclaimer"] = (
        "Ferramenta de apoio à organização clínica. Não substitui avaliação presencial, "
        "protocolos locais, julgamento profissional ou atendimento de emergência."
    )
    return result
