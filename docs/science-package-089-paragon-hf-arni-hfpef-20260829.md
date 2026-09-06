# Pacote 089/100 — PARAGON-HF: sacubitril/valsartana em IC com FEVE preservada

## Unidade clínica auditável

Revisão adversarial independente do PARAGON-HF para impedir que um resultado primário limítrofe/neutro e análises de subgrupos sejam convertidos em uma narrativa de RCT globalmente positivo ou de benefício de mortalidade.

## Fonte primária verificada

- Solomon SD, McMurray JJV, Anand IS, et al. *Angiotensin-Neprilysin Inhibition in Heart Failure with Preserved Ejection Fraction*. N Engl J Med. 2019;381:1609-1620.
- PMID: `31475794`.
- DOI: `10.1056/NEJMoa1908655`.
- URL PubMed: `https://pubmed.ncbi.nlm.nih.gov/31475794/`.

## População e desenho

Ensaio randomizado com 4.822 pacientes com insuficiência cardíaca NYHA II-IV, FEVE >=45%, peptídeos natriuréticos elevados e doença cardíaca estrutural. O comparador ativo foi valsartana.

## Resultado principal conferido

O desfecho primário de hospitalizações totais por insuficiência cardíaca + morte cardiovascular apresentou 894 eventos no grupo sacubitril/valsartana e 1.009 no grupo valsartana: rate ratio 0,87; IC95% 0,75-1,01; p=0,06. Portanto, o desfecho primário não atingiu significância estatística convencional.

Morte cardiovascular foi 8,5% vs. 8,9% (HR 0,95; IC95% 0,79-1,16). Hospitalizações totais por IC apresentaram rate ratio 0,85 (IC95% 0,72-1,00). Análises de subgrupos sugeriram heterogeneidade por FEVE e sexo, mas não substituem a hierarquia do desfecho primário.

## Revisão adversarial

1. **p=0,06 não é um desfecho primário positivo.** A proximidade do limiar estatístico não autoriza reclassificação retrospectiva do RCT.
2. **Não vender subgrupos como confirmação.** Sinais em mulheres ou em FEVE abaixo da mediana são geradores/qualificadores de hipótese e devem ser lidos dentro da multiplicidade e da hierarquia do ensaio.
3. **Não declarar benefício de mortalidade cardiovascular.** O componente de morte CV foi neutro.
4. **Não fundir PARAGON-HF com PARADIGM-HF.** Os fenótipos e os resultados são diferentes; benefício robusto em HFrEF não pode ser importado para a população do PARAGON-HF.
5. **Preservar o comparador ativo.** A comparação foi contra valsartana, e não contra ausência de bloqueio do SRAA.
6. **Não aplicar o corte histórico de FEVE sem contexto contemporâneo.** Definições de fenótipos de IC mudam com diretrizes; o pacote descreve a população exatamente como randomizada.

## Contexto contemporâneo

A 2026 ESC Guideline for the Management of Heart Failure (DOI `10.1093/eurheartj/ehag100`) foi conferida como documento vigente. Como a taxonomia e as recomendações de IC foram atualizadas em 2026, este pacote preserva o fenótipo do RCT e não reproduz classe/nível de recomendação sem conferir a tabela normativa específica.

## Guardrails para o CorVIA

- Rotular o resultado primário global do PARAGON-HF como **não estatisticamente significativo**.
- Distinguir hospitalização por IC, morte CV e composto total.
- Marcar subgrupos por sexo/FEVE como análises de heterogeneidade, não como novo desfecho primário.
- Não usar PARAGON-HF para alegar redução de mortalidade.
- Não criar dose, indicação automática ou classe/nível de recomendação a partir deste documento.

## Validação deste pacote

- PMID, DOI, população, comparador e resultados principais foram conferidos na publicação primária/PubMed.
- Nenhuma classe/nível de diretriz foi reproduzida sem conferência tabular específica.
- Nenhum slug, JSON clínico, `review_status`, schema, loader, migration, API, frontend ou runtime foi alterado.
- Pacote exclusivamente documental e additions-only.