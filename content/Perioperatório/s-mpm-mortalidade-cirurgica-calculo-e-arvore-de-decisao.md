---
title: "S-MPM: mortalidade cirúrgica em 30 dias"
slug: s-mpm-mortalidade-cirurgica-calculo-e-arvore-de-decisao
theme: "Perioperatório"
kind: documento
fonte_producao: chatgpt
review_status: pendente_revisao
summary: "Modelo simples de 9 pontos para mortalidade global em 30 dias, separado dos escores cardíacos."
source_refs:
  - "Glance LG, Lustik SJ, Hannan EL, et al. Ann Surg. 2012;255(4):696-702. PMID: 22418007. DOI: 10.1097/SLA.0b013e31824b45af."
---

# S-MPM

Endpoint: **mortalidade por todas as causas em 30 dias**, não MICA/MACE.

Pontuação: ASA I/II/III/IV/V = 0/2/4/5/6; risco do procedimento baixo/intermediário/alto = 0/1/2; emergência = +1. Total 0–9.

Classes originais: 0–4 = Classe I, mortalidade <0,5%; 5–6 = Classe II, 1,5–4,0%; 7–9 = Classe III, >10%. C-stat de validação: **0,897**.

```mermaid
flowchart TD
 A["Paciente candidato a cirurgia não cardíaca"] --> B["Pontuar ASA"]
 B --> C["Pontuar risco do procedimento"]
 C --> D{"Emergência?"}
 D -->|"Sim"| E["+1"]
 D -->|"Não"| F["+0"]
 E --> G["Total 0–9"]
 F --> G
 G --> H{"0–4 / 5–6 / 7–9"}
 H --> I["Classe I <0,5% / II 1,5–4,0% / III >10%"]
```

```mermaid
flowchart TD
 A["S-MPM calculado"] --> B["Comunicar mortalidade cirúrgica global"]
 B --> C{"Classe II/III?"}
 C -->|"Não"| D["Planejamento habitual"]
 C -->|"Sim"| E["Otimização + decisão compartilhada + nível de cuidado pós-op"]
 D --> F["Avaliar risco cardiovascular separadamente"]
 E --> F
 F --> G["Nunca somar S-MPM com RCRI/MICA/GSCRI"]
```

## Limitação crítica

A classe de risco do procedimento no S-MPM foi empiricamente derivada e não é automaticamente intercambiável com ESC/AHA. Se não puder ser enquadrada com segurança: **VERIFICAÇÃO HUMANA NECESSÁRIA**.