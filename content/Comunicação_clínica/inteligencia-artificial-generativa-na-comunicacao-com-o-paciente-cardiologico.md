---
title: "Inteligência Artificial Generativa na Comunicação com o Paciente Cardiológico: o que a Evidência Mostra e Onde Ela Falha"
slug: inteligencia-artificial-generativa-na-comunicacao-com-o-paciente-cardiologico
theme: "Comunicação clínica"
kind: estudo
review_status: revisado
source_refs: ["Rouhi AD, Ghanem YK, Yolchieva L, Saleh Z, Joshi H, Moccia MC, Suarez-Pierre A, Han JJ. Can Artificial Intelligence Improve the Readability of Patient Education Materials on Aortic Stenosis? A Pilot Study. Cardiol Ther. 2024;13(1):137-147. DOI: 10.1007/s40119-023-00347-0. PMID: 38194058", "Singh S, Errampalli E, Errampalli N, Miran MS. Enhancing Patient Education on Cardiovascular Rehabilitation with Large Language Models. Mo Med. 2025;122(1):67-71. PMID: 39958590", "Hu M, Wang Z, Zhang Z, Li M. Challenges of patient-facing generative artificial intelligence in hypertension care: A cross-platform evaluation of the quality, readability, and actionability of LLM-Generated patient education materials. Digit Health. 2026;12:20552076261464724. DOI: 10.1177/20552076261464724. PMID: 42404600", "Stephenson-Moe CA, Behers BJ, Gibons RM, Behers BM, De Jesus Herrera L, Anneaud D, Rosario MA, Wojtas CN, Bhambrah S, Hamad KM. Assessing the quality and readability of patient education materials on chemotherapy cardiotoxicity from artificial intelligence chatbots: An observational cross-sectional study. Medicine (Baltimore). 2025;104(15):e42135. DOI: 10.1097/MD.0000000000042135. PMID: 40228277", "Salam B, Kravchenko D, Nowak S, Sprinkart AM, Weinhold L, Odenthal A, Mesropyan N, Bischoff LM, Attenberger U, Kuetting DL, Luetkens JA, Isaak A. Generative Pre-trained Transformer 4 makes cardiovascular magnetic resonance reports easy to understand. J Cardiovasc Magn Reson. 2024;26(1):101035. DOI: 10.1016/j.jocmr.2024.101035. PMID: 38460841"]
legacy_source: "Documento novo, escrito em 07/08/2026. Esta pasta já tem documentos sobre letramento em saúde, numeracia e ferramentas de decisão compartilhada, mas nenhum cobria especificamente o uso de inteligência artificial (IA) generativa/modelos de linguagem de grande porte (LLM) como ferramenta de comunicação com o paciente cardiológico — lacuna coberta aqui com cinco estudos publicados entre 2024 e 2026, todos conferidos via PubMed nesta sessão."
---

# Inteligência Artificial Generativa na Comunicação com o Paciente Cardiológico: o que a Evidência Mostra e Onde Ela Falha

## Por que este tema importa agora
Pacientes já usam plataformas de IA generativa (ChatGPT, Gemini, Copilot, entre outras) por conta própria para tentar entender diagnóstico, exame ou material educativo recebido do serviço de saúde — e médicos vêm cogitando usar essas mesmas ferramentas para gerar ou simplificar material educativo antes de entregar ao paciente. Cinco estudos publicados entre 2024 e 2026, testando esse uso especificamente em contexto cardiovascular, permitem responder com dado real, não com impressão, a duas perguntas: a IA melhora a legibilidade do material? E o conteúdo clínico permanece correto depois de reescrito?

## Estenose aórtica: o estudo piloto que testou a promessa central
Rouhi AD et al., publicado em *Cardiology and Therapy* (2024;13(1):137-147, PMID 38194058), reuniram 21 materiais educativos online sobre estenose aórtica (EA), de sociedade cirúrgica cardiotorácica profissional e instituições acadêmicas dos EUA — originalmente em nível de leitura de 10ª-12ª série (difícil) — e pediram a duas plataformas de IA generativa gratuitas (ChatGPT-3.5 e Bard) para "reescrever no nível de leitura da 5ª série", medindo o resultado por quatro índices validados de legibilidade (Flesch Reading Ease, Flesch-Kincaid, SMOG, Gunning-Fog):

- **O ChatGPT-3.5 melhorou a legibilidade nos quatro índices** (p<0,001), levando o texto para aproximadamente **6ª-7ª série**;
- **O Bard melhorou em três dos quatro índices** (p<0,001; SMOG não teve melhora significativa, p=0,729), chegando a aproximadamente **8ª-9ª série**;
- **Nenhuma das duas plataformas produziu texto no nível de 6ª série recomendado** pelas diretrizes de comunicação em saúde (American Medical Association, National Institutes of Health), mesmo tendo recebido esse comando explícito;
- O ChatGPT-3.5 teve desempenho significativamente melhor que o Bard em todas as métricas comparadas (todos p<0,001).

## Reabilitação cardíaca: o mesmo padrão, com três plataformas mais recentes
Singh S et al., publicado em *Missouri Medicine* (2025;122(1):67-71, PMID 39958590), testaram ChatGPT-3.5, Copilot e Gemini respondendo perguntas de paciente sobre reabilitação cardiovascular, avaliando a legibilidade das respostas por Gunning Fog, Flesch-Kincaid e Flesch Reading Ease:

- **Nenhum dos três modelos atingiu o nível de leitura recomendado** para material educativo nos EUA;
- **Gemini e Copilot tiveram legibilidade melhor que o ChatGPT-3.5** — inverso do achado de Rouhi et al. com Bard (versão anterior do Gemini), sugerindo que o ranking entre plataformas muda com as versões e não é estável ao longo do tempo;
- Os autores concluem que os LLM podem servir como ferramenta educativa complementar sobre reabilitação cardíaca, mas "permanece a necessidade de melhorar a legibilidade do texto para educar o paciente de forma eficaz".

