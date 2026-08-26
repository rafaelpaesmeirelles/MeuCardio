---
title: "Hipotermia acidental e parada cardiorrespiratória"
slug: fluxograma-hipotermia-acidental-e-parada-cardiorrespiratoria
theme: "Terapia intensiva"
kind: fluxograma
summary: "Árvore de decisão da hipotermia acidental: separa quem ainda tem circulação (isolamento e transporte para reaquecimento, com rota direta a centro de ECLS se houver risco de instabilidade) de quem já está em parada — onde a temperatura central abaixo ou acima de 30°C decide reter ou não a adrenalina, espaçar o intervalo de doses e adiar novos choques em FV refratária, sempre rumo a reaquecimento por ECLS/ECMO."
review_status: revisado
review_note: "Atualizado em 26/08/2026 contra ERC/RCUK 2025. Acrescentados FC <45/min como critério de transferência direta a centro ECPR, dose de ataque de amiodarona 300 mg no ritmo chocável com postergação das doses seguintes até >30 °C e a exceção de não administrar adrenalina aos 30 °C quando a ECPR é iminente. A seção de avalanche permanece atribuída à fonte ERC 2021."
source_refs: ["Lott C, Karageorgos V, Abelairas-Gomez C, et al. European Resuscitation Council Guidelines 2025 Special Circumstances in Resuscitation. Resuscitation. 2025;215 Suppl 1:110753. DOI: 10.1016/j.resuscitation.2025.110753. PMID: 41117569.", "Resuscitation Council UK. Special circumstances guidelines 2025 — seção Accidental hypothermia, texto oficial conferido em 26/08/2026. https://www.resus.org.uk/library/2025-resuscitation-guidelines/special-circumstances-guidelines", "Lott C, Truhlář A, Alfonzo A, et al. European Resuscitation Council Guidelines 2021: Cardiac arrest in special circumstances. Resuscitation. 2021;161:152-219. DOI: 10.1016/j.resuscitation.2021.02.011. PMID: 33773826 — mantida para o trecho específico de resgate em avalanche."]
---

# Hipotermia acidental e parada cardiorrespiratória

Gatilho para este protocolo: **temperatura central medida <35 °C** (termômetro
de leitura baixa — timpânico se respiração espontânea, esofágico se via
aérea avançada), por exposição ao frio ou causa secundária. O eixo que
separa as condutas é, primeiro, **se o paciente já está em parada
cardiorrespiratória (PCR)** e, dentro da PCR, **se a temperatura central está
abaixo ou acima de 30 °C** — o corte que decide reter ou liberar a
adrenalina e adiar ou não novos choques em fibrilação ventricular (FV)
refratária.

## Árvore de decisão

```mermaid
flowchart TD
  R["Suspeita de hipotermia acidental: temperatura central medida<br/>com termômetro de leitura baixa — checar sinais de vida<br/>por até 1 min (exame clínico + ECG + capnografia/USG se disponíveis)"]
  R --> D1

  D1{"Paciente já está em parada cardiorrespiratória?"}
  D1 -->|"Não — ainda com circulação"| D2
  D1 -->|"Sim — em PCR"| D4

  D2{"Risco de instabilidade iminente:<br/>temperatura central <30°C, FC <45/min,<br/>arritmia ventricular ou PAS <90 mmHg?"}
  D2 -->|"Sim"| C1
  D2 -->|"Não"| C2

  C1(["Isolar do frio; transporte DIRETO e preferencial a centro<br/>com suporte de vida extracorpóreo (ECLS) de prontidão;<br/>iniciar RCP de imediato se houver deterioração ou parada"])
  C2(["Isolar do frio; transporte para hospital apropriado para<br/>reaquecimento; reaquecimento ativo não é indicado<br/>se o transporte for muito curto (menos de 1 hora)"])

  D4{"Temperatura central está abaixo de 30°C?"}
  D4 -->|"Sim, abaixo de 30°C"| M1
  D4 -->|"Não, 30°C ou mais"| M2

  M1["RCP contínua, com frequência de compressão e ventilação<br/>PADRÃO (igual ao paciente normotérmico);<br/>RETER adrenalina enquanto a temperatura estiver abaixo de 30°C"]
  M1 --> D5

  D5{"Fibrilação ventricular persiste<br/>após 3 tentativas de choque?"}
  D5 -->|"Sim, persiste"| C3
  D5 -->|"Não — ritmo não chocável, ou reverteu"| C4

  C3(["Após o 3º choque: amiodarona 300 mg de ataque;<br/>suspender NOVOS choques e doses adicionais de amiodarona<br/>até a temperatura ultrapassar 30°C; manter RCP contínua<br/>e seguir para reaquecimento por ECLS — preferencialmente VA-ECMO"])
  C4(["Manter RCP contínua, sem adrenalina, enquanto a temperatura<br/>estiver abaixo de 30°C; transporte direto a centro com ECLS<br/>para reaquecimento — preferencialmente ECMO, não CEC"])

  M2["RCP e desfibrilação seguem o algoritmo PADRÃO de PCR;<br/>aos 30°C, adrenalina 1 mg IV (exceto se ECPR iminente);<br/>repetir a cada 6–10 min enquanto a temperatura estiver entre 30–35°C"]
  M2 --> C5

  C5(["Ao atingir a normotermia, o protocolo padrão de drogas<br/>volta a valer; prosseguir RCP + reaquecimento (ECLS se<br/>disponível em até 6h; sem ECLS se não disponível) até RCE<br/>ou decisão de interromper"])

  classDef conduta fill:#eef6ef,stroke:#2f7a4f,color:#12301f;
  class C1,C2,C3,C4,C5 conduta;
```

## O que vale para todos os ramos, e por isso não está no diagrama

**Na hipotermia primária, PCR não testemunhada com assistolia como ritmo
inicial não é contraindicação** ao reaquecimento por ECLS.

**Em pacientes com temperatura abaixo de 28 °C**, RCP retardada pode ser
usada quando a RCP no local for perigosa demais ou inviável, e RCP
intermitente quando a contínua não for possível — é uma modificação
circunstancial (segurança do local), não um ramo clínico da árvore.

**Resgate em avalanche** segue regra própria, à parte deste fluxograma
geral: soterramento **menor que 60 minutos** é manejado como paciente
normotérmico (suporte avançado de vida padrão por, no mínimo, 20 minutos);
soterramento **maior que 60 minutos sem lesão claramente não sobrevivível**
recebe reanimação completa com reaquecimento por ECLS; soterramento **maior
que 60 minutos com via aérea obstruída** pode ter a RCP considerada fútil.
Dar 5 ventilações iniciais na parada por avalanche, porque a hipóxia é a
causa mais provável.

**Prognóstico e triagem**: o escore HOPE (Hypothermia Outcome Prediction
after ECLS rewarming — idade, sexo, temperatura central, potássio sérico,
presença de asfixia, duração da RCP) é o mais bem validado para estimar a
probabilidade de sobrevida antes de decidir reaquecer por ECLS, e é mais
confiável que a triagem tradicional por potássio sérico isolado.

**Nunca declarar óbito por inspeção rápida** no paciente profundamente
hipotérmico — ele pode parecer morto e ainda sobreviver à reanimação.
