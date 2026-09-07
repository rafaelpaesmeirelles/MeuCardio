---
title: "Fluxograma ambulatorial: dor torácica crônica — quando escalar ao PS"
slug: fluxograma-ambulatorial-dor-toracica-cronica-quando-escalar
theme: "Doença_coronariana"
kind: fluxograma
fonte_producao: grok
summary: "Árvore de consultório para dor torácica em seguimento de SCC/DAC: gate de instabilização → PS; padrão estável → plano ambulatorial e retorno; sem reabrir algoritmo 0/1 h de troponina da emergência."
review_status: pendente_revisao
review_note: "Irmão do protocolo sinalizadores-ambulatoriais-de-angina-instabilizando-quando-encaminhar (07/09/2026). ESC 2024 CCS PMID 39210710; ESC 2023 ACS PMID 37622654."
source_refs:
  - "Vrints C, Andreotti F, Koskinas KC, et al. 2024 ESC Guidelines for the management of chronic coronary syndromes. Eur Heart J. 2024;45(36):3415-3537. DOI: 10.1093/eurheartj/ehae177. PMID: 39210710"
  - "Byrne RA, Rossello X, Coughlan JJ, et al. 2023 ESC Guidelines for the management of acute coronary syndromes. Eur Heart J. 2023;44(38):3720-3826. DOI: 10.1093/eurheartj/ehad191. PMID: 37622654"
---

# Fluxograma ambulatorial: dor torácica crônica — quando escalar

Prosa: [`sinalizadores-ambulatoriais-de-angina-instabilizando-quando-encaminhar`](sinalizadores-ambulatoriais-de-angina-instabilizando-quando-encaminhar.md). Pós-IAM: [`pos-iam-ambulatorial-sinais-de-alarme-nas-primeiras-semanas`](pos-iam-ambulatorial-sinais-de-alarme-nas-primeiras-semanas.md). Vias agudas: [`fluxograma-sindrome-coronariana-aguda-esc-2023`](fluxograma-sindrome-coronariana-aguda-esc-2023.md).

## Árvore de decisão

```mermaid
flowchart TD
  R0["Consulta ambulatorial\ndor torácica / angina em SCC ou DAC"] --> D1{"Há sinal de instabilização?\nrepouso · crescendo · nitrato sem alívio\nequivalentes · ECG isquêmico novo"}

  D1 -->|"Sim ou dúvida fundamentada"| C1(["Encaminhar AGORA ao PS / emergência\nECG na porta · via SCA\nNão teste ergométrico ambulatorial"])

  D1 -->|"Não"| D2{"Padrão ainda effort-limited\ne previsível?"}

  D2 -->|"Não / atípico com alto risco"| C2(["Baixar limiar para PS ou observação\ncom suporte; não liberar sem plano"])

  D2 -->|"Sim"| D3{"Houve piora leve do limiar\nou gatilho reversível?"}

  D3 -->|"Sim"| C3(["Revisar adesão e gatilhos\nIntensificar antianginoso conforme plano\nRetorno em dias + orientação escrita"])
  D3 -->|"Não"| C4(["Manter terapia de SCC\nRetorno usual\nReforçar sinais de alarme"])

  C3 --> D4{"Acesso a medicação\ne retorno garantidos?"}
  D4 -->|"Não / fragilidade"| C5(["Antecipar retorno 24–72 h\nou encaminhar se insegurança"])
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
