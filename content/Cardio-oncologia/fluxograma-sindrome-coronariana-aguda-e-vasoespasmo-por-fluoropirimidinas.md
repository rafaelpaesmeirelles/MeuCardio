---
title: "Fluxograma: SCA e vasoespasmo coronariano por fluoropirimidinas"
slug: fluxograma-sindrome-coronariana-aguda-e-vasoespasmo-por-fluoropirimidinas
theme: "Cardio-oncologia"
kind: fluxograma
summary: "Árvore de decisão para dor torácica/isquemia em uso de 5-FU ou capecitabina, priorizando suspensão da fluoropirimidina, manejo como SCA e exclusão de doença coronária grave antes de atribuir o quadro a vasoespasmo."
review_status: revisado
source_refs: ["Lyon AR, López-Fernández T, Couch LS, et al.; ESC Scientific Document Group. 2022 ESC Guidelines on cardio-oncology. Eur Heart J. 2022;43(41):4229-4361. DOI: 10.1093/eurheartj/ehac244. PMID: 36017568.", "European Society of Cardiology. Monitoring and treatment of cardiovascular complications during cancer therapies. Part I: Anthracyclines, HER2-targeted therapies and fluoropyrimidines. ESC CardioPractice. Seção de fluoropirimidinas consultada nesta sessão.", "Zafar A, Drobni ZD, Lei M, et al. The efficacy and safety of cardio-protective therapy in patients with 5-FU-associated coronary vasospasm. PLoS One. 2022;17(4):e0265767. DOI: 10.1371/journal.pone.0265767. PMID: 35390017."]
---

# SCA/vasoespasmo durante 5-FU ou capecitabina

```mermaid
flowchart TD
  R0["Paciente em 5-FU/capecitabina com<br/>dor torácica, alteração de ECG, troponina,<br/>síncope, arritmia ou instabilidade"]
  P1["Interromper fluoropirimidina imediatamente;<br/>ECG + troponina + monitorização;<br/>avaliar como síndrome coronariana aguda"]
  D1{"Supra persistente, isquemia contínua,<br/>choque ou arritmia ameaçadora à vida?"}
  C1(["Sim: conduzir como SCA de alto risco;<br/>estratégia coronária urgente conforme diretriz vigente;<br/>não atrasar assumindo vasoespasmo"])
  P2["Não: excluir doença coronária grave<br/>por CCTA ou angiografia conforme risco/apresentação"]
  D2{"Doença coronária obstrutiva grave<br/>que explique o quadro?"}
  C2(["Sim: tratar SCA/DAC conforme anatomia e risco;<br/>decisão oncológica posterior em equipe multidisciplinar"])
  D3{"Sem obstrução grave + quadro compatível<br/>com vasoespasmo por fluoropirimidina?"}
  C3(["Sim: tratamento anti-isquêmico conforme estado<br/>hemodinâmico e protocolo de vasoespasmo;<br/>manter fluoropirimidina suspensa durante fase aguda"])
  C4(["Não: ampliar diagnóstico diferencial<br/>(miocardite, TTS, TEP, pericárdio, outras causas)"])
  D4{"Sintomas graves ou arritmia?"}
  C5(["Sim: monitorização contínua para detectar<br/>arritmia ventricular potencialmente fatal"])
  C6(["Não: observação/reavaliação conforme risco clínico"])
  P3["Após resolução: discutir alternativa oncológica.<br/>Rechallenge somente se necessário, em MDT,<br/>após excluir DAC grave e em ambiente monitorizado"]
  C7(["Se rechallenge selecionado: ESC recomenda<br/>profilaxia com nitrato de longa ação + CCB;<br/>dose específica depende do fármaco/bula e paciente"])

  R0 --> P1
  P1 --> D1
  D1 -->|"Sim"| C1
  D1 -->|"Não"| P2
  P2 --> D2
  D2 -->|"Sim"| C2
  D2 -->|"Não"| D3
  D3 -->|"Sim"| C3
  D3 -->|"Não"| C4
  C1 --> D4
  C2 --> D4
  C3 --> D4
  C4 --> D4
  D4 -->|"Sim"| C5
  D4 -->|"Não"| C6
  C5 --> P3
  C6 --> P3
  P3 --> C7

  classDef conduta fill:#eef6ef,stroke:#2f7a4f,color:#12301f;
  class C1,C2,C3,C4,C5,C6,C7 conduta;
```

## Regra de segurança

A emergência não é o momento de “testar” se a dor é apenas espasmo: **suspender a fluoropirimidina e excluir SCA/doença coronária grave primeiro**. Reexposição é uma decisão posterior, selecionada e multidisciplinar.
