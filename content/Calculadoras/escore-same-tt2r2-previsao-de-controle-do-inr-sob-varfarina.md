---
title: "Escore SAMe-TT2R2: Previsão da Qualidade do Controle de INR sob Varfarina"
slug: escore-same-tt2r2-previsao-de-controle-do-inr-sob-varfarina
theme: "Calculadoras"
kind: calculadora
review_status: revisado
source_refs: ["Apostolakis S, Sullivan RM, Olshansky B, Lip GYH. Factors affecting quality of anticoagulation control among patients with atrial fibrillation on warfarin: the SAMe-TT2R2 score. Chest. 2013;144(5):1555-1563. DOI: 10.1378/chest.13-0054. PMID: 23669885 — artigo de derivação, coorte do ensaio AFFIRM dividida em derivação e validação interna, com validação externa prospectiva adicional", "van Miert JHA, Bos S, Veeger NJGM, Meijer K. Clinical usefulness of the SAMe-TT2R2 score: A systematic review and simulation meta-analysis. PLoS One. 2018;13(3):e0194208. DOI: 10.1371/journal.pone.0194208. PMID: 29534092 — revisão sistemática e metanálise de 16 estudos, conclui efeito estatisticamente presente mas pequeno demais para uso individual", "Krittayaphong R, Winijkul A, Pirapatdit A, et al; Cool-AF Investigators. SAMe-TT2R2 score for prediction of suboptimal time in therapeutic range in a Thai population with atrial fibrillation. Singapore Med J. 2020;61(12):641-646. DOI: 10.11622/smedj.2019143. PMID: 31680175 — validação externa numa população asiática, 1.669 pacientes, 22 centros na Tailândia"]
legacy_source: "Documento novo, escrito em 02/08/2026. A pasta já cobre a decisão de QUEM anticoagular (CHA2DS2-VA) e o risco de sangramento de quem já anticoagula (HAS-BLED, ORBIT, ATRIA, HEMORR2HAGES), mas nenhum documento respondia a uma pergunta anterior e prática: dado que a decisão de anticoagular já foi tomada, o paciente é bom candidato a varfarina (antagonista de vitamina K) ou o perfil dele sugere de saída um anticoagulante de ação direta? O SAMe-TT2R2 fecha essa lacuna. Os três PMIDs foram lidos por completo (abstract via efetch do PubMed) nesta sessão antes de qualquer número entrar no documento; nenhum dado veio de memória ou de fonte secundária."
---

# Escore SAMe-TT2R2: Previsão da Qualidade do Controle de INR sob Varfarina

## A pergunta que este escore responde
Os demais escores desta pasta relacionados à fibrilação atrial respondem "devo anticoagular?" (CHA2DS2-VA) ou "qual o risco de sangramento de quem já anticoagula?" (HAS-BLED, ORBIT, ATRIA, HEMORR2HAGES, escores ABC). O **SAMe-TT2R2** responde a uma pergunta diferente, e anterior na prática: **se a escolha for varfarina (antagonista de vitamina K, VKA), este paciente tem perfil de manter bom controle de INR — ou o perfil dele prediz controle ruim, o que favoreceria de saída um anticoagulante oral direto (DOAC)?**

A lógica clínica por trás disso: com VKA, o benefício depende diretamente da qualidade do controle — medida pelo **tempo na faixa terapêutica (TTR, time in therapeutic range)** do INR. TTR baixo associa-se a mais eventos tromboembólicos **e** mais sangramento. Identificar antes de começar quem tende a um TTR ruim permite decidir por um DOAC (que não exige monitorização de INR) em vez de expor o paciente a meses de controle instável até essa conclusão ficar evidente na prática.

## Origem do escore
Derivado por Apostolakis et al. (Chest, 2013, PMID 23669885) a partir da população do ensaio **AFFIRM** (Atrial Fibrillation Follow-up Investigation of Rhythm Management), dividida aleatoriamente 1:1 em coorte de derivação e coorte de validação interna, com uma validação externa adicional numa coorte prospectiva independente.

Por regressão linear, nove variáveis emergiram como preditoras independentes do TTR: sexo feminino, idade menor que 50 anos, idade entre 50 e 60 anos, etnia não branca, tabagismo, mais de duas comorbidades, e uso de betabloqueador, verapamil ou (inversamente) amiodarona. Essas variáveis foram condensadas no esquema de pontuação abaixo.

## Componentes e pontuação
O nome é o próprio mnemônico: **S**exo, **A**ge (idade), **Me**dical history (história médica), **T**reatment (tratamento), **T**obacco (tabagismo, dobrado), **R**ace (raça/etnia, dobrado) — daí SAMe-TT2R2, com os subscritos 2 nos dois últimos itens.

| Letra | Variável | Pontos |
|---|---|---|
| **S** | Sexo feminino | 1 |
| **A** | Idade < 60 anos | 1 |
| **Me** | História médica: mais de duas comorbidades (dentre hipertensão, diabetes, doença arterial coronariana/infarto, doença arterial periférica, insuficiência cardíaca, AVC prévio, doença pulmonar, doença hepática ou renal) | 1 |
| **T** | Tratamento com fármaco que interage no controle do INR (ex.: amiodarona para controle de ritmo) | 1 |
| **T2** | Tabagismo (uso atual) | **2** |
| **R2** | Raça/etnia não branca | **2** |

**Pontuação máxima: 8.** O artigo original é explícito ao afirmar que tabagismo e raça "dobram" o peso em relação aos demais itens — é essa a origem do subscrito 2 em cada um, e não um erro de transcrição.

