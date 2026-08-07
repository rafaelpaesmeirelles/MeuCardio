"""Doses de antiagregantes orais na SCA — ACC/AHA 2025.

A diretriz contém uma discrepância interna no limite etário do clopidogrel
associado à fibrinólise: a Tabela 7 usa carga de 300 mg se idade <=75 anos,
enquanto o texto de suporte descreve carga para <75 e ausência de carga para
>=75. Para idade exatamente 75 anos esta calculadora retorna literalmente
VERIFICAÇÃO HUMANA NECESSÁRIA.

Fonte de produção: ChatGPT.
"""

from __future__ import annotations

from .calculators import Calculator, Field

FONTE_PRODUCAO = "chatgpt"

ACC_AHA_ACS_2025 = (
    "Rao SV, O'Donoghue ML, Ruel M, et al. 2025 ACC/AHA/ACEP/NAEMSP/SCAI Guideline for the "
    "Management of Patients With Acute Coronary Syndromes. J Am Coll Cardiol. 2025. "
    "doi:10.1016/j.jacc.2024.11.009. Table 7 and Section 4.3.2."
)


def _antiagregante_sca_2025(d: dict) -> dict:
    farmaco = d["farmaco"]
    fibrinolise = bool(d.get("fibrinolise"))
    idade = float(d["idade"])
    peso = float(d["peso"])
    pci = bool(d.get("pci"))
    if idade <= 0 or peso <= 0:
        raise ValueError("Idade e peso precisam ser maiores que zero.")

    if farmaco == "aas":
        return {
            "farmaco": "AAS",
            "carga": "162-325 mg VO",
            "administracao_carga": "preferir comprimido não entérico e mastigar quando possível",
            "manutencao": "75-100 mg VO 1x/dia",
        }

    if farmaco == "clopidogrel":
        if fibrinolise:
            if idade < 75:
                return {
                    "farmaco": "Clopidogrel",
                    "cenario": "STEMI com fibrinólise, idade <75 anos",
                    "carga": "300 mg VO",
                    "manutencao": "75 mg VO 1x/dia",
                }
            if idade > 75:
                return {
                    "farmaco": "Clopidogrel",
                    "cenario": "STEMI com fibrinólise, idade >75 anos",
                    "carga": "sem dose de ataque; dose inicial 75 mg VO",
                    "manutencao": "75 mg VO 1x/dia",
                }
            return {
                "farmaco": "Clopidogrel",
                "cenario": "STEMI com fibrinólise, idade exatamente 75 anos",
                "conduta": "VERIFICAÇÃO HUMANA NECESSÁRIA",
                "motivo": (
                    "ACC/AHA 2025 é internamente discrepante no corte: Tabela 7 diz carga 300 mg se idade <=75; "
                    "texto de suporte diz carga para <75 e sem carga para >=75."
                ),
            }
        return {
            "farmaco": "Clopidogrel",
            "cenario": "SCA sem fibrinólise",
            "carga": "300 ou 600 mg VO",
            "manutencao": "75 mg VO 1x/dia",
        }

    if farmaco == "ticagrelor":
        if fibrinolise:
            return {
                "farmaco": "Ticagrelor",
                "conduta": "nao_modelado_como_carga_imediata_pos_fibrinolitico",
                "motivo": (
                    "Tabela 7 do ACC/AHA 2025 fornece 180 mg de carga para NSTE-ACS/STEMI sem fibrinolítico; "
                    "o texto discute transição pós-fibrinólise em condições específicas, que não deve ser confundida "
                    "com carga imediata no momento do lítico."
                ),
            }
        return {
            "farmaco": "Ticagrelor",
            "carga": "180 mg VO",
            "manutencao": "90 mg VO 2x/dia",
            "aas_manutencao": "usar AAS <=100 mg/dia quando associado, segundo a diretriz consultada",
        }

    # prasugrel
    if fibrinolise:
        return {
            "farmaco": "Prasugrel",
            "conduta": "nao_modelado_como_carga_imediata_pos_fibrinolitico",
            "motivo": "Tabela 7 restringe o esquema de prasugrel a NSTE-ACS/STEMI sem fibrinolítico e submetido a PCI.",
        }
    if not pci:
        return {
            "farmaco": "Prasugrel",
            "conduta": "requer_pci_no_cenario_da_tabela",
            "motivo": "ACC/AHA 2025 modela prasugrel neste contexto para paciente submetido a PCI.",
        }
    manutencao = "5 mg VO 1x/dia" if (peso < 60 or idade >= 75) else "10 mg VO 1x/dia"
    return {
        "farmaco": "Prasugrel",
        "carga": "60 mg VO",
        "manutencao": manutencao,
        "motivo_reducao": (
            "peso <60 kg e/ou idade >=75 anos; usar cautela" if manutencao.startswith("5") else "nenhum critério de redução da Tabela 7"
        ),
    }


