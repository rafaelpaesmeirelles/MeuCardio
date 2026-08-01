---
title: "Pooled Cohort Equations (ASCVD Risk Estimator) e as Equações PREVENT: Risco Cardiovascular em Prevenção Primária"
slug: pooled-cohort-equations-e-equacoes-prevent-risco-cardiovascular-em-prevencao-primaria
theme: "Calculadoras"
kind: calculadora
review_status: revisado
source_refs: ["Goff DC Jr, Lloyd-Jones DM, Bennett G, Coady S, D'Agostino RB, Gibbons R, et al. 2013 ACC/AHA guideline on the assessment of cardiovascular risk. Circulation. 2014;129(25 Suppl 2):S49-73. DOI: 10.1161/01.cir.0000437741.48606.98. PMID: 24222018 — publicação simultânea em J Am Coll Cardiol. 2014;63(25 Pt B):2935-2959. DOI: 10.1016/j.jacc.2013.11.005. PMID: 24239921. Texto integral conferido via PMC4700825", "Arnett DK, Blumenthal RS, Albert MA, Buroker AB, Goldberger ZD, Hahn EJ, et al. 2019 ACC/AHA Guideline on the Primary Prevention of Cardiovascular Disease. Circulation. 2019;140(11):e596-e646. DOI: 10.1161/CIR.0000000000000678. PMID: 30879355", "Grundy SM, Stone NJ, Bailey AL, Beam C, Birtcher KK, Blumenthal RS, et al. 2018 AHA/ACC/AACVPR/AAPA/ABC/ACPM/ADA/AGS/APhA/ASPC/NLA/PCNA Guideline on the Management of Blood Cholesterol. Circulation. 2019;139(25):e1082-e1143. DOI: 10.1161/CIR.0000000000000625. PMID: 30586774 — texto integral conferido no PMC (PMC7403606)", "DeFilippis AP, Young R, Carrubba CJ, McEvoy JW, Budoff MJ, Blumenthal RS, et al. An analysis of calibration and discrimination among multiple cardiovascular risk scores in a modern multiethnic cohort. Ann Intern Med. 2015;162(4):266-275. DOI: 10.7326/M14-1281. PMID: 25686167 — validação externa na coorte MESA", "Khan SS, Matsushita K, Sang Y, Ballew SH, Grams ME, Surapaneni A, et al. Development and Validation of the American Heart Association's PREVENT Equations. Circulation. 2024;149(6):430-449. DOI: 10.1161/CIRCULATIONAHA.123.067626. PMID: 37947085. Texto integral conferido no PMC (PMC10910659)", "Fontenelle LF et al. Arq Bras Cardiol. 2025;122(6):e20240405. PMID: 40736124 — já citado no documento de Framingham desta mesma pasta"]
legacy_source: "Documento novo, escrito em 01/08/2026, fundindo dois rascunhos independentes produzidos na mesma rodada sobre o mesmo par de ferramentas (PCE + PREVENT), para evitar duas telas quase idênticas. A pasta já tinha Framingham (FRS) e SCORE2/SCORE2-OP (ESC), mas não a família de ferramentas que sustenta as diretrizes americanas de prevenção primária e de colesterol. SYNTAX/SYNTAX II, PESI/sPESI e STS Risk Score já têm documento dedicado nesta pasta."
---

# Pooled Cohort Equations (ASCVD Risk Estimator) e as Equações PREVENT: Risco Cardiovascular em Prevenção Primária

## Duas ferramentas para a mesma pergunta, de origem americana

A pasta já tem o **Framingham Risk Score** (2008, prevê doença coronariana "dura") e o **SCORE2/SCORE2-OP** (ESC, calibrado por região europeia, prevê eventos fatais e não fatais). As **Pooled Cohort Equations (PCE)**, publicadas no **2013 ACC/AHA Guideline on the Assessment of Cardiovascular Risk** (Goff DC Jr et al., Circulation. 2014;129(25 Suppl 2):S49-73, PMID 24222018), são a terceira família — a que sustenta hoje as diretrizes americanas de prevenção primária e de colesterol, popularizada como **ASCVD Risk Estimator Plus** (`tools.acc.org`). Nasceram de uma combinação (*pooling*) de coortes comunitárias americanas contemporâneas: **ARIC, Cardiovascular Health Study, CARDIA e parte do Framingham Original/Offspring**.

A diferença para Framingham não é cosmética: a PCE estima o risco de **primeiro evento ASCVD "duro"** — a fonte é explícita: *"infarto do miocárdio não fatal ou morte por doença coronariana, ou AVC fatal ou não fatal"* — em **10 anos**, para adultos de **40 a 79 anos** sem ASCVD estabelecida, com **quatro equações distintas**, específicas por sexo e raça (homens/mulheres brancos não hispânicos e homens/mulheres afro-americanos) — o Framingham original não fazia essa distinção.

