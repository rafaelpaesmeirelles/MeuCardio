---
title: "Calculadoras cha2ds2 va e has bled"
slug: calculadoras-cha2ds2-va-e-has-bled
theme: "Calculadoras"
kind: calculadora
review_status: pendente_revisao
source_refs: []
legacy_source: "calculadoras/calculadoras-cha2ds2-va-e-has-bled.md"
---

# Calculadoras cha2ds2 va e has bled

# Módulo — Calculadoras CHA2DS2-VA e HAS-BLED

```json
[
  {
    "id": "calc_cha2ds2va_019",
    "nome": "CHA2DS2-VA",
    "aplicacao": "Estimativa de risco tromboembólico anual em pacientes com fibrilação atrial, escore atualizado que substitui o CHA2DS2-VASc (remove sexo feminino como fator isolado) na diretriz ESC 2024",
    "variaveis": [
      {"nome": "C — Insuficiência cardíaca congestiva/disfunção de VE", "pontos": 1},
      {"nome": "H — Hipertensão", "pontos": 1},
      {"nome": "A2 — Idade ≥75 anos", "pontos": 2},
      {"nome": "D — Diabetes mellitus", "pontos": 1},
      {"nome": "S2 — AVC/AIT/tromboembolismo prévio", "pontos": 2},
      {"nome": "V — Doença vascular (DAC, doença arterial periférica, placa aórtica)", "pontos": 1},
      {"nome": "A — Idade 65-74 anos", "pontos": 1}
    ],
    "formula": "Soma direta dos pontos (escore máximo de 9, sem o ponto de sexo feminino do CHA2DS2-VASc)",
    "interpretacao": "Escore ≥2 em homens ou mulheres geralmente indica anticoagulação recomendada; escore 1 requer avaliação individualizada; escore 0 geralmente não requer anticoagulação",
    "fonte": "ESC 2024 AF-CARE "
  },
  {
    "id": "calc_hasbled_020",
    "nome": "HAS-BLED",
    "aplicacao": "Estimativa de risco de sangramento maior em pacientes com fibrilação atrial em uso de anticoagulação, complementar (não substituto) à decisão de anticoagular",
    "variaveis": [
      {"nome": "H — Hipertensão não controlada (PAS >160 mmHg)", "pontos": 1},
      {"nome": "A — Função renal/hepática anormal (1 ponto cada)", "pontos": "1-2"},
      {"nome": "S — AVC prévio", "pontos": 1},
      {"nome": "B — História de sangramento ou predisposição", "pontos": 1},
      {"nome": "L — INR lábil (se em uso de warfarina)", "pontos": 1},
      {"nome": "E — Idade >65 anos", "pontos": 1},
      {"nome": "D — Uso de fármacos predisponentes a sangramento (AINEs/antiplaquetários) ou álcool (1 ponto cada)", "pontos": "1-2"}
    ],
    "formula": "Soma direta dos pontos (escore de 0 a 9)",
    "interpretacao": "Escore ≥3 indica alto risco de sangramento, sinalizando necessidade de monitorização mais frequente e correção de fatores de risco modificáveis, não contraindicação absoluta à anticoagulação",
    "observacao_2024": "Diretriz ESC 2024 traz mudanças na abordagem de avaliação de risco de sangramento, com foco em fatores modificáveis antes de decidir contra anticoagulação",
    "fonte": "ESC 2024 "
  }
]
```
