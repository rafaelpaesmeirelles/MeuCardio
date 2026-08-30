---
title: "Fluxograma: ICFEr com fração de ejeção melhorada — manter ou retirar a terapia (TRED-HF)"
slug: fluxograma-icfer-com-fracao-de-ejecao-melhorada-manter-ou-retirar-a-terapia-tred-hf
theme: "Insuficiência cardíaca"
kind: fluxograma
summary: "Decisão diante da FEVE que subiu de 40% ou menos para acima de 40%: confirmar a melhora e manter a terapia modificadora da ICFEr, inclusive no assintomático e nas etiologias potencialmente reversíveis; o TRED-HF demonstrou recaída frequente após retirada e não definiu um subgrupo seguro para suspensão."
review_status: revisado
review_note: "Produção científica assistida (Claude) e revisão editorial e científica independente (Codex), concluídas em 26/08/2026. Fontes primárias, coerência clínica, lógica dos fluxos, metadados e links foram conferidos; correções incorporadas."
source_refs:
  - "Halliday BP, Wassall R, Lota AS, et al. Withdrawal of pharmacological treatment for heart failure in patients with recovered dilated cardiomyopathy (TRED-HF): an open-label, pilot, randomised trial. Lancet. 2019;393(10166):61-73. DOI: 10.1016/S0140-6736(18)32484-X. PMID: 30429050. Texto integral: https://pmc.ncbi.nlm.nih.gov/articles/PMC6319251/"
  - "Heidenreich PA, Bozkurt B, Aguilar D, et al. 2022 AHA/ACC/HFSA Guideline for the Management of Heart Failure. Circulation. 2022;145(18):e895-e1032. DOI: 10.1161/CIR.0000000000001063. Síntese oficial: https://professional.heart.org/en/science-news/2022-guideline-for-the-management-of%20heart-failure/top-things-to-know"
  - "McDonagh TA, Metra M, Adamo M, et al. 2021 ESC Guidelines for the diagnosis and treatment of acute and chronic heart failure. Eur Heart J. 2021;42(36):3599-3726. DOI: 10.1093/eurheartj/ehab368. https://academic.oup.com/eurheartj/article/42/36/3599/6358045"
  - "MacDonald BJ, Virani SA, Zieroth S, Turgeon R. Heart Failure Management in 2023: A Pharmacotherapy- and Lifestyle-Focused Comparison of Current International Guidelines. CJC Open. 2023;5(8):629-640. DOI: 10.1016/j.cjco.2023.05.008. https://pmc.ncbi.nlm.nih.gov/articles/PMC10502425/"
  - "Derivado de icfer-classificacao-diagnostico-quatro-pilares.md, segunda-definicao-universal-insuficiencia-cardiaca-2026.md e fluxograma-insuficiencia-cardiaca-cronica-por-fracao-de-ejecao-esc-2023.md, já publicados no acervo."
---

# Fluxograma: ICFEr com fração de ejeção melhorada (HFimpEF) — manter ou retirar a terapia

A melhora da fração de ejeção sob tratamento representa remissão, não cura demonstrada. A AHA/ACC/HFSA 2022 recomenda continuar a terapia da ICFEr em pacientes com HFimpEF, inclusive assintomáticos, para prevenir recaída de insuficiência cardíaca e disfunção ventricular. Nenhuma diretriz ou ensaio definiu uma etiologia “reversível” em que seja seguro suspender rotineiramente os fármacos modificadores de doença.

## Árvore de decisão

```mermaid
flowchart TD
  R0["Paciente com ICFEr prévia, FEVE de 40% ou menos,<br/>agora com FEVE acima de 40% sob terapia"]
  D1{"Melhora confirmada em nova imagem,<br/>preferencialmente pelo mesmo método,<br/>com paciente clinicamente estável?"}
  C1(["Não rotular como HFimpEF:<br/>manter a terapia da ICFEr e repetir a imagem<br/>no intervalo clinicamente apropriado"])
  P1["IC com fração de ejeção melhorada — HFimpEF"]
  D2{"Intolerância, efeito adverso ou contraindicação<br/>objetiva a algum componente da terapia?"}
  C2(["Manter todos os fármacos modificadores da ICFEr<br/>na dose máxima tolerada, mesmo assintomático<br/>e após correção de causa potencialmente reversível"])
  C3(["Tratar o fator reversível e ajustar somente<br/>a classe implicada, na menor extensão necessária;<br/>reintroduzir ou substituir quando possível.<br/>Não usar a melhora da FEVE como indicação de retirada"])

  R0 --> D1
  D1 -->|"Não"| C1
  D1 -->|"Sim"| P1
  P1 --> D2
  D2 -->|"Não"| C2
  D2 -->|"Sim"| C3

  classDef conduta fill:#eef6ef,stroke:#2f7a4f,color:#12301f;
  class C1,C2,C3 conduta;
```

