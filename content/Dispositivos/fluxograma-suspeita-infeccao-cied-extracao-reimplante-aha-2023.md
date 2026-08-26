---
title: "Fluxograma: suspeita de infecção de CIED — diagnóstico, extração e reimplante (AHA 2023)"
slug: fluxograma-suspeita-infeccao-cied-extracao-reimplante-aha-2023
theme: "Dispositivos"
kind: fluxograma
summary: "Caminho específico da suspeita de infecção de marcapasso, CDI ou TRC: reconhecer bolsa infectada, interpretar bacteremia e ETE/PET no contexto, remover todo o sistema quando a infecção é definitiva e só então planejar reimplante."
review_status: revisado
review_note: "Fluxograma auditado em 26/08/2026 contra o Scientific Statement AHA no periódico, sua página oficial Top Things to Know e o registro PubMed (PMID 38047353; DOI 10.1161/CIR.0000000000001187). A associação entre remoção em até 7 dias e menor mortalidade é observacional e foi rotulada como tal. O statement não é diretriz GRADE e não fornece um algoritmo validado; a árvore abaixo organiza suas decisões clínicas sem criar doses ou classes de recomendação. Cinco vínculos internos conferidos contra slugs existentes."
source_refs: ["Baddour LM, Esquer Garrigos Z, Sohail MR, et al. Update on Cardiovascular Implantable Electronic Device Infections and Their Prevention, Diagnosis, and Management: A Scientific Statement From the American Heart Association. Circulation. 2024;149(2):e201-e216. DOI: 10.1161/CIR.0000000000001187. PMID: 38047353. https://www.ahajournals.org/doi/10.1161/CIR.0000000000001187", "American Heart Association. Top Things to Know: Update on Cardiovascular Implantable Electronic Device Infections and Their Prevention, Diagnosis and Management. 04/12/2023. https://professional.heart.org/en/science-news/update-on-cardiovascular-implantable-electronic-device-infections/top-things-to-know"]
---

# Fluxograma: suspeita de infecção de CIED (AHA 2023)

Este fluxo começa onde o algoritmo geral de endocardite não basta: **bolsa do gerador, eletrodos e decisão de retirar/reimplantar um CIED**. CIED inclui marcapasso, cardiodesfibrilador implantável e sistemas de ressincronização.

## Da suspeita ao diagnóstico operacional

```mermaid
flowchart TD
  A["Paciente com CIED e suspeita de infecção"] --> B{"Há flutuação, drenagem purulenta,<br/>trajeto fistuloso ou erosão/exposição<br/>na bolsa do gerador?"}

  B -->|Sim| C(["Infecção de bolsa definitiva<br/>Coletar culturas e envolver imediatamente<br/>infectologia + equipe de extração"])
  B -->|Não| D["Colher hemoculturas antes do antibiótico<br/>se a condição clínica permitir<br/>e buscar fonte alternativa"]

  D --> E{"Hemoculturas positivas?"}
  E -->|Não| F{"Febre/SIRS persistente,<br/>sem outra fonte?"}
  F -->|Não| G(["Infecção de CIED não demonstrada<br/>Investigar outro diagnóstico e reavaliar<br/>se surgirem novos sinais"])
  F -->|Sim| H["ETE e, se a suspeita permanecer,<br/>considerar PET/CT com 18F-FDG"]

  E -->|Sim| I{"S. aureus ou estafilococo<br/>coagulase-negativo?"}
  I -->|Sim| J["ETE: ecodensidade no eletrodo,<br/>no contexto da bacteremia estafilocócica,<br/>é altamente sugestiva"]
  I -->|Não| K["Se bacteremia persiste por mais de 72 h<br/>com terapia apropriada e sem outra fonte,<br/>suspeitar de infecção de CIED"]
  K --> L["ETE; PET/CT com 18F-FDG pode apoiar<br/>infecção de eletrodo na bacteremia<br/>não estafilocócica"]

  H --> M{"Conjunto clínico, microbiológico<br/>e de imagem confirma infecção?"}
  J --> M
  L --> M
  M -->|Não/indeterminado| N(["Não interpretar massa no eletrodo<br/>ou PET isoladamente; discutir com equipe<br/>e repetir/estender investigação conforme risco"])
  M -->|Sim| O(["Infecção definitiva de CIED"])
  C --> O

  classDef action fill:#eef5f8,stroke:#1c7293,color:#0b2e45;
  class C,G,N,O action;
```

