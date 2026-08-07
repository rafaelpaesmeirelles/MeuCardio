---
title: "Fluxograma: reanimação neonatal na sala de parto — AHA/AAP 2025"
slug: fluxograma-reanimacao-neonatal-na-sala-de-parto-aha-aap-2025
theme: "Cardiologia pediátrica"
kind: fluxograma
summary: "Árvore de decisão para o recém-nascido que não inicia transição adequada: passos iniciais, ventilação, correção da ventilação, compressões 3:1 e adrenalina."
review_status: revisado
source_refs: ["Lee HC, Strand ML, Finan E, et al. Part 5: Neonatal Resuscitation: 2025 American Heart Association and American Academy of Pediatrics Guidelines for Cardiopulmonary Resuscitation and Emergency Cardiovascular Care. Circulation. 2025;152(suppl 2):S385-S423. DOI: 10.1161/CIR.0000000000001367."]
---

# Reanimação neonatal na sala de parto

```mermaid
flowchart TD
  R0["Recém-nascido ao nascer"]
  D1{"Respira/chora e apresenta boa transição?"}
  C1(["Cuidados de rotina, termorregulação,<br/>contato pele a pele e monitorização"])
  P1["Passos iniciais: aquecer, posicionar via aérea,<br/>secar quando apropriado e estimular"]
  D2{"Apneia/gasping OU FC <100 bpm?"}
  C2(["Ventilação com pressão positiva em até 60 s:<br/>30–60 insuflações/min; ajustar pressão para<br/>elevação da FC e movimento torácico"])
  C3(["Monitorizar respiração, FC, temperatura<br/>e saturação; suporte conforme necessidade"])
  D3{"Após ventilação: FC subiu e tórax expande?"}
  P2["Corrigir ventilação: máscara/posição/obstrução/fuga;<br/>considerar tubo endotraqueal ou máscara laríngea"]
  D4{"Após ≥30 s de ventilação que move o tórax:<br/>FC ainda <60 bpm?"}
  C4(["Continuar ventilação e monitorização;<br/>titular oxigênio às metas de saturação"])
  P3["Iniciar compressões 3:1,<br/>preferencialmente com via aérea alternativa;<br/>técnica dos 2 polegares; considerar O₂ 100%"]
  D5{"Após 60 s de compressões + ventilação adequada:<br/>FC ainda <60 bpm?"}
  C5(["Suspender compressões quando FC ≥60 bpm;<br/>manter ventilação até respiração/FC adequadas<br/>e reduzir O₂ conforme metas"])
  C6(["Administrar adrenalina preferencialmente IV<br/>por veia umbilical; IO se necessário;<br/>ET apenas como ponte enquanto obtém acesso;<br/>manter ventilação/compressões e buscar causas reversíveis"])

  R0 --> D1
  D1 -->|"Sim"| C1
  D1 -->|"Não"| P1
  P1 --> D2
  D2 -->|"Sim"| C2
  D2 -->|"Não"| C3
  C2 --> D3
  D3 -->|"Não"| P2
  D3 -->|"Sim, mas FC permanece <60"| D4
  D3 -->|"Sim e FC ≥60"| C4
  P2 --> D4
  D4 -->|"Não"| C4
  D4 -->|"Sim"| P3
  P3 --> D5
  D5 -->|"Não"| C5
  D5 -->|"Sim"| C6

  classDef conduta fill:#eef6ef,stroke:#2f7a4f,color:#12301f;
  class C1,C2,C3,C4,C5,C6 conduta;
```

## Ponto de segurança

No recém-nascido, **compressão sem ventilação eficaz é um erro de sequência**. A diretriz AHA/AAP 2025 mantém ventilação como intervenção prioritária e recomenda iniciar compressões somente quando a FC segue <60 bpm apesar de ventilação que efetivamente infla os pulmões.
