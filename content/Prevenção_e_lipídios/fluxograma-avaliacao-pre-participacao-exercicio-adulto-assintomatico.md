---
title: "Fluxograma: Avaliação pré-participação de exercício no adulto assintomático (não atleta)"
slug: fluxograma-avaliacao-pre-participacao-exercicio-adulto-assintomatico
theme: "Prevenção e lipídios"
kind: fluxograma
summary: "Quem, no adulto que vai começar ou progredir exercício e não é atleta competitivo, precisa de liberação médica antes de treinar: algoritmo ACSM 2015 (atividade atual, sintomas ou doença CV/metabólica/renal conhecida, intensidade pretendida), com o recorte brasileiro da SBC 2019 e a saída explícita para reabilitação e para cardiologia do esporte."
fonte_producao: grok
review_status: revisado
review_note: "Produção científica assistida (Grok) em 29/08/2026. Algoritmo ACSM extraído de Riebe et al. 2015 (PMID 26473759) e da descrição operacional do algoritmo (definição de exercício regular, ramos por doença conhecida e sintomas). Não é triagem pré-participação de atleta. Revisão científica concluída em 30/08/2026."
source_refs:
  - "Riebe D, Franklin BA, Thompson PD, Garber CE, Magal M, et al. Updating ACSM's Recommendations for Exercise Preparticipation Health Screening. Med Sci Sports Exerc. 2015;47(8):2473-2479. DOI: 10.1249/MSS.0000000000000664. PMID: 26473759. Errata: Med Sci Sports Exerc. 2016;48(3):579. Os três eixos do algoritmo (atividade atual, sintomas ou doença CV/metabólica/renal, intensidade desejada) estão no abstract; os ramos operacionais e a definição de exercício regular (30 min, ≥3 dias/semana, 3 meses, intensidade moderada) foram lidos em fontes secundárias que reproduzem a figura do artigo, não na figura original em alta resolução nesta revisão editorial."
  - "Whitfield GP, Riebe D, Magal M, Liguori G. Applying the ACSM Preparticipation Screening Algorithm to U.S. adults: NHANES 2001–04. Med Sci Sports Exerc. 2017;49(10):2056-2063. PMID: 28557860. PMCID: PMC7059860. Confirma os ramos: sedentário assintomático sem doença conhecida inicia leve-moderado sem liberação; sedentário com doença conhecida ou com sintomas pede liberação antes de qualquer intensidade."
  - "Précoma DB, Oliveira GMM, Simão AF, et al. Atualização da Diretriz de Prevenção Cardiovascular da Sociedade Brasileira de Cardiologia – 2019. Arq Bras Cardiol. 2019;113(4):787-891. DOI: 10.5935/abc.20190204. PMID: 31691761. Capítulo 8: avaliação inicial com anamnese, exame físico e ECG; teste ergométrico ou TCPE individualizado."
  - "Arnett DK, Blumenthal RS, Albert MA, et al. 2019 ACC/AHA Guideline on the Primary Prevention of Cardiovascular Disease. Circulation. 2019;140(11):e596-e646. DOI: 10.1161/CIR.0000000000000678. PMID: 30879355. Aconselhamento de rotina para estilo de vida ativo (I B-R) — a triagem não deve virar barreira desse aconselhamento."
  - "Visseren FLJ, Mach F, Smulders YM, et al. 2021 ESC Guidelines on cardiovascular disease prevention in clinical practice. Eur Heart J. 2021;42(34):3227-3337. DOI: 10.1093/eurheartj/ehab484. PMID: 34458905. A seção 4.3.1.1 remete o rastreio pré-participação a diretrizes ESC prévias e pede aumento gradual no sedentário."
  - "Documento irmão: prescricao-de-exercicio-em-prevencao-primaria-cardiovascular.md. Não usar triagem-cardiovascular-pre-participacao-ecg-atleta-aha-acc-2025 nem morte-subita-em-atletas-triagem-pre-participacao."
---

# Fluxograma: Avaliação pré-participação de exercício no adulto assintomático (não atleta)

