---
slug: fluxograma-ambulatorial-cardiomiopatia-quando-escalar-imagem-genetica
title: 'Fluxograma ambulatorial: cardiomiopatia — quando escalar imagem e genética'
kind: fluxograma
theme: Cardiomiopatias
summary: 'Árvore de consultório: alarme clínico → urgência; sem alarme → eco/ECG; quando pedir RMC; quando disparar
  investigação de amiloide/Fabry; quando genética e rastreio familiar — alinhada à ESC 2023.'
tags: []
source_refs:
- 'Arbelo E; Protonotarios A; Gimeno JR. 2023 ESC Guidelines for the management of cardiomyopathies. Eur Heart J.
  2023;44:3503. DOI: 10.1093/eurheartj/ehad194. PMID: 37622657.'
- 'Garcia-Pavia P, Rapezzi C, Adler Y, et al. Diagnosis and treatment of cardiac amyloidosis: a position statement
  of the ESC Working Group on Myocardial and Pericardial Diseases. Eur J Heart Fail. 2021;23(4):512-526. DOI: 10.1002/ejhf.2140'
evidence_level: null
source_tier: A
review_status: revisado
gaps: []
published: false
---

# Fluxograma ambulatorial: cardiomiopatia — quando escalar imagem e genética

Prosa: [sinalizadores-ambulatoriais-de-cardiomiopatia-hipertrofica-quando-encaminhar](/biblioteca/sinalizadores-ambulatoriais-de-cardiomiopatia-hipertrofica-quando-encaminhar) e [sinalizadores-ambulatoriais-de-suspeita-de-amiloidose-cardiaca](/biblioteca/sinalizadores-ambulatoriais-de-suspeita-de-amiloidose-cardiaca).

Não substitui [fluxograma-cardiomiopatia-hipertrofica-esc-2023](/biblioteca/fluxograma-cardiomiopatia-hipertrofica-esc-2023), [fluxograma-amiloidose-cardiaca-diagnostico-nao-invasivo](/biblioteca/fluxograma-amiloidose-cardiaca-diagnostico-nao-invasivo) nem [fluxograma-investigacao-genetica-cardiomiopatia-historia-familiar-morte-subita](/biblioteca/fluxograma-investigacao-genetica-cardiomiopatia-historia-familiar-morte-subita).

## Árvore de decisão

```mermaid
flowchart TD
  R0["Consulta: hipertrofia / IC / suspeita de cardiomiopatia"] --> D1{"Alarme urgente?<br/>síncope de esforço, TV/FV,<br/>IC aguda, angina instável"}

  D1 -->|"Sim"| C1(["Encaminhar AGORA<br/>PS / urgência / centro"])

  D1 -->|"Não"| P1["ECG + eco completo<br/>história familiar dirigida"]
  P1 --> D2{"Há red flags de fenocópia?<br/>amiloide / Fabry / outra"}

  D2 -->|"Amiloide suspeita"| C2(["Imunofixação sérica e urinária + cadeias leves<br/>em paralelo à cintilografia com SPECT<br/>Ver sinalizadores-amiloidose<br/>e fluxograma não invasivo"])
  D2 -->|"Fabry / outra"| C3(["Seguir red flags Fabry / etiológico<br/>ESC 2023"])
  D2 -->|"Não óbvio"| D3{"RMC na caracterização inicial; disponível?<br/>diagnóstico, fibrose, diferencial"}

  D3 -->|"Sim"| C4["Solicitar RMC cardíaca<br/>retorno com laudo"]
  D3 -->|"Indisponível / contraindicação"| ACCESS["Planejar acesso/referência ou alternativa apropriada"]
  ACCESS --> D4{"Genética / rastreio familiar<br/>indicados?"}

  D4 -->|"Sim"| C5(["Aconselhamento genético<br/>+ rastreio de 1º grau<br/>fluxograma genética MS"])
  D4 -->|"Não por ora"| C6(["Plano ambulatorial<br/>retorno precoce se sintomas<br/>reevaluar imagem/genética"])

  C4 --> D4

  classDef conduta fill:#eef6ef,stroke:#2f7a4f,color:#12301f;
  classDef alerta fill:#fdecea,stroke:#b3261e,color:#3b0a0a;
  class C1 alerta;
  class C2,C3,C4,C5,C6 conduta;
```

## Notas

- **D1** = gate de segurança ambulatorial (não negociável).
- **D2** = fenocópia antes de rotular “HCM sarcomérica”.
- **C2** = investigação paralela de amiloidose, com interpretação conjunta e exclusão monoclonal antes de diagnóstico não invasivo ATTR.
- **D4** = genética com aconselhamento, não “pedido solto”.
- Suspeita de cardiomiopatia arritmogênica ou sarcoidose requer avaliação etiológica e arrítmica específica.

Genética requer aconselhamento e classificação formal de variantes. VUS não é variante causal para orientar teste preditivo em cascata; manter rastreio clínico familiar conforme fenótipo e diretriz.
