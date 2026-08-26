---
title: "Fluxograma: Aneurisma de Aorta Abdominal — seguimento por tamanho e indicação de reparo (ESC 2024)"
slug: fluxograma-aneurisma-de-aorta-abdominal-seguimento-e-indicacao-de-reparo
theme: "Aorta e doença arterial periférica"
kind: fluxograma
fonte_producao: chatgpt
review_status: revisado
review_note: "Limiares de reparo eletivo (≥5,5 cm no homem, ≥5,0 cm na mulher) e o critério de crescimento rápido (≥1,0 cm em 12 meses) foram conferidos de forma cruzada e independente em duas fontes: o documento já publicado neste tema (aneurisma-de-aorta-abdominal-rastreamento-seguimento-e-indicacao-de-reparo, com fontes NCBI Bookshelf/American Family Physician) e a diretriz 2024 ESC for the management of peripheral arterial and aortic diseases (European Heart Journal 2024;45(36):3538-3700, DOI 10.1093/eurheartj/ehae179), cujo PMID 39210722 foi confirmado via PubMed esummary (título, revista, volume, páginas e data batendo exatamente) — mesma diretriz já usada nos outros três fluxogramas deste tema. Os intervalos de vigilância por faixa de diâmetro foram mantidos dentro do que já está verificado e publicado no corpus (revisão sistemática de crescimento/ruptura citada no documento-base), evitando um valor de intervalo de 3 meses para a faixa 5,0-5,4 cm que apareceu em apenas uma fonte de resumo de acesso condicionado e não pôde ser corroborado de forma independente — nesse ponto ficou o intervalo mais conservador e já em uso no acervo (6 a 12 meses), sem inventar número não conferido. EVAR como via preferencial de reparo eletivo hoje nos EUA (80% dos reparos eletivos) já está no documento-base, fonte PMC. Nada nesta árvore foi escrito de memória sem checagem contra uma dessas fontes."
source_refs: ["2024 ESC Guidelines for the management of peripheral arterial and aortic diseases · European Heart Journal · 2024 · 45(36):3538-3700 · PMID 39210722 · 10.1093/eurheartj/ehae179", "Thresholds for abdominal aortic aneurysm repair · NCBI Bookshelf · https://www.ncbi.nlm.nih.gov/books/NBK556917/", "Systematic review and meta-analysis of the growth and rupture rates of small abdominal aortic aneurysms · NCBI Bookshelf · https://www.ncbi.nlm.nih.gov/books/NBK261036/", "Abdominal Aortic Aneurysm · American Family Physician · 2022 · https://www.aafp.org/afp/2022/0800/abdominal-aortic-aneurysm", "Endovascular Aneurysm Repair Versus Open Surgical Repair in Treating Abdominal Aortic Aneurysm · PMC · https://www.ncbi.nlm.nih.gov/pmc/articles/PMC11540110/"]
---

# Fluxograma: Aneurisma de Aorta Abdominal — seguimento por tamanho e indicação de reparo (ESC 2024)

Os quatro fluxogramas já publicados neste tema cobrem emergência aórtica (síndrome
aórtica aguda), isquemia aguda de membro, a distinção entre claudicação/CLTI/isquemia
aguda e o diagnóstico de doença arterial periférica pelo ITB — todos cenários agudos ou
de investigação inicial. Faltava a árvore de decisão do cenário **eletivo e crônico**
mais comum na prática do aneurisma de aorta abdominal (AAA): uma vez identificado o
aneurisma, com que frequência reavaliar por tamanho, e em que ponto a vigilância cede
lugar à indicação de reparo. Esta árvore fecha essa lacuna, complementando o documento
já publicado no tema sobre rastreamento, seguimento e indicação de reparo.

A ESC 2024 fundiu, pela primeira vez, doença arterial periférica e doença aórtica num
único documento (substituindo as diretrizes de 2014 e 2017), fixando classe e nível de
evidência para os limiares que já eram praticados: reparo eletivo recomendado a partir
de **5,5 cm no homem** e **5,0 cm na mulher** — a mulher opera mais cedo por maior risco
de ruptura relativo ao diâmetro —, e crescimento acelerado (**≥1,0 cm em 12 meses**)
como indicação cirúrgica independente do diâmetro absoluto.

## Árvore de decisão

