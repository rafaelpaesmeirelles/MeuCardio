"""Taxonomia clínica canônica para o Guia de Doenças.

O catálogo preserva categorias editoriais granulares nos registros de origem.
Elas não são, porém, uma boa faceta de navegação: dezenas de rótulos têm um
único verbete e vários descrevem contexto, processo assistencial ou tipo de
tratamento em vez de uma área clínica. Este módulo agrega esses valores em
domínios estáveis sem reescrever nem perder o metadado original.

``area`` continua representando população/contexto (adulto, pediatria,
geriatria, oncologia e gestação). ``clinical_domain`` representa o campo
cardiovascular principal. As dimensões não devem ser misturadas novamente.
"""

from __future__ import annotations


CLINICAL_DOMAINS: tuple[dict[str, object], ...] = (
    {
        "id": "arritmias_e_eletrofisiologia",
        "label": "Arritmias, eletrofisiologia e dispositivos",
        "categories": (
            "arritmia", "arritmia_supraventricular", "disturbio_de_conducao",
            "dispositivo_cardiaco", "cardiogenetica",
        ),
    },
    {
        "id": "coronaria_e_intervencao",
        "label": "Doença coronariana e intervenção",
        "categories": ("doenca_coronariana", "avaliacao_pre_procedimento"),
    },
    {
        "id": "insuficiencia_e_miocardio",
        "label": "Insuficiência cardíaca, miocárdio e cardiomiopatias",
        "categories": (
            "insuficiencia_cardiaca", "cardiomiopatia", "doenca_miocardica",
        ),
    },
    {
        "id": "valvopatias_e_estrutural",
        "label": "Valvopatias e cardiologia estrutural",
        "categories": (
            "valvopatia", "valvopatia_e_anticoagulacao", "tumor_cardiaco",
        ),
    },
    {
        "id": "hipertensao_prevencao_e_risco",
        "label": "Hipertensão, prevenção e risco cardiovascular",
        "categories": (
            "hipertensao", "prevencao", "prevencao_e_risco",
            "prevencao_cardiovascular", "doenca_prevalente",
            "seguranca_antitrombotica", "antitromboticos",
            "hipertensao_na_gestacao",
        ),
    },
    {
        "id": "aorta_e_vascular",
        "label": "Aorta e medicina vascular",
        "categories": ("aortopatia", "doenca_vascular", "emergencia_vascular"),
    },
    {
        "id": "pulmonar_e_tromboembolismo",
        "label": "Circulação pulmonar e tromboembolismo",
        "categories": ("circulacao_pulmonar", "tromboembolismo"),
    },
    {
        "id": "inflamatorias_pericardio_e_infecciosas",
        "label": "Doenças inflamatórias, infecciosas e do pericárdio",
        "categories": ("doenca_inflamatoria", "pericardio", "histiocitose"),
    },
    {
        "id": "cardiopatias_congenitas",
        "label": "Cardiopatias congênitas",
        "categories": ("cardiopatia_congenita",),
    },
    {
        "id": "cardiologia_pediatrica",
        "label": "Cardiologia pediátrica adquirida",
        "categories": ("cardiopatia_adquirida",),
    },
    {
        "id": "cardiologia_fetal",
        "label": "Cardiologia fetal",
        "categories": ("cardiologia_fetal",),
    },
    {
        "id": "cardio_oncologia",
        "label": "Cardio-oncologia",
        "categories": (
            "avaliacao_basal", "terapia_alvo", "toxicidade_por_tratamento",
            "sobrevivencia", "quimioterapia", "imunoterapia_celular",
            "farmacologia", "seguimento",
        ),
    },
    {
        "id": "cardiogeriatria_e_cuidado",
        "label": "Cardiogeriatria e cuidado centrado na pessoa",
        "categories": (
            "sindrome_geriatrica", "avaliacao_global", "cuidado_centrado_pessoa",
            "transicao_cuidado",
        ),
    },
    {
        "id": "emergencias_e_cuidado_critico",
        "label": "Emergências cardiovasculares e cuidado crítico",
        "categories": (
            "emergencia_neurovascular", "emergencia_e_ressuscitacao",
            "emergencia_cardiovascular", "toxicologia_cardiovascular",
        ),
    },
    {
        "id": "cardiometabolicas_e_comorbidades",
        "label": "Condições cardiometabólicas e comorbidades",
        "categories": ("comorbidade_cardiovascular",),
    },
    {
        "id": "sindromes_e_avaliacao_clinica",
        "label": "Síndromes e avaliação cardiovascular",
        "categories": (
            "sintoma_e_sindrome", "sintoma_e_exame", "sindrome_clinica",
            "avaliacao_esportiva", "planejamento_reprodutivo", "planejamento",
        ),
    },
)


CLINICAL_DOMAIN_BY_ID = {
    str(domain["id"]): domain for domain in CLINICAL_DOMAINS
}
CATEGORY_TO_CLINICAL_DOMAIN = {
    str(category): str(domain["id"])
    for domain in CLINICAL_DOMAINS
    for category in domain["categories"]
}


def categories_for_domain(domain_id: str) -> tuple[str, ...]:
    domain = CLINICAL_DOMAIN_BY_ID.get(domain_id)
    if domain is None:
        return ()
    return tuple(str(category) for category in domain["categories"])
