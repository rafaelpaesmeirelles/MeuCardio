---
title: "RACHS-1: Ajuste de Risco para Cirurgia de Cardiopatia Congênita"
slug: rachs-1-ajuste-de-risco-para-cirurgia-de-cardiopatia-congenita
theme: "Calculadoras"
kind: calculadora
review_status: revisado
source_refs: ["Jenkins KJ, Gauvreau K, Newburger JW, Spray TL, Moller JH, Iezzoni LI. Consensus-based method for risk adjustment for surgery for congenital heart disease. J Thorac Cardiovasc Surg. 2002;123(1):110-118. DOI: 10.1067/mtc.2002.119064. PMID: 11782764 — artigo de derivação do método RACHS-1 (Risk Adjustment for Congenital Heart Surgery), abstract completo obtido verbatim nesta sessão via PubMed E-utilities (esearch por autor Jenkins KJ + termos do título 'congenital heart disease' e 'risk adjustment', depois efetch em texto puro do PMID confirmado)."]
legacy_source: "Documento novo, escrito nesta sessão (09/09/2026). A pasta Calculadoras já cobre escores de risco cirúrgico cardíaco em adultos (EuroSCORE II, STS Risk Score, ACEF, VSG-CRI) e o conteúdo pediátrico (pasta Cardiologia_pediátrica) já descreve dezenas de cardiopatias congênitas individuais e sua estratégia cirúrgica — mas nenhum documento existente descrevia um instrumento de ajuste de risco que permita comparar mortalidade cirúrgica ENTRE diferentes lesões congênitas e entre centros, que é exatamente o objeto do RACHS-1. Checagem de colisão feita em content/**/*.md, não só nos JSONs: busca por 'RACHS' (zero resultados), 'Aristotle' (presente apenas como o ensaio ARISTOTLE de apixabana em FA, sem relação), 'Zwolle' (presente apenas como o ensaio Zwolle de angioplastia primária, sem relação) — nenhuma colisão real encontrada. Verificado via PubMed E-utilities nesta sessão (esearch + efetch de texto puro do abstract, PMID confirmado diretamente no registro, não por fonte secundária)."
---

# RACHS-1: Ajuste de Risco para Cirurgia de Cardiopatia Congênita

## O que é e o problema que resolve
Comparar a mortalidade cirúrgica entre centros ou entre séries de casos de cardiopatia congênita é enganoso se não se ajustar para a complexidade da lesão operada: um centro que opera predominantemente comunicações interatriais simples terá mortalidade muito menor do que um centro que concentra procedimentos de Norwood ou Fontan, sem que isso reflita qualidade assistencial. Jenkins KJ et al., *Journal of Thoracic and Cardiovascular Surgery* 2002;123(1):110-118 (PMID 11782764), desenvolveram o **RACHS-1** (*Risk Adjustment for Congenital Heart Surgery*) exatamente para essa lacuna: um método de ajuste de risco para **mortalidade intra-hospitalar em crianças menores de 18 anos submetidas a cirurgia de cardiopatia congênita**, citado literalmente do objetivo do artigo.

## Como foi derivado
Citado literalmente do resumo (métodos):
- Um **painel nacional de 11 membros** — cardiologistas pediátricos e cirurgiões cardíacos — usou **julgamento clínico** para classificar procedimentos cirúrgicos em **seis categorias de risco**;
- As categorias foram **refinadas após revisão de dados** do *Pediatric Cardiac Care Consortium* (PCCC) e de **três bancos de dados estaduais de alta hospitalar**;
- O efeito de incluir variáveis clínicas adicionais foi explorado comparando **áreas sob curvas ROC** (valores numéricos exatos não constam no resumo indexado — ver seção "O que este documento NÃO reproduz");
- Ou seja: **o RACHS-1 não nasceu de uma regressão multivariável tradicional sobre uma coorte única**, como a maioria dos escores desta pasta (GRACE, TIMI, EuroSCORE II) — é um método de **consenso de especialistas**, posteriormente testado empiricamente contra dados observacionais reais.

