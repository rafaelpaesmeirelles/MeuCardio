---
title: "Fluxograma: Estenose Aórtica grave — decisão de intervenção e escolha da via (ESC/EACTS 2021)"
slug: fluxograma-estenose-aortica-decisao-de-intervencao-esc-eacts-2021
theme: "Valvopatias"
kind: fluxograma
summary: "Da estenose aórtica grave à escolha entre TAVI e cirurgia: decisão do Heart Team a partir de características clínicas, anatômicas, viabilidade transfemoral, experiência local e preferência informada do paciente."
review_status: revisado
source_refs: ["2021 ESC/EACTS Guidelines for the management of valvular heart disease · European Heart Journal · 2022 · 43(7):561-632 · https://academic.oup.com/eurheartj/article/43/7/561/6358470", "2021 ESC/EACTS Valvular Heart Disease Guidelines: Key Points · American College of Cardiology · 2021 · https://www.acc.org/Latest-in-Cardiology/ten-points-to-remember/2021/08/28/20/58/2021-ESC-EACTS-Guidelines-VHD-ESC-2021", "'Ten commandments' for the 2021 ESC/EACTS Guidelines on valvular heart disease · European Heart Journal · 2021 · 42(41):4207-4210 · https://academic.oup.com/eurheartj/article/42/41/4207/6371303"]
---

# Fluxograma: Estenose Aórtica grave — decisão de intervenção (ESC/EACTS 2021)

A diretriz europeia de 2021 **não resolve a escolha entre TAVI e cirurgia por um
corte etário rígido**. A decisão é atribuída ao Heart Team e resulta da
combinação de vários eixos — clínico, anatômico, técnico e de preferência do
paciente. O fluxograma reflete essa estrutura: a via de acesso é o último nó, não
o primeiro.

## Caminho decisório

```mermaid
flowchart TD
  A["Estenose aórtica grave"] --> B{"Indicação de intervenção<br/>estabelecida?"}
  B -->|Não| C["Acompanhamento clínico<br/>e reavaliação periódica"]
  B -->|Sim| D["Avaliação pelo Heart Team"]

  D --> E["Características clínicas"]
  D --> F["Características anatômicas"]
  D --> G["Fatores do serviço"]
  D --> H["Preferência informada<br/>do paciente"]

  E --> E1["Idade e expectativa<br/>de vida estimada"]
  E --> E2["Condição geral"]
  E --> E3["Risco relativo de<br/>cirurgia e de TAVI"]

  F --> F1["Viabilidade de acesso<br/>transfemoral"]
  F --> F2["Anatomia valvar e vascular"]

  G --> G1["Experiência local"]
  G --> G2["Dados de desfecho<br/>do serviço"]

  E1 --> I{"Modo de intervenção"}
  E2 --> I
  E3 --> I
  F1 --> I
  F2 --> I
  G1 --> I
  G2 --> I
  H --> I

  I -->|TAVI| J["Implante valvar aórtico<br/>por cateter"]
  I -->|Cirurgia| K["Troca valvar aórtica<br/>cirúrgica"]

  J --> L{"Outra indicação de<br/>anticoagulação oral?"}
  L -->|Não| M["Antiagregante plaquetário simples"]
  L -->|Sim| N["Manter a indicação<br/>de anticoagulação"]
```

## Os quatro eixos da decisão do Heart Team

A escolha do modo de intervenção mais apropriado deve considerar:

1. **características clínicas** — idade e expectativa de vida estimada, condição
   geral, e os riscos relativos de cirurgia e de TAVI para aquele paciente;
2. **características anatômicas**, incluindo a viabilidade do acesso
   transfemoral para TAVI;
3. **experiência local e dados de desfecho do próprio serviço**;
4. **preferência informada do paciente**.

## Antiagregação após TAVI

Em pacientes **sem outra indicação de anticoagulante oral**, recomenda-se
antiagregante plaquetário simples após o TAVI.

## Sobre a idade como critério

As diretrizes europeia e americana concordam que idade, risco cirúrgico,
durabilidade esperada da prótese e valores do paciente devem orientar a escolha
entre TAVI e cirurgia — mas **adotam pontos de corte etários diferentes entre
si**. A abordagem da ESC/EACTS 2021 é deliberadamente mais flexível e centrada
no paciente do que uma regra de idade isolada, e é por isso que este fluxograma
não fixa um número.
