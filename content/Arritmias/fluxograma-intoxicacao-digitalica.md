---
title: "Intoxicação digitálica"
slug: fluxograma-intoxicacao-digitalica
theme: "Arritmias"
kind: fluxograma
summary: "Conduta imediata na suspeita de intoxicação digitálica: da dosagem sérica de digoxina e do potássio até a indicação do anticorpo antidigoxina Fab, o manejo da hipercalemia associada e a conduta quando o Fab não está disponível."
review_status: revisado
source_refs: ["Cardiac Glycoside (Digoxin) Toxicity. StatPearls, NCBI Bookshelf, NBK459165 — seção de manifestações clínicas e achados eletrocardiográficos, consultada em 30/07/2026", "Digoxin Immune Fab. StatPearls, NCBI Bookshelf, NBK556101 — seção de indicações e fórmulas de dose, consultada em 30/07/2026", "Cardiac Glycoside (Digoxin) Toxicity. StatPearls, NCBI Bookshelf, NBK459165 — seção de manejo agudo (contraindicação de cálcio intravenoso e de cardioversão elétrica sincronizada), consultada em 03/08/2026", "Farkas J. Digoxin & cardiac glycosides: toxicity & therapeutic use. EMCrit Project, Internet Book of Critical Care (IBCC) — seção de manejo de bradiarritmia, marca-passo e cardioversão, consultada em 03/08/2026"]
---

# Intoxicação digitálica

Protocolo de conduta imediata para suspeita de intoxicação digitálica (gatilho: náusea, alteração visual, bradiarritmia ou qualquer arritmia em paciente sob digoxina). Cobre da suspeita clínica e da dosagem sérica até a indicação do anticorpo antidigoxina Fab (Digibind/DigiFab), o manejo da hipercalemia associada e a conduta quando o Fab não está disponível de imediato.

## Árvore de decisão

```mermaid
flowchart TD
    S1["Suspeita clínica de intoxicação digitálica (sintomas gastrointestinais, neurológicos ou cardíacos em uso de digoxina)"]
    S2["Dosar digoxina sérica, potássio e função renal; ECG (buscar taquicardia ventricular bidirecional)"]
    D1{"Arritmia ou instabilidade hemodinâmica com risco de vida (bradicardia sintomática, assistolia, bloqueio AV refratário a atropina, taquicardia ventricular)?"}
    D1a{"Anticorpo Fab disponível de imediato?"}
    D1b{"Qual o tipo de instabilidade predominante?"}
    D1c{"Bradiarritmia refratária a atropina?"}
    D1d{"Fibrilação ventricular ou parada cardíaca sem pulso?"}
    D2{"Hipercalemia significativa por intoxicação aguda (potássio maior que 5,5mEq/L em adulto ou maior que 6mEq/L em criança)?"}
    D2a{"Hipercalemia com sinais de risco imediato (alterações eletrocardiográficas de hipercalemia grave ou arritmia associada)?"}
    D2b{"Cálcio IV é a única forma de estabilização possível, sem resposta a outras medidas?"}
    D3{"Ingestão aguda maciça conhecida (maior que 10mg em adulto ou maior que 4mg/0,1mg por kg em criança, ou nível sérico maior ou igual a 10ng/mL) ou intoxicação crônica com nível maior que 6ng/mL em adulto ou maior que 4ng/mL em criança?"}
    C1(["Fab disponível — administrar anticorpo antidigoxina (Digibind/DigiFab) pela dose calculada"])
    C2(["Marca-passo transcutâneo/transvenoso, com cautela pelo risco de irritabilidade miocárdica e arritmia ventricular"])
    C3(["Atropina IV e suporte clínico, sem marca-passo de rotina"])
    C4(["Desfibrilação e RCP conforme protocolo de parada cardiorrespiratória (ACLS) — não é cardioversão sincronizada"])
    C5(["Evitar cardioversão elétrica sincronizada, risco de precipitar arritmia ventricular maligna em digitálico — tratamento farmacológico do ritmo e correção de eletrólitos"])
    C6(["Cálcio IV com cautela, apesar do risco teórico de coração de pedra cardíaco em digitálico, por ser a única forma de estabilização imediata"])
    C7(["Medidas usuais que evitam cálcio — insulina com glicose, beta-agonista, bicarbonato — evitando cálcio IV pelo risco teórico de coração de pedra cardíaco em digitálico"])
    C8(["Não corrigir a hipercalemia isoladamente — é marcador de gravidade da intoxicação, e o Fab já reduz o potássio ao neutralizar a digoxina livre"])
    C9(["Calcular a dose de Fab pela fórmula correspondente — dose ingerida, nível sérico ou empírica — e administrar"])
    C10(["Sem indicação clara de Fab no momento — monitorização contínua, ECG e potássio seriados, reavaliação; considerar Fab se surgir novo critério"])

    S1 --> S2
    S2 --> D1
    D1 -->|"Sim"| D1a
    D1a -->|"Sim"| C1
    D1a -->|"Não"| D1b
    D1b -->|"Bradiarritmia (bradicardia sintomática ou BAV avançado)"| D1c
    D1c -->|"Sim"| C2
    D1c -->|"Não"| C3
    D1b -->|"Taquiarritmia ventricular com instabilidade"| D1d
    D1d -->|"Sim"| C4
    D1d -->|"Não"| C5
    D1 -->|"Não"| D2
    D2 -->|"Sim"| D2a
    D2a -->|"Sim"| D2b
    D2b -->|"Sim"| C6
    D2b -->|"Não"| C7
    D2a -->|"Não"| C8
    D2 -->|"Não"| D3
    D3 -->|"Sim"| C9
    D3 -->|"Não"| C10

    classDef conduta fill:#eef6ef,stroke:#2f7a4f,color:#12301f;
    class C1,C2,C3,C4,C5,C6,C7,C8,C9,C10 conduta;
```

Em todo ramo com indicação confirmada de Fab, a administração do anticorpo pela fórmula correspondente é a conduta definitiva; o que muda entre os ramos é a medida de suporte enquanto ele é obtido ou age. Mantenha em paralelo, em qualquer ramo: ECG contínuo, suspensão da digoxina, potássio sérico seriado e correção de outros distúrbios eletrolíticos (magnésio, função renal) — sem repetir isso a cada nó da árvore.

**Fórmulas de dose do Fab** (StatPearls, Digoxin Immune Fab):
- Dose ingerida conhecida: nº de frascos = (dose ingerida em mg × 0,8) ÷ 0,5mg de digoxina ligada por frasco
- Concentração sérica conhecida: nº de frascos = concentração sérica (ng/mL) × peso (kg) ÷ 100
- Dose empírica, nível desconhecido: 10 frascos em adulto; 5 frascos em criança <20kg

O evitar cálcio IV na hipercalemia associada à intoxicação digitálica reflete a preocupação teórica com o "coração de pedra" (potencialização do efeito inotrópico do digitálico levando a estado não-contrátil irreversível); é a orientação padrão quando há alternativa, mas não é absoluta — diante de hipercalemia com risco de vida iminente e sem resposta a outras medidas, o cálcio IV não deve ser retido.
