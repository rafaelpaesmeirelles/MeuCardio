---
title: "Fluxograma: Síndrome aórtica aguda na gestação e no puerpério"
slug: fluxograma-sindrome-aortica-aguda-na-gestacao-e-puerperio
theme: "Gravidez"
kind: fluxograma
summary: "Árvore de decisão para suspeita de dissecção aórtica na gestante/puérpera, distinguindo tipo A, que exige cirurgia urgente, do tipo B inicialmente médico salvo complicações."
review_status: revisado
review_note: "Revisão de 26/08/2026 contra a seção 8.5 e cirurgia cardíaca na ESC 2025, mantendo ACC/AHA 2022 para a lógica tipo A/tipo B. Removida decisão fixa por trimestre: cesárea antes da cirurgia passou a depender de viabilidade fetal, estabilidade materna e capacidade do centro, como orienta a ESC 2025. Explicitado que parto não deve atrasar reparo tipo A quando não for seguro/viável e que suspeita de síndrome aórtica aguda justifica baixo limiar para TC de aorta."
source_refs: ["De Backer J, Haugaa KH, Hasselberg NE, et al.; ESC Scientific Document Group. 2025 ESC Guidelines for the management of cardiovascular disease and pregnancy. Eur Heart J. 2025;46(43):4462-4568. DOI: 10.1093/eurheartj/ehaf193. PMID: 40878294.", "Isselbacher EM, Preventza O, Black JH 3rd, et al. 2022 ACC/AHA Guideline for the Diagnosis and Management of Aortic Disease. Circulation. 2022;146(24):e334-e482. DOI: 10.1161/CIR.0000000000001106. PMID: 36322642. PMCID: PMC9876736."]
---

# Síndrome aórtica aguda na gestação/puerpério

```mermaid
flowchart TD
  R0["Gestante ou puérpera com dor abrupta intensa,<br/>assimetria de pulsos/PA, síncope, déficit neurológico,<br/>choque ou aortopatia conhecida + sintomas"]
  P1["ABC + monitorização + analgesia + estratégia anti-impulso;<br/>acionar equipe de aorta + Pregnancy Heart Team;<br/>baixo limiar para TC de aorta; não atrasar imagem definitiva"]
  D1{"Síndrome aórtica aguda confirmada?"}
  C1(["Não: investigar SCAD/SCA, TEP, PPCM,<br/>causas obstétricas e demais diagnósticos"])
  D2{"Dissecção tipo A?"}
  D0{"Gestação em curso<br/>ou puerpério?"}
  D3{"Feto viável e cesárea pode ser realizada<br/>antes da cirurgia sem atraso materno inseguro,<br/>em centro com capacidade?"}
  C2(["Considerar cesárea imediatamente antes<br/>da cirurgia aórtica; coordenar duas equipes<br/>e minimizar atraso do reparo materno"])
  C3(["Cirurgia aórtica urgente sem parto prévio;<br/>monitorização fetal quando factível;<br/>não atrasar reparo tipo A por corte gestacional fixo"])
  C4(["Puerpério: cirurgia aórtica urgente<br/>conforme protocolo de tipo A e equipe de aorta"])
  D4{"Tipo B com complicação aguda?<br/>ruptura, malperfusão ou deterioração clínica/hemodinâmica"}
  C5(["Não complicada: tratamento médico inicial<br/>e monitorização intensiva — ACC/AHA Classe I C-EO"])
  C6(["Complicada: discutir intervenção endovascular/cirúrgica<br/>urgente em centro experiente, individualizando<br/>condição materna e obstétrica"])
  C7(["Após estabilização: seguimento de aortopatia,<br/>genética quando indicada e plano pós-parto"])

  R0 --> P1
  P1 --> D1
  D1 -->|"Não"| C1
  D1 -->|"Sim"| D2
  D2 -->|"Sim"| D0
  D2 -->|"Não — tipo B"| D4
  D0 -->|"Gestação"| D3
  D0 -->|"Puerpério"| C4
  D3 -->|"Sim"| C2
  D3 -->|"Não"| C3
  D4 -->|"Não"| C5
  D4 -->|"Sim"| C6
  C2 --> C7
  C3 --> C7
  C4 --> C7
  C5 --> C7
  C6 --> C7

  classDef conduta fill:#eef6ef,stroke:#2f7a4f,color:#12301f;
  class C1,C2,C3,C4,C5,C6,C7 conduta;
```

## Regra prática

**Tipo A na gestação é emergência cirúrgica. Tipo B é inicialmente médico se não complicada.** A gestação modifica a coordenação materno-fetal, não elimina a urgência da doença aórtica.

Na ESC 2025, cesárea antes de cirurgia com circulação extracorpórea reduziu
mortalidade fetal na metanálise citada, sem diferença demonstrada na mortalidade
materna. A decisão, porém, deve usar **viabilidade fetal e capacidade do centro,
não trimestre fixo**. Se o parto criar atraso ou risco materno inaceitável, o
reparo tipo A permanece prioritário.

Em suspeita de síndrome aórtica aguda, a diretriz recomenda baixo limiar para TC
de aorta e consulta à equipe especializada; a radiação não justifica reter um
exame potencialmente salvador. Tipo B não complicada recebe tratamento médico e
vigilância intensiva; ruptura, malperfusão ou deterioração exigem intervenção.

## Tudo com Tudo

- [Síndrome aórtica aguda na gestação/puerpério — revisão clínica](sindrome-aortica-aguda-na-gestacao-e-puerperio.md)
- [Síndrome aórtica aguda — ESC 2024](../Aorta_e_doença_arterial_periférica/fluxograma-sindrome-aortica-aguda-esc-2024.md)
- [SCA na gestação e puerpério](fluxograma-sindrome-coronariana-aguda-na-gestacao-e-puerperio.md)
- [TEP agudo na gestação e puerpério](fluxograma-tromboembolismo-pulmonar-agudo-na-gestacao-e-puerperio-esc-2025.md)
- [Cardiomiopatia periparto descompensada](fluxograma-cardiomiopatia-periparto-descompensada-e-choque-no-puerperio-esc-2025.md)
