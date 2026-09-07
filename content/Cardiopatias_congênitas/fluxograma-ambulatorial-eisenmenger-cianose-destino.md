---
title: "Fluxograma ambulatorial Eisenmenger/cianose: sintoma novo → destino"
slug: fluxograma-ambulatorial-eisenmenger-cianose-destino
theme: "Cardiopatias congênitas"
kind: fluxograma
fonte_producao: grok
summary: "Árvore de consultório: adulto com Eisenmenger/cianose crônica + sintoma ou mudança de status → PS+ACHD agora vs. escalação urgente ao centro vs. retorno de rotina com reforço do que não fazer."
review_status: pendente_revisao
review_note: "Irmão dos protocolos sinalizadores Eisenmenger/cianose e o-que-não-fazer (07/09/2026), além de #845. Fontes: ESC ACHD 2020 PMID 32860028; ESC/ERS PH 2022 PMID 36017548. Sem doses."
source_refs:
  - "Baumgartner H, De Backer J, Babu-Narayan SV, et al; ESC Scientific Document Group. 2020 ESC Guidelines for the management of adult congenital heart disease. Eur Heart J. 2021;42(6):563-645. DOI: 10.1093/eurheartj/ehaa554. PMID: 32860028"
  - "Humbert M, Kovacs G, Hoeper MM, et al; ESC/ERS Scientific Document Group. 2022 ESC/ERS Guidelines for the diagnosis and treatment of pulmonary hypertension. Eur Heart J. 2022;43(38):3618-3731. DOI: 10.1093/eurheartj/ehac237. PMID: 36017548"
---

# Fluxograma ambulatorial Eisenmenger/cianose: destino

Prosa: [`sinalizadores-ambulatoriais-eisenmenger-cianose-quando-escalar`](sinalizadores-ambulatoriais-eisenmenger-cianose-quando-escalar.md). Braço o-que-não-fazer: [`eisenmenger-cianose-ambulatorial-o-que-nao-fazer-sem-doses`](eisenmenger-cianose-ambulatorial-o-que-nao-fazer-sem-doses.md). ACHD geral (#845): [`sinalizadores-ambulatoriais-em-cardiopatia-congenita-do-adulto-quando-encaminhar`](sinalizadores-ambulatoriais-em-cardiopatia-congenita-do-adulto-quando-encaminhar.md). Hospitalar: [`descompensacao-aguda-da-sindrome-de-eisenmenger-e-cardiopatia-cianotica`](descompensacao-aguda-da-sindrome-de-eisenmenger-e-cardiopatia-cianotica.md).

## Árvore de decisão

```mermaid
flowchart TD
  R0["Consulta ambulatorial<br/>Eisenmenger ou cianose crônica<br/>+ sintoma novo / mudança de status"] --> D1{"Mudança aguda vs. basal?<br/>SpO₂ caiu · hemoptise · síncope<br/>déficit focal · instabilidade"}

  D1 -->|"Sim ou dúvida fundamentada"| C1(["PS / emergência AGORA<br/>Estabilizar localmente<br/>Contatar centro ACHD imediatamente"])

  D1 -->|"Não"| D2{"Piora progressiva estável?<br/>esforço ↓ · edema insidioso<br/>arritmia nova · hemoptise leve<br/>nunca visto em ACHD"}

  D2 -->|"Sim"| C2(["Escalar URGENTE ao centro ACHD<br/>Não esperar retorno anual<br/>Reavaliar HAP / arritmia / ferro"])

  D2 -->|"Não"| D3{"Planejamento de risco?<br/>gestação · cirurgia eletiva<br/>viagem / altitude · acesso IV"}

  D3 -->|"Sim"| C3(["Aconselhamento no ACHD<br/>Gestação: ESC/ERS — não recomendada<br/>Filtros de ar em linhas IV"])
  D3 -->|"Não"| C4(["Retorno de rotina no ACHD<br/>Reforçar basal escrito + alarmes<br/>Ver o-que-não-fazer"])

  classDef conduta fill:#eef6ef,stroke:#2f7a4f,color:#12301f;
  classDef alerta fill:#fdecea,stroke:#b3261e,color:#3b0a0a;
  classDef urgente fill:#fff4e5,stroke:#b86e00,color:#3b2500;
  class C1 alerta;
  class C2,C3 urgente;
  class C4 conduta;
```

## Notas

- **D1** = gate de segurança (mudança vs. basal — ESC ACHD 2020).
- **D2** = escalação urgente ao centro ACHD sem instabilidade franca.
- **D3** = aconselhamento (gestação, procedimentos, embolia paradoxal) — ESC/ERS PH 2022.
- Não decide doses de terapia de HAP, anticoagulação, flebotomia terapêutica nem O₂ contínuo.
