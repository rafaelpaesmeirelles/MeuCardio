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

## Árvore de decisão

```mermaid
flowchart TD
  R0["Estenose aórtica grave"] --> D1{"Indicação de intervenção<br/>estabelecida?"}

  D1 -->|Não| C1(["Acompanhamento clínico<br/>e reavaliação periódica"])

  D1 -->|Sim| P1["Avaliação pelo Heart Team"]
  P1 --> D2{"Modo de intervenção"}

  D2 -->|Cirurgia| C2(["Troca valvar aórtica<br/>cirúrgica"])

  D2 -->|TAVI| D3{"Outra indicação de<br/>anticoagulação oral?"}
  D3 -->|Não| C3(["Implante por cateter e<br/>antiagregante plaquetário simples"])
  D3 -->|Sim| C4(["Implante por cateter e<br/>manutenção da anticoagulação<br/>já indicada"])

  classDef conduta fill:#eef5f8,stroke:#1c7293,color:#0b2e45;
  class C1,C2,C3,C4 conduta;
```

A decisão do Heart Team entre TAVI e cirurgia não é um teste com resposta
binária: pondera quatro conjuntos de fatores ao mesmo tempo, listados na seção
seguinte. Por isso eles não aparecem como ramos da árvore.

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
