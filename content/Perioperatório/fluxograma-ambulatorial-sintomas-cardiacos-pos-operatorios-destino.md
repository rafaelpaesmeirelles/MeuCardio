---
title: "Fluxograma ambulatorial: sintomas cardíacos pós-operatórios — PS agora vs. retorno precoce vs. seguimento MINS"
slug: fluxograma-ambulatorial-sintomas-cardiacos-pos-operatorios-destino
theme: "Perioperatório"
kind: fluxograma
fonte_producao: grok
summary: "Árvore ambulatorial pós-cirurgia não cardíaca: gate de alarme (SCA, IC aguda, arritmia/síncope, TEP, hipoperfusão), braço de sintoma controlável com retorno precoce, e braço MINS estável para seguimento cardiovascular sem doses."
review_status: revisado
review_note: "Revisão científica/adversarial 08/09/2026: findings PR872 reconstruídos; urgência, bibliografia e limites revistos. Fonte grok preservada."
source_refs:
  - "Thompson A, Fleischmann KE, Smilowitz NR, et al. 2024 AHA/ACC/ACS/ASNC/HRS/SCA/SCCT/SCMR/SVM Guideline for Perioperative Cardiovascular Management for Noncardiac Surgery. Circulation. 2024;150:e351-e442. DOI: 10.1161/CIR.0000000000001285. PMID: 39316661"
  - "Halvorsen S, Mehilli J, Cassese S, et al; ESC Scientific Document Group. 2022 ESC Guidelines on cardiovascular assessment and management of patients undergoing non-cardiac surgery. Eur Heart J. 2022;43(39):3826-3924. DOI: 10.1093/eurheartj/ehac270. PMID: 36017553"
  - "Writing Committee for the VISION Study Investigators; Devereaux PJ, Biccard BM, Sigamani A, et al. Association of Postoperative High-Sensitivity Troponin Levels With Myocardial Injury and 30-Day Mortality Among Patients Undergoing Noncardiac Surgery. JAMA. 2017;317(16):1642-1651. DOI: 10.1001/jama.2017.4360. PMID: 28444280"
  - "Gualandro DM, Fornari LS, Caramelli B, et al. Diretriz de Avaliação Cardiovascular Perioperatória da Sociedade Brasileira de Cardiologia – 2024. Arq Bras Cardiol. 2024;121(9):e20240590. DOI: 10.36660/abc.20240590"
---

# Fluxograma ambulatorial: sintomas cardíacos pós-operatórios — destino

Prosa: [`sinalizadores-ambulatoriais-sintomas-cardiacos-pos-cirurgia-nao-cardiaca-quando-encaminhar`](/biblioteca/sinalizadores-ambulatoriais-sintomas-cardiacos-pos-cirurgia-nao-cardiaca-quando-encaminhar). Braço MINS: [`mins-apos-alta-seguimento-ambulatorial-alarme-e-retorno`](/biblioteca/mins-apos-alta-seguimento-ambulatorial-alarme-e-retorno). Vigilância hospitalar: [`mins-lesao-miocardica-pos-operatoria-vigilancia-e-arvore-de-decisao`](/biblioteca/mins-lesao-miocardica-pos-operatoria-vigilancia-e-arvore-de-decisao).

## Árvore de decisão

```mermaid
flowchart TD
  R0["Consulta / contato ambulatorial<br/>após cirurgia NÃO cardíaca<br/>(pós-alta ou retorno precoce)"] --> D1{"Há alarme de PS?<br/>angina/SCA, IC aguda/hipoxemia<br/>síncope / arritmia grave<br/>suspeita TEP / hipoperfusão<br/>sangramento com instabilidade"}

  D1 -->|"Sim ou dúvida fundamentada"| C1(["Encaminhar AGORA ao PS / emergência<br/>Não atrasar por 'aguardar retorno<br/>do cirurgião' ou troponina ambulatorial"])

  D1 -->|"Não"| D2{"Sintoma cardiovascular novo<br/>sem hipoperfusão?<br/>dor atípica, dispneia de esforço,<br/>edema, palpitações, pré-síncope"}

  D2 -->|"Sim"| P1["ECG ± troponina/BNP se estável<br/>Revisar ferida, Hb, SpO2, panturrilhas<br/>Checar se houve MINS na internação"]
  P1 --> DE{"Achado agudo ou estabilidade incerta?"}
  DE -->|"Sim"| C1
  DE -->|"Não"| C2(["Reavaliação individualizada apenas<br/>após excluir hipótese aguda relevante<br/>Orientação escrita de alarmes"])

  D2 -->|"Sem sintoma novo"| D3
  D2 -->|"Sintoma novo mesmo brando"| P1{"História de MINS / troponina<br/>elevada na internação<br/>ou alto risco CV residual?"}

  D3 -->|"Sim"| C3(["Seguimento cardiovascular planejado<br/>Corrigir precipitantes; otimização do risco conforme mecanismo<br/>Ver mins-apos-alta — SEM doses aqui"])
  D3 -->|"Não"| C4(["Plano usual pós-op cirúrgico<br/>Reforçar sinais de alarme<br/>Retorno conforme especialidade"])

  C2 --> D4{"Acesso e suporte garantidos?"}
  D4 -->|"Acesso insuficiente sem piora"| C5
  D4 -->|"Piora / angina recorrente"| C1(["Antecipar retorno 24 h ou PS<br/>se surgir alarme da tabela"])
  D4 -->|"Sim"| C6(["Manter plano individual seguro<br/>Não substituir PS por exame<br/>agendado daqui a semanas"])

  classDef conduta fill:#eef6ef,stroke:#2f7a4f,color:#12301f;
  classDef alerta fill:#fdecea,stroke:#b3261e,color:#3b0a0a;
  class C1,C5 alerta;
  class C2,C3,C4,C6 conduta;
```

## Notas

- **D1** = gate de segurança (isquemia, IC aguda, arritmia/síncope, TEP, hipoperfusão — AHA/ACC 2024 / ESC 2022).
- **D2** = sintoma ambulatorial controlável → destino clínico precoce + ECG/biomarcadores se estável.
- **D3** = ponte para seguimento pós-MINS (VISION prognóstico; AHA/ACC: follow-up cardiovascular razoável).
- Não decide doses de antitrombóticos, diuréticos nem antiarrítmicos; não substitui a árvore hospitalar de MINS nem o pacote pré-op #836.

## Precisão diagnóstica e segurança

MINS é lesão miocárdica de mecanismo presumivelmente isquêmico após cirurgia, não qualquer troponina elevada. Excluir causas claramente não isquêmicas (por exemplo sepse, TEP ou miocardite); taquiarritmia pode exigir análise causal individual. ECG normal ou troponina isolada não excluem síndrome aguda. Dispneia nova tem também causas pulmonares, anemia, sangramento e infecção. Melena/sangramento clinicamente relevante ou queda inexplicada de Hb exigem avaliação no mesmo dia mesmo sem choque, incluindo equipe cirúrgica. MANAGE estudou selecionados: não iniciar dabigatrana/DAPT por troponina alta; considerar hemostasia, mecanismo e indicações preexistentes.
