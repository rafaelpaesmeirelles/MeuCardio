---
title: "Fluxograma: IECA após IAM e na DAC estável — SAVE, AIRE, TRACE, EUROPA, PEACE, HOPE"
slug: fluxograma-ieca-pos-iam-e-na-dac-estavel-save-aire-trace-europa-peace
theme: "Doença coronariana"
kind: fluxograma
summary: "Pós-IAM com FE baixa ou IC clínica: IECA reduz morte (SAVE/AIRE/TRACE). DAC estável sem IC: EUROPA positivo, PEACE neutro (FE preservada, terapia mais contemporânea). HOPE é alto risco sem IC. Não usar PEACE para negar IECA na FE reduzida."
review_status: revisado
fonte_producao: grok
review_note: "Produção científica contínua em 29/08/2026. Árvore ancorada em SAVE (PMID 1386652), AIRE (PMID 8104270), TRACE (PMID 7477219), EUROPA (PMID 13678872), PEACE (PMID 15531767) e HOPE da casa (PMID 10639539). Revisão científica concluída em 30/08/2026."
source_refs:
  - "Pfeffer MA, et al. SAVE. N Engl J Med. 1992;327(10):669-677. PMID: 1386652."
  - "AIRE Investigators. Lancet. 1993;342(8875):821-828. PMID: 8104270."
  - "Køber L, et al. TRACE. N Engl J Med. 1995;333(25):1670-1676. PMID: 7477219."
  - "Fox KM. EUROPA. Lancet. 2003;362(9386):782-788. PMID: 13678872."
  - "Braunwald E, et al. PEACE. N Engl J Med. 2004;351(20):2058-2068. PMID: 15531767."
---

# Fluxograma: IECA após IAM e na DAC estável

```mermaid
flowchart TD
  R0["Alguém perguntou se liga IECA"] --> D1{"Quando e qual o VE?"}

  D1 -->|"IAM recente + FE ≤40%<br/>mesmo sem IC"| C1(["SAVE: morte 20% vs 25%; P=0,019"])

  D1 -->|"IAM recente + IC clínica<br/>(mesmo transitória)"| C2(["AIRE: morte 17% vs 23%; P=0,002"])

  D1 -->|"IAM recente + FE ≤35% ao eco"| C3(["TRACE: morte 34,7% vs 42,3%; RR 0,78.<br/>Reinfarto NS"])

  D1 -->|"DAC estável, sem IC aparente"| D2{"FE preservada, já revascularizado,<br/>estatina ligada (perfil PEACE)?"}

  D2 -->|"Não — DAC estável clássica"| C4(["EUROPA: perindopril 8 mg,<br/>composto 8% vs 10%; P=0,0003"])

  D2 -->|"Sim"| C5(["PEACE: trandolapril HR 0,96; P=0,43.<br/>Não negar IECA se FE cair ou houver IC"])

  D1 -->|"Alto risco sem IC nem FE baixa"| C6(["HOPE: ramipril — documento da casa"])

  classDef conduta fill:#eef6ef,stroke:#2f7a4f,color:#12301f;
  class C1,C2,C3,C4,C5,C6 conduta;
```

## Mensagem prática

**FE baixa ou IC pós-IAM: IECA salva vida.** Na DAC estável com FE normal já 'pronta', o PEACE empata — não o use para desligar o pilar de quem tem disfunção.
