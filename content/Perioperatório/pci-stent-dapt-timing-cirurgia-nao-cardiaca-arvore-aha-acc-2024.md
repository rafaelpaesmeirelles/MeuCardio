---
title: "PCI, stent e DAPT: timing da cirurgia não cardíaca — AHA/ACC 2024"
slug: pci-stent-dapt-timing-cirurgia-nao-cardiaca-arvore-aha-acc-2024
theme: "Perioperatório"
kind: documento
fonte_producao: chatgpt
review_status: revisado
review_note: "Verificado por Claude/Grupo A em 08/08/2026: fonte primaria conferida no PubMed via E-utilities (titulo/revista/data exatos) ou DOI conferido contra a diretriz/consenso real quando muito recente para ter PMID; checado contra o corpus canonico para excluir duplicacao de escore/estudo ja publicado; doses cruzadas contra conhecimento clinico estabelecido, sem divergencia encontrada."
revisado_por_voce: false
summary: "Árvore prática para decidir timing de cirurgia não cardíaca após angioplastia/stent e manejo perioperatório de antiagregação conforme AHA/ACC 2024."
source_refs:
  - "Thompson A, Fleischmann KE, Smilowitz NR, et al. 2024 AHA/ACC/ACS/ASNC/HRS/SCA/SCCT/SCMR/SVM Guideline for Perioperative Cardiovascular Management for Noncardiac Surgery. Circulation. 2024;150:e351-e442. PMID: 39316661. DOI: 10.1161/CIR.0000000000001285."
---

# Cirurgia não cardíaca após PCI

O risco perioperatório após PCI depende de quatro informações que precisam aparecer no formulário pré-operatório:

1. **quando** a PCI foi realizada;
2. se houve **balão sem stent, BMS ou DES**;
3. se a indicação foi **síndrome coronariana aguda (SCA)** ou **doença coronária crônica (CCD)**;
4. se a cirurgia exige **interromper um ou mais antiagregantes**.

O simples rótulo “tem stent” é insuficiente.

## Timing recomendado pela AHA/ACC 2024

### Angioplastia por balão sem stent

Cirurgia não cardíaca eletiva deve ser adiada por **pelo menos 14 dias**.

### DES implantado por síndrome coronariana aguda

Se a cirurgia eletiva exige interrupção de pelo menos um antiagregante, o ideal é adiar por **≥12 meses** após a PCI.

### DES implantado por doença coronária crônica

Se a cirurgia eletiva exige interrupção de antiagregação, é razoável adiar por **≥6 meses**.

### Cirurgia tempo-sensível após DES

Quando atrasar a cirurgia traz risco clínico relevante e será necessário interromper antiagregação, a cirurgia **pode ser considerada a partir de ≥3 meses** após PCI em pacientes selecionados, após ponderar MACE versus consequência do atraso.

### Primeiros 30 dias após qualquer stent

Cirurgia eletiva que exija interrupção de um ou mais antiagregantes em paciente com BMS ou DES implantado há **≤30 dias** é considerada **potencialmente danosa** pelo alto risco de trombose do stent e complicações isquêmicas.

## Árvore de decisão

```mermaid
flowchart TD
    A["Paciente com PCI prévia candidato a cirurgia não cardíaca"] --> B["Confirmar data, indicação da PCI,<br/>tipo de intervenção e antiagregantes em uso"]
    B --> C{"Foi apenas angioplastia por balão<br/>sem stent?"}
    C -->|"Sim"| D{"≥14 dias desde a angioplastia?"}
    D -->|"Não"| E["Adiar cirurgia eletiva se possível"]
    D -->|"Sim"| F["Prosseguir para avaliação de risco/antiagregação"]
    C -->|"Não"| G{"Há stent coronário?"}
    G -->|"Não"| F
    G -->|"Sim"| H{"Cirurgia exige interromper<br/>aspirina ou P2Y12?"}
    H -->|"Não"| I["Planejar cirurgia mantendo terapia<br/>quando risco hemorrágico permitir"]
    H -->|"Sim"| J{"Tempo desde PCI ≤30 dias?"}
    J -->|"Sim"| K["Cirurgia eletiva com interrupção é potencialmente danosa;<br/>adiar se clinicamente possível"]
    J -->|"Não"| L{"DES foi implantado por SCA?"}
    L -->|"Sim"| M{"≥12 meses?"}
    M -->|"Sim"| F
    M -->|"Não"| N{"Cirurgia é tempo-sensível<br/>e ≥3 meses desde PCI?"}
    N -->|"Não"| O["Preferir adiar; discussão multidisciplinar"]
    N -->|"Sim"| P["Pode ser considerada se risco do atraso<br/>supera risco de MACE"]
    L -->|"Não — CCD"| Q{"≥6 meses?"}
    Q -->|"Sim"| F
    Q -->|"Não"| R{"Cirurgia tempo-sensível e ≥3 meses?"}
    R -->|"Sim"| P
    R -->|"Não"| O
    F --> S["Definir plano de antiagregação em equipe"]
    I --> S
    P --> S
    S --> T["Se possível, manter AAS 75–100 mg em paciente com PCI prévia"]
    T --> U{"Cirurgia tempo-sensível dentro de<br/><30 d BMS ou <3 meses DES?"}
    U -->|"Sim"| V["Manter DAPT se possível,<br/>salvo risco hemorrágico que supere benefício"]
    U -->|"Não"| W["Se P2Y12 precisar ser interrompido,<br/>usar janela farmacológica apropriada"]
```

## Continuação de aspirina e DAPT

AHA/ACC 2024 recomenda, em pacientes com PCI prévia submetidos a cirurgia não cardíaca:

- **continuar aspirina 75–100 mg, se possível**, para reduzir eventos cardíacos;
- em cirurgia tempo-sensível dentro de **30 dias de PCI com BMS** ou **<3 meses de PCI com DES**, **DAPT deve ser mantida** quando o risco cirúrgico de sangramento permitir;
- em situações selecionadas de muito alto risco trombótico após PCI, ponte com antiagregante intravenoso **pode ser considerada**, mas a evidência é limitada e exige equipe especializada.

## Tempo mínimo aproximado após interrupção para recuperação plaquetária

A tabela da AHA/ACC 2024 apresenta:

| Fármaco | Tempo mínimo da interrupção até recuperação da função plaquetária |
|---|---:|
| Aspirina | 4 dias |
| Clopidogrel | 5–7 dias |
| Prasugrel | 7–10 dias |
| Ticagrelor | 3–5 dias |

Esses intervalos **não são uma ordem automática para interromper**. Primeiro decide-se se a interrupção é aceitável; somente depois se aplica a janela farmacológica.

## Situações que exigem discussão multidisciplinar

- cirurgia oncológica ou outra cirurgia tempo-sensível;
- PCI recente por infarto/SCA;
- PCI complexa;
- necessidade de interromper DAPT precocemente;
- cirurgia com risco hemorrágico catastrófico;
- histórico de trombose de stent;
- impossibilidade de recuperar detalhes da PCI anterior.

## Regra prática

**Em paciente com stent, a pergunta mais importante não é “pode operar?”, mas “qual é a relação entre urgência da cirurgia, idade/indicação da PCI e necessidade de interromper antiagregação?”.** A resposta deve ser construída em conjunto por cardiologia, cirurgia, anestesia e paciente.
