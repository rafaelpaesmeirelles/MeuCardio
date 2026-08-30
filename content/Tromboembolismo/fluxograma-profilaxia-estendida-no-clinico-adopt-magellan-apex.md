---
title: "Fluxograma: profilaxia estendida no clínico — ADOPT NS, MAGELLAN sangra, APEX sequencial NS"
slug: fluxograma-profilaxia-estendida-no-clinico-adopt-magellan-apex
theme: "Tromboembolismo"
kind: fluxograma
summary: "Estender DOAC após internacão clínica: ADOPT (apixabana 30 d) primário P=0,44 e sangramento maior P=0,04. MAGELLAN (rivaroxabana 35 d) TEV dia 35 P=0,02 com sangramento maior+CRNMB P<0,001. APEX (betrixabana) primário D-dímero P=0,054 NS. MARINER já está no Padua — não reler aqui. Não vender nenhum destes como rotina de alta."
review_status: revisado
fonte_producao: grok
review_note: "Produção científica contínua em 29/08/2026. Árvore ancorada em ADOPT PMID 22077144, MAGELLAN PMID 23388003 e APEX PMID 27232649. MARINER permanece no arquivo Padua. Revisão científica concluída em 30/08/2026."
source_refs:
  - "Goldhaber SZ, et al. ADOPT. N Engl J Med. 2011;365(23):2167-2177. PMID: 22077144."
  - "Cohen AT, et al. MAGELLAN. N Engl J Med. 2013;368(6):513-523. PMID: 23388003."
  - "Cohen AT, et al. APEX. N Engl J Med. 2016;375(6):534-544. PMID: 27232649."
  - "Documento da casa profilaxia-de-tev-no-paciente-clinico-hospitalizado-escore-de-padua-e-profilaxia-estendida — MARINER."
---

# Fluxograma: estender anticoagulante no clínico?

```mermaid
flowchart TD
  R0["Alta de internacão clínica.<br/>Estender profilaxia com DOAC?"] --> D1{"Qual ensaio está sendo citado?"}

  D1 -->|"Apixabana 2,5 mg 30 d vs enoxaparina 6–14 d"| C1(["ADOPT: primário 2,71% vs 3,06%; P=0,44 NS<br/>Sangramento maior RR 2,58; P=0,04"])

  D1 -->|"Rivaroxabana 10 mg 35 d vs enoxaparina 10 d"| C2(["MAGELLAN: dia 10 NI. Dia 35 TEV P=0,02<br/>Maior+CRNMB P<0,001 nos dois tempos"])

  D1 -->|"Betrixabana 35–42 d, análise sequencial"| C3(["APEX: coorte D-dímero P=0,054 NS<br/>Overall é exploratório"])

  D1 -->|"Rivaroxabana pós-alta, IMPROVE"| C4(["MARINER. Já no arquivo Padua.<br/>Não reler números aqui"])

  classDef conduta fill:#eef6ef,stroke:#2f7a4f,color:#12301f;
  class C1,C2,C3,C4 conduta;
```

## Mensagem prática

**Nenhum destes autoriza estender DOAC de rotina na alta do clínico.** ADOPT empata e sangra; MAGELLAN reduz TEV no dia 35 com mais sangramento; APEX falha o primário sequencial.
