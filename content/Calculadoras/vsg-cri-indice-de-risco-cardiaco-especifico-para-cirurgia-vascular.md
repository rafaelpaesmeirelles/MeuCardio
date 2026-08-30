---
title: "VSG-CRI: Índice de Risco Cardíaco Específico para Cirurgia Vascular"
slug: vsg-cri-indice-de-risco-cardiaco-especifico-para-cirurgia-vascular
theme: "Calculadoras"
kind: calculadora
review_status: revisado
source_refs: ["Bertges DJ, Goodney PP, Zhao Y, Schanzer A, Nolan BW, Likosky DS, Eldrup-Jorgensen J, Cronenwett JL; Vascular Study Group of New England. The Vascular Study Group of New England Cardiac Risk Index (VSG-CRI) predicts cardiac complications more accurately than the Revised Cardiac Risk Index in vascular surgery patients. J Vasc Surg. 2010;52(3):674-683, 683.e1-683.e3. DOI: 10.1016/j.jvs.2010.03.031. PMID: 20570467 — 10.081 pacientes da Vascular Study Group of New England (2003-2008), coorte de derivação (8.208) e de validação (1.873)", "Welten GM, Schouten O, van Domburg RT, Feringa HH, Hoeks SE, Dunkelgrün M, van Gestel YR, Goei D, Bax JJ, Poldermans D. The influence of aging on the prognostic value of the revised cardiac risk index for postoperative cardiac complications in vascular surgery patients. Eur J Vasc Endovasc Surg. 2007;34(6):632-638. DOI: 10.1016/j.ejvs.2007.05.002. PMID: 17587611 — 2.642 pacientes de cirurgia vascular, estratificados em quatro faixas etárias", "Ford MK, Beattie WS, Wijeysundera DN. Systematic review: prediction of perioperative cardiac complications and mortality by the revised cardiac risk index. Ann Intern Med. 2010;152(1):26-35. PMID: 20048269 — revisão sistemática de 24 estudos e 792.740 pacientes, já citada no documento de RCRI/NSQIP MICA desta pasta", "Smeili LAA, Lotufo PA. Incidence and Predictors of Cardiovascular Complications and Death after Vascular Surgery. Arq Bras Cardiol. 2015;105(5):510-518. DOI: 10.5935/abc.20150113. PMID: 26421535. PMC4651410 — coorte prospectiva brasileira de 141 pacientes (Hospital das Clínicas de São Paulo, 2008-2010), validação externa de RCRI e VSG-CRI; usada aqui para a validação brasileira (área sob a curva) E para uma tabela candidata de pontos do VSG-CRI (Tabela 1, citando Bertges 2010) que NÃO foi adotada como confirmação da lacuna de verificação humana, por omitir o preditor 'teste de estresse anormal' sem explicação — ver texto do documento"]
legacy_source: "Documento novo, escrito em 01/08/2026. O documento `escores-de-risco-cardiaco-para-cirurgia-nao-cardiaca-rcri-e-nsqip-mica.md`, já existente nesta pasta, registra que o RCRI tem desempenho ruim especificamente na cirurgia VASCULAR (área sob a curva de 0,64 na meta-análise de Ford 2010, quase o mesmo que o acaso). O que faltava era o escore que foi desenhado para resolver exatamente esse ponto fraco: um índice derivado dentro da própria cirurgia vascular, não extrapolado de uma coorte mista. Este documento cobre o VSG-CRI, e complementa — não substitui — o documento geral de RCRI/NSQIP MICA."
---

# VSG-CRI: Índice de Risco Cardíaco Específico para Cirurgia Vascular

## Por que o RCRI não basta aqui
O documento `escores-de-risco-cardiaco-para-cirurgia-nao-cardiaca-rcri-e-nsqip-mica.md`, nesta
mesma pasta, já registra o achado central da revisão sistemática de Ford, Beattie e Wijeysundera
(Ann Intern Med. 2010;152(1):26-35, PMID 20048269): o RCRI discrimina razoavelmente na cirurgia não
cardíaca mista (área sob a curva **0,75**), mas **na cirurgia vascular cai para 0,64** — pouco
acima do acaso.

Dois achados adicionais, de fontes independentes, mostram por que isso não é detalhe estatístico:

1. **O RCRI sistematicamente SUBESTIMA risco em cirurgia vascular**, e a subestimação piora quanto
   mais complexo o procedimento (ver a seção de derivação do VSG-CRI abaixo).
