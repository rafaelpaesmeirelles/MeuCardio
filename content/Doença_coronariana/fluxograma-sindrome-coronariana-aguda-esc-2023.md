---
title: "Fluxograma: Síndrome Coronariana Aguda — do primeiro contato à reperfusão (ESC 2023)"
slug: fluxograma-sindrome-coronariana-aguda-esc-2023
theme: "Doença coronariana"
kind: fluxograma
summary: "Caminho decisório da dor torácica suspeita de SCA: ECG em 10 minutos, separação STEMI × NSTE-ACS, algoritmo 0h/1h de troponina ultrassensível e definição do tempo da estratégia invasiva."
review_status: revisado
source_refs: ["2023 ESC Guidelines for the management of acute coronary syndromes · European Heart Journal · 2023 · 44(38):3720-3826 · 10.1093/eurheartj/ehad191", "2023 ESC Guidelines for Acute Coronary Syndromes: Key Points · American College of Cardiology · 2023 · https://www.acc.org/Latest-in-Cardiology/ten-points-to-remember/2023/08/29/14/01/2023-esc-guidelines-acs-esc-2023", "'10 commandments' for the 2023 ESC Guidelines for the management of acute coronary syndromes · European Heart Journal · 2024 · 45(14):1193-1195 · https://academic.oup.com/eurheartj/article/45/14/1193/7516285"]
---

# Fluxograma: Síndrome Coronariana Aguda (ESC 2023)

A diretriz ESC 2023 unificou, pela primeira vez, STEMI e SCA sem elevação de ST
(NSTE-ACS) em um único documento. Testes diagnósticos e tratamento farmacológico
são praticamente os mesmos ao longo do espectro — **o que separa as formas de
apresentação é o tempo até a angiografia coronariana invasiva**. O fluxograma
abaixo é organizado em torno dessa decisão.

## Caminho decisório

```mermaid
flowchart TD
  A["Dor torácica ou equivalente<br/>suspeita de SCA"] --> B["ECG de 12 derivações<br/>em até 10 minutos do primeiro contato"]

  B --> C{"Elevação persistente<br/>do segmento ST?"}

  C -->|Sim| D["STEMI"]
  C -->|Não| E["NSTE-ACS suspeita"]

  D --> F{"ICP primária possível<br/>em até 120 min do diagnóstico?"}
  F -->|Sim| G["ICP primária"]
  F -->|Não| H["Fibrinólise imediata<br/>e transferência para centro com ICP"]

  E --> I{"Algum critério<br/>de risco muito alto?"}
  I -->|Sim| J["Angiografia invasiva imediata<br/>equiparada ao STEMI"]

  I -->|Não| K["Troponina ultrassensível<br/>algoritmo 0h/1h"]

  K --> L{"Resultado"}
  L -->|Rule-in| M["NSTEMI confirmado"]
  L -->|Zona de observação| N["Nova dosagem seriada<br/>e reavaliação clínica"]
  L -->|Rule-out| O["IAM afastado<br/>investigar diagnóstico alternativo"]

  N --> M
  N --> O

  M --> P{"Critério de alto risco?<br/>NSTEMI confirmado, GRACE > 140,<br/>elevação transitória de ST,<br/>alterações dinâmicas de ST/T"}
  P -->|Sim| Q["Estratégia invasiva precoce<br/>considerar em até 24h da admissão"]
  P -->|Não| R["Estratégia invasiva<br/>durante a internação"]
```

## Critérios de risco muito alto

Presente qualquer um deles, a angiografia invasiva é imediata, sem esperar
resultado de troponina:

- instabilidade hemodinâmica ou choque cardiogênico
- dor torácica recorrente ou persistente, refratária ao tratamento clínico
- insuficiência cardíaca aguda presumidamente secundária a isquemia em curso
- arritmia ameaçadora à vida ou parada cardíaca após a apresentação
- complicação mecânica
- alterações eletrocardiográficas dinâmicas recorrentes sugestivas de isquemia

## Observações sobre o uso do algoritmo 0h/1h

O algoritmo 0h/1h classifica o paciente em três faixas — *rule-out*, zona de
observação e *rule-in*. Os pontos de corte numéricos **dependem do ensaio de
troponina usado no laboratório**: não são intercambiáveis entre fabricantes, e
por isso não são reproduzidos aqui. Consulte os valores validados para o ensaio
da sua instituição.

A faixa de *rule-out* tem mortalidade e incidência de IAM cumulativas baixas em
30 dias, o que sustenta a alta segura a partir dela quando o quadro clínico
acompanha.

## Por que o tempo é a variável central

No STEMI, a reperfusão por ICP primária deve ocorrer em até 120 minutos do
diagnóstico; ultrapassado esse limite previsto, a fibrinólise imediata seguida
de transferência é a estratégia recomendada. No NSTE-ACS, a presença de critério
de risco muito alto aproxima o manejo do STEMI, com angiografia imediata.
