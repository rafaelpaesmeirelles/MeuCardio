---
title: "HCM Risk-SCD: Estratificação de Risco de Morte Súbita na Cardiomiopatia Hipertrófica"
slug: "hcm-risk-scd-escore-de-risco-de-morte-subita-na-cardiomiopatia-hipertrofica"
theme: "Calculadoras"
kind: estudo
review_status: revisado
source_refs: ["O'Mahony C, Jichi F, Pavlou M, et al. A novel clinical risk prediction model for sudden cardiac death in hypertrophic cardiomyopathy (HCM Risk-SCD). Eur Heart J. 2014;35(30):2010-2020. PMID 24126876", "O'Mahony C, Jichi F, Ommen SR, et al. International External Validation Study of the 2014 European Society of Cardiology Guidelines on Sudden Cardiac Death Prevention in Hypertrophic Cardiomyopathy (EVIDENCE-HCM). Circulation. 2018;137(10):1015-1023. PMID 29191938", "O'Mahony C, Akhtar MM, Anastasiou Z, et al. Effectiveness of the 2014 European Society of Cardiology guideline on sudden cardiac death in hypertrophic cardiomyopathy: a systematic review and meta-analysis. Heart. 2019;105(8):623-631. PMID 30366935", "Arbelo E, Protonotarios A, Gimeno JR, et al. 2023 ESC Guidelines for the management of cardiomyopathies. Eur Heart J. 2023;44(37):3503-3626. DOI 10.1093/eurheartj/ehad194. PMID 37622657"]
---

# HCM Risk-SCD: Estratificação de Risco de Morte Súbita na Cardiomiopatia Hipertrófica

## O que é

