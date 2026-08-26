---
title: "Fluxograma: Investigação genética na cardiomiopatia com história familiar de morte súbita — EHRA/HRS/APHRS/LAHRS 2022"
slug: fluxograma-investigacao-genetica-cardiomiopatia-historia-familiar-morte-subita
theme: "Cardiomiopatias"
kind: fluxograma
fonte_producao: chatgpt
review_status: revisado
review_note: "Baseado no EHRA/HRS/APHRS/LAHRS Expert Consensus Statement on the State of Genetic Testing for Cardiac Diseases (Wilde AAM et al., co-publicado em Europace 2022;24(8):1307-1367, DOI 10.1093/europace/euac030, PMID 35373836 — texto integral aberto e conferido nesta sessão via WebFetch direto no PMC9435643, https://pmc.ncbi.nlm.nih.gov/articles/PMC9435643/; e em Heart Rhythm 2022;19(7):e1-e60, DOI 10.1016/j.hrthm.2022.03.1225, PMID 35390533, mesmo conteúdo, verificado por esummary do PubMed E-utilities quanto a título/periódico/data/DOI). Cada nó da árvore foi conferido literalmente contra trecho citado do texto integral: a indicação de teste genético no caso índice de alta probabilidade diagnóstica ('Molecular genetic testing should be offered to all index patients with a high probability diagnosis' — recomendação forte, símbolo de coração verde 'should do this' — replicada para CMH, CMD e cardiomiopatia arritmogênica/Task Force Criteria); a proibição de testar genes de evidência limitada/disputada/refutada em fenótipo fraco ('should not be performed in patients with a weak (non-definite) phenotype' — coração vermelho, 'do not do this'); o aconselhamento genético como pré-requisito obrigatório ('performed only with appropriate genetic counselling'); o teste em cascata dirigido à variante específica nos parentes de primeiro grau após identificação de variante P/LP ('Variant-specific genetic testing is recommended for family members... following the identification of the disease-causing variant'); a liberação da vigilância do parente não portador ('released from further clinical surveillance in the vast majority of conditions') contra a vigilância clínica periódica do parente portador; a regra central de VUS ('A VUS that has not been upgraded to LP should not be used to facilitate cascade screening; rather, clinical screening is required'); e a exigência de rastreamento clínico periódico dos parentes quando o teste do caso índice é negativo ou não realizado, pela heterogeneidade fenotípica de idade de início e progressão dentro da mesma família. Nenhum limiar numérico, protocolo de imagem por fenótipo ou lista de genes foi extraído desta fonte para esta árvore — são tratados nos documentos já publicados desta mesma pasta (diagnóstico genético e risco de morte súbita da CMD, e CMH ESC 2023), e por isso não foram redesenhados aqui para não duplicar árvore já existente nem citar limiar de outra fonte sem reconferi-lo nesta sessão."
source_refs: ["Wilde AAM, Semsarian C, Márquez MF, et al. European Heart Rhythm Association (EHRA)/Heart Rhythm Society (HRS)/Asia Pacific Heart Rhythm Society (APHRS)/Latin American Heart Rhythm Society (LAHRS) Expert Consensus Statement on the State of Genetic Testing for Cardiac Diseases. Europace. 2022;24(8):1307-1367. DOI 10.1093/europace/euac030. PMID 35373836.", "Wilde AAM, Semsarian C, Márquez MF, et al. European Heart Rhythm Association (EHRA)/Heart Rhythm Society (HRS)/Asia Pacific Heart Rhythm Society (APHRS)/Latin American Heart Rhythm Society (LAHRS) Expert Consensus Statement on the State of Genetic Testing for Cardiac Diseases. Heart Rhythm. 2022;19(7):e1-e60. DOI 10.1016/j.hrthm.2022.03.1225. PMID 35390533."]
---

# Fluxograma: Investigação genética na cardiomiopatia com história familiar de morte súbita

O consenso de especialistas EHRA/HRS/APHRS/LAHRS de 2022 organiza a decisão de
testar geneticamente uma cardiomiopatia em duas perguntas que costumam ser
tratadas como uma só, e não são: **quem deve ser testado no caso índice**, e
**o que fazer com cada parente de primeiro grau depois do resultado**. A
segunda pergunta tem três respostas diferentes — variante patogênica
identificada, variante de significado incerto (VUS) e teste negativo —, e
confundir a VUS com um resultado negativo é o erro mais comum descrito pelo
próprio documento: uma VUS **não autoriza** liberar parente algum da vigilância
clínica.

O documento também fecha, de propósito, a porta mais perigosa do teste
genético amplo: testar genes de evidência fraca num fenótipo que não é claro
não esclarece nada e ainda produz variantes de significado incerto que geram
ansiedade e decisões clínicas erradas. Por isso a árvore abaixo começa **antes**
do teste — na qualidade do fenótipo do caso índice — e não na escolha do
painel genético.

## Árvore de decisão

