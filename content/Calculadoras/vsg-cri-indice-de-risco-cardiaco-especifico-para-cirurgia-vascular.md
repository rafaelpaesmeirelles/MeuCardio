---
title: "VSG-CRI: Índice de Risco Cardíaco Específico para Cirurgia Vascular"
slug: vsg-cri-indice-de-risco-cardiaco-especifico-para-cirurgia-vascular
theme: "Calculadoras"
kind: calculadora
review_status: revisado
source_refs: ["Bertges DJ, Goodney PP, Zhao Y, Schanzer A, Nolan BW, Likosky DS, Eldrup-Jorgensen J, Cronenwett JL; Vascular Study Group of New England. The Vascular Study Group of New England Cardiac Risk Index (VSG-CRI) predicts cardiac complications more accurately than the Revised Cardiac Risk Index in vascular surgery patients. J Vasc Surg. 2010;52(3):674-683, 683.e1-683.e3. DOI: 10.1016/j.jvs.2010.03.031. PMID: 20570467 — 10.081 pacientes da Vascular Study Group of New England (2003-2008), coorte de derivação (8.208) e de validação (1.873)", "Welten GM, Schouten O, van Domburg RT, Feringa HH, Hoeks SE, Dunkelgrün M, van Gestel YR, Goei D, Bax JJ, Poldermans D. The influence of aging on the prognostic value of the revised cardiac risk index for postoperative cardiac complications in vascular surgery patients. Eur J Vasc Endovasc Surg. 2007;34(6):632-638. DOI: 10.1016/j.ejvs.2007.05.002. PMID: 17587611 — 2.642 pacientes de cirurgia vascular, estratificados em quatro faixas etárias", "Ford MK, Beattie WS, Wijeysundera DN. Systematic review: prediction of perioperative cardiac complications and mortality by the revised cardiac risk index. Ann Intern Med. 2010;152(1):26-35. PMID: 20048269 — revisão sistemática de 24 estudos e 792.740 pacientes, já citada no documento de RCRI/NSQIP MICA desta pasta"]
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

## ⚠️ O que o resumo NÃO traz — VERIFICAÇÃO HUMANA NECESSÁRIA
O abstract confirma que **"preditores significativos foram convertidos em um escore inteiro para
criar uma fórmula prática de predição de risco cardíaco"**, mas **não publica, no próprio resumo, a
tabela de pontos atribuída a cada um dos nove preditores** — só as razões de chance da análise
multivariada, listadas acima. **Não é a mesma coisa**: odds ratio não é ponto de escore, e transformar
um no outro sem ver a tabela original seria inventar exatamente o tipo de dado que este projeto proíbe.

**VERIFICAÇÃO HUMANA NECESSÁRIA** — a tabela de pontos por preditor está no texto completo (J Vasc
Surg. 2010;52(3):674-683, com apêndices 683.e1-683.e3), não no resumo indexado no PubMed. Quem tiver
acesso ao texto integral pode completar este documento com a pontuação exata de cada fator.

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

## Limites
- **O VSG-CRI foi derivado só em pacientes do VSGNE (Nova Inglaterra, EUA)**, registro regional; não
  há validação externa em população brasileira.
- **O desfecho combina infarto, arritmia e insuficiência cardíaca** — categorias que se sobrepõem, e
  o resumo não permite decompor o peso de cada uma dentro do escore final.
- **A discriminação é moderada (0,71), não excelente** — melhor que o RCRI em cirurgia vascular, mas
  está longe de um modelo com alta capacidade discriminativa.
- **A tabela de pontos por preditor não está disponível no resumo indexado**, só no texto completo —
  ver a marcação de verificação humana acima.
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
  o resumo dá odds ratio, não pontos; tratar um pelo outro é inventar dado.
- **Aplicar o RCRI sem ajuste em paciente vascular muito idoso (>75 anos)** — a capacidade
  discriminativa cai para 0,62, próxima do acaso, segundo Welten et al.
- **Extrapolar o VSG-CRI para cirurgia vascular de urgência/emergência** — a coorte de derivação é de
  procedimentos eletivos e urgentes não emergenciais.