## As populações testadas e a alocação em categorias
Citado literalmente do resumo (resultados):
- **4.602 pacientes cirúrgicos** no banco de dados do Pediatric Cardiac Care Consortium e **4.493 pacientes** nos bancos de dados estaduais de alta hospitalar;
- **3.767 (81,9%)** e **3.832 (85,3%)**, respectivamente, tinham um **único procedimento cardíaco**;
- **98,5%** (PCCC) e **89,2%** (alta hospitalar) dos pacientes puderam ser **alocados em uma das seis categorias de risco** definidas pelo painel;
- Quando havia **múltiplos procedimentos** no mesmo paciente, o **melhor desempenho** foi obtido alocando o caso na categoria de risco do **procedimento mais complexo**.

## Mortalidade por categoria de risco
Citado literalmente do resumo, dados do banco Pediatric Cardiac Care Consortium:

| Categoria de risco | Mortalidade intra-hospitalar |
|---|---|
| 1 | 0,4% |
| 2 | 3,8% |
| 3 | 8,5% |
| 4 | 19,4% |
| 5 | **casos insuficientes para estimar** (citado literalmente: "too few cases in category 5 to estimate mortality rates") |
| 6 | 47,7% |

- Tendência de aumento de mortalidade entre categorias: **p < 0,001**;
- As taxas foram **semelhantes** nos bancos de dados de alta hospitalar (valores exatos por categoria nessa segunda coorte não constam no resumo indexado).

## Variáveis que refinam a predição além da categoria basal
Em modelos multivariáveis, três fatores **adicionaram** poder preditivo de óbito intra-hospitalar além da categoria de risco isolada, citados literalmente do resumo:
- **Idade mais jovem**;
- **Prematuridade**;
- **Presença de anomalia estrutural extracardíaca maior**.

## O que este documento NÃO reproduz
- **A tabela completa de alocação procedimento-por-categoria** (qual procedimento cirúrgico específico cai em qual das seis categorias) **não está reproduzida no resumo indexado** consultado nesta sessão — essa tabela existe no texto integral do artigo original (e em publicações posteriores do grupo). **VERIFICAÇÃO HUMANA NECESSÁRIA**: para classificar um procedimento real, consulte a tabela completa no texto integral (Jenkins KJ et al., J Thorac Cardiovasc Surg 2002;123(1):110-118) ou uma calculadora institucional validada — não infira a categoria por analogia a partir deste resumo.
- **Os valores numéricos exatos das áreas sob a curva ROC** comparando os modelos com e sem as variáveis adicionais (idade, prematuridade, anomalia extracardíaca) **não constam no resumo indexado** — o resumo menciona o método de comparação, mas não os coeficientes. **VERIFICAÇÃO HUMANA NECESSÁRIA** antes de citar um c-estatístico específico para o RACHS-1.
- **As taxas de mortalidade por categoria no segundo banco de dados** (bancos estaduais de alta hospitalar) não são reproduzidas numericamente — o resumo afirma apenas que foram "semelhantes" às do PCCC.
- Este documento **não é sobre uma lesão congênita específica** — é sobre o instrumento de ajuste de risco que permite comparar mortalidade entre lesões e entre centros; a fisiopatologia, o diagnóstico e a estratégia cirúrgica de cada cardiopatia congênita já estão descritos em documentos próprios desta base (ver "Tudo com Tudo").

## Leitura clínica e armadilhas
- **RACHS-1 não é um escore de decisão à beira do leito** para um paciente individual — é um instrumento de **ajuste de risco populacional/administrativo**, usado principalmente para comparar desfechos entre centros, auditorias de qualidade e pesquisa observacional em cardiopatia congênita, análogo em finalidade ao papel que o EuroSCORE II e o STS Risk Score cumprem na cirurgia cardíaca do adulto — mas derivado por **consenso de especialistas sobre a complexidade do procedimento**, não por regressão sobre variáveis do paciente coletadas prospectivamente.
- **Não confundir com escore de complexidade anatômica pontuado (tipo Aristotle Basic Complexity Score)**: o RACHS-1 aloca cada procedimento em uma de seis categorias ordinais definidas por consenso; não atribui pontos aditivos por componente anatômico. Uma busca dirigida nesta sessão não localizou, nesta base de conteúdo, nenhum documento sobre escores de complexidade anatômica alternativos — se outro escore desse tipo for adicionado no futuro, esta distinção deve ser explicitada.
- **Categoria de risco isolada não substitui julgamento clínico individual**: os próprios autores identificam que idade jovem, prematuridade e anomalia extracardíaca maior modificam o risco além da categoria — um recém-nascido prematuro com anomalia extracardíaca associada, mesmo em categoria RACHS-1 baixa, pode ter risco real mais alto do que a categoria sozinha sugere.
- **A categoria 5 tem dados insuficientes** para estimativa confiável de mortalidade nesta publicação original — não extrapole uma taxa para essa categoria a partir das categorias vizinhas.