## O que é HFimpEF

A AHA/ACC/HFSA 2022 define HFimpEF como FEVE prévia de 40% ou menos e medida de seguimento acima de 40%. A Definição Universal acrescenta aumento de pelo menos 10 pontos percentuais. Quando a diferença é pequena, convém confirmar pelo mesmo método de imagem e em condição clínica estável antes de mudar o rótulo — sem alterar a terapia enquanto isso.

## A regra: manter a terapia

A recomendação da AHA/ACC/HFSA 2022 é continuar o tratamento da ICFEr em pacientes com HFimpEF, inclusive assintomáticos, para prevenir recaída. Isso inclui os fármacos modificadores de doença que o paciente tolera. Taquicardiomiopatia controlada, cardiomiopatia periparto recuperada, miocardite e cardiotoxicidade tratada não constituem, por si sós, autorização para retirada: esses grupos não foram validados como subgrupos de baixo risco em ensaio de suspensão.

Se surgir hipotensão sintomática, disfunção renal aguda, hipercalemia, bradicardia ou outro evento adverso, a conduta é corrigir a causa e ajustar temporariamente a classe responsável, de modo individualizado. Essa decisão é diferente de retirar toda a terapia por considerar o coração “curado”. Indicações independentes — hipertensão, fibrilação atrial, doença renal crônica ou diabetes — também permanecem válidas.

## O que o TRED-HF mostrou

O TRED-HF foi um ensaio piloto, aberto e monocêntrico em cardiomiopatia dilatada não isquêmica recuperada. Incluiu 51 pacientes com FEVE prévia de 40% ou menos, FEVE atual de 50% ou mais, volume diastólico do VE normal, NT-proBNP abaixo de 250 ng/L e ausência de sintomas.

| Resultado | TRED-HF |
|---|---|
| Recaída em 6 meses | 11 de 25 após retirada — 44% — versus 0 de 26 com manutenção |
| Fase de crossover | 9 de 25 recaíram ao retirar a terapia |
| Total com recaída | 20 de 50 — 40% |
| Critério de recaída | queda de FEVE maior que 10 pontos para menos de 50%; aumento do volume diastólico acima do normal; NT-proBNP dobrado e acima de 400 ng/L; ou insuficiência cardíaca clínica |

O protocolo de retirada do estudo não deve ser usado como autorização clínica para suspender tratamento. Ele serviu para testar a hipótese e revelou taxa alta de recaída; não identificou um perfil confiável de “cura”. Além disso, o esquema basal era anterior ao uso contemporâneo de ARNI e iSGLT2.

## Limitações

- O TRED-HF tinha amostra pequena, seguimento inicial de 6 meses e população selecionada com cardiomiopatia dilatada não isquêmica.
- Não existe marcador isolado que demonstre segurança para retirar terapia em HFimpEF.
- Ajustes por contraindicação ou intolerância devem ser feitos classe a classe e não equivalem a suspensão por melhora da FEVE.

## Tudo com Tudo

- [Fluxograma: Insuficiência Cardíaca crônica — conduta por fração de ejeção (ESC 2021 / atualização 2023)](/biblioteca/fluxograma-insuficiencia-cardiaca-cronica-por-fracao-de-ejecao-esc-2023)
- [Insuficiência Cardíaca com Fração de Ejeção Reduzida — Classificação, Diagnóstico e os Quatro Pilares Terapêuticos](/biblioteca/icfer-classificacao-diagnostico-quatro-pilares)
- [Segunda Definição Universal de Insuficiência Cardíaca — Consenso AHA/ACC/ESC/WHF 2026](/biblioteca/segunda-definicao-universal-insuficiencia-cardiaca-2026)
- [Cardiomiopatia Induzida por Taquicardia: reversibilidade após controle da arritmia](/biblioteca/cardiomiopatia-induzida-por-taquicardia-reversibilidade-apos-controle-da-arritmia)
- [Cardiomiopatia Periparto: critérios diagnósticos, recuperação e manejo](/biblioteca/cardiomiopatia-periparto-criterios-diagnosticos-recuperacao-e-manejo)
- [Fluxograma: Sequenciamento e Titulação da Terapia Quádrupla na ICFEr](/biblioteca/fluxograma-sequenciamento-titulacao-terapia-quadrupla-icfer)
