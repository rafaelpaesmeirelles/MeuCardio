---
title: "Fluxograma: Taquicardia de QRS largo sem diagnóstico estabelecido (ESC 2019)"
slug: fluxograma-taquicardia-de-qrs-largo-esc-2019
theme: "Arritmias"
kind: fluxograma
summary: "Árvore de decisão do atendimento à taquicardia de QRS largo antes de saber se é TV: cardioversão imediata no instável, e no estável a sequência manobra vagal, adenosina, procainamida — com verapamil formalmente contraindicado."
review_status: revisado
source_refs: ["Brugada J, Katritsis DG, Arbelo E, et al. 2019 ESC Guidelines for the management of patients with supraventricular tachycardia · European Heart Journal · 2020 · 41(5):655-720 · DOI: 10.1093/eurheartj/ehz467 · PMID: 31504425", "Zeppenfeld K, Tfelt-Hansen J, de Riva M, et al. 2022 ESC Guidelines for the management of patients with ventricular arrhythmias and the prevention of sudden cardiac death · European Heart Journal · 2022 · 43(40):3997-4126 · DOI: 10.1093/eurheartj/ehac262 · PMID: 36017572", "Ortiz M, Martín A, Arribas F, et al. Randomized comparison of intravenous procainamide vs. intravenous amiodarone for the acute treatment of tolerated wide QRS tachycardia: the PROCAMIO study · European Heart Journal · 2017 · 38(17):1329-1335 · PMID: 27354046"]
---

# Fluxograma: Taquicardia de QRS largo sem diagnóstico estabelecido (ESC 2019)

Toda taquicardia de QRS largo é **taquicardia ventricular até prova em
contrário**. A regra não é retórica: ela decide a conduta antes de o diagnóstico
existir, e é o que impede o erro mais grave desse cenário — tratar como
supraventricular com aberrância uma TV que vai deteriorar com o fármaco errado.

O algoritmo abaixo é o da diretriz de 2019, escrito exatamente para o momento em
que **ainda não há diagnóstico**. Quando a TV já está estabelecida, a lógica muda
e está descrita na última seção.

## Árvore de decisão

```mermaid
flowchart TD
  R0["Taquicardia de QRS largo<br/>(QRS ≥ 120 ms), sem diagnóstico<br/>estabelecido"] --> D1{"Estabilidade hemodinâmica"}

  D1 -->|"Instável"| C1(["Cardioversão elétrica sincronizada,<br/>imediata — Classe I, nível B"])

  D1 -->|"Estável"| P1["ECG de 12 derivações durante a taquicardia<br/>— Classe I"]

  P1 --> D2{"Manobra vagal em decúbito dorsal<br/>com elevação das pernas<br/>reverte a taquicardia? — Classe I"}

  D2 -->|"Sim"| C2(["Taquicardia revertida:<br/>investigar o mecanismo e definir<br/>o tratamento definitivo"])

  D2 -->|"Não"| D3{"Pré-excitação no<br/>ECG de repouso?"}

  D3 -->|"Sim"| C3(["Não administrar adenosina.<br/>Seguir para procainamida EV ou<br/>cardioversão elétrica sincronizada"])

  D3 -->|"Não"| D4{"Adenosina endovenosa<br/>reverte a taquicardia? — Classe IIa"}

  D4 -->|"Sim"| C4(["Taquicardia revertida:<br/>investigar o mecanismo e definir<br/>o tratamento definitivo"])

  D4 -->|"Não"| D5{"Antiarrítmico endovenoso"}

  D5 -->|"Procainamida — preferencial<br/>(Classe IIa, nível B)"| C5(["Procainamida EV.<br/>Se não reverter nem controlar,<br/>cardioversão elétrica sincronizada<br/>— Classe I, nível B"])

  D5 -->|"Amiodarona — alternativa<br/>(Classe IIb, nível B)"| C6(["Amiodarona EV.<br/>Se não reverter nem controlar,<br/>cardioversão elétrica sincronizada<br/>— Classe I, nível B"])

  classDef conduta fill:#eef6ef,stroke:#2f7a4f,color:#12301f;
  class C1,C2,C3,C4,C5,C6 conduta;
```

## Verapamil é contraindicação formal

