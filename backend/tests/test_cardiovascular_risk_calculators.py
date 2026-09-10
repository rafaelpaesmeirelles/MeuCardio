"""Offline tests against cached numeric cells in the official FHS Excel downloads.

Downloaded 2026-09-10, no network/Excel dependency needed to run.
https://www.framinghamheartstudy.org/files/2017/08/gencardio_lipids.xls
SHA256: 83818029a3c73384247ab08b3cfbe524c3d204cb31754cb22528b67744e64274
Sheet2 D13:G13 (risk as proportion), corresponding inputs in B3:B9.
https://www.framinghamheartstudy.org/files/2017/08/gencardio_bmi.xls
SHA256: 1f164c4b141a8392ac953a9d438b8a2190a7d1e1ee229604e81b68d251a621b0
Sheet2 D28:G28, corresponding inputs in B19:B24.
Use model sheets, not stale display cells in the old workbook's Sheet1.
"""
import math

import pytest

# Initialize the shared registry first: calculator modules import its dataclasses.
from app.services import calculators  # noqa: F401
from app.services.cardiovascular_risk_calculators import (
    CARDIOVASCULAR_RISK_REGISTRY, _framingham_global, _framingham_imc,
)


def payload(**changes):
    data = dict(idade=30, sexo="F", pas=125, tratamento_hipertensao=False,
                tabagismo=False, diabetes=False, doenca_cardiovascular_previa=False,
                colesterol_total=180, hdl=45, imc=22.5)
    data.update(changes)
    return data


# Independent, cached spreadsheet results; do not regenerate from implementation.
@pytest.mark.parametrize("compute,sex,treated,proportion", [
    (_framingham_global, "M", False, 0.016541031859781286),
    (_framingham_global, "M", True, 0.022654152504833047),
    (_framingham_global, "F", False, 0.01309508819972538),
    (_framingham_global, "F", True, 0.017545543966781985),
    (_framingham_imc, "M", False, 0.0177611311514575),
    (_framingham_imc, "M", True, 0.02500868554244895),
    (_framingham_imc, "F", False, 0.010801167676829593),
    (_framingham_imc, "F", True, 0.015094153510678776),
])
@pytest.mark.parametrize("wire_format", ["number", "html_number_string"])
def test_official_workbook_cached_results(compute, sex, treated, proportion, wire_format):
    data = payload(sexo=sex, tratamento_hipertensao=treated)
    if wire_format == "html_number_string":
        data = {key: str(value) if type(value) in (int, float) else value
                for key, value in data.items()}
    result = compute(data)
    assert result["risco_pct"] == round(100 * proportion, 2)
    assert result["horizonte_anos"] == 10
    assert "insuficiência cardíaca" in result["desfecho"]


# Published smoking/diabetes coefficients have an independently testable effect
# on cumulative hazard, across both models and sexes. At most 0.005 percentage
# point display rounding is allowed at either end.
@pytest.mark.parametrize("compute,sex,smoking_beta,diabetes_beta", [
    (_framingham_global, "M", 0.65451, 0.57367),
    (_framingham_global, "F", 0.52873, 0.69154),
    (_framingham_imc, "M", 0.70953, 0.53160),
    (_framingham_imc, "F", 0.61868, 0.77763),
])
def test_published_smoking_and_diabetes_hazard_effect(compute, sex, smoking_beta, diabetes_beta):
    base = compute(payload(idade=55, sexo=sex))["risco_pct"]
    for smoking, diabetes, beta in [(True, False, smoking_beta),
                                    (False, True, diabetes_beta),
                                    (True, True, smoking_beta + diabetes_beta)]:
        observed = compute(payload(idade=55, sexo=sex, tabagismo=smoking, diabetes=diabetes))["risco_pct"]
        lower = 100 * (1 - (1 - (base - 0.005) / 100) ** math.exp(beta)) - 0.005
        upper = 100 * (1 - (1 - (base + 0.005) / 100) ** math.exp(beta)) + 0.005
        assert lower <= observed <= upper


@pytest.mark.parametrize("compute", [_framingham_global, _framingham_imc])
@pytest.mark.parametrize("age", [30, 74])
def test_age_boundaries(compute, age):
    assert 0 <= compute(payload(idade=age))["risco_pct"] <= 100


@pytest.mark.parametrize("compute", [_framingham_global, _framingham_imc])
@pytest.mark.parametrize("age", [29.999, 74.001, 80, 0, float("nan"), float("inf"), True, "55 years", 10**400])
def test_invalid_or_out_of_scope_age_is_rejected(compute, age):
    with pytest.raises(ValueError):
        compute(payload(idade=age))


@pytest.mark.parametrize("compute", [_framingham_global, _framingham_imc])
@pytest.mark.parametrize("key", ["tratamento_hipertensao", "tabagismo", "diabetes",
                                "doenca_cardiovascular_previa"])
