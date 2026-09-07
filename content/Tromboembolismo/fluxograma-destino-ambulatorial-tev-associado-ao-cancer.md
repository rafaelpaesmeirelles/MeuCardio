---
title: "Fluxograma: destino ambulatorial no TEV associado ao câncer — PS vs oncologia/hematologia"
slug: fluxograma-destino-ambulatorial-tev-associado-ao-cancer
theme: "Tromboembolismo"
kind: fluxograma
fonte_producao: grok
summary: "Árvore de destino ambulatorial no CAT: gate TEP/instabilidade/sangramento/isquemia → PS; estável → oncologia/hematologia (plaquetas, mucosa, interação, escolha) vs retorno curto — além de #837 e #871."
review_status: pendente_revisao
review_note: "Irmão de sinalizadores-ambulatoriais-tev-associado-ao-cancer-destino-ps-vs-oncologia e tev-associado-ao-cancer-quando-escalar-hematologia-oncologia-vs-urgencia (07/09/2026). Além de #837/#871; não duplica Caravaggio/Hokusai/AVERT. Fontes: ASH 2021 PMID 33570602; ASCO 2023 PMID 37075273; ITAC 2022 PMID 35772465; ESC/ERS 2019 PMID 31504429; ASH 2020 PMID 33007077."
source_refs:
  - "Lyman GH, Carrier M, Ay C, et al. American Society of Hematology 2021 guidelines for management of venous thromboembolism: prevention and treatment in patients with cancer. Blood Adv. 2021;5(4):927-974. DOI: 10.1182/bloodadvances.2020003442. PMID: 33570602"
  - "Key NS, Khorana AA, Kuderer NM, et al. Venous Thromboembolism Prophylaxis and Treatment in Patients With Cancer: ASCO Guideline Update. J Clin Oncol. 2023;41(16):3063-3071. DOI: 10.1200/JCO.23.00294. PMID: 37075273"
  - "Farge D, Frere C, Connors JM, et al. 2022 international clinical practice guidelines for the treatment and prophylaxis of venous thromboembolism in patients with cancer, including patients with COVID-19. Lancet Oncol. 2022;23(7):e334-e347. DOI: 10.1016/S1470-2045(22)00160-7. PMID: 35772465"
  - "Konstantinides SV, Meyer G, Becattini C, et al; ESC Scientific Document Group. 2019 ESC Guidelines for the diagnosis and management of acute pulmonary embolism developed in collaboration with the European Respiratory Society (ERS). Eur Heart J. 2020;41(4):543-603. DOI: 10.1093/eurheartj/ehz405. PMID: 31504429"
  - "Ortel TL, Neumann I, Ageno W, et al. American Society of Hematology 2020 guidelines for management of venous thromboembolism: treatment of deep vein thrombosis and pulmonary embolism. Blood Adv. 2020;4(19):4693-4738. DOI: 10.1182/bloodadvances.2020001830. PMID: 33007077"
---

# Fluxograma: destino ambulatorial no TEV associado ao câncer

Prosa: [`sinalizadores-ambulatoriais-tev-associado-ao-cancer-destino-ps-vs-oncologia`](sinalizadores-ambulatoriais-tev-associado-ao-cancer-destino-ps-vs-oncologia.md) · [`tev-associado-ao-cancer-quando-escalar-hematologia-oncologia-vs-urgencia`](tev-associado-ao-cancer-quando-escalar-hematologia-oncologia-vs-urgencia.md).

Além de [#837](https://github.com/rafaelpaesmeirelles/MeuCardio/pull/837) (pós-TEP) e [#871](https://github.com/rafaelpaesmeirelles/MeuCardio/pull/871) (TVP genérica). Escolha DOAC vs HBPM: [`fluxograma-doac-versus-dalteparina-no-tev-do-cancer`](fluxograma-doac-versus-dalteparina-no-tev-do-cancer.md).

## Árvore de decisão

```mermaid
flowchart TD
  R0["Consulta ambulatorial: câncer ativo + suspeita ou TEV conhecido"] --> D1{"TEP/instabilidade, isquemia de membro, sangramento maior ou falha crítica de anticoagulação?"}

  D1 -->|"Sim ou dúvida fundamentada"| C1(["Encaminhar AGORA ao PS / urgência. Não observar em casa"])

  D1 -->|"Não"| D2{"Trombocitopenia relevante, câncer GI/GU de alto risco mucoso, interação forte com terapia, ou escolha DOAC vs HBPM ainda aberta?"}

  D2 -->|"Sim"| C2(["Articular hematologia/oncologia (retorno 24–72 h). Sem doses neste fluxograma. Ver braço specialty"])

  D2 -->|"Não"| D3{"TEV já confirmado e rede segura (fármaco + retorno + contato oncológico)?"}

  D3 -->|"Não — só suspeita"| C3(["Imagem no fluxo (US/angio conforme cenário). Retorno curto; PS se surgir alarme"])
  D3 -->|"Sim"| C4(["Plano ambulatorial + orientação escrita. Retorno ≤7 dias; reforçar sinais de alarme"])

  classDef conduta fill:#eef6ef,stroke:#2f7a4f,color:#12301f;
  classDef alerta fill:#fdecea,stroke:#b3261e,color:#3b0a0a;
  class C1 alerta;
  class C2,C3,C4 conduta;
```

## Notas

- **D1** = gate de segurança (além de #837/#871, com pivô câncer).
- **D2** = gatilho specialty — não substitui a monografia de escolha do anticoagulante.
- **D3** = rede segura obrigatória antes de liberar CAT confirmado.
- **Não decide** doses, limiar plaquetário numérico nem duração após 3–6 meses.
