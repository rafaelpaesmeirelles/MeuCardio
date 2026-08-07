---
title: "Furosemida IV na IC aguda — metodologia do ensaio DOSE"
slug: furosemida-iv-ic-aguda-ensaio-dose-arvore-de-metodologia
theme: "Insuficiência cardíaca"
kind: documento
fonte_producao: chatgpt
review_status: pendente_revisao
source_refs:
  - "Felker GM, Lee KL, Bull DA, et al. Diuretic Strategies in Patients with Acute Decompensated Heart Failure. N Engl J Med. 2011;364:797-805. PMID: 21366472. DOI: 10.1056/NEJMoa1005419."
---

# Furosemida IV na IC aguda — metodologia do ensaio DOSE

Esta calculadora reproduz **a metodologia randomizada do ensaio DOSE**. Ela não define uma dose universal para todo paciente com insuficiência cardíaca aguda.

```mermaid
flowchart TD
    A[IC aguda com congestão e uso crônico prévio de diurético de alça] --> B[Converter dose oral domiciliar para equivalente de furosemida]
    B --> B1[Furosemida: 1 mg = 1 mg equivalente]
    B --> B2[Torsemida 20 mg = furosemida 40 mg]
    B --> B3[Bumetanida 1 mg = furosemida 40 mg]
    B1 --> C{Estratégia do ensaio}
    B2 --> C
    B3 --> C
    C -->|Baixa dose| D[Total IV/dia = 1x dose oral equivalente]
    C -->|Alta dose| E[Total IV/dia = 2,5x dose oral equivalente]
    D --> F{Modo}
    E --> F
    F -->|Bolus q12 h| G[Dividir total IV diário em 2 bolus]
    F -->|Infusão contínua| H[Dividir total IV diário por 24 = mg/h]
    G --> I[Reavaliar diurese, congestão, peso, PA, creatinina e eletrólitos]
    H --> I
```

## População do DOSE

O ensaio randomizou 308 pacientes com insuficiência cardíaca aguda descompensada que:

- tinham história de IC crônica;
- usavam diurético de alça oral havia pelo menos 1 mês;
- recebiam dose equivalente de furosemida entre **80 e 240 mg/dia**.

Foram excluídos, entre outros, pacientes com PAS <90 mmHg, creatinina >3,0 mg/dL e aqueles que precisavam de vasodilatador ou inotrópico IV para IC.

## Estratégias comparadas

### Intensidade

- **Baixa dose:** total de furosemida IV/dia igual à dose oral domiciliar equivalente.
- **Alta dose:** total de furosemida IV/dia = **2,5 vezes** a dose oral equivalente.

### Forma de administração

- bolus IV a cada 12 horas;
- ou infusão IV contínua.

## Resultado principal

Não houve diferença significativa nos endpoints coprimários entre bolus e infusão contínua. A comparação alta versus baixa dose também não atingiu diferença significativa nos endpoints coprimários, embora a estratégia de alta dose tenha produzido maior diurese e tendências favoráveis em algumas medidas de sintomas/congestão.

A elevação transitória da creatinina >0,3 mg/dL foi mais frequente na estratégia de alta dose (**23% versus 14%**).

## Como a calculadora deve ser interpretada

O resultado significa:

> “Esta é a dose que reproduz este braço do ensaio DOSE para a dose domiciliar informada.”

Não significa:

> “Esta é obrigatoriamente a melhor dose para este paciente.”

Se o equivalente domiciliar informado estiver fora de **80–240 mg/dia de furosemida**, a calculadora mantém a aritmética, mas exibe alerta de que a extrapolação não reproduz diretamente a população estudada.

## Fonte

Felker GM, Lee KL, Bull DA, et al. Diuretic Strategies in Patients with Acute Decompensated Heart Failure. *N Engl J Med*. 2011;364:797–805. PMID **21366472**. DOI **10.1056/NEJMoa1005419**.