A pergunta deste fluxograma é estreita: **este adulto, que não é atleta competitivo, precisa de liberação médica antes de começar ou de subir a intensidade do exercício?** Não é a pergunta da triagem pré-participação esportiva com ECG, nem a da indicação de reabilitação cardíaca.

O algoritmo que organiza os ramos é o da ACSM 2015 (Riebe et al., PMID 26473759). Ele abandonou a contagem de fatores de risco como critério de encaminhamento — a prevalência de fatores é alta e o evento relacionado ao exercício é raro, então o modelo antigo gerava encaminhamento excessivo e virava barreira. Ficaram três eixos: (1) a pessoa já treina com regularidade; (2) há sintomas sugestivos ou doença cardiovascular, metabólica ou renal conhecida; (3) a intensidade pretendida.

Diabetes tipo 1 ou 2 e doença renal entram no eixo de "doença conhecida" mesmo em prevenção primária de evento aterosclerótico. Doença pulmonar isolada **saiu** da lista que dispara encaminhamento automático: o risco de evento cardiovascular no exercício, nesse grupo, foi atribuído ao sedentarismo, não à pneumopatia em si.

## Árvore de decisão

```mermaid
flowchart TD
  R0["Adulto que quer iniciar ou progredir exercício,<br/>sem ser atleta competitivo"] --> D0{"Há doença aterosclerótica<br/>estabelecida, revascularização,<br/>IC, ou evento prévio?"}

  D0 -->|"Sim"| C0(["Isto não é prevenção primária:<br/>avaliar reabilitação cardíaca<br/>e a prescrição de prevenção secundária"])

  D0 -->|"Não"| D00{"A demanda é esporte competitivo,<br/>atleta master de alto volume,<br/>ou retorno ao esporte após diagnóstico?"}

  D00 -->|"Sim"| C00(["Não usar este fluxograma:<br/>triagem e elegibilidade ficam<br/>na Cardiologia do Esporte"])

  D00 -->|"Não"| D1{"Há sintoma sugestivo de doença<br/>cardiovascular, metabólica ou renal?<br/>Dor torácica, dispneia em repouso ou<br/>esforço leve, síncope ou tontura,<br/>ortopneia ou DPEN, edema de tornozelo,<br/>palpitação, claudicação, sopro conhecido,<br/>fadiga ou dispneia desproporcional"}

  D1 -->|"Sim"| C1(["Não iniciar ou interromper o exercício.<br/>Liberação médica antes de qualquer<br/>intensidade — este paciente deixou<br/>de ser o 'assintomático' do título"])

  D1 -->|"Não"| D2{"Já pratica exercício regular?<br/>Últimos 3 meses, ≥30 min,<br/>≥3 dias/semana, intensidade moderada<br/>(40–60% da reserva de FC ou<br/>64–76% da FC máxima) — ACSM 2015"}

  D2 -->|"Não: sedentário ou irregular"| D3{"Doença cardiovascular, metabólica<br/>ou renal conhecida?<br/>Inclui diabetes tipo 1 ou 2 e DRC.<br/>Não inclui pneumopatia isolada"}

  D3 -->|"Não"| C2(["Iniciar leve a moderado SEM liberação<br/>médica adicional. Progredir aos poucos.<br/>Não pular direto para vigoroso"])

  D3 -->|"Sim"| C3(["Liberação médica ANTES de qualquer<br/>intensidade. Depois de liberado,<br/>começar leve a moderado e progredir"])

  D2 -->|"Sim: já treina"| D4{"Doença cardiovascular, metabólica<br/>ou renal conhecida?"}

  D4 -->|"Não"| C4(["Continuar moderado ou vigoroso<br/>sem liberação. Progredir pelas<br/>regras habituais de progressão"])

  D4 -->|"Sim, e segue assintomático"| D5{"Intensidade pretendida"}

  D5 -->|"Manter moderada"| C5(["Pode continuar moderado sem nova<br/>liberação, se não houve mudança<br/>de sintomas ou de estado de saúde"])

  D5 -->|"Passar para vigorosa"| C6(["Liberação médica recomendada<br/>antes de vigoroso — se já houve<br/>liberação recente sem mudança de<br/>sintomas, não repetir por rotina"])

  classDef conduta fill:#eef6ef,stroke:#2f7a4f,color:#12301f;
  class C0,C00,C1,C2,C3,C4,C5,C6 conduta;
```

