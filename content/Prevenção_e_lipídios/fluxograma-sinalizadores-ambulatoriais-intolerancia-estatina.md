---
title: "Fluxograma: sinalizadores ambulatoriais de intolerância a estatina — PS vs. reexposição vs. especialista"
slug: fluxograma-sinalizadores-ambulatoriais-intolerancia-estatina
theme: "Prevenção e lipídios"
kind: fluxograma
fonte_producao: grok
summary: "Árvore ambulatorial: SAMS no consultório — gate de PS (rabdomiólise/fraqueza), via eletiva de CK/reexposição EAS e encaminhamento neuromuscular quando a CK não cai."
review_status: pendente_revisao
review_note: "Árvore irmã dos protocolos SAMS ambulatoriais (07/09/2026), complementar ao fluxograma revisado de definição/reexposição EAS e à #894. Stroes PMID 25694464; Mach PMID 31504418; Newman PMID 30580575. Sem doses."
source_refs:
  - "Stroes ES, Thompson PD, Corsini A, et al.; European Atherosclerosis Society Consensus Panel. Statin-associated muscle symptoms: impact on statin therapy—European Atherosclerosis Society Consensus Panel Statement on Assessment, Aetiology and Management. Eur Heart J. 2015;36(17):1012-1022. DOI: 10.1093/eurheartj/ehv043. PMID: 25694464"
  - "Mach F, Baigent C, Catapano AL, et al.; ESC Scientific Document Group. 2019 ESC/EAS Guidelines for the management of dyslipidaemias: lipid modification to reduce cardiovascular risk. Eur Heart J. 2020;41(1):111-188. DOI: 10.1093/eurheartj/ehz455. PMID: 31504418"
  - "Newman CB, Preiss D, Tobert JA, et al. Statin Safety and Associated Adverse Events: A Scientific Statement From the American Heart Association. Arterioscler Thromb Vasc Biol. 2019;39(2):e38-e81. DOI: 10.1161/ATV.0000000000000073. PMID: 30580575"
---

# Fluxograma: sinalizadores ambulatoriais de intolerância a estatina

Prosa: [`sams-no-consultorio-sinais-vermelhos-quando-ir-ao-ps`](sams-no-consultorio-sinais-vermelhos-quando-ir-ao-ps.md) e [`sinalizadores-ambulatoriais-de-intolerancia-a-estatina-quando-escalar`](sinalizadores-ambulatoriais-de-intolerancia-a-estatina-quando-escalar.md). Definição/reexposição EAS: [`intolerancia-a-estatina-definicao-operacional-e-protocolo-de-reexposicao-eas-2015`](intolerancia-a-estatina-definicao-operacional-e-protocolo-de-reexposicao-eas-2015.md) e [`fluxograma-intolerancia-a-estatina-definicao-e-protocolo-de-reexposicao`](fluxograma-intolerancia-a-estatina-definicao-e-protocolo-de-reexposicao.md).

## Árvore de decisão

```mermaid
flowchart TD
  R0["Consulta: sintoma muscular<br/>em usuário de estatina"] --> D1{"Fraqueza grave, urina escura,<br/>oligúria ou quadro de<br/>rabdomiólise?"}

  D1 -->|"Sim"| C1(["PS / emergência AGORA<br/>Parar estatina<br/>Sem doses neste fluxo"])

  D1 -->|"Não"| D2{"CK disponível?"}

  D2 -->|"Não"| C2(["Pedir CK ± creatinina<br/>Educar alarmes<br/>Não rotular intolerante ainda"])

  D2 -->|"Sim"| D3{"CK >10× LSN?"}

  D3 -->|"Sim"| C1

  D3 -->|"Não"| D4{"CK 4–10× LSN?"}

  D4 -->|"Sim"| D5{"Alto risco CV / ASCVD?"}
  D5 -->|"Não (baixo risco)"| C3(["Suspender · reavaliar indicação<br/>Se ainda precisa: outra estatina<br/>em dose menor + CK"])
  D5 -->|"Sim"| C4(["Pode continuar com CK seriada<br/>Suspender se CK >10× LSN<br/>(EAS 2015)"])

  D4 -->|"Não (CK <4× / normal)"| D6{"Sintoma some ao parar<br/>e volta ao reexpor<br/>(≥2 ciclos; ≥2–3 esquemas)?"}

  D6 -->|"Ainda não testou"| C5(["Dechallenge-rechallenge<br/>estruturado EAS<br/>Não abandonar a classe"])
  D6 -->|"Sim — intolerância<br/>estruturada"| C6(["Dose máxima tolerada<br/>+ não-estatínico<br/>Meta LDL mantida"])
  D6 -->|"CK não cai após suspender"| C7(["Especialista neuromuscular<br/>Suspeitar anti-HMGCR"])

  classDef conduta fill:#eef6ef,stroke:#2f7a4f,color:#12301f;
  classDef alerta fill:#fdecea,stroke:#b3261e,color:#3b0a0a;
  class C1 alerta;
  class C2,C3,C4,C5,C6,C7 conduta;
```

## Notas

- **D1/D3** = gate de segurança (rabdomiólise / CK \>10× LSN) — EAS 2015 + AHA 2019.
- **D5** = mesmo intervalo 4–10× LSN muda de destino conforme risco CV (EAS).
- **C5/C6** = StatinWISE + ESC/EAS 2019: reexpor antes do rótulo; depois, não abandonar meta de LDL.
- **C7** = fora do espectro SAMS comum — ver documento anti-HMGCR.
- Não decide doses, nem cascata HF (#894), nem AINE (#887).
