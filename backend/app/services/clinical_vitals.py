"""Validação de formato, finitude e limites físicos; não classifica gravidade clínica."""
import math
import re

_CAMPOS = {"pa_sistolica", "pa_diastolica", "fc", "fr", "temperatura", "spo2"}


def validar_sinais_vitais(values: object) -> dict:
    if not isinstance(values, dict):
        raise ValueError("Sinais vitais devem ser um objeto de valores numéricos.")
    result = dict(values)
    for key, value in values.items():
        if key not in _CAMPOS:
            raise ValueError(f"Sinal vital desconhecido: {key}.")
        if isinstance(value, bool) or value is None or not isinstance(value, (str, int, float)):
            raise ValueError(f"{key}: informe um valor numérico válido.")
        if isinstance(value, str) and not re.fullmatch(r"[+-]?\d+(?:[.,]\d+)?", value.strip()):
            raise ValueError(f"{key}: informe um valor numérico válido.")
        number = float(value.replace(",", ".") if isinstance(value, str) else value)
        if not math.isfinite(number) or number < 0 or (key == "spo2" and number > 100):
            raise ValueError(f"{key}: valor fora dos limites aceitos.")
        result[key] = number
    return result
