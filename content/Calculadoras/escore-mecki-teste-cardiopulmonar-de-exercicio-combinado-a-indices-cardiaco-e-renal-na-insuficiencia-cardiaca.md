---
title: 'MECKI: exercício, função cardíaca e renal no prognóstico da insuficiência cardíaca'
slug: escore-mecki-teste-cardiopulmonar-de-exercicio-combinado-a-indices-cardiaco-e-renal-na-insuficiencia-cardiaca
theme: Calculadoras
kind: calculadora
review_status: revisado
source_refs:
- 'Agostoni P, Corrà U, Cattadori G, Veglia F, La Gioia R, Scardovi AB, Emdin M, Metra M, Sinagra G, Limongelli G, Raimondo
  R, Re F, Guazzi M, Belardinelli R, Parati G, Magrì D, Fiorentini C, Mezzani A, Salvioni E, Scrutinio D, Ricci R, Bettari
  L, Di Lenarda A, Pastormerlo LE, Pacileo G, Vaninetti R, Apostolo A, Iorio A, Paolillo S, Palermo P, Contini M, Confalonieri
  M, Giannuzzi P, Passantino A, Cas LD, Piepoli MF, Passino C; MECKI Score Research Group. Metabolic exercise test data combined
  with cardiac and kidney indexes, the MECKI score: a multiparametric approach to heart failure prognosis. Int J Cardiol.
  2013;167(6):2710-2718. DOI: 10.1016/j.ijcard.2012.06.113. PMID: 22795401.'
- Centro Cardiologico Monzino. MECKI Score, calculadora oficial do grupo desenvolvedor. https://www.cardiologicomonzino.it/en/mecki-score/.
  Consultada em 09/09/2026.
review_note: 'Removida alegação de exclusividade e equivalência da AUC a excelência; fornecida calculadora oficial e unidades,
  distinguindo descrição do modelo de implementação local. Conferência editorial final: título alinhado ao corpo revisado,
  campos de classificação e resumo conferidos, referências bibliográficas organizadas e espaçamento corrigido quando necessário.
  Vínculos internos preservados.'
summary: O modelo MECKI integra teste cardiopulmonar e variáveis clínicas para estimar risco na insuficiência cardíaca sistólica.
  Foi desenvolvido em 2.716 pacientes de 13 centros italianos, com seguimento mediano de 1.041 dias e validação cruzada. O
  desfecho original combinava morte cardiovascular e transplante cardíaco urgente.
tags: []
source_tier: A
gaps: []
published: true
---

# MECKI: exercício, função cardíaca e renal no prognóstico da insuficiência cardíaca

O modelo MECKI integra teste cardiopulmonar e variáveis clínicas para estimar risco na insuficiência cardíaca sistólica. Foi desenvolvido em 2.716 pacientes de 13 centros italianos, com seguimento mediano de 1.041 dias e validação cruzada. O desfecho original combinava morte cardiovascular e transplante cardíaco urgente.

## Variáveis necessárias

- Hemoglobina e sódio.
- Função renal estimada por MDRD.
- Fração de ejeção ventricular esquerda.
- VO₂ de pico como percentual do predito.
- Inclinação VE/VCO₂.

## Desempenho original

| Horizonte | AUC (IC 95%) |
|---|---|
| 1 ano | 0,804 (0,754–0,852) |
| 2 anos | 0,789 (0,750–0,828) |
| 3 anos | 0,762 (0,726–0,799) |
| 4 anos | 0,760 (0,724–0,796) |

Discriminação nessa coorte não garante calibração em qualquer população, nem valida automaticamente uso na IC com fração de ejeção preservada. O escore não decide isoladamente listagem para transplante ou suporte mecânico.

[Estudo original: Agostoni et al., 2013](https://pubmed.ncbi.nlm.nih.gov/22795401/).

## Onde calcular

Use a [calculadora oficial do Centro Cardiologico Monzino](https://www.cardiologicomonzino.it/en/mecki-score/), destinada a profissionais. Este documento descreve o modelo, sem reproduzir sua equação. Respeite as unidades apresentadas no formulário, a equação renal especificada e o VO₂ em percentual predito; não substitua por mL/kg/min nem estime dados de exercício ausentes.

## Tudo com Tudo

- [Teste Cardiopulmonar de Exercício na Seleção do Candidato a Transplante Cardíaco: VO2 Pico e o Efeito do Betabloqueador](/biblioteca/teste-cardiopulmonar-de-exercicio-na-selecao-do-candidato-a-transplante-cardiaco-vo2-pico-e-o-efeito-do-betabloqueador) — Liga variáveis de teste cardiopulmonar do MECKI à avaliação prognóstica e seleção para transplante na IC, sem converter o escore em critério isolado.