## Interpretação
- **Escore 0-1**: perfil associado a bom controle de INR — o paciente tende a se beneficiar de varfarina, com TTR satisfatório esperado.
- **Escore ≥2**: perfil associado a controle de INR insatisfatório — favorece considerar um DOAC de saída, ou, se a varfarina for mantida (por exemplo, por contraindicação a DOAC como valvopatia reumática moderada a grave ou prótese mecânica), antecipar a necessidade de acompanhamento mais próximo e intervenções para melhorar a adesão.

O desempenho discriminativo relatado no artigo de derivação foi de **índice c 0,72 (IC95% 0,64-0,795)** na validação interna e **0,70 (IC95% 0,57-0,82)** na validação externa — desempenho moderado, não excelente.

## O que a validação subsequente mostra — e por que isso importa mais do que o índice c isolado
Um índice c de 0,70-0,72 já sinaliza discriminação apenas moderada. Duas fontes posteriores, lidas nesta sessão, quantificam a limitação prática disso:

**A revisão sistemática e metanálise de van Miert et al. (PLoS One, 2018, PMID 29534092)** reuniu 16 estudos e testou a capacidade do escore (cortes ≥2 e ≥3) de prever TTR abaixo de 70%. Resultado central: as razões de verossimilhança foram **1,25 (IC95% 1,14-1,38) para escore ≥2** e **1,24 (IC95% 1,09-1,40) para escore ≥3** — positivas, mas próximas de 1, o que os próprios autores traduzem como "a probabilidade pós-teste dificilmente difere da probabilidade prévia (prevalência)". Conclusão literal dos autores: o escore **prediz** TTR baixo, mas **o efeito é pequeno**, e "seu efeito em pacientes individuais é limitado demais para ser clinicamente útil".

**A validação de Krittayaphong et al. numa coorte tailandesa** (Singapore Med J, 2020, PMID 31680175; registro Cool-AF, 1.669 pacientes, 22 centros) encontrou que o SAMe-TT2R2 foi o **único preditor independente** de TTR subótimo (< 65%) em análise multivariada — mas com **índice c de apenas 0,54**, isto é, pouco acima do que se esperaria do acaso (0,50). Os próprios autores concluem que, apesar da significância estatística, "o escore pode ter poder discriminativo limitado".

**Por que a etnia como componente do próprio escore torna esse último achado especialmente relevante:** o SAMe-TT2R2 foi derivado majoritariamente numa população norte-americana (AFFIRM) em que "raça não branca" pontua 2 dos 8 pontos possíveis. Testá-lo numa coorte majoritariamente asiática, onde esse item se comporta de outro modo dentro da própria população de teste, ajuda a explicar por que a discriminação caiu tão acentuadamente fora da população de derivação — é um lembrete de que escore com componente étnico/racial pode não transportar seu desempenho original para outra população.

## Uso pretendido, honestamente descrito
Ler os três estudos juntos, não escolhendo um vencedor entre eles, dá o retrato mais correto: o escore tem base fisiopatológica plausível e associação estatística reproduzida em populações diferentes, mas a **capacidade de prever, no paciente individual, se ele terá bom ou mau controle de INR é modesta** — insuficiente, segundo a metanálise, para ancorar sozinha uma decisão terapêutica. Na prática, o SAMe-TT2R2 funciona melhor como **um dado a mais dentro de uma decisão compartilhada** (junto de preferência do paciente, custo, disponibilidade de DOAC, função renal, necessidade de reversão rápida, valvopatia associada) do que como um corte que, isoladamente, decide entre VKA e DOAC.

## Armadilhas clínicas
- **Tratar escore ≥2 como contraindicação a varfarina.** Não é: é um sinal de que o controle tende a ser mais trabalhoso, não uma exclusão. Em quem tem indicação preferencial de VKA (prótese valvar mecânica, estenose mitral reumática moderada a grave), a varfarina continua sendo a única opção validada, independentemente do escore.
- **Ignorar que o efeito discriminativo é pequeno.** A metanálise de van Miert é explícita: a razão de verossimilhança perto de 1 significa que, para um paciente individual, o escore muda pouco a estimativa de risco de TTR ruim em relação à prevalência de base.
- **Extrapolar o desempenho (índice c ~0,70-0,72) da coorte de derivação para qualquer população.** A validação tailandesa mostrou índice c de apenas 0,54 — quase sem poder discriminativo — na própria população em que um dos componentes do escore (raça/etnia) tem outro significado demográfico.
- **Confundir com HAS-BLED, ORBIT ou os demais escores de sangramento desta pasta.** O SAMe-TT2R2 não estima risco de sangramento nem de AVC — estima a probabilidade de bom controle de INR sob varfarina, uma pergunta anterior e diferente, sobre **qual classe de anticoagulante** escolher, não sobre **se** anticoagular.
- **Aplicar em quem já está estabelecido em varfarina há tempo com TTR conhecido.** O escore foi desenhado para apoiar a escolha **antes** de iniciar o tratamento; para quem já tem histórico de INR, o TTR real medido (por exemplo pelo método de Rosendaal) é informação direta e mais forte do que a predição do escore.

## Fonte
Apostolakis S et al. Chest. 2013;144(5):1555-1563 (derivação, coorte AFFIRM) — PMID 23669885; van Miert JHA et al. PLoS One. 2018;13(3):e0194208 (revisão sistemática e metanálise) — PMID 29534092; Krittayaphong R et al. Singapore Med J. 2020;61(12):641-646 (validação externa, registro Cool-AF, Tailândia) — PMID 31680175. Os três abstracts foram lidos na íntegra via E-utilities do PubMed nesta sessão (02/08/2026) antes da redação; nenhum número foi escrito de memória.