```mermaid
flowchart TD
  R0["AAA identificado — diâmetro aórtico infrarrenal<br/>máximo medido por USG, angio-TC ou RM"] --> D1{"Sintomático (dor abdominal<br/>ou lombar nova) ou sinais de ruptura<br/>(hipotensão, massa pulsátil dolorosa)?"}

  D1 -->|Sim| C1(["Emergência — conduzir como síndrome aórtica aguda:<br/>estabilizar e encaminhar para reparo imediato<br/>(ver fluxograma dedicado de síndrome aórtica aguda)"])

  D1 -->|Não| D2{"Diâmetro ≥5,5 cm no homem<br/>ou ≥5,0 cm na mulher?"}

  D2 -->|Sim| D3{"Anatomia favorável para reparo<br/>endovascular — colo proximal adequado,<br/>acessos ilíacos, sem tortuosidade proibitiva?"}

  D3 -->|Sim| C2(["Reparo endovascular eletivo (EVAR) — via preferencial<br/>hoje na maioria dos reparos eletivos de AAA intacto;<br/>seguimento com angio-TC em 1 mês e USG anual"])
  D3 -->|Não| C3(["Reparo aberto eletivo, com avaliação<br/>cardiovascular perioperatória prévia"])

  D2 -->|Não| D4{"Crescimento documentado ≥1,0 cm<br/>em 12 meses, mesmo abaixo<br/>do limiar de diâmetro?"}

  D4 -->|Sim| C4(["Encaminhar para avaliação de reparo eletivo por<br/>critério de crescimento rápido, mesmo abaixo<br/>do limiar de diâmetro — repetir o raciocínio<br/>de anatomia (EVAR versus reparo aberto)"])

  D4 -->|Não| D5{"Faixa de diâmetro atual?"}

  D5 -->|"3,0 a 3,9 cm"| C5(["Vigilância por ultrassonografia<br/>a cada 2 a 3 anos"])
  D5 -->|"4,0 a 4,4 cm"| C6(["Vigilância por ultrassonografia<br/>a cada 1 a 2 anos"])
  D5 -->|"4,5 cm até o limiar de reparo"| C7(["Vigilância por ultrassonografia<br/>a cada 6 a 12 meses"])

  classDef conduta fill:#eef6ef,stroke:#2f7a4f,color:#12301f;
  class C1,C2,C3,C4,C5,C6,C7 conduta;
```

## Por que o limiar difere entre homem e mulher

O risco de ruptura de um AAA não é função só do diâmetro absoluto — é maior, para o
mesmo diâmetro, na mulher. É por isso que o limiar de reparo eletivo recomendado é mais
baixo nela (5,0 cm) do que no homem (5,5 cm), e não uma diferença arbitrária de
protocolo. Abaixo do limiar de diâmetro, a razão de chances de ruptura por aumento de
1 cm no diâmetro é próxima nos dois sexos (cerca de 5,0-5,3), mas a mulher parte de um
risco basal mais alto na mesma faixa de tamanho.

## Por que o critério de crescimento existe além do diâmetro

Um aneurisma que cresce rápido — ≥1,0 cm em 12 meses — sinaliza instabilidade da parede
que o diâmetro absoluto isolado não captura. É por isso que a indicação cirúrgica não
espera o AAA atingir o limiar de tamanho quando esse ritmo de crescimento já foi
documentado: o risco de ruptura no intervalo até a próxima vigilância programada deixa
de ser aceitável.

## EVAR versus reparo aberto

A decisão entre via endovascular e cirurgia aberta depende primariamente da anatomia —
comprimento e angulação do colo proximal, calibre e tortuosidade dos acessos ilíacos —,
não de preferência isolada. Na prática atual dos EUA, o reparo endovascular já responde
por cerca de 80% dos reparos eletivos de AAA intacto, refletindo tanto a evolução das
endopróteses quanto o perfil de risco cirúrgico mais favorável do EVAR no perioperatório
imediato; o reparo aberto continua sendo a alternativa quando a anatomia não é favorável
ou quando a durabilidade de longo prazo pesa mais na decisão compartilhada com o
paciente.

## Racional da vigilância por faixa de tamanho

Abaixo do limiar de reparo, o risco anual de ruptura cresce de forma não linear com o
diâmetro — próximo de 0% na faixa de 3,0-3,9 cm, em torno de 1% na faixa de 4,0-4,9 cm —,
e é esse gradiente de risco que justifica encurtar o intervalo de reavaliação à medida
que o aneurisma se aproxima do limiar cirúrgico, em vez de manter uma frequência fixa de
exame desde o diagnóstico.
