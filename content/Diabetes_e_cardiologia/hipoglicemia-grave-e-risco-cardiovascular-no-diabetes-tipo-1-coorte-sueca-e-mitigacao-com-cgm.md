---
title: "Hipoglicemia Grave e Risco Cardiovascular no Diabetes Tipo 1: Coorte Sueca e Mitigação com CGM Intermitente (Eeg-Olofsson et al., Diabetologia 2025)"
slug: hipoglicemia-grave-e-risco-cardiovascular-no-diabetes-tipo-1-coorte-sueca-e-mitigacao-com-cgm
theme: "Diabetes e cardiologia"
kind: estudo
review_status: revisado
source_refs: ["Eeg-Olofsson K, Nathanson D, Spelman T, Kyhlstedt M, Seibold A, Levrat-Guillen F, Bolinder J. Severe hypoglycaemia is associated with increased risk of adverse cardiovascular complications in adults with type 1 diabetes: risk mitigation using intermittently scanned continuous glucose monitoring. Diabetologia. 2025;68(8):1647-1656. Epub 2025 Apr 24. DOI: 10.1007/s00125-025-06438-y. PMID: 40272529. PMCID: PMC12245946. Texto completo (Springer/Diabetologia, acesso aberto) conferido via PubMed E-utilities (esearch/esummary/efetch, db=pubmed e db=pmc) em 09/09/2026."]
legacy_source: "Documento novo, escrito em 09/09/2026. A pasta ja tem um documento mecanistico sobre hipoglicemia, arritmia e neuropatia autonomica cardiaca (protocolo, sem coorte quantitativa dedicada de desfecho cardiovascular apos hipoglicemia grave) e, do mesmo dia, um documento sobre CGM e desfechos cardiovasculares/mortalidade numa coorte coreana de diabetes tipo 1 (Kim et al., Diabetologia 2026, PMID 41865177) — mas nenhum documento cobria especificamente a quantificacao do risco cardiovascular apos evento de hipoglicemia grave nem a comparacao de mitigacao desse risco por tecnologia de monitorizacao (isCGM vs. automonitorizacao capilar). Buscado por grep em todo o content/Diabetes_e_cardiologia por Eeg-Olofsson, 40272529, isCGM, intermittently scanned: nenhum resultado antes deste documento. Candidato tambem verificado e descartado por ja estar coberto: orforglipron (ja documentado em orforglipron-primeiro-agonista-oral-de-glp-1-nao-peptidico-o-programa-achieve.md), retatrutida/TRANSCEND-T2D-1, GLP-1 em diabetes tipo 1 e CGM/mortalidade em diabetes tipo 1 (documento do mesmo dia, PMID diferente, coorte coreana, sem sobreposicao de PMID ou de pergunta clinica com este)."
---

# Hipoglicemia Grave e Risco Cardiovascular no Diabetes Tipo 1: Coorte Sueca e Mitigação com CGM Intermitente

## Pergunta clínica
A pasta já tem um documento mecanístico sobre por que a hipoglicemia pode causar arritmia (prolongamento de QT, ativação simpatoadrenal, síndrome "dead-in-bed") e um documento sobre CGM e desfechos duros numa coorte coreana de diabetes tipo 1. Faltava uma resposta quantitativa e direta a duas perguntas específicas: (1) um episódio de hipoglicemia grave (HG) realmente aumenta o risco de internação por complicação cardiovascular subsequente em diabetes tipo 1, fora do ambiente de ensaio clínico? E (2), se sim, o uso de monitorização contínua de glicose por escaneamento intermitente (isCGM, tecnologia FreeStyle Libre) reduz esse risco em comparação com automonitorização capilar (BGM)?

## Desenho
Eeg-Olofsson K et al. Diabetologia. 2025;68(8):1647-1656 (PMID 40272529; PMCID PMC12245946).

