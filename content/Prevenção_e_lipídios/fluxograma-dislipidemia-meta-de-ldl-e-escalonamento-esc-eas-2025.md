---
title: "Fluxograma: Dislipidemia — categoria de risco, meta de LDL-C e escalonamento do tratamento (ESC/EAS 2025)"
slug: fluxograma-dislipidemia-meta-de-ldl-e-escalonamento-esc-eas-2025
theme: "Prevenção e lipídios"
kind: fluxograma
summary: "Duas árvores da atualização focada ESC/EAS 2025: a que define a categoria de risco e a meta de LDL-C — com o SCORE2/SCORE2-OP substituindo o SCORE — e a do escalonamento farmacológico, em que a síndrome coronariana aguda deixou de esperar o retorno ambulatorial para intensificar."
review_status: revisado
source_refs: ["Mach F, Koskinas KC, Roeters van Lennep JE, et al. 2025 Focused Update of the 2019 ESC/EAS Guidelines for the management of dyslipidaemias · European Heart Journal · 2025 · 46(42):4359-4378 · DOI: 10.1093/eurheartj/ehaf190 · PMID: 40878289 — Tabela 3 (categorias de risco cardiovascular) e Tabelas de Recomendação 2, 3 e 4", "Mach F et al. 2019 ESC/EAS Guidelines for the management of dyslipidaemias: lipid modification to reduce cardiovascular risk · European Heart Journal · 2020 · 41(1):111-188 · DOI: 10.1093/eurheartj/ehz455 — metas de LDL-C por categoria e recomendações de redução farmacológica, que a atualização de 2025 complementa sem substituir"]
---

# Fluxograma: Dislipidemia — categoria de risco, meta de LDL-C e escalonamento do tratamento (ESC/EAS 2025)

A atualização focada de 2025 **não mexeu nas metas de LDL-C**. Ela mexeu em duas
outras coisas, e é por isso que vale um fluxograma novo:

- **Como se chega à categoria de risco.** O SCORE saiu; entraram **SCORE2 e
  SCORE2-OP**, que estimam evento cardiovascular **fatal e não fatal** em 10 anos —
  e não mais só mortalidade. Os pontos de corte foram convertidos por um
  multiplicador, o que explica por que os números novos são o dobro dos antigos.
- **Quando intensificar.** Na síndrome coronariana aguda, a intensificação passou
  a ser recomendada **durante a internação do próprio evento**, em vez de esperar
  a reavaliação ambulatorial.

Duas armadilhas que o desenho da árvore torna visíveis: a categoria de risco quase
sempre é decidida **antes** de qualquer escore — doença aterosclerótica
estabelecida, diabetes com lesão de órgão-alvo, doença renal crônica grave e
hipercolesterolemia familiar já classificam o paciente sozinhas; e a meta de risco
alto e muito alto é **dupla** — o valor absoluto *e* a redução de pelo menos 50%
do basal, sendo que atingir um sem o outro não cumpre a recomendação.

## Árvore de decisão: categoria de risco e meta de LDL-C

```mermaid
flowchart TD
  R0["Adulto em avaliação de risco cardiovascular,<br/>com perfil lipídico disponível"] --> D1{"Há doença aterosclerótica estabelecida,<br/>clínica ou inequívoca em imagem?"}

  D1 -->|"Sim: síndrome coronariana aguda prévia,<br/>síndrome coronariana crônica, revascularização,<br/>AVC ou AIT, doença arterial periférica,<br/>placa significativa em angiografia, angio-TC<br/>ou ultrassom de carótida e femoral"| C1(["Muito alto risco.<br/>Meta: LDL-C abaixo de 55 mg/dL<br/>E redução de pelo menos 50% do valor basal<br/>— Classe I, nível A na prevenção secundária"])

  D1 -->|"Não"| D2{"Há condição clínica que já define a categoria,<br/>dispensando o cálculo do escore?"}

  D2 -->|"Diabetes com lesão de órgão-alvo,<br/>ou com ao menos três fatores de risco maiores,<br/>ou diabetes tipo 1 de início precoce<br/>com mais de 20 anos de duração"| C2(["Muito alto risco.<br/>Meta: LDL-C abaixo de 55 mg/dL<br/>E redução de pelo menos 50% do basal"])

  D2 -->|"Doença renal crônica grave:<br/>TFGe abaixo de 30 mL/min/1,73 m²"| C3(["Muito alto risco.<br/>Meta: LDL-C abaixo de 55 mg/dL<br/>E redução de pelo menos 50% do basal"])

  D2 -->|"Hipercolesterolemia familiar com doença<br/>aterosclerótica ou com outro fator<br/>de risco maior associado"| C4(["Muito alto risco.<br/>Meta: LDL-C abaixo de 55 mg/dL<br/>E redução de pelo menos 50% do basal"])

  D2 -->|"Fator isolado muito elevado: colesterol total<br/>acima de 310 mg/dL, LDL-C acima de 190 mg/dL<br/>ou pressão arterial de 180/110 mmHg ou mais;<br/>hipercolesterolemia familiar sem outro fator maior;<br/>diabetes sem lesão de órgão-alvo com 10 anos ou mais<br/>de duração ou com outro fator associado;<br/>doença renal crônica moderada, TFGe de 30 a 59"| C5(["Alto risco.<br/>Meta: LDL-C abaixo de 70 mg/dL<br/>E redução de pelo menos 50% do basal"])

  D2 -->|"Nenhuma dessas condições"| P1["Calcular SCORE2, abaixo de 70 anos,<br/>ou SCORE2-OP, a partir de 70 anos:<br/>risco de evento cardiovascular fatal<br/>e não fatal em 10 anos"]

  P1 --> D3{"Risco estimado em 10 anos"}

  D3 -->|"20% ou mais"| C6(["Muito alto risco.<br/>Meta: LDL-C abaixo de 55 mg/dL<br/>E redução de pelo menos 50% do basal"])

  D3 -->|"De 10% a menos de 20%"| C7(["Alto risco.<br/>Meta: LDL-C abaixo de 70 mg/dL<br/>E redução de pelo menos 50% do basal"])

  D3 -->|"De 2% a menos de 10%"| C8(["Risco moderado.<br/>Meta: LDL-C abaixo de 100 mg/dL"])

  D3 -->|"Menos de 2%"| C9(["Baixo risco.<br/>Meta de LDL-C abaixo de 116 mg/dL<br/>deve ser considerada"])

  classDef conduta fill:#eef6ef,stroke:#2f7a4f,color:#12301f;
  class C1,C2,C3,C4,C5,C6,C7,C8,C9 conduta;
```

