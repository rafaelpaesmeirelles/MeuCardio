---
title: "Fluxograma: TEP agudo na gestação e no puerpério (ESC 2025)"
slug: fluxograma-tromboembolismo-pulmonar-agudo-na-gestacao-e-puerperio-esc-2025
theme: "Gravidez"
kind: fluxograma
summary: "Árvore de decisão para suspeita de embolia pulmonar: usa YEARS adaptado somente na gestante estável, remete o puerpério à estratégia diagnóstica padrão e separa a instabilidade que exige suporte e decisão multidisciplinar de reperfusão."
review_status: revisado
review_note: "Revisão de 26/08/2026 contra o texto integral da ESC 2025, seções 11.4–11.5, e o algoritmo YEARS original. Corrigida mistura de população: os limiares 500/1000 µg/L do YEARS adaptado ficam restritos à gestante hemodinamicamente estável; no puerpério, o fluxo remete à estratégia diagnóstica padrão e não inventa corte de D-dímero. Acrescentados os limites para anti-Xa rotineiro, filtro de veia cava e planejamento do parto sob dose terapêutica."
source_refs: ["De Backer J, Haugaa KH, Hasselberg NE, et al. 2025 ESC Guidelines for the management of cardiovascular disease and pregnancy. Eur Heart J. 2025;46(43):4462-4568. DOI: 10.1093/eurheartj/ehaf193. PMID: 40878294. Seções 11.4–11.5.", "van der Pol LM, Tromeur C, Bistervels IM, et al. Pregnancy-Adapted YEARS Algorithm for Diagnosis of Suspected Pulmonary Embolism. N Engl J Med. 2019;380(12):1139-1149. DOI: 10.1056/NEJMoa1813865. PMID: 30893534."]
---

# TEP agudo na gestação e no puerpério

```mermaid
flowchart TD
  R0["Gestante ou puérpera com suspeita de TEP:<br/>dispneia/dor torácica/síncope/hipoxemia"]
  P0["Esclarecimento diagnóstico imediato;<br/>na gestante, iniciar HBPM terapêutica antes da imagem<br/>e manter até excluir ou confirmar TEV"]
  D1{"Instabilidade hemodinâmica?"}
  D0{"Gestação em curso<br/>ou puerpério?"}
  P1["Estável: aplicar estratégia diagnóstica estruturada;<br/>avaliar sinais de TVP + hemoptise +<br/>TEP como diagnóstico mais provável (YEARS)"]
  P5["Puerpério estável: usar estratégia diagnóstica<br/>padrão de TEP; não aplicar automaticamente<br/>os cortes do YEARS adaptado à gestação"]
  D2{"Algum critério YEARS presente?"}
  D3{"D-dímero <500 µg/L?"}
  D4{"D-dímero <1000 µg/L?"}
  C1(["TEP pode ser excluído pelo algoritmo<br/>se demais condições da estratégia forem atendidas;<br/>interromper anticoagulação empírica se diagnóstico excluído"])
  P2["Não excluído: considerar US venosa compressiva<br/>se sinais de TVP e prosseguir para imagem torácica<br/>apropriada, incluindo CTPA quando indicada"]
  D5{"TEP confirmado?"}
  D7{"Gestação em curso<br/>ou puerpério?"}
  C2(["Não: suspender tratamento empírico<br/>e investigar diagnóstico alternativo"])
  C3(["Sim, estável: manter HBPM terapêutica<br/>ajustada ao peso do início da gestação;<br/>1x/dia ou 2x/dia são aceitáveis"])
  C7(["Puerpério: anticoagulação terapêutica;<br/>HBPM ou AVK são compatíveis com lactação;<br/>considerar hemorragia e anestesia neuraxial recentes"])
  P3["Instável: suporte ABC + TTE à beira do leito<br/>para VD quando apropriado; HNF pode ser usada<br/>na fase inicial da anticoagulação"]
  D6{"TEP de alto risco confirmado ou<br/>fortemente provável com choque?"}
  C4(["Não: completar investigação rapidamente<br/>e tratar conforme diagnóstico"])
  P4["Sim: ativar equipe multidisciplinar especializada;<br/>trombólise/intervenção NÃO são rotina periparto,<br/>mas podem ser consideradas no TEP de alto risco"]
  C5(["Individualizar reperfusão sistêmica, por cateter<br/>ou cirúrgica conforme risco hemorrágico,<br/>momento obstétrico e experiência do centro"])
  C6(["Pós-parto: anticoagulação terapêutica por<br/>≥6 semanas e duração total ≥3 meses,<br/>salvo indicação de tratamento indefinido"])

  R0 --> P0
  P0 --> D1
  D1 -->|"Não"| D0
  D1 -->|"Sim"| P3
  D0 -->|"Gestação"| P1
  D0 -->|"Puerpério"| P5
  P1 --> D2
  D2 -->|"Sim"| D3
  D2 -->|"Não"| D4
  D3 -->|"Sim"| C1
  D3 -->|"Não"| P2
  D4 -->|"Sim"| C1
  D4 -->|"Não"| P2
  P5 --> P2
  P2 --> D5
  D5 -->|"Não"| C2
  D5 -->|"Sim"| D7
  D7 -->|"Gestação"| C3
  D7 -->|"Puerpério"| C7
  P3 --> D6
  D6 -->|"Não"| C4
  D6 -->|"Sim"| P4
  P4 --> C5
  C3 --> C6
  C7 --> C6
  C5 --> C6

  classDef conduta fill:#eef6ef,stroke:#2f7a4f,color:#12301f;
  class C1,C2,C3,C4,C5,C6 conduta;
```

