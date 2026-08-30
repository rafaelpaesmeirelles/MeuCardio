---
title: "Fluxograma: revascularização completa no STEMI multiarterial — PRAMI, COMPARE, COMPLETE, FLOWER-MI"
slug: fluxograma-revascularizacao-completa-no-stemi-prami-compare-complete
theme: "Doença coronariana"
kind: fluxograma
summary: "Depois da culpada no IAMCSST multiarterial: completa está no COMPLETE. FFR vs angio na completa é FLOWER-MI (neutro). COMPARE-ACUTE (FFR no agudo) puxou revascularização, não morte. PRAMI (angio, n=465, parado cedo) é ancestral. Choque sai — CULPRIT-SHOCK."
review_status: revisado
fonte_producao: grok
review_note: "Produção científica contínua em 29/08/2026. Árvore ancorada nos abstracts de PRAMI (PMID 23991625) e COMPARE-ACUTE (PMID 28317428) relidos nesta revisão editorial, e nos documentos já existentes COMPLETE, FLOWER-MI, DANAMI-3-PRIMULTI e CULPRIT-SHOCK. Revisão científica concluída em 30/08/2026."
source_refs:
  - "Wald DS, et al. PRAMI. N Engl J Med. 2013;369(12):1115-23. PMID: 23991625."
  - "Smits PC, et al. COMPARE-ACUTE. N Engl J Med. 2017;376(13):1234-1244. PMID: 28317428."
  - "Documentos da casa revascularizacao-completa-versus-somente-lesao-culpada-no-iam-multiarterial-o-ensaio-complete, flower-mi-ffr-versus-angiografia-na-revascularizacao-completa-do-stemi, danami-3-primulti-10-anos-ffr-guiada-revascularizacao-completa-stemi, culprit-shock-pci-lesao-culpada-choque-cardiogenico."
---

# Fluxograma: revascularização completa no STEMI multiarterial

```mermaid
flowchart TD
  R0["IAMCSST multiarterial,<br/>culpada já aberta"] --> D1{"Choque cardiogênico?"}

  D1 -->|"Sim"| C0(["CULPRIT-SHOCK: só a culpada no agudo.<br/>Sai desta árvore"])

  D1 -->|"Não"| D2{"Completa já foi decidida<br/>e a dúvida é FFR vs angio?"}

  D2 -->|"Sim"| C1(["FLOWER-MI: FFR vs angio, neutro.<br/>Não atrasar a completa por FFR obrigatório"])

  D2 -->|"Não"| D3{"A pergunta é completa vs só culpada?"}

  D3 -->|"Sim"| C2(["COMPLETE é o n que segura a completa<br/>(não necessariamente no mesmo tempo da primária)"])

  D3 -->|"Não — FFR no agudo vs nada"| C3(["COMPARE-ACUTE: composto HR 0,35,<br/>puxado por nova revascularização;<br/>morte 1,4% vs 1,7% NS. Regra dos 45 d"])

  C2 --> N1(["PRAMI: ancestral angiográfico, n=465,<br/>parado cedo; morte cardíaca IC cruza 1"])

  classDef conduta fill:#eef6ef,stroke:#2f7a4f,color:#12301f;
  class C0,C1,C2,C3,N1 conduta;
```

## Mensagem prática

**Estável, multiarterial: completa (COMPLETE). Choque: só culpada. FFR vs angio na completa: FLOWER-MI. COMPARE não prova redução de morte.**
