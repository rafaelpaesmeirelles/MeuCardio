---
title: "Fluxograma: CTEPH — do diagnóstico à decisão entre endarterectomia, riociguate e angioplastia pulmonar por balão"
slug: fluxograma-cteph-operabilidade-bpa-riociguate
theme: "Hipertensão pulmonar"
kind: fluxograma
fonte_producao: chatgpt
review_status: revisado
review_note: "Árvore construída a partir de dois documentos já publicados e revisados nesta pasta, sem consulta a fonte nova: 'cteph-criterios-de-operabilidade-e-a-decisao-do-heart-team-especializado.md' (revisão de Kim NH et al., Eur Respir J 2024, PMID 39209473, com os critérios de operabilidade, a composição e as três funções do heart team, o papel do heart team, os limiares de resistência vascular pulmonar residual pós-operatória — PAPm igual ou superior a 38 mmHg e RVP igual ou superior a 5 UW aos 3-6 meses — e o corte de RVP acima de 4 unidades Wood para pré-tratamento farmacológico antes de BPA) e 'angioplastia-pulmonar-por-balao-na-cteph-inoperavel-race-e-mr-bpa.md' (ensaios RACE e MR BPA, já usados no documento de operabilidade para sustentar a sequência riociguate-depois-BPA). Os cortes numéricos e a sequência de decisão foram conferidos contra o texto desses dois documentos antes de montar a árvore; nenhum PMID novo foi buscado para este fluxograma."
source_refs: ["Kim NH, D'Armini AM, Delcroix M, Jaïs X, Jevnikar M, Madani MM, Matsubara H, Palazzini M, Wiedenroth CB, Simonneau G, Jenkins DP. Chronic thromboembolic pulmonary disease. Eur Respir J. 2024;64(4):2401294. DOI: 10.1183/13993003.01294-2024. PMID: 39209473 — já citado em 'cteph-criterios-de-operabilidade-e-a-decisao-do-heart-team-especializado.md' desta pasta, texto integral em acesso aberto (PMC11525345).", "Kawakami T, Matsubara H, Shinke T, et al. Balloon pulmonary angioplasty versus riociguat in inoperable chronic thromboembolic pulmonary hypertension (MR BPA): an open-label, randomised controlled trial. Lancet Respir Med. 2022;10(10):949-960. DOI: 10.1016/S2213-2600(22)00171-0. PMID: 35926544 — já citado em 'cteph-criterios-de-operabilidade-e-a-decisao-do-heart-team-especializado.md' e em 'angioplastia-pulmonar-por-balao-na-cteph-inoperavel-race-e-mr-bpa.md', ambos desta pasta.", "Humbert M, Kovacs G, Hoeper MM, et al. 2022 ESC/ERS Guidelines for the diagnosis and treatment of pulmonary hypertension. Eur Heart J. 2022;43(38):3618-3731. DOI: 10.1093/eurheartj/ehac237. PMID: 36017548 — recomendação Classe I/Nível B para BPA em doença inoperável ou residual, já citada em 'cteph-criterios-de-operabilidade-e-a-decisao-do-heart-team-especializado.md' desta pasta."]
---

# Fluxograma: CTEPH — do diagnóstico à decisão entre endarterectomia, riociguate e angioplastia pulmonar por balão

A hipertensão pulmonar tromboembólica crônica (CTEPH, grupo 4) é a única forma de
hipertensão pulmonar com tratamento potencialmente curativo — a endarterectomia
pulmonar. Mas a decisão de quem opera, quem faz angioplastia pulmonar por balão (BPA) e
quem recebe riociguate como ponte ou tratamento definitivo depende de uma avaliação em
equipe multidisciplinar, não de um corte isolado. Este fluxograma organiza essa sequência
de decisão a partir do momento em que o diagnóstico hemodinâmico já está confirmado.

## Árvore de decisão

