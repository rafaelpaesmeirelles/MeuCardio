---
title: "Fluxograma: Fadiga e Intolerância ao Esforço — do sintoma ao próximo exame"
slug: fluxograma-fadiga-e-intolerancia-ao-esforco-proximo-passo
theme: "Geral"
kind: fluxograma
summary: "Árvore de decisão para reconhecer red flags, definir o fenótipo que limita o esforço e escolher ECG, laboratório dirigido, ecocardiograma, monitorização, teste de esforço ou CPET conforme a pergunta clínica."
review_status: revisado
source_refs: ["Heidenreich PA, Bozkurt B, Aguilar D, et al. 2022 AHA/ACC/HFSA Guideline for the Management of Heart Failure. Circulation. 2022;145(18):e895-e1032. DOI: 10.1161/CIR.0000000000001063. PMID: 35363499.", "Humbert M, Kovacs G, Hoeper MM, et al. 2022 ESC/ERS Guidelines for the diagnosis and treatment of pulmonary hypertension. Eur Heart J. 2022;43(38):3618-3731. DOI: 10.1093/eurheartj/ehac237. PMID: 36017548.", "Ommen SR, Ho CY, Asif IM, et al. 2024 AHA/ACC/AMSSM/HRS/PACES/SCMR Guideline for the Management of Hypertrophic Cardiomyopathy. J Am Coll Cardiol. 2024;83(23):2324-2405. DOI: 10.1016/j.jacc.2024.02.014. PMID: 38727647.", "Praz F, Borger MA, Lanz J, et al. 2025 ESC/EACTS Guidelines for the management of valvular heart disease. Eur Heart J. 2025;46(44):4635-4736. DOI: 10.1093/eurheartj/ehaf194. PMID: 40878295."]
---

# Fluxograma: Fadiga e Intolerância ao Esforço — do sintoma ao próximo exame

Este fluxograma é a superfície operacional do documento **Fadiga e Intolerância ao Esforço: Abordagem Cardiovascular Orientada à Decisão**. Ele não tenta diagnosticar a causa pela queixa de "cansaço"; primeiro identifica risco, depois pergunta **o que efetivamente interrompe o esforço** e só então escolhe o exame com maior chance de modificar a conduta.

## Árvore de decisão

```mermaid
flowchart TD
  R0["Fadiga, queda de desempenho<br/>ou intolerância ao esforço"] --> D0{"Há red flag?<br/>dor torácica importante, síncope/pré-síncope no esforço,<br/>dispneia em repouso/hipoxemia, hipotensão/hipoperfusão<br/>ou palpitação sustentada com sintomas graves"}

  D0 -->|Sim| C0(["Não tratar como fadiga crônica<br/>usar o fluxo específico de dor torácica, dispneia,<br/>palpitações ou síncope e definir destino urgente/emergencial"])
  D0 -->|Não| D1{"O que limita o esforço?"}

  D1 -->|"Dispneia, ortopneia, edema"| A1["Procurar IC, valvopatia,<br/>HP e doença pulmonar<br/>ECG + avaliação de congestão"]
  A1 --> D2{"Suspeita de IC ou<br/>doença estrutural?"}
  D2 -->|Sim| A2["Peptídeo natriurético quando apropriado<br/>+ ecocardiograma transtorácico"]
  A2 --> D3{"Avaliação de repouso<br/>explica a limitação?"}
  D3 -->|Sim| C1(["Seguir o módulo da doença encontrada<br/>e tratar/estratificar conforme guideline"])
  D3 -->|Não| C2(["Considerar CPET ou teste sob esforço<br/>conforme a hipótese clínica<br/>HFpEF, limitação pulmonar/vascular ou doença dinâmica"])
  D2 -->|Não| C3(["Investigar causas não cardíacas dirigidas<br/>e reconsiderar CPET se dispneia permanecer inexplicada"])

  D1 -->|"Dor ou pressão torácica"| C4(["Migrar para triagem de dor torácica<br/>definir risco e teste de isquemia/imagem apropriado"])

  D1 -->|"Palpitação ou frequência inadequada"| A3["ECG e revisão de medicamentos<br/>correlacionar sintoma com ritmo"]
  A3 --> D4{"Sintoma é episódico ou<br/>a dúvida é resposta ao exercício?"}
  D4 -->|Episódico| C5(["Monitorização ambulatorial<br/>adequada à frequência dos eventos"])
  D4 -->|"Relacionado ao esforço"| C6(["Teste de esforço/monitorização durante esforço<br/>quando a pergunta é resposta cronotrópica ou arritmia"])

  D1 -->|"Pré-síncope ou síncope"| C7(["Avaliação cardiovascular prioritária<br/>ECG + imagem dirigida<br/>considerar arritmia, CMH/LVOTO, EAo e HP"])

  D1 -->|"Fraqueza/fadiga sem sintoma cardiopulmonar dominante"| A4["Revisar medicações, sono, infecção,<br/>anemia/ferro, tireoide, rim/metabolismo e descondicionamento"]
  A4 --> D5{"Há achado cardiovascular,<br/>fator de risco importante ou queda funcional inexplicada?"}
  D5 -->|Não| C8(["Investigar causa sistêmica dirigida<br/>e acompanhar evolução funcional"])
  D5 -->|Sim| C9(["ECG e avaliação estrutural dirigida<br/>escalonar para teste sob esforço se repouso for inconclusivo"])

  classDef conduta fill:#eef5f8,stroke:#1c7293,color:#0b2e45;
  class C0,C1,C2,C3,C4,C5,C6,C7,C8,C9 conduta;
```