## Variáveis de entrada da PCE
Idade, colesterol total, colesterol HDL, pressão arterial sistólica (com status de tratamento — tratada ou não tratada), diabetes e tabagismo atual — citadas literalmente da fonte. A própria diretriz reconhece que as equações **podem não ser generalizáveis** para grupos raciais/étnicos fora das duas categorias validadas; quem não se enquadra usa a equação de referência (branco), com a incerteza correspondente.

Não entram: HbA1c, proteína C-reativa, história familiar, escore de cálcio coronariano — são **fatores reforçadores de risco**, usados depois de calcular o percentual, não como entrada da equação (ver abaixo).

## Como o número é calculado
Modelo de **risco proporcional (Cox)** específico por sexo e raça, com termos de interação (idade × colesterol total, idade × HDL, idade × PAS tratada/não tratada, idade × tabagismo) — não é soma de pontos como o TIMI ou o HEART. O resultado sai direto como percentual de risco de evento ASCVD em 10 anos.

## Categorias de risco e o limiar de decisão para estatina
As faixas vêm da diretriz de colesterol de 2018 (Grundy et al., PMID 30586774), que usa a saída da PCE como insumo:
- **Baixo risco: < 5%** — ênfase em estilo de vida, estatina geralmente não indicada
- **Risco limítrofe: 5% a < 7,5%** — estatina pode ser considerada se houver fatores reforçadores de risco
- **Risco intermediário: 7,5% a < 20%** — **estatina de intensidade moderada recomendada** (Classe I) se a discussão de opções de tratamento favorecer a terapia
- **Risco alto: ≥ 20%** — **estatina de intensidade alta recomendada**, meta de redução de LDL ≥ 50%

**Texto da diretriz de 2018, citado literalmente**: *"em adultos de 40 a 75 anos sem diabetes mellitus e LDL-C ≥70 mg/dL, com risco ASCVD em 10 anos ≥7,5%, iniciar estatina de intensidade moderada se a discussão de opções de tratamento favorecer a terapia"*. No risco intermediário, a decisão é reforçada — não substituída — por **fatores de intensificação de risco** (*risk-enhancing factors*).

## Fatores reforçadores de risco e escore de cálcio coronariano
Introduzidos pelo **2019 ACC/AHA Guideline on the Primary Prevention of Cardiovascular Disease** (Arnett DK et al., PMID 30879355) para refinar a decisão nas faixas limítrofe e intermediária: história familiar de doença coronariana prematura, LDL persistentemente ≥ 160 mg/dL, síndrome metabólica, doença renal crônica, condições inflamatórias (psoríase, artrite reumatoide, HIV), pré-eclâmpsia ou menopausa precoce, etnia sul-asiática, triglicerídeos persistentemente ≥ 175 mg/dL, PCR-us ≥ 2,0 mg/L, lipoproteína(a) elevada, apoB elevada e índice tornozelo-braço < 0,9.

Quando a decisão permanece incerta, a mesma diretriz autoriza o **escore de cálcio coronariano (Agatston)** como desempate: escore 0 permite **adiar** a estatina na maioria dos pacientes (exceto tabagistas, diabéticos e história familiar muito forte); escore 1-99 favorece iniciar, sobretudo em ≥ 55 anos; escore ≥ 100 ou ≥ percentil 75 favorece fortemente iniciar.

## Desempenho medido — a superestimação sistemática na coorte MESA
DeFilippis AP et al., Ann Intern Med. 2015;162(4):266-275 (PMID 25686167): 4.227 participantes de 50-74 anos, sem diabetes, seguidos por 10,2 anos. A PCE e três escores baseados em Framingham **superestimaram** os eventos observados em **37% a 154% nos homens** e **8% a 67% nas mulheres**. Não é achado isolado — é o motivo pelo qual fatores reforçadores e escore de cálcio foram formalmente incorporados à diretriz de 2018/2019, para reduzir esse excesso de tratamento em casos limítrofes.

## Fonte brasileira: PCE não é calibrada para o Brasil
Fontenelle LF et al., Arq Bras Cardiol. 2025;122(6):e20240405 (PMID 40736124), comparou Framingham, PCE e Globorisk-LAC em 4.416 participantes da PNS 2013: risco mediano em 10 anos de **9,2% (Framingham) vs. 3,6% (PCE) vs. 4,7% (Globorisk-LAC)** — concordância entre PCE e Framingham de apenas 1,8%. Só o Globorisk-LAC foi recalibrado para o Brasil.