```mermaid
flowchart TD
  R0["CTEPH confirmada — cateterismo direito<br/>com padrão pré-capilar e imagem compatível<br/>(cintilografia V/Q e/ou angiotomografia)"] --> P1["Encaminhar a centro de expertise em CTEPH<br/>para decisão em heart team multidisciplinar<br/>(cirurgião de EAP, intervencionista de BPA,<br/>especialista em HP e radiologista torácico)"]

  P1 --> D1{"Doença tecnicamente operável?<br/>acessibilidade cirúrgica avaliada pela equipe<br/>RVP muito elevada, idade avançada, obesidade<br/>e cirurgia prévia não são contraindicação isolada"}

  D1 -->|"Sim, doença central acessível ao cirurgião"| D2{"Paciente aceita a cirurgia e não tem<br/>comorbidade proibitiva ao risco cirúrgico?"}

  D1 -->|"Não, doença distal além do<br/>alcance seguro do cirurgião"| D4{"Resistência vascular pulmonar<br/>pré-procedimento acima de 4 unidades Wood?"}

  D2 -->|"Sim"| P2["Endarterectomia pulmonar (EAP)"]

  D2 -->|"Não, recusa ou<br/>comorbidade proibitiva"| D4b{"Resistência vascular pulmonar<br/>pré-procedimento acima de 4 unidades Wood?"}

  P2 --> D3{"Hipertensão pulmonar residual<br/>3 a 6 meses após a cirurgia?<br/>PAPm igual ou superior a 38mmHg<br/>e RVP igual ou superior a 5 unidades Wood"}

  D3 -->|"Não"| C1(["Seguimento clínico e hemodinâmico<br/>periódico pós-endarterectomia"])

  D3 -->|"Sim"| C2(["Riociguate e/ou angioplastia pulmonar<br/>por balão complementar para a doença<br/>residual pós-endarterectomia"])

  D4 -->|"Sim"| C3(["Pré-tratamento com riociguate por cerca<br/>de 6 meses, seguido de angioplastia<br/>pulmonar por balão (BPA) seriada"])

  D4 -->|"Não"| C4(["Angioplastia pulmonar por balão (BPA)<br/>seriada, sem pré-tratamento<br/>farmacológico obrigatório"])

  D4b -->|"Sim"| C3b(["Pré-tratamento com riociguate por cerca<br/>de 6 meses, seguido de angioplastia<br/>pulmonar por balão (BPA) seriada"])

  D4b -->|"Não"| C4b(["Angioplastia pulmonar por balão (BPA)<br/>seriada, sem pré-tratamento<br/>farmacológico obrigatório"])

  classDef conduta fill:#eef6ef,stroke:#2f7a4f,color:#12301f;
  class C1,C2,C3,C4,C3b,C4b conduta;
```

## O que a árvore não mostra

- **"Operabilidade" não é um corte numérico único.** A própria fonte reconhece que não
  existe hoje um escore de risco pré-operatório validado, nem evidência sobre a
  objetividade da decisão entre diferentes equipes multidisciplinares — a avaliação
  depende da expertise coletiva do centro, e é por isso que a árvore trata a decisão de
  operabilidade como um nó de equipe, não como uma regra fixa.
- **Operabilidade técnica não é o mesmo que decisão de operar.** Um paciente pode ser
  tecnicamente operável e ainda assim não seguir para cirurgia, por recusa própria ou por
  comorbidade que torna a relação risco-benefício desfavorável — é essa distinção que
  separa os dois ramos de "resistência vascular pulmonar acima de 4 unidades Wood" na
  árvore, um vindo de inoperabilidade técnica e outro de operabilidade técnica sem
  indicação prática de cirurgia.
- **A mortalidade operatória em centros de expertise está hoje em torno de 2%, com
  centros de referência abaixo de 3%** — inclusive nas formas mais graves, com resistência
  vascular pulmonar pré-operatória acima de 1.000 dyn·s·cm⁻⁵, onde a mortalidade caiu para
  menos de 5%. Não é um ramo da árvore porque não muda a decisão de encaminhar — reforça
  por que a avaliação em centro de expertise vale mesmo em doença aparentemente grave.
- **Não há evidência de benefício em atrasar a cirurgia** de um paciente operável para
  tentar terapia-ponte, farmacológica ou por BPA — por isso a árvore não oferece esse
  desvio a quem já foi definido como candidato à endarterectomia.
- **Doença veno-oclusiva e microvasculopatia associada** não entram como ramo: quando a
  obstrução mecânica central não se correlaciona com a gravidade hemodinâmica encontrada,
  há suspeita de doença de pequenos vasos associada, que limita o benefício hemodinâmico
  esperado mesmo em doença central tecnicamente ressecável — achado que reforça a decisão
  do heart team, sem constituir um ramo separado.
- **A árvore não cobre a hipertensão pulmonar tromboembólica crônica em paciente com
  vasorreatividade positiva** (cenário distinto, sem indicação de bloqueador de canal de
  cálcio no grupo 4) nem os critérios de escolha inicial de terapia combinada na HAP do
  grupo 1 — ver o fluxograma próprio desta pasta para HAP idiopática/hereditária.
