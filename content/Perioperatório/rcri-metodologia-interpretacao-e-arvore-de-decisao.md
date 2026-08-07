---
title: "RCRI (Lee): metodologia, interpretação e árvore de decisão"
slug: rcri-metodologia-interpretacao-e-arvore-de-decisao
theme: "Perioperatório"
kind: documento
fonte_producao: chatgpt
review_status: pendente_revisao
summary: "Como calcular e, principalmente, como usar o RCRI dentro do algoritmo contemporâneo de avaliação cardiovascular pré-operatória."
source_refs:
  - "Lee TH, Marcantonio ER, Mangione CM, et al. Circulation. 1999;100(10):1043-1049. PMID: 10477528. DOI: 10.1161/01.CIR.100.10.1043."
  - "Thompson A, Fleischmann KE, Smilowitz NR, et al. 2024 AHA/ACC perioperative guideline. DOI: 10.1161/CIR.0000000000001285."
  - "Halvorsen S, Mehilli J, Cassese S, et al. Eur Heart J. 2022;43(39):3826-3924. PMID: 36017553. DOI: 10.1093/eurheartj/ehac270."
---

# RCRI — Revised Cardiac Risk Index

## O que o escore mede

O RCRI foi derivado para predizer complicações cardíacas maiores após cirurgia não cardíaca. São **6 variáveis binárias, 1 ponto cada**:

1. cirurgia de alto risco;
2. cardiopatia isquêmica;
3. insuficiência cardíaca;
4. doença cerebrovascular;
5. diabetes em uso de insulina;
6. creatinina sérica pré-operatória >2,0 mg/dL.

## Por que existem percentuais diferentes publicados para o mesmo RCRI

Não se deve apresentar um único percentual como se fosse universal. O **endpoint e a coorte** mudam a taxa observada.

Na coorte de validação original de Lee, para o composto clássico de IAM, edema pulmonar, fibrilação ventricular/parada cardíaca e bloqueio AV completo, as taxas observadas foram aproximadamente:

- 0 pontos: **0,4%**;
- 1 ponto: **0,9%**;
- 2 pontos: **7,0%**;
- ≥3 pontos: **11,0%**.

Quando o endpoint é redefinido para IAM, parada cardíaca e morte cardíaca, publicações de reavaliação do RCRI mostram estimativas menores na coorte original (aproximadamente 0,4%, 1,0%, 2,4% e 5,4%). Portanto, o laudo deve informar **qual endpoint está sendo citado**.

A diretriz AHA/ACC 2024 não exige converter cada classe em um percentual histórico específico para decidir investigação: tradicionalmente considera **RCRI >1** como um marcador de risco perioperatório elevado dentro do algoritmo clínico.

## Árvore de cálculo

```mermaid
flowchart TD
  A["Paciente candidato a cirurgia não cardíaca"] --> B["Somar 1 ponto para cada um dos 6 critérios do RCRI"]
  B --> C{"RCRI = 0?"}
  C -->|"Sim"| D["Classe I"]
  C -->|"Não"| E{"RCRI = 1?"}
  E -->|"Sim"| F["Classe II"]
  E -->|"Não"| G{"RCRI = 2?"}
  G -->|"Sim"| H["Classe III"]
  G -->|"Não"| I["RCRI ≥3: Classe IV"]
```

## Árvore de uso clínico contemporâneo

```mermaid
flowchart TD
  A["RCRI calculado"] --> B{"RCRI >1?"}
  B -->|"Não"| C{"Cirurgia/procedimento de baixo risco e paciente clinicamente estável?"}
  C -->|"Sim"| D["Em geral, prosseguir sem teste de isquemia de rotina"]
  C -->|"Não"| E["Integrar risco do procedimento, sintomas, fragilidade e capacidade funcional"]
  B -->|"Sim"| F["Risco calculado elevado pelo limiar tradicional AHA/ACC"]
  F --> G["Avaliar capacidade funcional por DASI/METs"]
  G --> H{"DASI >34 ou ≥4 METs e sintomas estáveis?"}
  H -->|"Sim"| I["Em geral, prosseguir com otimização; teste adicional apenas se indicação independente"]
  H -->|"Não / desconhecido"| J["Considerar biomarcadores e perguntar se exame adicional mudará manejo"]
  J --> K{"Mudará manejo?"}
  K -->|"Não"| L["Não testar por rotina"]
  K -->|"Sim"| M["Considerar teste funcional/isquêmico ou CCTA conforme contexto"]
```

## Vantagens

- Simples, reproduzível e amplamente validado.
- Útil para comunicação e para identificar pacientes em quem a avaliação deve ser aprofundada.
- Requer poucas variáveis e pode ser calculado à beira do leito.

## Limitações

- Não incorpora idade como variável contínua.
- Não incorpora capacidade funcional ou fragilidade.
- A definição de “cirurgia de alto risco” é histórica e não captura toda a granularidade dos procedimentos contemporâneos.
- O risco absoluto depende do endpoint e da população; não misturar taxas de diferentes recalibrações.
- RCRI alto **não é indicação automática de teste de estresse ou coronariografia**.
