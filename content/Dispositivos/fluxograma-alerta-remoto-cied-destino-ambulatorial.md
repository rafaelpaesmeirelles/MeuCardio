---
title: "Fluxograma: alerta remoto de CIED no ambulatório — destino"
slug: fluxograma-alerta-remoto-cied-destino-ambulatorial
theme: "Dispositivos"
kind: fluxograma
fonte_producao: grok
summary: "Árvore curta de destino após alerta de monitoramento remoto: sintoma de alarme, terapia de CDI, hardware vs alerta clínico assintomático — clínica de dispositivos vs PS. Não substitui IN-TIME nem os pacotes pós-choque (#835) e pré-RM (#870)."
review_status: pendente_revisao
review_note: "Irmão do protocolo alerta-remoto-de-cied-no-ambulatorio-quando-ligar-clinica-vs-ps (07/09/2026). Além #835/#870. PMIDs 37208301, 25981148, 25131977, 20625110."
source_refs:
  - "Ferrick AM, Raj SR, Deneke T, et al. 2023 HRS/EHRA/APHRS/LAHRS Expert Consensus Statement on Practical Management of the Remote Device Clinic. Europace. 2023;25(5):euad123. DOI: 10.1093/europace/euad123. PMID: 37208301"
  - "Slotwiner D, Varma N, Akar JG, et al. HRS Expert Consensus Statement on remote interrogation and monitoring for cardiovascular implantable electronic devices. Heart Rhythm. 2015;12(7):e69-e100. DOI: 10.1016/j.hrthm.2015.05.008. PMID: 25981148"
  - "Hindricks G, Taborsky M, Glikson M, et al; IN-TIME study group. Implant-based multiparameter telemonitoring of patients with heart failure (IN-TIME): a randomised controlled trial. Lancet. 2014;384(9943):583-590. DOI: 10.1016/S0140-6736(14)61176-4. PMID: 25131977"
  - "Varma N, Epstein AE, Irimpen A, Schweikert R, Love C; TRUST Investigators. Efficacy and safety of automatic remote monitoring for implantable cardioverter-defibrillator follow-up: the Lumos-T Safely Reduces Routine Office Device Follow-up (TRUST) trial. Circulation. 2010;122(4):325-332. DOI: 10.1161/CIRCULATIONAHA.110.937409. PMID: 20625110"
---

# Fluxograma: alerta remoto de CIED no ambulatório — destino

Prosa: [`alerta-remoto-de-cied-no-ambulatorio-quando-ligar-clinica-vs-ps`](alerta-remoto-de-cied-no-ambulatorio-quando-ligar-clinica-vs-ps.md). Premissa: [`monitoramento-remoto-nao-e-servico-de-emergencia-24h`](monitoramento-remoto-nao-e-servico-de-emergencia-24h.md). Evidência de desfecho: [`telemonitoramento-remoto-de-cdi-e-crt-d-e-desfecho-clinico-o-ensaio-in-time`](telemonitoramento-remoto-de-cdi-e-crt-d-e-desfecho-clinico-o-ensaio-in-time.md).

## Árvore de decisão

```mermaid
flowchart TD
  A["Alerta remoto / ligação: paciente com CIED"] --> D1{"Há sintoma de alarme agora?<br/>(síncope, choque sentido, dor torácica,<br/>dispneia aguda, instabilidade)"}

  D1 -->|"Sim"| C1(["PS / emergência agora<br/>Não esperar retorno da clínica remota"])

  D1 -->|"Não — assintomático ou sintoma leve"| D2{"Foi terapia de CDI<br/>(choque / ATP em cascata)?"}

  D2 -->|"Sim"| C2(["Via pós-choque (#835):<br/>PS ou centro urgente — não alta só com ‘alerta remoto’"])

  D2 -->|"Não"| D3{"Alerta de hardware?<br/>(impedância, noise, integridade, ERI crítico)"}

  D3 -->|"Sim"| C3(["Clínica de dispositivos no mesmo dia útil<br/>Se fora do horário e estável: próximo dia útil;<br/>sintoma novo → PS"])

  D3 -->|"Não"| D4{"Tipo: FA/TV não sustentada / HF index<br/>ou falha de transmissão?"}

  D4 -->|"FA/TVNS / HF alert"| C4(["Clínica de dispositivos / IC em dias curtos<br/>Não PS automático se estável"])

  D4 -->|"Falha de transmissão / offline"| C5(["Clínica em dias — reconectar monitor<br/>Não é emergência"])

  D4 -->|"Tipo desconhecido"| C6(["Triagem: pedir print/tipo do alerta<br/>+ sintomas; se dúvida com sintoma → PS"])

  classDef conduta fill:#eef6ef,stroke:#2f7a4f,color:#12301f;
  classDef alerta fill:#fdecea,stroke:#b3261e,color:#3b0a0a;
  class C1,C2 alerta;
  class C3,C4,C5,C6 conduta;
```

## O que a árvore não decide

- Reprogramação de zonas / discriminação.
- Anticoagulação na FA detectada remotamente.
- Se o índice de IC deve mudar diurético hoje.
- Extração de eletrodo ou colete vestível.

Essas decisões ficam com o centro de dispositivos / EP e com os documentos irmãos deste tema.

## Lembrete de evidência

RM acelera detecção (TRUST, PMID 20625110) e pode melhorar desfecho composto em IC selecionada (IN-TIME, PMID 25131977), mas o consenso 2023 (PMID 37208301) deixa explícito: **não é serviço de emergência**. Por isso o ramo “assintomático” aponta para a **clínica**, e o ramo “sintomático” para o **PS** — independentemente do bip no app.
