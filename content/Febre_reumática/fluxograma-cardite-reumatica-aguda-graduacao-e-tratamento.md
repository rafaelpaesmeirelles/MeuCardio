---
title: "Fluxograma: Cardite reumática aguda — graduação de gravidade e conduta terapêutica (SBC 2022)"
slug: fluxograma-cardite-reumatica-aguda-graduacao-e-tratamento
theme: "Febre reumática"
kind: fluxograma
fonte_producao: chatgpt
review_status: revisado
review_note: "Fonte é a Diretriz de Miocardites da Sociedade Brasileira de Cardiologia — 2022 (seção 7, Cardite Reumática, Tabelas 39 e 40), já lida e usada no documento em prosa 'Cardite reumática aguda: graduação de gravidade e tratamento (SBC 2022)' publicado nesta mesma pasta — todas as doses, classes e níveis deste fluxograma foram conferidos contra aquele documento, sem alterar nenhum valor. PMID da diretriz (versão em inglês, Arq Bras Cardiol) confirmado nesta sessão via PubMed E-utilities (esummary): 35830116 — título 'Brazilian Society of Cardiology Guideline on Myocarditis - 2022' batendo a publicação. Pendente revisão médica independente antes de uso assistencial."
source_refs: ["Sociedade Brasileira de Cardiologia. Brazilian Society of Cardiology Guideline on Myocarditis – 2022. Arquivos Brasileiros de Cardiologia. 2022. PMID: 35830116 — seção 7 (Cardite Reumática), Tabelas 39 (exames diagnósticos) e 40 (tratamento por gravidade)."]
---

# Fluxograma: Cardite reumática aguda — graduação de gravidade e conduta terapêutica (SBC 2022)

Este fluxograma pressupõe diagnóstico já fechado — critérios de Jones
revisados de 2015, cobertos no outro fluxograma deste tema — e a cardite já
caracterizada como manifestação maior. O que ele decide é **o que fazer**, a
partir de uma graduação cumulativa em quatro faixas (subclínica, leve,
moderada, grave), que é o eixo central da Tabela 40 da diretriz brasileira de
2022. A cardite reumática é uma pancardite, mas a manifestação dominante é
valvar — **valvulite aguda em 90% dos casos** —, e é por isso que a gravidade
se apoia tanto no achado clínico quanto na regurgitação valvar ao eco.

## Árvore de decisão

```mermaid
flowchart TD
  R0["Febre reumática aguda com cardite confirmada<br/>(critérios de Jones já aplicados),<br/>ecocardiograma transtorácico realizado"] --> D1{"Qual a faixa de gravidade<br/>da cardite?"}

  D1 -->|"Subclínica ou leve, com artrite<br/>e/ou pericardite associada"| C1(["AAS 100 mg/kg/dia (máx. 3-4 g) em 4 doses, OU<br/>naproxeno 20 mg/kg/dia (máx. 1.000 mg) em 2 doses —<br/>total de 2 semanas — Classe I, nível B"])

  D1 -->|"Subclínica a leve,<br/>sem artrite/pericardite associada"| D2{"Optar por corticoide<br/>— é opcional nesta faixa?"}

  D2 -->|"Sim"| C2(["Prednisona 0,5 a 1 mg/kg/dia (máx. 50 mg) VO, 15 dias,<br/>depois redução semanal de 20% da dose —<br/>total de 4 a 8 semanas — Classe IIb, nível B"])

  D2 -->|"Não"| C3(["Controle de sintomas e monitorização da evolução,<br/>sem corticoide — reavaliação clínica e<br/>ecocardiográfica seriada"])

  D1 -->|"Moderada a grave"| C4(["Prednisona 1 a 2 mg/kg/dia (máx. 60 mg) VO, 15 dias,<br/>depois redução semanal de 20% da dose — total em<br/>torno de 12 semanas — Classe I, nível B. Associar<br/>hospitalização (Classe IIa) e, se houver disfunção<br/>ventricular, diurético e drogas neuro-hormonais<br/>— Classe I, nível C"])

  D1 -->|"Grave, já refratária ao<br/>tratamento inicial"| D3{"Mantém sintomas limitantes de IC,<br/>com regurgitação valvar importante<br/>e/ou disfunção sistólica, apesar<br/>do tratamento inicial adequado?"}

  D3 -->|"Sim — refratariedade<br/>confirmada"| C5(["Cirurgia valvar na fase aguda — Classe I, nível B:<br/>plástica mitral, com técnica que permita<br/>crescimento do anel; prótese mecânica<br/>preferencial na valva aórtica"])

  D3 -->|"Sem indicação cirúrgica<br/>imediata definida"| C6(["Considerar metilprednisolona 30 mg/kg/dia,<br/>em ciclos semanais (pulsoterapia) nos casos<br/>graves refratários — Classe IIb, nível B;<br/>definir esquema e monitorização em centro especializado"])

  classDef conduta fill:#eef6ef,stroke:#2f7a4f,color:#12301f;
  class C1,C2,C3,C4,C5,C6 conduta;
```