- **Fonte de dados**: Registro Nacional de Diabetes da Suécia (NDR — Swedish National Diabetes Register), com cobertura **>90%** dos adultos com diabetes tipo 1 no país, linkado ao Registro Nacional de Pacientes da Suécia (NPR — hospitalizações e óbitos).
- **Desenho**: coorte retrospectiva comparativa, com adultos (≥18 anos) com diagnóstico clínico de diabetes tipo 1, visita registrada no NDR entre 01/01/2014 e 31/07/2023, e data-índice de primeiro uso registrado de isCGM a partir de 01/06/2017. Grupo controle: adultos com diabetes tipo 1 **CGM-naïve** durante o mesmo período (uso exclusivo de BGM).
- **Definição de HG (evento-índice)**: evento de hipoglicemia grave que exigiu assistência de terceiros ou internação hospitalar, registrado no NDR antes da data-índice de isCGM (ou, para não usuários de isCGM, antes da data-base equivalente).
- **Desfecho primário — desfecho composto de complicação cardiovascular (DCV)**: definição de seis pontos, como diagnóstico primário de internação: infarto agudo do miocárdio (IAM) não fatal, doença arterial coronariana, AVC não fatal, insuficiência cardíaca ou fibrilação atrial, OU morte cardiovascular.
- **Desfecho secundário (definição mais estrita, tipo MACE clássico)**: composto de IAM, AVC ou morte cardiovascular.
- **Análise estatística**: regressão binomial negativa com ponderação por escore de propensão (PS-IPTW — propensity score-based inverse probability of treatment weighting), ajustada por idade, sexo, IMC, HbA1c basal, uso de bomba de insulina (CSII), perfil lipídico, função renal, tabagismo, atividade física, comorbidade prévia e complicações diabéticas prévias. Diferenças padronizadas ponderadas <0,10 foram consideradas sem influência de confusão relevante; entre 0,10 e 0,20, confusão residual pequena e considerada pouco provável de influenciar o resultado.
- **Seguimento**: até 24 meses.
- **Financiamento**: Abbott Diabetes Care (fabricante do FreeStyle Libre, tecnologia isCGM avaliada). Vários autores são funcionários da Abbott Diabetes Care/Abbott Laboratories ou receberam honorários da empresa — conflito de interesse relevante e declarado pelos próprios autores, registrado aqui para leitura crítica do achado.

## População
- **14.829 adultos** com diabetes tipo 1 elegíveis, dos quais **11.822 iniciaram isCGM** no período e **3.007 permaneceram em BGM** (grupo controle).
- **1.313 (8,9%)** tiveram pelo menos um evento-índice de HG registrado; **13.516 (91,1%)** não tiveram HG prévia registrada.
- Dos 1.313 com HG prévia: **970 eram usuários de isCGM** e **343 eram usuários de BGM**.
- Idade média (coorte com HG prévia): **54,3 ± 18,7 anos**; sem HG prévia: **52,8 ± 18,5 anos**.
- Antes da ponderação, havia diferença etária relevante entre usuários de isCGM e controles BGM (média 50,1 vs. 66,2 anos) e maior uso de CSII entre usuários de isCGM (12,6% vs. 2,3%); a prevalência basal de doença arterial coronariana também era menor entre usuários de isCGM (8,6% vs. 15,7% nos controles BGM). Após PS-IPTW, as diferenças padronizadas ponderadas para idade (-0,172), uso de CSII (0,167) e doença coronariana (-0,135) ficaram abaixo de 0,20 — os autores descrevem isso como confusão residual pequena, não eliminada, e reconhecem essa assimetria basal como limitação para a generalização do achado.

## Resultados — hipoglicemia grave e risco de complicação cardiovascular

### Toda a coorte (isCGM + BGM combinados)
| | Sem HG prévia | Com HG prévia | Taxa relativa (IC95%) | p |
|---|---|---|---|---|
| Taxa de internação por DCV (por 100 pessoas-ano) | **5,04** (IC95% 4,85-5,23) | **7,58** (IC95% 6,74-8,49) | **2,06** (1,48-2,85) | <0,001 |

**Um evento de hipoglicemia grave aproximadamente dobrou o risco de internação por complicação cardiovascular** nos dois anos seguintes, na coorte toda.

### Estratificado por tecnologia de monitorização
| Grupo | Sem HG prévia (taxa/100 p-a) | Com HG prévia (taxa/100 p-a) | Taxa relativa (IC95%) | p |
|---|---|---|---|---|
| **Usuários de BGM** | 9,56 (9,00-10,14) | 14,23 (11,95-16,82) | **1,80** (1,08-2,99) | 0,023 |
| **Usuários de isCGM** | 3,80 (3,62-3,99) | 5,40 (4,59-6,31) | **1,89** (1,25-2,84) | 0,002 |

O aumento relativo de risco após HG persiste tanto em usuários de BGM quanto de isCGM — ou seja, a hipoglicemia grave continua sendo um marcador de risco cardiovascular mesmo entre quem já usa a tecnologia de monitorização mais avançada.

## Resultado central — isCGM reduz o risco absoluto pós-hipoglicemia grave
Comparando diretamente usuários de isCGM contra usuários de BGM, **dentro do subgrupo que teve HG prévia**:
- Taxa de internação por DCV: **5,40 por 100 pessoas-ano (isCGM)** vs. **14,23 por 100 pessoas-ano (BGM)**.
- **Redução relativa de 78%** no risco de internação por complicação cardiovascular pós-HG para usuários de isCGM (taxa relativa **0,22**; IC95% 0,11-0,43; p<0,001).

