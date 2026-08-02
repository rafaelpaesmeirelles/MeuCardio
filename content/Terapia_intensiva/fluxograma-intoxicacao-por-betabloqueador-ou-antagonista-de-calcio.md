---
title: "Intoxicação por betabloqueador ou antagonista de cálcio"
slug: fluxograma-intoxicacao-por-betabloqueador-ou-antagonista-de-calcio
theme: "Terapia intensiva"
kind: fluxograma
summary: "Árvore de decisão do choque cardiotóxico por betabloqueador ou bloqueador de canal de cálcio: atropina, glucagon e cálcio geralmente falham no paciente grave, a insulina em alta dose euglicêmica é a terapia central, e emulsão lipídica ou suporte circulatório mecânico (ECMO) entram como resgate no choque refratário."
review_status: revisado
source_refs: ["Engebretsen KM, Kaczmarek KM, Morgan J, Holger JS. High-dose insulin therapy in beta-blocker and calcium channel-blocker poisoning. Clin Toxicol (Phila). 2011;49(4):277-283. DOI: 10.3109/15563650.2011.582471. PMID: 21563902 — revisão de 485 artigos identificados, 72 considerados relevantes", "American College of Medical Toxicology (ACMT). Position Statement: Guidance for the Use of Intravenous Lipid Emulsion. J Med Toxicol. 2017;13(1):124-125. DOI: 10.1007/s13181-016-0550-z. PMID: 27121236 — recomenda emulsão lipídica IV como resgate em intoxicação por fármaco lipofílico cardiotóxico, incluindo betabloqueador e bloqueador de canal de cálcio, com instabilidade hemodinâmica refratária à ressuscitação padrão (volume, inotrópico, vasopressor)", "Sepulveda EA, Pak A. Lipid Emulsion Therapy. [Updated 2024 Feb 16]. In: StatPearls [Internet]. Treasure Island (FL): StatPearls Publishing; 2026 Jan-. NBK549897 — esquema de dose da emulsão lipídica a 20% (bólus e infusão) usado neste fluxograma", "Torre DE, Mangino D, Pirri C. Veno-Arterial Extracorporeal Membrane Oxygenation in Cardiotoxic Drug-Induced Cardiogenic Shock: A Systematic Narrative Review. Life (Basel). 2025;15(6):925. DOI: 10.3390/life15060925. PMID: 40566578 — ECMO veno-arterial como resgate no choque cardiogênico refratário por intoxicação, incluindo betabloqueador e bloqueador de canal de cálcio"]
---

# Intoxicação por betabloqueador ou antagonista de cálcio

Gatilho para este protocolo: **bradicardia com hipotensão refratária** ou
**choque cardiogênico** em paciente com ingestão ou uso de **betabloqueador**
ou **bloqueador de canal de cálcio**. O reflexo convencional (atropina,
glucagon, cálcio) costuma decepcionar no paciente gravemente intoxicado — o
que muda o desfecho é a **insulina em alta dose euglicêmica**, considerada
terapia inicial/central pela revisão de Engebretsen et al.

## Árvore de decisão

