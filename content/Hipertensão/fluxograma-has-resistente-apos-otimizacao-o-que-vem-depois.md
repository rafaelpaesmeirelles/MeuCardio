---
title: 'Fluxograma: HAS resistente após otimização — o que vem depois'
slug: fluxograma-has-resistente-apos-otimizacao-o-que-vem-depois
theme: Hipertensão
kind: fluxograma
review_status: revisado
source_refs:
- 'McEvoy JW, McCarthy CP, Bruno RM, et al.; ESC Scientific Document Group. 2024 ESC Guidelines for the management of elevated
  blood pressure and hypertension. Eur Heart J. 2024 Oct 7;45(38):3912-4018. DOI: 10.1093/eurheartj/ehae178. PMID: 39210715.'
- 'Jones DW, Ferdinand KC, Taler SJ, et al. 2025 AHA/ACC/AANP/AAPA/ABC/ACCP/ACPM/AGS/AMA/ASPC/NMA/PCNA/SGIM Guideline for
  the Prevention, Detection, Evaluation, and Management of High Blood Pressure in Adults. J Am Coll Cardiol. 2025;86(18):1567-1678.
  DOI: 10.1016/j.jacc.2025.05.007. PMID: 40815242. Também Circulation. 2025;152:e114-e218. DOI: 10.1161/CIR.0000000000001356.'
- 'Williams B, MacDonald TM, Morant S, Webb DJ, Sever P, McInnes G, Ford I, Cruickshank JK, Caulfield MJ, Salsbury J, Mackenzie
  I, Padmanabhan S, Brown MJ; British Hypertension Society''s PATHWAY Studies Group. Spironolactone versus placebo, bisoprolol,
  and doxazosin to determine the optimal treatment for drug-resistant hypertension (PATHWAY-2): a randomised, double-blind,
  crossover trial. Lancet. 2015 Nov 21;386(10008):2059-2068. DOI: 10.1016/S0140-6736(15)00257-3. PMID: 26414968. PMCID: PMC4655321.'
review_note: AHA2025 resistência/aldosteronismo e PATHWAY2 confrontados. Corrigida troca automática para eplerenona apesar
  de contraindicação ao ARM; potássio/TFGe antes de iniciar e investigação de aldosteronismo antecipada. Conexões temáticas
  selecionadas e links por slugs da fila conferidos.
summary: 'Árvore qualitativa para o adulto com pressão aparentemente não controlada em três classes. A lógica segue as diretrizes
  ESC 2024 e AHA/ACC 2025: confirmar resistência verdadeira, excluir pseudo-resistência, otimizar a tríade (tiazida-like +
  IECA ou BRA + bloqueador de cálcio) e, então, adicionar antagonista do receptor mineralocorticoide — espironolactona como
  próximo passo usual. Esta ficha não atribui Classe/COR aos nós. Números de Classe saem das diretrizes, não desta árvore.'
tags: []
source_tier: A
gaps: []
published: true
---

# Fluxograma: HAS resistente após otimização — o que vem depois

Árvore qualitativa para o adulto com **pressão aparentemente não controlada em três classes**. A lógica segue as diretrizes ESC 2024 e AHA/ACC 2025: confirmar resistência verdadeira, excluir pseudo-resistência, otimizar a tríade (tiazida-like + IECA ou BRA + bloqueador de cálcio) e, então, adicionar antagonista do receptor mineralocorticoide — espironolactona como próximo passo usual. **Esta ficha não atribui Classe/COR aos nós.** Números de Classe saem das diretrizes, não desta árvore.

Zilebesiran e lorundrostat, se aparecerem no fim, estão **rotulados como investigacionais**. Não são padrão de cuidado.

## Árvore de decisão

```mermaid
flowchart TD
    A["PA alta em 3 ou mais classes"] --> B{"Resistência verdadeira confirmada fora do consultório?"}
    B -->|"Não: técnica, adesão, jaleco branco, fármacos interferentes"| C(["Corrigir a pseudo-resistência e reavaliar"])
    B -->|"Sim"| D{"Tríade otimizada: tiazida-like + IECA ou BRA + BCC?"}
    D -->|"Não"| E(["Otimizar as 3 classes nas doses máximas toleradas"])
    D -->|"Sim"| F(["Avaliar potássio, TFGe e contraindicações; adicionar espironolactona quando elegível"])
    F --> G{"ARM tolerado e PA controlada?"}
    G -->|"Sim"| H(["Manter ARM e reavaliar PA fora do consultório"])
    G -->|"Intolerância, contra-indicação ou falha"| I(["Selecionar alternativa conforme causa da intolerância/contraindicação; investigar secundária"])
    I --> J{"Depois do ARM, o que falta?"}
    J -->|"Complexidade ou suspeita de secundária"| K(["Derivar a centro de HAS; rastrear hiperaldosteronismo"])
    J -->|"Dispositivo em selecionados"| L(["Considerar denervação renal após decisão compartilhada"])
    J -->|"Fármaco de ensaio"| M(["Zilebesiran e lorundrostat: investigacionais, não padrão de cuidado"])
    classDef conduta fill:#eef6ef,stroke:#2f7a4f,color:#12301f;
    class C,E,F,H,I,K,L,M conduta;
```

