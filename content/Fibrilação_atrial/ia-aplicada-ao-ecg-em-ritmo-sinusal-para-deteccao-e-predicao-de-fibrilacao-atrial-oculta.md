---
title: Inteligência Artificial Aplicada ao ECG em Ritmo Sinusal para Detecção e Predição de Fibrilação Atrial Oculta
slug: ia-aplicada-ao-ecg-em-ritmo-sinusal-para-deteccao-e-predicao-de-fibrilacao-atrial-oculta
theme: Fibrilação atrial
kind: documento
review_status: revisado
source_refs:
- 'An artificial intelligence-enabled ECG algorithm for the identification of patients with atrial fibrillation during sinus
  rhythm: a retrospective analysis of outcome prediction. 2019. PMID: 31378392. DOI: 10.1016/S0140-6736(19)31721-0.'
- 'AI-ECG for early detection of atrial fibrillation: First-year results from a stroke prevention study in Shimizu, Japan.
  2025. PMID: 40621219. DOI: 10.1002/joa3.70132.'
- 'Artificial intelligence 12-lead electrocardiography to determine atrial fibrillation risk among UK Biobank participants
  with predisposing conditions. 2026. PMID: 41815107. DOI: 10.1093/ehjdh/ztag025.'
- 'Artificial Intelligence Applied to Electrocardiograms Recorded in Sinus Rhythm for Detection and Prediction of Atrial Fibrillation:
  A Scoping Review. 2026. PMID: 41597485. DOI: 10.3390/medicina62010199.'
- 'Simple risk model predicts incidence of atrial fibrillation in a racially and geographically diverse population: the CHARGE-AF
  consortium. 2013. PMID: 23537808. DOI: 10.1161/JAHA.112.000102.'
- 'Noseworthy PA et al. Artificial intelligence-guided screening for atrial fibrillation using electrocardiogram during sinus
  rhythm: a prospective non-randomised interventional trial. 2022. PMID: 36179758. DOI: 10.1016/S0140-6736(22)01637-3.'
- 'Vedage NA et al. Risk-Guided Atrial Fibrillation Screening With Artificial Intelligence-Enabled Electrocardiogram Models:
  A VITAL-AF Trial Analysis. 2026. PMID: 41983618. DOI: 10.1016/j.jacc.2026.01.087.'
- 'Lee KJ et al. DEEP-AF design. 2026. DOI: 10.1016/j.hroo.2026.07.009. NCT07173673.'
- 'Liu WT et al. Artificial Intelligence-Enabled ECGs for Atrial Fibrillation Identification and Enhanced Oral Anticoagulant
  Adoption: A Pragmatic Randomized Clinical Trial. 2025. PMID: 40611485. DOI: 10.1161/JAHA.125.042106.'
fonte_producao: claude
review_note: Leitura integral, versões comparadas e oito abstracts PubMed primários conferidos. Corrigidos seguimento de sete
  dias e inclusão de ECG não sinusal no Shimizu, discriminação do modelo combinado no UK Biobank e anterioridade do estudo
  prospectivo Noseworthy. VITAL-AF foi análise de escores no ensaio por serviços, não ensaio de conduta guiada por IA; Liu
  identificava FA no traçado, não risco sinusal. Confirmado protocolo DEEP-AF no periódico (1.230, seis meses, ainda desenho).
  Mantidas distinções entre predição, diagnóstico documentado e benefício clínico.
summary: Um algoritmo pode estimar risco de fibrilação atrial a partir de um ECG em ritmo sinusal. Isso difere de identificar
  FA presente no próprio traçado e de registrar um episódio durante monitorização. Prever FA futura e identificar pessoas
  com FA paroxística já existente também são objetivos distintos. Um escore elevado não documenta a arritmia.
tags: []
source_tier: A
gaps: []
published: true
---

# IA aplicada ao ECG em ritmo sinusal para detecção e predição de FA

Um algoritmo pode estimar risco de fibrilação atrial a partir de um ECG em ritmo sinusal. Isso difere de identificar FA presente no próprio traçado e de registrar um episódio durante monitorização. Prever FA futura e identificar pessoas com FA paroxística já existente também são objetivos distintos. Um escore elevado não documenta a arritmia.