## Síntese

| Item | Valor |
|---|---|
| Nome | RACHS-1 (Risk Adjustment for Congenital Heart Surgery) |
| Método de derivação | Consenso de painel de 11 especialistas (cardiologistas pediátricos e cirurgiões cardíacos), refinado com dados observacionais |
| Categorias | 6 (ordinais, por complexidade do procedimento) |
| População testada 1 | Pediatric Cardiac Care Consortium, n = 4.602 |
| População testada 2 | 3 bancos estaduais de alta hospitalar, n = 4.493 |
| % alocável em categoria | 98,5% (PCCC) / 89,2% (alta hospitalar) |
| Mortalidade por categoria (PCCC) | Cat 1: 0,4% / Cat 2: 3,8% / Cat 3: 8,5% / Cat 4: 19,4% / Cat 5: dados insuficientes / Cat 6: 47,7% |
| Significância da tendência | p < 0,001 |
| Modificadores de risco além da categoria | Idade jovem, prematuridade, anomalia extracardíaca estrutural maior |
| Regra para múltiplos procedimentos | Alocar pela categoria do procedimento mais complexo |
| Uso pretendido | Ajuste de risco para comparação de mortalidade entre centros/coortes, não decisão individual à beira do leito |

## Tudo com Tudo

- [EuroSCORE II: Risco de Mortalidade em Cirurgia Cardíaca](/biblioteca/euroscore-ii-risco-de-mortalidade-em-cirurgia-cardiaca) — instrumento análogo de ajuste de risco cirúrgico, mas derivado e validado em população adulta
- [Escore STS: Cortes de Risco e a Decisão do Heart Team entre TAVI e Cirurgia](/biblioteca/escore-sts-cortes-de-risco-e-a-decisao-do-heart-team-entre-tavi-e-cirurgia) — outro modelo de risco cirúrgico cardíaco de referência, também de população adulta
- [Fluxograma: Qual Escore de Risco Cirúrgico Usar em Cada Cenário Perioperatório](/biblioteca/fluxograma-escolha-escore-risco-cirurgico-perioperatorio) — panorama dos escores de risco cirúrgico já cobertos nesta pasta, nenhum deles pediátrico até este documento
- [CIV e CIA na Criança: História Natural e Critérios de Fechamento](/biblioteca/civ-e-cia-na-crianca-historia-natural-e-criterios-de-fechamento) — exemplo de lesões tipicamente associadas às categorias RACHS-1 mais baixas
- [Defeito do Septo Atrioventricular na Síndrome de Down: Classificação, Hipertensão Pulmonar Precoce e Timing Cirúrgico](/biblioteca/defeito-do-septo-atrioventricular-na-sindrome-de-down-classificacao-hipertensao-pulmonar-precoce-e-timing-cirurgico) — exemplo de lesão de complexidade cirúrgica intermediária
- [Descompensação Aguda da Circulação de Fontan](/biblioteca/descompensacao-aguda-da-circulacao-de-fontan) — a via unica final de um percurso cirúrgico estagiado tipicamente classificado nas categorias RACHS-1 mais altas
- [Atresia Pulmonar: Anatomia, Dependência Coronariana e Estratégia Cirúrgica](/biblioteca/atresia-pulmonar-anatomia-dependencia-coronariana-e-estrategia-cirurgica) — exemplo de lesão complexa e heterogênea cuja categoria RACHS-1 depende da estratégia cirúrgica escolhida
