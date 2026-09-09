---
title: "Fluxograma ambulatorial pós-PCI: PS agora vs. retorno precoce"
slug: fluxograma-ambulatorial-pos-pci-destino-ps-vs-retorno
theme: "Doença_coronariana"
kind: fluxograma
fonte_producao: grok
summary: "Árvore de consultório após ICP: gate de trombose de stent/SCA e sangramento/acesso → PS; padrão estável → retorno precoce — sem reabrir doses de DAPT nem vias hospitalares de reperfusão."
review_status: pendente_revisao
review_note: "Irmão do protocolo sinalizadores-ambulatoriais-pos-pci-quando-encaminhar (07/09/2026), além de #843. ESC 2023 ACS PMID 37622654; ESC 2024 CCS PMID 39210710; ESC/EACTS 2018 PMID 30165437."
source_refs:
  - "Byrne RA, Rossello X, Coughlan JJ, et al. 2023 ESC Guidelines for the management of acute coronary syndromes. Eur Heart J. 2023;44(38):3720-3826. DOI: 10.1093/eurheartj/ehad191. PMID: 37622654"
  - "Vrints C, Andreotti F, Koskinas KC, et al. 2024 ESC Guidelines for the management of chronic coronary syndromes. Eur Heart J. 2024;45(36):3415-3537. DOI: 10.1093/eurheartj/ehae177. PMID: 39210710"
  - "Neumann FJ, Sousa-Uva M, Ahlsson A, et al; ESC Scientific Document Group. 2018 ESC/EACTS Guidelines on myocardial revascularization. Eur Heart J. 2019;40(2):87-165. DOI: 10.1093/eurheartj/ehy394. PMID: 30165437"
---

# Fluxograma ambulatorial pós-PCI: destino

Prosa: [`sinalizadores-ambulatoriais-pos-pci-quando-encaminhar`](sinalizadores-ambulatoriais-pos-pci-quando-encaminhar.md). Acesso/sangramento: [`acesso-e-sangramento-pos-pci-ambulatorial-alarme-sem-doses`](acesso-e-sangramento-pos-pci-ambulatorial-alarme-sem-doses.md). Angina/pós-IAM (#843): [`sinalizadores-ambulatoriais-de-angina-instabilizando-quando-encaminhar`](sinalizadores-ambulatoriais-de-angina-instabilizando-quando-encaminhar.md).

## Árvore de decisão

```mermaid
flowchart TD
  R0["Consulta / contato ambulatorial<br/>após PCI (eletiva ou SCA)"] --> D1{"Alarme isquêmico?<br/>repouso · crescendo · nitrato sem alívio<br/>ECG isquêmico novo · equivalentes"}

  D1 -->|"Sim ou dúvida fundamentada"| C1(["Encaminhar AGORA ao PS<br/>Suspeita trombose de stent / SCA<br/>Não teste ergométrico ambulatorial"])

  D1 -->|"Não"| D2{"Alarme de acesso ou sangramento?<br/>hematoma expansivo · massa pulsátil<br/>flanco + hipotensão · sangramento maior"}

  D2 -->|"Sim"| C2(["Encaminhar AGORA ao PS<br/>Não suspender DAPT no consultório<br/>Ver braço acesso/sangramento"])

  D2 -->|"Não"| D3{"Sintoma limítrofe ou dúvida<br/>de acesso estável / adesão?"}

  D3 -->|"Sim"| C3(["Retorno 24–72 h<br/>Orientação escrita de alarmes<br/>Revisar adesão sem mudar doses aqui"])
  D3 -->|"Não"| C4(["Plano usual pós-PCI<br/>Reforçar alarmes<br/>Retorno conforme rede"])

  C3 --> D4{"Acesso a medicação<br/>e retorno garantidos?"}
  D4 -->|"Não / fragilidade / piora"| C5(["Antecipar retorno 24 h<br/>ou PS se surgir alarme"])
  D4 -->|"Sim"| C6(["Manter retorno 24–72 h<br/>Lista escrita PS vs. telefone"])

  classDef conduta fill:#eef6ef,stroke:#2f7a4f,color:#12301f;
  classDef alerta fill:#fdecea,stroke:#b3261e,color:#3b0a0a;
  class C1,C2,C5 alerta;
  class C3,C4,C6 conduta;
```

## Notas

- **D1** = gate de segurança isquêmico (ESC 2023 ACS / ESC 2024 CCS): trombose de stent até prova em contrário.
- **D2** = gate vascular/hemorrágico pós-procedimento (ESC/EACTS 2018 + prática de acesso).
- **D3–D4** = braço estável com retorno precoce — não decide duração de DAPT nem escolha de P2Y12.
- Não reabre 0/1 h de troponina, timing NSTE nem estratégia de reperfusão.
