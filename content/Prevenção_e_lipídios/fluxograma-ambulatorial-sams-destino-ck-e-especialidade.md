---
title: "Fluxograma ambulatorial: SAMS — destino (suspender/labs vs. reexposição vs. especialidade)"
slug: fluxograma-ambulatorial-sams-destino-ck-e-especialidade
theme: "Prevenção e lipídios"
kind: fluxograma
fonte_producao: grok
summary: "Árvore ambulatorial: alarme → suspender+CK/PS; SAMS leve → reexposição; não-resolução pós-suspensão → especialidade neuromuscular."
review_status: revisado
published: false
review_note: "Revisão clínica/editorial Codex em 08/09/2026: consenso EAS, ESC/EAS 2025 e StatinWISE verificados; gate de rabdomiólise, reexposição e suspeita anti-HMGCR mantidos sem doses. Não representa revisão humana independente."
source_refs:
  - "Stroes ES, Thompson PD, Corsini A, et al. Statin-associated muscle symptoms: EAS Consensus Panel. Eur Heart J. 2015;36(17):1012-1022. DOI: 10.1093/eurheartj/ehv043. PMID: 25694464"
  - "Mach F, Koskinas KC, Roeters van Lennep J, et al. 2025 focused update of the 2019 ESC/EAS Guidelines for the management of dyslipidaemias. Eur Heart J. 2025;46(42):4359-4378. DOI: 10.1093/eurheartj/ehaf190"
  - "Herrett E, Williamson E, Brack K, et al. StatinWISE. BMJ. 2021;372:n135. DOI: 10.1136/bmj.n135. PMID: 33627334"
---

# Fluxograma ambulatorial: SAMS — destino

Prosa: [`sinalizadores-ambulatoriais-sams-quando-suspender-e-escalar-labs`](sinalizadores-ambulatoriais-sams-quando-suspender-e-escalar-labs.md).

## Árvore de decisão

```mermaid
flowchart TD
  R0["Consulta ambulatorial<br/>sintoma muscular em uso de estatina"] --> D1{"Há alarme de gravidade?<br/>fraqueza incapacitante<br/>urina escura / oligúria<br/>instabilidade / precipitante agudo"}

  D1 -->|"Sim ou dúvida fundamentada"| C1(["Suspender estatina AGORA<br/>Pedir CK ± creatinina/eletrólitos<br/>PS se rabdomiólise / instabilidade"])

  D1 -->|"Não"| D2{"Sintoma leve/moderado<br/>sem fraqueza incapacitante?"}

  D2 -->|"Sim"| P1["Checar exercício, tireoide,<br/>interações; CK se disponível"]
  P1 --> C2(["Via ambulatorial de reexposição<br/>EAS 2015 / StatinWISE<br/>Não rotular intolerância definitiva"])

  D2 -->|"Não / dúvida"| D3{"Após suspender:<br/>fraqueza ou CK persistem/pioram<br/>semanas depois?"}

  D3 -->|"Sim"| C3(["Escalar especialidade<br/>neuromuscular / anti-HMGCR"])
  D3 -->|"Não / melhora"| C4(["Retomar protocolo de<br/>reexposição estruturada<br/>Manter meta lipídica ESC/EAS"])

  C2 --> D4{"Acesso e retorno garantidos?"}
  D4 -->|"Não / piora rápida"| C5(["Antecipar retorno 24–72 h<br/>ou PS se surgir alarme"])
  D4 -->|"Sim"| C6(["Retorno acordado + orientação<br/>escrita de alarmes<br/>Sem doses neste fluxograma"])

  classDef conduta fill:#eef6ef,stroke:#2f7a4f,color:#12301f;
  classDef alerta fill:#fdecea,stroke:#b3261e,color:#3b0a0a;
  class C1,C5 alerta;
  class C2,C3,C4,C6 conduta;
```

## Notas

- **D1** = gate de segurança (suspender + labs / PS).
- **D2** = SAMS comum → reexposição (StatinWISE / EAS).
- **D3** = não-resolução → especialidade (anti-HMGCR).
- Não decide doses nem o próximo hipolipemiante não estatínico.

## Conteúdo CorVIA conectado

- [Sinalizadores de SAMS: quando suspender e escalar exames](/biblioteca/sinalizadores-ambulatoriais-sams-quando-suspender-e-escalar-labs)
- [Intolerância a estatina: definição e protocolo de reexposição](/biblioteca/intolerancia-a-estatina-definicao-operacional-e-protocolo-de-reexposicao-eas-2015)
- [SAMS no consultório: sinais vermelhos](/biblioteca/sams-no-consultorio-sinais-vermelhos-quando-ir-ao-ps)
