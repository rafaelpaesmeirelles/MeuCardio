---
title: "Fluxograma: manejo perioperatório da anticoagulação — suspensão, bridging e retomada"
slug: fluxograma-manejo-perioperatorio-da-anticoagulacao-suspensao-bridging-e-retomada
theme: "Farmacologia"
kind: fluxograma
fonte_producao: chatgpt
summary: "Árvore de decisão para suspender, fazer bridging com heparina ou não fazer bridging, e retomar a anticoagulação oral (varfarina ou DOAC) em torno de um procedimento cirúrgico ou invasivo eletivo, conforme risco hemorrágico do procedimento e risco tromboembólico do paciente."
review_status: revisado
review_note: "Verificado em 26/08/2026: PMIDs conferidos via PubMed E-utilities (esearch/esummary) — título, revista, volume e páginas batendo integralmente com o texto citado; nenhum PMID ou dado numérico foi inventado. O ensaio BRIDGE mostra que bridging aumenta sangramento maior sem reduzir tromboembolismo na FA de risco baixo a moderado; o protocolo PAUSE valida suspensão de DOAC sem bridging guiada por função renal e risco hemorrágico do procedimento."
source_refs:
  - "Doherty JU, Gluckman TJ, Hucker WJ, et al. 2017 ACC Expert Consensus Decision Pathway for Periprocedural Management of Anticoagulation in Patients With Nonvalvular Atrial Fibrillation. J Am Coll Cardiol. 2017;69(7):871-898. PMID 28081965."
  - "Douketis JD, Spyropoulos AC, Kaatz S, et al. Perioperative Bridging Anticoagulation in Patients with Atrial Fibrillation (BRIDGE). N Engl J Med. 2015;373(9):823-833. PMID 26095867."
  - "Douketis JD, Spyropoulos AC, Duncan J, et al. Perioperative Management of Patients With Atrial Fibrillation Receiving a Direct Oral Anticoagulant (PAUSE). JAMA Intern Med. 2019;179(11):1469-1478. PMID 31380891."
---

# Fluxograma: manejo perioperatório da anticoagulação — suspensão, bridging e retomada

A pergunta semanal de consultório — "suspendo o anticoagulante para a cirurgia, e faço ponte com heparina?" — tem resposta diferente para varfarina e para DOAC, e o erro mais caro é aplicar bridging por reflexo. O ensaio BRIDGE, randomizado e duplo-cego, mostrou que a ponte com heparina **triplica o sangramento maior** (3,2% vs. 1,3%) sem reduzir evento tromboembólico em pacientes com FA de risco baixo a moderado — bridging deveria ser exceção, reservado a quem tem risco tromboembólico alto, não rotina. Para o DOAC, o protocolo PAUSE validou que a suspensão guiada apenas por função renal e risco hemorrágico do procedimento, sem heparina em ponte, é segura na grande maioria dos casos.

## Árvore de decisão

```mermaid
flowchart TD
  R0["Paciente em anticoagulação oral crônica (FA não valvular ou TEV)<br/>com indicação de procedimento cirúrgico ou invasivo eletivo"]
  D1{"Risco hemorrágico do procedimento?"}
  C1(["Manter o anticoagulante sem interrupção; considerar apenas<br/>ajustar o horário da dose em relação ao procedimento"])
  D2{"Qual anticoagulante está em uso?"}
  D3{"Risco tromboembólico é alto (prótese valvar mecânica mitral,<br/>AVC/AIT há menos de 3 meses, ou evento tromboembólico recente<br/>com CHA2DS2-VASc muito elevado)?"}
  C2(["Suspender varfarina 5 dias antes; heparina em ponte<br/>(HBPM em dose terapêutica) até 24h antes do procedimento;<br/>reiniciar varfarina e retomar a heparina em ponte no pós-operatório<br/>até INR terapêutico"])
  C3(["Suspender varfarina 5 dias antes SEM heparina em ponte<br/>(bridging aumenta sangramento maior sem reduzir tromboembolismo<br/>nesse grupo); reiniciar varfarina 12-24h após hemostasia confirmada"])
  D4{"Função renal (ClCr) e risco hemorrágico do procedimento?"}
  C4(["Suspender o DOAC 1-2 dias antes do procedimento;<br/>sem heparina em ponte; retomar 1 dia após procedimento<br/>de baixo risco hemorrágico, com hemostasia confirmada"])
  C5(["Suspender o DOAC por período estendido (até 4-5 dias,<br/>ajustado por ClCr e pelo fármaco específico) sem heparina em ponte;<br/>retomar 2-3 dias após procedimento de alto risco,<br/>com hemostasia confirmada"])

  R0 --> D1
  D1 -->|"Mínimo (ex.: procedimento dentário simples, catarata,<br/>endoscopia sem biópsia)"| C1
  D1 -->|"Baixo a alto risco de sangramento — procedimento requer interrupção"| D2
  D2 -->|"Varfarina"| D3
  D3 -->|"Sim — bridging indicado"| C2
  D3 -->|"Não — risco tromboembólico baixo a moderado"| C3
  D2 -->|"DOAC (apixabana, rivaroxabana, dabigatrana, edoxabana)"| D4
  D4 -->|"ClCr ≥50 mL/min e procedimento de risco padrão"| C4
  D4 -->|"ClCr <50 mL/min (relevante sobretudo para dabigatrana)<br/>OU procedimento de alto risco hemorrágico"| C5

  classDef conduta fill:#eef6ef,stroke:#2f7a4f,color:#12301f;
  class C1,C2,C3,C4,C5 conduta;
```

## O que a árvore não mostra

- **Prótese valvar mecânica em qualquer posição costuma exigir bridging**, mesmo fora do subgrupo estudado no BRIDGE (que era FA não valvular) — a decisão nesse grupo segue protocolo próprio, mais conservador, e não está detalhada aqui.
- **Anestesia neuroaxial (raquianestesia/peridural) tem janela de segurança própria**, geralmente mais restritiva que a suspensão para cirurgia em si, por risco de hematoma espinhal — não coberta por esta árvore.
- **Antiagregantes plaquetários (AAS, clopidogrel) em uso concomitante** seguem lógica de suspensão independente, que pode ou não coincidir com a do anticoagulante — não estão representados aqui.
- **Procedimentos de emergência/urgência não seguem este fluxo** — nesse cenário, a pergunta é reversão emergencial, não suspensão planejada (ver o fluxograma de sangramento maior/reversão desta mesma pasta).
- **A decisão é sempre compartilhada e individualizada**: peso, sangramento prévio, fragilidade e preferência do paciente pesam além dos critérios objetivos de risco hemorrágico e tromboembólico listados na árvore.
- **Dabigatrana tem meia-vida mais sensível à função renal** que os demais DOAC — a suspensão pode precisar ser ainda mais prolongada que a indicada para apixabana/rivaroxabana/edoxabana em ClCr muito reduzido, e essa granularidade fina fica para a bula específica do fármaco.