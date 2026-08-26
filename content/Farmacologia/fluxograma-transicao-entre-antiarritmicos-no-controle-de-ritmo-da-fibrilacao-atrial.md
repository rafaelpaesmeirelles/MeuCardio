---
title: "Fluxograma: transição entre antiarrítmicos no controle de ritmo da fibrilação atrial"
slug: fluxograma-transicao-entre-antiarritmicos-no-controle-de-ritmo-da-fibrilacao-atrial
theme: "Farmacologia"
kind: fluxograma
fonte_producao: chatgpt
summary: "Árvore de decisão para trocar de antiarrítmico de controle de ritmo na fibrilação atrial por falha de eficácia, prolongamento de QT/evento arrítmico ou intolerância não cardíaca, incluindo o período de washout necessário conforme a meia-vida do fármaco suspenso."
review_status: revisado
review_note: "Verificado em 26/08/2026: PMIDs conferidos via PubMed E-utilities (esearch/esummary) — título, revista, volume e páginas batendo integralmente com o texto citado; nenhum PMID ou dado numérico foi inventado. Seleção de antiarrítmico por presença de cardiopatia estrutural e a contraindicação de classe Ic/dronedarona nesse contexto cruzadas contra as duas diretrizes de fibrilação atrial citadas."
source_refs:
  - "Joglar JA, Chung MK, Armbruster AL, et al. 2023 ACC/AHA/ACCP/HRS Guideline for the Diagnosis and Management of Atrial Fibrillation. Circulation. 2024;149(1):e1-e156. PMID 38033089."
  - "Hindricks G, Potpara T, Dagres N, et al. 2020 ESC Guidelines for the diagnosis and management of atrial fibrillation. Eur Heart J. 2021;42(5):373-498. PMID 32860505."
---

# Fluxograma: transição entre antiarrítmicos no controle de ritmo da fibrilação atrial

Trocar de antiarrítmico na fibrilação atrial não é só escolher o próximo da lista — o motivo da troca muda o caminho. Falha de eficácia em coração estruturalmente normal permite quase qualquer opção; falha em cardiopatia estrutural elimina a classe Ic por risco de proarritmia; e quando a troca é motivada por prolongamento de QT ou evento arrítmico, existe um período de washout obrigatório antes do próximo fármaco — e esse período muda de dias para semanas quando o fármaco suspenso é a amiodarona, pela meia-vida de eliminação extremamente longa.

## Árvore de decisão

```mermaid
flowchart TD
  R0["Paciente em antiarrítmico para controle de ritmo na fibrilação atrial,<br/>necessitando trocar de fármaco (falha, intolerância ou nova contraindicação)"]
  D1{"Qual o motivo da troca?"}
  D2{"Há cardiopatia estrutural significativa<br/>(insuficiência cardíaca, doença coronariana,<br/>hipertrofia de VE significativa)?"}
  C1(["Trocar para outro antiarrítmico de classe Ic (flecainida ou<br/>propafenona) ou considerar amiodarona/dronedarona/sotalol<br/>conforme perfil do paciente; sem necessidade de washout<br/>se ECG normal e sem sinais de toxicidade"])
  D3{"Há insuficiência cardíaca com fração de ejeção reduzida?"}
  C2(["Amiodarona é a opção preferencial (classe Ic e dronedarona<br/>contraindicadas nesse contexto); dofetilida como alternativa,<br/>se disponível e sob monitorização"])
  C3(["Sotalol ou amiodarona são as opções; classe Ic é contraindicada<br/>por risco de proarritmia na doença estrutural"])
  X1["Suspender o antiarrítmico atual e aguardar normalização<br/>do QTc antes de iniciar o próximo (washout mínimo de<br/>5 meias-vidas do fármaco suspenso)"]
  D4{"O fármaco suspenso foi amiodarona?"}
  C4(["Aguardar washout prolongado (semanas), com ECG seriado<br/>de QTc, antes de iniciar novo antiarrítmico que também<br/>prolongue QT; considerar classe Ic, se sem cardiopatia<br/>estrutural, por não ter efeito aditivo relevante em QT"])
  C5(["Washout de aproximadamente 2-3 dias (5 meias-vidas), com<br/>monitorização de QTc, antes de iniciar o novo antiarrítmico;<br/>evitar sobreposição de fármacos que prolongam QT"])
  C6(["Suspender o fármaco causador do efeito adverso e reavaliar<br/>a indicação de controle de ritmo com fármaco de perfil de<br/>efeitos colaterais distinto (ex.: dronedarona ou classe Ic,<br/>se sem cardiopatia estrutural); sem necessidade de washout<br/>de segurança elétrica"])

  R0 --> D1
  D1 -->|"Falha de eficácia (recorrência de FA em dose otimizada)"| D2
  D2 -->|"Não — coração estruturalmente normal"| C1
  D2 -->|"Sim — cardiopatia estrutural presente"| D3
  D3 -->|"Sim"| C2
  D3 -->|"Não — doença coronariana ou hipertrofia sem IC"| C3
  D1 -->|"Prolongamento do QT ou evento arrítmico ventricular<br/>associado ao fármaco atual"| X1
  X1 --> D4
  D4 -->|"Sim — meia-vida muito longa (semanas a meses)"| C4
  D4 -->|"Não — sotalol, dofetilida ou outro fármaco<br/>de meia-vida mais curta"| C5
  D1 -->|"Intolerância não cardíaca (ex.: disfunção tireoidiana<br/>ou pulmonar por amiodarona)"| C6

  classDef conduta fill:#eef6ef,stroke:#2f7a4f,color:#12301f;
  class C1,C2,C3,C4,C5,C6 conduta;
```

## O que a árvore não mostra

- **Ablação por cateter pode ser preferível a uma segunda ou terceira tentativa de antiarrítmico**, especialmente após falha de um primeiro fármaco em paciente sintomático — as diretrizes atuais de FA rebaixaram o limiar para oferecer ablação mais cedo, e essa alternativa não aparece nesta árvore, que é só sobre escolha farmacológica.
- **"Pill-in-the-pocket" com flecainida ou propafenona** é uma estratégia à parte (cardioversão química ambulatorial para episódio paroxístico) e não uma "troca de antiarrítmico de manutenção" — não está contemplada aqui.
- **Ajuste de dose por função renal e hepática** é necessário para vários destes fármacos (sotalol e dofetilida por via renal, propafenona por via hepática) e não está detalhado nesta árvore, que trata apenas de qual classe escolher e do tempo de washout.
- **Síndromes arritmogênicas hereditárias (Brugada, QT longo congênito)** mudam completamente a lista de fármacos seguros e exigem avaliação eletrofisiológica especializada antes de qualquer troca — fora do escopo desta árvore, pensada para FA sem essas condições de base.
- **O tempo de 5 meias-vidas para washout é uma aproximação farmacocinética**, não uma regra fixa de segurança elétrica — em pacientes com função renal/hepática reduzida, a eliminação é mais lenta e o intervalo real de segurança pode ser maior do que o calculado pela meia-vida de bula.