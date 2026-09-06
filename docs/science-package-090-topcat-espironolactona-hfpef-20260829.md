# Pacote 090/100 — TOPCAT: espironolactona em IC com FEVE preservada

## Unidade clínica auditável

Revisão adversarial independente do TOPCAT, priorizando a neutralidade do desfecho primário global, o sinal de hospitalização por IC, a toxicidade por hipercalemia/função renal e o risco de transformar análises geográficas pós-hoc em resultado randomizado primário.

## Fonte primária verificada

- Pitt B, Pfeffer MA, Assmann SF, et al. *Spironolactone for heart failure with preserved ejection fraction*. N Engl J Med. 2014;370:1383-1392.
- PMID: `24716680`.
- DOI: `10.1056/NEJMoa1313731`.
- URL PubMed: `https://pubmed.ncbi.nlm.nih.gov/24716680/`.

## População e desenho

Ensaio randomizado, duplo-cego, com 3.445 pacientes com insuficiência cardíaca sintomática e FEVE >=45%, comparando espironolactona a placebo. O desfecho primário foi morte cardiovascular, parada cardíaca abortada ou hospitalização por insuficiência cardíaca.

## Resultado principal conferido

O desfecho primário ocorreu em 18,6% com espironolactona e 20,4% com placebo: HR 0,89; IC95% 0,77-1,04; p=0,14. Assim, o desfecho primário global foi neutro.

Entre os componentes, hospitalização por insuficiência cardíaca foi menor com espironolactona (12,0% vs. 14,2%; HR 0,83; IC95% 0,69-0,99; p=0,04). Mortalidade total e hospitalizações por qualquer causa não foram significativamente reduzidas.

Hipercalemia ocorreu em 18,7% com espironolactona vs. 9,1% com placebo, acompanhada por aumento de creatinina sérica; o RCT utilizou monitorização frequente.

## Revisão adversarial

1. **TOPCAT global não foi positivo para o desfecho primário.** A redução de hospitalização por IC não autoriza rebatizar o composto como significativo.
2. **Não declarar redução de mortalidade.** O estudo não demonstrou redução significativa de mortalidade total.
3. **Não promover análise regional pós-hoc a evidência randomizada principal.** Diferenças entre Américas e Rússia/Geórgia geraram importantes discussões sobre recrutamento, aderência e validade, mas análises regionais posteriores não substituem a randomização e o resultado global prespecificado.
4. **Não banalizar hipercalemia e disfunção renal.** A segurança observada ocorreu com seleção e monitorização laboratoriais; o risco de hipercalemia aproximadamente dobrou.
5. **Não transportar diretamente TOPCAT para todo fenótipo contemporâneo de HFpEF.** O RCT usou FEVE >=45% e critérios próprios de elegibilidade.
6. **Não usar sinal de hospitalização como equivalente a benefício de sobrevida.** São desfechos clinicamente distintos.

## Contexto contemporâneo

A 2026 ESC Guideline for the Management of Heart Failure (DOI `10.1093/eurheartj/ehag100`) foi verificada como diretriz vigente. Este pacote não reproduz classe/nível da diretriz nem converte recomendações contemporâneas em uma reinterpretação retroativa do TOPCAT.

## Guardrails para o CorVIA

- Exibir `primário global neutro` sempre que TOPCAT for resumido.
- Separar o sinal de redução de hospitalização por IC dos desfechos de mortalidade.
- Identificar análises geográficas como pós-hoc/heterogeneidade, não como novo RCT.
- Exigir menção ao risco de hipercalemia e deterioração renal quando a evidência for usada clinicamente.
- Não gerar dose, titulação, corte automático de potássio/TFG ou classe de recomendação a partir deste documento.

## Validação deste pacote

- PMID, DOI, população, desfecho primário, componente de hospitalização e eventos de hipercalemia foram conferidos na publicação primária/PubMed.
- Nenhuma classe/nível de diretriz foi reproduzida sem conferência tabular específica.
- Nenhum slug, JSON clínico, `review_status`, schema, loader, migration, API, frontend ou runtime foi alterado.
- Pacote exclusivamente documental e additions-only.