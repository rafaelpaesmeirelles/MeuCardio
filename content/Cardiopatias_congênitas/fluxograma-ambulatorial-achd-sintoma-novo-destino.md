---
slug: fluxograma-ambulatorial-achd-sintoma-novo-destino
title: 'Fluxograma ambulatorial ACHD: sintoma novo → destino'
kind: fluxograma
theme: Cardiopatias congênitas
summary: 'Árvore de consultório: sintoma novo em ACHD → PS+ACHD agora vs. escalação eletiva ao centro vs. retorno
  de rotina; ramo Fontan com limiar baixo.'
tags: []
source_refs:
- 'Baumgartner H; De Backer J; Babu-Narayan SV. 2020 ESC Guidelines for the management of adult congenital heart
  disease. Eur Heart J. 2021;42:563. DOI: 10.1093/eurheartj/ehaa554. PMID: 32860028.'
- 'De Backer J, et al. 2025 ESC Guidelines for the management of cardiovascular disease and pregnancy. DOI: 10.1093/eurheartj/ehaf193.'
evidence_level: null
source_tier: A
review_status: revisado
gaps: []
published: true
---

# Fluxograma ambulatorial ACHD: sintoma novo → destino

Prosa: [sinalizadores-ambulatoriais-em-cardiopatia-congenita-do-adulto-quando-encaminhar](/biblioteca/sinalizadores-ambulatoriais-em-cardiopatia-congenita-do-adulto-quando-encaminhar). Braço Fontan: [sinalizadores-ambulatoriais-pos-fontan-quando-escalar](/biblioteca/sinalizadores-ambulatoriais-pos-fontan-quando-escalar). Hub: [cardiopatia-congenita-do-adulto-achd-manejo-abrangente-esc-2020](/biblioteca/cardiopatia-congenita-do-adulto-achd-manejo-abrangente-esc-2020).

## Árvore de decisão

```mermaid
flowchart TD
  R0["Consulta ambulatorial<br/>adulto com cardiopatia congênita<br/>+ sintoma novo ou mudança de status"] --> D1{"Instabilidade<br/>ou sinal de alarme, inclusive hemoptise relevante,<br/>hipoxemia ou deterioração rápida?"}

  D1 -->|"Sim"| C1(["PS / emergência AGORA<br/>Estabilizar localmente<br/>Contatar centro ACHD imediatamente"])

  D1 -->|"Não"| D2{"Circulação de Fontan<br/>ou univentricular?"}

  D2 -->|"Sim"| D3{"Edema não explicado, queda de esforço,<br/>arritmia nova, cianose, hemoptise<br/>ou nova complicação objetiva (trombo, fígado, enteropatia)?"}
  D3 -->|"Sim"| C2(["Escalar URGENTE ao centro ACHD<br/>Avaliação hemodinâmica especializada;<br/>cateterismo conforme mecanismo, não automático"])
  D3 -->|"Não"| C3(["Manter/agendar seguimento ACHD<br/>Não delegar complicação só ao ambulatório geral"])

  D2 -->|"Não"| D4{"Sintoma novo estável, arritmia documentada<br/>em lesão moderada/grave, mudança objetiva de função/gradiente/trombo<br/>ou nunca visto em ACHD?"}
  D4 -->|"Sim"| C4(["Contatar centro ACHD e definir prioridade<br/>Sintoma/alteração nova: avaliação rápida<br/>Primeira avaliação estável: agendar nível de cuidado"])
  D4 -->|"Não"| C5(["Retorno de rotina conforme nível já definido<br/>Reforçar sinais de alarme por escrito"])

  classDef conduta fill:#eef6ef,stroke:#2f7a4f,color:#12301f;
  classDef alerta fill:#fdecea,stroke:#b3261e,color:#3b0a0a;
  classDef urgente fill:#fff4e5,stroke:#b86e00,color:#3b2500;
  class C1 alerta;
  class C2 urgente;
  class C3,C4,C5 conduta;
```

## Notas

- **D1** = gate de segurança (ESC 2020: não atrasar tratamento de instabilidade).
- **D2/D3** = ramo Fontan com limiar baixo (edema, esforço, arritmia nova, cianose, hemoptise).
- **D4** = separar alteração nova, que exige avaliação prioritária conforme gravidade, da primeira avaliação de paciente estável sem complicação. Trombo novo exige contato imediato com especialista para definir tratamento e necessidade de hospitalização, sem aguardar fila eletiva.
- Não decide lesão-específico de intervenção nem doses.

## Informação para transferência e gravidez

Informar anatomia, cirurgias/intervenções, shunts/conduits/fenestração, dispositivos, arritmias, anticoagulação e saturação/hemodinâmica basais. Gestação requer estratificação mWHO e Pregnancy Heart Team conforme ESC 2025; estabilidade não elimina necessidade de revisão especializada. Hemoptise pequena nova no Fontan/cianótico exige avaliação rápida com baixa tolerância à espera; gravidade e acesso definem hospitalização.
