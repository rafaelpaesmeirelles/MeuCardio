---
title: "Fluxograma: Torsades de Pointes e QT Longo Adquirido — Conduta Imediata"
slug: fluxograma-torsades-de-pointes-e-qt-longo-adquirido
theme: "Arritmias"
kind: fluxograma
summary: "Árvore de decisão da conduta imediata no torsades de pointes e no QT longo adquirido: TdP ativa exige desfibrilação ou cardioversão conforme pulso/estabilidade seguida de sulfato de magnésio IV independente do nível sérico, e QT longo identificado sem TdP segue via de prevenção guiada pelo escore de Tisdale."
review_status: revisado
source_refs: ["Tisdale JE, Jaynes HA, Kingery JR, et al. Development and validation of a risk score to predict QT interval prolongation in hospitalized patients. Circ Cardiovasc Qual Outcomes. 2013;6(4):479-487. DOI: 10.1161/CIRCOUTCOMES.113.000152. PMID: 23716032 — pontuação por variável conferida contra duas fontes secundárias independentes, texto completo bloqueado nesta sessão (paywall)", "Torsade de Pointes. StatPearls, NCBI Bookshelf, NBK459388 — seção de tratamento, consultada em 30/07/2026"]
---

# Fluxograma: Torsades de Pointes e QT Longo Adquirido — Conduta Imediata

Torsades de pointes (TdP) é a taquicardia ventricular polimórfica associada ao
QT longo **adquirido** — por fármaco, distúrbio eletrolítico ou combinação dos
dois. A conduta imediata separa dois cenários que não se misturam: TdP **em
curso**, que exige estabilização elétrica conforme pulso/estabilidade e
sulfato de magnésio sem esperar a dosagem sérica, e QT longo **identificado
antes do evento**, em que a conduta é prevenir a torsades, não tratá-la. O
escore de risco e o detalhamento fisiopatológico estão no documento de
origem; aqui o foco é a sequência de decisão à beira do leito.

## Árvore de decisão

```mermaid
flowchart TD
  R1{"Torsades de pointes ativa<br/>(TV polimórfica documentada) ou<br/>QT longo identificado,<br/>sem TdP em curso?"}
  C_prev(["QT longo identificado, estável:<br/>suspender fármaco prolongador de QT,<br/>corrigir distúrbio eletrolítico e<br/>estratificar risco pelo escore de Tisdale —<br/>monitorização eletrocardiográfica conforme risco"])
  D2{"Paciente sem pulso?"}
  C_desfib(["Desfibrilação imediata —<br/>mesmo protocolo de FV/TV sem pulso"])
  D3{"Hemodinamicamente instável<br/>(hipotensão, síncope persistente,<br/>sinais de baixo débito)?"}
  C_cv(["Cardioversão elétrica sincronizada —<br/>100J monofásico ou 50J bifásico"])
  P_mg["Sulfato de magnésio IV:<br/>2g em push lento, independente do<br/>nível sérico de magnésio, seguido de<br/>infusão de manutenção de 1-4g/hora"]
  D4{"TdP recorrente apesar<br/>do sulfato de magnésio?"}
  C_manter(["Manter magnésio de manutenção e<br/>monitorização eletrocardiográfica<br/>contínua até normalização do QT"])
  C_refrat(["Overdrive pacing (FC ventricular<br/>90-110bpm, até 140bpm se necessário)<br/>ou isoproterenol IV 10-20mcg em push,<br/>ou infusão titulada para FC ~100bpm —<br/>mecanismo bradicardia/pausa-dependente;<br/>isoproterenol contraindicado no QT longo<br/>congênito, reservado ao adquirido"])

  R1 -->|"QT longo identificado, estável"| C_prev
  R1 -->|"TdP ativa"| D2
  D2 -->|"Sim, sem pulso"| C_desfib
  D2 -->|"Não, com pulso"| D3
  D3 -->|"Sim, instável"| C_cv
  D3 -->|"Não, estável"| P_mg
  P_mg -->|"Após magnésio"| D4
  D4 -->|"Não"| C_manter
  D4 -->|"Sim, refratária"| C_refrat

  classDef conduta fill:#eef6ef,stroke:#2f7a4f,color:#12301f;
  class C_prev,C_desfib,C_cv,C_manter,C_refrat conduta;
```

## O que se repete em todo ramo, e por isso não está no diagrama

**Suspender o fármaco prolongador de QT e corrigir o distúrbio eletrolítico de
base** é a primeira ação em qualquer ramo desta árvore — feita de imediato, em
paralelo à estabilização elétrica ou ao início do magnésio, nunca como medida
tardia ou acessória.

**Potássio alvo 4,5–5,0mEq/L** durante o tratamento da torsades — faixa
alta-normal, acima da normalidade habitual (3,5–4,5mEq/L), especificamente
para reduzir a dispersão de repolarização.

**Não usar antiarrítmicos de classe Ia ou III** (ex.: procainamida,
amiodarona, sotalol) no manejo agudo do torsades — esses fármacos prolongam
ainda mais o QT e podem perpetuar a arritmia.

**Reavaliação eletrocardiográfica contínua** (telemetria/monitor) em qualquer
ramo, até a normalização do QT.

## Escore de Tisdale — risco de prolongamento do QTc em paciente internado

Usado na via de **prevenção** (QT longo identificado, sem TdP ativa) para
decidir quem precisa de monitorização eletrocardiográfica mais próxima antes
que a torsades ocorra — não para tratar o evento já instalado.

| Variável | Pontos |
|---|---|
| Idade ≥68 anos | 1 |
| Sexo feminino | 1 |
| Diurético de alça | 1 |
| Potássio sérico ≤3,5mEq/L | 2 |
| QTc na admissão ≥450ms | 2 |
| IAM agudo | 2 |
| Sepse | 3 |
| Insuficiência cardíaca | 3 |
| Um fármaco prolongador de QTc | 3 |
| ≥2 fármacos prolongadores de QTc | 3 |
| **Pontuação máxima** | 21 |

**Estratificação de risco** (grupo de validação): baixo risco ≤6 pontos
(incidência 15%); risco moderado 7-10 pontos (incidência 37%); alto risco ≥11
pontos (incidência 73%).

## Isoproterenol é contraindicação formal no QT longo congênito

O isoproterenol (via de refratariedade ao magnésio) é **reservado ao QT longo
adquirido**. Na síndrome do QT longo **congênito** ele é contraindicado —
pode paradoxalmente prolongar ainda mais o QT nesse cenário, em vez de
encurtá-lo como no adquirido.