No subgrupo **sem** HG prévia, isCGM também associou-se a **redução relativa de 77%** (taxa relativa 0,23; IC95% 0,18-0,28; p<0,001) em relação a BGM.

**Usando a definição mais estrita de MACE** (IAM, AVC ou morte cardiovascular, sem incluir doença coronariana isolada, insuficiência cardíaca ou fibrilação atrial), o padrão se repete: **redução relativa de 63%** para isCGM no subgrupo com HG prévia (taxa relativa 0,37; IC95% 0,18-0,75; p=0,006) e **redução relativa de 70%** no subgrupo sem HG prévia (taxa relativa 0,30; IC95% 0,26-0,38; p<0,001).

## Subgrupo por história prévia de doença cardiovascular
Entre os que já tinham DCV prévia registrada:
- BGM: **34,94** internações por 100 pessoas-ano.
- isCGM: **23,61** por 100 pessoas-ano (p<0,001) — **redução relativa de 49%**.

Entre os **sem** DCV prévia:
- BGM: **6,47** por 100 pessoas-ano.
- isCGM: **2,46** por 100 pessoas-ano (p<0,001) — **redução relativa de 80%**.

## O que este estudo NÃO prova
Os próprios autores são explícitos: **este é um estudo de associação, não de causalidade.** Os dados não permitem afirmar que a hipoglicemia grave *causa* diretamente o evento cardiovascular subsequente, nem que a redução de risco observada com isCGM decorre exclusivamente da redução de hipoglicemia. Mecanismos propostos pelos autores (não testados diretamente neste desenho): hipoglicemia aguda ativa mediadores pró-inflamatórios, ativação plaquetária e estresse endotelial vascular; hipoglicemia recorrente está associada a aumento de calcificação coronariana em subanálise da coorte DCCT (documento já registrado nesta pasta cobre DCCT/EDIC e calcificação coronariana, mas não especificamente este mecanismo hipoglicemia→calcificação).

## Limitações reconhecidas pelos próprios autores
- **Desenho retrospectivo, observacional** — não permite inferência causal.
- **Confusão por indicação/seleção não eliminada**: o início de isCGM pode vir acompanhado de educação estruturada sobre autocuidado que não é capturada nem controlada na análise; usuários de isCGM eram mais jovens e tinham menos comorbidade cardiovascular basal antes da ponderação, e a ponderação por escore de propensão reduz mas não elimina esse desequilíbrio (diferenças padronizadas residuais de até 0,17-0,19 para idade, CSII e doença coronariana prévia).
- **Sem dados de variabilidade glicêmica ou tempo em hiperglicemia** no NDR — não é possível isolar o efeito da redução de hipoglicemia do efeito de outras variáveis glicêmicas não capturadas.
- **Sem data exata do evento de HG** em relação ao desfecho cardiovascular — não é possível estabelecer uma janela temporal precisa entre os dois eventos.
- **Sem dados de comedicação cardiovascular, etnia, escolaridade ou indicadores de vulnerabilidade social** no NDR/NPR.
- **Financiamento pela Abbott Diabetes Care**, fabricante da tecnologia isCGM avaliada (FreeStyle Libre) — vários autores são funcionários da empresa ou receberam honorários dela. Isso não invalida os achados (a metodologia PS-IPTW e a magnitude consistente entre múltiplas definições de desfecho são pontos a favor da robustez), mas é um conflito de interesse relevante para leitura crítica.
- **Generalização**: coorte sueca, com cobertura quase completa da população nacional de diabetes tipo 1, mas de um sistema de saúde específico — a magnitude exata do benefício não deve ser extrapolada diretamente para outros sistemas de saúde sem verificação.
- Os autores também discutem explicitamente a divergência com estudos anteriores: um estudo sueco de 2014 (mesmo NDR, período diferente, Lung TWC et al., Diabetes Care) não encontrou associação entre HG prévia e risco de evento cardiovascular fatal subsequente (mas usou desfecho restrito a IAM e AVC apenas, com metodologia distinta); o estudo EURODIAB e duas coortes prospectivas (dinamarquesa e holandesa, menores) também não encontraram associação entre HG/consciência prejudicada de hipoglicemia e mortalidade cardiovascular quando não usada como parte de desfecho composto. Os autores atribuem a diferença de resultado à definição mais ampla de desfecho composto (seis categorias de complicação, não só IAM/AVC fatal) usada neste estudo.

