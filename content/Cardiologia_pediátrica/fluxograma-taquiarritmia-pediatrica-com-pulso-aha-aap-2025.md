---
title: "Fluxograma: taquiarritmia pediátrica com pulso — AHA/AAP 2025"
slug: fluxograma-taquiarritmia-pediatrica-com-pulso-aha-aap-2025
theme: "Cardiologia pediátrica"
kind: fluxograma
summary: "Árvore de decisão para TSV e taquicardia de QRS largo em lactentes e crianças com pulso, guiada por comprometimento cardiopulmonar e largura do QRS."
review_status: revisado
review_note: "Fonte primária corrigida e conferida no PubMed em 26/08/2026: a autoria canônica começa por Lasa, não Topjian; PMID, DOI, volume, suplemento e páginas foram adicionados. Mantidas as energias de cardioversão e a restrição de adenosina ao QRS largo regular e monomórfico estável, sem inserir dose farmacológica ausente nesta ficha."
source_refs: ["Lasa JJ, Dhillon GS, Duff JP, et al. Part 8: Pediatric Advanced Life Support: 2025 American Heart Association and American Academy of Pediatrics Guidelines for Cardiopulmonary Resuscitation and Emergency Cardiovascular Care. Circulation. 2025;152(16 Suppl 2):S479-S537. DOI: 10.1161/CIR.0000000000001368. PMID: 41122885. Publicação companheira em Pediatrics: DOI 10.1542/peds.2025-074351; PMID 41122862."]
---

# Taquiarritmia pediátrica com pulso

```mermaid
flowchart TD
  R0["Lactente/criança com taquicardia e pulso"]
  D1{"Há comprometimento cardiopulmonar?<br/>alteração mental, hipotensão ou choque"}
  D2{"QRS estreito e ritmo regular<br/>compatível com TSV?"}
  C1(["Cardioversão sincronizada urgente<br/>0,5–1 J/kg; se falhar, 2 J/kg.<br/>Não atrasar por antiarrítmico"])
  P1["Sem compromisso cardiopulmonar:<br/>avaliar largura e regularidade do QRS"]
  C2(["Manobra vagal apropriada à idade;<br/>se IV/IO disponível, adenosina.<br/>Se refratária, consulta especializada"])
  D3{"QRS largo?"}
  C3(["Tratar causa não arrítmica/sinusal<br/>conforme avaliação clínica"])
  D4{"QRS largo regular e monomórfico?"}
  C4(["Consulta especializada antes de antiarrítmico;<br/>adenosina pode ser útil se regular/monomórfico<br/>e sem comprometimento cardiopulmonar"])
  C5(["Consulta especializada; evitar antiarrítmico<br/>empírico sem caracterização do mecanismo<br/>quando o paciente está estável"])
  D5{"Instabilidade surgiu durante avaliação?"}
  C6(["Cardioversão sincronizada 0,5–1 J/kg;<br/>se falhar, 2 J/kg"])
  C7(["Manter monitorização e condução especializada<br/>conforme mecanismo identificado"])

  R0 --> D1
  D1 -->|"Sim"| C1
  D1 -->|"Não"| P1
  P1 --> D2
  D2 -->|"Sim"| C2
  D2 -->|"Não"| D3
  D3 -->|"Não"| C3
  D3 -->|"Sim"| D4
  D4 -->|"Sim"| C4
  D4 -->|"Não"| C5
  C4 --> D5
  C5 --> D5
  D5 -->|"Sim"| C6
  D5 -->|"Não"| C7

  classDef conduta fill:#eef6ef,stroke:#2f7a4f,color:#12301f;
  class C1,C2,C3,C4,C5,C6,C7 conduta;
```

## Regra de segurança

Na presença de comprometimento cardiopulmonar, a cardioversão sincronizada é prioritária **independentemente de o mecanismo ser supraventricular ou ventricular**. A diretriz AHA/AAP 2025 recomenda 0,5–1 J/kg inicialmente, escalando para 2 J/kg se necessário.

## Tudo com Tudo

- [Protocolo de taquiarritmia pediátrica com pulso](taquiarritmia-pediatrica-com-pulso-aha-aap-2025.md)
- [Taquicardia supraventricular no lactente e na criança](taquicardia-supraventricular-no-lactente-e-na-crianca-manejo-agudo-e-cronico.md)
- [Fluxograma de fibrilação atrial pré-excitada/WPW](fluxograma-fibrilacao-atrial-pre-excitada-wpw-na-crianca-e-adolescente.md)
- [Fluxograma de taquicardia juncional ectópica pós-operatória](fluxograma-taquicardia-juncional-ectopica-pos-operatoria-jet.md)
- [Taquicardia ventricular idiopática na criança e no adolescente](taquicardia-ventricular-idiopatica-na-crianca-e-no-adolescente-diagnostico-diferencial-manobras-e-decisao-de-tratar.md)