## Equações PREVENT (Khan et al., AHA 2024) — a sucessora, ainda não substituindo formalmente a PCE
Publicadas em *Circulation* (PMID 37947085), nasceram de três limitações explícitas da PCE, citadas da fonte: o risco estimado pode não refletir a prevalência contemporânea de fatores de risco; as equações não capturam a carga total de doença cardiovascular (não incluíam insuficiência cardíaca); e podem não ser generalizáveis a grupos fora da derivação original.

**A mudança mais visível: raça deixou de ser variável.** Texto literal da fonte: *"raça e etnia são construtos sociais e, portanto, não foram consideradas como preditoras na modelagem de risco, para eliminar a propagação de algoritmos de risco baseados em raça"*.

**Variáveis do modelo-base**: idade, sexo, PAS, HDL-C, colesterol não-HDL, **eGFR** (entra no modelo-base, não como opcional), tabagismo, uso de anti-hipertensivo ou estatina, diabetes. Três **preditores adicionais opcionais**: UACR, HbA1c e índice de privação social (SDI).

**Alcance maior que o da PCE**: faixa etária de **30 a 79 anos** (vs. 40-79); estima risco em **10 e em 30 anos**; equações separadas para **DCV total** (composto de ASCVD e IC — definida literalmente pela fonte como *"composto de eventos ASCVD e IC fatais e não fatais"*), ASCVD isolada, IC isolada e os componentes de ASCVD em separado.

**Escala da derivação/validação**: **3.281.919 participantes em 25 bases** na derivação e **3.330.085 participantes em 21 bases** na validação — **6.612.004 adultos** ao todo.

**Importante, e a fonte não afirma o contrário**: a diretriz de prevenção primária de 2019 do ACC/AHA, vigente, ainda referencia a PCE. O artigo da PREVENT **não declara** substituição formal — é ferramenta publicada e validada, mas a adoção como padrão de prática ainda depende de diretriz que a incorpore explicitamente.

## Comparação direta

| | Pooled Cohort Equations (2013) | PREVENT (2024) |
|---|---|---|
| Faixa etária | 40-79 anos | 30-79 anos |
| Raça como variável | Sim (branco/afro-americano) | **Não** — removida deliberadamente |
| Horizonte | 10 anos | 10 e 30 anos |
| Desfecho | ASCVD "duro" (IAM não fatal, morte coronariana, AVC) | DCV total (ASCVD + IC), com submodelos separados |
| Variáveis-base | Idade, CT, HDL, PAS, diabetes, tabagismo | Idade, sexo, PAS, HDL, não-HDL, **eGFR**, tabagismo, medicação, diabetes |
| Preditores opcionais | Nenhum | UACR, HbA1c, índice de privação social |

## O que nenhuma das duas faz
- **Não se aplicam a quem já tem ASCVD estabelecida** — nesses pacientes a conduta é prevenção **secundária**, com estatina de alta intensidade independente do percentual
- **Não são a mesma equação usada pela ESC (SCORE2)** — coortes, desfechos e horizontes de calibração diferentes; divergência entre as famílias é esperada, não é erro
- **Não incorporam diabetes tipo 1 de forma diferenciada** (PCE) — apenas como variável binária, sem distinguir tempo de doença nem complicações microvasculares

## Armadilhas clínicas
- **Aplicar a PCE fora de 40-79 anos, ou fora das duas categorias raciais validadas** — a PREVENT resolve isso ao remover raça e ampliar a faixa etária, mas ainda não é a ferramenta formalmente endossada em diretriz vigente
- **Tratar 7,5% como gatilho automático de estatina** — a diretriz de 2018 condiciona a decisão a uma conversa sobre opções de tratamento, e no risco intermediário depende de fatores reforçadores, não só do número bruto
- **Usar qualquer uma das duas em prevenção secundária** — ambas são para **primeira** ocorrência de evento
- **Comparar diretamente o percentual da PCE/PREVENT com o do SCORE2** para o mesmo paciente e tratar a diferença como erro — são desfechos, coortes e horizontes diferentes; não somar ou comparar os percentuais diretamente entre famílias
- **Ignorar a superestimação sistemática documentada na coorte MESA** ao decidir estatina num caso limítrofe — é exatamente o cenário em que os fatores reforçadores existem para ajudar
- **Confundir com o "Reynolds Risk Score"** (citado no mesmo estudo de validação como alternativa com padrão de erro diferente — subestimação em mulheres) — não é o mesmo instrumento
- **Confundir esta frente com PESI/sPESI, Wells ou Genebra** — aqueles estimam prognóstico ou probabilidade de tromboembolismo pulmonar já suspeito/diagnosticado; este documento é sobre risco cardiovascular de primeiro evento em prevenção primária, pergunta clínica inteiramente diferente
