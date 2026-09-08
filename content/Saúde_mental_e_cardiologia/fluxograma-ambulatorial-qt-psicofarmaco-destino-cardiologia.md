---
title: "Fluxograma ambulatorial: preocupação com QT por psicofármaco — PS agora vs. retorno precoce vs. Psycho-Cardio"
slug: fluxograma-ambulatorial-qt-psicofarmaco-destino-cardiologia
theme: "Saúde mental e cardiologia"
kind: fluxograma
fonte_producao: grok
summary: "Destino clínico individualizado e limites de segurança; critérios detalhados no protocolo e navegação canônica do pacote."
review_status: revisado
review_note: "Revisão científica/adversarial 08/09/2026: findings PR881 reconstruídos; urgência, bibliografia e limites revistos. Fonte grok preservada."
source_refs:
  - "Bueno H, Deaton C, Farrero M, et al. 2025 ESC Clinical Consensus Statement on mental health and cardiovascular disease: developed under the auspices of the ESC Clinical Practice Guidelines Committee. Eur Heart J. 2025;46(41):4156-4225. DOI: 10.1093/eurheartj/ehaf191. PMID: 40878270"
  - "Drew BJ, Ackerman MJ, Funk M, et al. Prevention of torsade de pointes in hospital settings: a scientific statement from the American Heart Association and the American College of Cardiology Foundation. Circulation. 2010;121(8):1047-1060. DOI: 10.1161/CIRCULATIONAHA.109.192704. PMID: 20142454"
  - "Wenzel-Seifert K, Wittmann M, Haen E. QTc prolongation by psychotropic drugs and the risk of Torsade de Pointes. Dtsch Arztebl Int. 2011;108(41):687-693. DOI: 10.3238/arztebl.2011.0687. PMID: 22114630"
  - "Ray WA, Chung CP, Murray KT, Hall K, Stein CM. Atypical antipsychotic drugs and the risk of sudden cardiac death. N Engl J Med. 2009;360(3):225-235. DOI: 10.1056/NEJMoa0806994. PMID: 19144938"
---

# Fluxograma ambulatorial: preocupação com QT por psicofármaco — PS agora vs. retorno precoce vs. Psycho-Cardio

```mermaid
flowchart TD
 A["Síncope arrítmica, instabilidade, arritmia ventricular ou intoxicação?"] -->|Sim| B["Emergência; crise suicida em toda intoxicação intencional"]
 A -->|Não| C["Validar QT, QRS e método; revisar exposição e eletrólitos"]
 C --> D{"QT relevante ou risco elevado confirmado?"}
 D -->|Sim| E["Avaliação cardiológica urgente; monitorização conforme risco e acesso"]
 D -->|Não| F["Revisão conjunta com prescritor e ECG individualizado"]
```

Consulte o protocolo de sinalizadores do mesmo pacote para critérios e limites. Reavalie o destino após exames e diante de qualquer piora.


## Navegação

- [`sinalizadores-ambulatoriais-preocupacao-qt-psicofarmaco-quando-escalar`](/biblioteca/sinalizadores-ambulatoriais-preocupacao-qt-psicofarmaco-quando-escalar)
- [`checklist-ambulatorial-alarme-qt-psicofarmaco-cardiopata`](/biblioteca/checklist-ambulatorial-alarme-qt-psicofarmaco-cardiopata)
- [`fluxograma-escolha-de-antidepressivo-e-antipsicotico-no-cardiopata-risco-de-qt`](/biblioteca/fluxograma-escolha-de-antidepressivo-e-antipsicotico-no-cardiopata-risco-de-qt)
