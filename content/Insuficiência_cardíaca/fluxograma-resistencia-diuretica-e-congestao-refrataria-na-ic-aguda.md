---
title: "Fluxograma: Resistência Diurética e Congestão Refratária na IC Aguda — Sequência de Escalonamento"
slug: fluxograma-resistencia-diuretica-e-congestao-refrataria-na-ic-aguda
theme: "Insuficiência cardíaca"
kind: fluxograma
review_status: revisado
source_refs: ["Felker GM, Lee KL, Bull DA, et al. Diuretic strategies in patients with acute decompensated heart failure (DOSE-AHF). N Engl J Med. 2011;364(9):797-805. DOI: 10.1056/NEJMoa1005419. PMID: 21366472", "Bart BA, Goldsmith SR, Lee KL, et al. Ultrafiltration in decompensated heart failure with cardiorenal syndrome (CARRESS-HF). N Engl J Med. 2012;367(24):2296-2304. DOI: 10.1056/NEJMoa1210357. PMID: 23131078", "Mullens W, Dauw J, Martens P, et al. Acetazolamide in acute decompensated heart failure with volume overload (ADVOR). N Engl J Med. 2022;387(13):1185-1195. DOI: 10.1056/NEJMoa2203094. PMID: 36027559", "Trullàs JC, Morales-Rull JL, Casado J, Carrera-Izquierdo M, Sánchez-Marteles M, Conde-Martel A, et al. Combining loop with thiazide diuretics for decompensated heart failure: the CLOROTIC trial. Eur Heart J. 2023;44(5):411-421. DOI: 10.1093/eurheartj/ehac689. PMID: 36423214", "Ellison DH. The physiologic basis of diuretic synergism: its role in treating diuretic resistance. Ann Intern Med. 1991;114(10):886-894. PMID: 2014951", "ter Maaten JM, Valente MA, Damman K, Hillege HL, Navis G, Voors AA. Diuretic response in acute heart failure-pathophysiology, evaluation, and therapy. Nat Rev Cardiol. 2015;12(4):184-192. PMID: 25560378", "2021 ESC Guidelines for the diagnosis and treatment of acute and chronic heart failure. Eur Heart J. 2021;42(36):3599-3726", "2023 Focused Update of the 2021 ESC Guidelines for the diagnosis and treatment of acute and chronic heart failure. Eur Heart J. 2023;44(37):3627-3639. DOI: 10.1093/eurheartj/ehad195. PMID: 37622666"]
legacy_source: "Documento novo. Zoom decisório sobre um ramo que os dois fluxogramas já publicados de IC ('fluxograma-insuficiencia-cardiaca-aguda-descompensada.md' e a prosa de 'estrategia-diuretica-na-insuficiencia-cardiaca-aguda-descompensada.md'/'resistencia-diuretica-na-insuficiencia-cardiaca-aguda-mecanismos-e-bloqueio-sequencial-do-nefron.md') tratam como folha única ('escalonar a estratégia diurética — ver prosa abaixo'), sem árvore de decisão dedicada. Nenhum número novo: todos os PMIDs e resultados já estavam verificados nos dois documentos de origem, citados acima; nenhum corte numérico foi inventado onde a fonte já registra que não existe critério formal validado (os dois documentos-fonte declaram explicitamente que não há corte numérico validado de quando escalar — os nós de decisão deste fluxograma são deliberadamente qualitativos, fiéis a essa limitação)."
---

# Fluxograma: Resistência Diurética e Congestão Refratária na IC Aguda

Este fluxograma detalha, em árvore de decisão, a sequência de escalonamento que
`estrategia-diuretica-na-insuficiencia-cardiaca-aguda-descompensada.md` e
`resistencia-diuretica-na-insuficiencia-cardiaca-aguda-mecanismos-e-bloqueio-sequencial-do-nefron.md`
já descrevem em prosa — e que o fluxograma geral de IC aguda já publicado
(`fluxograma-insuficiencia-cardiaca-aguda-descompensada.md`) resume como um
único nó ("escalonar a estratégia diurética"). Aplica-se ao paciente que já
está em diurético de alça intravenoso e não está descongestionando como
esperado.

## Árvore de decisão

