# Referências pré-operatórias — fontes primárias

Levantamento pedido pelo Rafael em 07/08/2026 (repassando pedido do ChatGPT): figuras/tabelas
das publicações originais dos escores de risco perioperatório, para conferência visual antes de
expandir a Avaliação Cardiológica Pré-Operatória — nunca reconstruir árvore/tabela de memória.

Este README já traz tudo embutido (GitHub renderiza as imagens abaixo direto). Página equivalente,
fora do repositório: https://claude.ai/code/artifact/c3166189-22be-4eb2-be99-215169e096ca

## Obtido

**Lee TH et al., Circulation. 1999;100(10):1043-1049, PMID 10477528** — PDF de acesso aberto em
https://cloudfront.escholarship.org/dist/prd/content/qt845640mb/qt845640mb.pdf

![Tabela 4 do original — os 6 preditores, OR bruto e ajustado nas duas coortes](RCRI_Lee_1999_tabela_6preditores.png)

![Tabela 3 do original — taxa de evento por classe, nas 4 escalas comparadas](RCRI_Lee_1999_tabela_classes_eventos.png)

## Parcial

**ACS-NSQIP Surgical Risk Calculator** — só a tela de abertura (riskcalculator.facs.org, v4.0.4).
Não fui além: os termos da própria ferramenta proíbem automação ("we do not permit... the
functionality of the calculator to be automated in any way"), e a entrada tem CAPTCHA — as duas
coisas juntas impedem capturar as telas de variáveis/resultado por este caminho.

![Tela inicial oficial do ACS NSQIP Surgical Risk Calculator](ACS_NSQIP_tela_inicial.png)

## Bloqueado (testado, não é falta de tentativa)

- AHA/ACC 2024 (Perioperative Cardiovascular Management for Noncardiac Surgery) — 403 em
  ahajournals.org e jacc.org, sem depósito em PMC para nenhum dos 3 PMIDs da publicação tripla.
- ESC 2022 (Cardiovascular Assessment and Management of Patients Undergoing Non-Cardiac Surgery)
  — 403 em academic.oup.com.
- Gupta MICA (Circulation 2011, PMID 21730309) — 403 em ahajournals.org; PMC só tem artigos que
  citam o estudo, não o texto original. **É a lacuna real que motivou o pedido do ChatGPT** — os
  coeficientes hoje em uso na Corvia vieram de calculadoras de terceiros, nunca confirmados
  contra a tabela publicada.
- DASI original (Hlatky 1989, Am J Cardiol) e METS Study (Wijeysundera, Lancet 2018) — sem PMC
  nem Europe PMC.
- AUB-HAS2 (Dakik 2019, PMID 31221255) — sem PMC (o abstract já foi validado à parte, mas não a
  tabela/figura completa).

## Não testado ainda

CCS guideline (perioperatório, BNP/troponina), SORT, POSPOM, ACS-SRC.

## Achado à parte, fora da lista pedida

**GSCRI (Alrezk et al. 2017, PMID 29146612) tem PMC aberto (PMC5721761)** — diferente de todos os
outros desta lista. Ainda não extraído, mas é o caminho mais fácil se quiserem ampliar esse
escore.
