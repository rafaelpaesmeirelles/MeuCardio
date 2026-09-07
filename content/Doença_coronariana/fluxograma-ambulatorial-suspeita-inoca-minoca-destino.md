---
title: "Fluxograma ambulatorial: suspeita de INOCA/MINOCA — PS vs. via especializada"
slug: fluxograma-ambulatorial-suspeita-inoca-minoca-destino
theme: "Doença_coronariana"
kind: fluxograma
fonte_producao: grok
summary: "Árvore de consultório: alarme de SCA/MINOCA → PS; sintoma estável após angiografia sem obstrução → escalada para RM/teste funcional invasivo — sem reabrir endótipos nem doses."
review_status: pendente_revisao
review_note: "Irmão do protocolo suspeita-ambulatorial-inoca-minoca-quando-escalar (07/09/2026), além de #843/#874. ESC 2024 CCS PMID 39210710; ESC 2023 ACS PMID 37622654; AHA MINOCA PMID 30913893; CorMicA PMID 30266608."
source_refs:
  - "Vrints C, Andreotti F, Koskinas KC, et al. 2024 ESC Guidelines for the management of chronic coronary syndromes. Eur Heart J. 2024;45(36):3415-3537. DOI: 10.1093/eurheartj/ehae177. PMID: 39210710"
  - "Byrne RA, Rossello X, Coughlan JJ, et al. 2023 ESC Guidelines for the management of acute coronary syndromes. Eur Heart J. 2023;44(38):3720-3826. DOI: 10.1093/eurheartj/ehad191. PMID: 37622654"
  - "Tamis-Holland JE, Jneid H, Reynolds HR, et al. Contemporary Diagnosis and Management of Patients With Myocardial Infarction in the Absence of Obstructive Coronary Artery Disease. Circulation. 2019;139(18):e891-e908. DOI: 10.1161/CIR.0000000000000670. PMID: 30913893"
  - "Ford TJ, Stanley B, Good R, et al. Stratified Medical Therapy Using Invasive Coronary Function Testing in Angina: The CorMicA Trial. J Am Coll Cardiol. 2018;72(23 Pt A):2841-2855. DOI: 10.1016/j.jacc.2018.09.006. PMID: 30266608"
---

# Fluxograma ambulatorial: suspeita de INOCA/MINOCA — destino

Prosa: [`suspeita-ambulatorial-inoca-minoca-quando-escalar`](suspeita-ambulatorial-inoca-minoca-quando-escalar.md). Pós-angiografia: [`pos-angiografia-sem-obstrucao-ambulatorial-alarme-e-encaminhamento`](pos-angiografia-sem-obstrucao-ambulatorial-alarme-e-encaminhamento.md). Diagnóstico: [`anoca-inoca-angina-e-isquemia-sem-obstrucao-coronariana-esc-2024`](anoca-inoca-angina-e-isquemia-sem-obstrucao-coronariana-esc-2024.md). MINOCA hospitalar: [`fluxograma-minoca-investigacao-diagnostica`](fluxograma-minoca-investigacao-diagnostica.md).

## Árvore de decisão

```mermaid
flowchart TD
  R0["Consulta ambulatorial<br/>angina/isquemia + coronárias sem obstrução<br/>ou alta suspeita de ANOCA/INOCA"] --> D1{"Alarme de SCA / MINOCA agudo?<br/>repouso · crescendo · nitrato sem alívio<br/>ECG isquêmico novo · equivalentes"}

  D1 -->|"Sim ou dúvida fundamentada"| C1(["Encaminhar AGORA ao PS<br/>MINOCA/SCA de trabalho<br/>Não teste ergométrico ambulatorial<br/>Não aguardar RM eletiva"])

  D1 -->|"Não"| D2{"Sintoma isquêmico persistente<br/>ou QoL comprometida após<br/>angiografia sem obstrução?"}

  D2 -->|"Não — assintomático / explicação clara"| C2(["Plano usual de prevenção<br/>Reforçar alarmes escritos<br/>Retorno conforme rede"])

  D2 -->|"Sim"| D3{"História de troponina / MINOCA<br/>ou dúvida de miocardite/Takotsubo?"}

  D3 -->|"Sim"| C3(["Escalar: RM cardíaca prioritária<br/>+ retorno precoce<br/>Ver fluxograma-minoca-investigacao"])

  D3 -->|"Não"| C4(["Escalar: centro com teste funcional<br/>invasivo / expertise ANOCA-INOCA<br/>ESC 2024 · CorMicA — sem doses aqui"])

  C3 --> D4{"Acesso a RM / retorno garantidos?"}
  C4 --> D4
  D4 -->|"Não / piora / novo alarme"| C5(["Antecipar retorno 24–72 h<br/>ou PS se surgir alarme"])
  D4 -->|"Sim"| C6(["Manter via eletiva dirigida<br/>Lista escrita PS vs. telefone"])

  classDef conduta fill:#eef6ef,stroke:#2f7a4f,color:#12301f;
  classDef alerta fill:#fdecea,stroke:#b3261e,color:#3b0a0a;
  class C1,C5 alerta;
  class C2,C3,C4,C6 conduta;
```

## Notas

- **D1** = gate de segurança (ESC 2023 ACS / ESC 2024 CCS): anatomia prévia sem obstrução **não** cancela SCA/MINOCA agudo.
- **D2–D3** = braço estável: AHA MINOCA (trabalho diagnóstico) + ESC 2024 (CFT quando mecanismo incerto / sintomas persistentes).
- **D4** = operacional local — não decide endótipo nem farmacoterapia.
- Não reabre limiares de CFR/IMR, ACh provocativo nem vias 0/1 h de troponina.