## Árvore de decisão: escalonamento do tratamento hipolipemiante

```mermaid
flowchart TD
  R1["Meta de LDL-C já definida<br/>pela categoria de risco"] --> D4{"Em que contexto o paciente<br/>está sendo tratado?"}

  D4 -->|"Internado por síndrome<br/>coronariana aguda"| D5{"Já vinha em uso de algum hipolipemiante<br/>antes da internação?"}

  D5 -->|"Sim"| C10(["Intensificar a terapia hipolipemiante durante<br/>a internação do próprio evento, para reduzir<br/>mais o LDL-C — Classe I, nível C"])

  D5 -->|"Não, virgem de tratamento"| C11(["Iniciar estatina de alta intensidade combinada<br/>a ezetimiba já na internação, quando não se espera<br/>atingir a meta apenas com estatina<br/>— Classe IIa, nível B"])

  D4 -->|"Ambulatorial"| D6{"O paciente tolera estatina?"}

  D6 -->|"Não, mesmo após nova tentativa<br/>com outra estatina ou outra dose"| C12(["Terapia não estatínica com benefício cardiovascular<br/>comprovado — ezetimiba, anticorpo anti-PCSK9<br/>ou ácido bempedoico —, isolada ou combinada,<br/>escolhida pela magnitude de redução ainda<br/>necessária — Classe I"])

  D6 -->|"Sim"| P2["Estatina de alta intensidade na maior dose<br/>tolerada, até a meta da categoria<br/>— Classe I, nível A"]

  P2 --> D7{"Meta de LDL-C atingida?"}

  D7 -->|"Sim"| C13(["Manter o esquema e reavaliar o perfil lipídico<br/>no seguimento próprio da categoria de risco"])

  D7 -->|"Não"| P3["Associar ezetimiba à estatina<br/>em dose máxima tolerada<br/>— Classe I, nível B"]

  P3 --> D8{"Meta atingida com estatina<br/>em dose máxima tolerada mais ezetimiba?"}

  D8 -->|"Sim"| C14(["Manter o esquema e seguir o paciente"])

  D8 -->|"Não"| D9{"Qual é o cenário deste paciente?"}

  D9 -->|"Prevenção secundária,<br/>muito alto risco"| C15(["Associar inibidor de PCSK9<br/>— Classe I, nível A"])

  D9 -->|"Hipercolesterolemia familiar de muito alto risco:<br/>com doença aterosclerótica ou outro fator maior"| C16(["Associar inibidor de PCSK9<br/>— Classe I, nível C"])

  D9 -->|"Prevenção primária,<br/>muito alto risco, sem<br/>hipercolesterolemia familiar"| C17(["Inibidor de PCSK9 pode ser considerado<br/>— Classe IIb, nível C"])

  D9 -->|"Alto risco, ainda fora da meta"| C18(["Acrescentar ácido bempedoico à estatina em dose<br/>máxima tolerada, com ou sem ezetimiba,<br/>deve ser considerado — Classe IIa"])

  classDef conduta fill:#eef6ef,stroke:#2f7a4f,color:#12301f;
  class C10,C11,C12,C13,C14,C15,C16,C17,C18 conduta;
```

## As metas, reunidas

A atualização de 2025 declara explicitamente que estas metas **não mudaram** em
relação a 2019.

