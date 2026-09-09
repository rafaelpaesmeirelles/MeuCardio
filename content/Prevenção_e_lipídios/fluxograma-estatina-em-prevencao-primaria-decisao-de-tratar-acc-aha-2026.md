---
title: "Fluxograma: Estatina em Prevenção Primária — Decisão de Tratar pela ACC/AHA 2026 (PREVENT-ASCVD)"
slug: fluxograma-estatina-em-prevencao-primaria-decisao-de-tratar-acc-aha-2026
theme: "Prevenção e lipídios"
kind: fluxograma
fonte_producao: chatgpt
review_status: revisado
review_note: "Revisão adversarial Codex em 08/09/2026: alto risco PREVENT e LDL ≥190 não terminam sem tratamento por ausência de CAC; risco limítrofe/intermediário e risco de 30 anos separados. Fonte primária AHA/ACC 2026 e material oficial PREVENT para clínicos conferidos."
source_refs:
  - "Blumenthal RS, Morris PB, Gaudino M, et al. 2026 ACC/AHA/AACVPR/ABC/ACPM/ADA/AGS/APhA/ASPC/NLA/PCNA Guideline on the Management of Dyslipidemia. J Am Coll Cardiol. 2026;87(19):2624-2757. DOI: 10.1016/j.jacc.2025.11.016. PMID: 41824590."
  - "Blumenthal RS, Morris PB, Gaudino M, et al. 2026 Guideline on the Management of Dyslipidemia. Circulation. Published online March 13, 2026. DOI: 10.1161/CIR.0000000000001423."
  - "Derivado de acc-aha-2026-diretriz-dislipidemia-prevent-lpa-apob-e-metas-ldl.md, já publicado no acervo (Prevenção e lipídios)."
---

# Fluxograma: Estatina em Prevenção Primária — ACC/AHA 2026

Este roteiro orienta a decisão inicial de reduzir LDL-C segundo a **ACC/AHA 2026**. O PREVENT-ASCVD é aplicado na população apropriada, não substitui vias específicas de doença aterosclerótica já conhecida, hipercolesterolemia grave ou situações especiais, e não deve ser confundido com SCORE2/ESC. Estilo de vida e decisão compartilhada acompanham todos os caminhos.

## Árvore de decisão

```mermaid
flowchart TD
  A["Adulto em avaliação de prevenção primária<br/>Rever lipídios, causas secundárias, comorbidades,<br/>tratamento atual e preferências"] --> S{"ASCVD clínica, aterosclerose subclínica já conhecida,<br/>gestação/lactação, idade maior que 75 anos<br/>ou situação fora deste roteiro?"}
  S -->|Sim| SP["Usar a via específica correspondente<br/>Não aplicar automaticamente o ramo de risco geral"]
  S -->|Não| G{"LDL-C de 190 mg/dL ou mais?"}
  G -->|Sim| GH["Estatina na máxima intensidade tolerada<br/>independentemente do risco calculado<br/>Investigar causas secundárias e hipercolesterolemia familiar"]
  G -->|Não| D{"40 a 75 anos com diabetes,<br/>DRC estágio 3 ou 4 não dialítica, ou HIV?"}
  D -->|Sim| DT["Terapia redutora de LDL pela via específica<br/>Não exigir risco PREVENT mínimo para iniciar<br/>Individualizar intensidade e interações"]
  D -->|Não| E{"Elegível para PREVENT:<br/>30 a 79 anos, LDL-C 70 a 189 mg/dL<br/>e sem ASCVD/subclínica conhecida?"}
  E -->|Não| IND["Individualizar por idade, fenótipo, risco cumulativo,<br/>fragilidade, expectativa de benefício e preferências<br/>Não concluir ausência de indicação por falta de escore"]
  E -->|Sim| P["Calcular risco PREVENT-ASCVD em 10 anos<br/>Personalizar com fatores agravantes"]
  P --> R{"Risco em 10 anos"}
  R -->|10 por cento ou mais| HIGH["Iniciar estatina de alta intensidade se tolerada<br/>Não condicionar a indicação a realizar CAC"]
  R -->|5 a menos de 10 por cento| MID["Iniciar estatina pelo menos de intensidade moderada<br/>Individualizar intensidade e metas"]
  R -->|3 a menos de 5 por cento| BORDER["Considerar estatina moderada após discussão<br/>e avaliação de fatores agravantes"]
  R -->|Menos de 3 por cento| LOW{"30 a 59 anos com LDL-C 160 a 189 mg/dL<br/>ou risco PREVENT em 30 anos de 10 por cento ou mais?"}
  LOW -->|Sim| LONG["É razoável considerar estatina moderada<br/>para reduzir exposição cumulativa"]
  LOW -->|Não| LIFE["Priorizar hábitos saudáveis e reavaliar risco<br/>Considerar história familiar e situações especiais"]
  MID --> UNC{"Após discussão, decisão ainda incerta?"}
  BORDER --> UNC
  UNC -->|Não| PLAN["Executar plano compartilhado e acompanhar resposta"]
  UNC -->|Sim e elegível| CAC["Considerar CAC seletivo para reclassificar<br/>Integrar escore, percentil e condições clínicas<br/>Não converter CAC em uma faixa PREVENT inventada"]
  CAC --> DEC["Decidir início ou intensidade conforme a via de CAC<br/>CAC zero não anula indicação de LDL elevado grave<br/>ou outras condições de alto risco"]
```

