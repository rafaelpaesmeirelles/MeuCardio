---
title: "Qual escore usar no pré-operatório? Comparação e árvore de seleção"
slug: comparacao-e-selecao-de-escores-de-risco-pre-operatorio
theme: "Perioperatório"
kind: documento
fonte_producao: chatgpt
review_status: pendente_revisao
revisado_por_voce: false
summary: "Comparação prática entre RCRI, Gupta MICA, AUB-HAS2, GSCRI, DASI e ACS NSQIP, com árvore para escolher a metodologia conforme paciente, objetivo e cirurgia."
source_refs:
  - "Thompson A, Fleischmann KE, Smilowitz NR, et al. 2024 AHA/ACC Guideline for Perioperative Cardiovascular Management for Noncardiac Surgery. Circulation. 2024. PMID: 39316661. DOI: 10.1161/CIR.0000000000001285."
  - "Lee TH et al. Circulation. 1999;100:1043-1049. PMID: 10477528. DOI: 10.1161/01.CIR.100.10.1043."
  - "Gupta PK et al. Circulation. 2011;124:381-387. PMID: 21730309. DOI: 10.1161/CIRCULATIONAHA.110.015701."
  - "Dakik HA et al. J Am Coll Cardiol. 2019;73:3067-3078. PMID: 31221255. DOI: 10.1016/j.jacc.2019.04.023."
  - "Alrezk R et al. J Am Heart Assoc. 2017;6:e006648. PMID: 29146612. DOI: 10.1161/JAHA.117.006648."
  - "Hlatky MA et al. Am J Cardiol. 1989;64:651-654. PMID: 2782256. DOI: 10.1016/0002-9149(89)90496-7."
  - "Bilimoria KY et al. J Am Coll Surg. 2013;217:833-842.e1-3. PMID: 24055383. DOI: 10.1016/j.jamcollsurg.2013.07.385."
---

# Seleção da metodologia de risco

Nenhuma ferramenta responde todas as perguntas do pré-operatório. O primeiro passo é definir **qual desfecho se deseja estimar** e qual população está sendo avaliada.

## Árvore de seleção

```mermaid
flowchart TD
    A["Avaliação cardiovascular pré-operatória"] --> B{"Qual é a principal pergunta?"}
    B -->|"Quero uma triagem cardíaca simples e amplamente conhecida"| C["RCRI"]
    B -->|"Quero probabilidade percentual de IAM/parada cardíaca"| D["Gupta MICA"]
    B -->|"Quero um índice curto com emergência, anemia e sintomas"| E["AUB-HAS2"]
    B -->|"Paciente tem ≥65 anos e quero modelo sensível ao idoso"| F["GSCRI"]
    B -->|"Quero medir capacidade funcional"| G["DASI"]
    B -->|"Quero risco cirúrgico global e múltiplos desfechos"| H["ACS NSQIP oficial"]

    C --> I["6 fatores binários<br/>evento cardíaco maior"]
    D --> J["Idade + ASA + dependência funcional + creatinina + tipo cirúrgico"]
    E --> K["6 fatores binários<br/>morte/IAM/AVC"]
    F --> L["Modelo para ≥65 anos<br/>IAM/parada cardíaca"]
    G --> M["12 atividades<br/>DASI ≤34 = capacidade funcional ruim no algoritmo AHA/ACC 2024"]
    H --> N["Modelo dinâmico por CPT<br/>19 desfechos em 30 dias"]

    I --> O["Integrar com capacidade funcional e modificadores"]
    J --> O
    K --> O
    L --> O
    M --> O
    N --> O
    O --> P{"O resultado muda investigação ou manejo?"}
    P -->|"Não"| Q["Evitar exames adicionais sem indicação"]
    P -->|"Sim"| R["Aplicar árvore de ECG/eco/biomarcadores/isquemia"]
```

## Comparação resumida

| Método | Principal saída | Pontos fortes | Limitação central |
|---|---|---|---|
| **RCRI** | classes/pontos | simples, histórico, amplamente conhecido | pouca granularidade e não inclui idade/capacidade funcional |
| **Gupta MICA** | % IAM/PCR em 30 dias | individualização maior; inclui cirurgia e status funcional | implementação depende de regressão/categorias cirúrgicas |
| **AUB-HAS2** | baixo/intermediário/alto | seis perguntas simples; inclui emergência, anemia e sintomas | desfecho inclui AVC, diferente de outros modelos |
| **GSCRI** | risco IAM/PCR | específico para ≥65 anos | equação completa deve ser validada antes de cálculo local |
| **DASI** | 0–58,2 | capacidade funcional estruturada e recomendada em diretriz | não é escore de MACE; não diagnostica isquemia |
| **ACS NSQIP** | múltiplos riscos em 30 dias | amplo, procedimento-específico, atualizado | ferramenta externa/dinâmica; não deve ser automatizada na Corvia |

## Recomendação operacional para a função Corvia

Uma avaliação completa pode apresentar **mais de um eixo**, sem somar escores entre si:

1. **Risco cardiovascular:** RCRI e/ou Gupta MICA; AUB-HAS2 como alternativa complementar.
2. **Capacidade funcional:** DASI.
3. **Paciente idoso:** destacar GSCRI como metodologia geriátrica quando ≥65 anos.
4. **Risco cirúrgico global:** abrir ACS NSQIP oficial quando desejado.
5. **Modificadores de risco:** tratados fora dos escores por árvore clínica.

## Regra prática

**Não fazer média entre escores e não escolher o maior ou menor valor como “verdade”.** Cada modelo tem população, desfecho e variáveis diferentes. Divergência entre métodos é informação clínica que deve motivar revisão dos fatores responsáveis pela diferença.
