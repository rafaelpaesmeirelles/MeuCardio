---
title: "Fluxograma: Trombose de prótese valvar mecânica na gestação"
slug: fluxograma-trombose-de-protese-valvar-mecanica-na-gestacao
theme: "Gravidez"
kind: fluxograma
summary: "Árvore de emergência para gestante com prótese mecânica e suspeita de trombose, diferenciando apresentação subaguda não crítica de trombose aguda obstrutiva com necessidade de intervenção urgente."
review_status: revisado
source_refs: ["De Backer J, Haugaa KH, Hasselberg NE, et al.; ESC Scientific Document Group. 2025 ESC Guidelines for the management of cardiovascular disease and pregnancy. Eur Heart J. 2025;46(43):4462-4568. DOI: 10.1093/eurheartj/ehaf193. PMID: 40878294. Seção 12.5.3.2.2.", "van Hagen IM, Roos-Hesselink JW, Ruys TPE, et al. Pregnancy in Women With a Mechanical Heart Valve: Data of the European Society of Cardiology Registry of Pregnancy and Cardiac Disease (ROPAC). Circulation. 2015;132(2):132-142. DOI: 10.1161/CIRCULATIONAHA.115.015242. PMID: 26100109."]
---

# Trombose de prótese mecânica na gestação

```mermaid
flowchart TD
  R0["Gestante com prótese mecânica + dispneia nova,<br/>IC, síncope, embolia, novo sopro ou clique alterado"]
  P1["ABC + revisar anticoagulação/INR/anti-Xa +<br/>TTE urgente; acionar Pregnancy Heart Team"]
  D1{"TTE confirma ou mantém forte suspeita<br/>de disfunção/trombose protética?"}
  C1(["Não: ampliar diagnóstico diferencial e<br/>seguir investigação conforme risco"])
  P2["Sim: TEE e/ou fluoroscopia/CT conforme necessidade<br/>para mobilidade dos folhetos e gravidade"]
  D2{"Instabilidade, obstrução importante,<br/>regurgitação grave ou deterioração aguda?"}
  P3["Não crítica/subaguda + anticoagulação subterapêutica:<br/>otimizar HNF e restabelecer INR terapêutico com VKA;<br/>monitorização estreita e imagem seriada"]
  D3{"Função protética e quadro clínico melhoram?"}
  C2(["Sim: manter estratégia anticoagulante<br/>especializada e vigilância da prótese"])
  P4["Não / quadro agudo grave: decisão urgente<br/>entre cirurgia e trombólise pelo Pregnancy Heart Team"]
  D4{"Cirurgia imediata disponível e apropriada<br/>ao quadro materno/gestacional?"}
  C3(["Sim: cirurgia urgente; discutir momento do parto<br/>conforme viabilidade fetal e condição materna"])
  C4(["Não / cenário selecionado: trombólise pode ser<br/>considerada por equipe especializada;<br/>dose/regime exige protocolo específico conferido"])
  C5(["Pós-estabilização: reavaliar anticoagulação,<br/>causa da trombose e plano obstétrico"])

  R0 --> P1
  P1 --> D1
  D1 -->|"Não"| C1
  D1 -->|"Sim"| P2
  P2 --> D2
  D2 -->|"Não"| P3
  D2 -->|"Sim"| P4
  P3 --> D3
  D3 -->|"Sim"| C2
  D3 -->|"Não"| P4
  P4 --> D4
  D4 -->|"Sim"| C3
  D4 -->|"Não/indisponível"| C4
  C2 --> C5
  C3 --> C5
  C4 --> C5

  classDef conduta fill:#eef6ef,stroke:#2f7a4f,color:#12301f;
  class C1,C2,C3,C4,C5 conduta;
```

## Segurança

Trombose de prótese mecânica na gestação tem alta mortalidade materna. **Eco urgente e definição rápida de obstrução/instabilidade vêm antes da escolha entre cirurgia e trombólise.**
