---
title: "Farmacogenômica da Varfarina: Algoritmos de Dose por CYP2C9 e VKORC1"
slug: farmacogenomica-da-varfarina-algoritmos-de-dose-por-cyp2c9-e-vkorc1
theme: "Farmacologia"
kind: estudo
review_status: revisado
source_refs: ["International Warfarin Pharmacogenetics Consortium; Klein TE, Altman RB, Eriksson N, Gage BF, Kimmel SE, Lee MT, et al. Estimation of the Warfarin Dose with Clinical and Pharmacogenetic Data. N Engl J Med. 2009;360(8):753-764. DOI: 10.1056/NEJMoa0809329. PMID: 19228618 — ensaio/algoritmo IWPC, coorte de derivação 4.043 + validação 1.009 pacientes. Erratum publicado em N Engl J Med. 2009;361(16):1613 ('Dosage error in article text') — erratum não lido nesta redação, declarado aqui", "Pirmohamed M, Burnside G, Eriksson N, Jorgensen AL, Toh CH, Nicholson T, et al; EU-PACT Group. A Randomized Trial of Genotype-Guided Dosing of Warfarin. N Engl J Med. 2013;369(24):2294-2303. DOI: 10.1056/NEJMoa1311386. PMID: 24251363 — ensaio EU-PACT, 455 pacientes", "Kimmel SE, French B, Kasner SE, Johnson JA, Anderson JL, Gage BF, et al; COAG Investigators. A Pharmacogenetic versus a Clinical Algorithm for Warfarin Dosing. N Engl J Med. 2013;369(24):2283-2293. DOI: 10.1056/NEJMoa1310669. PMID: 24251361. PMCID: PMC3942158 — ensaio COAG, 1.015 pacientes", "Johnson JA, Caudle KE, Gong L, Whirl-Carrillo M, Stein CM, Scott SA, et al. Clinical Pharmacogenetics Implementation Consortium (CPIC) Guideline for Pharmacogenetics-Guided Warfarin Dosing: 2017 Update. Clin Pharmacol Ther. 2017;102(3):397-404. DOI: 10.1002/cpt.668. PMID: 28198005. PMCID: PMC5546947 — texto integral lido no PMC para as recomendações práticas por genótipo e ancestralidade"]
legacy_source: "Documento novo, escrito em 01/08/2026. O verbete varfarina-sodica.md já cita VKORC1 e CYP2C9 em uma frase na seção de farmacogenética, mas não há na base nenhum documento sobre os ensaios que testaram a dosagem guiada por genótipo na prática, nem sobre o algoritmo que os softwares de apoio de fato usam. É a mesma lacuna que o documento de farmacogenômica do clopidogrel já preencheu para o CYP2C19 — aqui o caso é mais delicado, porque os dois maiores ensaios randomizados (EU-PACT e COAG) chegaram a conclusões opostas."
---

# Farmacogenômica da Varfarina: Algoritmos de Dose por CYP2C9 e VKORC1

## Por que essa pergunta chega ao consultório
A varfarina tem a maior variabilidade de dose terapêutica entre os fármacos de uso comum em cardiologia — a faixa observada na prática vai de menos de 1 mg/dia a mais de 15 mg/dia para o mesmo INR-alvo de 2 a 3. Boa parte dessa variação tem explicação genética, concentrada em dois genes: **VKORC1**, que codifica o alvo farmacológico da varfarina (a enzima vitamina K epóxido redutase), e **CYP2C9**, a principal enzima que metaboliza o enantiômero S da varfarina, mais potente que o R.

A pergunta prática não é apenas "existe associação genética" — isso já era conhecido havia mais de uma década —, e sim **se genotipar antes de prescrever muda algum desfecho que importa**: tempo até a faixa terapêutica, risco de INR supraterapêutico, sangramento. É exatamente essa pergunta que os ensaios clínicos randomizados abaixo tentaram responder, com resultados que **não convergem**.

