---
title: "Fluxograma: Parada cardiorrespiratória — o que o primeiro ritmo decide"
slug: fluxograma-parada-cardiorrespiratoria-ritmo-inicial
theme: "Terapia intensiva"
kind: fluxograma
summary: "Árvore de decisão do atendimento inicial à parada no adulto: o que o monitor mostra separa chocável de não chocável, e a linha reta exige confirmação antes de ser chamada de assistolia."
review_status: revisado
review_note: "Atualizado em 26/08/2026 contra o ALS AHA 2025 (PMID 41122884). Corrigida a energia: no desfibrilador bifásico, o primeiro choque segue a recomendação do fabricante (120–200 J conforme o equipamento), usando-se a energia máxima disponível somente quando ela é desconhecida; choques subsequentes podem ser equivalentes ou maiores. Explicitada a entrada do antiarrítmico após o terceiro choque no algoritmo chocável."
source_refs: ["Wigginton JG, Agarwal S, Bartos JA, et al. Part 9: Adult Advanced Life Support: 2025 American Heart Association Guidelines for Cardiopulmonary Resuscitation and Emergency Cardiovascular Care. Circulation. 2025;152(16 Suppl 2):S538-S577. DOI: 10.1161/CIR.0000000000001376. PMID: 41122884.", "Bernoche C, Timerman S, Polastri TF, et al. Atualização da Diretriz de Ressuscitação Cardiopulmonar e Cuidados Cardiovasculares de Emergência da Sociedade Brasileira de Cardiologia — 2019. Arq Bras Cardiol. 2019;113(3):449-663. PMID: 31621787 — mantida como referência brasileira histórica; a energia e a sequência deste fluxo seguem a fonte AHA 2025."]
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

  D1 -->|"FV ou TV sem pulso"| C1(["Desfibrilar: bifásico conforme fabricante<br/>(máxima se desconhecida) ou monofásico 360 J;<br/>retomar a RCP de imediato"])

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

**Energia da desfibrilação**: no bifásico, usar no primeiro choque a energia
recomendada pelo fabricante (por exemplo, 120–200 J conforme o equipamento); se
ela for desconhecida, usar a energia máxima disponível. Choques bifásicos
subsequentes podem usar energia equivalente ou maior, considerando a máxima. No
monofásico, usar 360 J.

**Parâmetros da compressão**: 100 a 120 por minuto, profundidade de 5 a 6 cm,
ciclos de 30 compressões para 2 ventilações.

**Reavaliação a cada 2 minutos.** O ritmo é checado ao fim de cada ciclo, e quem
comprime é revezado no mesmo intervalo — é quando a qualidade da compressão cai
por fadiga, mesmo sem o socorrista perceber.

**Adrenalina a cada 3 a 5 minutos**, 1 mg por via intravenosa ou intraóssea, em
qualquer ritmo. Nos ritmos não chocáveis, o mais cedo possível; na FV/TVSP, a
partir do segundo ciclo.

**Antiarrítmico na FV/TVSP que persiste**: no algoritmo chocável AHA 2025,
amiodarona ou lidocaína entram durante a RCP **após o terceiro choque**.
Amiodarona: 300 mg, com dose adicional de 150 mg se necessário. Lidocaína:
1,0 a 1,5 mg/kg, com segunda dose de 0,5 a 0,75 mg/kg se persistir.

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

## Tudo com Tudo

- [Cuidados pós-parada e coronariografia](fluxograma-cuidado-pos-parada-e-coronariografia.md)
- [Hipocalemia grave e parada hipocalêmica](fluxograma-hipocalemia-grave-risco-arritmico.md)
- [Torsades de pointes e QT longo adquirido](../Arritmias/fluxograma-torsades-de-pointes-e-qt-longo-adquirido.md)
- [Hipotermia acidental e parada cardiorrespiratória](fluxograma-hipotermia-acidental-e-parada-cardiorrespiratoria.md)
- [Afogamento e parada cardiorrespiratória](fluxograma-afogamento-manejo-da-parada-cardiorrespiratoria.md)
- [Neuroprognóstico multimodal pós-parada](neuroprognostico-multimodal-pos-parada-cardiorrespiratoria-algoritmo-erc-esicm-2021-e-a-atualizacao-aha-2025.md)
