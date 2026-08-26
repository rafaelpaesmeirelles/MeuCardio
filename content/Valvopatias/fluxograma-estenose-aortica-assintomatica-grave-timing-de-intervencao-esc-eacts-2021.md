---
title: "Fluxograma: Estenose Aórtica Grave Assintomática — Quando Intervir (ESC/EACTS 2021)"
slug: fluxograma-estenose-aortica-assintomatica-grave-timing-de-intervencao-esc-eacts-2021
theme: "Valvopatias"
kind: fluxograma
fonte_producao: chatgpt
review_status: revisado
review_note: "Árvore construída a partir de dois documentos já publicados e revisados nesta pasta — 'estenose-aortica-grave-decisao-tavi-vs-savr-esceacts-2021.md' (que já lista os critérios de indicação independente de sintomas espontâneos: teste de esforço anormal, FEVE <50%, EA muito grave, progressão rápida, BNP elevado) e 'troca-valvar-aortica-precoce-na-estenose-aortica-assintomatica-grave-metanalise-de-4-rcts.md' — e da diretriz ESC/EACTS 2021 diretamente. As classes e níveis de recomendação (I/B para FEVE ≤50%, I/C para teste de esforço anormal e para cirurgia concomitante, IIa/C para os critérios adicionais de EA muito grave/progressão/BNP/hipertensão pulmonar) seguem a estrutura padrão da Seção 5.2.1 da diretriz. PMID 34453165 e PMID 40831305 conferidos nesta sessão via PubMed E-utilities (esummary): título, revista e ano batem exatamente com o citado. Este fluxograma não duplica 'fluxograma-estenose-aortica-decisao-de-intervencao-esc-eacts-2021.md', já publicado nesta pasta — aquele parte da indicação de intervenção JÁ ESTABELECIDA e decide o modo (Heart Team: TAVI vs. cirurgia); este responde à pergunta que vem antes, no paciente SEM sintomas espontâneos: a intervenção está indicada ou não."
source_refs: ["Vahanian A, Beyersdorf F, Praz F, et al.; ESC/EACTS Scientific Document Group. 2021 ESC/EACTS Guidelines for the management of valvular heart disease. Eur Heart J. 2022;43(7):561-632. DOI: 10.1093/eurheartj/ehab395. PMID: 34453165 — Seção 5.2.1 (indicações de intervenção na estenose aórtica), já citada e verificada em outros documentos desta pasta; título/revista/ano reconferidos nesta sessão via PubMed E-utilities.", "Song Q, Liu R, Yang K, Tu X, Tan H, Fan C, Li X. Early Aortic Valve Replacement of Asymptomatic Severe Aortic Stenosis: A Meta-Analysis of Randomized Controlled Trials. J Am Heart Assoc. 2025;14:e041283. DOI: 10.1161/JAHA.125.041283. PMID: 40831305 — já publicado como documento próprio nesta pasta; título/revista/ano reconferidos nesta sessão via PubMed E-utilities."]
---

# Fluxograma: Estenose Aórtica Grave Assintomática — Quando Intervir (ESC/EACTS 2021)

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
  R0["Estenose aórtica grave confirmada<br/>por critérios ecocardiográficos,<br/>paciente sem sintomas relatados"] --> D1{"Teste ergométrico mostra sintomas,<br/>queda de pressão arterial ou resposta<br/>anormal ao esforço?"}

  D1 -->|"Sim"| C1(["Intervenção indicada — sintoma<br/>mascarado desmascarado pelo esforço<br/>equivale a estenose sintomática,<br/>Classe I, Nível C"])

  D1 -->|"Não, teste normal<br/>ou não realizável"| D2{"FEVE ≤50%, sem outra<br/>causa identificável?"}

  D2 -->|"Sim"| C2(["Intervenção indicada — disfunção<br/>de ventrículo esquerdo por sobrecarga<br/>de pressão, Classe I, Nível B"])

  D2 -->|"Não"| D3{"Baixo risco cirúrgico E pelo menos<br/>um destes: estenose muito grave,<br/>progressão hemodinâmica rápida,<br/>BNP muito elevado sem outra causa,<br/>ou hipertensão pulmonar grave<br/>em repouso?"}

  D3 -->|"Sim"| C3(["Intervenção deve ser<br/>considerada — Classe IIa, Nível C"])

  D3 -->|"Não"| D4{"Cirurgia cardíaca já indicada<br/>por outro motivo — revascularização,<br/>cirurgia de aorta ou de outra valva?"}

  D4 -->|"Sim"| C4(["Troca valvar aórtica concomitante<br/>— Classe I, Nível C"])

  D4 -->|"Não"| C5(["Vigilância clínica e ecocardiográfica<br/>periódica, com teste ergométrico e<br/>biomarcadores reavaliados no seguimento"])

  classDef conduta fill:#eef6ef,stroke:#2f7a4f,color:#12301f;
  class C1,C2,C3,C4,C5 conduta;
```

## Por que o teste ergométrico vem antes da fração de ejeção

Boa parte dos pacientes que se dizem "assintomáticos" na consulta apenas
reduziram a própria atividade sem perceber — é um viés comum em quem convive com
limitação progressiva. O teste ergométrico, feito sob supervisão em quem
realmente não relata sintoma espontâneo (e é **contraindicado** em quem já tem
sintoma claro), expõe esse mascaramento: sintoma limitante, queda da pressão
arterial abaixo do valor basal, ou elevação insuficiente da pressão ao esforço
reclassificam o paciente como sintomático na prática, mesmo sem queixa
espontânea — e a conduta passa a ser a mesma da estenose sintomática.

## Os critérios do nó D3, resumidos

O nó de decisão D3 reúne quatro achados que, isoladamente, cada um já sustenta a
recomendação Classe IIa em paciente de baixo risco cirúrgico — não são
bifurcações sucessivas, são entradas independentes da mesma avaliação:

- **estenose muito grave**, pelo pico de velocidade transvalvar muito acima do
  corte de gravidade padrão;
- **progressão hemodinâmica rápida** entre dois ecocardiogramas seriados;
- **BNP marcadamente elevado**, acima do esperado para idade e sexo, sem outra
  causa que explique a elevação (arritmia, disfunção renal, outra cardiopatia);
- **hipertensão pulmonar grave em repouso**, sem outra explicação.

A metanálise de 4 ensaios randomizados já publicada nesta pasta
(`troca-valvar-aortica-precoce-na-estenose-aortica-assintomatica-grave-metanalise-de-4-rcts.md`)
reforça a mesma direção — no agregado dos 4 estudos, intervenção precoce teve
benefício de sobrevida e de desfecho composto sobre vigilância pura —, mas
naquele documento a própria conclusão avisa que o corte de "assintomático grave"
precisa ser confirmado por teste ergométrico, não por ausência de queixa
espontânea. É exatamente o nó D1 desta árvore.

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
