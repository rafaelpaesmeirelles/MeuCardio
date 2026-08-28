"""Inicialização dos serviços clínicos adicionais produzidos pelo ChatGPT."""

from . import calculators as calculators
from .dose_calculators_acls2025_chatgpt import ACLS_2025_DOSE_REGISTRY
from .dose_calculators_antiagregantes_sca2025_chatgpt import ANTIAGREGANTES_SCA_2025_DOSE_REGISTRY
from .dose_calculators_anticoagulacao_sca2025_chatgpt import ANTICOAGULACAO_SCA_2025_DOSE_REGISTRY
from .dose_calculators_choque_cardiogenico2025_chatgpt import CHOQUE_CARDIOGENICO_2025_DOSE_REGISTRY
from .dose_calculators_diuretico_icaguda_chatgpt import DIURETICO_IC_AGUDA_DOSE_REGISTRY
from .dose_calculators_doac_brasil_chatgpt import DOAC_BRASIL_DOSE_REGISTRY
from .dose_calculators_enoxaparina_sca_chatgpt import ENOXAPARINA_SCA_DOSE_REGISTRY
from .dose_calculators_entresto_brasil_chatgpt import ENTRESTO_BRASIL_DOSE_REGISTRY
from .dose_calculators_fibrinoliticos_stemi_chatgpt import FIBRINOLITICOS_STEMI_DOSE_REGISTRY
from .dose_calculators_icfer_chatgpt import ICFER_DOSE_REGISTRY
from .dose_calculators_mra_icfer_chatgpt import MRA_ICFER_DOSE_REGISTRY
from .dose_calculators_pals2025_chatgpt import PALS_2025_DOSE_REGISTRY
from .intensive_care_brash_safety import INTENSIVE_CARE_BRASH_SAFETY_REGISTRY
from .intensive_care_calculators import INTENSIVE_CARE_CALCULATOR_REGISTRY
from .intensive_care_hyperkalemia_safety import INTENSIVE_CARE_HYPERKALEMIA_SAFETY_REGISTRY
from .perioperative_calculators_frailty import FRAILTY_PERIOPERATIVE_REGISTRY
from .perioperative_calculators_geriatria import GERIATRIC_PERIOPERATIVE_REGISTRY
from .perioperative_calculators_mortalidade import MORTALITY_PERIOPERATIVE_REGISTRY
from .perioperative_calculators_sort import SORT_PERIOPERATIVE_REGISTRY

_CHATGPT_REGISTRIES = [
    ACLS_2025_DOSE_REGISTRY,
    ANTIAGREGANTES_SCA_2025_DOSE_REGISTRY,
    ANTICOAGULACAO_SCA_2025_DOSE_REGISTRY,
    CHOQUE_CARDIOGENICO_2025_DOSE_REGISTRY,
    DIURETICO_IC_AGUDA_DOSE_REGISTRY,
    DOAC_BRASIL_DOSE_REGISTRY,
    ENOXAPARINA_SCA_DOSE_REGISTRY,
    ENTRESTO_BRASIL_DOSE_REGISTRY,
    FIBRINOLITICOS_STEMI_DOSE_REGISTRY,
    ICFER_DOSE_REGISTRY,
    MRA_ICFER_DOSE_REGISTRY,
    PALS_2025_DOSE_REGISTRY,
    INTENSIVE_CARE_BRASH_SAFETY_REGISTRY,
    INTENSIVE_CARE_CALCULATOR_REGISTRY,
    INTENSIVE_CARE_HYPERKALEMIA_SAFETY_REGISTRY,
    FRAILTY_PERIOPERATIVE_REGISTRY,
    GERIATRIC_PERIOPERATIVE_REGISTRY,
    MORTALITY_PERIOPERATIVE_REGISTRY,
    SORT_PERIOPERATIVE_REGISTRY,
]

# O dataclass Calculator legado não possui esse campo. Objetos Python sem slots
# aceitam o atributo dinamicamente, permitindo expor a origem pela API sem
# alterar retroativamente o schema de todas as calculadoras históricas.
for registry in _CHATGPT_REGISTRIES:
    for calculator in registry.values():
        calculator.fonte_producao = "chatgpt"
        calculators.REGISTRY[calculator.slug] = calculator
