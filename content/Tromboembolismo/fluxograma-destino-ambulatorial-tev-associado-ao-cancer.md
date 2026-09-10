---
slug: fluxograma-destino-ambulatorial-tev-associado-ao-cancer
title: 'Fluxograma: destino ambulatorial no TEV associado ao câncer — PS vs oncologia/hematologia'
kind: fluxograma
theme: Tromboembolismo
summary: 'Árvore de destino no CAT: urgência; avaliação especializada por risco hemorrágico/renal/interações; TEP
  estratificado antes de alta; e rede segura obrigatória em TEV confirmado.'
tags: []
source_refs:
- 'Creager MA et al. AHA/ACC acute PE 2026. DOI: 10.1161/CIR.0000000000001415. Disposição ambulatorial.'
- 'ASH 2021 VTE in cancer. PMID: 33570602'
- 'ASCO cancer VTE 2023. PMID: 37075273'
- 'ITAC 2022. PMID: 35772465'
- 'ESC/ERS 2019 acute PE. PMID: 31504429'
evidence_level: null
source_tier: A
review_status: revisado
gaps: []
published: true
---

# Fluxograma: destino ambulatorial no TEV associado ao câncer

```mermaid
flowchart TD
  R0["Câncer ativo + TEV suspeito ou confirmado"] --> D1{"Instabilidade, TEP sintomático de alarme,<br/>sangramento maior, flegmasia/isquemia<br/>ou falha crítica de anticoagulação?"}
  D1 -->|"Sim/dúvida"| C1(["PS / urgência AGORA"])

  D1 -->|"Não"| D2{"TEV confirmado?"}
  D2 -->|"Não"| C2(["Investigação em tempo oportuno;<br/>definir anticoagulação provisória conforme<br/>probabilidade e risco hemorrágico<br/>Sem via segura ou alarme: urgência"])

  D2 -->|"Sim"| D3{"É TEP confirmado/incidental?"}
  D3 -->|"Sim"| P3["Estratificar PESI/sPESI ou Hestia<br/>+ VD/biomarcadores quando indicados"]
  P3 --> D4{"Baixo risco e elegível a manejo ambulatorial<br/>segundo fluxo canônico?"}
  D4 -->|"Não / risco intermediário-alto"| C3(["Observação/hospitalização conforme risco"])
  D4 -->|"Sim"| D5
  D3 -->|"Não (ex. TVP)"| D5{"Trombocitopenia, alto risco GI/GU,<br/>interação, disfunção renal grave<br/>ou escolha anticoagulante ainda aberta?"}

  D5 -->|"Sim"| C4(["Avaliação especializada imediata para plano seguro<br/>Sem acesso: cuidado supervisionado"])
  C4 --> D6
  D5 -->|"Não"| D6{"Rede segura?<br/>fármaco + retorno + contato + monitorização"}
  D6 -->|"Não"| C5(["Cuidado supervisionado / observação<br/>até plano seguro estar garantido"])
  D6 -->|"Sim"| C6(["Manejo ambulatorial + alarmes escritos"])

  classDef alerta fill:#fdecea,stroke:#b3261e,color:#3b0a0a;
  classDef conduta fill:#eef6ef,stroke:#2f7a4f,color:#12301f;
  class C1,C3,C5 alerta;
  class C2,C4,C6 conduta;
```

## Notas
- TEP e TVP não compartilham automaticamente o mesmo gate de alta.
- Disfunção renal grave precisa de revisão especializada porque altera seleção/segurança de anticoagulantes.
- TEV confirmado sem rede segura não volta ao ramo de “pedir imagem”.
- Sem doses neste fluxo.

No câncer, sPESI já é ≥1 pelo diagnóstico oncológico; isso exige avaliação integrada, não proíbe por si só toda via ambulatorial. Critérios Hestia e avaliação clínica/VD, quando apropriados, podem apoiar seleção de baixo risco. Não misturar categorias AHA/ACC 2026 com estratos ESC como equivalentes automáticos. Suspeita de TEV demanda investigação em tempo oportuno e decisão sobre anticoagulação enquanto se investiga conforme probabilidade/risco hemorrágico; não aguardar consulta eletiva se não houver via diagnóstica segura. TEV confirmado com fatores complexos exige plano imediato, sem deixar o paciente sem tratamento seguro enquanto aguarda especialista.

## Conteúdo CorVIA conectado

- [Sinalizadores no TEV associado ao câncer: PS versus oncologia/hematologia](/biblioteca/sinalizadores-ambulatoriais-tev-associado-ao-cancer-destino-ps-vs-oncologia)
- [TEV associado ao câncer: quando escalar hematologia/oncologia versus urgência](/biblioteca/tev-associado-ao-cancer-quando-escalar-hematologia-oncologia-vs-urgencia)
