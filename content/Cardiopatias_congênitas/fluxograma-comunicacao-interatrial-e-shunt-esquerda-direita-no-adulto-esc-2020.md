---
title: "Fluxograma: Comunicação interatrial e shunt esquerda-direita no adulto — decisão de fechar (ESC 2020)"
slug: fluxograma-comunicacao-interatrial-e-shunt-esquerda-direita-no-adulto-esc-2020
theme: "Cardiopatias congênitas"
kind: fluxograma
summary: "Duas árvores da diretriz ESC 2020 de cardiopatia congênita do adulto: a da comunicação interatrial, em que a resistência vascular pulmonar em unidades Wood decide entre fechar, fechar fenestrado e não fechar; e a dos demais shunts esquerda-direita, com a indicação por tipo de defeito."
review_status: revisado
source_refs: ["Baumgartner H, De Backer J, Babu-Narayan SV, et al. 2020 ESC Guidelines for the management of adult congenital heart disease · European Heart Journal · 2021 · 42(6):563-645 · DOI: 10.1093/eurheartj/ehaa554 — tabelas de recomendação para intervenção em comunicação interatrial, comunicação interventricular, defeito do septo atrioventricular e persistência do canal arterial, e Tabela 3 (recomendações revisadas e novas)"]
---

# Fluxograma: Comunicação interatrial e shunt esquerda-direita no adulto — decisão de fechar (ESC 2020)

A diretriz de 2020 tornou a indicação de fechar shunt **mais restritiva** que a de
2010, e organizou a decisão em torno de um único número: a **resistência vascular
pulmonar em unidades Wood**, medida invasivamente. Três pontos que a árvore torna
difíceis de contornar:

- **Sinal não invasivo de pressão pulmonar elevada obriga cateterismo.** Não é
  sugestão: medir a resistência vascular pulmonar de forma invasiva é **Classe I**
  quando há PAP sistólica calculada acima de 40 mmHg ou sinais indiretos. Decidir
  fechar com base só no ecocardiograma, nesse cenário, pula uma recomendação
  Classe I.
- **Resistência de 5 unidades Wood ou mais apesar de tratamento dirigido é
  Classe III** — não fechar. O mesmo vale para fisiologia de Eisenmenger e para
  dessaturação ao esforço, que entrou como contraindicação nesta edição.
- **Doença do ventrículo esquerdo muda o sinal do benefício.** Fechar a
  comunicação interatrial de quem tem disfunção diastólica ou doença do VE pode
  piorar o paciente, ao elevar a pressão de enchimento. A diretriz manda fazer
  teste com balão oclusor e considerar explicitamente três saídas — fechar,
  fechar com fenestração ou não fechar.

## Árvore de decisão: comunicação interatrial

```mermaid
flowchart TD
  R0["Adulto com comunicação interatrial<br/>e sobrecarga de volume do ventrículo direito"] --> D1{"Há sinais não invasivos de pressão arterial<br/>pulmonar elevada — PAP sistólica calculada<br/>acima de 40 mmHg ou sinais indiretos?"}

  D1 -->|"Não"| D2{"Há doença do ventrículo esquerdo?"}

  D2 -->|"Sim"| C1(["Teste com balão oclusor, pesando o benefício de<br/>eliminar o shunt contra o impacto negativo do aumento<br/>da pressão de enchimento. Considerar as três saídas:<br/>fechar, fechar com fenestração ou não fechar<br/>— Classe I, nível C"])

  D2 -->|"Não"| D3{"O defeito é do tipo ostium secundum<br/>e tecnicamente adequado a dispositivo?"}

  D3 -->|"Sim"| C2(["Fechar, independentemente de sintomas<br/>— Classe I, nível B —, por dispositivo, que é<br/>o método de escolha no ostium secundum<br/>tecnicamente adequado — Classe I, nível C"])

  D3 -->|"Não: outro tipo de defeito<br/>ou anatomia inadequada"| C3(["Fechamento cirúrgico, independentemente de sintomas<br/>— Classe I, nível B. No idoso não candidato a<br/>dispositivo, pesar com cuidado o risco cirúrgico<br/>contra o benefício do fechamento — Classe I, nível C"])

  D1 -->|"Sim"| P1["Medida invasiva da resistência vascular pulmonar<br/>é obrigatória — Classe I, nível C.<br/>Teste de esforço para excluir dessaturação"]

  P1 --> D4{"Resistência vascular pulmonar,<br/>com Qp:Qs acima de 1,5"}

  D4 -->|"Abaixo de 3 unidades Wood"| C4(["Fechar — Classe I"])

  D4 -->|"De 3 a menos de 5 unidades Wood"| C5(["Fechamento deve ser considerado — Classe IIa"])

  D4 -->|"5 unidades Wood ou mais, caindo abaixo de 5<br/>após tratamento dirigido da hipertensão arterial<br/>pulmonar, com shunt esquerda-direita<br/>significativo mantido"| C6(["Fechamento pode ser considerado — Classe IIb —<br/>e apenas com fenestração"])

  D4 -->|"5 unidades Wood ou mais apesar do tratamento<br/>dirigido; ou fisiologia de Eisenmenger;<br/>ou dessaturação ao esforço"| C7(["Não fechar — Classe III, nível C"])

  classDef conduta fill:#eef6ef,stroke:#2f7a4f,color:#12301f;
  class C1,C2,C3,C4,C5,C6,C7 conduta;
```

