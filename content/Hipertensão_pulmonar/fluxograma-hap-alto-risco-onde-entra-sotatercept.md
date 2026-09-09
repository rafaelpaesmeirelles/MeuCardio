---
title: 'Fluxograma: HAP de alto risco — onde entra o sotatercept'
slug: fluxograma-hap-alto-risco-onde-entra-sotatercept
theme: Hipertensão pulmonar
kind: fluxograma
review_status: revisado
source_refs:
- Humbert M, et al. Sotatercept in Patients with Pulmonary Arterial Hypertension at High Risk for Death. N Engl J Med. 2025;392:1987-2000.
  PMID 40167274. NCT04896008.
- Hoeper MM, et al. Phase 3 Trial of Sotatercept for Treatment of Pulmonary Arterial Hypertension. N Engl J Med. 2023. PMID
  36877098. NCT04576988.
- Anvisa. Winrevair novo registro. https://www.gov.br/anvisa/pt-br/assuntos/medicamentos/novos-medicamentos-e-indicacoes/winrevair-sotatercepte-novo-registro
- 'Anvisa. Winrevair (sotatercepte): novo registro, DOU 16/12/2024. https://www.gov.br/anvisa/pt-br/assuntos/medicamentos/novos-medicamentos-e-indicacoes/winrevair-sotatercepte-novo-registro'
review_note: Critério REVEALLite2≥9/CFIII–IV conferido no ZENITH. Emergência agora triada antes da otimização ambulatorial;
  corrigido ramo que atribuía doença esquerda a todos grupos e adicionada segurança Anvisa. Conexões temáticas selecionadas
  e links por slugs da fila conferidos. Conferência final de aplicabilidade e segurança preservada antes das conexões TCT.
summary: 'ZENITH (n=172, interrompido precocemente): composto morte / transplante / hospitalização ≥24 h por HAP 17,4% vs
  54,7%; HR 0,24 (0,13–0,43). STELLAR é outro ensaio (6MWD +40,8 m). Grupo 2 fora. O recorte ZENITH exigia CF III–IV e REVEAL
  Lite2 ≥9; isso não equivale a qualquer definição genérica de alto risco.'
tags: []
source_tier: A
gaps: []
published: true
---

# Fluxograma: HAP de alto risco — onde entra o sotatercept

ZENITH (n=172, interrompido precocemente): composto morte / transplante / hospitalização ≥24 h por HAP **17,4% vs 54,7%**; HR **0,24** (0,13–0,43). STELLAR é outro ensaio (6MWD +40,8 m). Grupo 2 fora. O recorte ZENITH exigia CF III–IV e REVEAL Lite2 ≥9; isso não equivale a qualquer definição genérica de alto risco.

## Árvore de decisão

```mermaid
flowchart TD
  X0["Paciente com hipertensão pulmonar"]
  D0{"É HAP grupo 1 confirmada — não é grupo 2 da cardiopatia esquerda?"}
  C0(["Definir etiologia e tratar conforme o grupo de HP; não aplicar sotatercept pelo ZENITH"])
  D1{"Terapia de fundo da HAP na dose máxima tolerada?"}
  C1(["Otimizar antagonista de endotelina, I-5PDE, selexipague ou prostaciclina conforme o centro — STELLAR e ZENITH foram add-on"])
  D2{"CF III–IV e REVEAL Lite2 ≥9 — recorte ZENITH?"}
  C2(["STELLAR: capacidade de exercício em FC II–III típica. +40,8 m na 6MWD. Não é o composto de morte"])
  C3(["ZENITH: sotatercept vs placebo em alto risco. Composto 15/86 vs 47/86; HR 0,24. Avaliar sangramento, hemoglobina e plaquetas; manter tratamento de base"])
  C4(["Instabilidade / choque: UTI e centro de HAP — fora do recorte ambulatorial do ensaio"])

  X0 --> U0{"Instabilidade ou choque?"}
  U0 -->|"Sim"| C4
  U0 -->|"Não"| D0
  D0 -->|"Não — grupo 2 ou outro"| C0
  D0 -->|"Sim — grupo 1"| D1
  D1 -->|"Não"| C1
  D1 -->|"Sim"| D2
  D2 -->|"FC II–III estável — pergunta de metros"| C2
  D2 -->|"Alto risco — pergunta de morte/hosp/tx"| C3

  classDef conduta fill:#eef6ef,stroke:#2f7a4f,color:#12301f
  class C0,C1,C2,C3,C4 conduta
```

## Aplicação e segurança

Sotatercepte é terapia adicional da HAP em acompanhamento especializado; a Anvisa aprovou Winrevair em dezembro de 2024. Sua avaliação não deve atrasar escalonamento urgente indicado, inclusive prostaciclina parenteral em pacientes de alto risco. Não associar riociguate a inibidor de PDE5.

## Tudo com Tudo

- [ZENITH: sotatercept na HAP de alto risco de morte](/biblioteca/sotatercept-zenith-hap-alto-risco-de-morte)
- [STELLAR: sotatercept e capacidade de exercício na HAP](/biblioteca/stellar-sotatercept-capacidade-de-exercicio-na-hap)
- [BREATHE-5: bosentana na Eisenmenger não é ZENITH](/biblioteca/breathe-5-bosentana-na-eisenmenger-nao-e-zenith)
- [Depois da HAP, quais temas acendem](/biblioteca/depois-da-hap-quais-temas-acendem)