## O gene, os alelos e o algoritmo que os une
**VKORC1**: o polimorfismo mais estudado é o **-1639G>A** (também referido como VKORC1*2, ou o SNP rs9923231). O alelo A está associado a menor expressão da enzima-alvo e, portanto, **maior sensibilidade à varfarina** — pacientes com genótipo A/A precisam de doses mais baixas para o mesmo efeito anticoagulante que pacientes G/G.

**CYP2C9**: os alelos de perda de função mais estudados são **CYP2C9*2** e **CYP2C9*3**, mais comuns em populações de ascendência europeia. Portadores desses alelos metabolizam a varfarina mais lentamente, acumulam o fármaco e precisam de **doses menores** — o risco associado não é falta de eficácia, e sim **excesso de anticoagulação e sangramento** durante a fase de indução, antes de a dose ser ajustada pelo INR.

Além desses dois genes centrais, o guideline CPIC 2017 (Johnson et al., PMID 28198005) incorpora dois achados mais recentes, com recomendação de uso restrita por ancestralidade:
- **CYP4F2 (rs2108622, também chamado *3)**: metanálises citadas na diretriz mostram um efeito estatisticamente significativo, porém **modesto** — cerca de 8-11% de dose mais alta em portadores do alelo A, em população de ascendência não africana. A recomendação de ajuste (aumentar a dose calculada em 5-10% quando o *3 é detectado) é **opcional**, e a diretriz explicita que **não faz recomendação de uso desse marcador em pacientes negros**.
- **rs12777823**: variante identificada por estudo de associação genômica ampla especificamente em afrodescendentes (a maioria de ancestralidade da África Ocidental), associada a necessidade de dose **menor** — a diretriz cita reduções de aproximadamente 7 a 9 mg/semana em heterozigotos e homozigotos para o alelo A frente aos não portadores.
- **CYP2C9\*5, \*6, \*8 e \*11**: alelos de perda de função praticamente restritos a populações de ascendência africana ("alelos africano-específicos"). Quando não testados, a diretriz é explícita: **dosar clinicamente**, sem tentar extrapolar a partir de *2/*3 (que são raros nessa população e não capturam o efeito). Quando testados, a orientação é reduzir a dose calculada em 15-30% por alelo variante, com redução maior (20-40%) em homozigotos.

**O algoritmo, na prática, não é uma tabela fixa de redução percentual por genótipo** — os dois algoritmos validados (o do consórcio IWPC e o de Gage, disponíveis publicamente em calculadoras como o `warfarindosing.org`) combinam **idade, sexo, peso, altura, indicação, INR-alvo, tabagismo, uso de fármacos interativos (amiodarona, indutores enzimáticos) e genótipo** numa única equação, produzindo uma dose diária estimada com uma casa decimal. É esse tipo de ferramenta que os três ensaios abaixo testaram contra a prática convencional.

## O ensaio que derivou o algoritmo: IWPC (Klein et al., NEJM 2009, PMID 19228618)
O International Warfarin Pharmacogenetics Consortium reuniu dados clínicos e genéticos de **4.043 pacientes** de múltiplos centros para **derivar** um algoritmo de dose combinando variáveis clínicas e genéticas, e validou-o numa coorte independente de **1.009 pacientes**.

- Na coorte de validação, o algoritmo farmacogenético identificou corretamente uma proporção maior de pacientes que precisavam de **doses extremas** — **≤21 mg/semana**: 49,4% (farmacogenético) vs. 33,3% (clínico), p<0,001; **≥49 mg/semana**: 24,8% vs. 7,2%, p<0,001 — do que o algoritmo baseado só em variáveis clínicas.
- **O maior ganho do algoritmo genético concentra-se exatamente nos extremos de dose** (46,2% da população do estudo precisava de ≤21 ou ≥49 mg/semana) — é nesses pacientes que uma dose-padrão fixa (por exemplo, 5 mg/dia) mais frequentemente erra por excesso ou por falta.
- **Nota de erratum, declarada e não lida nesta redação**: há uma errata publicada em outubro de 2009 (N Engl J Med. 2009;361(16):1613, "Dosage error in article text") sobre erro de dosagem no texto do artigo original — quem for citar valores específicos de dose do artigo de 2009 deve conferir a errata antes.

Este estudo **não testou desfecho clínico** (sangramento, tempo em faixa terapêutica) — foi um estudo de **acurácia preditiva de dose**, e é o algoritmo que os dois ensaios seguintes testaram na prática.

## Os dois ensaios que testaram a estratégia na prática — com resultados opostos

### EU-PACT (Pirmohamed et al., NEJM 2013, PMID 24251363) — positivo
Ensaio randomizado, multicêntrico, europeu, em **455 pacientes** com fibrilação atrial ou tromboembolismo venoso iniciando varfarina. Genotipagem para **CYP2C9\*2, CYP2C9\*3 e VKORC1 (-1639G→A)** feita por teste rápido à beira do leito (point-of-care). No grupo guiado por genótipo, a dose dos primeiros 5 dias seguiu algoritmo farmacogenético; no grupo controle, esquema de dose de ataque de 3 dias sem informação genética.

- **Desfecho primário — percentual de tempo na faixa terapêutica de INR (2,0-3,0) nas primeiras 12 semanas**: **67,4% no grupo guiado por genótipo vs. 60,3% no grupo controle** — diferença ajustada de 7,0 pontos percentuais (IC95% 3,3-10,6; p<0,001).
- **Menos episódios de anticoagulação excessiva** (INR ≥4,0) no grupo guiado por genótipo.
- **Tempo até atingir INR terapêutico**: mediana de **21 dias** no grupo guiado por genótipo vs. **29 dias** no grupo controle (p<0,001).

### COAG (Kimmel et al., NEJM 2013, PMID 24251361) — neutro
Ensaio randomizado, americano, em **1.015 pacientes**, com desenho duplo-cego para a dose (pacientes e médicos não sabiam a dose administrada nas primeiras 4 semanas). Comparou um algoritmo com dados clínicos **e** genótipo contra um algoritmo só com dados clínicos, ambos usados para guiar a dose dos primeiros 5 dias.

- **Desfecho primário — percentual de tempo na faixa terapêutica em 4 semanas**: **45,2% no grupo guiado por genótipo vs. 45,4% no grupo guiado clinicamente** — diferença ajustada de -0,2 ponto percentual (IC95% -3,4 a 3,1; p=0,91). **Sem diferença.**
- **Sem diferença mesmo no subgrupo com maior discrepância de dose prevista** entre os dois algoritmos (≥1 mg/dia).
- **Interação significativa entre estratégia e raça** (p=0,003): em pacientes negros, o percentual de tempo em faixa terapêutica foi **menor** no grupo guiado por genótipo do que no grupo guiado clinicamente.
- Sem diferença significativa no desfecho combinado de INR ≥4, sangramento maior ou tromboembolismo.

**Por que os dois ensaios discordam, e o que isso ensina sobre ler farmacogenômica com ceticismo:**
1. **Composição racial diferente.** O COAG incluiu proporção maior de pacientes negros, população em que **CYP2C9\*2 e \*3 são raros** e a variabilidade genética relevante está em alelos que o algoritmo do COAG não testava (\*5, \*6, \*8, \*11, rs12777823) — um algoritmo "guiado por genótipo" que não testa a variante genética relevante para aquele paciente equivale, na prática, a não genotipar.
2. **Desenho de comparação diferente.** O EU-PACT comparou o algoritmo genético contra um esquema de dose de ataque fixo de 3 dias (mais rígido); o COAG comparou dois algoritmos, ambos já sofisticados e ajustados por variáveis clínicas — a régua de comparação do COAG era mais difícil de superar.
3. **Desfecho e janela temporal diferentes.** O COAG mediu tempo em faixa terapêutica a partir do dia 4-5 até o dia 28; o EU-PACT mediu ao longo de 12 semanas, incluindo o período de maior instabilidade inicial, onde o efeito da informação genética é teoricamente maior.
**A leitura honesta não é "um ensaio está certo e o outro errado" — é que o benefício da genotipagem parece depender de que alelo se testa e em qual população**, e essa é exatamente a lição que a diretriz CPIC 2017 incorporou ao diferenciar recomendações por ancestralidade.

## O que a diretriz CPIC 2017 recomenda, na prática
A CPIC (Johnson et al., 2017, atualização da diretriz de 2011) recomenda, quando o genótipo já está disponível:

- **Usar um algoritmo farmacogenético validado publicamente** (os do IWPC ou de Gage, disponíveis em calculadoras como `warfarindosing.org`) para estimar a dose diária estável — **não uma tabela fixa de redução percentual por genótipo isolado**.
- **CYP2C9\*2/\*3 e VKORC1 -1639G>A**: entram diretamente como variáveis do algoritmo, junto com idade, peso, altura, indicação, INR-alvo, tabagismo e fármacos interativos.
- **CYP2C9\*5, \*6, \*8, \*11** (predominantemente em ascendência africana): se não testados, a orientação é **dosar clinicamente** — não extrapolar a partir de \*2/\*3. Se testados, reduzir a dose calculada em 15-30% por alelo variante (20-40% em homozigotos).
- **rs12777823** (predominantemente em ascendência africana): reduções de dose da ordem de 10-25% em heterozigotos/homozigotos para o alelo A, com magnitude descrita na diretriz na faixa de 7 a 9 mg/semana a menos frente a não portadores.
- **CYP4F2 (rs2108622/\*3)**: ajuste **opcional**, de +5-10% na dose calculada, só em população de ascendência não africana — a diretriz não recomenda seu uso em pacientes negros.
- **Pediatria**: para crianças de ascendência europeia com CYP2C9\*2/\*3 e VKORC1 -1639G>A disponíveis, a diretriz recomenda uso de algoritmo farmacogenético pediátrico validado (por exemplo, os de Hamberg et al. e Biss et al.). Nenhum estudo pediátrico incluiu genotipagem de CYP2C9\*5, \*6, \*8 ou \*11, e não há recomendação equivalente para outras ancestralidades pediátricas.

## Limites e armadilhas clínicas
- **Genotipagem não substitui a monitorização do INR.** Mesmo no EU-PACT, que foi positivo, a genotipagem melhorou o percentual de tempo em faixa terapêutica — não eliminou a necessidade de ajuste subsequente por INR seriado.
- **"Guiado por genótipo" só funciona se o painel testar o alelo relevante para aquele paciente.** O contraste EU-PACT/COAG mostra isso de forma direta: testar \*2/\*3 numa população em que a variabilidade relevante está em alelos africano-específicos ou no rs12777823 é testar a variante errada.
- **O ganho absoluto de tempo em faixa terapêutica (7 pontos percentuais no EU-PACT) é real, mas modesto**, e nenhum dos dois ensaios teve poder estatístico para desfechos clínicos duros (sangramento maior, tromboembolismo) como desfecho primário — os números de segurança citados são, em ambos, desfechos secundários ou exploratórios.
- **Sociedades de cardiologia não recomendam genotipagem rotineira antes de iniciar varfarina** — a evidência disponível justifica o uso do teste farmacogenético quando já disponível ou em populações/contextos específicos, não uma política de testagem universal.
- **O teste de ponto de cuidado usado no EU-PACT não está amplamente disponível** — a maioria dos serviços depende de laboratório central, com tempo de retorno que pode ultrapassar a janela de decisão dos primeiros 3-5 dias de dose, esvaziando parte do benefício demonstrado no ensaio.
- **A vitamina K, dieta, interações medicamentosas (amiodarona, indutores enzimáticos) e adesão continuam sendo determinantes maiores da instabilidade do INR no dia a dia** do que a variação genética isolada — o algoritmo entra como uma estimativa inicial mais precisa, não como substituto do acompanhamento clínico.