O HCM Risk-SCD é o modelo de predição de risco de morte súbita cardíaca (MSC) em 5 anos
recomendado pela ESC para orientar a decisão de implante profilático (primário) de
cardiodesfibrilador implantável (CDI) na cardiomiopatia hipertrófica (CMH) em adultos. Ele
substituiu o método anterior de contagem simples de fatores de risco (abordagem binária,
"presente/ausente") por um modelo estatístico multivariado que combina sete variáveis
clínicas contínuas e categóricas em uma estimativa numérica individualizada de risco
(O'Mahony et al., Eur Heart J. 2014;35(30):2010-2020, PMID 24126876).

## Como foi derivado

O modelo foi desenvolvido a partir de uma coorte multicêntrica retrospectiva de **3.675
pacientes** com CMH, acompanhados em 6 centros europeus por um total de **24.313
pacientes-ano** (mediana de acompanhamento de 5,7 anos). Durante o seguimento, **198
pacientes (5%)** morreram subitamente ou tiveram choque apropriado de CDI — o desfecho
combinado usado para construir o modelo. A partir de análise de regressão de riscos
proporcionais de Cox, sete variáveis mostraram associação independente e significativa com
o desfecho, com desempenho discriminativo medido por **índice C de 0,70** (O'Mahony et al.,
Eur Heart J. 2014;35(30):2010-2020, PMID 24126876).

## As sete variáveis do modelo

O índice prognóstico (PI) é calculado somando a contribuição de cada variável, ponderada
pelo respectivo coeficiente de regressão de Cox estimado no estudo de derivação. Os
coeficientes abaixo foram conferidos de forma cruzada em duas fontes independentes que
reproduzem a implementação original do algoritmo (a calculadora offline `doc2do.com/hcm` e
uma síntese técnica publicada de terceiros) — **o texto completo do artigo original está
atrás de paywall na European Heart Journal (Oxford Academic) e não foi acessado
diretamente nesta sessão**; os coeficientes numéricos abaixo, portanto, ficam com
**VERIFICAÇÃO HUMANA NECESSÁRIA** contra o PDF/suplemento original antes de qualquer uso em
ferramenta de cálculo do produto, ainda que as duas fontes secundárias consultadas
concordem exatamente entre si.

| Variável | Coeficiente (β) | Direção do efeito |
|---|---|---|
| Espessura máxima de parede do VE, mm (termo linear) | +0,15939858 | Aumenta o risco |
| Espessura máxima de parede do VE, mm² (termo quadrático) | −0,00294271 | Atenua o efeito linear em espessuras muito altas (relação não linear) |
| Diâmetro do átrio esquerdo, mm | +0,0259082 | Aumenta o risco |
| Gradiente máximo da via de saída do VE (repouso/provocado), mmHg | +0,00446131 | Aumenta o risco |
| História familiar de morte súbita em parente de 1º grau | +0,4583082 (presente) | Aumenta o risco |
| Taquicardia ventricular não sustentada (TVNS) ao Holter | +0,82639195 (presente) | Aumenta o risco — maior peso isolado do modelo |
| Síncope inexplicada (não vasovagal, não neurocardiogênica) | +0,71650361 (presente) | Aumenta o risco |
| Idade na avaliação clínica, anos | −0,01799934 | **Reduz** o risco — quanto mais jovem o paciente, maior o risco estimado, a igualdade dos demais fatores |

A probabilidade de MSC em 5 anos é então obtida por:

```
Probabilidade de MSC em 5 anos = 1 − 0,998^exp(PI)
```

em que PI é a soma ponderada acima. **Nota sobre o formato do escore:** ao contrário de
escores de pontos inteiros somados (como CHA₂DS₂-VASc), o HCM Risk-SCD é um modelo de
regressão contínuo — não existe "pontuação total" arredondada, e o cálculo manual sem
calculadora eletrônica é impraticável. Idade e espessura de parede entram como variáveis
contínuas (não em faixas), e o termo quadrático da espessura de parede reflete que o
excesso de risco por milímetro adicional não é constante ao longo de toda a faixa de
espessura.

## Validação externa: EVIDENCE-HCM

O modelo foi validado prospectivamente numa segunda coorte internacional independente de
**3.703 pacientes**, em estudo publicado 4 anos após a derivação. Resultados de calibração
e discriminação:

- **Índice C de 0,70** (idêntico ao da coorte de derivação) e **estatística D de 1,17**;
- **Inclinação de calibração (calibration slope) de 1,02** — próxima do valor ideal de 1,0,
  indicando que o risco previsto pelo modelo corresponde de perto ao risco observado;
- **73 pacientes (2%) atingiram o desfecho de MSC** dentro de 5 anos de seguimento
  (incidência observada de 5 anos: **2,4%**);
- Incidência observada por categoria de risco previsto: **1,4%** nos pacientes com risco
  previsto **<4%**, e **8,9%** nos pacientes com risco previsto **≥6%**.

(O'Mahony et al., EVIDENCE-HCM, Circulation. 2018;137(10):1015-1023, PMID 29191938.)

## Metanálise de desempenho

Uma revisão sistemática e metanálise subsequente reuniu **7.291 indivíduos** de 6 estudos
para avaliar o desempenho agregado do modelo na prática clínica real. Achados:

- Prevalência combinada do desfecho de MSC em 5 anos: **1,01% no grupo de baixo risco**,
  **2,43% no grupo de risco intermediário** e **8,4% no grupo de alto risco**;
- Do total de 184 eventos de MSC analisados, **68% ocorreram em pacientes com risco
  estimado em 5 anos ≥4%** — ou seja, a maioria dos eventos concentrou-se nas categorias
  intermediária e alta, validando a lógica de estratificação, embora uma minoria relevante
  de eventos (32%) ainda ocorra na faixa classificada como baixo risco.

(O'Mahony et al., Heart. 2019;105(8):623-631, PMID 30366935.)

## Categorias de risco e decisão de CDI (ESC 2023)

A diretriz europeia de cardiomiopatias usa o resultado do HCM Risk-SCD para orientar — não
determinar automaticamente — a indicação de CDI em prevenção primária, sempre dentro de
decisão compartilhada com o paciente:

- **Risco estimado em 5 anos ≥6% (alto risco):** implante de CDI **deve ser considerado**
  (Classe de recomendação IIa, Nível de evidência B);
- **Risco estimado em 5 anos entre 4% e <6% (risco intermediário):** implante de CDI
  **pode ser considerado** (Classe IIb, Nível B);
- **Risco estimado em 5 anos <4% (baixo risco):** CDI profilático não é rotineiramente
  recomendado; na presença de realce tardio extenso (LGE ≥15% da massa do VE) na
  ressonância cardíaca, o implante **pode ser considerado** em decisão compartilhada
  (Classe IIb, Nível B) — a extensão de fibrose por LGE não faz parte das sete variáveis do
  modelo original e funciona como reclassificador adicional nessa faixa;
- **Prevenção secundária** (sobrevivente de parada cardíaca por taquicardia/fibrilação
  ventricular, ou TV sustentada com comprometimento hemodinâmico): CDI **é recomendado**
  independentemente do escore (Classe I, Nível B) — o HCM Risk-SCD não se aplica a essa
  população, que já tem indicação estabelecida por outro critério.

O cálculo do risco em 5 anos deve ser feito na avaliação inicial e **reavaliado a cada
1-2 anos**, ou sempre que houver mudança no quadro clínico, porque as sete variáveis podem
mudar ao longo do seguimento (nova síncope, TVNS incidental ao Holter, progressão da
espessura de parede ou do gradiente).

(Arbelo E, Protonotarios A, Gimeno JR, et al. 2023 ESC Guidelines for the management of
cardiomyopathies. Eur Heart J. 2023;44(37):3503-3626, PMID 37622657.)

## Limitações conhecidas do escore

- **Validação restrita a adultos, ≥16 anos.** O modelo não deve ser usado em crianças e
  adolescentes menores de 16 anos — para essa faixa etária, a diretriz recomenda modelos
  pediátricos validados especificamente (ex.: HCM Risk-Kids), que usam variáveis e pesos
  diferentes;
- **Não validado em atletas de elite/competitivos** — o efeito do condicionamento físico
  intenso sobre as variáveis do modelo (em especial espessura de parede) não foi
  incorporado à coorte de derivação;
- **Não se aplica a CMH secundária a doenças metabólicas de depósito (ex.: doença de
  Fabry) ou síndromes genéticas (ex.: síndrome de Noonan)** — fenocópias com fisiopatologia
  distinta da CMH sarcomérica que compôs a coorte original;
- **Não se aplica a pacientes já com indicação de CDI por prevenção secundária** (parada
  cardíaca abortada, TV sustentada com instabilidade hemodinâmica) — nesses casos o CDI é
  indicado independentemente do escore;
- **Cautela na interpretação após miectomia septal ou ablação septal alcoólica** — os
  procedimentos de redução septal alteram diretamente duas das sete variáveis (espessura de
  parede e gradiente da via de saída), e o desempenho do modelo pós-procedimento não é o
  mesmo da coorte de derivação, composta majoritariamente por pacientes não submetidos a
  esses procedimentos;
- **Índice C de 0,70 é discriminação moderada, não excelente** — em ambas as coortes
  (derivação e validação externa), o modelo erra a classificação de risco em uma fração
  não desprezível de pacientes; a metanálise mostra que quase um terço dos eventos de MSC
  ocorre em pacientes classificados como baixo risco, o que a ESC reconhece ao permitir a
  reclassificação por LGE extenso mesmo abaixo do corte de 4%;
- **O escore não substitui julgamento clínico nem decisão compartilhada** — os próprios
  documentos de validação e a diretriz da ESC enquadram o resultado numérico como um dos
  insumos da decisão, não como critério automático de indicação ou contraindicação de CDI.

## Síntese

| Item | Valor |
|---|---|
| Variáveis do modelo | 7 (idade, espessura máxima de parede, diâmetro de átrio esquerdo, gradiente de VSVE, história familiar de MSC, TVNS, síncope inexplicada) |
| Desfecho previsto | Risco de morte súbita cardíaca ou choque apropriado de CDI em 5 anos |
| Índice C (derivação e validação externa) | 0,70 nas duas coortes |
| Corte de baixo risco | <4% em 5 anos |
| Corte de risco intermediário | 4% a <6% em 5 anos |
| Corte de alto risco | ≥6% em 5 anos |
| População validada | Adultos ≥16 anos com CMH sarcomérica, sem indicação prévia de CDI por prevenção secundária |
