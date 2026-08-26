---
title: "Fluxograma: isquemia arterial por nilotinibe/ponatinibe"
slug: fluxograma-isquemia-aguda-de-membro-e-doenca-arterial-por-nilotinibe-ou-ponatinibe
theme: "Cardio-oncologia"
kind: fluxograma
summary: "Árvore para isquemia de membro durante TKI BCR-ABL, priorizando viabilidade, reperfusão e revisão do agente causal."
review_status: revisado
source_refs: ["Gornik HL, Aronow HD, Goodney PP, et al. 2024 ACC/AHA/AACVPR/APMA/ABC/SCAI/SVM/SVN/SVS/SIR/VESS Guideline for the Management of Lower Extremity Peripheral Artery Disease. Circulation. 2024;149(24):e1313-e1410. DOI: 10.1161/CIR.0000000000001251. PMID: 38743805.", "Lyon AR, López-Fernández T, Couch LS, et al. 2022 ESC Guidelines on cardio-oncology. Eur Heart J. 2022;43(41):4229-4361. DOI: 10.1093/eurheartj/ehac244. PMID: 36017568."]
review_note: "Revisado em 26/08/2026 contra a seção 11 da diretriz ACC/AHA 2024 de doença arterial periférica (PMID 38743805) e a seção 6.8 da ESC 2022 de cardio-oncologia (PMID 36017568). Corrigida a sequência que colocava Doppler/angio-TC antes da avaliação de viabilidade e usava 'antitrombose' genérica: a avaliação clínica por especialista e Doppler contínuo não deve ser atrasada por imagem; na isquemia aguda, HNF IV terapêutica é iniciada ao diagnóstico salvo contraindicação. Foram separados membro irreversível (não revascularizar), categoria IIb (revascularização emergente), IIa (urgente) e viável. Progressão rápida sob nilotinibe/ponatinibe retorna à decisão hematológica de troca para TKI de menor risco. Pendente revisão médica independente antes de uso assistencial."
---

# Isquemia arterial por TKI BCR-ABL

```mermaid
flowchart TD
  R0["Paciente em nilotinibe/ponatinibe<br/>+ dor, frialdade ou perda de pulso"]
  D0{"Início agudo há &lt;2 semanas?"}
  P1["Emergência vascular: avaliar viabilidade clínica<br/>+ Doppler contínuo arterial e venoso;<br/>imagem somente se não atrasar terapia"]
  D1{"Categoria III irreversível?<br/>anestesia/paralisia completas + ausência<br/>de sinais arterial e venoso ao Doppler"}
  C0(["Não revascularizar membro inviável;<br/>amputação primária/conduta paliativa<br/>conforme prognóstico e objetivos de cuidado"])
  P2["HNF IV terapêutica ao diagnóstico,<br/>salvo sangramento/alto risco, dissecção aórtica<br/>ou trauma vascular maior"]
  D2{"Categoria IIb: ameaça imediata?<br/>perda sensitiva além dos pododáctilos<br/>ou fraqueza muscular"}
  C1(["Revascularização emergente;<br/>não atrasar por investigação etiológica"])
  D3{"Categoria IIa: ameaça marginal?<br/>sinal arterial ausente/venoso presente +<br/>perda sensitiva mínima, sem fraqueza"}
  C2(["Revascularização urgente;<br/>imagem rápida apenas se mudar a estratégia"])
  C3(["Categoria I viável: avaliação anatômica/etiológica<br/>expedita e revascularização conforme indicação"])
  P3["Quadro não agudo: estadiar DAP,<br/>progressão e risco cardiovascular"]
  D4{"DAP rapidamente progressiva<br/>ou evento arterial grave?"}
  P4["Pausar/rever TKI na fase aguda;<br/>discutir troca para alternativa de menor risco"]
  D5{"SCA/AVC em outro território?"}
  C4(["Sim: migrar imediatamente<br/>para algoritmo coronário/neurológico"])
  C5(["Não: prevenção vascular intensiva<br/>+ seguimento vascular e cardio-oncológico"])

  R0 --> D0
  D0 -->|"Sim"| P1
  D0 -->|"Não"| P3
  P1 --> P2
  P2 --> D1
  D1 -->|"Sim"| C0
  D1 -->|"Não"| D2
  D2 -->|"Sim"| C1
  D2 -->|"Não"| D3
  D3 -->|"Sim"| C2
  D3 -->|"Não"| C3
  C0 --> D4
  C1 --> D4
  C2 --> D4
  C3 --> D4
  P3 --> D4
  D4 -->|"Sim"| P4
  D4 -->|"Não"| D5
  P4 --> D5
  D5 -->|"Sim"| C4
  D5 -->|"Não"| C5

  classDef conduta fill:#eef6ef,stroke:#2f7a4f,color:#12301f;
  class C0,C1,C2,C3,C4,C5 conduta;
```

## Regra prática

A toxicidade arterial por TKI é **arterial**, não um subtipo de TEV: defina viabilidade antes de pedir imagem extensa, anticoagule a isquemia aguda quando não houver contraindicação e não reperfunda tecido irreversivelmente inviável. A investigação da causa e a decisão sobre o TKI não podem atrasar terapia salvadora do membro.