## Como usar a árvore sem transformá-la em barreira

A ACC/AHA 2019 pede aconselhamento de rotina para um estilo de vida ativo (Classe I, B-R). O algoritmo ACSM existe para **não** mandar todo sedentário hipertenso ao teste ergométrico antes de caminhar. Whitfield et al. (2017), aplicando o algoritmo ao NHANES, mostraram o ponto: no sedentário assintomático **sem** as doenças especificadas, a conduta é começar leve a moderado sem liberação; no sedentário **com** doença conhecida, a liberação vem antes de qualquer intensidade.

"Liberação médica" neste fluxograma é avaliação clínica dirigida — história, exame, decisão sobre ECG ou teste funcional — não um carimbo e não um laudo de atleta. A SBC 2019, capítulo 8, descreve a avaliação inicial como **anamnese, exame físico e ECG**, e reserva teste ergométrico ou TCPE máximo para indicação **individualizada**, junto com antropometria, força e flexibilidade. Na consulta de prevenção primária brasileira isso já está acontecendo: o cardiologista que prescreve exercício já fez história e exame. O ECG de consultório não é o programa de Pádua. O teste de esforço não é pedágio da caminhada.

Depois da liberação, a ESC 2021 pede aumento **gradual** no sedentário. Intensidade moderada, na Tabela 4 da ACC/AHA 2019, é 3,0–5,9 METs (caminhada rápida, ciclismo leve, natação recreativa). Vigoroso é ≥6 METs. A prescrição do que fazer depois de passar pela árvore está no documento irmão.

## O que a árvore não é

**Não é triagem de atleta.** História direcionada a síncope de esforço, ECG com critérios de atleta, eco, Holter, decisão de elegibilidade — outra pasta, outros documentos. Quem caiu no ramo C00 deve sair daqui.

**Não é indicação de reabilitação cardíaca.** Doença estabelecida cai no ramo C0. Exercício e reabilitação na ESC 2024 de síndromes coronarianas crônicas (PMID 39210710) pertencem àquele documento, não a este.

**Não reintroduz contagem de fatores de risco como critério de encaminhamento.** Hipertensão, dislipidemia, idade, tabagismo e história familiar **não** disparam, sozinhos, o pedido de liberação no algoritmo ACSM 2015. Foi exatamente isso que a atualização removeu. Diabetes e DRC disparam porque estão na lista de doença metabólica/renal conhecida, não porque "somam pontos".

**Não autoriza ignorar sintoma novo em quem já treina.** O ramo do sintoma (C1) vale para o sedentário e para quem já corre: interromper, avaliar, só então retomar.

## Lista operacional de sintomas (ACSM)

A lista que o algoritmo trata como "sinais ou sintomas sugestivos" — e que tira o paciente do título "assintomático" — é:

- Dor ou desconforto (ou equivalente anginoso) em tórax, pescoço, mandíbula, braços ou outra área que possa ser isquemia
- Dispneia em repouso ou aos pequenos esforços
- Tontura ou síncope
- Ortopneia ou dispneia paroxística noturna
- Edema de tornozelo
- Palpitações ou taquicardia
- Claudicação intermitente
- Sopro conhecido
- Fadiga ou dispneia desproporcional às atividades habituais

Um único item positivo encerra o ramo "assintomático" e manda para avaliação, **independentemente** de a pessoa já treinar.

## Definição de "já treina"