2. **A capacidade discriminativa do RCRI piora com a idade.** Welten et al. (Eur J Vasc Endovasc
   Surg. 2007;34(6):632-638, PMID 17587611), em **2.642 pacientes de cirurgia vascular**
   estratificados em quatro faixas etárias (≤55, 56-65, 66-75, >75 anos): a estatística c do RCRI
   foi **0,76 nos pacientes com 55 anos ou menos** e caiu para **0,62 nos maiores de 75 anos**.
   Ajustando o RCRI por idade, risco cirúrgico (baixo/baixo-intermediário/alto-intermediário/alto)
   e hipertensão, a estatística c nos idosos **melhorou de 0,62 para 0,69**. **Conclusão literal dos
   autores:** o valor prognóstico do índice de Lee é **reduzido em pacientes idosos** de cirurgia
   vascular, e ajustá-lo por idade, risco do procedimento e hipertensão **melhora significativamente**
   sua performance.

Foi para resolver o primeiro ponto — não o ajuste por idade, que segue sem escore dedicado — que o
Vascular Study Group of New England (VSGNE) derivou um índice específico para cirurgia vascular.

## Derivação do VSG-CRI
Bertges DJ et al., J Vasc Surg. 2010;52(3):674-683 (PMID 20570467). Estudo de **10.081 pacientes**
submetidos, entre 2003 e 2008, a quatro procedimentos
vasculares eletivos ou urgentes (não emergenciais) dentro do registro do VSGNE:

- **Endarterectomia de carótida (CEA)** — 5.293 pacientes
- **Bypass de membro inferior (LEB)** — 2.673 pacientes
- **Reparo endovascular de aneurisma de aorta abdominal (EVAR)** — 1.005 pacientes
- **Reparo aberto infrarrenal de aneurisma de aorta abdominal (OAAA)** — 1.110 pacientes

**Incidência geral de evento cardíaco maior intra-hospitalar na coorte: 6,3%** (infarto do
miocárdio 2,5%, arritmia 3,9%, insuficiência cardíaca congestiva 1,8% — as categorias se
sobrepõem, por isso a soma excede o total).

**O RCRI subestimou complicações cardíacas em 1,7 a 7,4 vezes**, conforme o procedimento, com base
nas taxas reais observadas por número de fatores de risco: **2,6%, 6,7%, 11,6% e 18,4%** para
pacientes com 0, 1, 2 e ≥3 fatores do RCRI, respectivamente — muito acima do que o RCRI original
previa para essas mesmas faixas. **O RCRI previu razoavelmente bem após CEA, mas subestimou
substancialmente o risco após LEB, EVAR e OAAA**, tanto no extremo de baixo quanto no de alto risco.

## Os nove preditores independentes, com razão de chance (odds ratio)
Análise multivariada na coorte de derivação (8.208 pacientes), com os seguintes preditores
independentes de evento cardíaco adverso:

| Preditor | Odds ratio |
|---|---|
| **Idade crescente** (por faixa) | **1,7 a 2,8** |
| Tabagismo | 1,3 |
| Diabetes insulino-dependente | 1,4 |
| Doença arterial coronariana | 1,4 |
| Insuficiência cardíaca congestiva | 1,9 |
| Teste de estresse cardíaco anormal | 1,2 |
| Betabloqueador de uso crônico | 1,4 |
| Doença pulmonar obstrutiva crônica | 1,6 |
| Creatinina ≥ 1,8 mg/dL | 1,7 |
| **Revascularização cardíaca prévia** | **0,8 (protetor)** |

**Revascularização cardíaca prévia foi o único fator protetor** — reduz, e não aumenta, a chance de
evento cardíaco perioperatório na coorte.

## O que o resumo não permite afirmar
O abstract confirma que **"preditores significativos foram convertidos em um escore inteiro para
criar uma fórmula prática de predição de risco cardíaco"**, mas **não publica, no próprio resumo, a
tabela de pontos atribuída a cada um dos nove preditores** — só as razões de chance da análise
multivariada, listadas acima. **Não é a mesma coisa**: odds ratio não é ponto de escore, e transformar
um no outro sem ver a tabela original seria inventar exatamente o tipo de dado que este projeto proíbe.

