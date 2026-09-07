---
title: "Fluxograma: sinalizadores ambulatoriais na TVP — PS agora vs imagem/retorno vs home treatment"
slug: fluxograma-sinalizadores-ambulatoriais-tvp-destino
theme: "Tromboembolismo"
kind: fluxograma
fonte_producao: grok
summary: "Árvore de destino ambulatorial na TVP: gate de TEP/isquemia/sangramento → PS; suspeita sem alarme → Wells/US; TVP confirmada sem alarme → elegibilidade home treatment vs internação — além de #837 (pós-TEP)."
review_status: pendente_revisao
review_note: "Irmão de sinalizadores-ambulatoriais-tvp-quando-escalar-urgencia e tvp-confirmada-no-consultorio-ambulatorial-versus-internacao (07/09/2026). Além de #837; não duplica árvore Wells/D-dímero/US. Fontes: ASH 2018 PMID 30482764; ASH 2020 PMID 33007077; CHEST 2021 PMID 34352278; ESC/ERS 2019 PMID 31504429."
source_refs:
  - "Lim W, Le Gal G, Bates SM, et al. American Society of Hematology 2018 guidelines for management of venous thromboembolism: diagnosis of venous thromboembolism. Blood Adv. 2018;2(22):3226-3256. DOI: 10.1182/bloodadvances.2018024828. PMID: 30482764"
  - "Ortel TL, Neumann I, Ageno W, et al. American Society of Hematology 2020 guidelines for management of venous thromboembolism: treatment of deep vein thrombosis and pulmonary embolism. Blood Adv. 2020;4(19):4693-4738. DOI: 10.1182/bloodadvances.2020001830. PMID: 33007077"
  - "Stevens SM, Woller SC, Kreuziger LB, et al. Antithrombotic Therapy for VTE Disease: Second Update of the CHEST Guideline and Expert Panel Report. Chest. 2021;160(6):e545-e608. DOI: 10.1016/j.chest.2021.07.055. PMID: 34352278"
  - "Konstantinides SV, Meyer G, Becattini C, et al; ESC Scientific Document Group. 2019 ESC Guidelines for the diagnosis and management of acute pulmonary embolism developed in collaboration with the European Respiratory Society (ERS). Eur Heart J. 2020;41(4):543-603. DOI: 10.1093/eurheartj/ehz405. PMID: 31504429"
---

# Fluxograma: sinalizadores ambulatoriais na TVP — destino

Prosa: [`sinalizadores-ambulatoriais-tvp-quando-escalar-urgencia`](sinalizadores-ambulatoriais-tvp-quando-escalar-urgencia.md) · [`tvp-confirmada-no-consultorio-ambulatorial-versus-internacao`](tvp-confirmada-no-consultorio-ambulatorial-versus-internacao.md).

Diagnóstico (Wells/D-dímero/US): [`fluxograma-trombose-venosa-profunda-suspeita-wells-d-dimero-e-ultrassom`](fluxograma-trombose-venosa-profunda-suspeita-wells-d-dimero-e-ultrassom.md). Pós-TEP: [#837](https://github.com/rafaelpaesmeirelles/MeuCardio/pull/837).

## Árvore de decisão

```mermaid
flowchart TD
  R0["Consulta ambulatorial: suspeita de TVP ou TVP conhecida"] --> D1{"TEP associado, instabilidade, isquemia de membro, sangramento maior ou falha crítica de anticoagulação?"}

  D1 -->|"Sim ou dúvida fundamentada"| C1(["Encaminhar AGORA ao PS / urgência. Não observar em casa"])

  D1 -->|"Não"| D2{"TVP já confirmada por imagem?"}

  D2 -->|"Não — só suspeita"| D3{"Wells TVP dois níveis"}

  D3 -->|"Improvável ≤1"| C2(["D-dímero alta sensibilidade. Negativo → exclui; positivo → US. Ver fluxograma Wells/US"])
  D3 -->|"Provável ≥2"| C3(["US direto (não atrasar por D-dímero). Retorno 24–72 h se US pendente"])

  D2 -->|"Sim"| D4{"Elegível a home treatment? estável · baixo risco hemorrágico · acesso ao fármaco · retorno garantido (ASH 2020)"}

  D4 -->|"Não"| C4(["Internar / observar com suporte até rede segura"])
  D4 -->|"Sim"| C5(["Home treatment + orientação escrita. Retorno curto; sem doses neste fluxograma"])

  classDef conduta fill:#eef6ef,stroke:#2f7a4f,color:#12301f;
  classDef alerta fill:#fdecea,stroke:#b3261e,color:#3b0a0a;
  class C1,C4 alerta;
  class C2,C3,C5 conduta;
```

## Notas

- **D1** = gate de segurança (além do pós-TEP do #837).
- **D3** = só aponta o caminho; o detalhe do algoritmo está no fluxograma Wells/US.
- **D4** = elegibilidade ASH 2020 — ver protocolo irmão de TVP confirmada.
- **Não decide** doses, escolha DOAC vs HBPM nem duração após 3–6 meses.
