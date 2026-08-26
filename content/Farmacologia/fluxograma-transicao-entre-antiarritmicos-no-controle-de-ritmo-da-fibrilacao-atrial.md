---
title: "Fluxograma: transição entre antiarrítmicos no controle de ritmo da fibrilação atrial"
slug: fluxograma-transicao-entre-antiarritmicos-no-controle-de-ritmo-da-fibrilacao-atrial
theme: "Farmacologia"
kind: fluxograma
fonte_producao: chatgpt
summary: "Árvore de decisão para trocar de antiarrítmico de controle de ritmo na fibrilação atrial por falha de eficácia, prolongamento de QT/evento arrítmico ou intolerância não cardíaca, incluindo o período de washout necessário conforme a meia-vida do fármaco suspenso."
review_status: revisado
review_note: "Auditoria científica em 26/08/2026 contra a diretriz ACC/AHA/ACCP/HRS 2023. Removidos washout fixo não sustentado e sobreposição insegura; corrigida seleção por HFrEF, infarto/cicatriz, QT, função renal e descompensação recente, incluindo internação mínima de 3 dias para iniciar/recarregar dofetilida ou sotalol oral. Mantida pendência de revisão médica/eletrofisiológica antes da publicação clínica."
source_refs:
  - "Joglar JA, Chung MK, Armbruster AL, et al. 2023 ACC/AHA/ACCP/HRS Guideline for the Diagnosis and Management of Atrial Fibrillation. Circulation. 2024;149(1):e1-e156. PMID 38033089."
  - "Hindricks G, Potpara T, Dagres N, et al. 2020 ESC Guidelines for the diagnosis and management of atrial fibrillation. Eur Heart J. 2021;42(5):373-498. PMID 32860505."
---

# Fluxograma: transição entre antiarrítmicos no controle de ritmo da fibrilação atrial

Trocar de antiarrítmico na fibrilação atrial exige reavaliar se o controle de ritmo farmacológico ainda é a melhor estratégia, o substrato cardíaco e a toxicidade que motivou a troca. Não existe um washout universal: QTc, eletrólitos, função renal/hepática, meia-vida, interações e persistência da amiodarona definem a transição. Dofetilida e sotalol oral exigem iniciação/recarregamento monitorizado.

## Árvore de decisão

```mermaid
flowchart TD
  R0["Paciente em antiarrítmico para controle de ritmo na fibrilação atrial,<br/>necessitando trocar de fármaco (falha, intolerância ou nova contraindicação)"]
  X0["Antes da troca: ECG/QTc, K+, Mg++, função renal/hepática,<br/>FEVE, infarto/cicatriz, interações e indicação de ablação"]
  D1{"Qual o motivo da troca?"}
  D2{"Há HFrEF (FEVE ≤40%)?"}
  C1(["Dofetilida ou amiodarona; iniciar/recarregar dofetilida<br/>internado por pelo menos 3 dias, com ClCr e ECG contínuo;<br/>evitar classe Ic, dronedarona e, em geral, sotalol"])
  D3{"Há infarto prévio, cicatriz/fibrose ventricular<br/>ou cardiopatia estrutural significativa?"}
  C2(["Não usar flecainida/propafenona; considerar dronedarona<br/>se não houve IC descompensada recente/disfunção grave,<br/>ou dofetilida/sotalol conforme QT, rim e monitorização;<br/>reservar amiodarona quando outras estratégias falham"])
  C3(["Flecainida ou propafenona com bloqueador do nó AV são<br/>opções; dronedarona, dofetilida ou sotalol dependem de<br/>QT/rim/comorbidades; reservar amiodarona pelo perfil tóxico"])
  C4(["Suspender o agente, corrigir K+/Mg++ e aguardar QTc seguro;<br/>não aplicar washout fixo nem sobrepor prolongadores de QT;<br/>se iniciar dofetilida ou sotalol oral, internar por ≥3 dias"])
  C5(["Suspender e tratar a toxicidade orgânica; definir intervalo<br/>pela eliminação e interações do agente — amiodarona persiste<br/>por semanas/meses; escolher substituto pelo substrato cardíaco"])

  R0 --> X0
  X0 --> D1
  D1 -->|"Falha de eficácia (recorrência de FA em dose otimizada)"| D2
  D2 -->|"Sim"| C1
  D2 -->|"Não"| D3
  D3 -->|"Sim"| C2
  D3 -->|"Não"| C3
  D1 -->|"Prolongamento do QT ou evento ventricular"| C4
  D1 -->|"Intolerância não cardíaca/toxicidade orgânica"| C5

  classDef conduta fill:#eef6ef,stroke:#2f7a4f,color:#12301f;
  class C1,C2,C3,C4,C5 conduta;
```

## O que a árvore não mostra

- **Ablação por cateter pode ser preferível a uma segunda ou terceira tentativa de antiarrítmico**, especialmente após falha de um primeiro fármaco em paciente sintomático — as diretrizes atuais de FA rebaixaram o limiar para oferecer ablação mais cedo, e essa alternativa não aparece nesta árvore, que é só sobre escolha farmacológica.
- **"Pill-in-the-pocket" com flecainida ou propafenona** é uma estratégia à parte (cardioversão química ambulatorial para episódio paroxístico) e não uma "troca de antiarrítmico de manutenção" — não está contemplada aqui.
- **Ajuste de dose por função renal e hepática** é necessário para vários destes fármacos (sotalol e dofetilida por via renal, propafenona por via hepática) e não está detalhado nesta árvore, que trata apenas de qual classe escolher e do tempo de washout.
- **Dofetilida e sotalol oral não devem ser iniciados como simples troca ambulatorial.** A diretriz recomenda pelo menos 3 dias em ambiente com cálculo de ClCr, ECG contínuo e capacidade de ressuscitação para iniciação ou recarga.
- **Síndromes arritmogênicas hereditárias (Brugada, QT longo congênito)** mudam completamente a lista de fármacos seguros e exigem avaliação eletrofisiológica especializada antes de qualquer troca — fora do escopo desta árvore, pensada para FA sem essas condições de base.
- **Não existe regra universal de cinco meias-vidas.** A transição é individualizada por toxicidade, QTc, rim/fígado e interações; amiodarona exige cautela especial porque seus efeitos e interações persistem por semanas a meses.
