---
title: "Fluxograma: Taquicardia Supraventricular de QRS Estreito Regular (ESC 2019)"
slug: fluxograma-taquicardia-supraventricular-qrs-estreito-esc-2019
theme: "Arritmias"
kind: fluxograma
summary: "Árvore de decisão do atendimento agudo à taquicardia regular de QRS estreito: cardioversão elétrica imediata no instável; no estável, manobra vagal, adenosina (com verapamil preferido na asma grave) e, por fim, verapamil/diltiazem ou betabloqueador — com a fibrilação atrial pré-excitada tratada à parte pelo risco de fibrilação ventricular com bloqueadores do nó AV."
review_status: revisado
source_refs: ["2019 ESC Guidelines for the management of patients with supraventricular tachycardia · European Heart Journal · 2020 · 41(5):655-720 · https://academic.oup.com/eurheartj/article/41/5/655/5556821", "ESC Guidelines for Management of Supraventricular Tachycardia: Key Points · American College of Cardiology · 2019 · https://www.acc.org/Latest-in-Cardiology/ten-points-to-remember/2019/09/10/12/36/2019-ESC-Guidelines-for-Supraventricular-Tachycardia"]
---

# Fluxograma: Taquicardia Supraventricular de QRS Estreito Regular (ESC 2019)

Este fluxograma cobre a conduta imediata na taquicardia regular de QRS estreito
(≤120 ms), da avaliação da estabilidade hemodinâmica até a reversão ou o
controle da arritmia. A base é o algoritmo de manejo agudo da diretriz ESC
2019 para TSV. A fibrilação atrial pré-excitada é um ritmo **irregular**, com
risco próprio de fibrilação ventricular, e por isso tem árvore separada mais
abaixo.

## Árvore de decisão: Taquicardia regular de QRS estreito

```mermaid
flowchart TD
  R0["Taquicardia regular de QRS estreito<br/>(≤120 ms)"]
  D1{"Instabilidade hemodinâmica<br/>(hipotensão, alteração aguda do<br/>estado mental, dor torácica,<br/>sinais de IC aguda ou choque)?"}
  C1(["Cardioversão elétrica sincronizada<br/>imediata — Classe I, nível B"])
  P1["Manobra vagal, preferencialmente<br/>em decúbito dorsal com elevação<br/>das pernas — Classe I, nível B"]
  D2{"Reverteu com a<br/>manobra vagal?"}
  C2(["Taquicardia revertida:<br/>investigar o mecanismo e definir<br/>o tratamento definitivo"])
  D3{"Asma brônquica grave<br/>(verapamil é mais apropriado<br/>que a adenosina)?"}
  P2["Verapamil ou diltiazem<br/>IV — Classe IIa, nível B"]
  P3["Adenosina IV em bolus rápido:<br/>6 mg inicial; se não reverter, 12 mg;<br/>considerar 18 mg se ainda ineficaz<br/>— Classe I, nível B"]
  D5{"Reverteu ou controlou<br/>a frequência?"}
  C4(["Taquicardia revertida ou controlada:<br/>investigar o mecanismo e definir<br/>o tratamento definitivo"])
  C5(["Cardioversão elétrica<br/>sincronizada — Classe I, nível B"])
  D4{"Reverteu com<br/>a adenosina?"}
  C3(["Taquicardia revertida:<br/>investigar o mecanismo e definir<br/>o tratamento definitivo"])
  P4["Verapamil ou diltiazem IV<br/>— Classe IIa, nível B — ou<br/>beta-bloqueador IV<br/>— Classe IIa, nível C"]
  D6{"Reverteu ou controlou<br/>a frequência?"}
  C6(["Taquicardia revertida ou controlada:<br/>investigar o mecanismo e definir<br/>o tratamento definitivo"])
  C7(["Cardioversão elétrica<br/>sincronizada — Classe I, nível B"])

  R0 --> D1
  D1 -->|"Sim"| C1
  D1 -->|"Não"| P1
  P1 --> D2
  D2 -->|"Sim"| C2
  D2 -->|"Não"| D3
  D3 -->|"Sim"| P2
  D3 -->|"Não"| P3
  P2 --> D5
  D5 -->|"Sim"| C4
  D5 -->|"Não"| C5
  P3 --> D4
  D4 -->|"Sim"| C3
  D4 -->|"Não"| P4
  P4 --> D6
  D6 -->|"Sim"| C6
  D6 -->|"Não"| C7

  classDef conduta fill:#eef6ef,stroke:#2f7a4f,color:#12301f;
  class C1,C2,C3,C4,C5,C6,C7 conduta;
```

