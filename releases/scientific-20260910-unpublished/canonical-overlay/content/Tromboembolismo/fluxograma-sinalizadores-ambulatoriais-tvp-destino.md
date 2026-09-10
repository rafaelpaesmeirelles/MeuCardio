---
slug: fluxograma-sinalizadores-ambulatoriais-tvp-destino
title: 'Fluxograma: sinalizadores ambulatoriais na TVP — PS agora vs imagem/retorno vs home treatment'
kind: fluxograma
theme: Tromboembolismo
summary: 'Destino na TVP: urgência diante de TEP, ameaça de membro ou sangramento importante; diagnóstico com imagem
  oportuna e decisão entre tratamento domiciliar, hospitalar ou vigilância da TVP distal selecionada.'
tags: []
source_refs:
- 'NICE NG158. Venous thromboembolic diseases: diagnosis, management and thrombophilia testing. Updated 2023. https://www.nice.org.uk/guidance/ng158/chapter/recommendations'
- 'Lim W, Le Gal G, Bates SM, et al. American Society of Hematology 2018 guidelines for management of venous thromboembolism:
  diagnosis of venous thromboembolism. Blood Adv. 2018;2(22):3226-3256. DOI: 10.1182/bloodadvances.2018024828. PMID:
  30482764'
- 'Ortel TL, Neumann I, Ageno W, et al. American Society of Hematology 2020 guidelines for management of venous
  thromboembolism: treatment of deep vein thrombosis and pulmonary embolism. Blood Adv. 2020;4(19):4693-4738. DOI:
  10.1182/bloodadvances.2020001830. PMID: 33007077'
- 'Stevens SM, Woller SC, Kreuziger LB, et al. Antithrombotic Therapy for VTE Disease: Second Update of the CHEST
  Guideline and Expert Panel Report. Chest. 2021;160(6):e545-e608. DOI: 10.1016/j.chest.2021.07.055. PMID: 34352278'
- 'Konstantinides SV, Meyer G, Becattini C, et al; ESC Scientific Document Group. 2019 ESC Guidelines for the diagnosis
  and management of acute pulmonary embolism developed in collaboration with the European Respiratory Society (ERS).
  Eur Heart J. 2020;41(4):543-603. DOI: 10.1093/eurheartj/ehz405. PMID: 31504429'
evidence_level: null
source_tier: A
review_status: revisado
gaps: []
published: false
---

# Fluxograma: sinalizadores ambulatoriais na TVP — destino

Prosa: [`sinalizadores-ambulatoriais-tvp-quando-escalar-urgencia`](/biblioteca/sinalizadores-ambulatoriais-tvp-quando-escalar-urgencia) · [`tvp-confirmada-no-consultorio-ambulatorial-versus-internacao`](/biblioteca/tvp-confirmada-no-consultorio-ambulatorial-versus-internacao).

Diagnóstico (Wells/D-dímero/US): [`fluxograma-trombose-venosa-profunda-suspeita-wells-d-dimero-e-ultrassom`](/biblioteca/fluxograma-trombose-venosa-profunda-suspeita-wells-d-dimero-e-ultrassom). Pós-TEP: [Sinalizadores após TEP](/biblioteca/sinalizadores-ambulatoriais-pos-tep-quando-reencaminhar-urgencia).

## Árvore de decisão

```mermaid
flowchart TD
  R0["Consulta ambulatorial: suspeita de TVP ou TVP conhecida"] --> D1{"TEP associado, instabilidade, isquemia de membro, sangramento maior ou falha crítica de anticoagulação?"}

  D1 -->|"Sim ou dúvida fundamentada"| C1(["Encaminhar AGORA ao PS / urgência. Não observar em casa"])

  D1 -->|"Não"| D2{"Imagem confirma episódio ATUAL de TVP?"}

  D2 -->|"Não — só suspeita"| DP{"Primeiro episódio de membro inferior<br/>não gestante?"}
  DP -->|"Não: recorrência/gestação/membro superior"| CP["Via diagnóstica específica<br/>Não excluir por Wells/D-dímero genérico"]
  DP -->|"Sim"| D3{"Wells TVP dois níveis"}

  D3 -->|"Improvável ≤1"| C2(["D-dímero de alta sensibilidade rápido.<br/>Negativo → exclui; positivo → US.<br/>Atraso → via NG158 e anticoagulação interina se segura"])
  D3 -->|"Provável ≥2"| C3(["US rápido; se indisponível, avaliação de anticoagulação interina segura e imagem em até 24 h conforme NG158; urgência se rede insuficiente"])

  D2 -->|"Sim"| DD{"Distal isolada sem sintomas graves<br/>nem risco de extensão?"}
  DD -->|"Sim"| CD["Considerar US seriado por duas semanas<br/>Protocolo distal; tratar se indicação/extensão"]
  DD -->|"Não: proximal ou distal com indicação"| D4{"Elegível a home treatment? estável · baixo risco hemorrágico · acesso ao fármaco · retorno garantido (ASH 2020)"}

  D4 -->|"Não"| C4(["Internar / observar com suporte até rede segura"])
  D4 -->|"Sim"| C5(["Home treatment + orientação escrita. Retorno curto; sem doses neste fluxograma"])

  classDef conduta fill:#eef6ef,stroke:#2f7a4f,color:#12301f;
  classDef alerta fill:#fdecea,stroke:#b3261e,color:#3b0a0a;
  class C1,C4 alerta;
  class C2,C3,C5 conduta;
```

## Notas

- **D1** = gate de segurança.
- **D3** = só aponta o caminho; o detalhe do algoritmo está no fluxograma Wells/US.
- **D4** = elegibilidade ASH 2020 — ver protocolo irmão de TVP confirmada.
- **Não decide** doses, escolha DOAC vs HBPM nem duração após 3–6 meses.

## Condições para plano domiciliar

Confirmar episódio atual e localização. Distal isolada de baixo risco pode seguir US seriado em vez de anticoagulação; proximal e distal com indicação precisam tratamento oportuno, sem aguardar consulta vascular. Avaliar dor, comorbidades, rim/fígado, gestação, câncer, risco hemorrágico, acesso ao fármaco, adesão e suporte. Phlegmasia, ameaça de membro ou TEP exigem urgência. Sangramento segue [classificação maior/CRNM/nuisance](/biblioteca/sinalizadores-ambulatoriais-doac-sangramento-quando-encaminhar).
