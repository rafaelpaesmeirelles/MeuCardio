---
title: "Checklist ambulatorial: AINE no retorno cardiológico"
slug: checklist-ambulatorial-aine-no-retorno-cardiologico
theme: "Farmacologia"
kind: protocolo
fonte_producao: grok
summary: "Lista de 60–90 segundos: perguntar AINE OTC pelo nome, cruzar com IC/SCA/HAS/DRC/anticoagulação, e agir se edema, isquemia ou sangramento — sem doses."
review_status: pendente_revisao
review_note: "Doc 3/3 do pacote AINE ambulatorial (07/09/2026). Complementa sinalizadores + fluxograma. CNT PMID 23726390; AHA 2007 PMID 17325246; ESC HF 2021; PRECISION PMID 27752637. Sem doses."
source_refs:
  - "Coxib and traditional NSAID Trialists' (CNT) Collaboration, Bhala N, Emberson J, Merhi A, et al. Vascular and upper gastrointestinal effects of non-steroidal anti-inflammatory drugs: meta-analyses of individual participant data from randomised trials. Lancet. 2013;382(9894):769-779. DOI: 10.1016/S0140-6736(13)60900-9. PMID: 23726390"
  - "Antman EM, Bennett JS, Daugherty A, Furberg C, Roberts H, Taubert KA. Use of nonsteroidal antiinflammatory drugs: an update for clinicians: a scientific statement from the American Heart Association. Circulation. 2007;115(12):1634-1642. DOI: 10.1161/CIRCULATIONAHA.106.181646. PMID: 17325246"
  - "McDonagh TA, Metra M, Adamo M, et al. 2021 ESC Guidelines for the diagnosis and treatment of acute and chronic heart failure. Eur Heart J. 2021;42(36):3599-3726. DOI: 10.1093/eurheartj/ehab368"
  - "Nissen SE, Yeomans ND, Solomon DH, et al. Cardiovascular Safety of Celecoxib, Naproxen, or Ibuprofen for Arthritis (PRECISION). N Engl J Med. 2016;375(26):2519-2529. DOI: 10.1056/NEJMoa1611593. PMID: 27752637"
---

# Checklist ambulatorial: AINE no retorno cardiológico

Cenário: adulto no retorno (IC, DAC, HAS, FA anticoagulada, prevenção, geriatria) com dor musculoesquelética ou uso de “anti-inflamatório da farmácia”.

Complementa: [`sinalizadores-ambulatoriais-de-aine-no-paciente-cardiologico`](sinalizadores-ambulatoriais-de-aine-no-paciente-cardiologico.md) · [`fluxograma-ambulatorial-aine-quando-evitar-e-escalar`](fluxograma-ambulatorial-aine-quando-evitar-e-escalar.md).

Ensaio de magnitude: [`anti-inflamatorios-nao-esteroidais-aines-e-risco-cardiovascular-metanalise-cnt`](../Geral/anti-inflamatorios-nao-esteroidais-aines-e-risco-cardiovascular-metanalise-cnt.md).

## Checklist de 60–90 segundos

| Item | Pergunta / dado | Se positivo / alarme |
|---|---|---|
| Nome | Qual comprimido? (ibuprofeno, diclofenaco, naproxeno, celecoxibe, “muscular”) | Anotar molécula — diclofenaco ≠ naproxeno (CNT) |
| IC | FE reduzida/preservada, edema, ortopneia, BNP alto recente | **Evitar AINE** (ESC 2021; CNT IC de classe) |
| DAC | IAM/angina/stent recente | Evitar; dor torácica → via SCA |
| HAS | PA↑ sem mudança de fármacos | Suspender AINE; ver [#828](https://github.com/rafaelpaesmeirelles/MeuCardio/pull/828) |
| Rim | Creatinina↑ / IECA+BRA+diurético | Freio renal; cardiorrenal [#829](https://github.com/rafaelpaesmeirelles/MeuCardio/pull/829) |
| Sangue | Anticoagulado / HDA / anemia | [#860](https://github.com/rafaelpaesmeirelles/MeuCardio/pull/860); emergência se ativo |
| Prescritor | Reumato/orto manteve AINE crônico | Contato coordenado + menor exposição |

## Alarmes → agir agora

| Situação | Destino |
|---|---|
| Edema + dispneia sob AINE | Suspender + pacote [#842](https://github.com/rafaelpaesmeirelles/MeuCardio/pull/842) |
| Dor torácica / equivalente | Via SCA — não “só muscular” |
| Hemorragia digestiva / anemia aguda | Emergência + [#860](https://github.com/rafaelpaesmeirelles/MeuCardio/pull/860) |
| Crise hipertensiva ambulatorial + AINE | Suspender + [#828](https://github.com/rafaelpaesmeirelles/MeuCardio/pull/828) |

## O que reforçar (sem protocolar dose)

1. Em IC **não há AINE seguro** para o eixo de descompensação (CNT; ESC 2021).
2. OTC não é “inofensivo” — perguntar pelo nome (AHA 2007).
3. Naproxeno pode ser menos desfavorável no eixo trombótico na CNT, mas **não** livra de IC/GI.
4. PRECISION contextualiza celecoxibe vs ibuprofeno/naproxeno em artrite selecionada — não libera AINE na IC.

## Armadilhas

- Esquecer de perguntar AINE em todo retorno de IC.
- Trocar diclofenaco por ibuprofeno e achar o problema resolvido na IC.
- Deixar AINE contínuo “porque a reumato mandou” sem contato.

## Limite da evidência

Checklist operacional de **seguimento cardiológico**. Esquemas anti-inflamatórios especializados ficam fora de escopo.
