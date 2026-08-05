from __future__ import annotations

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
        return bool(actual)
    if operator == "falsy":
        return not bool(actual)
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
        left = float(actual)
        right = float(expected)
    except (TypeError, ValueError):
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


def validate_answers(
    questions: list[dict[str, Any]],
    answers: dict[str, Any],
) -> tuple[list[str], list[str]]:
    known = _question_map(questions)
    missing_required: list[str] = []
    invalid_fields: list[str] = []

    for field, question in known.items():
        value = answers.get(field)
        if question.get("required") and (value is None or value == ""):
            missing_required.append(field)
            continue
        if value is None or value == "":
            continue
        question_type = question.get("type")
        if question_type == "number":
            try:
                number = float(value)
            except (TypeError, ValueError):
                invalid_fields.append(field)
                continue
            minimum = question.get("min")
            maximum = question.get("max")
            if minimum is not None and number < float(minimum):
                invalid_fields.append(field)
            if maximum is not None and number > float(maximum):
                invalid_fields.append(field)
        elif question_type == "select":
            options = {option.get("value") for option in question.get("options", []) if isinstance(option, dict)}
            if options and value not in options:
                invalid_fields.append(field)
        elif question_type == "multiselect":
            options = {option.get("value") for option in question.get("options", []) if isinstance(option, dict)}
            if not isinstance(value, list) or (options and any(item not in options for item in value)):
                invalid_fields.append(field)

    unknown = set(answers) - set(known)
    invalid_fields.extend(sorted(unknown))
    return sorted(set(missing_required)), sorted(set(invalid_fields))


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
    if len(answers) > 120:
        raise ValueError("Quantidade de respostas acima do limite permitido.")

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

    for rule in sorted(
        (item for item in rules if isinstance(item, dict)),
        key=lambda item: int(item.get("priority", 0)),
        reverse=True,
    ):
        condition = rule.get("when") or {}
        if not _group_matches(condition, answers):
            continue
        additions = rule.get("add") or {}
        rule_id = str(rule.get("id") or f"regra-{len(result['matched_rules']) + 1}")
        result["matched_rules"].append(rule_id)

        candidate_risk = str(additions.get("risk") or "")
        if candidate_risk in RISK_ORDER and RISK_ORDER[candidate_risk] > RISK_ORDER[result["risk"]]:
            result["risk"] = candidate_risk

        for key in (
            "red_flags", "supporting", "opposing", "missing_information",
            "suggested_tests", "differentials", "ambulatory_flow",
            "emergency_flow", "messages",
        ):
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
