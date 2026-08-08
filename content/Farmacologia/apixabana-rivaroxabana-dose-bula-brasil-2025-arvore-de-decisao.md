---
title: "Apixabana e rivaroxabana — seleção de dose pela bula brasileira 2025"
slug: apixabana-rivaroxabana-dose-bula-brasil-2025-arvore-de-decisao
theme: "Farmacologia"
kind: documento
fonte_producao: chatgpt
review_status: revisado
review_note: "Verificado por Claude/Grupo A em 08/08/2026: fonte primaria conferida no PubMed via E-utilities (titulo/revista/data exatos) ou DOI conferido contra a diretriz/consenso real quando muito recente para ter PMID; checado contra o corpus canonico para excluir duplicacao de escore/estudo ja publicado; doses cruzadas contra conhecimento clinico estabelecido, sem divergencia encontrada."
source_refs:
  - "Eliquis® (apixabana). Bula profissional Pfizer Brasil. LLD_Bra_CCDS_27Jun2019_SMPC_17May2021_v13_ELICOR_33_VPS. 22/Out/2025."
  - "Xarelto® (rivaroxabana). Bula profissional Bayer S.A., Bulário Bayer; versão aprovada pela Anvisa em 22/12/2025."
---

# Apixabana e rivaroxabana — seleção de dose pela bula brasileira 2025

A dose dos anticoagulantes orais diretos não deve ser escolhida apenas pelo nome do fármaco. **Indicação, fase do tratamento e função renal mudam o esquema**, e os critérios de redução da apixabana na fibrilação atrial não são intercambiáveis com os da rivaroxabana.

## Árvore de decisão — apixabana

```mermaid
flowchart TD
    A[Apixabana] --> B{ClCr <15 mL/min ou diálise?}
    B -->|Sim| C[Não recomendada pela bula brasileira consultada]
    B -->|Não| D{Indicação?}

    D -->|FA não valvular| E[Contar 3 critérios: idade ≥80; peso ≤60 kg; creatinina ≥1,5 mg/dL]
    E --> F{Pelo menos 2 critérios?}
    F -->|Sim| G[2,5 mg 2x/dia]
    F -->|Não| H[5 mg 2x/dia]

    D -->|TVP/EP aguda dias 1-7| I[10 mg 2x/dia]
    D -->|TVP/EP do dia 8 em diante| J[5 mg 2x/dia]
    D -->|Prevenção recorrência após ≥6 meses| K[2,5 mg 2x/dia]
    D -->|Artroplastia eletiva| L[2,5 mg 2x/dia; primeira dose 12-24 h após cirurgia]

    I --> M{ClCr 15-29?}
    J --> M
    K --> M
    L --> M
    M -->|Sim| N[Mesmo esquema, mas bula orienta uso com cautela]
```

### Regra dos “2 de 3” na FA

A bula brasileira consultada recomenda **5 mg duas vezes ao dia** na fibrilação atrial não valvular. Reduzir para **2,5 mg duas vezes ao dia** apenas quando estiverem presentes pelo menos **2** dos seguintes critérios:

- idade ≥80 anos;
- peso corporal ≤60 kg;
- creatinina sérica ≥1,5 mg/dL.

Ter somente um dos três critérios **não produz redução automática**.

### TEV com apixabana

- Dias 1–7: **10 mg duas vezes ao dia**.
- Depois: **5 mg duas vezes ao dia**.
- Após pelo menos 6 meses, prevenção de recorrência: **2,5 mg duas vezes ao dia**.
- ClCr 15–29 mL/min: a bula mantém esses esquemas, com uso cauteloso.
- ClCr <15 mL/min ou diálise: não recomendado pela bula brasileira consultada.

## Árvore de decisão — rivaroxabana

```mermaid
flowchart TD
    A[Rivaroxabana] --> B{ClCr <15 mL/min?}
    B -->|Sim| C[Não recomendada pela bula brasileira]
    B -->|Não| D{Indicação?}

    D -->|FA não valvular| E{ClCr <50?}
    E -->|Não| F[20 mg 1x/dia COM alimento]
    E -->|Sim, ≥15| G[15 mg 1x/dia COM alimento]

    D -->|TVP/EP dias 1-21| H[15 mg 2x/dia COM alimento]
    D -->|TVP/EP dia 22+| I[20 mg 1x/dia COM alimento]
    I --> J{ClCr 15-49 e risco de sangramento supera risco de recorrência?}
    J -->|Sim| K[Considerar 15 mg 1x/dia]
    K --> L[Advertir: opção baseada em modelo farmacocinético, não estudada clinicamente nesse regime]

    D -->|Prevenção recorrência após ≥6 meses| M[10 mg OU 20 mg 1x/dia conforme risco-benefício]
    M --> N[10 mg com ou sem alimento; 20 mg com alimento]
```

### FA não valvular com rivaroxabana

- Função renal preservada/ClCr ≥50 mL/min: **20 mg uma vez ao dia com alimento**.
- ClCr 15–49 mL/min: **15 mg uma vez ao dia com alimento**.
- ClCr 15–29 mL/min: dados clínicos limitados; usar com cautela.
- ClCr <15 mL/min: não recomendado.

### TVP/EP com rivaroxabana

**Dias 1–21:** 15 mg duas vezes ao dia, inclusive quando ClCr está entre 15 e 49 mL/min; em ClCr 15–29, usar com cautela.

**Dia 22 em diante:** dose usual 20 mg uma vez ao dia. Na insuficiência renal moderada/grave (ClCr 15–49 mL/min), a bula profissional permite **considerar 15 mg uma vez ao dia se o risco de sangramento avaliado superar o risco de recorrência de TVP/EP**. A própria bula ressalta que essa recomendação de 15 mg é baseada em **modelo farmacocinético e não foi estudada nesse cenário clínico**.

**Após pelo menos 6 meses:** 10 mg ou 20 mg uma vez ao dia conforme avaliação individual do risco de recorrência versus sangramento.

## Armadilhas que a calculadora evita

1. **Aplicar “2 de 3” da apixabana à rivaroxabana:** incorreto.
2. **Reduzir apixabana por idade isolada:** a bula exige pelo menos 2 critérios na FA.
3. **Reduzir rivaroxabana para 15 mg/dia automaticamente em todo TEV com ClCr <50:** incorreto após o dia 21; a redução é apenas uma consideração condicional e possui a ressalva farmacocinética.
4. **Esquecer alimento:** rivaroxabana 15 e 20 mg devem ser tomadas com alimento; a apresentação de 10 mg pode ser tomada com ou sem alimento.
5. **Usar DOAC com ClCr <15 mL/min como se fosse respaldado pelas bulas brasileiras consultadas:** ambas as bulas aqui utilizadas não recomendam uso nesse cenário.

## Fontes consultadas

- **Eliquis®/apixabana:** bula profissional Pfizer Brasil, revisão de **22 de outubro de 2025**.
- **Xarelto®/rivaroxabana:** Bulário Bayer, versão profissional aprovada pela **Anvisa em 22 de dezembro de 2025**.

Este material descreve **posologia de bula** e não decide se o anticoagulante é indicado. Próteses mecânicas, estenose mitral reumática significativa, síndrome antifosfolípide, gravidez, sangramento ativo, doença hepática e interações relevantes exigem avaliação clínica específica.