## Árvore de decisão: os demais shunts esquerda-direita

Esta árvore pressupõe **ausência de hipertensão arterial pulmonar**, definida na
diretriz como não haver sinal não invasivo de pressão pulmonar elevada — ou,
havendo, confirmação invasiva de resistência vascular pulmonar abaixo de
3 unidades Wood.

```mermaid
flowchart TD
  R1["Shunt esquerda-direita no adulto,<br/>sem hipertensão arterial pulmonar"] --> D5{"Qual é o defeito?"}

  D5 -->|"Comunicação interatrial, com sobrecarga<br/>de volume do ventrículo direito"| C8(["Fechar, independentemente de sintomas<br/>— Classe I, nível B. Dispositivo é o método de escolha<br/>no ostium secundum tecnicamente adequado<br/>— Classe I, nível C"])

  D5 -->|"Comunicação interventricular, com sobrecarga<br/>de volume do ventrículo esquerdo"| C9(["Fechar, independentemente de sintomas<br/>— Classe I, nível C"])

  D5 -->|"Persistência do canal arterial, com sobrecarga<br/>de volume do ventrículo esquerdo"| C10(["Fechar, independentemente de sintomas<br/>— Classe I, nível C —, por dispositivo, que é<br/>o método de escolha quando tecnicamente<br/>adequado — Classe I, nível C"])

  D5 -->|"Defeito do septo atrioventricular, com sobrecarga<br/>de volume do ventrículo direito significativa"| C11(["Fechamento cirúrgico, realizado apenas por<br/>cirurgião cardíaco congênito — Classe I, nível C"])

  classDef conduta fill:#eef6ef,stroke:#2f7a4f,color:#12301f;
  class C8,C9,C10,C11 conduta;
```

## A tabela de resistência que decide a primeira árvore

Com Qp:Qs acima de 1,5, a diretriz ajustou as recomendações de fechamento de
shunt conforme a resistência vascular pulmonar calculada:

| Resistência vascular pulmonar | CIA | CIV e PCA |
|---|---|---|
| abaixo de 3 UW | Classe I | Classe I |
| de 3 a menos de 5 UW | Classe IIa | Classe IIa |
| 5 UW ou mais, caindo abaixo de 5 após tratamento dirigido | Classe IIb — **apenas fechamento fenestrado** | — |
| 5 UW ou mais | Classe III, se persistir apesar do tratamento dirigido | Classe IIb, como decisão individual cuidadosa em centro especializado |

Repare na assimetria: **na comunicação interatrial, 5 unidades Wood ou mais
apesar de tratamento dirigido fecha a porta — Classe III**; na comunicação
interventricular e na persistência do canal arterial, a mesma faixa permanece
como decisão individual cuidadosa em centro especializado, Classe IIb. Não é
inconsistência da diretriz: reflete que o átrio não protege o leito pulmonar do
mesmo modo, e que o shunt atrial pode inverter com mais facilidade.

## Onde não fechar, nas três lesões

O `Classe III` aparece com redação quase idêntica em CIA, CIV, defeito do septo
atrioventricular e persistência do canal arterial:

- **fisiologia de Eisenmenger**;
- **hipertensão arterial pulmonar grave, com resistência de 5 unidades Wood ou
  mais**, que na CIA vale quando persiste apesar do tratamento dirigido;
- **dessaturação ao esforço** — na persistência do canal arterial, dessaturação
  de membros inferiores.

A dessaturação ao esforço como contraindicação foi **acrescentada nesta edição**
para CIA, CIV, defeito do septo atrioventricular e canal arterial. Por isso o
teste de esforço aparece na árvore junto do cateterismo: sem ele, uma
contraindicação formal simplesmente não é procurada.

## O que as árvores não mostram

**A investigação por imagem que antecede tudo isso.** O ecocardiograma
transesofágico é em geral necessário para diagnosticar defeito do tipo seio
venoso, e é exigido antes do fechamento percutâneo de defeito ostium secundum —
para medir o defeito, examinar a morfologia e a qualidade das bordas do septo
residual, excluir defeitos adicionais e confirmar conexão venosa pulmonar
normal. A ressonância cardíaca raramente é necessária, mas ajuda na sobrecarga
de volume do VD, no defeito de seio venoso inferior e na quantificação do Qp:Qs.

**O tamanho do shunt não é o critério isolado.** A diretriz é explícita ao
preferir, como base da decisão, a **consequência hemodinâmica do defeito** — a
sobrecarga de volume da câmara — em vez da razão de fluxos isolada.

**Defeito do septo atrioventricular tem regras valvares próprias**, que não
couberam na árvore: cirurgia valvar, preferencialmente reparo, é recomendada no
paciente sintomático com regurgitação atrioventricular moderada a grave — Classe I,
nível C. No assintomático com regurgitação grave da valva atrioventricular
esquerda, a cirurgia é recomendada quando o diâmetro sistólico final do VE atinge
45 mm ou mais e/ou a fração de ejeção cai a 60% ou menos, afastadas outras causas
de disfunção — Classe I, nível C.

**Gravidez e hipertensão pulmonar não se misturam.** É recomendado que a paciente
com cardiopatia congênita e hipertensão pulmonar pré-capilar confirmada seja
aconselhada contra engravidar — Classe I, nível C.
