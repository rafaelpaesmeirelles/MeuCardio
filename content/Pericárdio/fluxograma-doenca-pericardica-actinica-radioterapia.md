---
title: "Fluxograma: Doença pericárdica induzida por radioterapia — da fase aguda à constrição tardia"
slug: fluxograma-doenca-pericardica-actinica-radioterapia
theme: "Pericárdio"
kind: fluxograma
fonte_producao: chatgpt
review_status: revisado
review_note: "Construído a partir do documento em prosa já publicado e verificado nesta mesma pasta 'Doença Pericárdica Induzida por Radioterapia: da Pericardite Aguda à Constrição Tardia' — as duas fontes primárias (Quintero-Martinez JA et al., J Clin Med 2021;11(1):146, DOI 10.3390/jcm11010146, PMID 35011887, PMCID PMC8745750, texto integral já lido via PMC naquele documento; e von Kemp BA, Cosyns B, Curr Cardiol Rep 2023;25(10):1113-1121, DOI 10.1007/s11886-023-01933-3, PMID 37584875) foram reconferidas contra aquele documento nesta sessão. Nenhum limiar de dose, incidência ou intervalo de rastreamento foi alterado; os dois nós que remetem a outros fluxogramas desta pasta (pericardite aguda, derrame pericárdico, constrição) preservam a decisão de que a etiologia actínica não substitui os critérios diagnósticos já publicados para essas condições."
source_refs: ["Quintero-Martinez JA, Cordova-Madera SN, Villarraga HR. Radiation-Induced Heart Disease. Journal of Clinical Medicine. 2021;11(1):146. DOI: 10.3390/jcm11010146. PMID: 35011887. PMCID: PMC8745750 — fases clínicas, limiares de dose e recomendações de rastreamento por ecocardiograma.", "von Kemp BA, Cosyns B. Radiation-Induced Pericardial Disease: Mechanisms, Diagnosis, and Treatment. Current Cardiology Reports. 2023;25(10):1113-1121. DOI: 10.1007/s11886-023-01933-3. PMID: 37584875 — classificação em fase aguda e fase crônica/tardia."]
---

# Fluxograma: Doença pericárdica induzida por radioterapia — da fase aguda à constrição tardia

A radioterapia torácica — usada em linfoma de Hodgkin, câncer de mama
(sobretudo do lado esquerdo), câncer de pulmão e outros tumores mediastinais
— pode lesar o pericárdio em duas janelas temporais bem separadas: **dias a
meses** depois (fase aguda) ou **anos a décadas** depois (fase
crônica/tardia), muitas vezes já fora do acompanhamento oncológico ativo. O
primeiro ramo desta árvore não é uma decisão clínica diante de sintoma, mas
sim **em que momento clínico o paciente está agora** — porque é isso que
decide se a via é vigilância assintomática, tratamento de pericardite aguda,
diferencial de derrame, ou investigação de constrição tardia.

## Árvore de decisão

