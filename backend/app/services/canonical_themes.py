"""Taxonomia canônica de `theme` para `documents` (auditoria de 02/09/2026,
Parte C da correção coordenada).

Os 30 valores abaixo são exatamente os temas hoje em uso por `documents`
publicados (conferido por SQL contra produção em 02/09/2026: `SELECT DISTINCT
theme FROM documents WHERE published`). Servem dois propósitos:

1. Restringir o `theme` gerado pelo pipeline `corvia-intelligence`
   (`guideline_clinical_update.py`) a este enum, para que nenhum documento
   novo repita o incidente dos 22 documentos de 02/09/2026 — cada um com uma
   frase única em vez de um tema real, o que os deixava sem qualquer relação
   por tema com o resto do acervo.
2. Classificar retroativamente um texto (tema livre + título) num destes 30
   valores, para o backfill único dos 22 documentos afetados — função
   genérica, reaproveitável por qualquer conteúdo futuro que precise da mesma
   normalização, não específica a nenhum documento.
"""
from __future__ import annotations

import re
import unicodedata

TEMAS_CANONICOS: tuple[str, ...] = (
    "Aorta e doença arterial periférica",
    "Arritmias",
    "Calculadoras",
    "Cardiologia do Esporte e do Exercício",
    "Cardiologia geriátrica",
    "Cardiologia pediátrica",
    "Cardiomiopatias",
    "Cardio-oncologia",
    "Cardiopatias congênitas",
    "Comunicação clínica",
    "Diabetes e cardiologia",
    "Dispositivos",
    "Doença coronariana",
    "Endocardite",
    "Farmacologia",
    "Febre reumática",
    "Fibrilação atrial",
    "Geral",
    "Gravidez",
    "Hipertensão",
    "Hipertensão pulmonar",
    "Insuficiência cardíaca",
    "Pericárdio",
    "Perioperatório",
    "Prevenção e lipídios",
    "Saúde mental e cardiologia",
    "Síncope",
    "Terapia intensiva",
    "Tromboembolismo",
    "Valvopatias",
)

TEMA_PADRAO = "Geral"

# Termos característicos por tema, usados só na classificação retroativa
# (item 2 do docstring do módulo) — o pipeline em si passa a exigir que o
# próprio modelo escolha um destes 30 valores (item 1), o que tende a ser
# mais preciso que casamento de palavra-chave. Ordem importa: o primeiro tema
# cujos termos aparecerem no texto vence, então termos mais específicos vêm
# antes de termos genéricos que poderiam capturar demais. Termos com acento
# são normalizados junto com o texto de entrada — escritos aqui na grafia
# natural só por legibilidade, nunca comparados literalmente.
_TERMOS_POR_TEMA: tuple[tuple[str, tuple[str, ...]], ...] = (
    ("Calculadoras", ("calculadora", "escore de risco", "score de risco")),
    ("Cardio-oncologia", ("cardio-oncolog", "cardiooncolog", "carcinoma", "quimioterap", "antracicl", "oncolog", "câncer")),
    ("Cardiologia geriátrica", ("geriatr", "idoso", "fragilidade", "frágil", "nonagenar", "centenári")),
    ("Cardiologia pediátrica", ("pediatr", "criança", "infânc", "adolescen")),
    ("Cardiopatias congênitas", ("cardiopatia congênita", "guch", "congênit")),
    ("Gravidez", ("gravidez", "gestante", "gestação", "puerper", "materna")),
    ("Perioperatório", ("perioperatóri", "pré-operatóri", "pós-operatóri", "sangramento perioperatório")),
    ("Terapia intensiva", ("terapia intensiva", "\\buti\\b", "\\buco\\b", "cuidados críticos", "choque cardiogênico")),
    ("Diabetes e cardiologia", ("diabetes", "diabét", "glicêmi", "insulin")),
    ("Hipertensão pulmonar", ("hipertensão pulmonar",)),
    ("Hipertensão", ("hipertens", "pressão arterial")),
    ("Fibrilação atrial", ("fibrilação atrial", "\\bfa\\b", "anticoagulação")),
    ("Arritmias", ("arritmia", "antiarrítmic", "taquicardia", "bradicardia", "\\btsv\\b")),
    ("Cardiomiopatias", ("cardiomiopatia", "amiloidose", "miocardiopat")),
    ("Insuficiência cardíaca", ("insuficiência cardíaca", "\\bicfep\\b", "\\bicfer\\b", "\\bicfem\\b")),
    ("Doença coronariana", ("coronária", "infarto", "síndrome coronariana", "angina", "\\biam\\b")),
    # Endocardite antes de Valvopatias de propósito: "endocardite ... valvar"/
    # "prótese valvar" batem nos dois, e o diagnóstico mais específico
    # (infecção) deve vencer sobre o mais genérico (doença estrutural).
    ("Endocardite", ("endocardite",)),
    ("Valvopatias", ("valvopat", "valvar", "\\bvalva\\b", "estenose mitral", "regurgitação mitral")),
    ("Pericárdio", ("pericárdi",)),
    ("Tromboembolismo", ("tromboembolismo", "trombose", "\\btep\\b", "\\btev\\b", "trombólise", "trombectomia")),
    ("Aorta e doença arterial periférica", ("aorta", "arterial periférica", "aneurisma")),
    ("Dispositivos", ("marca-passo", "marcapasso", "\\bcdi\\b", "ressincroniz", "dispositivo implant", "dispositivo")),
    ("Cardiologia do Esporte e do Exercício", ("esporte", "exercício físico", "atleta")),
    ("Prevenção e lipídios", ("prevenção", "lipíd", "colesterol", "vacina", "estatina", "rastreamento")),
    ("Saúde mental e cardiologia", ("saúde mental", "depress", "ansiedade", "estresse psicossocial", "estressor psicossocial")),
    ("Comunicação clínica", ("comunicação clínica", "autogestão", "adesão")),
    ("Síncope", ("síncope",)),
    ("Febre reumática", ("febre reumátic", "cardiopatia reumátic")),
    ("Farmacologia", ("farmacolog", "posologia", "interação medicamentosa")),
)


def _normalizar(texto: str) -> str:
    sem_acento = "".join(
        c for c in unicodedata.normalize("NFD", texto or "")
        if unicodedata.category(c) != "Mn"
    )
    return sem_acento.casefold()


def _termo_para_regex(termo: str) -> str:
    # Termos já escritos como regex de fronteira de palavra (\b...\b) passam
    # direto; os demais (frases/prefixos livres) só precisam ser normalizados
    # e escapados antes de virar um padrão literal.
    if termo.startswith("\\b"):
        return _normalizar(termo)
    return re.escape(_normalizar(termo))


_PADROES_POR_TEMA: tuple[tuple[str, re.Pattern], ...] = tuple(
    (tema, re.compile("|".join(_termo_para_regex(termo) for termo in termos)))
    for tema, termos in _TERMOS_POR_TEMA
)


def classificar_tema_canonico(*textos: str) -> str:
    """Classifica um texto livre (tema gerado + título, tipicamente) num dos
    30 temas canônicos, por presença de termo característico com fronteira de
    palavra (evita falso positivo tipo "uti" dentro de "semaglutida"). Sem
    correspondência clara, cai em `TEMA_PADRAO` ("Geral") — mesma filosofia de
    `content_areas.matching_area_ids`: nunca inventa uma classificação
    específica sem sinal textual real."""
    texto_normalizado = _normalizar(" ".join(t for t in textos if t))
    for tema, padrao in _PADROES_POR_TEMA:
        if padrao.search(texto_normalizado):
            return tema
    return TEMA_PADRAO