### Duas cautelas de imagem

- **ETE não é diagnóstico isolado**: ecodensidades em eletrodos podem ser trombos ou material fibrótico; o resultado deve ser integrado a hemoculturas e quadro clínico.
- **PET/CT pode ser falsamente pouco sensível** em infecção discreta de bolsa/eletrodo ou após antibiótico; um exame negativo nessas condições não encerra sozinho a investigação.

## Da infecção definitiva ao reimplante

```mermaid
flowchart TD
  A(["Infecção definitiva de CIED<br/>ou endocardite valvar em paciente com CIED"]) --> B["Remover completamente gerador e eletrodos<br/>+ colher material + antimicrobiano dirigido"]
  B --> C["Não adiar encaminhamento:<br/>remoção em até 7 dias associou-se a menor<br/>mortalidade em dados observacionais"]
  C --> D{"O paciente ainda tem indicação<br/>de dispositivo após a extração?"}
  D -->|Não| E(["Não reimplantar<br/>Acompanhar a indicação clínica"])
  D -->|Sim| F{"Há endocardite valvar?"}
  F -->|Não| G["Aguardar resolução local e sistêmica<br/>+ hemoculturas negativas por pelo menos 72 h"]
  F -->|Sim| H["Aguardar resolução local e sistêmica<br/>+ hemoculturas negativas por 14 dias,<br/>conforme o statement"]
  G --> I["Implantar em sítio distante do infectado:<br/>contralateral, ilíaco ou epicárdico"]
  H --> I
  I --> J(["Se alto risco de reinfecção, considerar<br/>marcapasso sem eletrodo ou S-ICD<br/>quando compatíveis com a necessidade clínica"])

  classDef action fill:#eef5f8,stroke:#1c7293,color:#0b2e45;
  class E,J action;
```

O benefício associado à extração precoce não define um “prazo seguro” para espera: é evidência observacional e reforça **agilidade**, não autorização para postergar uma remoção já indicada.

## Exceção de alto risco

Quando o risco da remoção supera claramente o benefício, o statement admite supressão antimicrobiana crônica em pacientes selecionados. Isso é exceção individualizada, idealmente decidida por equipe multidisciplinar; não equivale a tratar rotineiramente infecção definitiva apenas com antibiótico.

## Conteúdo CorVIA conectado

- [Orientação AHA, extração precoce e WRAP-IT](/biblioteca/infeccao-de-dispositivo-cardiaco-extracao-de-eletrodo-e-envelope-antibiotico)
- [Infecção de CIED: biofilme, ETE e explante completo](/biblioteca/infeccao-de-cied-espectro-clinico-biofilme-eco-transesofagico-e-necessidade-de-explante-completo)
- [Extração transvenosa de eletrodo](/biblioteca/extracao-de-eletrodo-transvenoso-seguranca-e-o-efeito-do-volume-do-centro)
- [Critérios Duke-ISCVID 2023](/biblioteca/duke-iscvid-2023-criterios-diagnosticos-endocardite-infecciosa)
- [Fluxograma geral de endocardite ESC 2023](/biblioteca/fluxograma-endocardite-infecciosa-esc-2023)

## O que este fluxo não decide

- escolha e duração do antimicrobiano, que dependem de agente, foco, culturas do sistema e presença de endocardite valvar;
- técnica de extração, que depende de anatomia, tempo de implante, carga de eletrodos e experiência do centro;
- necessidade de aspiração de vegetação ou cirurgia valvar;
- reimplante automático: a indicação do dispositivo deve ser reavaliada depois da extração.