```mermaid
flowchart TD
  R0["Paciente com história de radioterapia<br/>torácica prévia — linfoma, câncer de<br/>mama, câncer de pulmão ou tumor<br/>mediastinal"] --> D1{"Qual o momento clínico atual?"}

  D1 -->|"Assintomático, dentro do<br/>seguimento oncológico estruturado,<br/>sem sinal cardíaco novo"| D2{"Há fator de alto risco: dose<br/>cumulativa alta, quimioterapia<br/>cardiotóxica concomitante (por<br/>exemplo antraciclina em dose alta),<br/>radioterapia do lado esquerdo, ou<br/>comorbidade cardiovascular associada?"}

  D2 -->|"Sim, alto risco"| C1(["Ecocardiograma de rastreamento a partir<br/>de 5 anos após o tratamento; considerar<br/>imagem de estresse não invasiva para<br/>rastrear doença coronariana associada"])

  D2 -->|"Não, baixo risco"| C2(["Ecocardiograma de rastreamento a partir<br/>de 10 anos após o tratamento, com<br/>repetição a cada 5 anos"])

  D1 -->|"Sintomas agudos — dor torácica<br/>pleurítica, atrito pericárdico —,<br/>dias a meses após a radioterapia"| C3(["Investigar e tratar como pericardite<br/>aguda, seguindo o fluxograma de<br/>pericardite aguda desta biblioteca — a<br/>etiologia actínica não muda a<br/>abordagem inicial"])

  D1 -->|"Derrame pericárdico assintomático,<br/>achado em exame de imagem de<br/>seguimento oncológico"| C4(["Seguir a árvore de derrame pericárdico<br/>desta biblioteca para diagnóstico<br/>diferencial e decisão de drenagem,<br/>registrando a radioterapia prévia como<br/>etiologia possível"])

  D1 -->|"Sinais insidiosos de insuficiência<br/>cardíaca direita, anos a décadas<br/>após a radioterapia"| D3{"Ecocardiograma, tomografia contrastada<br/>ou ressonância com realce tardio<br/>mostram espessamento pericárdico e<br/>critérios hemodinâmicos de constrição?"}

  D3 -->|"Sim"| C5(["Pericardite constritiva actínica<br/>confirmada: conduta pelos critérios já<br/>estabelecidos de constrição desta<br/>biblioteca — a etiologia por radiação<br/>não muda os critérios diagnósticos<br/>nem a indicação cirúrgica"])

  D3 -->|"Não confirma constrição"| C6(["Investigar diagnóstico alternativo para a<br/>insuficiência cardíaca direita — a<br/>história de radioterapia não confirma,<br/>por si só, a constrição"])

  classDef conduta fill:#eef6ef,stroke:#2f7a4f,color:#12301f;
  class C1,C2,C3,C4,C5,C6 conduta;
```

## O que a árvore não mostra

**Os números antigos assustam mais do que deveriam hoje.** Antes das
técnicas modernas de planejamento (blindagem cardíaca, fracionamento,
radioterapia conformada), a incidência de pericardite pós-radioterapia
chegava a cerca de 70% em pacientes tratados para linfoma e carcinoma. Nas
últimas décadas ela caiu para 6-30% — ainda assim, a doença pericárdica
continua sendo a complicação cardíaca **mais comum** da radioterapia
torácica, o que justifica manter o rastreamento estruturado mesmo com o
risco absoluto reduzido.

**Os limiares de dose citados são para doença cardíaca actínica em geral, não
específicos de pericárdio.** Doses cumulativas acima de 30 Gy e frações
diárias acima de 2 Gy aumentam o risco de RIHD (radiation-induced heart
disease) como categoria ampla; quimioterapia concomitante com antraciclina em
dose alta (450 mg/m²) associada a radioterapia do lado esquerdo eleva o risco
em até 10 vezes. A fonte consultada não fornece um corte de dose isolado só
para pericardite.

**Perguntar sobre radioterapia torácica prévia é o passo mais fácil de
pular.** Em paciente com derrame pericárdico de causa não imediatamente
óbvia — sobretudo se anos ou décadas se passaram desde o tratamento
oncológico — a exposição pode nem ser mencionada espontaneamente, e o próprio
paciente pode não relacionar sintomas cardíacos atuais a um tratamento
distante. Constrição de início insidioso em ex-paciente oncológico deve
levantar a hipótese actínica mesmo sem outro fator de risco clássico para
constrição, como tuberculose ou cirurgia cardíaca prévia.

**Os critérios hemodinâmicos específicos de constrição não são repetidos
aqui.** Variação respiratória de fluxo mitral/tricúspide, septal bounce e
acoplamento ventricular seguem os mesmos critérios já publicados nos
documentos desta pasta sobre pericardite efusivo-constritiva e critérios
numéricos de constrição por imagem — não há, na literatura consultada,
particularidade descrita para a constrição especificamente pós-radiação que
justifique um critério à parte (`VERIFICAÇÃO HUMANA NECESSÁRIA` quanto a essa
ausência de particularidade, que pode refletir apenas lacuna da fonte
revisada, não confirmação de equivalência total).
