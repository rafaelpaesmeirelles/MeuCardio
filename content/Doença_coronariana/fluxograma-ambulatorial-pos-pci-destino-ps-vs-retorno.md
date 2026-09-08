---
title: "Fluxograma ambulatorial pós-PCI: PS agora vs. retorno precoce"
slug: fluxograma-ambulatorial-pos-pci-destino-ps-vs-retorno
theme: "Doença coronariana"
kind: fluxograma
fonte_producao: grok
summary: "Árvore de consultório após ICP: gate de trombose de stent/SCA e sangramento/acesso → PS; padrão estável → retorno precoce — sem reabrir doses de DAPT nem vias hospitalares de reperfusão."
review_status: revisado
review_note: "Revisão científica/adversarial 08/09/2026: findings PR874 reconstruídos; urgência, bibliografia e limites revistos. Fonte grok preservada."
source_refs:
  - "Byrne RA, Rossello X, Coughlan JJ, et al. 2023 ESC Guidelines for the management of acute coronary syndromes. Eur Heart J. 2023;44(38):3720-3826. DOI: 10.1093/eurheartj/ehad191. PMID: 37622654"
  - "Vrints C, Andreotti F, Koskinas KC, et al. 2024 ESC Guidelines for the management of chronic coronary syndromes. Eur Heart J. 2024;45(36):3415-3537. DOI: 10.1093/eurheartj/ehae177. PMID: 39210710"
  - "Neumann FJ, Sousa-Uva M, Ahlsson A, et al; ESC Scientific Document Group. 2018 ESC/EACTS Guidelines on myocardial revascularization. Eur Heart J. 2019;40(2):87-165. DOI: 10.1093/eurheartj/ehy394. PMID: 30165437"
---

# Fluxograma ambulatorial pós-PCI: destino

Prosa: [`sinalizadores-ambulatoriais-pos-pci-quando-encaminhar`](/biblioteca/sinalizadores-ambulatoriais-pos-pci-quando-encaminhar). Acesso/sangramento: [`acesso-e-sangramento-pos-pci-ambulatorial-alarme-sem-doses`](/biblioteca/acesso-e-sangramento-pos-pci-ambulatorial-alarme-sem-doses). Angina/pós-IAM (#843): [`sinalizadores-ambulatoriais-de-angina-instabilizando-quando-encaminhar`](/biblioteca/sindrome-coronariana-aguda-diagnostico-e-manejo-esc-2023).

## Árvore de decisão

```mermaid
flowchart TD
  R0["Consulta / contato ambulatorial<br/>após PCI (eletiva ou SCA)"] --> D1{"Alarme isquêmico?<br/>repouso · crescendo · sintoma novo/progressivo<br/>ECG isquêmico novo · equivalentes"}

  D1 -->|"Sim ou dúvida fundamentada"| C1(["Encaminhar AGORA ao PS<br/>Suspeita trombose de stent / SCA<br/>Não teste ergométrico ambulatorial"])

  D1 -->|"Não"| DA{"Síncope, pré-síncope com palpitação,<br/>edema pulmonar novo ou choque?"}
  DA -->|"Sim"| C1
  DA -->|"Não"| D2{"Alarme de acesso ou sangramento?<br/>hematoma expansivo · sangramento ativo<br/>isquemia distal (palidez/frialdade/déficit)<br/>dor nova em flanco/abdome ou hipotensão ou queda de Hb · sangramento maior"}

  D2 -->|"Sim"| C2(["Encaminhar AGORA ao PS<br/>Manejo antitrombótico pela equipe aguda<br/>Conforme gravidade e risco do stent"])

  D2 -->|"Não"| D3{"Sintoma limítrofe ou dúvida<br/>de acesso estável / adesão?"}

  D3 -->|"Sim"| C3(["Retorno em prazo individualizado<br/>Orientação escrita de alarmes<br/>Revisar adesão sem mudar doses aqui"])
  D3 -->|"Não"| C4(["Plano usual pós-PCI<br/>Reforçar alarmes<br/>Retorno conforme rede"])

  C3 --> D4{"Acesso a medicação<br/>e retorno garantidos?"}
  D4 -->|"Não / fragilidade / piora"| C5(["Antecipar retorno 24 h<br/>ou PS se surgir alarme"])
  D4 -->|"Sim"| C6(["Manter retorno prazo individualizado<br/>Lista escrita PS vs. telefone"])

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

## Classificação e acesso

Pseudoaneurisma/FAV suspeitos estáveis requerem Doppler e avaliação rápida; frêmito isolado não obriga PS. Isquemia, sangramento/expansão, compressão, infecção, IC de alto débito sintomática ou instabilidade mudam para emergência. Sangramento visível não é automaticamente maior: usar [maior, CRNM e nuisance](/biblioteca/sinalizadores-ambulatoriais-doac-sangramento-quando-encaminhar). Hematêmese/melena e sinais neurológicos requerem avaliação urgente; hematúria/epistaxe dependem de intensidade, anemia e repercussão. Não mudar DAPT por nuisance sem equipe PCI; sangramento maior segue emergência. Retornos de prazo individualizado são operacionais, nunca prazo para resolver falta do antiplaquetário.