| Categoria | Meta de LDL-C | Também |
|---|---|---|
| Muito alto risco | abaixo de 55 mg/dL, ou 1,4 mmol/L | redução de pelo menos 50% do basal |
| Alto risco | abaixo de 70 mg/dL, ou 1,8 mmol/L | redução de pelo menos 50% do basal |
| Risco moderado | abaixo de 100 mg/dL, ou 2,6 mmol/L | — |
| Baixo risco | abaixo de 116 mg/dL, ou 3,0 mmol/L | deve ser considerada |

**Metas secundárias**, para quando o LDL-C isolado não conta a história toda —
hipertrigliceridemia, diabetes, síndrome metabólica, LDL-C muito baixo:

| | Muito alto risco | Alto risco | Risco moderado |
|---|---|---|---|
| Não-HDL-C | abaixo de 85 mg/dL | abaixo de 100 mg/dL | abaixo de 130 mg/dL |
| ApoB | abaixo de 65 mg/dL | abaixo de 80 mg/dL | abaixo de 100 mg/dL |

## O paciente que volta a ter evento: a meta abaixo de 40 mg/dL

Para quem tem doença aterosclerótica e **sofre um segundo evento vascular em até
2 anos** — não necessariamente do mesmo tipo do primeiro — já em uso de estatina
na dose máxima tolerada, uma meta de LDL-C **abaixo de 40 mg/dL, ou 1,0 mmol/L,
pode ser considerada: Classe IIb, nível B**.

Repare no que a classe diz e no que não diz. IIb é o degrau mais fraco entre as
recomendações a favor — a diretriz abre a porta, não empurra o paciente por ela.
E o gatilho é específico: **evento recorrente em janela de 2 anos, já sob
tratamento**, não "paciente grave" em sentido genérico.

## O que as árvores não mostram

**Lipoproteína(a) deve ser dosada ao menos uma vez na vida.** É determinada
geneticamente e praticamente não varia ao longo da vida, então uma única
dosagem basta. Valores **acima de 50 mg/dL, ou 105 nmol/L, devem ser
considerados fator agravante de risco cardiovascular em todo adulto — Classe
IIa, nível B** —, e quanto mais alta a Lp(a), maior o acréscimo de risco. Ela não
entra como ramo porque não muda a meta: reclassifica o risco, que é o que a
primeira árvore já faz.

**Modificadores de risco não são ramos, e por bom motivo.** Aterosclerose
coronariana subclínica, escore de cálcio coronariano elevado e proteína C-reativa
de alta sensibilidade acima de 2 mg/L refinam a estimativa do SCORE2 no paciente
de risco limítrofe. Colocá-los na árvore transformaria uma decisão de reclassificação
em uma cascata de ramos que ninguém percorre à beira do leito — o lugar deles é a
prosa e o julgamento clínico.

**Estilo de vida não desaparece porque não está desenhado.** Dieta, peso,
atividade física e cessação do tabagismo são a base sobre a qual toda a árvore
farmacológica se apoia, em qualquer categoria.

**Populações que a atualização de 2025 tratou à parte**, cada uma com recomendação
própria: pessoas vivendo com HIV a partir de 40 anos em prevenção primária
— estatina recomendada independentemente do risco estimado e do LDL-C, Classe I,
nível B —; pacientes sob quimioterapia com antraciclina e alto ou muito alto risco
de cardiotoxicidade — estatina deve ser considerada, Classe IIa, nível B —;
hipercolesterolemia familiar homozigótica a partir dos 5 anos fora da meta apesar
de terapia máxima — evinacumabe deve ser considerado, Classe IIa, nível B —; e
hipertrigliceridemia grave da síndrome de quilomicronemia familiar, acima de
750 mg/dL — volanesorsena 300 mg por semana deve ser considerada, Classe IIa,
nível B.

**Suplemento alimentar e vitamina não têm lugar aqui.** A diretriz é explícita:
não há indicação para reduzir LDL-C nem risco aterosclerótico — **Classe III,
nível B**. É recomendação contra, não ausência de recomendação.

## Uma nota de procedência sobre esta página

O nível de evidência das duas recomendações de **ácido bempedoico** não pôde ser
lido com segurança na extração do PDF da diretriz — a fonte do documento é
subconjunto sem mapa de caracteres, e os glifos de classe e nível saem ambíguos.
A **classe** está afirmada aqui a partir da redação literal da própria diretriz,
usando a convenção de linguagem que ela define ("é recomendado" para Classe I,
"deve ser considerado" para Classe IIa). O nível correspondente é
`VERIFICAÇÃO HUMANA NECESSÁRIA` — conferir na Tabela de Recomendação 2 impressa
antes de considerar esta página fechada.

Todo o restante — metas, categorias de risco, classes e níveis de estatina,
ezetimiba, inibidor de PCSK9, síndrome coronariana aguda, Lp(a) e populações
especiais — foi lido diretamente do texto das diretrizes de 2019 e 2025.
