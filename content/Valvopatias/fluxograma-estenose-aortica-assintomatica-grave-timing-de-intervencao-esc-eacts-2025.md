---
title: "Fluxograma: Estenose Aórtica Grave Assintomática — Quando Intervir (ESC/EACTS 2025)"
slug: fluxograma-estenose-aortica-assintomatica-grave-timing-de-intervencao-esc-eacts-2025
theme: "Valvopatias"
kind: fluxograma
fonte_producao: chatgpt
review_status: revisado
review_note: "Atualizado para a diretriz ESC/EACTS 2025, que substituiu a estratégia de 2021 e incorporou quatro ensaios randomizados. Conferidos diretamente na seção 8.4.2 e na tabela de recomendações: FEVE <50% sem outra causa (I/B); intervenção precoce como alternativa à vigilância em estenose grave de alto gradiente, FEVE ≥50%, baixo risco procedimental e teste de esforço normal se factível (IIa/A); características de alto risco com baixo risco procedimental (IIa/B); e queda sustentada da PA >20 mmHg no esforço (IIa/C). Sintomas provocados no esforço reclassificam o paciente como sintomático. O fluxograma não usa hipertensão pulmonar como critério autônomo porque ela não integra a lista 2025."
source_refs: ["Praz F, Borger MA, Lanz J, et al.; ESC/EACTS Scientific Document Group. 2025 ESC/EACTS Guidelines for the management of valvular heart disease. Eur Heart J. 2025;46(44):4635-4747. DOI: 10.1093/eurheartj/ehaf194. PMID: 40878295 — seção 8.4.2 e Recommendation Table 4.", "Song Q, Liu R, Yang K, Tu X, Tan H, Fan C, Li X. Early Aortic Valve Replacement of Asymptomatic Severe Aortic Stenosis: A Meta-Analysis of Randomized Controlled Trials. J Am Heart Assoc. 2025;14:e041283. DOI: 10.1161/JAHA.125.041283. PMID: 40831305."]
---

# Fluxograma: Estenose Aórtica Grave Assintomática — Quando Intervir (ESC/EACTS 2025)

A pasta já tem um fluxograma para a decisão entre TAVI e cirurgia — mas aquele
parte de uma indicação de intervenção **já estabelecida**. A pergunta clínica mais
difícil, e a que costuma ser resolvida errado, vem antes: num paciente com
estenose aórtica grave que **diz não ter sintomas**, quando a intervenção deve
ser indicada mesmo assim? Esperar o sintoma clássico aparecer tem custo — o
paciente pode chegar já com dano ventricular ou evento embólico —, mas intervir
cedo demais expõe alguém realmente assintomático ao risco de um procedimento que
poderia esperar. Este fluxograma organiza os critérios objetivos que decidem essa
fronteira.

## Árvore de decisão

```mermaid
flowchart TD
  R0["Estenose aórtica grave confirmada<br/>por avaliação integrada,<br/>paciente sem sintomas relatados"] --> D1{"Teste de esforço factível e seguro<br/>provoca sintomas atribuíveis<br/>à estenose aórtica?"}

  D1 -->|"Sim"| C1(["Reclassificar como estenose<br/>sintomática e indicar intervenção,<br/>se expectativa de vida e benefício<br/>esperado forem compatíveis"])

  D1 -->|"Não, ou teste não factível"| D1b{"Queda sustentada da PA >20 mmHg<br/>durante o teste, sem sintomas?"}

  D1b -->|"Sim"| C1b(["Intervenção deve ser considerada —<br/>Classe IIa, Nível C"])

  D1b -->|"Não"| D2{"FEVE <50%, sem outra<br/>causa identificável?"}

  D2 -->|"Sim"| C2(["Intervenção recomendada —<br/>Classe I, Nível B"])

  D2 -->|"Não"| D3{"Estenose grave de alto gradiente,<br/>FEVE ≥50%, risco procedimental baixo<br/>e teste normal, se factível?"}

  D3 -->|"Sim"| C3(["Intervenção precoce deve ser<br/>considerada como alternativa à<br/>vigilância ativa — Classe IIa,<br/>Nível A; decisão compartilhada<br/>pelo Heart Team"])

  D3 -->|"Não"| D4{"Risco procedimental baixo e fator<br/>de alto risco: Vmax >5 m/s ou gradiente<br/>médio ≥60 mmHg; calcificação grave +<br/>progressão Vmax ≥0,3 m/s/ano; BNP/NT-proBNP<br/>>3x normal repetido; ou FEVE <55%?"}

  D4 -->|"Sim"| C4(["Intervenção deve ser considerada —<br/>Classe IIa, Nível B"])

  D4 -->|"Não"| C5(["Vigilância clínica e ecocardiográfica<br/>ativa pelo menos a cada 6 meses,<br/>com educação para relatar sintomas<br/>e repetição do teste quando factível"])

  classDef conduta fill:#eef6ef,stroke:#2f7a4f,color:#12301f;
  class C1,C1b,C2,C3,C4,C5 conduta;
```