## Como ler cada ramo

**Confirmar resistência verdadeira.** PA de consultório alta em três classes, nas doses máximas toleradas, **não basta**. Confirmar fora do consultório (MAPA ou MRPA). ESC 2024 define resistência quando diurético (tiazida ou tiazida-like) + bloqueador do SRA + bloqueador de cálcio falham em baixar a PA de consultório a <140/90 mmHg, com confirmação fora do consultório. AHA/ACC 2025 trabalha com a tríade IECA/BRA + BCC + tiazida-like (clortalidona ou indapamida). Com TFGe baixa, o diurético de alça entra na definição — detalhe de diretriz, não inventado aqui.

**Excluir pseudo-resistência.** Técnica (manguito, posição, repouso), adesão (incluindo combinação em pílula única quando possível), hipertensão do avental branco e fármacos interferentes (AINE, descongestionantes, simpaticomiméticos, glicocorticoide, eritropoetina, entre outros). Enquanto a pseudo-resistência não foi excluída, **não** se rotula o caso como resistente verdadeira e **não** se avança para o quarto fármaco por esse rótulo.

**Otimizar as três classes.** Tiazida-like (indapamida ou clortalidona, conforme a diretriz em uso) + IECA ou BRA + bloqueador de cálcio di-hidropiridínico, nas doses máximas toleradas. Hidroclorotiazida em dose baixa, sem tiazida-like, **não** fecha a tríade. Otimizar o diurético conforme função renal e tolerabilidade; não atrasar o manejo de PA grave enquanto se esclarece o fenótipo.

**Adicionar ARM.** Rastrear aldosteronismo primário antes de iniciar ARM quando possível, pois esses fármacos interferem no exame; não esperar falha de quatro drogas para investigar. Espironolactona é o próximo passo **usual** na resistência verdadeira. PATHWAY-2 (PMID **26414968**) mostrou superioridade da espironolactona 25–50 mg sobre placebo, doxazosina e bisoprolol na PAS domiciliar — ensaio de pressão, não de MACE. Potássio e TFGe limitam o uso; a AHA/ACC 2025 condiciona o ARM a TFGe ≥45 mL/min/1,73 m² no recorte de resistência. Se houver efeitos endócrinos da espironolactona, eplerenona pode ser alternativa. Hipercalemia e disfunção renal também limitam eplerenona; nesses casos selecionar outra estratégia — sem hierarquia numérica nesta árvore.

**Derivar, secundária, dispositivo.** Encaminhar a centro experiente. Rastrear hiperaldosteronismo primário mesmo sem hipocalemia (mensagem da AHA/ACC 2025). Denervação renal: opção em **selecionados**, após decisão compartilhada, em centro com volume, **não** atalho para quem ainda não otimizou tríade e ARM.

**Investigacionais.** Zilebesiran (KARDIA, PAS ambulatória, fase 2) e lorundrostat (Target-HTN, Launch-HTN, Advance-HTN — PAS, não MACE) **não** substituem o ARM aprovado. Se o paciente pergunta, o rótulo é ensaio.

Nós verdes (estádio) são condutas. Losangos são decisões. Cada nó tem um único pai: quando a mesma ideia reaparece, o texto se repete em vez de fechar um ciclo.

## Tudo com Tudo

- [Fluxograma: HAS não controlada — o que o KARDIA-2 não substitui](/biblioteca/fluxograma-has-nao-controlada-o-que-kardia-2-nao-substitui)
- [Lorundrostat (Target-HTN e Advance-HTN): inibidor da sintase da aldosterona — PAS, não MACE](/biblioteca/lorundrostat-target-htn-inibidor-aldosterona-sintase)
- [Lorundrostat (Target-HTN e Launch-HTN): inibidor da sintase da aldosterona — PAS, não MACE](/biblioteca/lorundrostat-target-htn-ou-launch-htn)
- [ESC 2026 STAMP e PREVENT: duas portas de rastreio que o clínico geral não pode perder](/biblioteca/esc-2026-stamp-e-prevent-duas-portas-de-rastreio-que-o-clinico-geral-nao-pode-perder)
