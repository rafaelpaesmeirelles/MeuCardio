---
title: "Candidatos ambulatoriais à avaliação de CDI após síncope: quando encaminhar"
slug: candidatos-ambulatoriais-avaliacao-cdi-apos-sincope-quando-encaminhar
theme: "Síncope"
kind: protocolo
fonte_producao: grok
summary: "Gate de consultório: síncope + substrato de alto risco de morte súbita — quando encaminhar para avaliação de elegibilidade a CDI / EP, sem decidir implante, sem doses e sem duplicar disfunção de dispositivo já coberto em Dispositivos."
review_status: pendente_revisao
review_note: "Doc 3/3 do pacote ambulatory Síncope EPS/CDI (07/09/2026), além de #859. Lacuna ausente em main/PRs abertos de Síncope. Anti-colisão com #835 (disfunção eletrodo/choque CDI). ESC 2018 PMID 29562304; ACC/AHA/HRS 2017 PMID 28280231. Sem doses; sem inventar classes de implante."
source_refs:
  - "Brignole M, Moya A, de Lange FJ, et al.; ESC Scientific Document Group. 2018 ESC Guidelines for the diagnosis and management of syncope. Eur Heart J. 2018;39(21):1883-1948. DOI: 10.1093/eurheartj/ehy037. PMID: 29562304"
  - "Shen WK, Sheldon RS, Benditt DG, et al. 2017 ACC/AHA/HRS Guideline for the Evaluation and Management of Patients With Syncope. Circulation. 2017;136(5):e60-e122. DOI: 10.1161/CIR.0000000000000499. PMID: 28280231"
  - "Brignole M, Moya A, de Lange FJ, et al. Practical Instructions for the 2018 ESC Guidelines for the diagnosis and management of syncope. Eur Heart J. 2018;39(21):e43-e80. DOI: 10.1093/eurheartj/ehy071"
---

# Candidatos ambulatoriais à avaliação de CDI após síncope: quando encaminhar

Uso: paciente com **síncope** (recente ou recorrente) em **consultório**, sem indicação imediata de PS, mas com **substrato** que levanta risco de morte súbita cardíaca (MSC). A pergunta é **quando encaminhar para avaliação de elegibilidade a CDI / eletrofisiologia**, não “implantar CDI neste encontro”.

Não substitui:
- disfunção de eletrodo / choque em quem **já tem** CDI — pasta Dispositivos / pacote #835;
- pós-alta baixo risco — [`sinalizadores-ambulatoriais-sincope-pos-alta-quando-retornar`](sinalizadores-ambulatoriais-sincope-pos-alta-quando-retornar.md);
- EPS selecionado sem questão de CDI — [`sinalizadores-ambulatoriais-sincope-recorrente-inexplicada-quando-referir-eletrofisiologia`](sinalizadores-ambulatoriais-sincope-recorrente-inexplicada-quando-referir-eletrofisiologia.md);
- ILR após investigação negativa sem indicação convencional de CDI/MP — [`fluxograma-sincope-inexplicada-recorrente-monitor-de-eventos-implantavel`](fluxograma-sincope-inexplicada-recorrente-monitor-de-eventos-implantavel.md).

## Princípio

A ESC 2018 dedica manejo específico à **síncope inexplicada em pacientes com alto risco de MSC** e separa isso da síncope reflexa de baixo risco. O ACC/AHA/HRS 2017 (PMID 28280231) observa que o papel do EPS na avaliação de arritmias ventriculares na síncope **diminuiu** porque o CDI de **prevenção primária** em cardiomiopatia com disfunção ventricular grave já é indicação estabelecida: **EPS não é exigido** antes de considerar CDI nesse cenário. CDI pode reduzir risco de morte e **ainda assim não impedir** nova síncope.

Este gate só decide: **encaminhar agora para avaliação especializada** versus **não misturar com o caminho reflexo/ILR puro**.

## Encaminhar avaliação de CDI / risco de MSC (consultório)

| Contexto clínico | Sinal para escalar |
|---|---|
| Cardiomiopatia com FE reduzida já conhecida | Síncope (mesmo sem VA documentada no consultório) → discutir elegibilidade / timing com EP/IC avançada |
| VA sustentada documentada + síncope | Encaminhamento prioritário (não “aguardar Holter de rotina”) |
| Canalopatia / Brugada / QT longo / CPVT / MCH de alto risco já rotulados | Síncope arrítmica suspeita → reabrir estratificação com centro de referência |
| Cicatriz isquêmica + síncope inexplicada | Avaliar com EP (EPS selecionado **e/ou** caminho de dispositivo conforme substrato) |
| Recuperação de PCR / síncope com TV/FV abortada | Urgência / EP — fora do “plano ambulatorial estável” |

**Conduta mínima:** história + ECG + documentação da FE/estrutura; **encaminhar**; orientar sinais de PS; **não** protocolar zona de terapia, drogas antiarrítmicas com dose, nem “CDI empírico” neste texto.

## Não é este gate

- Síncope vasovagal típica, ECG normal, estrutura normal → educação / pacote pós-avaliação; **não** rotular como candidato a CDI.
- Quem **já tem** CDI e apresenta choque, ruído ou síncope → interrogação / Dispositivos (#835), não “nova elegibilidade”.
- Após investigação completa negativa, **sem** indicação convencional de CDI/MP → ILR (ESC Classe I A no fluxograma da pasta), não CDI “por exclusão”.

## Checklist de 90 segundos

1. Alarme de PS? → PS.
2. Substrato de MSC / FE reduzida / VA / canalopatia de risco? → **encaminhar avaliação de CDI/EP**.
3. Sem substrato de MSC, mas bifascicular/cicatriz selecionados? → EPS ([protocolo irmão](sinalizadores-ambulatoriais-sincope-recorrente-inexplicada-quando-referir-eletrofisiologia.md)).
4. Sem substrato? → ILR/monitorização ou plano reflexo — não inventar CDI.
5. Sem doses; sem laudo de implante neste encontro.

## Limite da evidência

Critérios formais de implante (FE numérica, tempo pós-IAM, prevenção secundária) pertencem às diretrizes de dispositivos/MSC e à decisão do especialista. Este documento **ancora** o encaminhamento ambulatorial na lógica ESC 2018 + ACC/AHA/HRS 2017 e **não** cria classes de recomendação de implante novas.
