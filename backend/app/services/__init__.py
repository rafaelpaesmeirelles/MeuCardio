"""Inicialização dos serviços clínicos adicionais produzidos pelo ChatGPT."""

from . import calculators as calculators
from .perioperative_calculators_geriatria import GERIATRIC_PERIOPERATIVE_REGISTRY

calculators.REGISTRY.update(GERIATRIC_PERIOPERATIVE_REGISTRY)
