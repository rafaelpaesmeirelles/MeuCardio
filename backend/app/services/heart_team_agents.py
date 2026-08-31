"""Agent registry and prompts for independent Heart Team deliberation."""

from __future__ import annotations

from copy import deepcopy
from dataclasses import dataclass


@dataclass(frozen=True)
class HeartTeamAgent:
    key: str
    name: str
    remit: str
    mandatory: bool = False
    model_tier: str = "clinical"


AGENTS: dict[str, HeartTeamAgent] = {
    "coordinator": HeartTeamAgent("coordinator", "Coordenador clínico", "Sintetizar consenso sem apagar divergências.", True),
    "heart_failure": HeartTeamAgent("heart_failure", "Insuficiência cardíaca e cardiomiopatias", "Fenótipos, etiologia, descompensação e terapias."),
    "electrophysiology": HeartTeamAgent("electrophysiology", "Arritmias e eletrofisiologia", "Ritmo, risco arrítmico, dispositivos e eletrofisiologia."),
    "imaging": HeartTeamAgent("imaging", "Imagem cardiovascular", "Adequação, qualidade e interpretação de métodos de imagem."),
    "critical_care": HeartTeamAgent("critical_care", "Cardiologia intensiva e emergências", "Instabilidade, prioridades e sinais de gravidade."),
    "pharmacology": HeartTeamAgent("pharmacology", "Farmacologia e segurança terapêutica", "Interações, contraindicações e ajustes renal/hepático."),
    "evidence": HeartTeamAgent("evidence", "Evidências e diretrizes", "Reabrir fontes e validar DOI, PMID, data, população e resultados.", True),
    "red_team": HeartTeamAgent("red_team", "Agente crítico / red team", "Procurar erros, contraindicações, extrapolações e afirmações sem respaldo.", True),
}

DEFAULT_SPECIALISTS = [
    "heart_failure", "electrophysiology", "imaging", "critical_care", "pharmacology",
]


def selected_agent_keys(selected: list[str] | None) -> list[str]:
    chosen = [key for key in (selected or DEFAULT_SPECIALISTS) if key in AGENTS and key != "coordinator"]
    for mandatory in ("evidence", "red_team"):
        if mandatory not in chosen:
            chosen.append(mandatory)
    return list(dict.fromkeys(chosen))


def independent_round_inputs(snapshot: dict, agent_keys: list[str]) -> dict[str, dict]:
    """Deep isolated inputs: no specialist sees a peer's first-round answer."""
    return {key: deepcopy(snapshot) for key in agent_keys}


BASE_SYSTEM = """
Você integra o CorVIA Heart Team Virtual, apoio à decisão exclusivo do médico.
Nunca se comunique como se falasse com o paciente, nunca prescreva, nunca
substitua validação humana e nunca invente dose, probabilidade, resultado,
classe ou nível de evidência. Use somente source_ids fornecidos. Quando não
houver comprovação adequada, escreva literalmente 'evidência insuficiente'.
Responda SOMENTE JSON válido com: summary, alerts, differential_diagnoses,
missing_data, additional_tests, therapeutic_options, safety, claims,
source_ids, confidence, limitations, human_decisions. Cada claim deve conter
statement, source_ids e position (support|oppose|uncertain).
""".strip()


def specialist_prompt(agent_key: str) -> str:
    agent = AGENTS[agent_key]
    return f"{BASE_SYSTEM}\nPapel: {agent.name}. Escopo: {agent.remit}"


def contestation_prompt(agent_key: str) -> str:
    return (
        f"{BASE_SYSTEM}\nVocê é {AGENTS[agent_key].name}. Reavalie sua posição à luz das objeções "
        "fornecidas, mantendo divergências justificadas. Não adote a maioria por concordância social."
    )


COORDINATOR_SYSTEM = f"""{BASE_SYSTEM}
Você é o coordenador. Preserve pareceres individuais, todas as divergências,
as objeções do red team e a validação de evidências. Não crie recomendação nova.
Além das chaves-base, retorne final_consensus e divergences.
"""