## Desenvolvimento retrospectivo: Attia 2019

Attia analisou 649.931 ECGs em ritmo sinusal de 180.922 pacientes da Mayo Clinic, com conjuntos separados para desenvolvimento, validação interna e teste. O rótulo positivo dependia de FA ou flutter documentado, e o teste incluía pessoas com FA previamente verificada. Portanto, não foi uma demonstração prospectiva de detecção exclusivamente de FA desconhecida. [Attia](https://doi.org/10.1016/S0140-6736(19)31721-0)

Com um ECG, AUROC foi 0,87, sensibilidade 79,0% e especificidade 79,5%; o F1 de 39,2% ajuda a evitar leitura excessivamente otimista da discriminação. Incorporar vários ECGs da janela de interesse elevou AUROC para 0,90, mas já é outra quantidade de informação. O estudo não provou qual mecanismo biológico o algoritmo reconhecia nem que seu uso reduzisse AVC.

## Shimizu: monitorização de sete dias e população não inteiramente sinusal

Masumura incluiu 362 participantes analisáveis em exames de saúde no Japão, sem FA conhecida. A avaliação utilizou monitorização de uma derivação por sete dias, detectando 11 casos de FA (3,0%). O título “primeiro ano” não transforma esses achados em incidência durante um ano de acompanhamento individual. [Shimizu 2025](https://doi.org/10.1002/joa3.70132)

Traçados não sinusais foram classificados como não aplicáveis à IA. A comparação principal agrupou risco moderado/alto **e não aplicáveis** contra baixo risco, OR 9,36 (IC95% 1,99–44,01). Ao excluir os não aplicáveis, OR foi 4,89 (0,88–27,1), sem significância estatística. Assim, a comparação principal não mede apenas desempenho intrínseco do algoritmo em ritmo sinusal.

AUROC de 0,75 versus 0,68 para CHADS₂ ≥1 é uma diferença numérica em amostra pequena, não prova de superioridade estatística nem comparação com um modelo clínico otimizado de incidência de FA. Seleção de voluntários, poucos eventos e duração da monitorização limitam a generalização.

## Evidência prospectiva anterior e validação populacional

Em 2022, Noseworthy já havia publicado estudo prospectivo intervencional não randomizado: 1.003 pessoas completaram monitorização de até 30 dias. FA foi detectada em 7,6% do grupo de alto risco e 1,6% do de baixo risco, OR 4,98 (2,11–11,75). A comparação secundária com cuidado usual usou controles pareados, não randomizados. Demonstrou enriquecimento do rendimento diagnóstico; não redução comprovada de AVC. Portanto, Shimizu não é a primeira evidência prospectiva dessa estratégia. [Noseworthy](https://doi.org/10.1016/S0140-6736(22)01637-3)

Zheng avaliou 21.842 participantes do UK Biobank com fatores predisponentes e sem FA, seguimento mediano de 3,7 anos. Em um e três anos, a IA isolada teve AUROC 0,73 e 0,69; o modelo clínico, 0,71 e 0,71; a combinação, 0,75 e 0,74. Os valores da combinação não devem ser atribuídos à IA isolada. A aplicação a uma coorte selecionada não estabelece desempenho em toda população ou benefício de implementar rastreio. [Zheng 2026](https://doi.org/10.1093/ehjdh/ztag025)

## O que acrescenta a análise VITAL-AF de 2026

Uma análise de 16.937 participantes com dados prévios de ECG e clínica encontrou AUROC de 0,711 para CHARGE-AF, 0,784 para ECG-AI e 0,788 para a combinação CH-AI. No decil superior da combinação, a diferença de detecção entre rastreio e controle foi 2,32 diagnósticos por 100 pessoas-ano (IC95% 0,01–4,63). [Vedage 2026](https://doi.org/10.1016/j.jacc.2026.01.087)

O estudo original randomizou serviços para rastreio com ECG de uma derivação; esta análise aplicou escores de risco ao conjunto com ECG prévio disponível. Não houve randomização de pacientes para uma conduta prospectivamente guiada pela IA. O achado sugere seleção mais eficiente, com menor cobertura populacional, e não demonstra prevenção de AVC pela estratégia.

O protocolo DEEP-AF, publicado em julho de 2026, prevê randomização de 1.230 pacientes sintomáticos para estratégia guiada por IA ou cuidado usual, com diagnóstico de FA em seis meses como desfecho primário. A publicação é de desenho, não de resultados concluídos. [DEEP-AF](https://doi.org/10.1016/j.hroo.2026.07.009)

## Limites de comparação e aplicação

A revisão de Mrak reuniu 19 estudos, predominantemente retrospectivos, com problemas de seleção, calibração pouco relatada e poucos dados prospectivos de impacto. Intervalos de AUROC entre estudos heterogêneos não formam uma estimativa combinada de desempenho. Validação externa, calibração, valor preditivo na população-alvo e efeitos da estratégia sobre desfechos e custos continuam essenciais. [Revisão de escopo](https://doi.org/10.3390/medicina62010199)

No CHARGE-AF, acrescentar variáveis eletrocardiográficas convencionais não melhorou materialmente o modelo clínico. Isso não responde à mesma pergunta de redes neurais sobre o sinal bruto. Também não prova que todo modelo de IA supere CHARGE-AF; comparação requer a mesma população, horizonte e desfecho. [CHARGE-AF](https://doi.org/10.1161/JAHA.112.000102)

Há ensaios de **outras aplicações** de IA-ECG: o estudo de Liu randomizou alertas de FA identificada no ECG e aumentou diagnóstico e prescrição de anticoagulante, sem diferença significativa em AVC ou mortalidade. Não era predição de FA oculta a partir de ritmo sinusal. Não se deve usar esse resultado como validação direta da estratégia aqui descrita. [Liu 2025](https://doi.org/10.1161/JAHA.125.042106)

Reutilizar um ECG digital pode evitar nova aquisição, mas exige formato compatível, software validado, integração e eventual monitorização confirmatória: não significa custo zero. Uma recomendação de uso amplo necessita avaliação econômica própria da estratégia e do sistema de saúde.

O escore de IA pode apoiar a escolha de quem investigar, sem substituir confirmação do ritmo e avaliação clínica. Não justifica anticoagulação isoladamente. Se houver FA ou episódios atriais documentados por dispositivo, aplicam-se os critérios específicos desse cenário, incluindo duração e risco tromboembólico. Fotopletismografia sugere irregularidade e requer confirmação; LOOP usa monitor implantável, enquanto STROKESTOP utilizou ECG intermitente, não implante.

## Tudo com Tudo
- [Fibrilação Atrial Subclínica Detectada por Dispositivo: NOAH-AFNET 6, ARTESiA e a Metanálise que os Reconcilia](/biblioteca/fibrilacao-atrial-subclinica-detectada-por-dispositivo-noah-afnet-6-artesia-e-metanalise)
- [Rastreio Populacional de Fibrilação Atrial no Idoso: LOOP e STROKESTOP](/biblioteca/rastreio-populacional-de-fibrilacao-atrial-no-idoso-loop-e-strokestop)
- [Dispositivos Vestíveis e Detecção de Fibrilação Atrial na População Geral: o Apple Heart Study](/biblioteca/dispositivos-vestiveis-e-deteccao-de-fibrilacao-atrial-na-populacao-geral-o-apple-heart-study)
- [Escore CHARGE-AF: Predição de Risco de Desenvolver Fibrilação Atrial](/biblioteca/escore-charge-af-predicao-de-risco-de-desenvolver-fibrilacao-atrial)
- [Inteligência Artificial Aplicada ao ECG na Predição de Risco Cardiovascular: a Plataforma AIRE e o Estado da Arte 2025](/biblioteca/inteligencia-artificial-aplicada-ao-ecg-na-predicao-de-risco-cardiovascular)
- [Fibrilação Atrial: Diagnóstico e Manejo (ESC 2024) — Via AF-CARE](/biblioteca/fibrilacao-atrial-diagnostico-e-manejo-esc-2024-via-af-care)