```mermaid
flowchart TD
  R0["Caso índice com fenótipo de cardiomiopatia — hipertrófica, dilatada<br/>ou arritmogênica — em avaliação, com ou sem história familiar de<br/>morte súbita cardíaca precoce ou inexplicada em parente<br/>de primeiro grau"] --> D1{"Fenótipo de alta probabilidade diagnóstica confirmado<br/>por critérios clínicos e de imagem — ex.: critérios<br/>de Task Force para cardiomiopatia arritmogênica?"}

  D1 -->|"Não — fenótipo fraco ou não definido"| C1(["Não testar genes de evidência limitada, disputada<br/>ou refutada nesse contexto. Reavaliar clinicamente<br/>e reconsiderar teste genético se o fenótipo<br/>se tornar mais definido"])

  D1 -->|"Sim — fenótipo de alta probabilidade"| P1["Aconselhamento genético estruturado antes do teste:<br/>padrão de herança, penetrância incompleta e variável,<br/>implicações reprodutivas, direito de não testar"]

  P1 --> D2{"Após o aconselhamento, paciente e família aceitam<br/>prosseguir com painel de genes de evidência<br/>definida ou forte para a doença?"}

  D2 -->|"Não aceita testar"| C2(["Teste genético não realizado: manter vigilância<br/>clínica do caso índice. Parentes de primeiro grau<br/>também requerem rastreamento clínico periódico, pela<br/>heterogeneidade de idade de início e progressão"])

  D2 -->|"Aceita testar"| P2["Realizar teste genético em painel (sequenciamento de<br/>nova geração) no caso índice, restrito a genes com<br/>evidência definida ou forte de causalidade para a doença"]

  P2 --> D3{"Resultado do teste genético no caso índice?"}

  D3 -->|"Variante patogênica ou provavelmente<br/>patogênica (P/LP) identificada"| P3["Oferecer teste em cascata, dirigido à variante<br/>específica, aos parentes de primeiro grau<br/>e demais parentes apropriados"]

  D3 -->|"Variante de significado<br/>incerto (VUS)"| C3(["VUS não deve ser usada para rastreamento em cascata.<br/>Parentes de primeiro grau seguem rastreamento CLÍNICO<br/>periódico, não genético. Considerar reclassificação em<br/>centro multidisciplinar de cardiogenética conforme<br/>evidência de segregação familiar do fenótipo"])

  D3 -->|"Teste negativo — nenhuma<br/>variante P/LP identificada"| C4(["Rastreamento genético em cascata não é possível.<br/>Parentes de primeiro grau seguem rastreamento CLÍNICO<br/>periódico, pela heterogeneidade fenotípica de idade<br/>de início e progressão dentro da mesma família"])

  P3 --> D4{"Resultado do teste em cascata<br/>no parente de primeiro grau?"}

  D4 -->|"Não carreia a variante"| C5(["Liberado da vigilância clínica cardíaca de rotina<br/>na vasta maioria das condições. Reforçar<br/>aconselhamento sobre risco residual da população geral"])

  D4 -->|"Carreia a variante (P/LP)"| C6(["Rastreamento clínico cardíaco periódico — ECG,<br/>ecocardiograma, e ressonância quando indicada —,<br/>pela penetrância incompleta e variável: carrear<br/>a variante não implica necessariamente doença clínica"])

  classDef conduta fill:#eef6ef,stroke:#2f7a4f,color:#12301f;
  class C1,C2,C3,C4,C5,C6 conduta;
```

## O sistema de graduação do consenso, e por que ele aparece pouco na árvore

O documento não usa Classe I/IIa/IIb/III nem nível A/B/C — usa um símbolo de
três cores por recomendação: **coração verde** ("deve fazer", apoiado por
evidência observacional forte ou opinião de especialista consolidada),
**coração amarelo** ("pode fazer", indicação razoável mas com evidência ou
consenso menos firme) e **coração vermelho** ("não fazer"). As recomendações
centrais desta árvore — oferecer teste ao caso índice de alta probabilidade,
exigir aconselhamento genético antes de testar, oferecer teste em cascata
dirigido à variante após identificação de P/LP, e não testar genes de
evidência fraca em fenótipo indefinido — são todas **coração verde ou
vermelho**, ou seja, no nível mais firme de recomendação que o documento
oferece.

## Por que esta ordem, e o que fica de fora do diagrama

A árvore separa deliberadamente **duas populações que recebem a mesma palavra
"vigilância" no consultório, mas com significado oposto**: o parente que
carrega a variante (vigilância clínica **porque** o risco está confirmado, e
a penetrância é incompleta e variável — carrear a variante não é o mesmo que
ter a doença) e o parente cujo caso índice teve teste negativo ou não
realizado (vigilância clínica **apesar de** não haver variante confirmada,
porque o teste negativo não exclui doença monogênica e a heterogeneidade de
idade de início dentro da mesma família permanece). As duas situações levam
ao mesmo tipo de acompanhamento — eletrocardiograma e ecocardiograma seriados
— mas por raciocínios diferentes, e tratá-las como equivalentes esconde a
diferença de certeza diagnóstica por trás de cada uma.

**Não entram como ramos da árvore, por serem específicos de cada fenótipo e já
tratados em profundidade noutros documentos desta pasta:** os limiares
numéricos de rastreamento clínico e a periodicidade exata por doença (o
documento "Cardiomiopatia Dilatada (CMD): Diagnóstico Genético e Manejo — ESC
2023" e o fluxograma de risco de morte súbita e CDI na CMD cobrem isso para a
forma dilatada; o fluxograma de CMH ESC 2023 cobre a estratificação de risco
por HCM Risk-SCD); a lista de genes por fenótipo com evidência definida,
forte, moderada, limitada, disputada ou refutada, que o consenso publica em
tabelas próprias por doença; e a calculadora de risco específica para
portador de variante em *LMNA*, já citada e verificada no fluxograma de
investigação etiológica da CMD desta mesma pasta. Redesenhar qualquer um
desses pontos aqui duplicaria árvore já publicada, ou citaria número de fonte
não reconferida nesta sessão.

**O aconselhamento genético não é etapa administrativa.** O consenso é
explícito sobre o que ele precisa cobrir antes de qualquer amostra ser
colhida: o padrão de herança esperado (em geral autossômico dominante, com
transmissão de 50% para a prole), a penetrância incompleta e variável — a
família precisa entender que carregar a variante não significa
necessariamente desenvolver a doença —, e as opções reprodutivas quando há
plano de gestação, incluindo teste genético pré-natal e diagnóstico
genético pré-implantacional.
