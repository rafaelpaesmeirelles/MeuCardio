---
title: "Escore IABP-SHOCK II: Estratificação de Mortalidade em 30 Dias no Choque Cardiogênico"
slug: escore-iabp-shock-ii-estratificacao-de-mortalidade-em-30-dias-no-choque-cardiogenico
theme: "Calculadoras"
kind: calculadora
review_status: revisado
source_refs: ["Pöss J, Köster J, Fuernau G, Eitel I, de Waha S, Ouarrak T, Lassus J, Harjola VP, Zeymer U, Thiele H, Desch S. Risk Stratification for Patients in Cardiogenic Shock After Acute Myocardial Infarction. J Am Coll Cardiol. 2017;69(15):1913-1920. DOI: 10.1016/j.jacc.2017.02.027. PMID: 28408020 — derivação a partir do ensaio IABP-SHOCK II (NCT00491036), validação interna no registro IABP-SHOCK II e validação externa na coorte CardShock (n=137)"]
legacy_source: "Documento novo. A pasta Calculadoras já tem escores de risco cirúrgico/procedimento (EuroSCORE II, STS, SYNTAX/SYNTAX II, ACEF) e um escore de suporte farmacológico já em curso (VIS), mas nenhum instrumento dedicado a estratificar mortalidade de curto prazo especificamente em choque cardiogênico já estabelecido. Não duplica o documento já publicado sobre o ENSAIO IABP-SHOCK II (content/Terapia_intensiva/balao-intra-aortico-no-choque-cardiogenico-o-ensaio-iabp-shock-ii.md e content/Doença_coronariana/choque-cardiogenico-na-sindrome-coronariana-aguda-culprit-shock-e-iabp-shock-ii.md), que trata da eficácia do balão intra-aórtico (Thiele H et al., NEJM 2012 e Lancet 2013) — pergunta clínica distinta. Este documento trata do ESCORE DE RISCO derivado posteriormente a partir da base de dados do mesmo ensaio (Pöss J et al., JACC 2017), publicação e pergunta diferentes: não 'o IABP funciona?', mas 'qual é o risco de morte em 30 dias deste paciente em choque cardiogênico, e como isso orienta a intensidade do suporte?'."
---

# Escore IABP-SHOCK II: Estratificação de Mortalidade em 30 Dias no Choque Cardiogênico

## O que resolve
A mortalidade do choque cardiogênico complicando infarto agudo do miocárdio permanece alta, e a decisão sobre intensidade de suporte hemodinâmico (do inotrópico isolado ao dispositivo de suporte circulatório mecânico) se beneficia de uma estratificação de risco objetiva, feita à beira do leito, a partir de variáveis já disponíveis na admissão e no momento da intervenção coronária. O **escore IABP-SHOCK II** foi desenvolvido exatamente para isso: um instrumento simples, calculável na rotina clínica, para prever mortalidade de curto prazo (30 dias) em choque cardiogênico pós-infarto.

## Derivação (Pöss J et al., JACC 2017, PMID 28408020)
Estudo derivado da base de dados do ensaio **IABP-SHOCK II** (Intraaortic Balloon Pump in Cardiogenic Shock II, NCT00491036) — o mesmo ensaio já registrado em documentos separados desta biblioteca sobre a eficácia do balão intra-aórtico, aqui usado como coorte para construir um escore de risco, não para testar o dispositivo. Metodologia: análise de regressão multivariável por seleção stepwise, com o desfecho primário sendo **mortalidade por qualquer causa em 30 dias**.

**Seis variáveis emergiram como preditores independentes** e compõem o escore, cada uma valendo 1 ou 2 pontos:
- **Idade > 73 anos**
- **AVC prévio**
- **Glicemia na admissão > 10,6 mmol/L (191 mg/dL)**
- **Creatinina na admissão > 132,6 µmol/L (1,5 mg/dL)**
- **Fluxo TIMI < 3 após intervenção coronária percutânea**
- **Lactato arterial na admissão > 5 mmol/L**

**A fonte primária verificada nesta sessão não detalha, no resumo, exatamente qual das seis variáveis recebe 1 ponto e qual recebe 2** — o abstract afirma que "1 ou 2 pontos foram atribuídos a cada variável", sem especificar a atribuição individual linha a linha. Para reprodução exata da pontuação por variável, `VERIFICAÇÃO HUMANA NECESSÁRIA` contra a Tabela 2 do texto completo do artigo (JACC 2017;69(15):1913-1920).

