from app.services.rag import (
    HISTORICO_MAX_CHARS,
    MODELO_COMPLEXO,
    MODELO_EQUILIBRADO,
    MODELO_RAPIDO,
    escolher_modelo_automatico,
    limitar_historico,
)


def test_modelo_rapido_para_consulta_direta():
    assert escolher_modelo_automatico("Quais são os quatro pilares da ICFER?") == MODELO_RAPIDO


def test_modelo_equilibrado_para_decisao_terapeutica_curta():
    assert escolher_modelo_automatico("Como fazer ajuste de dose de apixabana na DRC?") == MODELO_EQUILIBRADO


def test_modelo_complexo_para_caso_longo():
    pergunta = "Caso clínico com múltiplos achados. " + ("detalhes clínicos " * 45)
    assert len(pergunta) >= 600
    assert escolher_modelo_automatico(pergunta) == MODELO_COMPLEXO


def test_modelo_complexo_para_multiplos_marcadores():
    pergunta = "Caso clínico com comorbidades, polifarmácia e diagnóstico diferencial."
    assert escolher_modelo_automatico(pergunta) == MODELO_COMPLEXO


def test_historico_respeita_limite_e_preserva_ordem():
    historico = [
        {"role": "user" if i % 2 == 0 else "assistant", "content": str(i) * 5_000}
        for i in range(8)
    ]
    limitado = limitar_historico(historico)

    assert sum(len(item["content"]) for item in limitado) <= HISTORICO_MAX_CHARS
    assert [item["content"][0] for item in limitado] == sorted(
        item["content"][0] for item in limitado
    )
    assert limitado[-1]["content"].startswith("7")
