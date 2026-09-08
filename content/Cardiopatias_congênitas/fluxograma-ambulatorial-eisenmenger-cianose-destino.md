---
title: "Fluxograma ambulatorial Eisenmenger/cianose: sintoma novo → destino"
slug: fluxograma-ambulatorial-eisenmenger-cianose-destino
theme: "Cardiopatias congênitas"
kind: fluxograma
fonte_producao: grok
summary: "Árvore de consultório: adulto com Eisenmenger/cianose crônica + sintoma ou mudança de status → PS+ACHD agora vs. escalação urgente ao centro vs. retorno de rotina com reforço do que não fazer."
review_status: revisado
review_note: "Revisão científica/adversarial 08/09/2026: findings PR876 reconstruídos; urgência, bibliografia e limites revistos. Fonte grok preservada."
source_refs:
  - "Baumgartner H, De Backer J, Babu-Narayan SV, et al; ESC Scientific Document Group. 2020 ESC Guidelines for the management of adult congenital heart disease. Eur Heart J. 2021;42(6):563-645. DOI: 10.1093/eurheartj/ehaa554. PMID: 32860028"
  - "Humbert M, Kovacs G, Hoeper MM, et al; ESC/ERS Scientific Document Group. 2022 ESC/ERS Guidelines for the diagnosis and treatment of pulmonary hypertension. Eur Heart J. 2022;43(38):3618-3731. DOI: 10.1093/eurheartj/ehac237. PMID: 36017548"
---

# Fluxograma ambulatorial Eisenmenger/cianose: destino

Prosa: [`sinalizadores-ambulatoriais-eisenmenger-cianose-quando-escalar`](/biblioteca/sinalizadores-ambulatoriais-eisenmenger-cianose-quando-escalar). Braço o-que-não-fazer: [`eisenmenger-cianose-ambulatorial-o-que-nao-fazer-sem-doses`](/biblioteca/eisenmenger-cianose-ambulatorial-o-que-nao-fazer-sem-doses). ACHD geral (#845): [`sinalizadores-ambulatoriais-em-cardiopatia-congenita-do-adulto-quando-encaminhar`](/biblioteca/descompensacao-aguda-da-sindrome-de-eisenmenger-e-cardiopatia-cianotica). Hospitalar: [`descompensacao-aguda-da-sindrome-de-eisenmenger-e-cardiopatia-cianotica`](/biblioteca/descompensacao-aguda-da-sindrome-de-eisenmenger-e-cardiopatia-cianotica).

## Árvore de decisão

```mermaid
flowchart TD
  R0["Consulta ambulatorial<br/>Eisenmenger ou cianose crônica<br/>+ sintoma novo / mudança de status"] --> D1{"Mudança aguda vs. basal?<br/>queda significativa persistente vs basal · hemoptise relevante/recorrente · síncope<br/>déficit focal · instabilidade"}

  D1 -->|"Sim ou dúvida fundamentada"| C1(["PS / emergência AGORA<br/>Estabilizar localmente<br/>Contatar centro ACHD imediatamente"])

  D1 -->|"Não"| D2{"Piora progressiva estável?<br/>esforço ↓ · edema insidioso<br/>arritmia não sustentada sem repercussão<br/>nunca visto em ACHD"}

  D2 -->|"Sim"| C2(["Escalar URGENTE ao centro ACHD<br/>Não esperar retorno anual<br/>Reavaliar HAP / arritmia / ferro"])

  D2 -->|"Não"| D3{"Planejamento de risco?<br/>gestação · cirurgia eletiva<br/>viagem / altitude · acesso IV"}

  D3 -->|"Sim"| C3(["Aconselhamento no ACHD<br/>Gestação em Eisenmenger/HAP: desaconselhada<br/>Outras cianóticas: avaliação individual<br/>Filtros de ar em linhas IV"])
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

## Critérios de precedência

Hemoptise nova, mesmo pequena e autolimitada, recebe avaliação urgente no mesmo dia; PS se relevante, recorrente, queda de Hb/saturação, repercussão ou acesso inseguro. Seguimento ambulatorial só após avaliação e plano explícito. Cianose crônica usa basal individual, não alvo de SpO₂ 100%. Oxigênio não é rotina apenas pelo número, mas pode ser necessário em situação aguda ou benefício documentado. Flebotomia somente em contexto de hiperviscosidade moderada/grave, após excluir desidratação e ferropenia, pelo centro com reposição volêmica; Ht alto isolado não indica. Arritmia atrial/trombo exigem balanço trombose–sangramento, não anticoagulação automática. Gestação assintomática em Eisenmenger/HAP pede prioridade ACHD/Pregnancy Heart Team, não PS só por gestação. Eliminar ar e usar filtro em linha IV.
