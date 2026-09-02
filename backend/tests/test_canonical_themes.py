"""Regressão da Parte C (correção coordenada de 02/09/2026): classificador de
tema canônico usado no backfill dos 22 documentos "corvia-intelligence" e nas
futuras cargas do mesmo pipeline."""

from app.services.canonical_themes import (
    TEMA_PADRAO,
    TEMAS_CANONICOS,
    classificar_tema_canonico,
)


def test_ja_canonico_permanece_no_mesmo_tema():
    for tema in TEMAS_CANONICOS:
        assert classificar_tema_canonico(tema) == tema


def test_sem_sinal_textual_cai_no_padrao():
    assert classificar_tema_canonico("Uma frase qualquer sem termo clínico") == TEMA_PADRAO
    assert classificar_tema_canonico("") == TEMA_PADRAO


def test_nao_falso_positivo_de_substring_sem_fronteira_de_palavra():
    # Regressão do bug pego ao rodar contra os 22 documentos reais: "uti"
    # (Terapia intensiva) não pode casar dentro de "semaglutida", nem "iam"
    # (Doença coronariana) dentro de verbos como "fariam"/"seriam".
    assert classificar_tema_canonico(
        "Efeito da semaglutida sobre COVID-19 em diabetes tipo 2"
    ) == "Diabetes e cardiologia"
    assert classificar_tema_canonico(
        "Exercício terapêutico estruturado em hemodiálise"
    ) == TEMA_PADRAO
    assert classificar_tema_canonico(
        "Os pacientes fariam a reabilitação se pudessem"
    ) == TEMA_PADRAO


def test_classifica_pelos_termos_caracteristicos_do_tema():
    casos = {
        "Cardio-oncologia": "Cardiotoxicidade por antraciclina em paciente oncológico",
        "Cardiologia geriátrica": "Fragilidade e desfechos no idoso nonagenário",
        "Cardiologia pediátrica": "Miocardite em criança de 8 anos",
        "Gravidez": "Pré-eclâmpsia e risco cardiovascular na gestante",
        "Perioperatório": "Avaliação de risco pré-operatório em cirurgia não cardíaca",
        "Fibrilação atrial": "Anticoagulação na fibrilação atrial valvar",
        "Cardiomiopatias": "Amiloidose cardíaca por transtirretina",
        "Insuficiência cardíaca": "Sacubitril-valsartana na ICFEr",
        "Doença coronariana": "Angioplastia primária no IAM com supra de ST",
        "Valvopatias": "Estenose mitral reumática grave",
        "Endocardite": "Endocardite infecciosa em prótese valvar",
        "Pericárdio": "Derrame pericárdico e tamponamento",
        "Tromboembolismo": "Trombectomia mecânica no TEP de alto risco",
        "Aorta e doença arterial periférica": "Aneurisma de aorta abdominal roto",
        "Dispositivos": "Troca de gerador de marca-passo definitivo",
        "Prevenção e lipídios": "Estatina de alta potência e prevenção primária",
        "Síncope": "Síncope vasovagal recorrente",
        "Farmacologia": "Interação medicamentosa entre varfarina e amiodarona",
    }
    for tema_esperado, texto in casos.items():
        assert classificar_tema_canonico(texto) == tema_esperado, texto


def test_todo_resultado_pertence_ao_enum_canonico():
    textos = [
        "Belzutifano e cabozantinibe no carcinoma renal",
        "Currículo essencial de formação em cardiologia",
        "Reabilitação da maxila edêntula",
        "Aprendizado de máquina em doenças neurológicas",
    ]
    for texto in textos:
        assert classificar_tema_canonico(texto) in TEMAS_CANONICOS
