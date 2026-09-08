---
title: 'Fluxograma ambulatorial: crise psiquiátrica no cardiopata — crise agora vs. retorno precoce vs. Psycho-Cardio'
slug: fluxograma-ambulatorial-crise-psiquiatrica-destino-cardiologia
theme: Saúde mental e cardiologia
kind: fluxograma
fonte_producao: grok
summary: 'Árvore ambulatorial de destino: gate de segurança (ideação/plano/psicose) para via de crise/PS; braço de sofrimento intenso com retorno precoce;
  braço de stepped care / Psycho-Cardio sem risco iminente.'
review_status: revisado
review_note: 'Revisão clínica e editorial focal em 08/09/2026 do PR #847, desde seu HEAD remoto. Correções e fontes verificadas registradas em docs/revisao-cientifica-pr826-859-20260908.md.
  Prazos operacionais não equivalem a recomendações normativas; preservar avaliação individual e vias de emergência.'
source_refs:
- NIMH. Adult Outpatient Brief Suicide Safety Assessment Guide. https://www.nimh.nih.gov/research/research-conducted-at-nimh/asq-toolkit-materials/adult-outpatient/adult-outpatient-brief-suicide-safety-assessment-guide
  (consultado 08/09/2026).
- 'Bueno H; Deaton C; Farrero M. 2025 ESC Clinical Consensus Statement on mental health and cardiovascular disease: developed under the auspices of the
  ESC Clinical Practice Guidelines Committee. Eur Heart J. 2025;46:4156. DOI: 10.1093/eurheartj/ehaf191. PMID: 40878270.'
- 'Lichtman JH; Bigger JT; Blumenthal JA. Depression and coronary heart disease: recommendations for screening, referral, and treatment: a science advisory
  from the American Heart Association Prevention Committee of the Council on Cardiovascular Nursing, Council on Clinical Cardiology, Council on Epidemiology
  and Prevention, and Interdisciplinary Council on Quality of Care and Outcomes Research: endorsed by the American Psychiatric Association. Circulation.
  2008;118:1768. DOI: 10.1161/CIRCULATIONAHA.108.190769. PMID: 18824640.'
---

# Fluxograma ambulatorial: crise psiquiátrica — destino

Prosa: [[sinalizadores-ambulatoriais-crise-psiquiatrica-no-consultorio-de-cardiologia](/biblioteca/sinalizadores-ambulatoriais-crise-psiquiatrica-no-consultorio-de-cardiologia)](/biblioteca/sinalizadores-ambulatoriais-crise-psiquiatrica-no-consultorio-de-cardiologia). Checklist: [[checklist-ambulatorial-alarme-crise-psiquiatrica-cardiopata](/biblioteca/checklist-ambulatorial-alarme-crise-psiquiatrica-cardiopata)](/biblioteca/checklist-ambulatorial-alarme-crise-psiquiatrica-cardiopata). Rastreamento ACTIVE: [[fluxograma-rastreamento-saude-mental-cuidado-escalonado-esc-2025](/biblioteca/fluxograma-rastreamento-saude-mental-cuidado-escalonado-esc-2025)](/biblioteca/fluxograma-rastreamento-saude-mental-cuidado-escalonado-esc-2025).

## Árvore de decisão

```mermaid
flowchart TD
 R["Sofrimento mental ou rastreamento positivo"] --> A["Avaliar no mesmo encontro ideação, intenção,<br/>preparação, tentativas, psicose, intoxicação,<br/>impulsividade, meios, rede e capacidade de segurança"]
 A --> D{"Risco iminente ou segurança não garantida?"}
 D -->|Sim ou dúvida fundamentada| E["Via local de crise/emergência agora;<br/>não deixar sozinho e cuidar da estabilidade cardiovascular"]
 D -->|Não| S["Definir plano de segurança e referência;<br/>gravidade, funcionamento e acesso definem prazo"]
 S --> F{"Sofrimento intenso, prejuízo importante ou rede frágil?"}
 F -->|Sim| P["Avaliação qualificada no mesmo dia ou retorno precoce<br/>conforme risco; 24–72 h é marco operacional"]
 F -->|Não| C["Cuidado escalonado e contato programado;<br/>orientações para piora e via de crise"]
 P --> G{"Acesso e segurança confirmados?"}
 G -->|Não| E
 G -->|Sim| C
```

## Notas

- **D1** = gate de segurança (ESC 2025: urgência segue protocolo local; AHA 2008: ideação no rastreamento → avaliação imediata).
- **D2** = sofrimento ambulatorial controlável com rede → destino clínico precoce + referência qualificada.
- **D3** = ponte para ACTIVE / Psycho-Cardio e para pacotes de QT/antidepressivo já existentes, **sem** decidir fármaco aqui.
- Não decide doses, ponto de corte único de escala nem periodicidade universal de rastreamento.

## Avaliação de segurança no mesmo encontro

Ausência de plano não libera o paciente. Aprofundar qualquer ideação ou desejo de morrer: intensidade/persistência, intenção, preparação, tentativas anteriores, intoxicação, agitação/psicose, impulsividade, meios disponíveis, desesperança, rede e fatores protetores. PHQ-9 item 9 ou qualquer escore isolado não diagnostica risco nem autoriza alta; usar entrevista estruturada adequada e protocolo local por equipe capacitada.

Se não houver risco iminente, construir plano de segurança colaborativo, acesso ao apoio e redução segura de acesso a meios letais. Não substituir avaliação por promessa de não se ferir. O prazo de referência depende da gravidade e do acesso, podendo ser no mesmo dia; 24–72 h/7 dias não são regras universais. Na suspeita de abuso, violência, coerção ou ameaça a terceiros, acionar proteção e via institucional/legal local.

Abandono de tratamento exige avaliar acesso, efeitos adversos, capacidade e preferências; não atribuir automaticamente à depressão. Dor torácica, dispneia, síncope, delirium/intoxicação e efeitos de medicamentos exigem investigação clínica paralela. Risco de QT depende de molécula, dose, eletrólitos, QT basal e interações; usar o protocolo canônico, sem trocar classe automaticamente.
