---
title: "Fluxograma: Rastreio de Hipertensão Pulmonar na Esclerose Sistêmica — Algoritmo DETECT"
slug: fluxograma-rastreio-hipertensao-pulmonar-esclerose-sistemica-detect
theme: "Hipertensão pulmonar"
kind: fluxograma
fonte_producao: chatgpt
review_status: revisado
review_note: "Árvore nova, recorte ainda não coberto pelos 5 fluxogramas já publicados nesta pasta (classificação em 5 grupos, diagnóstico geral ESC/ERS 2022, estratificação de risco/terapia combinada inicial, vasorreatividade aguda na HAP idiopática, CTEPH/operabilidade — nenhum trata de rastreio de HAP em doença do tecido conjuntivo). Construída a partir do estudo original do algoritmo DETECT (Coghlan JG et al., Ann Rheum Dis 2014, PMID 23687283), que já está citado e resumido no documento não-fluxograma 'hipertensao-arterial-pulmonar-associada-a-esclerose-sistemica-algoritmo-detect.md' desta mesma pasta — conferi esse documento antes de escrever para não duplicar o mesmo conteúdo em formato de prosa, e reaproveitei nesta árvore apenas os dois pontos de decisão estrutural do algoritmo (elegibilidade para o rastreio DETECT e limiar de encaminhamento para cateterismo), sem repetir a análise de desempenho já publicada naquele documento. PMID 23687283 conferido nesta sessão via PubMed E-utilities (esummary e efetch): título, periódico (Annals of the Rheumatic Diseases), volume 73, fascículo 7, páginas 1340-1349, ano 2014, DOI 10.1136/annrheumdis-2013-203301 e PMCID PMC4078756 batendo exatamente com o texto e com o registro já usado no documento-fonte desta pasta. O terceiro nó de decisão (resultado do cateterismo) e a conduta terapêutica subsequente da HAP confirmada apontam para o fluxograma já publicado 'fluxograma-hap-estratificacao-risco-terapia-combinada-inicial.md' desta mesma pasta, sem repetir aquele conteúdo aqui."
source_refs: ["Coghlan JG, Denton CP, Grünig E, et al; DETECT study group. Evidence-based detection of pulmonary arterial hypertension in systemic sclerosis: the DETECT study. Ann Rheum Dis. 2014;73(7):1340-1349. DOI: 10.1136/annrheumdis-2013-203301. PMID: 23687283. PMCID: PMC4078756 — conferido via PubMed E-utilities (esearch/esummary/efetch) nesta sessão; já citado e resumido em 'hipertensao-arterial-pulmonar-associada-a-esclerose-sistemica-algoritmo-detect.md' desta pasta.", "Humbert M, Kovacs G, Hoeper MM, et al. 2022 ESC/ERS Guidelines for the diagnosis and treatment of pulmonary hypertension. Eur Heart J. 2022;43(38):3618-3731. DOI: 10.1093/eurheartj/ehac237. PMID: 36017548 — conferido via PubMed E-utilities nesta sessão; usado apenas para o contexto de que a HAP associada a doença do tecido conjuntivo é um dos subtipos do grupo 1, e para apontar a conduta terapêutica subsequente ao fluxograma de estratificação de risco/terapia combinada já publicado nesta pasta."]
---

# Fluxograma: Rastreio de Hipertensão Pulmonar na Esclerose Sistêmica — Algoritmo DETECT

A hipertensão arterial pulmonar (HAP) associada à esclerose sistêmica (ES) é uma das
principais causas de morte nessa doença, e costuma se apresentar ainda pouco
sintomática — na coorte original do DETECT, 64% dos casos confirmados por cateterismo
estavam em classe funcional OMS I/II. O algoritmo diagnóstico genérico de hipertensão
pulmonar (suspeita clínica → ecocardiograma → cateterismo, ver fluxograma próprio desta
pasta) não foi desenhado para essa população específica e, aplicado a ela, perde quase
1 em cada 3 diagnósticos. O DETECT é o algoritmo de rastreio validado especificamente
para esclerose sistêmica de risco aumentado, e esta árvore organiza os dois pontos de
decisão estrutural dele — elegibilidade para o rastreio e limiar de encaminhamento para
cateterismo — sem repetir os coeficientes numéricos do escore, que não são ramos de
decisão, e sim entradas de um mesmo cálculo.

## Árvore de decisão