## Armadilhas clínicas
- **Tratar o achado como prova de que hipoglicemia grave causa infarto/AVC** — é uma associação robusta e biologicamente plausível, não uma relação causal comprovada por este desenho.
- **Atribuir toda a redução de risco isoladamente ao "sensor" em si**, ignorando que usuários de isCGM eram sistematicamente diferentes dos usuários de BGM antes da ponderação (mais jovens, menos doença coronariana prévia, mais uso de bomba de insulina) — a ponderação por escore de propensão reduz, mas os próprios autores reconhecem confusão residual.
- **Ignorar o subgrupo de maior risco absoluto**: pacientes com diabetes tipo 1, DCV prévia E hipoglicemia grave prévia usando apenas BGM têm a maior taxa de internação cardiovascular de toda a análise (34,94/100 pessoas-ano) — é o subgrupo em que a intervenção (troca para monitorização contínua) tem maior potencial de impacto absoluto.
- **Extrapolar para diabetes tipo 2** — a coorte é exclusivamente de diabetes tipo 1; `VERIFICAÇÃO HUMANA NECESSÁRIA` quanto à magnitude do mesmo fenômeno em diabetes tipo 2, população com fisiopatologia e perfil de risco cardiovascular basal diferentes.
- **Confundir isCGM (escaneamento intermitente, FreeStyle Libre 1, a tecnologia estudada aqui) com CGM em tempo real (Dexcom, Guardian Sensor, com alarme automático de hipoglicemia)** — este estudo especificamente avalia isCGM contra BGM; a magnitude do benefício de CGM em tempo real com alarme (que tem mecanismo adicional de alerta ativo) não foi objeto direto desta análise.
- **Assumir cobertura/reembolso de isCGM no Brasil equivalente ao sistema sueco estudado**, ou posicionamento oficial da SBD sobre este achado específico — `VERIFICAÇÃO HUMANA NECESSÁRIA`.

## Tudo com Tudo

- [Hipoglicemia, Arritmia e Neuropatia Autonômica Cardíaca no Diabetes](/biblioteca/hipoglicemia-arritmia-e-neuropatia-autonomica-cardiaca-no-diabetes)
- [Monitorização Contínua de Glicose e Desfechos Cardiovasculares e Mortalidade no Diabetes Tipo 1: Coorte Nacional Coreana (Kim et al., Diabetologia 2026)](/biblioteca/monitorizacao-continua-de-glicose-e-desfechos-cardiovasculares-no-diabetes-tipo-1-coorte-coreana)
- [Diabetes Tipo 1 e Risco Cardiovascular: Idade de Início e o Registro Sueco](/biblioteca/diabetes-tipo-1-e-risco-cardiovascular-idade-de-inicio-e-registro-sueco)
- [Diabetes Tipo 1 de Longa Duração e Calcificação Coronariana: os Estudos CACTI e DCCT/EDIC](/biblioteca/diabetes-tipo-1-de-longa-duracao-e-calcificacao-coronariana-cacti-e-dcct-edic)
- [Controle Glicêmico Intensivo e Desfecho Cardiovascular no Diabetes Tipo 2: ACCORD, ADVANCE, VADT e o Efeito Legado do UKPDS](/biblioteca/controle-glicemico-intensivo-e-desfecho-cardiovascular-no-diabetes-tipo-2-accord-advance-e-vadt)
- [GLP-1 em Diabetes Tipo 1: MACE e Doença Renal Terminal em Emulação de Ensaio-Alvo (Xu et al., Nature Medicine 2026)](/biblioteca/glp-1-em-diabetes-tipo-1-mace-e-doenca-renal-terminal-emulacao-de-ensaio-alvo)
- [Neuropatia Autonômica Cardíaca Diabética: Manifestações, Testes de Ewing e Valor Prognóstico](/biblioteca/neuropatia-autonomica-cardiaca-diabetica-manifestacoes-testes-de-ewing-e-valor-prognostico)

## Revisão editorial CorVIA

Revisado em 09/09/2026 com fontes públicas rastreáveis (PubMed E-utilities — esearch/esummary/efetch em db=pubmed e db=pmc). Todos os números centrais deste documento (n, idade, taxas de internação por 100 pessoas-ano, taxas relativas, IC95%, valores de p, definições de desfecho, achados por subgrupo de história cardiovascular prévia) foram conferidos diretamente no texto completo em acesso aberto, indexado no PubMed Central (PMCID PMC12245946), com verificação cruzada por duas extrações independentes de trechos verbatim do artigo. Conflito de interesse do estudo-fonte (financiamento pela Abbott Diabetes Care, fabricante da tecnologia isCGM avaliada) está declarado explicitamente neste documento. `VERIFICAÇÃO HUMANA NECESSÁRIA`: status de cobertura/reembolso de isCGM no Brasil e eventual posicionamento de diretrizes nacionais (SBD) sobre este achado específico; magnitude do mesmo fenômeno em diabetes tipo 2.