## Categorias de risco e mortalidade observada em 30 dias
A soma dos pontos define três categorias de risco, com mortalidade em 30 dias fortemente escalonada (p < 0,0001):

| Categoria | Pontuação | Mortalidade em 30 dias |
|---|---|---|
| Baixo risco | 0 a 2 pontos | **23,8%** |
| Risco intermediário | 3 a 4 pontos | **49,2%** |
| Alto risco | 5 a 9 pontos | **76,6%** |

## Validação interna e externa
- **Validação interna**, no registro do próprio IABP-SHOCK II: boa discriminação, com **área sob a curva ROC de 0,79**.
- **Validação externa**, na coorte do ensaio **CardShock** (n=137, população finlandesa de choque cardiogênico de etiologia mais ampla, não restrita a infarto): mortalidade de curto prazo de **28,0%** (escore 0-2), **42,9%** (escore 3-4) e **77,3%** (escore 5-9; p < 0,001), com **área sob a curva de 0,73** — discriminação um pouco menor que na coorte de derivação, mas ainda relevante clinicamente, e o gradiente de risco entre as três categorias se manteve consistente numa população distinta.
- **Análise de Kaplan-Meier** confirmou aumento escalonado de mortalidade entre as categorias (0-2 vs. 3-4: p=0,04; 0-2 vs. 5-9: p=0,008).

## Conclusão do próprio estudo
**"O escore IABP-SHOCK II pode ser facilmente calculado na prática clínica diária e se correlacionou fortemente com mortalidade em pacientes com choque cardiogênico relacionado a infarto. Pode ajudar a estratificar o risco de mortalidade de curto prazo e, assim, facilitar a tomada de decisão clínica."**

## Síntese prática
O escore IABP-SHOCK II preenche uma lacuna real desta biblioteca de calculadoras: nenhum instrumento já registrado estratifica risco especificamente em choque cardiogênico estabelecido, cenário em que a decisão sobre intensidade de suporte (droga vasoativa isolada, balão intra-aórtico, ou dispositivo de suporte circulatório mecânico mais robusto como Impella ou ECMO-VA, já descritos em documentos de Terapia intensiva) precisa ser tomada rapidamente e sob incerteza prognóstica considerável. As seis variáveis são todas rotineiramente disponíveis na admissão e no momento pós-intervenção coronária (idade, história de AVC, glicemia, creatinina, fluxo TIMI pós-ICP e lactato), sem exigir exame adicional. A validação externa numa coorte de etiologia mais heterogênea de choque (CardShock) — embora com discriminação um pouco menor que na coorte de derivação — sustenta aplicabilidade além do choque estritamente pós-infarto tratado por ICP primária, com a ressalva de que a derivação e a validação interna foram especificamente nessa população.

## Armadilhas clínicas
- Aplicar o escore antes da intervenção coronária percutânea — uma das seis variáveis (fluxo TIMI pós-ICP) só está disponível depois do procedimento; o escore, como derivado, pressupõe que a revascularização já ocorreu.
- Tratar o escore de baixo risco (0-2 pontos, mortalidade de 23,8% em 30 dias) como "risco baixo" no sentido absoluto — é baixo apenas *relativo* às outras duas categorias desta escala; quase 1 em 4 pacientes nessa faixa morre em 30 dias, e a decisão clínica deve refletir essa gravidade de base do choque cardiogênico como síndrome, não o rótulo da categoria isoladamente.
- Usar a pontuação por variável (1 ou 2 pontos) sem confirmar a atribuição exata de cada uma contra a Tabela 2 do artigo original — o resumo indexado, verificado nesta sessão, não distingue individualmente qual variável vale 1 e qual vale 2 pontos.
- Extrapolar a validação externa da coorte CardShock (n=137, choque de etiologia mista) como equivalente à validação na população de derivação (choque pós-infarto por ICP) — a área sob a curva caiu de 0,79 para 0,73 entre as duas, sinal de que a discriminação é algo menor fora do cenário original, ainda que clinicamente útil nos dois.
