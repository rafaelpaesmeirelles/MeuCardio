---
title: "CARP: revascularização coronária profilática antes de cirurgia vascular"
slug: carp-revascularizacao-coronaria-profilatica-antes-de-cirurgia-vascular
theme: "Perioperatório"
kind: documento
fonte_producao: chatgpt
review_status: revisado
review_note: "Verificado por Claude/Grupo A em 08/08/2026: fonte primaria conferida no PubMed via E-utilities (titulo/revista/data exatos) ou DOI conferido contra a diretriz/consenso real quando muito recente para ter PMID; checado contra o corpus canonico para excluir duplicacao de escore/estudo ja publicado; doses cruzadas contra conhecimento clinico estabelecido, sem divergencia encontrada."
revisado_por_voce: false
summary: "Resumo do ensaio CARP e árvore para distinguir indicação coronária independente de revascularização feita apenas para reduzir risco de cirurgia não cardíaca."
source_refs:
  - "McFalls EO, Ward HB, Moritz TE, et al. Coronary-artery revascularization before elective major vascular surgery. N Engl J Med. 2004;351(27):2795-2804. PMID: 15625331. DOI: 10.1056/NEJMoa041905."
  - "Thompson A, Fleischmann KE, Smilowitz NR, et al. 2024 AHA/ACC/ACS/ASNC/HRS/SCA/SCCT/SCMR/SVM Guideline for Perioperative Cardiovascular Management for Noncardiac Surgery. Circulation. 2024;150:e351-e442. PMID: 39316661. DOI: 10.1161/CIR.0000000000001285."
---

# CARP — Coronary Artery Revascularization Prophylaxis

O CARP é um dos estudos fundamentais para evitar uma estratégia historicamente comum: detectar doença coronariana estável no pré-operatório e realizar PCI/CABG **apenas para tentar reduzir o risco da cirurgia vascular**.

O estudo testou diretamente essa hipótese.

## Desenho

Em 18 centros Veterans Affairs, pacientes com risco cardiovascular aumentado e doença coronariana clinicamente significativa que seriam submetidos a cirurgia vascular eletiva foram randomizados para:

- **revascularização coronária antes da cirurgia vascular**; ou
- **não realizar revascularização profilática** antes da cirurgia.

Dos 5.859 pacientes avaliados para operações vasculares, **510** preencheram critérios e foram randomizados.

As indicações de cirurgia vascular foram:

- aneurisma de aorta abdominal em expansão: **33%**;
- doença arterial oclusiva de membros inferiores: **67%**.

No grupo revascularização, **59%** foram tratados com PCI e **41%** com cirurgia de revascularização miocárdica.

## Resultados principais

A estratégia de revascularização atrasou a cirurgia vascular:

- mediana até a cirurgia vascular: **54 dias** no grupo revascularização;
- **18 dias** no grupo sem revascularização;
- **P<0,001**.

Após mediana de 2,7 anos:

- mortalidade após estratégia de revascularização: **22%**;
- sem revascularização profilática: **23%**;
- RR **0,98**; IC95% **0,70–1,37**; P=0,92.

IAM pós-operatório em até 30 dias da cirurgia vascular:

- revascularização: **12%**;
- sem revascularização: **14%**;
- P=0,37.

Portanto, em pacientes selecionados com **sintomas cardíacos estáveis**, a revascularização coronária profilática antes de cirurgia vascular não melhorou desfechos de longo prazo nem reduziu significativamente o IAM perioperatório.

## Árvore de decisão

```mermaid
flowchart TD
    A["Paciente candidato a cirurgia não cardíaca<br/>com DAC conhecida ou suspeita"] --> B{"Existe SCA, isquemia instável<br/>ou outra condição cardíaca aguda?"}
    B -->|"Sim"| C["Tratar condição aguda conforme diretriz de DAC/SCA;<br/>reavaliar timing da cirurgia"]
    B -->|"Não"| D["Estimar risco perioperatório + capacidade funcional"]
    D --> E{"Há indicação de investigação coronária<br/>que mudaria manejo independentemente da cirurgia?"}
    E -->|"Não"| F["Não investigar/revascularizar apenas para obter<br/>'liberação' cirúrgica"]
    E -->|"Sim"| G["Realizar investigação apropriada"]
    G --> H{"Foi identificada uma indicação de revascularização<br/>que existiria mesmo sem a cirurgia planejada?"}
    H -->|"Sim"| I["Considerar PCI/CABG conforme diretrizes de DAC,<br/>depois planejar timing da cirurgia não cardíaca"]
    H -->|"Não — DAC estável sem indicação independente"| J["Não realizar revascularização profilática<br/>apenas para reduzir risco perioperatório"]
    J --> K["Otimizar tratamento clínico + plano anestésico/cirúrgico<br/>+ monitorização conforme risco"]
    F --> K
    I --> L["Considerar implicações de DAPT,<br/>cicatrização e atraso necessário da cirurgia"]
```

## O que o CARP não significa

O estudo **não demonstra** que revascularização coronária nunca deve ser feita antes de cirurgia não cardíaca.

A interpretação correta é:

- **não criar uma indicação de PCI/CABG exclusivamente por causa da cirurgia**;
- se o paciente possui uma indicação coronária legítima e independente — por síndrome coronariana aguda, anatomia/prognóstico ou sintomas conforme as diretrizes vigentes — essa condição deve ser tratada por seus próprios méritos;
- após PCI/CABG, o novo problema passa a incluir timing cirúrgico, antiagregação e risco de interrupção da terapia antitrombótica.

## Limitações e aplicabilidade

- O CARP estudou pacientes selecionados para **cirurgia vascular eletiva** e com DAC estável suficiente para randomização.
- Populações coronarianas de risco extremo não devem ser extrapoladas mecanicamente do ensaio.
- Técnicas de PCI, stents, terapia antitrombótica e prevenção cardiovascular evoluíram desde 2004.
- O princípio do estudo, entretanto, permanece incorporado na estratégia contemporânea: **indicar revascularização pelas mesmas razões pelas quais seria indicada fora do contexto cirúrgico**.

## Regra prática

**Não transforme uma cirurgia programada em indicação de revascularização coronária.** Trate a DAC conforme sua indicação própria; a avaliação perioperatória deve evitar tanto subtratamento de doença ativa quanto procedimentos profiláticos sem benefício demonstrado.