## O que vale para todo ramo, e por isso não está na árvore

**Erradicação estreptocócica é Classe I, nível C, para todo paciente com
cardite reumática**, independentemente da faixa de gravidade — mesmo quando o
quadro é interpretado como resposta imune tardia à infecção, não infecção
ativa no momento: penicilina G benzatina IM em dose única (1.200.000 UI se
20 kg ou mais; 600.000 UI se menos de 20 kg), ou amoxicilina 50 mg/kg/dia
(máx. 1.500 mg) em 3 doses por 10 dias; eritromicina 40 mg/kg/dia
(máx. 1.000 mg) em 4 doses por 10 dias no alérgico à penicilina. É a dose que
erradica o episódio agudo — a profilaxia secundária que se segue, com a
mesma penicilina em intervalo repetido, é decisão à parte, coberta em
documento próprio deste tema.

**Repouso é Classe IIa, nível C, no caso moderado ou grave** — recomendação
que acompanha qualquer conduta farmacológica escolhida nessas duas faixas,
não é alternativa a ela.

## O que a árvore não mostra

**A tensão interna da própria diretriz sobre corticoide na forma leve.** O
texto corrido diz que a forma subclínica/leve "implica controle dos sintomas
e monitoramento da evolução", e que só a forma moderada/grave "implica uso de
corticosteroides" — mas a Tabela 40 traz uma linha de prednisona para o caso
subclínico a leve, ainda que como Classe IIb. A leitura que concilia as duas
partes do texto é a que a árvore usa: corticoide não é rotina na forma leve,
é opção — e quem decidir isso à beira do leito deve conferir o texto integral
da diretriz, não só este resumo.

**Troponina normal não afasta cardite reumática.** O dano miocárdico costuma
ser pequeno nessa doença, por isso a troponina como critério diagnóstico é
apenas Classe IIb, nível B — não é exame usado para graduar gravidade nesta
árvore.

**Cintilografia com Gálio-67 é o exame de imagem de escolha quando a
investigação etiológica precisa ir além do ecocardiograma** (Classe IIa,
nível B) — a ressonância cardíaca é Classe IIb aqui, ao contrário do peso que
tem na miocardite viral, porque a diretriz reconhece que faltam trabalhos
específicos para febre reumática e que o acometimento é prioritariamente
valvar, não miocárdico.

**Miocardite reumática propriamente dita** — insuficiência cardíaca manifesta
sem valvopatia aguda anatomicamente importante — deve levar a investigar
diagnósticos diferenciais de miocardite antes de tratar como cardite
reumática típica; este fluxograma pressupõe que a valvulite já esteja
caracterizada.

**Cerca de metade dos casos de cardite aguda evolui para cardiopatia
reumática crônica** (tipicamente valvopatia mitral e/ou aórtica) — o
seguimento dessa evolução, e a decisão entre reparo e substituição valvar na
doença já estabelecida, têm documento próprio nesta pasta e não estão
cobertos aqui.
