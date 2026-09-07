---
title: "Fluxograma ambulatorial: IC com piora progressiva — PS agora vs. retorno precoce"
slug: fluxograma-ambulatorial-ic-piora-progressiva-destino
theme: "Insuficiência cardíaca"
kind: fluxograma
fonte_producao: grok
summary: "Árvore ambulatorial de destino na piora de IC: gate de alarme para PS, braço de congestão leve–moderada com retorno precoce, e lembrete pós-alta sem titulação de GDMT."
review_status: pendente_revisao
review_note: "Irmão do protocolo sinalizadores-ambulatoriais-de-descompensacao-de-ic-quando-encaminhar (07/09/2026). ESC 2021 PMID 34447992; ESC 2023 PMID 37622666; STRONG-HF PMID 36356631. Sem doses; anti-colisão cardiorrenal e GDMT."
source_refs:
  - "McDonagh TA, Metra M, Adamo M, et al. 2021 ESC Guidelines for the diagnosis and treatment of acute and chronic heart failure. Eur Heart J. 2021;42(36):3599-3726. DOI: 10.1093/eurheartj/ehab368. PMID: 34447992"
  - "McDonagh TA, Metra M, Adamo M, et al. 2023 Focused Update of the 2021 ESC Guidelines for the diagnosis and treatment of acute and chronic heart failure. Eur Heart J. 2023;44(37):3627-3639. DOI: 10.1093/eurheartj/ehad195. PMID: 37622666"
  - "Mebazaa A, Davison B, Chioncel O, et al. Safety, tolerability and efficacy of up-titration of guideline-directed medical therapies for acute heart failure (STRONG-HF): a multinational, open-label, randomised, trial. Lancet. 2022;400(10367):1938-1952. DOI: 10.1016/S0140-6736(22)02076-1. PMID: 36356631"
---

# Fluxograma ambulatorial: IC com piora progressiva — destino

Prosa: [`sinalizadores-ambulatoriais-de-descompensacao-de-ic-quando-encaminhar`](sinalizadores-ambulatoriais-de-descompensacao-de-ic-quando-encaminhar.md). Pós-alta 14 dias: [`pos-alta-de-ic-checklist-de-alarme-nas-duas-primeiras-semanas`](pos-alta-de-ic-checklist-de-alarme-nas-duas-primeiras-semanas.md). Aguda hospitalar: [`fluxograma-insuficiencia-cardiaca-aguda-descompensada`](fluxograma-insuficiencia-cardiaca-aguda-descompensada.md).

## Árvore de decisão

```mermaid
flowchart TD
  R0["Consulta ambulatorial / contato pós-alta<br/>com IC e piora referida"] --> D1{"Há alarme de PS?<br/>dispneia em repouso / hipoxemia<br/>hipoperfusão / síncope<br/>dor anginosa / arritmia instável"}

  D1 -->|"Sim ou dúvida fundamentada"| C1(["Encaminhar AGORA ao PS / emergência<br/>Seguir fluxograma-insuficiencia-cardiaca-aguda-descompensada"])

  D1 -->|"Não"| D2{"Congestão progressiva leve–moderada?<br/>edema / ganho de peso / ortopneia<br/>sem hipoperfusão"}

  D2 -->|"Sim"| P1["Checar adesão, sal, AINE, infecção<br/>Exame focado + peso"]
  P1 --> C2(["Retorno ambulatorial 24–72 h<br/>Orientação escrita de alarmes<br/>Labs se mudarem conduta"])

  D2 -->|"Não / muito brando"| D3{"Pós-alta nas últimas 2 semanas?"}

  D3 -->|"Sim"| C3(["Aplicar checklist pós-alta 14 dias<br/>Manter vigilância; retorno ≤7 dias<br/>se sinalizadores brandos"])
  D3 -->|"Não"| C4(["Plano usual + educação de alarmes<br/>Peso diário se congestão recorrente<br/>Retorno conforme estabilidade"])

  C2 --> D4{"Acesso e suporte garantidos?"}
  D4 -->|"Não / fragilidade / piora rápida"| C5(["Antecipar retorno 24 h ou PS<br/>se surgir alarme da tabela"])
  D4 -->|"Sim"| C6(["Manter retorno 24–72 h<br/>Não titular GDMT neste fluxograma"])

  classDef conduta fill:#eef6ef,stroke:#2f7a4f,color:#12301f;
  classDef alerta fill:#fdecea,stroke:#b3261e,color:#3b0a0a;
  class C1,C5 alerta;
  class C2,C3,C4,C6 conduta;
```

## Notas

- **D1** = gate de segurança (perfil de IC aguda / ESC 2021).
- **D2** = congestão ambulatorial sem hipoperfusão → destino clínico precoce.
- **D3** = janela pós-alta alinhada à vigilância das primeiras semanas (ESC 2023 / STRONG-HF).
- Não decide doses de GDMT, diurético IV, ultrafiltração nem manejo cardiorrenal.
