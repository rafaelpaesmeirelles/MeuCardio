---
title: "Fluxograma ambulatorial: PPCM / suspeita no puerpério — PS agora vs. retorno precoce vs. pregnancy heart team"
slug: fluxograma-ambulatorial-ppcm-puerperio-destino
theme: "Gravidez"
kind: fluxograma
fonte_producao: grok
summary: "Árvore ambulatorial de destino na puérpera com PPCM conhecida ou suspeita: gate de alarme para PS, braço de sintoma equívoco com retorno precoce, e braço sem coordenação cardiológica para pregnancy heart team."
review_status: pendente_revisao
review_note: "Irmão do protocolo sinalizadores-ambulatoriais-ppcm-puerperio-quando-encaminhar (07/09/2026). ESC 2025 DOI 10.1093/eurheartj/ehaf193; Bauersachs 2019 PMID 31243866; ACC 2026 ECDP PMID 42171544. Sem doses; anti-colisão com #849 e com fluxograma de choque/PPCM."
source_refs:
  - "De Backer J, Haugaa KH, Hasselberg NE, et al. 2025 ESC Guidelines for the management of cardiovascular disease and pregnancy. Eur Heart J. 2025. DOI: 10.1093/eurheartj/ehaf193"
  - "Bauersachs J, König T, van der Meer P, et al. Pathophysiology, diagnosis and management of peripartum cardiomyopathy: a position statement from the Heart Failure Association of the European Society of Cardiology Study Group on PPCM. Eur J Heart Fail. 2019;21(7):827-843. DOI: 10.1002/ejhf.1493. PMID: 31243866"
  - "Lindley KJ, Bello NA, Berlacher KL, et al. Optimization of Postpartum Care for Patients With and at Risk for Premature and Long-Term Cardiovascular Disease: 2026 ACC Expert Consensus Decision Pathway. J Am Coll Cardiol. Published online May 22, 2026. DOI: 10.1016/j.jacc.2025.11.001. PMID: 42171544"
---

# Fluxograma ambulatorial: PPCM / suspeita no puerpério — destino

Prosa: [`sinalizadores-ambulatoriais-ppcm-puerperio-quando-encaminhar`](sinalizadores-ambulatoriais-ppcm-puerperio-quando-encaminhar.md). Checklist: [`ppcm-checklist-ambulatorial-alarme-pos-parto`](ppcm-checklist-ambulatorial-alarme-pos-parto.md). Emergência: [`fluxograma-cardiomiopatia-periparto-descompensada-e-choque-no-puerperio-esc-2025`](fluxograma-cardiomiopatia-periparto-descompensada-e-choque-no-puerperio-esc-2025.md).

## Árvore de decisão

```mermaid
flowchart TD
  R0["Consulta ambulatorial / contato\npuérpera com PPCM conhecida\nou suspeita de IC periparto"] --> D1{"Há alarme de PS?\ndispneia em repouso / ortopneia grave\nhipoperfusão / síncope\nhipoxemia súbita / TEP suspeito\ndor torácica / SCAD suspeita\nFEVE reduzida com piora rápida"}

  D1 -->|"Sim ou dúvida fundamentada"| C1(["Encaminhar AGORA ao PS\nUsar fluxograma PPCM descompensada/choque\nDiferencial: TEP / SCAD / pré-eclâmpsia"])

  D1 -->|"Não"| D2{"Sintoma cardiovascular equívoco\nsem hipoperfusão?\ndispneia leve / edema simétrico\nfadiga desproporcional"}

  D2 -->|"Sim"| P1["Exame focado + ECG\n± BNP/NT-proBNP\n± eco se mudar conduta\nChecar rede de suporte"]
  P1 --> C2(["Retorno ambulatorial 24–72 h\nOrientação escrita de alarmes\n(≤7 dias se brando e suporte OK)"])

  D2 -->|"Não / estável"| D3{"PPCM/suspeita sem pregnancy\nheart team / cardiologia ativa\nou transição do 1º ano incompleta?"}

  D3 -->|"Sim"| C3(["Referência pregnancy heart team\n/ cardiologia + plano ACC 2026\naté 12 semanas e 1º ano"])
  D3 -->|"Não"| C4(["Plano usual + educação de alarmes\nManter janela crítica das 2 primeiras\nsemanas do puerpério em mente"])

  C2 --> D4{"Acesso e suporte garantidos?"}
  D4 -->|"Não / piora rápida / FEVE muito baixa"| C5(["Antecipar retorno 24 h ou PS\nse surgir alarme da tabela"])
  D4 -->|"Sim"| C6(["Manter retorno 24–72 h\nNão protocolar doses neste fluxograma"])

  classDef conduta fill:#eef6ef,stroke:#2f7a4f,color:#12301f;
  classDef alerta fill:#fdecea,stroke:#b3261e,color:#3b0a0a;
  class C1,C5 alerta;
  class C2,C3,C4,C6 conduta;
```

## Notas

- **D1** = gate de segurança (congestão grave, hipoperfusão, arritmia, TEP/SCAD — Bauersachs 2019 + ESC 2025 + ACC 2026).
- **D2** = sintoma equívoco ambulatorial → destino clínico precoce (primeiras semanas do puerpério).
- **D3** = ponte para pregnancy heart team / transição do 1º ano (ACC 2026), **sem** decidir fármaco aqui.
- Não decide doses de GDMT, bromocriptina, anticoagulação nem suporte avançado.