```mermaid
flowchart TD
  R0["Congestão persistente sob diurético<br/>de alça IV na IC aguda descompensada<br/>(edema, ganho de peso, estertores<br/>sem a melhora esperada)"]
  D1{"Diurético de alça já está em dose<br/>e via otimizadas (dose adequada,<br/>infusão contínua ou bolus frequente)?"}
  C1(["Otimizar primeiro o próprio diurético<br/>de alça — aumentar dose e/ou<br/>intensificar a via — antes de associar<br/>qualquer outro fármaco (DOSE-AHF: sem<br/>diferença significativa bolus x infusão<br/>nem dose baixa x alta nos desfechos<br/>coprimários, mas dose alta produziu<br/>maior diurese)"])
  D2{"Resposta à dose otimizada foi<br/>adequada (diurese/perda de peso<br/>conforme meta)?"}
  C2(["Manter o diurético de alça<br/>otimizado, reavaliar peso e diurese<br/>diariamente até euvolemia"])
  D3{"Há hipoperfusão ou choque<br/>cardiogênico associado (hipotensão<br/>persistente + hipoperfusão orgânica)?"}
  C3(["Priorizar suporte hemodinâmico —<br/>seguir o fluxograma de choque<br/>cardiogênico (estágios SCAI) antes<br/>de escalar a estratégia diurética"])
  D4{"Função renal e potássio permitem<br/>associar um segundo diurético com<br/>monitorização próxima?"}
  C4(["Reavaliar via alternativa: tratar o<br/>fator precipitante, otimizar a<br/>perfusão renal, e considerar<br/>ultrafiltração como resgate sob<br/>vigilância renal próxima — o próprio<br/>risco renal/eletrolítico já limita a<br/>associação farmacológica"])
  D5{"Estratégia de associação:<br/>acetazolamida ou tiazídico<br/>(bloqueio sequencial do néfron)?"}
  D6{"Resposta adequada após<br/>acetazolamida associada ao diurético<br/>de alça (ADVOR)?"}
  C5(["Manter diurético de alça +<br/>acetazolamida, reavaliar peso e<br/>diurese diariamente até euvolemia"])
  C6(["Escalar para ultrafiltração como<br/>resgate — reservada para quando a<br/>estratégia farmacológica escalonada<br/>falhou (CARRESS-HF: ultrafiltração<br/>foi inferior à terapia farmacológica<br/>escalonada, com mais piora renal e<br/>mais eventos adversos graves)"])
  D7{"Resposta adequada após tiazídico<br/>associado ao diurético de alça<br/>(bloqueio sequencial do néfron —<br/>CLOROTIC), com monitorização<br/>diária de potássio e creatinina?"}
  C7(["Manter diurético de alça +<br/>tiazídico, reavaliar peso, diurese,<br/>potássio e creatinina diariamente<br/>até euvolemia"])
  C8(["Escalar para ultrafiltração como<br/>resgate — reservada para quando a<br/>estratégia farmacológica escalonada<br/>falhou (CARRESS-HF: ultrafiltração<br/>foi inferior à terapia farmacológica<br/>escalonada, com mais piora renal e<br/>mais eventos adversos graves)"])

  R0 --> D1
  D1 -->|"Não — ainda não otimizado"| C1
  D1 -->|"Sim — já otimizado"| D2
  D2 -->|"Sim"| C2
  D2 -->|"Não — resistência diurética confirmada"| D3
  D3 -->|"Sim"| C3
  D3 -->|"Não — congestão sem choque"| D4
  D4 -->|"Não — risco renal/eletrolítico<br/>proibitivo para associar"| C4
  D4 -->|"Sim"| D5
  D5 -->|"Acetazolamida — descongestão<br/>mais rápida, sem excesso de piora<br/>renal demonstrado (ADVOR)"| D6
  D5 -->|"Tiazídico — maior perda de peso e<br/>diurese, à custa de mais piora<br/>renal (CLOROTIC)"| D7
  D6 -->|"Sim"| C5
  D6 -->|"Não"| C6
  D7 -->|"Sim"| C7
  D7 -->|"Não"| C8

  classDef conduta fill:#eef6ef,stroke:#2f7a4f,color:#12301f;
  class C1,C2,C3,C4,C5,C6,C7,C8 conduta;
```

## O que não está numa árvore de decisão validada

**Não há corte numérico validado** de débito urinário, natriurese pontual ou
peso para decidir "resposta inadequada" — os dois documentos-fonte já
registram essa ausência de critério formal (`estrategia-diuretica-...`: "Escore
ou critério formal de quando escalar para ultrafiltração — este documento
estabelece a hierarquia... não o gatilho numérico"; `resistencia-diuretica-...`:
"não um algoritmo numérico de decisão validado"). Os nós de decisão deste
fluxograma são deliberadamente qualitativos, fiéis a essa limitação da fonte,
em vez de inventar um corte que a evidência não sustenta.

**Dose e esquema posológico** de cada fármaco (furosemida, acetazolamida,
hidroclorotiazida) não são o objeto deste fluxograma — ver os documentos
`estrategia-diuretica-na-insuficiencia-cardiaca-aguda-descompensada.md` e
`resistencia-diuretica-na-insuficiencia-cardiaca-aguda-mecanismos-e-bloqueio-sequencial-do-nefron.md`
para o que está e não está verificado sobre dose.
