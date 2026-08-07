---
title: "Fluxograma: TEP agudo na gestação e no puerpério (ESC 2025)"
slug: fluxograma-tromboembolismo-pulmonar-agudo-na-gestacao-e-puerperio-esc-2025
theme: "Gravidez"
kind: fluxograma
summary: "Árvore de decisão para suspeita de embolia pulmonar na gestação/puerpério, separando paciente estável com YEARS adaptado da paciente instável que exige suporte e decisão multidisciplinar de reperfusão."
review_status: revisado
source_refs: ["De Backer J, Haugaa KH, et al. 2025 ESC Guidelines for the management of cardiovascular disease and pregnancy. Eur Heart J. 2025;46(43):4462-4568. DOI: 10.1093/eurheartj/ehaf193. Seção 11.4 — Management of acute venous thromboembolism."]
---

# TEP agudo na gestação e no puerpério

```mermaid
flowchart TD
  R0["Gestante ou puérpera com suspeita de TEP:<br/>dispneia/dor torácica/síncope/hipoxemia"]
  P0["Se suspeita clínica relevante de TEV:<br/>iniciar HBPM terapêutica imediatamente,<br/>mesmo antes da imagem, até excluir/confirmar"]
  D1{"Instabilidade hemodinâmica?"}
  P1["Estável: aplicar estratégia diagnóstica estruturada;<br/>avaliar sinais de TVP + hemoptise +<br/>TEP como diagnóstico mais provável (YEARS)"]
  D2{"Algum critério YEARS presente?"}
  D3{"D-dímero <500 µg/L?"}
  D4{"D-dímero <1000 µg/L?"}
  C1(["TEP pode ser excluído pelo algoritmo<br/>se demais condições da estratégia forem atendidas;<br/>interromper anticoagulação empírica se diagnóstico excluído"])
  P2["Não excluído: considerar US venosa compressiva<br/>se sinais de TVP e prosseguir para imagem torácica<br/>apropriada, incluindo CTPA quando indicada"]
  D5{"TEP confirmado?"}
  C2(["Não: suspender tratamento empírico<br/>e investigar diagnóstico alternativo"])
  C3(["Sim, estável: manter HBPM terapêutica<br/>ajustada ao peso do início da gestação;<br/>1x/dia ou 2x/dia são aceitáveis"])
  P3["Instável: suporte ABC + TTE à beira do leito<br/>para VD quando apropriado; HNF pode ser usada<br/>na fase inicial da anticoagulação"]
  D6{"TEP de alto risco confirmado ou<br/>fortemente provável com choque?"}
  C4(["Não: completar investigação rapidamente<br/>e tratar conforme diagnóstico"])
  P4["Sim: ativar equipe multidisciplinar especializada;<br/>trombólise/intervenção NÃO são rotina periparto,<br/>mas podem ser consideradas no TEP de alto risco"]
  C5(["Individualizar reperfusão sistêmica, por cateter<br/>ou cirúrgica conforme risco hemorrágico,<br/>momento obstétrico e experiência do centro"])
  C6(["Pós-parto: anticoagulação terapêutica por<br/>≥6 semanas e duração total ≥3 meses,<br/>salvo indicação de tratamento indefinido"])

  R0 --> P0
  P0 --> D1
  D1 -->|"Não"| P1
  D1 -->|"Sim"| P3
  P1 --> D2
  D2 -->|"Sim"| D3
  D2 -->|"Não"| D4
  D3 -->|"Sim"| C1
  D3 -->|"Não"| P2
  D4 -->|"Sim"| C1
  D4 -->|"Não"| P2
  P2 --> D5
  D5 -->|"Não"| C2
  D5 -->|"Sim"| C3
  P3 --> D6
  D6 -->|"Não"| C4
  D6 -->|"Sim"| P4
  P4 --> C5
  C3 --> C6
  C5 --> C6

  classDef conduta fill:#eef6ef,stroke:#2f7a4f,color:#12301f;
  class C1,C2,C3,C4,C5,C6 conduta;
```

## Notas de segurança

O D-dímero não é interpretado isoladamente; os cortes de 500 e 1000 µg/L pertencem ao algoritmo YEARS adaptado descrito pela ESC 2025. Na instabilidade, não atrasar suporte e decisão de reperfusão aguardando uma sequência diagnóstica desenhada para pacientes estáveis.
