---
title: "Fluxograma: ICP primária vs lise — PAMI-1 / Zwolle / GUSTO-IIb (mesmo hospital) ≠ PRAGUE-1 / AIR-PAMI / DANAMI-2 / PRAGUE-2 (transporte)"
slug: fluxograma-icp-primaria-versus-lise-pami-prague-air
theme: "Doença coronariana"
kind: fluxograma
summary: "PAMI-1: morte P=0,06; composto hospitalar sim. GUSTO-IIb: composto 30 d sim; morte e 6 meses NS. AIR-PAMI: MACE P=0,331, n=138. PRAGUE-1: composto 3 braços. PRAGUE-2: morte ITT P=0,12."
review_status: revisado
fonte_producao: grok
review_note: "Produção científica contínua em 29/08/2026. Árvore ancorada em PAMI-1 PMID 8433725, Zwolle PMID 8433726, GUSTO-IIb PMID 9173270, PRAGUE-1 PMID 10781354, AIR-PAMI PMID 12039480. Revisão científica concluída em 30/08/2026."
source_refs:
  - "Grines CL, et al. PAMI. N Engl J Med. 1993;328(10):673-679. PMID: 8433725."
  - "Zijlstra F, et al. N Engl J Med. 1993;328(10):680-684. PMID: 8433726."
  - "GUSTO IIb Angioplasty Substudy Investigators. N Engl J Med. 1997;336(23):1621-1628. PMID: 9173270."
  - "Widimský P, et al. PRAGUE. Eur Heart J. 2000;21(10):823-831. PMID: 10781354."
  - "Grines CL, et al. Air PAMI. J Am Coll Cardiol. 2002;39(11):1713-1719. PMID: 12039480."
  - "Documento da casa prague-2-transporte-para-icp-primaria-versus-lise-no-hospital."
  - "Documento da casa danami-2-transferencia-para-icp-versus-fibrinolise."
  - "Documento da casa captim-angioplastia-primaria-versus-fibrinolise-pre-hospitalar — lise na rua, primário NS."
  - "Documento da casa c-port-icp-primaria-em-hospital-sem-cirurgia-versus-tpa — composto sim, morte NS."
  - "Documento da casa fluxograma-lise-pre-hospitalar-captim-west-cport-stat."
---

# Fluxograma: ICP primária contra lise

```mermaid
flowchart TD
  R0["ICP primária ou lise?"] --> D1{"Onde está o paciente?"}

  D1 -->|"Já no hospital com sala"| C1(["PAMI-1: morte P=0,06; composto sim<br/>GUSTO-IIb: 30 d sim; morte e 6 meses NS<br/>Zwolle n=142: reinfarto/FE; morte ausente"])

  D1 -->|"Hospital sem sala — transferir?"| C2(["DANAMI-2: composto sim, morte NS<br/>PRAGUE-2: morte ITT P=0,12<br/>AIR-PAMI: MACE P=0,331, n=138"])

  D1 -->|"Três braços, n=300"| C3(["PRAGUE-1: C 8% vs B 15% vs A 23%<br/>Composto. ≠ PRAGUE-2"])

  classDef conduta fill:#eef6ef,stroke:#2f7a4f,color:#12301f;
  class C1,C2,C3 conduta;
```

## Mensagem prática

**Mesmo hospital ≠ transferência.** Morte isolada falha em PAMI-1, GUSTO-IIb, AIR-PAMI e PRAGUE-2. Não fundir numeração PRAGUE.
