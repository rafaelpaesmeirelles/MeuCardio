---
title: "Fluxograma ambulatorial: gestação/puerpério com piora cardiovascular — PS agora vs. retorno precoce vs. pregnancy heart team"
slug: fluxograma-ambulatorial-gravidez-cardiopatia-piora-destino
theme: "Gravidez"
kind: fluxograma
fonte_producao: grok
summary: "Árvore ambulatorial de destino na gestante ou puérpera: gate de alarme para PS, braço de sintoma equívoco com retorno precoce, e braço de risco mWHO/desfecho adverso para pregnancy heart team."
review_status: pendente_revisao
review_note: "Irmão do protocolo sinalizadores-ambulatoriais-gravidez-cardiopatia-quando-encaminhar (07/09/2026). ESC 2025 DOI 10.1093/eurheartj/ehaf193; ACC 2026 ECDP PMID 42171544. Sem doses; anti-colisão com PPCM/SCAD/TEP/eclâmpsia."
source_refs:
  - "De Backer J, Haugaa KH, Hasselberg NE, et al. 2025 ESC Guidelines for the management of cardiovascular disease and pregnancy. Eur Heart J. 2025. DOI: 10.1093/eurheartj/ehaf193"
  - "Lindley KJ, Bello NA, Berlacher KL, et al. Optimization of Postpartum Care for Patients With and at Risk for Premature and Long-Term Cardiovascular Disease: 2026 ACC Expert Consensus Decision Pathway. J Am Coll Cardiol. Published online May 22, 2026. DOI: 10.1016/j.jacc.2025.11.001. PMID: 42171544"
---

# Fluxograma ambulatorial: gestação/puerpério com piora — destino

Prosa: [`sinalizadores-ambulatoriais-gravidez-cardiopatia-quando-encaminhar`](sinalizadores-ambulatoriais-gravidez-cardiopatia-quando-encaminhar.md). Checklist: [`gravidez-checklist-ambulatorial-de-alarme`](gravidez-checklist-ambulatorial-de-alarme.md).

## Árvore de decisão

```mermaid
flowchart TD
  R0["Consulta ambulatorial / contato\ngestação ou puerpério\ncom cardiopatia ou risco ampliado"] --> D1{"Há alarme de PS?\ndispneia em repouso / ortopneia grave\nPA ≥160/110 + sintomas de eclâmpsia\ndor torácica / interescapular\nsíncope / hipoxemia súbita\nHAP/Eisenmenger em piora\nsuspeita PPCM / SCAD / TEP / aorta"}

  D1 -->|"Sim ou dúvida fundamentada"| C1(["Encaminhar AGORA ao PS\nUsar fluxograma da emergência suspeita\n(PPCM / SCAD / TEP / eclâmpsia / aorta)"])

  D1 -->|"Não"| D2{"Sintoma cardiovascular equívoco\nsem hipoperfusão?\ndispneia leve / edema simétrico\nPA elevada sem urgência\npalpitações estáveis"}

  D2 -->|"Sim"| P1["Exame focado + ECG ± biomarcadores\n± eco se mudar conduta\nChecar adesão e rede de suporte"]
  P1 --> C2(["Retorno ambulatorial 24–72 h\nOrientação escrita de alarmes\n(≤7 dias se brando e suporte OK)"])

  D2 -->|"Não / estável"| D3{"mWHO II–IV / desfecho adverso\nsem pregnancy heart team ativo\nou transição pós-parto incompleta?"}

  D3 -->|"Sim"| C3(["Referência pregnancy heart team\n/ cardiologia + plano ACC 2026\naté 12 semanas e 1º ano"])
  D3 -->|"Não"| C4(["Plano usual + educação de alarmes\nManter janela crítica das 2 primeiras\nsemanas do puerpério em mente"])

  C2 --> D4{"Acesso e suporte garantidos?"}
  D4 -->|"Não / piora rápida / mWHO alto"| C5(["Antecipar retorno 24 h ou PS\nse surgir alarme da tabela"])
  D4 -->|"Sim"| C6(["Manter retorno 24–72 h\nNão protocolar doses neste fluxograma"])

  classDef conduta fill:#eef6ef,stroke:#2f7a4f,color:#12301f;
  classDef alerta fill:#fdecea,stroke:#b3261e,color:#3b0a0a;
  class C1,C5 alerta;
  class C2,C3,C4,C6 conduta;
```

## Notas

- **D1** = gate de segurança (PPCM, PA grave/eclâmpsia, SCAD/aorta, TEP, HAP — ESC 2025 + ACC 2026).
- **D2** = sintoma equívoco ambulatorial → destino clínico precoce (primeiras semanas do puerpério).
- **D3** = ponte para pregnancy heart team / transição do 1º ano (ACC 2026), **sem** decidir fármaco aqui.
- Não decide doses de anti-hipertensivo, anticoagulação, bromocriptina nem suporte avançado.
