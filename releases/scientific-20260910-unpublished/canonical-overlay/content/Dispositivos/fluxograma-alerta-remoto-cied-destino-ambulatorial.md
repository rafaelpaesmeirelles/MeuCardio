---
slug: fluxograma-alerta-remoto-cied-destino-ambulatorial
title: 'Fluxograma: alerta remoto de CIED no ambulatório — destino'
kind: fluxograma
theme: Dispositivos
summary: 'Árvore de destino após alerta remoto: emergência por sintoma/terapia recorrente, avaliação urgente do
  dependente de marca-passo com falha de captura/sensing, choque isolado estável e alertas assintomáticos.'
tags: []
source_refs:
- 'Ferrick AM, Raj SR, Deneke T, et al. 2023 HRS/EHRA/APHRS/LAHRS Expert Consensus Statement on Practical Management
  of the Remote Device Clinic. Europace. 2023;25(5):euad123. DOI: 10.1093/europace/euad123. PMID: 37208301'
- 'Slotwiner D, Varma N, Akar JG, et al. HRS Expert Consensus Statement on remote interrogation and monitoring for
  cardiovascular implantable electronic devices. Heart Rhythm. 2015;12(7):e69-e100. DOI: 10.1016/j.hrthm.2015.05.008.
  PMID: 25981148'
- 'Hindricks G, Taborsky M, Glikson M, et al; IN-TIME study group. Implant-based multiparameter telemonitoring of
  patients with heart failure (IN-TIME): a randomised controlled trial. Lancet. 2014;384(9943):583-590. DOI: 10.1016/S0140-6736(14)61176-4.
  PMID: 25131977'
- 'Varma N, Epstein AE, Irimpen A, Schweikert R, Love C; TRUST Investigators. Efficacy and safety of automatic remote
  monitoring for implantable cardioverter-defibrillator follow-up: the Lumos-T Safely Reduces Routine Office Device
  Follow-up (TRUST) trial. Circulation. 2010;122(4):325-332. DOI: 10.1161/CIRCULATIONAHA.110.937409. PMID: 20625110'
- 'van Veldhuisen DJ, Braunschweig F, Conraads V, et al. Intrathoracic impedance monitoring, audible patient alerts,
  and outcome in patients with heart failure. Circulation. 2011;124(16):1719-1726. DOI: 10.1161/CIRCULATIONAHA.111.043042.
  PMID: 21931078'
evidence_level: null
source_tier: A
review_status: revisado
gaps: []
published: false
---

# Fluxograma: alerta remoto de CIED no ambulatório — destino

Prosa: [alerta-remoto-de-cied-no-ambulatorio-quando-ligar-clinica-vs-ps](/biblioteca/alerta-remoto-de-cied-no-ambulatorio-quando-ligar-clinica-vs-ps). Premissa: [monitoramento-remoto-nao-e-servico-de-emergencia-24h](/biblioteca/monitoramento-remoto-nao-e-servico-de-emergencia-24h). Fluxos canônicos: [fluxograma-disfuncao-de-eletrodo-fratura-e-falha-de-isolamento-conduta](/biblioteca/fluxograma-disfuncao-de-eletrodo-fratura-e-falha-de-isolamento-conduta) e [fluxograma-choque-inapropriado-de-cdi-investigacao-e-manejo](/biblioteca/fluxograma-choque-inapropriado-de-cdi-investigacao-e-manejo).

## Árvore de decisão

```mermaid
flowchart TD
  A["Alerta remoto / ligação: paciente com CIED"] --> D1{"TV sustentada em curso,<br/>sintoma de alarme ou instabilidade?<br/>síncope/pré-síncope, dor torácica,<br/>dispneia aguda, IC descompensada"}

  D1 -->|"Sim"| C1(["PS / emergência agora<br/>Não esperar retorno da clínica remota"])

  D1 -->|"Não"| D2{"Houve terapia do CDI?"}

  D2 -->|"Choques/ATP repetidos<br/>em curto intervalo"| C1
  D2 -->|"Um choque isolado<br/>e paciente estável"| C2(["Clínica de dispositivos / EP URGENTE no mesmo dia<br/>Interrogar e classificar terapia<br/>Novo choque, sintoma ou sem acesso seguro → PS"])
  D2 -->|"ATP isolada / TV sustentada terminada"| C2
  D2 -->|"Não"| D3{"Alerta de hardware?<br/>captura/sensing, impedância, noise,<br/>integridade, bateria crítica"}

  D3 -->|"Sim"| D3A{"Dependente de marca-passo<br/>E alerta sugere perda de captura<br/>ou sensing clinicamente efetivo?"}
  D3A -->|"Sim"| C3(["Avaliação MONITORIZADA urgente hoje<br/>Centro de dispositivos; se não disponível imediatamente → PS"])
  D3A -->|"Não"| BAT{"EOL/depleção crítica, risco de perda de terapia<br/>ou dependência com bateria comprometida?"}
  BAT -->|"Sim"| C3
  BAT -->|"Não"| C4(["Clínica de dispositivos no mesmo dia útil<br/>Fora do horário e estável: próximo dia útil<br/>Sintoma novo → PS"])

  D3 -->|"Não"| D4{"Tipo clínico do alerta?"}
  D4 -->|"FA/TVNS/HF index"| C5(["Clínica de dispositivos / IC em curto prazo<br/>Não PS automático se estável"])
  D4 -->|"Falha de transmissão/offline"| C6(["Clínica em dias — reconectar monitor<br/>Não é emergência por si só"])
  D4 -->|"TV sustentada terminada / ATP isolada"| C2
  D4 -->|"Outro / tipo desconhecido"| C7(["Triagem: identificar alerta + sintomas<br/>+ dependência de marca-passo<br/>Dúvida com risco clínico → avaliação presencial"])

  classDef conduta fill:#eef6ef,stroke:#2f7a4f,color:#12301f;
  classDef alerta fill:#fdecea,stroke:#b3261e,color:#3b0a0a;
  classDef urgente fill:#fff4e5,stroke:#b36b00,color:#3b2200;
  class C1 alerta;
  class C2,C3 urgente;
  class C4,C5,C6,C7 conduta;
```

## Notas

- **D1**: sintoma/instabilidade prevalece sobre qualquer classificação remota.
- **D2**: choque isolado estável não é equivalente a terapias repetidas/tempestade; ainda exige avaliação rápida do dispositivo.
- **D3A**: dependência de marca-passo muda a urgência quando há suspeita de perda de captura/sensing.
- **D4**: alerta de FA/TVNS/HF index assintomático exige avaliação dirigida, não ida automática ao PS; DOT-HF (PMID 21931078) é um freio contra intervenção baseada apenas no alerta de impedância.
- O fluxo não decide reprogramação, anticoagulação, extração de eletrodo, doses ou terapias antiarrítmicas.

**TV sustentada já terminada espontaneamente ou por ATP isolada** exige contato urgente com dispositivos/EP no mesmo dia para revisar o episódio; arritmia em curso, recorrência ou sintomas mudam para emergência. **Bateria/ERI/EOL:** classificar pelo fabricante, tempo restante, dependência e eficácia das terapias. ERI isolada não é PS automático, mas EOL/depleção crítica com risco de perda de estimulação/terapia requer avaliação monitorizada imediata. Se a avaliação urgente não estiver disponível, usar PS. FA detectada exige confirmar eletrogramas/carga e avaliar risco antes de anticoagular; alerta de IC isolado não determina diurético.