Não é "caminha até o mercado". A ACSM 2015 classifica como exercício regular quem, **nos últimos 3 meses**, faz pelo menos **30 minutos**, em **3 ou mais dias por semana**, em intensidade **moderada** (40–60% da reserva de frequência cardíaca ou 64–76% da FC máxima). Quem está abaixo disso entra pelo ramo do sedentário — inclusive o paciente que "às vezes sobe escada" e se acha ativo.

## Depois da árvore

Quem caiu em C2 (sedentário assintomático sem doença conhecida) recebe a prescrição de prevenção primária e começa **leve a moderado**, com progressão. Quem caiu em C3 só recebe essa prescrição **depois** da avaliação. Quem caiu em C4 segue e pode progredir. O conteúdo da prescrição — 150–300 minutos de moderado ou 75–150 de vigoroso, resistido em 2 ou mais dias, reduzir tempo sedentário — está em `prescricao-de-exercicio-em-prevencao-primaria-cardiovascular.md`. Passos por dia e "guerreiro de fim de semana" são documentos de volume, não de triagem.

## Limitações e o que confirmar

- Os **três eixos** do algoritmo ACSM 2015 estão no abstract de Riebe et al., PMID 26473759 (atividade atual; sintomas e/ou doença CV, metabólica ou renal; intensidade desejada). A **figura original** do artigo não foi aberta em alta resolução nesta revisão editorial; os ramos operacionais reproduzidos no diagrama vêm dessa tríade mais a descrição padrão do algoritmo (incluindo Whitfield 2017, PMC7059860). Conferir a figura e a errata de 2016 (Med Sci Sports Exerc. 2016;48(3):579) antes de transformar o diagrama em protocolo institucional.
- A definição de exercício regular (30 min, 3 dias, 3 meses, moderado) é a do algoritmo ACSM reproduzida nas fontes secundárias lidas; está alinhada ao abstract, mas o número "30 minutos / 3 dias / 3 meses" deve ser conferido na figura/texto integral.
- "Liberação nos últimos 12 meses" para quem já treina, tem doença conhecida e quer vigoroso aparece em material didático ACSM; **LIMITE DA EVIDÊNCIA DISPONÍVEL** se esse prazo de 12 meses está no artigo de 2015 ou só em edições posteriores das Guidelines for Exercise Testing and Prescription.
- Pneumopatia fora da lista de encaminhamento automático: descrito nas fontes que reproduzem a justificativa do roundtable 2015; conferir no texto integral.
- A SBC 2019 é mais "ECG na avaliação inicial" do que a ACSM; as duas não se contradizem se o ECG não virar barreira para começar atividade leve a moderada no assintomático de baixo risco.
- Este fluxograma não decide sobre estatina, aspirina, escore de cálcio ou SCORE2/PREVENT — só sobre exercício.

## Tudo com Tudo

- [Prescrição de Exercício em Prevenção Primária Cardiovascular](/biblioteca/prescricao-de-exercicio-em-prevencao-primaria-cardiovascular)
- [Reabilitação Cardíaca e Prescrição de Exercício na Prevenção Secundária](/biblioteca/reabilitacao-cardiaca-e-prescricao-de-exercicio-na-prevencao-secundaria)
- [Passos por Dia e Mortalidade: o que Substitui a Meta dos 10 Mil](/biblioteca/passos-por-dia-e-mortalidade-o-que-substitui-a-meta-dos-10-mil)
- [Tempo Sentado e Atividade Física: a Dose que Anula o Risco](/biblioteca/tempo-sentado-e-atividade-fisica-a-dose-que-anula-o-risco)
- [Atividade Física Concentrada no Fim de Semana e Risco Cardiovascular](/biblioteca/atividade-fisica-concentrada-no-fim-de-semana-e-risco-cardiovascular)
- [Fadiga e Intolerância ao Esforço: Abordagem Cardiovascular Orientada à Decisão](/biblioteca/fadiga-e-intolerancia-ao-esforco-abordagem-cardiovascular-orientada-a-decisao)
- [Fluxograma: Fadiga e intolerância ao esforço — próximo passo](/biblioteca/fluxograma-fadiga-e-intolerancia-ao-esforco-proximo-passo)