**VERIFICAÇÃO HUMANA NECESSÁRIA** — a tabela de pontos por preditor está no texto completo (J Vasc
Surg. 2010;52(3):674-683, com apêndices 683.e1-683.e3), não no resumo indexado no PubMed. Em
02/08/2026 apareceu uma **tabela candidata** por fonte secundária real e citável (ver bloco
próprio logo abaixo), mas ela tem uma lacuna própria — não pontua o "teste de estresse cardíaco
anormal", que é um dos nove preditores confirmados no resumo original — e por isso **não foi
adotada como resposta à marcação**. Quem tiver acesso ao texto integral (incluindo os apêndices
683.e1-683.e3) pode completar este documento com a pontuação exata de cada fator e, de posse
dela, confirmar ou descartar a tabela candidata documentada abaixo.

**Vias de acesso ao texto completo já tentadas em 02/08/2026, e todas fechadas — não repetir:**
- **PMC/PMID 20570467**: `elink.fcgi` (dbfrom=pubmed, db=pmc) devolve só `pubmed_pmc_refs` (artigos
  que citam o estudo), nenhum `pubmed_pmc` — o artigo **não está depositado no PMC**. Coerente com o
  registro do PubMed, que classifica o financiamento como `Research Support, U.S. Gov't, Non-P.H.S.`
  — sem financiamento do NIH/PHS, não há mandato de depósito no PubMed Central.
- **Unpaywall** (DOI 10.1016/j.jvs.2010.03.031): `is_oa: false`, `oa_locations: []`,
  `has_repository_copy: false` — nenhuma cópia de acesso aberto catalogada, em repositório
  institucional ou preprint.
- **ScienceDirect/Elsevier** (`linkinghub.elsevier.com`, PII S0741-5214(10)00774-3): a página é um
  redirecionador que exige JavaScript; sem assinatura, não expõe o corpo do artigo nem os apêndices.
- **ResearchGate** (publicação 44694849): retorna 403 (bloqueio de acesso automatizado).
- **medicalalgorithms.com**: tem uma página dedicada ao VSG-CRI de Bertges et al., mas o conteúdo
  está atrás de assinatura — a busca não expôs a tabela de pontos.
- **PMC5079798** (Bertges DJ et al., "The Vascular Quality Initiative Cardiac Risk Index for
  prediction of myocardial infarction after vascular surgery", J Vasc Surg. 2016;64(5):1411-1421,
  PMID 27449347) é **um escore diferente** — o VQI-CRI, sucessor do VSG-CRI, derivado numa coorte
  maior e mais recente (88.791 procedimentos, 2012-2014) e com desfecho restrito a infarto
  (excluindo arritmia/ICC). O texto completo está aberto (NIHPA Author Manuscript), mas cita o
  VSG-CRI só na lista de referências — **não reproduz a tabela de pontos do escore de 2010**, e
  usar os pontos do VQI-CRI como se fossem do VSG-CRI seria atribuir dado ao escore errado.
- **Resultados de busca na web** (WebSearch) devolveram uma tabela de pontos por preditor (idade em
  faixas, DAC, ICC, DPOC, creatinina, tabagismo, diabetes, betabloqueador, revascularização prévia)
  atribuída ao VSG-CRI, mas **sem página-fonte citável e verificável** — o resumo do resultado
  aponta para calculadoras online (ex.: appcardio.com) e agregadores, categorias de fonte já
  registradas como inaceitáveis neste projeto. **Não foi usada**, porque não há como conferir que os
  valores vieram do artigo original e não de estimativa/reconstrução de terceiros.

## Tabela candidata encontrada em 02/08/2026 — fonte real, mas NÃO adotada
Nesta rodada de verificação apareceu uma fonte secundária diferente das anteriores: **Smeili LAA,
Lotufo PA. Incidence and Predictors of Cardiovascular Complications and Death after Vascular
Surgery. Arq Bras Cardiol. 2015;105(5):510-518. DOI: 10.5935/abc.20150113. PMID: 26421535.**
Artigo brasileiro, revisado por pares, de acesso aberto no PMC (**PMC4651410**), que valida RCRI e
VSG-CRI na mesma coorte de cirurgia vascular (área sob a curva **0,635** para o RCRI e **0,639**
para o VSG-CRI, em complicação cardiovascular precoce). A **Tabela 1** desse artigo reproduz uma
tabela de pontos do VSG-CRI, citando Bertges DJ et al. 2010 como referência 12 — conferida em
**três leituras independentes** (HTML renderizado duas vezes, XML bruto via `efetch` do PMC uma
vez, para excluir erro de transcrição desta sessão):