## Pontos que mudam a decisão

**Alto risco não é ausência de indicação.** PREVENT-ASCVD ≥10% conduz a estatina de alta intensidade quando tolerada; LDL-C ≥190 mg/dL tem indicação pela hipercolesterolemia grave independentemente do escore. CAC não é requisito para tratar esses grupos. No risco intermediário (5% a <10%), a recomendação é pelo menos estatina moderada; risco limítrofe (3% a <5%) exige discussão dos agravantes e do benefício esperado. Em 30–59 anos com risco de 10 anos baixo, LDL-C 160–189 mg/dL ou risco de 30 anos ≥10% pode justificar terapia moderada.

**CAC é seletivo.** Pode esclarecer decisões incertas, principalmente no risco limítrofe/intermediário, em homens a partir de 40 anos e mulheres a partir de 45 anos. Sua interpretação considera valor absoluto, percentil e contexto; não existe neste roteiro uma conversão de CAC para “PREVENT 3%–10%”. Um CAC zero não exclui placa não calcificada e não deve apagar indicações independentes ou fatores de alto risco. A decisão de adiar tratamento precisa respeitar a diretriz, inclusive contexto de diabetes, tabagismo, hipercolesterolemia familiar e história familiar forte.

**Lp(a) e ApoB podem influenciar o plano.** Medir Lp(a) pelo menos uma vez na vida adulta; elevação é agravante de risco e pode modificar a decisão/intensidade. ApoB é útil de forma seletiva, especialmente na discordância entre LDL-C e número de partículas aterogênicas, em hipertrigliceridemia, diabetes e risco residual. Não apresentá-las como incapazes de mudar a decisão inicial.

**Hipertrigliceridemia exige avaliação própria.** Corrigir causas secundárias, dieta e risco aterosclerótico; não esperar triglicerídeos chegarem a 1.000 mg/dL para reconhecer risco de pancreatite e necessidade de manejo específico. Elevação grave, sintomas abdominais e condições associadas mudam a urgência e a estratégia. As opções para pancreatite e para redução de eventos ateroscleróticos têm objetivos e critérios distintos.

**Populações especiais não são um “não tratar”.** DRC em diálise, gestação/lactação, crianças, LDL fora da faixa do escore e idosos com fragilidade/benefício limitado exigem recomendações próprias. Após 75 anos, individualizar início ou continuidade conforme condição funcional, expectativa de benefício, tolerância e preferências, sem negar tratamento apenas pela idade nem impor uma intensidade universal.

Após decidir tratar, avaliar resposta lipídica, tolerância e metas correspondentes ao risco. O acompanhamento e eventual associação de outros agentes seguem a diretriz vigente; não suspender estatina ou terapia essencial automaticamente por sintoma inespecífico.

Fonte operacional primária: [AHA/ACC 2026 — uso de PREVENT-ASCVD para manejo lipídico, material oficial para clínicos](https://professional.heart.org/en/science-news/-/media/731B2098BB23427F9EA8EDDF98E08145.ashx), seções 4.2.3.2 e 4.2.3.7 e tabela de tratamento por faixa de risco. [Página oficial da diretriz](https://professional.heart.org/en/science-news/2026-guideline-on-the-management-of-dyslipidemia).
