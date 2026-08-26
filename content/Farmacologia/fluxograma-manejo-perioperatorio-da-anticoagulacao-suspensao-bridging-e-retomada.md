---
title: "Fluxograma: manejo perioperatório da anticoagulação — suspensão, bridging e retomada"
slug: fluxograma-manejo-perioperatorio-da-anticoagulacao-suspensao-bridging-e-retomada
theme: "Farmacologia"
kind: fluxograma
fonte_producao: chatgpt
summary: "Árvore de decisão para suspender, fazer bridging com heparina ou não fazer bridging, e retomar a anticoagulação oral (varfarina ou DOAC) em torno de um procedimento cirúrgico ou invasivo eletivo, conforme risco hemorrágico do procedimento e risco tromboembólico do paciente."
review_status: revisado
review_note: "Auditoria científica em 26/08/2026: PMIDs conferidos e diretriz CHEST 2022 incorporada. Removidas a ponte automática em prótese mecânica, a mistura de populações fora do BRIDGE/PAUSE e as janelas inespecíficas dos DOACs; bridging passou a exceção multidisciplinar. Mantida pendência de revisão médica antes da publicação clínica."
source_refs:
  - "Doherty JU, Gluckman TJ, Hucker WJ, et al. 2017 ACC Expert Consensus Decision Pathway for Periprocedural Management of Anticoagulation in Patients With Nonvalvular Atrial Fibrillation. J Am Coll Cardiol. 2017;69(7):871-898. PMID 28081965."
  - "Douketis JD, Spyropoulos AC, Kaatz S, et al. Perioperative Bridging Anticoagulation in Patients with Atrial Fibrillation (BRIDGE). N Engl J Med. 2015;373(9):823-833. PMID 26095867."
  - "Douketis JD, Spyropoulos AC, Duncan J, et al. Perioperative Management of Patients With Atrial Fibrillation Receiving a Direct Oral Anticoagulant (PAUSE). JAMA Intern Med. 2019;179(11):1469-1478. PMID 31380891."
  - "Douketis JD, Spyropoulos AC, Murad MH, et al. Perioperative Management of Antithrombotic Therapy: CHEST Clinical Practice Guideline. Chest. 2022;162(5):e207-e243. PMID 35964704."
---

# Fluxograma: manejo perioperatório da anticoagulação — suspensão, bridging e retomada

A pergunta semanal de consultório — "suspendo o anticoagulante para a cirurgia, e faço ponte com heparina?" — tem resposta diferente para varfarina e para DOAC, e o erro mais caro é aplicar bridging por reflexo. O ensaio BRIDGE, randomizado e duplo-cego, mostrou que a ponte com heparina **triplica o sangramento maior** (3,2% vs. 1,3%) sem reduzir evento tromboembólico em pacientes com FA de risco baixo a moderado — bridging deveria ser exceção, reservado a quem tem risco tromboembólico alto, não rotina. Para o DOAC, o protocolo PAUSE validou que a suspensão guiada apenas por função renal e risco hemorrágico do procedimento, sem heparina em ponte, é segura na grande maioria dos casos.

## Árvore de decisão

```mermaid
flowchart TD
  R0["Paciente em anticoagulação oral crônica por fibrilação atrial<br/>com indicação de procedimento cirúrgico ou invasivo eletivo"]
  D1{"Risco hemorrágico do procedimento?"}
  C1(["Manter o anticoagulante sem interrupção; considerar apenas<br/>ajustar o horário da dose em relação ao procedimento"])
  D2{"Qual anticoagulante está em uso?"}
  D3{"Risco tromboembólico excepcionalmente alto<br/>(AVC/AIT há menos de 3 meses ou CHA2DS2-VASc 7–9)?"}
  C2(["Suspender varfarina 5 dias antes; não fazer ponte<br/>automaticamente: discutir se risco excepcional justifica HBPM/HNF;<br/>reiniciar varfarina após hemostasia; CHEST recomenda contra rotina"])
  C3(["Suspender varfarina 5 dias antes SEM heparina em ponte<br/>(bridging aumenta sangramento maior sem reduzir tromboembolismo<br/>nesse grupo); reiniciar varfarina 12-24h após hemostasia confirmada"])
  D4{"Risco hemorrágico do procedimento é baixo/moderado?"}
  C4(["Interromper DOAC 1 dia antes e retomar cerca de 24h depois,<br/>com hemostasia; para dabigatrana com ClCr abaixo de 50,<br/>interromper 2 dias antes; nunca fazer ponte com heparina"])
  C5(["Alto risco: interromper DOAC 2 dias antes e retomar<br/>48–72h depois, com hemostasia; para dabigatrana com<br/>ClCr abaixo de 50, interromper 4 dias antes; sem ponte"])

  R0 --> D1
  D1 -->|"Mínimo (ex.: procedimento dentário simples, catarata,<br/>endoscopia sem biópsia)"| C1
  D1 -->|"Baixo a alto risco de sangramento — procedimento requer interrupção"| D2
  D2 -->|"Varfarina"| D3
  D3 -->|"Sim — exceção a discutir"| C2
  D3 -->|"Não — risco tromboembólico baixo a moderado"| C3
  D2 -->|"DOAC (apixabana, rivaroxabana, dabigatrana, edoxabana)"| D4
  D4 -->|"Sim"| C4
  D4 -->|"Não — alto risco"| C5

  classDef conduta fill:#eef6ef,stroke:#2f7a4f,color:#12301f;
  class C1,C2,C3,C4,C5 conduta;
```

## O que a árvore não mostra

- **Prótese valvar mecânica e TEV estão fora desta árvore.** BRIDGE e PAUSE estudaram FA; a CHEST 2022 também sugere contra ponte rotineira em prótese mecânica ou TEV, mas a decisão individual depende de tipo de prótese, evento recente e procedimento.
- **Anestesia neuroaxial (raquianestesia/peridural) tem janela de segurança própria**, geralmente mais restritiva que a suspensão para cirurgia em si, por risco de hematoma espinhal — não coberta por esta árvore.
- **Antiagregantes plaquetários (AAS, clopidogrel) em uso concomitante** seguem lógica de suspensão independente, que pode ou não coincidir com a do anticoagulante — não estão representados aqui.
- **Procedimentos de emergência/urgência não seguem este fluxo** — nesse cenário, a pergunta é reversão emergencial, não suspensão planejada (ver o fluxograma de sangramento maior/reversão desta mesma pasta).
- **A decisão é sempre compartilhada e individualizada**: peso, sangramento prévio, fragilidade e preferência do paciente pesam além dos critérios objetivos de risco hemorrágico e tromboembólico listados na árvore.
- **Dabigatrana tem meia-vida mais sensível à função renal** que os demais DOAC — a suspensão pode precisar ser ainda mais prolongada que a indicada para apixabana/rivaroxabana/edoxabana em ClCr muito reduzido, e essa granularidade fina fica para a bula específica do fármaco.
