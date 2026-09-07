---
title: "Fluxograma: sinais de alarme ambulatoriais na hipertensão — PS agora vs. retorno em dias"
slug: fluxograma-sinais-de-alarme-ambulatoriais-hipertensao
theme: "Hipertensão"
kind: fluxograma
fonte_producao: grok
summary: "Árvore ambulatorial: triagem de lesão aguda, encaminhamento imediato, PA ≥180/110 sem lesão aguda (oral + retorno ≤7 dias) e papel do MAPA/MRPA."
review_status: pendente_revisao
review_note: "Irmão do protocolo sinais-de-alarme-ambulatoriais-na-hipertensao-quando-encaminhar (07/09/2026). ESC 2024 PMID 39210715; SBC 2025 PMID 41294179; ESC Council PMID 30165588; ESH 2023 PMID 37345492."
source_refs:
  - "McEvoy JW, McCarthy CP, Bruno RM, et al. 2024 ESC Guidelines for the management of elevated blood pressure and hypertension. Eur Heart J. 2024;45(38):3912-4018. DOI: 10.1093/eurheartj/ehae178. PMID: 39210715"
  - "Brandão AA, Rodrigues CIS, Bortolotto LA, et al. Diretriz Brasileira de Hipertensão Arterial – 2025. Arq Bras Cardiol. 2025;122(9):e20250624. DOI: 10.36660/abc.20250624. PMID: 41294179"
  - "van den Born BJM, Lip GYH, Brguljan-Hitij J, et al. ESC Council on hypertension position document on the management of hypertensive emergencies. Eur Heart J Cardiovasc Pharmacother. 2019;5(1):37-46. DOI: 10.1093/ehjcvp/pvy032. PMID: 30165588"
  - "Jones DW, Ferdinand KC, Taler SJ, et al. 2025 AHA/ACC Multisociety Guideline for High Blood Pressure in Adults. J Am Coll Cardiol. 2025;86(18):1567-1678. DOI: 10.1016/j.jacc.2025.05.007. PMID: 40815242"
  - "Mancia G, Kreutz R, Brunström M, et al. 2023 ESH Guidelines for the management of arterial hypertension. J Hypertens. 2023;41(12):1874-2071. DOI: 10.1097/HJH.0000000000003480. PMID: 37345492"
---

# Fluxograma: sinais de alarme ambulatoriais na hipertensão

Prosa: [`sinais-de-alarme-ambulatoriais-na-hipertensao-quando-encaminhar`](sinais-de-alarme-ambulatoriais-na-hipertensao-quando-encaminhar.md). Emergência com lesão aguda: [`fluxograma-emergencia-hipertensiva`](fluxograma-emergencia-hipertensiva.md).

## Árvore de decisão

```mermaid
flowchart TD
  R0["Consulta ambulatorial com PA elevada<br/>ou hipertensão em seguimento"] --> D1{"Há sinal/sintoma de lesão aguda<br/>de órgão-alvo?"}

  D1 -->|"Sim ou dúvida fundamentada"| C1(["Encaminhar AGORA ao PS / emergência<br/>Não baixar PA agressivamente no consultório<br/>Seguir fluxograma-emergencia-hipertensiva"])

  D1 -->|"Não"| D2{"PA de consultório ≥180/110 mmHg?"}

  D2 -->|"Sim"| P1["Confirmar técnica e causas transitórias<br/>(dor, ansiedade, estimulantes, má adesão)"]
  P1 --> C2(["Iniciar/intensificar anti-hipertensivo ORAL<br/>Retorno ambulatorial em até 7 dias (SBC 2025)<br/>Orientação escrita dos sinais de alarme"])

  D2 -->|"Não"| D3{"A decisão terapêutica muda com<br/>medida fora do consultório?"}

  D3 -->|"Sim"| C3(["Solicitar MAPA e/ou MRPA<br/>Ver fluxograma-jaleco-branco-e-mascarada-mapa-mrpa"])
  D3 -->|"Não"| C4(["Ajustar plano conforme meta vigente<br/>Definir retorno usual<br/>Reforçar sinais de alarme e adesão"])

  C2 --> D4{"Acesso a medicação e retorno garantidos?"}
  D4 -->|"Não / fragilidade / PA persiste muito elevada"| C5(["Antecipar retorno 24–72 h ou observar<br/>com suporte; PS se surgirem alarmes"])
  D4 -->|"Sim"| C6(["Manter plano oral + retorno ≤7 dias<br/>MRPA domiciliar se disponível"])

  classDef conduta fill:#eef6ef,stroke:#2f7a4f,color:#12301f;
  classDef alerta fill:#fdecea,stroke:#b3261e,color:#3b0a0a;
  class C1,C5 alerta;
  class C2,C3,C4,C6 conduta;
```

## Notas

- **D1** = gate de segurança (ESC 2024 / SBC 2025).
- **D2** = limiar operacional ≥180/110 mmHg.
- **D3** = fenótipo (jaleco branco/mascarada) só após excluir emergência.
- Não decide metas IV por síndrome-alvo nem quarta droga na resistente.