```mermaid
flowchart TD
  R0["Paciente com esclerose sistêmica (ES) —<br/>avaliar risco de hipertensão arterial pulmonar (HAP)"] --> D1{"Critérios de risco aumentado do DETECT preenchidos?<br/>ES há mais de 3 anos E DLCO% predita menor que 60%"}

  D1 -->|"Não preenche os critérios"| C1(["Fora da população validada pelo DETECT —<br/>manter rastreio clínico habitual de hipertensão pulmonar<br/>na esclerose sistêmica, sem aplicar o algoritmo DETECT"])

  D1 -->|"Preenche os critérios (ES > 3 anos e DLCO < 60%)"| S1["Passo 1 do DETECT: calcular escore a partir de<br/>6 variáveis não ecocardiográficas — razão CVF%/DLCO%<br/>predita, telangiectasia atual ou prévia, anticorpo<br/>anticentrômero sérico, NT-proBNP sérico, ácido úrico<br/>sérico e desvio de eixo para a direita no ECG"]

  S1 --> S2["Realizar ecocardiograma e calcular o escore do Passo 2,<br/>somando o escore do Passo 1 a duas variáveis<br/>ecocardiográficas — área do átrio direito e velocidade<br/>do jato de regurgitação tricúspide"]

  S2 --> D2{"Escore total do Passo 2 do DETECT acima do<br/>limiar de encaminhamento para cateterismo?"}

  D2 -->|"Abaixo do limiar"| C2(["Não encaminhar para cateterismo agora —<br/>repetir o algoritmo DETECT anualmente, dentro do<br/>rastreio de rotina da esclerose sistêmica de risco aumentado"])

  D2 -->|"Acima do limiar"| S3["Encaminhar para cateterismo cardíaco direito<br/>(padrão-ouro diagnóstico)"]

  S3 --> D3{"Cateterismo confirma hipertensão pulmonar<br/>pré-capilar (HAP, grupo 1)?"}

  D3 -->|"Confirma HAP"| C3(["HAP confirmada — iniciar avaliação de risco e terapia<br/>combinada específica (ver fluxograma de estratificação de<br/>risco e terapia combinada inicial na HAP, nesta pasta)"])

  D3 -->|"Não confirma HAP pré-capilar"| C4(["Cateterismo não confirma HAP — investigar outras causas<br/>de dispneia/sintoma na esclerose sistêmica (doença pulmonar<br/>intersticial, disfunção diastólica, hipertensão pulmonar dos<br/>grupos 2/3) e manter reavaliação clínica periódica"])

  classDef conduta fill:#eef6ef,stroke:#2f7a4f,color:#12301f;
  class C1,C2,C3,C4 conduta;
```

## O que a árvore não mostra

- **Os coeficientes exatos do escore não são ramos de decisão.** O Passo 1 combina 6
  variáveis por regressão ponderada em um único número, e o Passo 2 soma a esse número
  duas variáveis ecocardiográficas — são entradas de um mesmo cálculo, não uma sequência
  de perguntas sim/não. O artigo original disponibiliza nomogramas para uso clínico; esta
  árvore representa apenas os dois pontos em que o resultado do cálculo muda a conduta
  (fazer ou não ecocardiograma faz parte do fluxo padrão do Passo 1 para o Passo 2 — na
  prática todo paciente elegível é encaminhado ao ecocardiograma — e encaminhar ou não
  para cateterismo, que é o ramo que de fato bifurca a conduta).
- **A população de validação é estreita, e a árvore respeita esse limite.** O DETECT foi
  desenhado e validado apenas para esclerose sistêmica com mais de 3 anos de doença e
  DLCO% predita abaixo de 60% — fora desse subgrupo, a árvore não recomenda aplicar o
  algoritmo, e sim manter o rastreio clínico habitual (que não é detalhado aqui, por ser
  o padrão genérico já coberto no fluxograma de diagnóstico desta pasta).
- **O desempenho comparativo do DETECT contra o algoritmo genérico** (62% de encaminhamento
  a cateterismo com 4% de falso-negativo, contra 40% de encaminhamento e 29% de
  falso-negativo do algoritmo ESC/ERS da época aplicado à mesma coorte) está detalhado no
  documento "Hipertensão Arterial Pulmonar Associada à Esclerose Sistêmica: Algoritmo
  DETECT", já publicado nesta pasta — não repetido aqui para não duplicar conteúdo.
- **A conduta terapêutica da HAP confirmada não está nesta árvore.** Uma vez confirmada
  por cateterismo, a estratificação de risco e a escolha de terapia combinada seguem o
  mesmo caminho de qualquer HAP do grupo 1, coberto pelo fluxograma "HAP — terapia
  combinada inicial e escalonamento por estratificação de risco", já publicado nesta
  pasta.
- **Periodicidade de repetição do DETECT.** A árvore indica repetição anual para quem
  fica abaixo do limiar, refletindo a prática de rastreio periódico da doença de risco
  aumentado descrita no documento-fonte; o artigo original não define esse intervalo como
  parte do algoritmo propriamente dito, e por isso essa recomendação de intervalo carrega
  menor força de evidência do que os dois pontos de decisão do próprio DETECT.
