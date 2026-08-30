---
title: "Fluxograma: GPI na SCA — PURSUIT, PRISM-PLUS, GUSTO-IV e EARLY-ACS"
slug: fluxograma-gpi-pursuit-prism-plus-gusto-iv-early-acs
theme: "Doença coronariana"
kind: fluxograma
summary: "PURSUIT: eptifibatida ganha 1,5 pp de morte/IAM (era antiga). PRISM-PLUS: tirofibana+heparina ganha; isolada parou por morte 4,6% vs 1,1%. GUSTO-IV: abciximabe médico sem revasc precoce NS. EARLY-ACS: eptifibatida ≥12 h antes da angio NS. GPI de laboratório ≠ GPI de enfermaria."
review_status: revisado
fonte_producao: grok
review_note: "Produção científica contínua em 29/08/2026. Árvore ancorada em PURSUIT PMID 9705684, PRISM-PLUS PMID 9599103, GUSTO-IV ACS PMID 11425411, EARLY-ACS PMID 19332455. Revisão científica concluída em 30/08/2026."
source_refs:
  - "PURSUIT Investigators. N Engl J Med. 1998;339(7):436-443. PMID: 9705684."
  - "PRISM-PLUS Investigators. N Engl J Med. 1998;338(21):1488-1497. PMID: 9599103."
  - "Simoons ML. GUSTO IV-ACS. Lancet. 2001;357(9272):1915-1924. PMID: 11425411."
  - "Giugliano RP, et al. EARLY ACS. N Engl J Med. 2009;360(21):2176-2190. PMID: 19332455."
  - "PARAGON Investigators. Circulation. 1998;97(24):2386-2395. PMID: 9641689."
---

# Fluxograma: GPI na SCA

```mermaid
flowchart TD
  R0["Quer GPI (IIb/IIIa) na SCA?"] --> D1{"Onde?"}

  D1 -->|"Enfermaria, sem ida precoce ao cateter<br/>(GUSTO-IV ACS, abciximabe)"| C1(["Não. Morte/IAM 8,0% vs 8,2% vs 9,1%"])

  D1 -->|"Infusão ≥12 h antes da angio<br/>(EARLY-ACS, eptifibatida)"| C2(["Não. Primário 9,3% vs 10,0% P=0,23<br/>Mais sangramento"])

  D1 -->|"Tirofibana sem heparina<br/>(PRISM-PLUS, braço isolado)"| C3(["Não. Parou por morte 7 d<br/>4,6% vs 1,1%"])

  D1 -->|"Era 1998, heparina+AAS, eptifibatida<br/>(PURSUIT)"| C4(["Primário 14,2% vs 15,7% P=0,04<br/>Não é a prática 2026 de rotina"])

  D1 -->|"Lamifibana médico (PARAGON-A)"| C5(["Não. Primário 30 d P=0,668 NS<br/>Não vender o 6.º mês"])

  classDef conduta fill:#eef6ef,stroke:#2f7a4f,color:#12301f;
  class C1,C2,C3,C4,C5 conduta;
```

## Mensagem prática

**GPI médico de rotina não sobreviveu a GUSTO-IV e EARLY-ACS.** PRISM-PLUS proíbe tirofibana isolada. PURSUIT é o ancestral positivo, não o protocolo atual.
