---
title: 'Fluxograma ambulatorial: dor torácica crônica — quando escalar ao PS'
slug: fluxograma-ambulatorial-dor-toracica-cronica-quando-escalar
theme: Doença coronariana
kind: fluxograma
fonte_producao: grok
summary: 'Árvore de consultório para dor torácica em seguimento de SCC/DAC: gate de instabilização → PS; padrão estável → plano ambulatorial e retorno;
  sem reabrir algoritmo 0/1 h de troponina da emergência.'
review_status: revisado
review_note: 'Revisão clínica e editorial focal em 08/09/2026 do PR #843, desde seu HEAD remoto. Correções e fontes verificadas registradas em docs/revisao-cientifica-pr826-859-20260908.md.
  Prazos operacionais não equivalem a recomendações normativas; preservar avaliação individual e vias de emergência.'
source_refs:
- 'Vrints C; Andreotti F; Koskinas KC. 2024 ESC Guidelines for the management of chronic coronary syndromes. Eur Heart J. 2024;45:3415. DOI: 10.1093/eurheartj/ehae177.
  PMID: 39210710.'
- 'Byrne RA; Rossello X; Coughlan JJ. 2023 ESC Guidelines for the management of acute coronary syndromes. Eur Heart J. 2023;44:3720. DOI: 10.1093/eurheartj/ehad191.
  PMID: 37622654.'
---

# Fluxograma ambulatorial: dor torácica crônica — quando escalar

Prosa: [[sinalizadores-ambulatoriais-de-angina-instabilizando-quando-encaminhar](/biblioteca/sinalizadores-ambulatoriais-de-angina-instabilizando-quando-encaminhar)](/biblioteca/sinalizadores-ambulatoriais-de-angina-instabilizando-quando-encaminhar). Pós-IAM: [[pos-iam-ambulatorial-sinais-de-alarme-nas-primeiras-semanas](/biblioteca/pos-iam-ambulatorial-sinais-de-alarme-nas-primeiras-semanas)](/biblioteca/pos-iam-ambulatorial-sinais-de-alarme-nas-primeiras-semanas). Vias agudas: [[fluxograma-sindrome-coronariana-aguda-esc-2023](/biblioteca/fluxograma-sindrome-coronariana-aguda-esc-2023)](/biblioteca/fluxograma-sindrome-coronariana-aguda-esc-2023).

## Árvore de decisão

```mermaid
flowchart TD
  R0["Consulta ambulatorial<br/>dor torácica / angina em SCC ou DAC"] --> D1{"Há sinal de instabilização?<br/>repouso · crescendo<br/>equivalentes · ECG isquêmico novo"}

  D1 -->|"Sim ou dúvida fundamentada"| C1(["Encaminhar AGORA ao PS / emergência<br/>ECG na porta · via SCA<br/>Não teste ergométrico ambulatorial"])

  D1 -->|"Não"| D2{"Padrão ainda effort-limited<br/>e previsível?"}

  D2 -->|"Não / atípico com alto risco"| C2(["Baixar limiar para PS ou observação<br/>com suporte; não liberar sem plano"])

  D2 -->|"Sim"| D3{"Há necessidade de otimização<br/>sem mudança do padrão anginoso?"}

  D3 -->|"Sim"| C3["Revisar adesão e gatilhos<br/>Intensificar antianginoso conforme plano<br/>Retorno em dias + orientação escrita"]
  D3 -->|"Não"| C4(["Manter terapia de SCC<br/>Retorno usual<br/>Reforçar sinais de alarme"])

  C3 --> D4{"Acesso a medicação<br/>e retorno garantidos?"}
  D4 -->|"Não / fragilidade"| C5(["Antecipar retorno 24–72 h<br/>ou encaminhar se insegurança"])
  D4 -->|"Sim"| C6(["Plano ambulatorial + alarmes escritos"])

  classDef conduta fill:#eef6ef,stroke:#2f7a4f,color:#12301f;
  classDef alerta fill:#fdecea,stroke:#b3261e,color:#3b0a0a;
  class C1,C2,C5 alerta;
  class C3,C4,C6 conduta;
```

## Notas

- **D1** = gate de segurança (ESC 2023 ACS / ESC 2024 CCS): decide PS vs. consultório.
- **D2–D3** = braço estável: não reabre 0/1 h de troponina nem timing invasivo de NSTE.
- **D4** = segurança do plano (acesso/fragilidade), não nova classe terapêutica.
- Não decide doses, escolha de P2Y12 nem estratégia de reperfusão.

## Segurança diagnóstica

Alívio ou ausência de alívio com nitrato não confirma nem exclui SCA. ECG normal também não a exclui. Suspeita razoável exige via aguda com ECG/troponina seriados e observação; não teste ergométrico nem espera domiciliar por troponina. No pós-IAM considerar reinfarto/trombose de stent, pericardite, complicação mecânica, IC, arritmia e causas não cardíacas. Sangramento menor pede avaliação e não suspensão empírica de DAPT; cefaleia súbita grave sob antitrombótico é alarme neurológico, não diagnóstico de hemorragia sem imagem.
