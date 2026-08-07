"""Inicialização dos serviços clínicos adicionais produzidos pelo ChatGPT."""

from . import calculators as calculators
from .dose_calculators_acls2025_chatgpt import ACLS_2025_DOSE_REGISTRY
from .dose_calculators_pals2025_chatgpt import PALS_2025_DOSE_REGISTRY
from .perioperative_calculators_frailty import FRAILTY_PERIOPERATIVE_REGISTRY
from .perioperative_calculators_geriatria import GERIATRIC_PERIOPERATIVE_REGISTRY
from .perioperative_calculators_mortalidade import MORTALITY_PERIOPERATIVE_REGISTRY
from .perioperative_calculators_sort import SORT_PERIOPERATIVE_REGISTRY

calculators.REGISTRY.update(ACLS_2025_DOSE_REGISTRY)
# PALS 2025 vem depois do registry legado para substituir os mesmos slugs 2020
# sem quebrar URLs/favoritos já existentes.
calculators.REGISTRY.update(PALS_2025_DOSE_REGISTRY)
calculators.REGISTRY.update(FRAILTY_PERIOPERATIVE_REGISTRY)
calculators.REGISTRY.update(GERIATRIC_PERIOPERATIVE_REGISTRY)
calculators.REGISTRY.update(MORTALITY_PERIOPERATIVE_REGISTRY)
calculators.REGISTRY.update(SORT_PERIOPERATIVE_REGISTRY)
