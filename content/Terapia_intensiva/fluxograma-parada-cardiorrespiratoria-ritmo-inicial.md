---
title: "Fluxograma: Parada cardiorrespiratória — o que o primeiro ritmo decide"
slug: fluxograma-parada-cardiorrespiratoria-ritmo-inicial
theme: "Terapia intensiva"
kind: fluxograma
summary: "Árvore de decisão do atendimento inicial à parada no adulto: o que o monitor mostra separa chocável de não chocável, e a linha reta exige confirmação antes de ser chamada de assistolia."
review_status: revisado
source_refs: ["Bernoche C, Timerman S, Polastri TF, et al. Atualização da Diretriz de Ressuscitação Cardiopulmonar e Cuidados Cardiovasculares de Emergência da Sociedade Brasileira de Cardiologia — 2019 · Arquivos Brasileiros de Cardiologia · 2019 · 113(3):449-663 · PMID: 31621787"]
---

# Fluxograma: Parada cardiorrespiratória — o que o primeiro ritmo decide

A parada é atendida em **ciclos de 2 minutos**, e ciclo não cabe numa árvore de
decisão. O diagrama abaixo cobre o que a árvore representa bem: **a primeira
bifurcação**, aquela em que o ritmo no monitor separa condutas que não se
misturam. O que se repete a cada ciclo está em prosa logo depois — é onde essa
informação fica correta.

## Árvore de decisão: ritmo inicial

```mermaid
flowchart TD
  R0["Vítima não responsiva,<br/>sem respiração normal<br/>ou apenas com gasping"] --> P1["Acionar ajuda e pedir desfibrilador.<br/>Iniciar RCP de alta qualidade"]

  P1 --> D1{"O que o monitor mostra?"}

  D1 -->|"FV ou TV sem pulso"| C1(["Desfibrilar na energia máxima<br/>e retomar a RCP de imediato"])

  D1 -->|"Ritmo organizado"| D2{"Pulso carotídeo<br/>em 5 a 10 segundos?"}

  D2 -->|"Ausente"| C2(["AESP: não desfibrilar.<br/>RCP, adrenalina e<br/>busca de causa reversível"])
  D2 -->|"Presente"| C3(["Retorno da circulação:<br/>cuidados pós-parada"])

  D1 -->|"Linha reta"| D3{"Cabos, ganho máximo e<br/>troca de derivação:<br/>segue reto?"}

  D3 -->|"Segue reto"| C4(["Assistolia: não desfibrilar.<br/>RCP, adrenalina e<br/>busca de causa reversível"])
  D3 -->|"Aparece FV fina"| C5(["Tratar como FV:<br/>desfibrilar e retomar a RCP"])

  classDef conduta fill:#eef6ef,stroke:#2f7a4f,color:#12301f;
  class C1,C2,C3,C4,C5 conduta;
```

## O que se repete a cada ciclo, e por isso não está no diagrama

**Energia da desfibrilação**: máxima do aparelho — 360 J no monofásico, 120 a
200 J no bifásico conforme o fabricante, e 200 J quando essa orientação for
desconhecida.

**Parâmetros da compressão**: 100 a 120 por minuto, profundidade de 5 a 6 cm,
ciclos de 30 compressões para 2 ventilações.

**Reavaliação a cada 2 minutos.** O ritmo é checado ao fim de cada ciclo, e quem
comprime é revezado no mesmo intervalo — é quando a qualidade da compressão cai
por fadiga, mesmo sem o socorrista perceber.

**Adrenalina a cada 3 a 5 minutos**, 1 mg por via intravenosa ou intraóssea, em
qualquer ritmo. Nos ritmos não chocáveis, o mais cedo possível; na FV/TVSP, a
partir do segundo ciclo.

**Antiarrítmico na FV/TVSP que persiste** apesar de RCP, desfibrilação e
vasopressor: amiodarona 300 mg, com dose adicional de 150 mg possível,
intercalada com o vasopressor; ou lidocaína 1,0 a 1,5 mg/kg, com segunda dose de
0,5 a 0,75 mg/kg se persistir.

**Procurar a causa reversível o tempo todo**, em todos os ritmos — os 5H e 5T.
Não é um passo do algoritmo que acontece uma vez: é uma busca paralela que corre
junto com as compressões.

**Depois da via aérea avançada**, as compressões passam a ser contínuas, sem
pausa para ventilar, com uma ventilação a cada 6 segundos.

## Por que a linha reta tem um ramo próprio

Porque ela **não é um diagnóstico**, é uma imagem compatível com dois quadros de
condutas opostas: assistolia e fibrilação ventricular fina. A amplitude do
traçado da FV depende das reservas de ATP do miocárdio, e uma FV terminal pode
aparecer quase plana.

Deixar de desfibrilar uma FV é inadmissível; desfibrilar uma assistolia piora o
prognóstico. É por isso que a diretriz coloca três manobras entre a imagem e a
decisão — conexão dos cabos, ganho máximo, troca de derivação — e dá menos de 10
segundos para elas.