@pytest.mark.parametrize("invalid", [None, "false", "true", "", 0, 1, [], {}])
def test_boolean_requires_actual_explicit_answer(compute, key, invalid):
    with pytest.raises(ValueError):
        compute(payload(**{key: invalid}))
    data = payload()
    del data[key]
    with pytest.raises(ValueError):
        compute(data)


@pytest.mark.parametrize("compute", [_framingham_global, _framingham_imc])
@pytest.mark.parametrize("sex", [None, "", "male", "f", 0, True, [], {}])
def test_invalid_sex(compute, sex):
    with pytest.raises(ValueError):
        compute(payload(sexo=sex))


@pytest.mark.parametrize("compute", [_framingham_global, _framingham_imc])
def test_secondary_prevention_is_rejected(compute):
    with pytest.raises(ValueError, match="prevenção primária"):
        compute(payload(doenca_cardiovascular_previa=True))


@pytest.mark.parametrize("compute,key,invalid", [
    (_framingham_global, "pas", 59), (_framingham_global, "pas", 301),
    (_framingham_imc, "imc", 9.9), (_framingham_imc, "imc", 70.1),
    (_framingham_imc, "imc", float("nan")), (_framingham_imc, "imc", None),
    (_framingham_global, "colesterol_total", 5.0),  # mmol/L must not masquerade as mg/dL
    (_framingham_global, "colesterol_total", 601),
    (_framingham_global, "hdl", 1.2), (_framingham_global, "hdl", 151),
    (_framingham_global, "pas", True), (_framingham_imc, "imc", "25 kg/m²"),
    (_framingham_global, "hdl", float("inf")),
])
def test_numeric_guardrails(compute, key, invalid):
    with pytest.raises(ValueError):
        compute(payload(**{key: invalid}))


def test_inconsistent_lipids_and_missing_lab_input():
    with pytest.raises(ValueError):
        _framingham_global(payload(colesterol_total=100, hdl=100))
    data = payload()
    del data["hdl"]
    with pytest.raises(ValueError):
        _framingham_global(data)


def test_bmi_model_needs_no_laboratory_results():
    data = payload()
    del data["colesterol_total"]
    del data["hdl"]
    assert _framingham_imc(data)["risco_pct"] == 1.08


def test_registry_explicit_boolean_contract_and_clinical_scope():
    assert set(CARDIOVASCULAR_RISK_REGISTRY) == {"framingham-global", "framingham-imc"}
    for slug, calculator in CARDIOVASCULAR_RISK_REGISTRY.items():
        assert calculator.kind == "assessment"
        assert calculator.theme == "Prevenção e lipídios"
        assert calculator.compute and calculator.interpret
        assert "10.1161/CIRCULATIONAHA.107.699579" in calculator.reference
        for field in calculator.fields:
            assert field.required is True
            if field.name in {"tratamento_hipertensao", "tabagismo", "diabetes",
                               "doenca_cardiovascular_previa"}:
                assert field.type == "select"
                assert all(type(option["value"]) is bool for option in field.options)
        result = calculator.compute(payload())
        assert "categoria" not in result and "conduta" not in result
        assert "não define" in calculator.interpret(result)


def test_external_official_resources_do_not_execute_or_transmit_patient_data(monkeypatch):
    from urllib.parse import urlsplit
    from app.services.cardiovascular_risk_resources import CARDIOVASCULAR_RISK_RESOURCES
    assert {"prevent", "score2", "score2-op", "score2-diabetes"} <= set(CARDIOVASCULAR_RISK_RESOURCES)
    for slug, calculator in CARDIOVASCULAR_RISK_RESOURCES.items():
        if slug == "sbc-risco-cardiovascular":
            assert calculator.status == "verificacao_humana_necessaria"
            assert calculator.external_url is None and calculator.compute is None
            with pytest.raises(ValueError):
                calculators.run(slug, payload())
            continue
        assert calculator.status == "referencia_externa"
        assert calculator.compute is None and calculator.fields == []
        url = urlsplit(calculator.external_url)
        assert url.scheme == "https"
        assert url.hostname in {"tools.acc.org", "www.heartscore.org", "www.escardio.org"}
        assert not url.query and not url.fragment and not url.username
        monkeypatch.setitem(calculators.REGISTRY, slug, calculator)
        with pytest.raises(ValueError):
            calculators.run(slug, payload())


@pytest.mark.parametrize("compute", [_framingham_global, _framingham_imc])
@pytest.mark.parametrize("invalid", ["", " ", " 55", "55 ", "NaN", "Inf", "Infinity",
                                     "-inf", "nan", "true", "1_000", "55,0", "0x37",
                                     "5e999", "5e", "55\n", "５５", "5" * 129])
def test_invalid_numeric_strings(compute, invalid):
    with pytest.raises(ValueError):
        compute(payload(idade=invalid))


@pytest.mark.parametrize("age", ["55", "55.0", "+55", "5.5e1"])
def test_valid_html_decimal_formats(age):
    assert _framingham_global(payload(idade=age)) == _framingham_global(payload(idade=55))
