---
title: "Fluxograma: anticoagulação periprocedimento na FA para procedimento eletivo — BRIDGE e PAUSE"
slug: fluxograma-anticoagulacao-periprocedimento-fa-bridge-pause
theme: "Fibrilação atrial"
kind: fluxograma
fonte_producao: chatgpt
review_status: revisado
review_note: "Verificado por Claude em 26/08/2026: fonte primaria conferida; conteudo derivado de documento(s) ja publicado(s) no acervo, listado(s) em source_refs."
source_refs:
  - "Douketis JD, Spyropoulos AC, Kaatz S, et al; BRIDGE Investigators. Perioperative Bridging Anticoagulation in Patients with Atrial Fibrillation. New England Journal of Medicine. 2015;373(9):823-833. DOI: 10.1056/NEJMoa1501035. PMID: 26095867."
  - "Douketis JD, Spyropoulos AC, Duncan J, et al. Perioperative Management of Patients With Atrial Fibrillation Receiving a Direct Oral Anticoagulant (PAUSE). JAMA Internal Medicine. 2019;179(11):1469-1478. DOI: 10.1001/jamainternmed.2019.2431. PMID: 31380891."
  - "Derivado do documento já publicado no acervo 'Interrupção do Anticoagulante para Procedimento Eletivo na FA: BRIDGE e PAUSE' (content/Fibrilação_atrial/interrupcao-do-anticoagulante-para-procedimento-eletivo-na-fa-bridge-e-pause.md), que cita as mesmas duas fontes acima."
---

# Fluxograma: anticoagulação periprocedimento na FA para procedimento eletivo — BRIDGE e PAUSE

Esta é a pergunta de consultório mais frequente na FA anticoagulada: o paciente vai fazer uma cirurgia ou procedimento eletivo qualquer — extração dentária, colonoscopia, cirurgia de catarata, herniorrafia — e não uma cardioversão ou ablação. Durante anos, a resposta padrão era "ponte com heparina, por segurança". O BRIDGE (varfarina) e o PAUSE (DOAC) mostraram que essa prática causa dano sem entregar proteção, e que a interrupção pode seguir um protocolo simples baseado em dias, não em exame de coagulação.

## Árvore de decisão

```mermaid
flowchart TD
  R0["Paciente com FA em anticoagulação oral crônica, com procedimento eletivo agendado (não cardioversão)"] --> D1{"Qual anticoagulante está em uso?"}

  D1 -->|"Antagonista de vitamina K (varfarina)"| D2{"Paciente com risco tromboembólico muito alto (prótese valvar mecânica, estenose mitral reumática ou AVC recente) — população excluída do BRIDGE?"}
  D2 -->|"Sim"| C1(["Não extrapolar o resultado do BRIDGE; individualizar com equipe especializada, considerando ponte com heparina caso a caso"])
  D2 -->|"Não"| P1["Suspender a varfarina 5 dias antes do procedimento; reiniciar em até 24 horas depois"]
  P1 --> C2(["Não fazer ponte com heparina de rotina — o BRIDGE mostrou não inferioridade para tromboembolismo arterial e menos sangramento maior sem a ponte"])

  D1 -->|"DOAC (apixabana, dabigatrana ou rivaroxabana)"| D3{"Risco de sangramento do procedimento"}
  D3 -->|"Baixo risco de sangramento"| C3(["Omitir o DOAC 1 dia antes do procedimento e reiniciar 1 dia depois, sem ponte e sem dosar coagulação"])
  D3 -->|"Alto risco de sangramento"| P2["Considerar a função renal, especialmente relevante para a dabigatrana (eliminação predominantemente renal)"]
  P2 --> C4(["Omitir o DOAC 2 dias antes do procedimento e reiniciar 2 a 3 dias depois, sem ponte e sem dosar coagulação"])

  D1 -->|"Edoxabana"| C5(["Protocolo do PAUSE não incluiu edoxabana; seguir orientação farmacocinética específica e discutir com especialista"])

  classDef conduta fill:#eef5f8,stroke:#1c7293,color:#0b2e45;
  class C1,C2,C3,C4,C5 conduta;
```

## O que a árvore não mostra

**Os números do BRIDGE**: tromboembolismo arterial em 0,4% sem ponte contra 0,3% com ponte (não inferioridade, p=0,01), e sangramento maior em 1,3% sem ponte contra 3,2% com ponte (risco relativo 0,41; p=0,005 para superioridade) — a ponte estava tentando prevenir um evento raro ao custo de triplicar o sangramento maior.

**Os números do PAUSE**, coorte de 3.007 pacientes com FA em apixabana, dabigatrana ou rivaroxabana: sangramento maior em 30 dias variou de 0,90% (dabigatrana) a 1,85% (rivaroxabana), e tromboembolismo arterial de 0,16% a 0,60% — nenhuma dosagem de coagulação foi usada para liberar o procedimento.

**Ambos os estudos são de procedimento eletivo** — nada nesta árvore se aplica a cirurgia de urgência, cenário em que a discussão é de reversão do anticoagulante, não de suspensão programada. **O BRIDGE é randomizado, duplo-cego**; **o PAUSE é coorte prospectiva, sem braço comparador** — demonstra segurança da estratégia, não superioridade sobre outra. **Em qualquer ramo, a retomada do anticoagulante no prazo definido faz parte do protocolo** — interromper sem plano de reinício é o outro lado do mesmo erro.