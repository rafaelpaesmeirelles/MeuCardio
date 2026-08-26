---
title: "Fluxograma: Sopro cardíaco na criança — inocente versus patológico"
slug: fluxograma-sopro-cardiaco-na-crianca-inocente-versus-patologico
theme: "Cardiopatias congênitas"
kind: fluxograma
fonte_producao: chatgpt
review_status: revisado
review_note: "Fonte verificada via PubMed E-utilities (esummary) nesta sessão: PMID 22010618 confirmado (Frank JE, Jacobe KM. Evaluation and management of heart murmurs in children. Am Fam Physician. 2011;84(7):793-800). O artigo original da American Family Physician não tem resumo estruturado indexado no PubMed (é artigo de revisão da AAFP); o texto integral, de acesso aberto no site da própria AAFP (aafp.org/pubs/afp/issues/2011/1001/p793.html), foi consultado diretamente nesta sessão para extrair as características descritas de cada sopro inocente nomeado (Still, fluxo pulmonar, zumbido venoso, supraclavicular) e a lista de achados de alerta — nenhum valor foi completado de memória."
source_refs: ["Frank JE, Jacobe KM. Evaluation and Management of Heart Murmurs in Children. American Family Physician. 2011;84(7):793-800. PMID: 22010618 — texto integral em acesso aberto, aafp.org/pubs/afp/issues/2011/1001/p793.html, consultado diretamente nesta sessão."]
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
  R0["Criança com sopro cardíaco identificado<br/>ao exame físico de rotina"] --> D1{"Há sintoma sistêmico ou história<br/>preocupante associada — dificuldade de<br/>ganho de peso, cianose, dispneia ao<br/>esforço, ou história familiar de morte<br/>súbita precoce/cardiomiopatia?"}

  D1 -->|"Sim"| C1(["Encaminhar para ecocardiograma e avaliação<br/>por cardiologia pediátrica, independentemente<br/>das características do sopro à ausculta"])

  D1 -->|"Não — achado isolado,<br/>criança assintomática"| D2{"O sopro tem alguma destas<br/>características: timbre áspero (harsh);<br/>holossistólico ou diastólico; grau 3 ou<br/>mais; B2 desdobrada de forma fixa ou<br/>única; clique sistólico; foco de maior<br/>intensidade em borda esternal superior<br/>esquerda; ou aumenta de intensidade<br/>quando a criança fica em pé?"}

  D2 -->|"Sim, alguma dessas<br/>características presente"| C2(["Sopro patológico provável: encaminhar<br/>para ecocardiograma e avaliação por<br/>cardiologia pediátrica"])

  D2 -->|"Não — nenhuma característica<br/>de alerta"| D3{"O sopro se encaixa em qual padrão<br/>clássico de sopro inocente?"}

  D3 -->|"Sopro de Still: grau 1 a 3, sistólico<br/>precoce, timbre vibratório ou musical,<br/>borda esternal inferior esquerda, mais<br/>intenso em decúbito e diminui em pé"| C3(["Sopro inocente (de Still) — tranquilizar a<br/>família, sem exame complementar nem<br/>restrição de atividade física"])

  D3 -->|"Sopro de fluxo pulmonar: grau 2 ou 3,<br/>crescendo-decrescendo, sistólico precoce<br/>a médio, borda esternal esquerda, mais<br/>intenso em decúbito e diminui em pé"| C4(["Sopro inocente (fluxo pulmonar) —<br/>tranquilizar a família, sem exame<br/>complementar nem restrição de<br/>atividade física"])

  D3 -->|"Zumbido venoso: contínuo, na<br/>região cervical anterior, com timbre<br/>de sopro/rugido/zunido, desaparece<br/>em decúbito"| C5(["Sopro inocente (zumbido venoso) —<br/>confirmar o desaparecimento em<br/>decúbito ou com rotação/compressão<br/>do pescoço antes de tranquilizar<br/>a família"])

  D3 -->|"Sopro supraclavicular ou<br/>braquiocefálico: acima das clavículas,<br/>diminui com hiperextensão dos ombros"| C6(["Sopro inocente (supraclavicular) —<br/>confirmar a diminuição com a manobra<br/>de hiperextensão antes de tranquilizar<br/>a família"])

  D3 -->|"Não se encaixa em nenhum<br/>padrão clássico"| C7(["Classificação incerta: encaminhar para<br/>ecocardiograma e cardiologia pediátrica<br/>por segurança"])

  classDef conduta fill:#eef6ef,stroke:#2f7a4f,color:#12301f;
  class C1,C2,C3,C4,C5,C6,C7 conduta;
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

**Recém-nascido é população à parte.** Sopro identificado nos primeiros dias
de vida tem menor especificidade dos critérios acima — o fechamento do canal
arterial e a queda da resistência vascular pulmonar ainda em curso mudam a
ausculta ao longo dos primeiros dias, e a fonte consultada recomenda limiar
mais baixo para investigação complementar nesse período, sem propor um
critério numérico único.

**Este fluxograma não substitui a investigação dirigida de uma cardiopatia
congênita já suspeita por outro motivo** (cianose neonatal, achado
pré-natal, síndrome genética associada) — ele organiza o raciocínio do sopro
como achado isolado no exame de rotina, que é o cenário mais frequente na
prática ambulatorial.
