---
title: "Itens 12 13"
slug: itens-12-13
theme: "Farmacologia"
kind: farmacologia
review_status: pendente_revisao
source_refs: []
legacy_source: "medicamentos/banco-de-medicamentos-itens-12-13.md"
---

# Itens 12 13

# Módulo — Banco de Medicamentos (itens 12-13)

```json
[
  {
    "id": "medicamento_apixabana_012",
    "nome_generico": "Apixabana",
    "nomes_comerciais": ["Eliquis"],
    "classe": "Anticoagulante oral direto (DOAC) — inibidor direto do fator Xa",
    "mecanismo_acao": "Inibição direta, seletiva e reversível do fator Xa, tanto livre quanto ligado ao complexo protrombinase, sem necessidade de antitrombina",
    "indicacoes_cardiologicas": "Prevenção de AVC/embolismo sistêmico em FA não valvar, tratamento e prevenção de TVP/TEP",
    "apresentacoes": "2,5 mg e 5 mg (comprimidos)",
    "dose_fa": "5 mg 2x/dia (dose padrão); 2,5 mg 2x/dia se ≥2 dos critérios: idade ≥80 anos, peso ≤60 kg, creatinina sérica ≥1,5 mg/dL",
    "ajuste_renal": {
      "leve_moderada": "Nenhum ajuste de dose necessário em insuficiência renal leve ou moderada",
      "grave": "Dados clínicos limitados; uso com cautela",
      "fonte": "Bula oficial "
    },
    "ajuste_hepatico": "Não recomendado em hepatopatia associada a coagulopatia e risco de sangramento (Child-Pugh B/C)",
    "contraindicacoes": ["Sangramento ativo clinicamente significativo", "Hepatopatia com coagulopatia", "Uso concomitante de inibidores potentes duais de CYP3A4 e P-gp"],
    "interacoes": "Risco aumentado de sangramento com antiplaquetários/outros anticoagulantes; inibidores/indutores potentes de CYP3A4 e P-gp alteram exposição plasmática",
    "vantagem_relativa": "Entre os DOACs, apresenta o perfil de ajuste renal mais favorável, com critérios objetivos de redução de dose (idade, peso, creatinina) em vez de corte único por ClCr",
    "referencias": [
      {"titulo": "Apixabana: bula, para que serve e como usar", "organizacao": "Consulta Remédios/ANVISA", "url": "https://consultaremedios.com.br/apixabana/bula"}
    ]
  },
  {
    "id": "medicamento_warfarina_013",
    "nome_generico": "Warfarina",
    "nomes_comerciais": ["Marevan", "Coumadin"],
    "classe": "Anticoagulante oral — antagonista da vitamina K",
    "mecanismo_acao": "Inibição da enzima vitamina K epóxido redutase, bloqueando a regeneração da vitamina K reduzida necessária para a carboxilação dos fatores de coagulação II, VII, IX e X",
    "indicacoes_cardiologicas": "FA (especialmente valvar/prótese mecânica, onde DOACs são contraindicados), TVP/TEP, prótese valvar mecânica, trombo intracavitário",
    "monitorizacao": "INR (razão normalizada internacional), com alvo terapêutico variável conforme indicação (geralmente 2,0-3,0; até 2,5-3,5 em prótese mecânica mitral)",
    "interacoes_principais": {
      "aumentam_inr": ["Amiodarona (redução de 25-50% da dose de warfarina esperada, interação lenta ao longo de 6-8 semanas)", "Fluconazol", "Metronidazol", "Sulfametoxazol-trimetoprima", "Doxiciclina", "Fibratos", "Vacina influenza (variável)"],
      "diminuem_inr": ["Rifampicina (aumento de 2-5x na necessidade de dose)", "Carbamazepina", "Dicloxacilina (>14 dias)"],
      "risco_sangramento_aumentado": ["Antiplaquetários", "Óleo de peixe/ômega-3", "AINEs", "Outros anticoagulantes", "Corticosteroides", "Vitamina E"],
      "fonte": "UCSD Anticoagulation Clinic "
    },
    "vantagem_sobre_doacs": "Único anticoagulante oral com eficácia estabelecida em prótese valvar mecânica e algumas formas de FA valvar reumática, onde DOACs são contraindicados",
    "desafios_praticos": "Necessidade de monitorização laboratorial frequente, múltiplas interações medicamentosas e alimentares (alimentos ricos em vitamina K), maior variabilidade individual de resposta",
    "referencias": [
      {"titulo": "Warfarin Drug Interactions", "organizacao": "UCSD Health Anticoagulation Clinic", "url": "https://health.ucsd.edu/for-health-care-professionals/anticoagulation-guidelines/warfarin/drug-interactions/"}
    ]
  }
]
```

Com isso, completei três módulos substanciais nesta rodada (hipertensão, apixabana, warfarina), além dos entregues anteriormente. A busca sobre amiodarona não retornou fonte primária adequada nesta rodada — será priorizada na próxima entrega, junto com os ensaios ROCKET-AF/ARISTOTLE e o protocolo de arritmias ventriculares/morte súbita.

---