| Preditor | Pontos (tabela candidata) |
|---|---|
| Idade > 80 anos | 4 |
| Idade 70-79 anos | 3 |
| Idade 60-69 anos | 2 |
| Doença arterial coronariana | 2 |
| Insuficiência cardíaca | 2 |
| DPOC | 2 |
| Creatinina > 1,8 mg/dL | 2 |
| Tabagismo | 1 |
| Diabetes insulino-dependente | 1 |
| Betabloqueador de uso crônico | 1 |
| Revascularização coronariana prévia | -1 (protetor) |

**A mesma tabela, com os mesmos onze valores, também aparece numa calculadora online**
(appcardio.com) — duas fontes convergindo seria, em outras circunstâncias, o tipo de corroboração
que já justificaria adotar um dado. **Mas há uma discrepância real que impede tratar esta
tabela como resposta à lacuna**: ela **não pontua o "teste de estresse cardíaco anormal"**, que é
um dos nove preditores independentes já confirmados no resumo do Bertges 2010 (razão de chance
1,2, na tabela de odds ratio mais acima neste documento). Duas explicações são possíveis, e nenhuma
das duas pode ser confirmada sem o apêndice original:

1. o teste de estresse, por ter o menor odds ratio dos nove, pode ter recebido **0 pontos** no
   escore inteiro final e por isso não aparecer numa tabela que só lista itens com peso diferente
   de zero — nesse caso a tabela acima estaria correta e completa por omissão intencional;
2. a tabela secundária está **incompleta ou foi copiada de uma fonte comum** às duas páginas sem
   conferência contra o artigo original — nesse caso adotá-la reproduziria um erro dentro de uma
   calculadora clínica, o tipo de defeito que este projeto trata como mais grave que a lacuna.

**Por não haver como distinguir as duas hipóteses, esta tabela NÃO foi incorporada ao corpo do
documento como dado confirmado**, e a marcação de verificação humana permanece — agora mais
estreita, porque documenta exatamente que falta resolver: confirmar (ou não) esta tabela contra o
apêndice 683.e1-683.e3 do artigo original, com atenção específica ao peso do teste de estresse.

## O que o resumo garante: estratificação por número de fatores e por escore final
Duas estratificações distintas aparecem no resumo, e não devem ser confundidas entre si:

**Por número bruto de fatores de risco presentes** (contagem simples, não ponderada):

| Fatores de risco VSG | Coorte de derivação | Coorte de validação |
|---|---|---|
| **0 a 3** | **3,1%** | **3,8%** |
| **4** | **5,0%** | **5,2%** |
| **5** | **6,8%** | **8,1%** |
| **≥ 6** | **11,6%** | **10,1%** |

**Pelo escore VSG-CRI final** (ponderado, 0 a 8 pontos — a fórmula prática mencionada acima): **seis
categorias de risco, variando de 2,6% a 14,3%**, discerníveis ao longo da faixa de escore de 0-3 a 8.

## Desempenho por procedimento
O modelo agregado (todos os quatro procedimentos juntos) foi bem calibrado (**r = 0,99**, p < 0,001),
com discriminação **moderada** (área sob a curva ROC **0,71**). Os modelos específicos por
procedimento variaram pouco:

| Procedimento | Área sob a curva (ROC) |
|---|---|
| CEA (endarterectomia de carótida) | **0,74** |
| LEB (bypass de membro inferior) | **0,72** |
| EVAR (reparo endovascular de AAA) | **0,74** |
| OAAA (reparo aberto de AAA) | **0,68** |
| **Modelo agregado** | **0,71** |

**Conclusão literal dos autores:** o modelo cardíaco do VSGNE prediz de forma **mais precisa** o
risco real de complicação cardíaca do que o RCRI, tanto no extremo de baixo quanto no de alto risco,
ao longo dos quatro procedimentos vasculares estudados, e **representa uma ferramenta importante
para a decisão clínica**.

## Como decidir entre RCRI e VSG-CRI na prática vascular
| | RCRI | VSG-CRI |
|---|---|---|
| população de derivação | cirurgia não cardíaca **mista**, 1999 | cirurgia **vascular**, 2003-2008 |
| variáveis | 6, dicotômicas | 9, incluindo idade em faixas |
| discriminação em cirurgia vascular | **0,64** (meta-análise) | **0,71-0,74** (derivação própria) |
| desempenho por procedimento | não diferencia | **diferencia** CEA/LEB/EVAR/OAAA |
| ajuste por idade | não incorpora idade | **incorpora idade como preditor** |
| tabela de pontos publicamente disponível no resumo | não se aplica (soma de 6 itens dicotômicos) | **não está no resumo — texto completo necessário** |