## Por que a asma grave entra antes da adenosina

A adenosina pode ser usada com cautela em pacientes asmáticos, mas na **asma
brônquica grave** o verapamil é a escolha mais apropriada — daí a bifurcação
antes da adenosina, e não uma contraindicação absoluta.

Verapamil e diltiazem, por sua vez, devem ser evitados em caso de
hipotensão, insuficiência cardíaca com fração de ejeção reduzida (<40%) ou
suspeita de taquicardia ventricular. Beta-bloqueadores endovenosos são
contraindicados na insuficiência cardíaca descompensada. Essas ressalvas
valem em qualquer ponto da árvore em que esses fármacos apareçam.

## Por que a adenosina tem faixa de dose, não dose fixa

O esquema é incremental: 6 mg em bolus rápido; se a taquicardia não reverter,
12 mg; um paciente ainda não revertido pode receber 18 mg, conforme
tolerabilidade individual. A meia-vida plasmática é curtíssima (segundos), o
que torna segura a repetição da dose já a partir de 1 minuto da anterior.

## Por que a fibrilação atrial pré-excitada tem árvore própria

Quando o ECG basal mostra pré-excitação (padrão de Wolff-Parkinson-White) mas
a taquicardia **atual** é regular e de QRS estreito — ou seja, uma taquicardia
por reentrada atrioventricular ortodrômica —, a adenosina continua sendo
conduta Classe I: a árvore acima permanece válida.

O que muda tudo é a irregularidade do ritmo. Na fibrilação atrial
pré-excitada, o impulso pode conduzir preferencialmente pela via acessória,
que tem período refratário mais curto que o do nó AV. Por isso, **qualquer
bloqueador do nó AV — adenosina, verapamil, diltiazem, beta-bloqueador ou
digoxina — deve ser evitado**, porque pode acelerar a condução pela via
acessória e precipitar fibrilação ventricular. É esse cenário que a árvore
abaixo cobre.

## Árvore de decisão: Fibrilação atrial pré-excitada (suspeita de via acessória / WPW)

```mermaid
flowchart TD
  R1["Fibrilação atrial pré-excitada<br/>(irregular, com via acessória<br/>manifesta) — suspeita ou confirmada"]
  D7{"Instabilidade hemodinâmica?"}
  C8(["Cardioversão elétrica<br/>sincronizada — Classe I, nível B"])
  D8{"Antiarrítmico endovenoso"}
  P5["Ibutilida ou procainamida IV"]
  P6["Flecainida ou propafenona IV"]
  D9{"Reverteu ou controlou<br/>a taquicardia?"}
  C9(["Taquicardia revertida ou controlada:<br/>investigar o mecanismo e definir<br/>o tratamento definitivo"])
  C10(["Cardioversão elétrica<br/>sincronizada — Classe I, nível B"])
  D10{"Reverteu ou controlou<br/>a taquicardia?"}
  C11(["Taquicardia revertida ou controlada:<br/>investigar o mecanismo e definir<br/>o tratamento definitivo"])
  C12(["Cardioversão elétrica<br/>sincronizada — Classe I, nível B"])

  R1 --> D7
  D7 -->|"Sim"| C8
  D7 -->|"Não"| D8
  D8 -->|"Ibutilida ou procainamida —<br/>preferencial (Classe IIa, nível B)"| P5
  D8 -->|"Flecainida ou propafenona —<br/>alternativa (Classe IIb, nível B)"| P6
  P5 --> D9
  D9 -->|"Sim"| C9
  D9 -->|"Não"| C10
  P6 --> D10
  D10 -->|"Sim"| C11
  D10 -->|"Não"| C12

  classDef conduta fill:#eef6ef,stroke:#2f7a4f,color:#12301f;
  class C8,C9,C10,C11,C12 conduta;
```

Amiodarona endovenosa **não é recomendada** na fibrilação atrial
pré-excitada — a condução pela via acessória pode ser maior do que se
pensava, com relatos de precipitação de fibrilação ventricular.

## O que a árvore não mostra

O diagnóstico diferencial entre AVNRT, taquicardia por reentrada
atrioventricular ortodrômica e taquicardia atrial não muda a conduta
imediata — todas seguem a mesma primeira árvore. Ele importa para a decisão
de tratamento definitivo (ablação por cateter, na maioria dos casos), não
para o atendimento agudo.
