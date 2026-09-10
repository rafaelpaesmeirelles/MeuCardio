---
slug: fluxograma-ambulatorial-ascvd-diabetes-destino-encaminhamento
title: 'Fluxograma ambulatorial: ASCVD no diabetes — PS vs retorno vs Heart Team'
kind: fluxograma
theme: Diabetes e cardiologia
summary: 'Destino no diabetes com ASCVD: sintomas de SCA ou instabilidade exigem urgência; sintomas persistentes
  e anatomia/risco orientam avaliação especializada e eventual Heart Team, sem usar porcentagem isolada de isquemia
  como indicação automática.'
tags: []
source_refs:
- 'Marx N, Federici M, Schütt K, et al. 2023 ESC Guidelines for the management of cardiovascular disease in patients
  with diabetes. Eur Heart J. 2023;44(39):4043-4140. DOI: 10.1093/eurheartj/ehad192. PMID: 37622663'
- 'Vrints C, Andreotti F, Koskinas KC, et al. 2024 ESC Guidelines for the management of chronic coronary syndromes.
  Eur Heart J. 2024;45(36):3415-3537. DOI: 10.1093/eurheartj/ehae177. PMID: 39210710'
- 'Neumann FJ, Sousa-Uva M, Ahlsson A, et al; ESC Scientific Document Group. 2018 ESC/EACTS Guidelines on myocardial
  revascularization. Eur Heart J. 2019;40(2):87-165. DOI: 10.1093/eurheartj/ehy394. PMID: 30165437'
- 'Farkouh ME, Domanski M, Sleeper LA, et al; FREEDOM Trial Investigators. Strategies for multivessel revascularization
  in patients with diabetes. N Engl J Med. 2012;367(25):2375-2384. DOI: 10.1056/NEJMoa1211585. PMID: 23121323'
evidence_level: null
source_tier: A
review_status: revisado
gaps: []
published: false
---

# Fluxograma ambulatorial: ASCVD no diabetes — destino de encaminhamento

Prosa: [sinalizadores-ambulatoriais-ascvd-no-diabetes-quando-encaminhar](/biblioteca/sinalizadores-ambulatoriais-ascvd-no-diabetes-quando-encaminhar) · [angina-ccs-persistente-no-diabetes-quando-discutir-revascularizacao](/biblioteca/angina-ccs-persistente-no-diabetes-quando-discutir-revascularizacao).

Não substitui a avaliação de lesão de órgão-alvo, IC/FA, hipoglicemia ou eventos adversos de iSGLT2/GLP-1, FREEDOM detalhado nem vias hospitalares de SCA.

## Árvore de decisão

```mermaid
flowchart TD
  R0["Consulta / teleatendimento<br/>diabético com ASCVD conhecida<br/>ou altamente suspeita"] --> D1{"Alarme de SCA / instabilização?<br/>repouso · crescendo · nitrato sem alívio<br/>ECG isquêmico no contexto clínico · equivalentes graves<br/>déficit focal novo/AVC-AIT<br/>membro agudamente doloroso/frio/pálido"}

  D1 -->|"Sim ou dúvida fundamentada"| C1(["PS / urgência AGORA<br/>Não teste ergométrico ambulatorial<br/>Não esperar retorno longo"])

  D1 -->|"Não"| D2{"Gatilho de revascularização?<br/>angina CCS persistente<br/>isquemia documentada >10% VE<br/>tronco significativo ou multiarterial não tratada<br/>ou revascularização incompleta/estratégia pendente"}

  D2 -->|"Sim"| DA{"Obstrução epicárdica significativa<br/>passível de revascularização?"}
  DA -->|"Confirmada"| P1
  DA -->|"Anatomia não definida"| CA(["Cardiologia: definir anatomia/fisiologia<br/>antes de indicar intervenção"])
  DA -->|"Não: ANOCA/INOCA"| CN(["Avaliação coronária funcional<br/>tratamento conforme mecanismo"])
  P1["Confirmar estabilidade<br/>Listar alarmes por escrito"]
  P1 --> C2(["Heart Team / discussão de<br/>revascularização em prazo CURTO<br/>dias–poucas semanas conforme rede<br/>Sem escolher CABG vs PCI isolado"])

  D2 -->|"Não"| D3{"Sintoma limítrofe ou dúvida<br/>de adesão / precipitantes?"}

  D3 -->|"Sim"| C3(["Retorno precoce<br/>Orientação escrita de alarmes<br/>Sem inventar doses neste fluxo"])
  D3 -->|"Não"| C4(["Plano escrito + retorno programado<br/>Manter prevenção secundária já prescrita"])

  C2 --> D4{"Acesso a Heart Team / avaliação<br/>de isquemia-anatomia OK?"}
  D4 -->|"Não, permanece estável"| C5(["Acionar cardiologia de referência<br/>ou regulação regional com prioridade"])
  D4 -->|"Deterioração / novo alarme"| C1
  D4 -->|"Sim"| C6(["Completar articulação<br/>Não diluir em retorno de 6 meses"])

  classDef conduta fill:#eef6ef,stroke:#2f7a4f,color:#12301f;
  classDef alerta fill:#fdecea,stroke:#b3261e,color:#3b0a0a;
  class C1 alerta;
  class C2,C3,C4,C6 conduta;
```

## Notas

- **D1** = gate de segurança SCA (ESC 2024 CCS / ESC 2023 diabetes).
- **D2** = gatilho de revascularização ambulatorial (angina persistente, isquemia >10% VE, multiarterial — ESC 2023 + FREEDOM/Heart Team).
- **D3–D4** = limítrofe vs estável; prazos curtos são operacionais de rede.
- **Não decide** doses, SCORE2, rastreio IC/FA, alarmes iSGLT2 nem a escolha final CABG vs PCI.

## Qualificação do destino

Angina persistente ou isquemia extensa exige reavaliação, mas revascularização requer obstrução epicárdica significativa, passível de tratamento. Se a anatomia não foi definida, encaminhar à cardiologia para investigação; se não houver obstrução relevante, seguir [ANOCA/INOCA](/biblioteca/anoca-inoca-angina-e-isquemia-sem-obstrucao-coronariana-esc-2024), sem indicar PCI/CABG por sintomas isolados.

Tronco de coronária esquerda significativo é gatilho próprio de avaliação prioritária, mesmo sem alto SYNTAX. Multiarterial já completamente revascularizada e clinicamente controlada não obriga nova discussão; a prioridade se aplica a doença não tratada, incompleta ou com estratégia pendente. Avaliar a indicação primeiro; decidir PCI/CABG depois, por anatomia, risco, preferências e Heart Team.

Falta de acesso, mantendo estabilidade, exige contato com cardiologia de referência ou regulação regional e plano de acompanhamento. Novo alarme muda o destino para urgência. Prazos em dias/semanas são operacionais e se ajustam ao risco; não são espera obrigatória. Déficit neurológico focal agudo, mesmo transitório, ou isquemia aguda de membro não seguem a fila coronariana eletiva.
