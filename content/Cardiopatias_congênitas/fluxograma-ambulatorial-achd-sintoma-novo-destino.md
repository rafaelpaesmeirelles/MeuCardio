---
title: "Fluxograma ambulatorial ACHD: sintoma novo → destino"
slug: fluxograma-ambulatorial-achd-sintoma-novo-destino
theme: "Cardiopatias congênitas"
kind: fluxograma
fonte_producao: grok
summary: "Árvore de consultório: sintoma novo em ACHD → PS+ACHD agora vs. escalação eletiva ao centro vs. retorno de rotina; ramo Fontan com limiar baixo."
review_status: pendente_revisao
review_note: "Irmão dos protocolos sinalizadores ACHD e pós-Fontan (07/09/2026). Fonte: ESC ACHD 2020 PMID 32860028. Sem doses."
source_refs:
  - "Baumgartner H, De Backer J, Babu-Narayan SV, et al; ESC Scientific Document Group. 2020 ESC Guidelines for the management of adult congenital heart disease. Eur Heart J. 2021;42(6):563-645. DOI: 10.1093/eurheartj/ehaa554. PMID: 32860028"
---

# Fluxograma ambulatorial ACHD: sintoma novo → destino

Prosa: [`sinalizadores-ambulatoriais-em-cardiopatia-congenita-do-adulto-quando-encaminhar`](sinalizadores-ambulatoriais-em-cardiopatia-congenita-do-adulto-quando-encaminhar.md). Braço Fontan: [`sinalizadores-ambulatoriais-pos-fontan-quando-escalar`](sinalizadores-ambulatoriais-pos-fontan-quando-escalar.md). Hub: [`cardiopatia-congenita-do-adulto-achd-manejo-abrangente-esc-2020`](cardiopatia-congenita-do-adulto-achd-manejo-abrangente-esc-2020.md).

## Árvore de decisão

```mermaid
flowchart TD
  R0["Consulta ambulatorial<br/>adulto com cardiopatia congênita<br/>+ sintoma novo ou mudança de status"] --> D1{"Instabilidade<br/>ou sinal de alarme?"}

  D1 -->|"Sim"| C1(["PS / emergência AGORA<br/>Estabilizar localmente<br/>Contatar centro ACHD imediatamente"])

  D1 -->|"Não"| D2{"Circulação de Fontan<br/>ou univentricular?"}

  D2 -->|"Sim"| D3{"Edema não explicado, queda de esforço,<br/>arritmia nova, cianose ou hemoptise?"}
  D3 -->|"Sim"| C2(["Escalar URGENTE ao centro ACHD<br/>Limiar baixo de cateterismo ESC 2020"])
  D3 -->|"Não"| C3(["Manter/agendar seguimento ACHD<br/>Não delegar complicação só ao ambulatório geral"])

  D2 -->|"Não"| D4{"Sintoma novo estável, arritmia documentada<br/>em lesão moderada/grave, ou nunca visto em ACHD?"}
  D4 -->|"Sim"| C4(["Encaminhar eletivo ao centro ACHD<br/>Definir nível de cuidado / expertise arritmia"])
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
- **D4** = escalação eletiva / primeira avaliação em centro ACHD.
- Não decide lesão-específico de intervenção nem doses.