def _antiagregante_sca_2025_txt(r: dict) -> str:
    if r.get("conduta") == "VERIFICAÇÃO HUMANA NECESSÁRIA":
        return f"VERIFICAÇÃO HUMANA NECESSÁRIA — {r['motivo']}"
    if r.get("conduta"):
        return f"{r['farmaco']}: nenhuma dose sugerida neste cenário — {r['motivo']}"
    texto = f"{r['farmaco']}: carga {r['carga']}; manutenção {r['manutencao']}"
    if r.get("administracao_carga"):
        texto += f". Carga: {r['administracao_carga']}"
    if r.get("aas_manutencao"):
        texto += f". {r['aas_manutencao']}"
    if r.get("motivo_reducao"):
        texto += f". {r['motivo_reducao']}"
    return texto + "."


_ANTIAGREGANTE_SCA_2025 = Calculator(
    slug="antiagregante-oral-sca-acc-aha-2025",
    name="Antiagregantes orais na SCA — AAS, clopidogrel, prasugrel e ticagrelor (ACC/AHA 2025)",
    theme="Doses — Cardiologia Geral",
    purpose="Seleciona carga/manutenção conforme fármaco, fibrinólise, idade, peso e realização de PCI.",
    fields=[
        Field("farmaco", "Fármaco", "select", options=[
            {"value": "aas", "label": "AAS"},
            {"value": "clopidogrel", "label": "Clopidogrel"},
            {"value": "prasugrel", "label": "Prasugrel"},
            {"value": "ticagrelor", "label": "Ticagrelor"},
        ]),
        Field("fibrinolise", "STEMI tratado com fibrinolítico", "boolean"),
        Field("pci", "Paciente está sendo submetido a PCI", "boolean"),
        Field("idade", "Idade", "number", "anos", min=18, max=120),
        Field("peso", "Peso", "number", "kg", min=20, max=300),
    ],
    compute=_antiagregante_sca_2025,
    interpret=_antiagregante_sca_2025_txt,
    reference=ACC_AHA_ACS_2025,
    kind="dose",
    limitations=[
        "Esta calculadora reproduz doses da Tabela 7 e texto de suporte ACC/AHA 2025; não decide qual P2Y12 é preferível para cada paciente.",
        "Clopidogrel + fibrinólise aos exatos 75 anos retorna VERIFICAÇÃO HUMANA NECESSÁRIA pela discrepância interna da diretriz no sinal de igualdade do corte etário.",
        "Prasugrel aqui é modelado apenas em SCA sem fibrinolítico e com PCI, como na Tabela 7.",
        "Contraindicações individuais, história de sangramento, AVC/AIT, anticoagulação concomitante, necessidade de cirurgia e interações devem ser checadas fora desta calculadora.",
        "Para ticagrelor, a diretriz consultada recomenda AAS de manutenção <=100 mg/dia quando usados em conjunto.",
    ],
)


ANTIAGREGANTES_SCA_2025_DOSE_REGISTRY: dict[str, Calculator] = {
    _ANTIAGREGANTE_SCA_2025.slug: _ANTIAGREGANTE_SCA_2025
}
