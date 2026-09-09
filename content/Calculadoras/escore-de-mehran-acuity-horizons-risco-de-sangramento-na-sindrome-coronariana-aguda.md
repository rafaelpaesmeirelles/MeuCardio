---
title: 'Escore de Mehran (ACUITY/HORIZONS-AMI): derivação e limites da estimativa de sangramento na SCA'
slug: escore-de-mehran-acuity-horizons-risco-de-sangramento-na-sindrome-coronariana-aguda
theme: Calculadoras
kind: documento
review_status: revisado
source_refs:
- 'Mehran R, Pocock SJ, Nikolsky E, Clayton T, Dangas GD, Kirtane AJ, Parise H, Fahy M, Manoukian SV, Feit F, Ohman ME, Witzenbichler
  B, Guagliumi G, Lansky AJ, Stone GW. A risk score to predict bleeding in patients with acute coronary syndromes. J Am Coll
  Cardiol. 2010;55(23):2556-2566. DOI: 10.1016/j.jacc.2009.09.076. PMID: 20513595 — artigo de derivação, coorte, preditores,
  c-estatístico e associação com mortalidade conferidos nesta sessão via PubMed E-utilities (esearch por autor ''Mehran R''
  + termos ''bleeding percutaneous coronary intervention risk score'', depois efetch em XML/texto puro do registro, PMID confirmado
  diretamente).'
- 'Taha S, D''Ascenzo F, Moretti C, Omedè P, Montefusco A, Bach RG, Alexander KP, Mehran R, Ariza-Solé A, Zoccai GB, Gaita
  F. Accuracy of bleeding scores for patients presenting with myocardial infarction: a meta-analysis of 9 studies and 13,759
  patients. Postepy Kardiol Interwencyjnej. 2015;11(3):182-190. DOI: 10.5114/pwki.2015.54011. PMID: 26677357. PMCID: PMC4631731
  — usado apenas como validação externa agregada (AUC do escore ACUITY/Mehran fora da coorte de derivação), abstract conferido
  nesta sessão via PubMed E-utilities.'
legacy_source: Documento original preservado no histórico e em tmp/agent071-extra-sources/original-0.md. Convertido de calculadora
  para síntese descritiva na revisão de 09/09/2026, mantendo a pergunta de derivação/validação do modelo.
summary: Síntese descritiva da derivação e validação do escore de sangramento ACUITY/HORIZONS-AMI. Não contém tabela operacional
  de pontos nem realiza cálculo individual.
review_note: 'PMID20513595 e PMC4631731 verificados online. Conforme escopo autorizado, convertido de calculadora em documento
  descritivo: removida tabela de pontos não conferida, recomendação de cálculo e incidência incoerente do próprio abstract
  (744/17.421 não corresponde a7,3%). Preservados coorte, preditores, c-estatístico e AUCs, com limites de comparação e de
  aplicação contemporânea.'
tags: []
source_tier: A
gaps: []
published: true
---

# Escore de Mehran (ACUITY/HORIZONS-AMI): derivação e limites

## A pergunta do estudo

O estudo de Mehran e colaboradores, publicado no JACC em 2010, desenvolveu um modelo de **sangramento maior não relacionado à cirurgia de revascularização nos primeiros 30 dias** em pacientes com síndrome coronariana aguda. Utilizou os ensaios ACUITY e HORIZONS-AMI, reunindo **17.421 participantes** com diferentes apresentações de SCA. Esta é uma síntese descritiva da evidência, sem tabela operacional de pontos ou cálculo individual. [Artigo de derivação](https://pubmed.ncbi.nlm.nih.gov/20513595/).

## Variáveis e desempenho

O modelo de regressão logística identificou seis preditores basais: sexo feminino, idade, creatinina sérica, leucócitos, anemia e apresentação clínica (infarto com ou sem supra de ST versus SCA sem biomarcadores elevados). Acrescentou o regime antitrombótico: heparina associada a inibidor da glicoproteína IIb/IIIa versus bivalirudina isolada.

A discriminação relatada foi **c=0,74**. O gradiente de risco estimado pelo modelo estendeu-se de aproximadamente 1% a mais de 40%, sem que isso estabeleça calibração atual em qualquer população. A análise ajustada também associou sangramento maior a risco de morte cerca de 3,2 vezes maior; essa associação prognóstica não prova que modificar um componente do escore, por si, reduza mortalidade.

## Validação externa e comparação com outros escores

A metanálise de Taha e colaboradores reuniu **nove estudos e 13.759 pacientes**. Para ACUITY, encontrou AUC **0,71 (IC 0,63–0,77)**; CRUSADE **0,71 (0,64–0,80)**, ACTION **0,75 (0,72–0,79)** e GRACE **0,66 (0,64–0,67)**. São estimativas agregadas de coortes e definições de sangramento heterogêneas: diferenças numéricas entre AUC não demonstram superioridade clínica direta de um escore. A revisão relatou desempenho semelhante entre escores em STEMI e particularidades de validação em NSTEMI e segundo acesso vascular. [Metanálise completa](https://pmc.ncbi.nlm.nih.gov/articles/PMC4631731/).

## Como interpretar no contexto clínico

- O modelo responde a uma pergunta de **risco hemorrágico agudo na SCA**, diferente de HAS-BLED/ORBIT na anticoagulação crônica de fibrilação atrial e de PARIS no seguimento após implante de stent.
- A variável de tratamento reflete estratégias dos ensaios de origem. Sua presença não recomenda uso rotineiro de inibidores de GP IIb/IIIa, não define automaticamente escolha de anticoagulante e não substitui avaliação de risco isquêmico.
- Mudanças de acesso vascular, antiagregação e manejo contemporâneo podem alterar o risco absoluto e a calibração. AUC mede discriminação; não garante precisão da probabilidade individual nem benefício de decisões orientadas pelo escore.
- Esta síntese não fornece coeficientes, pontos ou conversão de pontuação em risco. Não deve ser usada para calcular manualmente uma probabilidade individual.

## Tudo com Tudo

- [CRUSADE Bleeding Score](/biblioteca/crusade-bleeding-score)
- [HAS-BLED](/biblioteca/has-bled)
- [Escore ORBIT: Risco de Sangramento em Fibrilação Atrial Anticoagulada](/biblioteca/escore-orbit-risco-de-sangramento-em-fibrilacao-atrial-anticoagulada)
- [Escores ATRIA: Risco de AVC e de Sangramento na Fibrilação Atrial](/biblioteca/escores-atria-risco-de-avc-e-de-sangramento-na-fibrilacao-atrial)
- [Escore PARIS: Risco de Trombose e de Sangramento Após Stent](/biblioteca/escore-paris-risco-de-trombose-e-de-sangramento-apos-stent)
- [DAPT Score e PRECISE-DAPT: Duração da Dupla Antiagregação Após Stent](/biblioteca/dapt-score-e-precise-dapt-duracao-da-dupla-antiagregacao-apos-stent)
- [ACUITY: Bivalirudina na SCA Invasiva](/biblioteca/acuity-bivalirudina-na-sca-invasiva)
