---
title: "Fluxograma ambulatorial: tireoide no retorno cardiológico — quando pedir TSH e escalar"
slug: fluxograma-ambulatorial-tireoide-quando-pedir-tsh-e-escalar
theme: "Geral"
kind: fluxograma
fonte_producao: grok
summary: "Árvore de consultório: pista de disfunção tireoidiana em paciente CV → TSH/T4 → destino (plano habitual vs endocrino vs urgência). Bifurca amiodarona para o pacote #838. Sem doses."
review_status: pendente_revisao
review_note: "Irmão do protocolo sinalizadores-ambulatoriais-de-disfuncao-tireoidiana-no-retorno-cardiologico (07/09/2026). Klein/Danzi PMID 17923583; ATA hiper PMID 27521067; ESC 2024 FA. Anti-colisão #838 (amiodarona) e doc FA+hipertireoidismo subclínico (cardioversão)."
source_refs:
  - "Klein I, Danzi S. Thyroid disease and the heart. Circulation. 2007;116(15):1725-1735. DOI: 10.1161/CIRCULATIONAHA.106.678625. PMID: 17923583"
  - "Ross DS, Burch HB, Cooper DS, et al. 2016 American Thyroid Association Guidelines for Diagnosis and Management of Hyperthyroidism and Other Causes of Thyrotoxicosis. Thyroid. 2016;26(10):1343-1421. DOI: 10.1089/thy.2016.0229. PMID: 27521067"
  - "Van Gelder IC, Rienstra M, Bunting KV, et al. 2024 ESC Guidelines for the management of atrial fibrillation. Eur Heart J. 2024;45(36):3314-3414. DOI: 10.1093/eurheartj/ehae176"
  - "Jabbar A, Pingitore A, Pearce SH, Zaman A, Iervasi G, Razvi S. Thyroid hormones and cardiovascular disease. Nat Rev Cardiol. 2017;14(1):39-55. DOI: 10.1038/nrcardio.2016.174. PMID: 27811932"
---

# Fluxograma ambulatorial: tireoide — quando pedir TSH e escalar

Prosa: [`sinalizadores-ambulatoriais-de-disfuncao-tireoidiana-no-retorno-cardiologico`](sinalizadores-ambulatoriais-de-disfuncao-tireoidiana-no-retorno-cardiologico.md). Checklist: [`checklist-ambulatorial-tireoide-no-paciente-cardiologico`](checklist-ambulatorial-tireoide-no-paciente-cardiologico.md). Amiodarona: pacote [#838](https://github.com/rafaelpaesmeirelles/MeuCardio/pull/838).

## Árvore de decisão

```mermaid
flowchart TD
  R0["Retorno cardiológico\nFA / HAS / IC / bradicardia / LDL / derrame"] --> D0{"Usa amiodarona?"}

  D0 -->|"Sim"| C0(["Ir ao pacote de monitoramento\namiodarona — PR #838"])

  D0 -->|"Não"| D1{"Há pista clínica ou fenótipo\nque dispara TSH?"}

  D1 -->|"Não"| C1(["Plano CV habitual\nNão medicalizar TSH\nsem indicação"])

  D1 -->|"Sim"| P1["Dosar TSH\n(+ T4 livre se TSH anormal)"]
  P1 --> D2{"Resultado"}

  D2 -->|"TSH normal"| C2(["Buscar outra causa CV\nReavaliar se nova pista"])

  D2 -->|"Sugere hipo"| D3{"Sinais de gravidade?\nhipotermia, rebaixamento,\nhipotensão, hipoventilação"}
  D3 -->|"Sim"| C3(["Emergência / UTI\nComa mixedematoso —\nver verbete hipotireoidismo"])
  D3 -->|"Não"| C4(["Articular reposição com\nendocrino/clínico\nAjustar expectativas CV\n(bradicardia, LDL, derrame)"])

  D2 -->|"Sugere hiper / tireotoxicose"| D4{"Instabilidade CV?\nFA rápida, IC, angina, síncope"}
  D4 -->|"Sim"| C5(["Estabilizar + lab urgente\n+ endocrino\nNão só ‘subir betabloqueador’”])
  D4 -->|"Não"| C6(["Endocrino para tipagem\ne terapia\nPlano de ritmo/FA em paralelo\n(ESC 2024); cardioversão:\ndoc FA+subclínico"])

  classDef conduta fill:#eef6ef,stroke:#2f7a4f,color:#12301f;
  classDef alerta fill:#fdecea,stroke:#b3261e,color:#3b0a0a;
  class C3,C5 alerta;
  class C0,C1,C2,C4,C6 conduta;
```

## Notas

- **D0**: amiodarona tem calendário e decisões próprias (#838).
- **D1**: filtro de probabilidade (Klein/Danzi; Jabbar) — não TSH universal.
- **D2/D4**: ATA 2016 ancora tireotoxicose como causa tratável; ESC 2024 FA pede causa precipitante.
- Não decide dose de levotiroxina, tionamida, I-131 nem suspende GDMT automaticamente.