## Hipertensão: comparação de seis plataformas mostra heterogeneidade grande — e uma lacuna específica
Hu M et al., publicado em *Digital Health* (2026;12:20552076261464724, PMID 42404600), compararam seis plataformas de LLM voltadas ao paciente (incluindo ChatGPT, DeepSeek-R1, Qwen3-Max-Thinking-Preview, entre outras) gerando material educativo sobre hipertensão, avaliando compreensibilidade e "acionabilidade" (PEMAT-P), qualidade da informação (EQIP-36) e legibilidade:

- **Qualidade e compreensibilidade gerais foram favoráveis**, mas com **heterogeneidade substancial entre plataformas** — a pontuação total de PEMAT-P variou de plataforma para plataforma, com Qwen3-Max-Thinking-Preview no topo (77,00) e a legibilidade **pior** (FKGL ≈14,38, nível universitário), enquanto DeepSeek-R1 teve a legibilidade mais fácil (FKGL ≈10,10) com pontuação de qualidade menor;
- **Achado clinicamente mais relevante**: a "acionabilidade" — a clareza sobre o que o paciente deve efetivamente fazer — foi sistematicamente **menor** nos domínios de "compreensão básica da doença e complicações" e "aspectos psicológicos e sociais" do que nos domínios de "cuidado diário e prevenção". Ou seja, os LLM testados são melhores dizendo *o que fazer no dia a dia* do que ajudando o paciente a entender *a doença em si* ou a lidar com o impacto psicológico dela — padrão relevante para quem for usar essas ferramentas como apoio, não substituto, da consulta.

## Cardiotoxicidade por quimioterapia: qualidade alta, legibilidade baixa — e nenhum consenso sobre qual chatbot é melhor
Stephenson-Moe CA et al., publicado em *Medicine* (2025;104(15):e42135, PMID 40228277), testaram ChatGPT, Microsoft Copilot, Google Gemini e Meta AI respondendo 10 perguntas sobre cardiotoxicidade induzida por quimioterapia, avaliando legibilidade (7 índices) e qualidade (PEMAT modificado, DISCERN):

- **Nível médio de leitura de 13,7ª série** (equivalente a ensino superior) entre os quatro chatbots — bem acima do recomendado para material ao público geral;
- **Qualidade da informação foi alta** (DISCERN médio 4,2 em escala de 1 a 5; compreensibilidade 91,7%);
- **Acionabilidade foi mais baixa e mais variável** (mediana 75%, com Meta AI caindo a 50%);
- Os autores concluem que os chatbots produzem material de **alta qualidade, mas baixa legibilidade** — e que não há consenso, entre os quatro testados, sobre qual produz o melhor material, reforçando que a escolha da plataforma por si só não resolve o problema de legibilidade.

## O outro lado da moeda: simplificar o que já existe, com verificação por especialista
Salam B et al., publicado no *Journal of Cardiovascular Magnetic Resonance* (2024;26(1):101035, PMID 38460841), testaram uma aplicação diferente: usar GPT-4 para **traduzir laudos técnicos de ressonância magnética cardiovascular (RMC) já prontos** para linguagem compreensível ao leigo, em vez de gerar material educativo do zero. Dois radiologistas cardiovasculares avaliaram cada versão simplificada quanto a corretude factual, completude e potencial de dano, e 13 leigos avaliaram a compreensibilidade:

- **Laudos gerados pelo GPT-4 tiveram Automated Readability Index muito menor** (mediana 5 [4-6] vs. 10 [9-12] do laudo original; p<0,001) e foram **subjetivamente muito mais fáceis de entender** para os leigos (mediana 4 [4-5] em escala de 1-5, vs. 1 [1] do original; p<0,001);
- Apenas **2/60 (3%) dos laudos gerados pelo GPT-4** ficaram no nível de 8ª série ou acima, contra **18/20 (90%) dos laudos originais**;
- **Correção factual foi avaliada como "forte concordância" em 94% (113/120) das avaliações**, e completude dos achados relevantes em 81% (97/120) — ou seja, a simplificação manteve a informação clinicamente correta na grande maioria dos casos, mas não em 100% deles;
- Tempo médio de geração: 52±13 segundos por laudo.

## Síntese prática
Lidos em conjunto, os cinco estudos sustentam três conclusões que mudam como usar essas ferramentas na prática:

1. **A IA generativa melhora a legibilidade de forma mensurável, mas raramente chega ao nível de 6ª série recomendado** para material de saúde ao público geral — em nenhum dos cinco estudos (estenose aórtica, reabilitação cardíaca, hipertensão, cardiotoxicidade por quimioterapia) a saída, sem edição humana adicional, atingiu de forma consistente o padrão recomendado.
2. **Não existe uma plataforma "vencedora" estável** — o ranking entre ChatGPT, Bard/Gemini, Copilot, DeepSeek e outras mudou de estudo para estudo, e as próprias versões testadas já estão em grande parte descontinuadas ou substituídas, o que limita a validade de qualquer recomendação de plataforma específica no tempo.
3. **A aplicação mais promissora, com verificação mais forte, é simplificar informação já existente e verificada** (como o laudo de RMC do estudo de Salam et al., com corretude checada por radiologista) — em vez de gerar material educativo novo do zero, que carrega mais risco de conteúdo impreciso não verificado por profissional. Em ambos os usos, a literatura reunida aqui converge no mesmo ponto: IA generativa é ferramenta de rascunho a ser revisada por profissional de saúde antes de chegar ao paciente, não substituto do controle de qualidade humano.