## Por que o teste de esforço vem antes da fração de ejeção

Boa parte dos pacientes que se dizem "assintomáticos" na consulta apenas
reduziram a própria atividade sem perceber — é um viés comum em quem convive com
limitação progressiva. O teste ergométrico, feito sob supervisão em quem
realmente não relata sintoma espontâneo (e é **contraindicado** em quem já tem
sintoma claro), expõe esse mascaramento: sintoma limitante atribuível à
estenose reclassifica o paciente como sintomático, mesmo sem queixa espontânea,
e a conduta passa a ser a mesma da estenose sintomática. Uma
queda sustentada de pressão >20 mmHg, sem sintomas, é uma indicação distinta e
mais fraca (IIa/C), não deve ser rotulada como Classe I.

## Os critérios do nó D4, resumidos

O nó de decisão D4 reúne quatro achados que, isoladamente, cada um já sustenta a
recomendação Classe IIa/B em paciente de baixo risco procedimental — não são
bifurcações sucessivas, são entradas independentes da mesma avaliação:

- **estenose muito grave**, pelo pico de velocidade transvalvar muito acima do
  corte de gravidade padrão;
- **progressão hemodinâmica rápida** entre dois ecocardiogramas seriados;
- **BNP marcadamente elevado**, acima do esperado para idade e sexo, sem outra
  causa que explique a elevação (arritmia, disfunção renal, outra cardiopatia);
- **FEVE <55%**, sem outra explicação.

A metanálise de 4 ensaios randomizados já publicada nesta pasta
(`troca-valvar-aortica-precoce-na-estenose-aortica-assintomatica-grave-metanalise-de-4-rcts.md`)
reforça a redução de desfechos compostos, mas não autoriza afirmar benefício de
mortalidade em todos os pacientes. No EARLY TAVR, a diferença do composto foi
fortemente influenciada por hospitalização/intervenção não planejada, sem
diferença significativa isolada de mortalidade ou AVC em cinco anos.

## O que a árvore não mostra

- **Esta árvore não decide o modo de intervenção.** Uma vez indicada a
  intervenção por qualquer um dos ramos acima, a escolha entre TAVI e cirurgia
  segue o próprio fluxograma desta pasta,
  `fluxograma-estenose-aortica-decisao-de-intervencao-esc-eacts-2021.md`, que
  pondera características clínicas, anatômicas, experiência do centro e
  preferência do paciente pelo Heart Team.
- **A definição de gravidade em si não está aqui.** Os cortes que definem
  estenose aórtica grave — velocidade de pico, gradiente médio, área valvar e
  área indexada — e o problema da discordância entre esses parâmetros em 20-30%
  dos casos estão em `valvopatias-estenose-aortica-e-atualizacoes-gerais-esceacts-2021.md`,
  nesta mesma pasta.
- **Estenose de baixo fluxo e baixo gradiente exige avaliação à parte,** com
  ecocardiograma sob estresse com dobutamina ou escore de cálcio por tomografia
  para confirmar gravidade antes mesmo de entrar nesta árvore — pular essa etapa
  e aplicar o nó D2/D3 direto a um gradiente discordante é o erro mais comum
  nesse subgrupo.
- **Expectativa de vida e comorbidade não fazem parte da árvore**, mas continuam
  pesando na decisão real: intervir cedo num paciente com expectativa de vida
  muito curta por outra doença grave raramente muda o desfecho que importa para
  ele.