## Notas de segurança

O D-dímero não é interpretado isoladamente. Os cortes de 500 e 1000 µg/L
pertencem ao algoritmo YEARS adaptado à **gestação** descrito pela ESC 2025;
eles não devem ser transportados automaticamente ao puerpério. Na instabilidade,
não atrasar suporte e decisão de reperfusão aguardando uma sequência diagnóstica
desenhada para pacientes estáveis.

Na gestante com TEV confirmado, HBPM terapêutica é ajustada pelo peso do início
da gestação, em uma ou duas administrações diárias. Monitorização rotineira de
anti-Xa não melhora desfecho e só deve ser considerada em insuficiência renal ou
obesidade. Na instabilidade por TEP, HNF pode ser usada na fase inicial.

Trombólise ou intervenção não é rotina no periparto; só deve ser considerada no
TEP de alto risco após avaliação multidisciplinar especializada. Filtro de veia
cava fica restrito a TEV recorrente apesar de anticoagulação apropriada ou
contraindicação à dose terapêutica. Quem recebe anticoagulação terapêutica na
gestação precisa de parto planejado com interrupção prévia da HBPM, evitando
trabalho de parto espontâneo sob anticoagulação plena.

## Tudo com Tudo

- [YEARS adaptado e CT-PE Pregnancy](diagnostico-de-tep-na-gestante-years-adaptado-e-a-estrategia-do-ct-pe-pregnancy.md)
- [TEP na gestação e puerpério — revisão clínica](tromboembolismo-pulmonar-agudo-na-gestacao-e-puerperio-esc-2025.md)
- [Diagnóstico de TEP no adulto — ESC 2019](../Tromboembolismo/fluxograma-tromboembolismo-pulmonar-diagnostico-esc-2019.md)
- [Anticoagulantes na gestação e lactação](../Tromboembolismo/anticoagulantes-na-gestacao-e-lactacao-o-que-diz-a-bula-registrada.md)
- [Terapia dirigida por cateter no TEP](../Tromboembolismo/terapia-dirigida-por-cateter-no-tep-peerless-e-o-que-ainda-nao-esta-respondido.md)
- [Filtro de veia cava no TEP agudo — PREPIC2](../Tromboembolismo/filtro-de-veia-cava-inferior-recuperavel-no-tep-agudo-o-ensaio-prepic2.md)