## Ramos que merecem uma regra própria

### Dispneia persistente depois de embolia pulmonar

Se a queda de tolerância ou a dispneia é persistente ou nova após embolia pulmonar, a diretriz ESC/ERS 2022 recomenda investigação adicional para **CTEPH/CTEPD (Classe I)**. Esse antecedente muda a árvore: não se deve encerrar o caso como descondicionamento sem reconsiderar doença tromboembólica crônica.

### CMH com sintomas e eco de repouso sem obstrução relevante

Em paciente sintomático com cardiomiopatia hipertrófica e sem gradiente de via de saída ≥50 mmHg em repouso ou à provocação convencional, a AHA/ACC 2024 recomenda **ecocardiograma de exercício (Classe I, B-NR)** para detectar e quantificar LVOTO dinâmica.

### Valvopatia com discrepância entre relato e capacidade funcional

A ESC/EACTS 2025 enfatiza que pacientes podem reduzir atividades de forma gradual e negar sintomas. Teste de exercício pode revelar sintomas e intolerância hemodinâmica; CPET pode ajudar quando é necessário separar limitação cardíaca, pulmonar ou descondicionamento.

### Dispneia inexplicada após avaliação inicial

Na AHA/ACC/HFSA 2022, CPET é **razoável (Classe IIa, C-LD)** em paciente ambulatorial com dispneia inexplicada para avaliar sua causa. O exame deve responder uma pergunta fisiológica concreta; não é rastreio universal para fadiga.

## O que este fluxograma deliberadamente não faz

- não cria cutoff próprio de frequência cardíaca, VO2, BNP/NT-proBNP ou teste de caminhada;
- não transforma um resultado isolado em diagnóstico;
- não presume que ECG ou ecocardiograma de repouso normais excluam HFpEF, LVOTO dinâmica, HP inicial ou arritmia intermitente;
- não prescreve quais exames laboratoriais devem ser pedidos para todo paciente com fadiga;
- não substitui os fluxos específicos quando dor torácica, dispneia, palpitação ou síncope são o sintoma dominante.

## Conexões no CorVIA

- Documento-base: `fadiga-e-intolerancia-ao-esforco-abordagem-cardiovascular-orientada-a-decisao`;
- Triagens: `dor-toracica`, `dispneia`, `palpitacoes`, `sincope-e-pre-sincope`;
- IC: `icfer-classificacao-diagnostico-quatro-pilares` e módulos de HFpEF;
- CMH: `cardiomiopatia-hipertrofica-diagnostico-e-tratamento-diretriz-brasileira-2024`;
- Valvopatias: `valvopatias-atualizacao-diretriz-esceacts-2025`;
- HP: `fluxograma-hipertensao-pulmonar-diagnostico-esc-ers-2022` e `ecocardiograma-na-triagem-da-hap-sinais-e-limites-de-acuracia`.