**Verapamil não é recomendado na taquicardia de QRS largo de etiologia
desconhecida — Classe III, nível B.** O motivo é concreto: em paciente com TV
até então estável, o verapamil pode provocar **deterioração hemodinâmica grave**.
Ele só tem lugar quando o diagnóstico de taquicardia supraventricular está
completa e seguramente estabelecido.

É o item mais importante desta página, e o que mais aparece invertido na
prática: a taquicardia "regular, bem tolerada, paciente jovem" é justamente a que
tenta o médico a tratar como supraventricular.

## Por que a adenosina depende do ECG de repouso

A adenosina deve ser considerada quando as manobras vagais falham **e não há
pré-excitação no ECG de repouso** (Classe IIa). Ela ajuda de duas formas: revela
o mecanismo pela resposta, e pode interromper uma TV adenosina-sensível.

A ressalva não é burocrática — **na presença de pré-excitação, a adenosina deve
ser evitada**, porque uma taquicardia pré-excitada pode acelerar a condução pela
via acessória.

## Procainamida antes de amiodarona

A hierarquia entre os dois antiarrítmicos vem do PROCAMIO, ensaio randomizado que
comparou procainamida e amiodarona intravenosas na taquicardia de QRS largo
tolerada: **a procainamida teve menos eventos adversos e maior taxa de terminação
precoce**. Daí a assimetria das classes — procainamida IIa, amiodarona IIb.

No Brasil, a disponibilidade da procainamida endovenosa é limitada, e o
antiarrítmico efetivamente escolhido acaba sendo outro. Isso não muda a
recomendação da diretriz; muda o que se pode fazer com ela, e vale registrar a
diferença em vez de silenciar sobre ela.

## Quando a TV já está diagnosticada, a lógica muda

O algoritmo acima vale para a **ausência de diagnóstico**. Quando se trata de
taquicardia ventricular monomórfica sustentada já estabelecida, a diretriz
europeia de 2022 de arritmias ventriculares desloca a cardioversão elétrica para
o **início** do atendimento, e não para depois da falha dos fármacos, mesmo com
o paciente hemodinamicamente tolerado — desde que o risco anestésico/de sedação
seja baixo. O raciocínio: a cardioversão resolve mais rápido e com menos
exposição do que a sequência farmacológica.

**Parcialmente resolvido em 30/07/2026** — a classe foi confirmada, o nível de
evidência não. O acesso direto à tabela da diretriz (Eur Heart J.
2022;43(40):3997-4126, DOI 10.1093/eurheartj/ehac262) ficou bloqueado nesta
sessão em todas as vias tentadas (Oxford Academic, site da ESC, ResearchGate).
Uma fonte secundária independente e revisada por pares (resumo das inovações da
diretriz, PMC9691474, de acesso aberto) confirma que a recomendação de
cardioversão elétrica precoce na TV monomórfica sustentada hemodinamicamente
tolerada é **Classe I** — mesma classe da recomendação, também confirmada por
essa fonte, de ablação por cateter rápida na TV incessante ou na tempestade
elétrica por TV monomórfica recorrente. **O nível de evidência (A/B/C) de
nenhuma das duas continua sem confirmação** — a fonte secundária não o
reproduz. `VERIFICAÇÃO HUMANA NECESSÁRIA`, agora restrita ao nível, não à
classe.

## O que a árvore não mostra

**Critérios eletrocardiográficos de TV** — dissociação atrioventricular, batimentos
de captura e de fusão, concordância precordial, morfologia do QRS — não são ramos
da árvore porque não mudam a conduta imediata: na dúvida, trata-se como TV. Eles
importam para o diagnóstico definitivo e para o tratamento a longo prazo.

**Torsades de pointes e TV polimórfica** têm via própria: correção de potássio e
magnésio, retirada do fármaco que prolonga o QT, e estimulação temporária ou
isoproterenol nos casos refratários. Taquicardia polimórfica não entra nesta
árvore, que é a da taquicardia **regular** de QRS largo.

**Causa reversível é investigação paralela**: isquemia aguda, distúrbio
eletrolítico, intoxicação por fármaco e descompensação de insuficiência cardíaca
mudam o tratamento de fundo, não o passo imediato.
