---
kind: fluxograma
published: true
review_note: Conferidos PREVENT artigo integral/37947085 e AHA 2025; corrigida amostra
  de validação (3.330.085, total 6.612.004), escopo de DCV total 10 anos e faixa 30–79.
  Confirmado estágio B PAS<130 I A ESC 2026. Fluxo distingue início de manutenção
  e usa PAS ou PAD, com individualização e urgência. Removidas alegações de software
  por strings e comorbidades obrigatórias; STAMP não é escore.
review_status: revisado
slug: fluxograma-inicio-de-farmaco-aha-2025-prevent
source_refs:
- 'Jones DW et al. J Am Coll Cardiol. 2025;86(18):1567-1678. DOI: 10.1016/j.jacc.2025.05.007.
  PMID: 40815242.'
- 'Khan SS et al. Circulation. 2024;149(6):430-449. PMID: 37947085.'
- AHA/ACC 2025 hipertensão, texto integral. https://nefro.cl/web/docs/AHA_Hypertension_Guidelines_2025%5B1%5D.pdf
theme: Hipertensão
title: 'Fluxograma: iniciar fármaco na HAS — AHA/ACC 2025 e PREVENT ≥7,5%'
---

# Fluxograma: iniciar fármaco na HAS — AHA/ACC 2025 e PREVENT ≥7,5%

## Árvore de decisão

```mermaid
flowchart TD
  R0["Adulto não gestante, sem tratamento:<br/>PA média confirmada, incluindo medidas fora do consultório quando indicadas"] --> D1{"Categoria"}
  D1 -->|"PAS <130 e PAD <80"| C1(["Estilo de vida. Sem fármaco por HAS neste degrau"])
  D1 -->|"PAS >=140 ou PAD >=90"| D2{"Fragilidade, institucionalização ou vida limitada?"}
  D2 -->|"Não"| C2(["Fármaco + estilo de vida. Meta menor que 130/80"])
  D2 -->|"Sim"| C3(["Decisão compartilhada de início/intensidade<br/>e meta individualizada"])
  D1 -->|"130-139 ou 80-89"| D3{"DCV, AVC, diabetes, DRC ou PREVENT >=7,5%?"}
  D3 -->|"Sim"| D4{"Fragilidade, institucionalização ou vida limitada?"}
  D4 -->|"Não"| C4(["Fármaco + estilo de vida agora. Meta menor que 130/80"])
  D4 -->|"Sim"| C5(["Decisão compartilhada de início/intensidade<br/>e meta individualizada"])
  D3 -->|"Não"| P1["Estilo de vida 3 a 6 meses"]
  P1 --> D5{"PAS permanece >=130 ou PAD >=80?"}
  D5 -->|"Não"| C6(["Manter estilo de vida e reavaliar"])
  D5 -->|"Sim"| C7(["Iniciar fármaco conforme benefício e tolerância.<br/>Meta usual <130/80, individualizar se fragilidade"])
  classDef conduta fill:#eef6ef,stroke:#2f7a4f,color:#12301f;
  class C1,C2,C3,C4,C5,C6,C7 conduta;
```

## Tudo com Tudo

Hipertensão · Prevenção e lipídios · Diabetes e cardiologia · Cardiorrenal · Comunicação clínica.
A árvore aborda início eletivo; PA grave com lesão aguda de órgão-alvo exige atendimento de emergência. Em quem já usa fármacos, PA controlada não é indicação de retirada. Não calcular PREVENT em gestação, DCV estabelecida ou fora de 30–79 anos; em idosos além dessa faixa, avaliar benefício/dano e objetivos de cuidado. A categoria é determinada pelo componente sistólico ou diastólico mais elevado.
