---
title: "Fluxograma: RCRI — estratificação de risco cardíaco cirúrgico e conduta"
slug: fluxograma-rcri-estratificacao-risco-cirurgico
theme: "Perioperatório"
kind: fluxograma
fonte_producao: chatgpt
review_status: revisado
review_note: "Verificado por Claude em 26/08/2026: fonte primaria conferida; conteudo derivado de documento(s) ja publicado(s) no acervo, listado(s) em source_refs."
source_refs:
  - "Lee TH, Marcantonio ER, Mangione CM, et al. Derivation and prospective validation of a simple index for prediction of cardiac risk of major noncardiac surgery. Circulation. 1999;100(10):1043-1049. PMID: 10477528. DOI: 10.1161/01.CIR.100.10.1043."
  - "Thompson A, Fleischmann KE, Smilowitz NR, et al. 2024 AHA/ACC/ACS/ASNC/HRS/SCA/SCCT/SCMR/SVM Guideline for Perioperative Cardiovascular Management for Noncardiac Surgery. Circulation. 2024;150:e351-e442. PMID: 39316661. DOI: 10.1161/CIR.0000000000001285."
  - "Derivado do documento já publicado no acervo 'RCRI (Lee): cálculo, interpretação e árvore de decisão' (content/Perioperatório/arvore-decisao-rcri-lee.md), que cita as mesmas duas fontes acima."
---

# Fluxograma: RCRI — estratificação de risco cardíaco cirúrgico e conduta

O Revised Cardiac Risk Index (RCRI) é a porta de entrada mais usada para estratificar risco cardíaco antes de cirurgia não cardíaca — seis critérios binários, um ponto cada. O ponto que costuma ser pulado é que o número final **não é uma autorização cirúrgica**: ele decide se a avaliação segue por um caminho de baixa exigência ou se abre a pergunta seguinte, sobre capacidade funcional e necessidade de investigação adicional.

Os seis critérios que compõem a pontuação: cirurgia de alto risco, cardiopatia isquêmica, insuficiência cardíaca, doença cerebrovascular, diabetes tratado com insulina e creatinina sérica pré-operatória acima de 2,0 mg/dL.

## Árvore de decisão

```mermaid
flowchart TD
  R0["Paciente candidato a cirurgia não cardíaca eletiva"] --> P1["Calcular o RCRI: 1 ponto para cada um dos 6 critérios — cirurgia de alto risco, cardiopatia isquêmica, insuficiência cardíaca, doença cerebrovascular, diabetes em uso de insulina, creatinina acima de 2,0 mg/dL"]
  P1 --> D1{"Pontuação do RCRI"}

  D1 -->|"0 ou 1 ponto (RCRI menor ou igual a 1)"| P2["Risco basal baixo; risco calculado NÃO elevado no algoritmo contemporâneo"]
  P2 --> D2{"Há modificador de risco ou condição cardiovascular ativa (valvopatia grave, síndrome coronariana aguda ou recente, insuficiência cardíaca descompensada, arritmia significativa)?"}
  D2 -->|"Não"| C1(["Prosseguir para a cirurgia; não investigar de rotina só por causa do RCRI baixo"])
  D2 -->|"Sim"| C2(["Avaliação dirigida da condição cardiovascular ativa antes de prosseguir com a cirurgia"])

  D1 -->|"2 ou mais pontos (RCRI maior que 1)"| P3["Risco calculado elevado no algoritmo contemporâneo"]
  P3 --> D3{"Capacidade funcional avaliada, preferencialmente pelo DASI"}
  D3 -->|"DASI maior que 34 (boa capacidade funcional)"| C3(["Prosseguir com otimização clínica, sem investigação cardíaca adicional de rotina"])
  D3 -->|"DASI menor ou igual a 34, ou capacidade funcional desconhecida/ruim"| D4{"Um exame adicional (biomarcador ou imagem) mudaria a conduta cirúrgica?"}
  D4 -->|"Não"| C4(["Prosseguir conforme o contexto clínico, sem exame que não mudaria a conduta"])
  D4 -->|"Sim"| C5(["Considerar dosagem de biomarcadores (NT-proBNP/troponina) e investigação adicional antes de decidir a via cirúrgica"])

  classDef conduta fill:#eef6ef,stroke:#2f7a4f,color:#12301f;
  class C1,C2,C3,C4,C5 conduta;
```

## O que a árvore não mostra

**RCRI ≤1 não encerra a avaliação sozinho.** Valvopatia grave, hipertensão pulmonar grave, cardiopatia congênita de alto risco, stent ou revascularização recente, AVC recente, dispositivo cardíaco implantável e fragilidade são modificadores que podem exigir estratégia própria independentemente da pontuação — por isso a árvore inclui essa pergunta mesmo no ramo de risco baixo.

**As taxas de evento associadas a cada classe (0, 1, 2, ≥3 pontos) são da coorte original de Lee et al. 1999** e não devem ser apresentadas como probabilidade individual exata em 2026 — por isso a árvore usa a categorização binária (≤1 vs. >1) que a diretriz AHA/ACC 2024 cita como limiar prático, em vez de repetir os quatro números da coorte de derivação como se fossem ramos de conduta.

**O RCRI não incorpora idade como variável contínua, não mede capacidade funcional diretamente e não discrimina bem todos os tipos cirúrgicos modernos** — é exatamente por isso que, no ramo de risco elevado, o próximo passo obrigatório é avaliar capacidade funcional, não pedir exame de imagem direto.