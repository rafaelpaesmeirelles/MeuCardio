---
title: "Fluxograma: sinalizadores ambulatoriais de PVC frequente — PS agora vs. EP/ablation vs. vigilância"
slug: fluxograma-sinalizadores-ambulatoriais-pvc-frequente
theme: "Arritmias"
kind: fluxograma
fonte_producao: grok
summary: "Árvore ambulatorial: PVC frequente no consultório — gate de PS (síncope/TV/alto risco), via eletiva de carga/FEVE→ablation e vigilância quando carga baixa e coração normal."
review_status: pendente_revisao
review_note: "Árvore irmã dos protocolos de PVC ambulatorial (07/09/2026), além #839/#864/#867. Complementa o fluxograma revisado de indicação de ablação sem duplicar classes. ESC 2022 PMID 36017572; HRS 2019 PMID 32071620; Baman PMID 20348027. Sem doses."
source_refs:
  - "Zeppenfeld K, Tfelt-Hansen J, de Riva M, et al. 2022 ESC Guidelines for the management of patients with ventricular arrhythmias and the prevention of sudden cardiac death. Eur Heart J. 2022;43(40):3997-4126. DOI: 10.1093/eurheartj/ehac262. PMID: 36017572"
  - "Cronin EM, Bogun FM, Maury P, et al. 2019 HRS/EHRA/APHRS/LAHRS expert consensus statement on catheter ablation of ventricular arrhythmias: Executive summary. J Arrhythm. 2020;36(1):1-58. DOI: 10.1002/joa3.12264. PMID: 32071620"
  - "Baman TS, Lange DC, Ilg KJ, et al. Relationship between burden of premature ventricular complexes and left ventricular function. Heart Rhythm. 2010;7(7):865-869. DOI: 10.1016/j.hrthm.2010.03.036. PMID: 20348027"
---

# Fluxograma: sinalizadores ambulatoriais de PVC frequente

Prosa: [`pvc-frequente-no-consultorio-sinais-vermelhos-quando-ir-ao-ps`](pvc-frequente-no-consultorio-sinais-vermelhos-quando-ir-ao-ps.md) e [`sinalizadores-ambulatoriais-de-carga-de-pvc-quando-escalar-ablacao`](sinalizadores-ambulatoriais-de-carga-de-pvc-quando-escalar-ablacao.md). Indicação Classe I/IIa detalhada: [`fluxograma-extrassistole-ventricular-frequente-cardiomiopatia-induzida-e-indicacao-de-ablacao`](fluxograma-extrassistole-ventricular-frequente-cardiomiopatia-induzida-e-indicacao-de-ablacao.md). Evidência de corte: [`extrassistole-ventricular-frequente-e-cardiomiopatia-induzida-carga-que-preve-disfuncao`](extrassistole-ventricular-frequente-e-cardiomiopatia-induzida-carga-que-preve-disfuncao.md).

## Árvore de decisão

```mermaid
flowchart TD
  R0["Consulta: PVC frequente<br/>(ECG / Holter / monitor)"] --> D1{"Há síncope, instabilidade,<br/>TV sustentada, PVC polimórfica<br/>sintomática ou SCA/IC aguda?"}

  D1 -->|"Sim"| C1(["PS / emergência AGORA<br/>ECG 12 derivações<br/>Sem doses neste fluxo"])

  D1 -->|"Não"| D2{"Eco: FEVE reduzida<br/>ou dilatação de VE?"}

  D2 -->|"Sim"| D3{"Carga >24% e PVC<br/>predominantemente monomórfica<br/>sem outra causa mais provável?"}
  D3 -->|"Sim"| C2(["EP eletiva rápida<br/>Discutir ablação Classe I<br/>(após antiarrítmico ineficaz/<br/>não tolerado/não preferido)"])
  D3 -->|"Não / dúvida"| C3(["Investigar causa estrutural<br/>RM se útil · carga 10–24%:<br/>EP eletiva se PVC contribuinte"])

  D2 -->|"Não"| D4{"Carga de PVC ≥10%?<br/>(piso de risco reversível)"}
  D4 -->|"Sim"| C4(["Vigilância próxima<br/>Holter/eco de controle<br/>± RM · ablação NÃO automática"])
  D4 -->|"Não"| C5(["Vigilância periódica<br/>Educar alarmes<br/>Reavaliar se sintoma/carga sobe"])

  classDef conduta fill:#eef6ef,stroke:#2f7a4f,color:#12301f;
  classDef alerta fill:#fdecea,stroke:#b3261e,color:#3b0a0a;
  class C1 alerta;
  class C2,C3,C4,C5 conduta;
```

## Notas

- **D1** = gate de segurança (ESC 2022) — não confundir com indicação eletiva de ablação.
- **D3** = corte Baman >24% + morfologia monomórfica + exclusão de alternativa (HRS 2019).
- **C4** = carga ≥10% sem disfunção atual ≠ ablação automática; é vigilância mais próxima.
- Não decide anticoagulação de FA (#827/#852/#883) nem doses antiarrítmicas.