```mermaid
flowchart TD
  R["Choque cardiotóxico por betabloqueador ou<br/>bloqueador de canal de cálcio: hipotensão,<br/>bradicardia e resistência vascular sistêmica reduzida"]
  R --> A1

  A1["Ressuscitação volêmica com solução salina<br/>(medida essencial) + monitorização contínua<br/>e acesso venoso calibroso"]
  A1 --> B1

  B1["Tentar atropina para a bradicardia<br/>(geralmente pouco eficaz nesta intoxicação);<br/>glucagon e cálcio IV também podem ser<br/>considerados — atropina, glucagon e cálcio<br/>frequentemente FALHAM no paciente gravemente<br/>intoxicado (fonte não diferencia a eficácia de<br/>cada fármaco entre betabloqueador e bloqueador<br/>de canal de cálcio — VERIFICAÇÃO HUMANA NECESSÁRIA)"]
  B1 --> D1

  D1{"Choque grave ou refratário<br/>às medidas convencionais?"}
  D1 -->|"Não — resposta hemodinâmica adequada"| C1
  D1 -->|"Sim — choque grave/refratário"| B2

  C1(["Manter volume e atropina/glucagon/cálcio<br/>conforme resposta, com monitorização<br/>hemodinâmica contínua"])

  B2["Iniciar insulina em alta dose euglicêmica:<br/>bólus de 1 U/kg seguido de infusão contínua<br/>de 1 a 10 U/kg/h — terapia inicial/central<br/>nesta intoxicação"]
  B2 --> D2

  D2{"Hipotensão/choque persiste apesar<br/>de volume e insulina em alta dose?"}
  D2 -->|"Não — estabilizou"| C2
  D2 -->|"Sim — choque persiste"| B3

  C2(["Manter insulina em alta dose com volume,<br/>e monitorização hemodinâmica e<br/>laboratorial seriada"])

  B3["Associar vasopressor/suporte inotrópico,<br/>titulado com cautela — catecolaminas elevam<br/>a resistência vascular sistêmica e a demanda<br/>miocárdica de oxigênio, podendo reduzir<br/>o débito cardíaco"]
  B3 --> D3

  D3{"Choque refratário mesmo com<br/>vasopressor/inotrópico associado?"}
  D3 -->|"Não — estabilizou"| C3
  D3 -->|"Sim — choque refratário"| B4

  C3(["Manter suporte combinado (volume, insulina<br/>em alta dose, vasopressor titulado) com<br/>monitorização contínua"])

  B4["Emulsão lipídica IV a 20% como resgate:<br/>bólus de 1,5 mL/kg seguido de infusão de<br/>0,25 mL/kg/min, podendo repetir o bólus e<br/>dobrar a infusão se persistir instabilidade<br/>(dose cumulativa máxima ≈ 12 mL/kg)"]
  B4 --> D4

  D4{"Choque refratário mesmo com<br/>emulsão lipídica, ou risco<br/>iminente de morte?"}
  D4 -->|"Não — estabilizou"| C4
  D4 -->|"Sim"| C5

  C4(["Manter suporte combinado e monitorização;<br/>reduzir vasopressor conforme resposta"])
  C5(["Acionar suporte circulatório mecânico<br/>(ECMO veno-arterial), em centro com<br/>capacidade para tal, como resgate final"])

  classDef conduta fill:#eef6ef,stroke:#2f7a4f,color:#12301f;
  class C1,C2,C3,C4,C5 conduta;
```

## O que vale para todos os ramos, e por isso não está no diagrama

**Ressuscitação salina** mantida ao longo de todo o atendimento, não só na
medida inicial — é o que corrige a vasodilatação e as pressões de enchimento
baixas.

**Monitorização seriada de glicemia e potássio** durante toda a infusão de
insulina em alta dose. A suplementação de glicose provavelmente será
necessária durante toda a terapia e **por até 24 horas após a suspensão** da
infusão, pelo risco de hipoglicemia tardia. **A queda do potássio sob
insulina reflete deslocamento para o intracelular, não depleção dos
estoques corporais** — não repor de forma agressiva.

**A base de evidência da insulina em alta dose é animal e de relatos/séries
de casos** — não há ensaio clínico controlado publicado em humanos. Em
modelos animais, a insulina em alta dose mostrou-se superior a sais de
cálcio, glucagon, epinefrina e vasopressina em sobrevida.

**Emulsão lipídica e ECMO usadas ao mesmo tempo** exigem atenção ao circuito
— há relato de camadas, aglutinação e formação de coágulos na linha quando
as duas terapias correm juntas.

## Limites

- **A revisão-base da parte de insulina é de 2011** e declara explicitamente
  que não há ensaio clínico controlado em humanos para essa terapia.
- **O documento-fonte não diferencia a eficácia de atropina, glucagon e
  cálcio IV entre betabloqueador e bloqueador de canal de cálcio** — este
  fluxograma trata os três como classe geral nesse ponto; a diferenciação
  farmacológica clássica (por exemplo, glucagon atuando por via não
  beta-adrenérgica, mais relevante no betabloqueador) não veio das fontes
  consultadas para este documento e precisa de **VERIFICAÇÃO HUMANA
  NECESSÁRIA** antes de orientar conduta.
- **Emulsão lipídica e ECMO vêm de fontes novas**, pesquisadas especificamente
  para este fluxograma porque o documento-fonte de hipercalemia/intoxicação
  não cobre resgate em choque refratário — conferir a posologia da emulsão
  lipídica e os critérios de acionamento de ECMO do serviço antes de aplicar.
