---
title: "Fluxograma: Sopro cardíaco na criança — inocente versus patológico"
slug: fluxograma-sopro-cardiaco-na-crianca-inocente-versus-patologico
theme: "Cardiopatias congênitas"
kind: fluxograma
fonte_producao: chatgpt
review_status: revisado
review_note: "PMID 22010618 confirmado via PubMed E-utilities (Frank JE, Jacobe KM. Evaluation and Management of Heart Murmurs in Children. Am Fam Physician. 2011;84(7):793-800); o texto integral oficial foi usado para as características dos sopros nomeados. A atualização oficial da AAFP de 2022 (Ford B, Lara S, Park J. Am Fam Physician. 2022;105(3):250-261) foi conferida para separar neonatos, priorizar encaminhamento ao cardiologista antes de ecocardiograma reflexo e incluir oximetria de pulso. A atualização não possui PMID informado na página oficial; nenhum identificador foi inventado. Pendente revisão médica independente antes de uso assistencial."
source_refs: ["Frank JE, Jacobe KM. Evaluation and Management of Heart Murmurs in Children. American Family Physician. 2011;84(7):793-800. PMID: 22010618.", "Ford B, Lara S, Park J. Heart Murmurs in Children: Evaluation and Management. American Family Physician. 2022;105(3):250-261. https://www.aafp.org/pubs/afp/issues/2022/0300/p250.html — atualização oficial para neonatos, oximetria e critérios de encaminhamento."]
---

# Fluxograma: Sopro cardíaco na criança — inocente versus patológico

Sopro cardíaco é achado extremamente comum na infância, e a maioria é
inocente — sem doença estrutural por trás. O trabalho do exame clínico é
separar, sem exame complementar, quem pode ser tranquilizado na consulta de
quem precisa de ecocardiograma. Duas perguntas fazem a maior parte desse
trabalho: existe **algum sintoma ou história associada** que já tira o caso
da faixa "achado isolado", e, não havendo isso, o sopro tem **alguma
característica de alerta** à ausculta — e só depois disso vale checar se ele
se encaixa no padrão clássico de um dos sopros inocentes nomeados.

## Árvore de decisão

```mermaid
flowchart TD
  R0["Criança com sopro cardíaco identificado<br/>ao exame físico de rotina"] --> D0{"É recém-nascido<br/>(menos de 28 dias)?"}

  D0 -->|"Sim"| C0(["Realizar/confirmar oximetria de pulso<br/>para cardiopatia crítica e encaminhar à<br/>cardiologia pediátrica; consulta é preferível<br/>a solicitar ecocardiograma reflexamente.<br/>Se cianose, má perfusão ou desconforto:<br/>avaliação emergencial"])

  D0 -->|"Não"| D1{"Há sintoma sistêmico ou história<br/>preocupante associada — dificuldade de<br/>ganho de peso, cianose, dispneia ao<br/>esforço, ou história familiar de morte<br/>súbita precoce/cardiomiopatia?"}

  D1 -->|"Sim"| C1(["Encaminhar à cardiologia pediátrica;<br/>ecocardiograma conforme avaliação.<br/>Cianose, síncope de esforço, má perfusão<br/>ou desconforto respiratório exigem<br/>avaliação urgente"])

  D1 -->|"Não — achado isolado,<br/>criança assintomática"| D2{"O sopro tem alguma destas<br/>características: timbre áspero; diastólico<br/>ou holossistólico; grau 3 ou mais; irradia<br/>para dorso/pescoço; B2 fixa ou única;<br/>clique sistólico; ou aumenta quando<br/>a criança fica em pé?"}

  D2 -->|"Sim, alguma dessas<br/>características presente"| C2(["Sopro patológico possível: encaminhar<br/>à cardiologia pediátrica; ecocardiograma<br/>conforme avaliação especializada"])

  D2 -->|"Não — nenhuma característica<br/>de alerta"| D3{"O sopro se encaixa em qual padrão<br/>clássico de sopro inocente?"}

  D3 -->|"Sopro de Still: grau 1 a 2, sistólico<br/>precoce, timbre vibratório ou musical,<br/>borda esternal inferior esquerda, mais<br/>intenso em decúbito e diminui em pé"| C3(["Sopro inocente (de Still) — tranquilizar a<br/>família, sem exame complementar nem<br/>restrição de atividade física"])

  D3 -->|"Sopro de fluxo pulmonar: grau 1 ou 2,<br/>crescendo-decrescendo, sistólico precoce<br/>a médio, borda esternal esquerda, mais<br/>intenso em decúbito e diminui em pé"| C4(["Sopro inocente (fluxo pulmonar) —<br/>tranquilizar a família, sem exame<br/>complementar nem restrição de<br/>atividade física"])

  D3 -->|"Zumbido venoso: contínuo, na<br/>região cervical anterior, com timbre<br/>de sopro/rugido/zunido, desaparece<br/>em decúbito"| C5(["Sopro inocente (zumbido venoso) —<br/>confirmar o desaparecimento em<br/>decúbito ou com rotação/compressão<br/>do pescoço antes de tranquilizar<br/>a família"])

  D3 -->|"Sopro supraclavicular ou<br/>braquiocefálico: acima das clavículas,<br/>diminui com hiperextensão dos ombros"| C6(["Sopro inocente (supraclavicular) —<br/>confirmar a diminuição com a manobra<br/>de hiperextensão antes de tranquilizar<br/>a família"])

  D3 -->|"Não se encaixa em nenhum<br/>padrão clássico"| C7(["Classificação incerta: encaminhar para<br/>ecocardiograma e cardiologia pediátrica<br/>por segurança"])

  classDef conduta fill:#eef6ef,stroke:#2f7a4f,color:#12301f;
  class C0,C1,C2,C3,C4,C5,C6,C7 conduta;
```

## O que a árvore não mostra

**"Aumenta em pé" é o sinal invertido do que separa inocente de patológico
nesta árvore.** Os dois sopros inocentes sistólicos mais comuns (Still e
fluxo pulmonar) **diminuem** quando a criança fica em pé, porque dependem de
maior retorno venoso em decúbito; um sopro que **aumenta** de intensidade em
pé — como o de uma cardiomiopatia hipertrófica obstrutiva — é justamente o
oposto, e por isso entra como achado de alerta na segunda pergunta da árvore,
não como característica de um sopro inocente.

**A manobra confirmatória é parte do diagnóstico, não um detalhe.** O
zumbido venoso e o sopro supraclavicular só são caracterizados como inocentes
depois que a manobra postural (decúbito/rotação cervical no primeiro,
hiperextensão dos ombros no segundo) muda a intensidade do sopro — pular essa
etapa e classificar pelo local de ausculta isoladamente é o erro mais comum
nesses dois.

**Recém-nascido é população à parte.** Todo neonato deve ter rastreamento de
cardiopatia congênita crítica por oximetria de pulso, idealmente após 24 horas
e antes da alta. Como o sopro neonatal tem maior taxa de doença estrutural e
é mais difícil de classificar, a atualização de 2022 prioriza consulta com
cardiologia pediátrica — preferencialmente na primeira semana — antes de
ecocardiograma solicitado de forma reflexa, salvo urgência clínica.

**Este fluxograma não substitui a investigação dirigida de uma cardiopatia
congênita já suspeita por outro motivo** (cianose neonatal, achado
pré-natal, síndrome genética associada) — ele organiza o raciocínio do sopro
como achado isolado no exame de rotina, que é o cenário mais frequente na
prática ambulatorial.
