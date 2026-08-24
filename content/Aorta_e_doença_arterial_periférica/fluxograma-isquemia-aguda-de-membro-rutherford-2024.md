---
title: "Fluxograma: Isquemia Aguda de Membro — Viabilidade, Rutherford e Reperfusão"
slug: fluxograma-isquemia-aguda-de-membro-rutherford-2024
theme: "Aorta e doença arterial periférica"
kind: fluxograma
summary: "Fluxo emergencial de isquemia aguda de membro: reconhecimento clínico, classificação da viabilidade, heparina salvo contraindicação, revascularização do membro salvável e investigação etiológica sem atrasar reperfusão."
review_status: revisado
source_refs: ["Gornik HL, Aronow HD, Goodney PP, et al. 2024 ACC/AHA/AACVPR/APMA/ABC/SCAI/SVM/SVN/SVS/SIR/VESS Guideline for the Management of Lower Extremity Peripheral Artery Disease. Circulation. 2024;149(24):e1313-e1410. DOI: 10.1161/CIR.0000000000001251. PMID: 38743805.", "Mazzolai L, Teixido-Tura G, Lanzi S, et al. 2024 ESC Guidelines for the management of peripheral arterial and aortic diseases. Eur Heart J. 2024;45(36):3538-3700. DOI: 10.1093/eurheartj/ehae179. PMID: 39210722."]
---

# Fluxograma: Isquemia Aguda de Membro — Viabilidade, Rutherford e Reperfusão

Este é o fluxograma específico do módulo `isquemia-aguda-de-membro-classificacao-de-rutherford-e-conduta`. A prioridade é **viabilidade do membro e tempo para reperfusão**, não confirmação anatômica antes de acionar a equipe vascular.

## Árvore de decisão

```mermaid
flowchart TD
  R0["Suspeita de ALI<br/>dor aguda, palidez, membro frio,<br/>pulso reduzido/ausente, parestesia ou déficit motor"] --> A0["Acionar avaliação vascular emergencial<br/>examinar perfusão, sensibilidade e força<br/>+ Doppler arterial/venoso à beira do leito"]

  A0 --> D0{"Há anestesia profunda,<br/>paralisia/rigidez e ausência de sinais<br/>arterial E venoso ao Doppler?"}

  D0 -->|Sim| C0(["Rutherford III — membro não salvável<br/>NÃO revascularizar tecido inviável<br/>avaliar manejo cirúrgico e repercussão sistêmica"])

  D0 -->|Não| D1{"Há déficit motor<br/>ou perda sensitiva além dos artelhos?"}

  D1 -->|Sim| A1["Rutherford IIb provável<br/>membro imediatamente ameaçado"]
  A1 --> C1(["Revascularização imediata<br/>pela estratégia mais adequada/disponível<br/>NÃO atrasar por investigação extensa"])

  D1 -->|Não| D2{"Há perda sensitiva mínima<br/>com força preservada e sinal venoso presente?"}

  D2 -->|Sim| A2["Rutherford IIa provável<br/>membro marginalmente ameaçado"]
  A2 --> C2(["Revascularização pronta/urgente<br/>imagem anatômica somente se útil<br/>sem atraso desnecessário"])

  D2 -->|Não| A3["Rutherford I provável<br/>membro viável, sem déficit sensitivo-motor"]
  A3 --> C3(["Definir anatomia e estratégia com urgência adequada<br/>manter reavaliação seriada porque a classe pode piorar"])

  A0 --> D3{"Há contraindicação relevante<br/>à anticoagulação sistêmica?"}
  D3 -->|Não| C4(["Iniciar heparina não fracionada sistêmica<br/>ACC/AHA 2024: Classe I, C-EO<br/>enquanto a estratégia definitiva é organizada"])
  D3 -->|Sim| C5(["Não aplicar regra automática de heparina<br/>individualizar risco hemorrágico/trauma/dissecção<br/>com equipe responsável"])

  C1 --> A4["Após reperfusão: vigiar síndrome compartimental,<br/>rabdomiólise, hipercalemia, acidose e lesão renal"]
  C2 --> A4
  C3 --> A4

  A4 --> D4{"Causa provável já está definida?"}
  D4 -->|"Embolia suspeita"| C6(["Investigar fonte cardioembólica/aórtica<br/>FA, trombo intracardíaco, valvopatia/endocardite,<br/>aorta/aneurisma — sem atrasar salvamento"])
  D4 -->|"Trombose local suspeita"| C7(["Avaliar DAP prévia, stent/enxerto,<br/>aneurisma, acesso vascular, trauma<br/>e estados pró-trombóticos"])
  D4 -->|Não| C8(["História/exame etiológico + investigação dirigida<br/>e plano de prevenção de recorrência"])

  classDef conduta fill:#eef5f8,stroke:#1c7293,color:#0b2e45;
  class C0,C1,C2,C3,C4,C5,C6,C7,C8 conduta;
```

## Pontos que o fluxograma protege

### 1. Não esperar imagem avançada para reconhecer ameaça imediata

A ACC/AHA 2024 recomenda avaliação emergencial de viabilidade — **Classe I, C-EO** — e afirma que a avaliação inicial pode ser realizada **sem duplex, angio-TC ou angio-RM — Classe I, C-LD**.

A imagem anatômica é útil quando modifica a estratégia e existe tempo. Ela não deve atrasar revascularização de Rutherford IIb.

### 2. Heparina é recomendada, mas não possui evidência randomizada direta

Na ALI, heparina não fracionada sistêmica é recomendada salvo contraindicação — **Classe I, C-EO**. A diretriz explicita que esse uso se baseia em prática aceita e prevenção de propagação/embolização adicional, não em ensaio randomizado contra nenhuma anticoagulação.

O CorVIA deve apresentar simultaneamente **a força da recomendação e a limitação da evidência**.

### 3. Rutherford III não significa “amputar automaticamente pela tabela”

O princípio de guideline é: **não revascularizar membro não salvável — Classe III: dano, C-EO**. Manejo cirúrgico definitivo depende de avaliação vascular, extensão de tecido inviável, repercussão sistêmica, dor/infecção e objetivos de cuidado.

### 4. Reperfusão não encerra o episódio

Após restauração de fluxo, vigiar síndrome compartimental e repercussão metabólica. Depois, investigar a causa para prevenir recorrência. A investigação cardiovascular de fonte embólica pode ser útil — **Classe IIa, C-LD** — mas jamais deve atrasar salvamento do membro.

## Conexões no CorVIA

- documento especializado: `isquemia-aguda-de-membro-classificacao-de-rutherford-e-conduta`;
- porta sindrômica: `fluxograma-dor-membro-claudicacao-clti-isquemia-aguda`;
- DAP crônica: `doenca-arterial-periferica-de-membros-diagnostico-por-itb-e-isquemia-critica`;
- fibrilação atrial e fontes cardioembólicas;
- endocardite e doença valvar;
- aortopatias e aneurisma poplíteo;
- cardio-oncologia: `isquemia-aguda-de-membro-e-doenca-arterial-por-nilotinibe-ou-ponatinibe`;
- futura entrada `isquemia-aguda-de-membro` no modo Emergência.

## Limites

- Rutherford deve ser reavaliado seriamente se a intervenção não for imediata;
- a classificação não escolhe sozinha a técnica de revascularização;
- este fluxograma não contém posologia de anticoagulante ou trombolítico;
- protocolos locais de cirurgia vascular/intervenção e capacidade de transferência continuam determinantes.
