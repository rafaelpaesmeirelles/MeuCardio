---
title: "Fluxograma: Bradicardia sintomática — manejo agudo da instabilidade"
slug: fluxograma-bradicardia-sintomatica-manejo-agudo
theme: "Arritmias"
kind: fluxograma
summary: "Árvore de decisão da conduta imediata na bradicardia sintomática: a instabilidade hemodinâmica decide se há tempo para só observar, o padrão eletrocardiográfico decide se vale a pena tentar atropina, e a resposta ao tratamento decide entre marca-passo transcutâneo, droga cronotrópica em infusão e marca-passo transvenoso temporário."
review_status: revisado
source_refs: ["Second-Degree Atrioventricular Block · StatPearls (NCBI Bookshelf) · https://www.ncbi.nlm.nih.gov/books/NBK482359/", "Atropine · StatPearls (NCBI Bookshelf) · https://www.ncbi.nlm.nih.gov/books/NBK470551/", "Adult Bradycardia With a Pulse Algorithm · American Heart Association, atualização 2020 · https://cpr.heart.org/-/media/cpr-files/cpr-guidelines-files/algorithms/algorithmacls_bradycardia_200612.pdf — PDF original não extraível em texto; conteúdo (sinais de instabilidade, dose de atropina, marca-passo transcutâneo, dopamina 5-20mcg/kg/min, adrenalina 2-10mcg/min) conferido via resumo em ACLS-Algorithms.com em 03/08/2026", "Glikson M, Nielsen JC, Kronborg MB, et al. 2021 ESC Guidelines on cardiac pacing and cardiac resynchronization therapy · European Heart Journal · 2021 · 42(35):3427-3520 · DOI: 10.1093/eurheartj/ehab364 · PMID: 34455430"]
---

# Fluxograma: Bradicardia sintomática — manejo agudo da instabilidade

Este fluxograma cobre a **conduta imediata** diante de bradicardia com sintoma ou
sinal atribuível a ela — do reconhecimento da instabilidade até a estabilização
com marca-passo transcutâneo, droga cronotrópica ou marca-passo transvenoso
temporário. Não é o fluxograma de indicação de marca-passo **definitivo** (esse
já existe, em Dispositivos) nem cobre a tempestade elétrica de TV/FV do
documento-fonte, que é um mecanismo diferente (taquiarritmia ventricular
recorrente, não bradicardia).

## Árvore de decisão

```mermaid
flowchart TD
  R0["Bradicardia (FC baixa) com sintoma<br/>ou sinal atribuível a ela"]
  D1{"Sinais de instabilidade?<br/>(hipotensão, alteração aguda de consciência,<br/>sinais de choque, isquemia miocárdica,<br/>congestão aguda)"}
  C1(["Sem tratamento imediato da frequência:<br/>monitorização contínua,<br/>investigar e tratar a causa, reavaliar"])
  D2{"ECG sugere bloqueio infra-nodal?<br/>(Mobitz II, BAV 2:1 infra-hissiano<br/>ou BAVT com QRS largo)"}
  P1["Marca-passo transcutâneo imediato,<br/>sem aguardar resposta a droga"]
  D3{"Captura elétrica e mecânica eficaz,<br/>estabilidade restaurada?"}
  C2(["Manter marca-passo transcutâneo com<br/>analgesia/sedação; providenciar marca-passo<br/>transvenoso temporário sem demora"])
  C3(["Associar dopamina 5-20mcg/kg/min ou<br/>adrenalina 2-10mcg/min em infusão;<br/>marca-passo transvenoso temporário de urgência"])
  P2["Atropina 0,5-1mg IV,<br/>repetir a cada 3-5min até 3mg"]
  D4{"Resposta adequada de FC<br/>e reversão da instabilidade?"}
  C4(["Manter vigilância, tratar a causa de base<br/>e reavaliar se a bradicardia recorrer"])
  P3["Marca-passo transcutâneo e/ou<br/>dopamina/adrenalina em infusão, como ponte"]
  C5(["Marca-passo transvenoso temporário indicado —<br/>refratário a droga cronotrópica IV (Classe I, ESC 2021)"])

  R0 --> D1
  D1 -->|"Não"| C1
  D1 -->|"Sim"| D2
  D2 -->|"Sim — atropina<br/>provavelmente ineficaz"| P1
  P1 --> D3
  D3 -->|"Sim"| C2
  D3 -->|"Não"| C3
  D2 -->|"Não — bloqueio provavelmente<br/>nodal/supra-hissiano"| P2
  P2 --> D4
  D4 -->|"Sim"| C4
  D4 -->|"Não — refratário à atropina"| P3
  P3 --> C5

  classDef conduta fill:#eef6ef,stroke:#2f7a4f,color:#12301f;
  class C1,C2,C3,C4,C5 conduta;
```

## Por que o ECG decide antes da atropina

A atropina bloqueia o tônus vagal sobre o nó sinusal e o nó atrioventricular —
mecanismo que não alcança um bloqueio **infra-nodal**. No BAV de segundo grau
Mobitz II e no BAV total com QRS largo, o bloqueio costuma estar abaixo do nó
AV, fora do alcance desse mecanismo; insistir em atropina nesses casos só atrasa
o marca-passo transcutâneo, que não deve esperar a resposta à droga.

## O que se repete em todo ramo, fora da árvore

**Buscar e tratar a causa reversível em paralelo à estabilização** — fármaco
(betabloqueador, bloqueador de canal de cálcio, digoxina), distúrbio
eletrolítico, isquemia miocárdica ativa e hipóxia são as causas mais comuns, e
corrigi-las muda a conduta mesmo depois de escolhido um ramo da árvore.

**Monitorização contínua** (ECG, oximetria, pressão arterial não invasiva ou
invasiva conforme gravidade) e **ECG de 12 derivações** assim que possível, sem
atrasar o tratamento da instabilidade.

**Cautela com atropina em isquemia coronariana ativa**: o aumento de frequência
cardíaca eleva o consumo miocárdico de oxigênio e pode piorar a isquemia — nesse
contexto, limitar a dose total a 2-3 mg.

**Reavaliação frequente da resposta**, em qualquer ramo — a árvore representa um
único ciclo de decisão, mas a bradicardia pode recorrer ou o bloqueio pode
progredir depois de estabilizado.

## O que este fluxograma não cobre

**Indicação de marca-passo definitivo** — quando o bloqueio documentado justifica
implante permanente (independente da fase aguda), ver o fluxograma dedicado em
Dispositivos: *Bradiarritmia — indicação de marcapasso definitivo (ESC 2021)*.

**Tempestade elétrica** — no documento-fonte, tempestade elétrica é definida
como três ou mais episódios de TV sustentada, FV ou choques apropriados de CDI
em 24 horas: um mecanismo de taquiarritmia ventricular recorrente, não de
bradicardia, e por isso não tem ramo neste fluxograma.

**Bradicardia por intoxicação digitálica** tem manejo próprio (anticorpo
antidigoxina Fab), já coberto em documento dedicado no tema Arritmias.
