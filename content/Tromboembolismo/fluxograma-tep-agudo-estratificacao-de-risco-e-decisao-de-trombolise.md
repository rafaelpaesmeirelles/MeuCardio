---
title: "Fluxograma: TEP agudo — estratificação de risco e decisão de trombólise"
slug: fluxograma-tep-agudo-estratificacao-de-risco-e-decisao-de-trombolise
theme: "Tromboembolismo"
kind: fluxograma
fonte_producao: chatgpt
summary: "Depois do diagnóstico confirmado de TEP agudo, a árvore de risco combina instabilidade hemodinâmica, PESI/sPESI, disfunção de ventrículo direito e biomarcadores para separar quem precisa de reperfusão imediata, quem pode ser tratado ambulatorialmente e as duas faixas intermediárias que decidem se há terapia de reperfusão de resgate."
review_status: revisado
review_note: "PMIDs conferidos individualmente no PubMed via E-utilities (esummary) nesta sessão: 31504429 (ESC 2019 diretriz de TEP agudo, Konstantinides SV, Eur Heart J 41(4):543-603), 16020800 (PESI original, Aujesky D, Am J Respir Crit Care Med 172(8):1041-1046), 20696966 (sPESI, Jiménez D, Arch Intern Med 170(15):1383-1389) e 24716681 (PEITHO, Meyer G, NEJM 370(15):1402-1411). Título, revista, volume/página e autor conferidos contra o registro oficial antes de citar. Este fluxograma cobre estratificação e decisão terapêutica; o fluxograma já publicado do tema (fluxograma-tromboembolismo-pulmonar-diagnostico-esc-2019) cobre a etapa diagnóstica anterior, sem sobreposição de escopo."
source_refs: ["2019 ESC Guidelines for the diagnosis and management of acute pulmonary embolism developed in collaboration with the European Respiratory Society (ERS) · European Heart Journal · 2020 · 41(4):543-603 · https://pubmed.ncbi.nlm.nih.gov/31504429/", "Derivation and validation of a prognostic model for pulmonary embolism (PESI) · American Journal of Respiratory and Critical Care Medicine · 2005 · 172(8):1041-1046 · https://pubmed.ncbi.nlm.nih.gov/16020800/", "Simplification of the pulmonary embolism severity index for prognostication in patients with acute symptomatic pulmonary embolism (sPESI) · Archives of Internal Medicine · 2010 · 170(15):1383-1389 · https://pubmed.ncbi.nlm.nih.gov/20696966/", "Fibrinolysis for patients with intermediate-risk pulmonary embolism (PEITHO) · New England Journal of Medicine · 2014 · 370(15):1402-1411 · https://pubmed.ncbi.nlm.nih.gov/24716681/"]
---

# Fluxograma: TEP agudo — estratificação de risco e decisão de trombólise

Confirmado o diagnóstico de TEP agudo, a pergunta muda de "é TEP?" para "qual
o risco de morte precoce, e isso muda a conduta agora?". A diretriz ESC 2019
organiza essa resposta em quatro categorias, combinando instabilidade
hemodinâmica, o escore clínico PESI (ou sua versão simplificada, sPESI),
disfunção de ventrículo direito por imagem e biomarcador de lesão miocárdica
elevado. A trombólise sistêmica de rotina só está indicada no risco alto — no
risco intermediário-alto, ela entra como opção de resgate diante de
deterioração, não como conduta inicial.

## Árvore de decisão

```mermaid
flowchart TD
  R0["TEP agudo confirmado"] --> D1{"Instabilidade hemodinâmica<br/>(choque, parada cardíaca ou<br/>hipotensão persistente)?"}

  D1 -->|"Sim"| C1(["TEP de alto risco: reperfusão<br/>imediata — trombólise sistêmica, ou<br/>embolectomia/tratamento dirigido por<br/>cateter se houver contraindicação"])

  D1 -->|"Não"| D2{"PESI classe III a V,<br/>ou sPESI ≥ 1?"}

  D2 -->|"Não — PESI I-II<br/>ou sPESI 0"| C2(["TEP de baixo risco: considerar<br/>tratamento ambulatorial ou<br/>alta hospitalar precoce"])

  D2 -->|"Sim"| D3{"Disfunção de ventrículo direito<br/>(eco ou angioTC) E biomarcador<br/>de lesão miocárdica elevado<br/>(troponina/BNP), os dois presentes?"}

  D3 -->|"Não — apenas um<br/>positivo, ou nenhum"| C3(["TEP de risco intermediário-baixo:<br/>anticoagulação e monitorização<br/>hospitalar"])

  D3 -->|"Sim, os dois positivos"| D4{"Sinais clínicos de deterioração<br/>hemodinâmica iminente (taquicardia<br/>progressiva, hipotensão limítrofe,<br/>piora do lactato/perfusão)?"}

  D4 -->|"Sim"| C4(["TEP de risco intermediário-alto com<br/>deterioração: considerar reperfusão<br/>(trombólise ou tratamento dirigido<br/>por cateter) como terapia de resgate,<br/>monitorização em unidade intensiva"])

  D4 -->|"Não"| C5(["TEP de risco intermediário-alto<br/>estável: anticoagulação em unidade<br/>de monitorização, vigilância ativa<br/>para deterioração, reperfusão de<br/>resgate se piora"])

  classDef conduta fill:#eef6ef,stroke:#2f7a4f,color:#12301f;
  class C1,C2,C3,C4,C5 conduta;
```

## O que a árvore não mostra

**O PEITHO mostrou por que a trombólise não é rotina no risco
intermediário-alto.** No braço trombolítico houve redução de descompensação
hemodinâmica, mas às custas de aumento de sangramento maior (6,3% versus 1,2%)
e de acidente vascular cerebral hemorrágico (2,0% versus 0,2%) em relação a
placebo mais anticoagulação — é esse equilíbrio que faz a diretriz reservar a
reperfusão para deterioração, não para todo paciente de risco
intermediário-alto.

**PESI e sPESI são escores de mortalidade em 30 dias, não medem diretamente
disfunção de VD.** Um paciente pode ter sPESI 0 e ainda assim ter achado
incidental de disfunção de VD — a diretriz recomenda a avaliação de imagem e
biomarcador apenas quando o escore já indicou risco não baixo, exatamente a
sequência que a árvore segue.

**A escolha entre trombólise sistêmica em dose plena, dose reduzida ou terapia
dirigida por cateter dentro do ramo de resgate** depende de risco de
sangramento individual, disponibilidade de sala de hemodinâmica e experiência
do centro — não é uma hierarquia fixa, e por isso a árvore agrupa essas opções
sob "considerar reperfusão" em vez de ramificá-las.

**Filtro de veia cava inferior** não aparece como ramo desta árvore por ser
reservado a contraindicação absoluta de anticoagulação, cenário à parte da
decisão de reperfusão que esta árvore resolve.