**Para cirurgia vascular especificamente, a literatura favorece o VSG-CRI sobre o RCRI genérico** —
é exatamente a lacuna que a meta-análise de Ford 2010 já apontava (RCRI com AUC 0,64 em vascular) e
que motivou a derivação de um escore próprio. **Fora do contexto vascular, o RCRI segue sendo o mais
usado e o mais transportável** — ver o documento geral de RCRI/NSQIP MICA desta pasta.

## Validação externa em população brasileira
Encontrada em 02/08/2026, ao investigar a lacuna da tabela de pontos (ver acima): **Smeili LAA,
Lotufo PA. Incidence and Predictors of Cardiovascular Complications and Death after Vascular
Surgery. Arq Bras Cardiol. 2015;105(5):510-518. DOI: 10.5935/abc.20150113. PMID: 26421535.**
Coorte **prospectiva de 141 pacientes** do Hospital das Clínicas de São Paulo (agosto de 2008 a
janeiro de 2010), que testou RCRI e VSG-CRI na mesma população vascular brasileira: área sob a
curva **0,635 (RCRI) e 0,639 (VSG-CRI)** para complicação cardiovascular precoce, e **0,562 (RCRI)
e 0,610 (VSG-CRI)** para óbito em 30 dias. O VSG-CRI discriminou melhor que o RCRI nas duas
comparações, mas com diferença mais modesta do que a observada na coorte de derivação americana —
e a diferença é maior no desfecho de óbito do que no de complicação cardiovascular. Este é o
único achado de validação em população brasileira localizado até agora para o VSG-CRI.

## Limites
- **O VSG-CRI foi derivado em pacientes do VSGNE (Nova Inglaterra, EUA)**, registro regional. Há
  uma validação externa em população brasileira (Smeili & Lotufo 2015, ver seção acima), mas numa
  coorte pequena (141 pacientes) e com discriminação mais modesta que a da derivação original —
  não substitui uma validação em amostra brasileira de porte comparável ao estudo americano.
- **O desfecho combina infarto, arritmia e insuficiência cardíaca** — categorias que se sobrepõem, e
  o resumo não permite decompor o peso de cada uma dentro do escore final.
- **A discriminação é moderada (0,71), não excelente** — melhor que o RCRI em cirurgia vascular, mas
  está longe de um modelo com alta capacidade discriminativa.
- **A tabela de pontos por preditor não está confirmada contra a fonte primária** — só no texto
  completo, que segue inacessível. Existe uma tabela candidata de fonte secundária (ver seção
  própria acima), mas com uma lacuna própria (não pontua o teste de estresse) que impede tratá-la
  como confirmada.
- **O estudo é de 2010, com dados de 2003-2008** — antecede parte da evolução do manejo
  perioperatório vascular contemporâneo (endpoints de troponina de alta sensibilidade, mudanças na
  técnica endovascular).
- **Nenhum dos dois estudos aqui citados (VSG-CRI e o de envelhecimento) propõe um escore único que
  combine ponderação por idade contínua com os nove preditores do VSG-CRI** — são achados
  complementares, não um instrumento fundido.

## Armadilhas clínicas
- **Usar o RCRI isoladamente para estratificar risco de cirurgia vascular maior** (LEB, EVAR, OAAA)
  sem reconhecer que ele **subestima risco em até 7,4 vezes** nesse contexto, pela própria derivação
  do VSG-CRI.
- **Confundir a estratificação por "número de fatores VSG" com o "escore VSG-CRI ponderado"** — são
  as duas tabelas de risco do resumo, com faixas e percentuais diferentes entre si.
- **Escrever ou usar uma tabela de pontos por preditor do VSG-CRI que não veio do texto completo** —
  o resumo dá odds ratio, não pontos; tratar um pelo outro é inventar dado. Isso vale inclusive para
  a tabela candidata documentada acima (Smeili & Lotufo 2015): ela é citável e real, mas tem uma
  omissão não explicada (o teste de estresse) que a torna imprópria para uso clínico até ser
  confirmada contra o apêndice do Bertges 2010.
- **Aplicar o RCRI sem ajuste em paciente vascular muito idoso (>75 anos)** — a capacidade
  discriminativa cai para 0,62, próxima do acaso, segundo Welten et al.
- **Extrapolar o VSG-CRI para cirurgia vascular de urgência/emergência** — a coorte de derivação é de
  procedimentos eletivos e urgentes não emergenciais.
