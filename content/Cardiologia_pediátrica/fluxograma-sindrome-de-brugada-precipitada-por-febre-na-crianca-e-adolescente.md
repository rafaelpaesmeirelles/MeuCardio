---
title: "Fluxograma: Brugada precipitada por febre na criança/adolescente"
slug: fluxograma-sindrome-de-brugada-precipitada-por-febre-na-crianca-e-adolescente
theme: "Cardiologia pediátrica"
kind: fluxograma
summary: "Árvore de emergência para febre em paciente pediátrico com Brugada conhecido ou padrão tipo 1, com antitermia, telemetria e tratamento de TV/FV."
review_status: revisado
source_refs: ["Zeppenfeld K, Tfelt-Hansen J, de Riva M, et al. 2022 ESC Guidelines for ventricular arrhythmias. Eur Heart J. 2022;43(40):3997-4126. DOI: 10.1093/eurheartj/ehac262.", "Michowitz Y, et al. Heart Rhythm. 2018. PMID: 29649615.", "Relatos de caso isolados, não uma diretriz graduada, cada um descrito com precisão: menina de 10 anos com tempestade de FV pós-fechamento cirúrgico de CIA, tratada com quinina IV (diastereômero da quinidina) por indisponibilidade de quinidina — PMID 21040093; adolescente com síndrome de Brugada maligna, 15 episódios de FV em 10 dias após implante de CDI, controlado com quinidina oral 1000mg/dia por 18 meses de seguimento — PMID 15189543 (não é o mesmo caso nem a mesma fonte do anterior — corrigido no Lote 1B-correção, que havia atribuído esse caso à referência errada, PMC3433527).", "Peltenburg PJ, Hoedemaekers YM, Clur SB, et al. Screening, diagnosis and follow-up of Brugada syndrome in children: a Dutch expert consensus statement. Neth Heart J. 2023;31(4):133-137 (publicação eletrônica em 2022). DOI: 10.1007/s12471-022-01723-6. PMID: 36223066 — consenso de especialistas pediátricos (não é diretriz da ESC): recomenda isoproterenol em infusão para arritmias ventriculares/tempestade elétrica; TV monomórfica durante febre pode ser tratada com betabloqueador; quinidina pode ser considerada em pacientes altamente sintomáticos, reconhecendo evidência pediátrica limitada. O texto integral não contém a regra de substituir isoproterenol por betabloqueador especificamente em variante de SCN5A de fenótipo rate/use-dependente com elevação de ST ou aumento de PR/QRS — essa formulação foi retirada no Lote 1B-correção (2026-08-24) por não ter lastro nesta fonte."]
review_note: "Lote 1B-correção (2026-08-24): corrige a atribuição do caso do adolescente (era PMC3433527, é PMID 15189543) e descreve com precisão o caso PMID 21040093 (menina de 10 anos, quinina IV, não quinidina). Corrigido em nova rodada de correção (2026-08-24): a citação de Heart Rhythm 2018 tinha o autor errado (era 'Gaita F et al.', é Michowitz Y et al., PMID 29649615); a citação de Peltenburg et al. corrigida para Neth Heart J. 2023;31(4):133-137 (publicação eletrônica em 2022); e removida a regra de substituição isoproterenol→betabloqueador em variante SCN5A rate/use-dependent com elevação de ST/PR/QRS, que não consta no texto integral do consenso — mantido só o que o consenso de fato recomenda (isoproterenol para arritmia ventricular/tempestade elétrica, betabloqueador para TV monomórfica febril, quinidina em paciente muito sintomático com evidência pediátrica limitada). Sem dose fixa, por não existir posologia pediátrica robustamente validada por diretriz graduada. Pendente de validação médica final."
---

# Brugada + febre

```mermaid
flowchart TD
  R0["Criança/adolescente com febre<br/>+ Brugada conhecido ou ECG suspeito"]
  P1["Antitermia imediata + ECG<br/>+ eletrólitos + tratar causa da febre"]
  D1{"Síncope, TV/FV, choque<br/>ou padrão tipo 1 de alto risco?"}
  P2["Telemetria/UTI conforme gravidade;<br/>eletrofisiologia pediátrica"]
  D2{"TV/FV ou PCR?"}
  C1(["Sim: cardioversão/desfibrilação<br/>+ PCR pediátrica se necessário"])
  D3{"Tempestade elétrica/<br/>choques recorrentes?"}
  P3["Considerar isoproterenol/quinidina<br/>sob EP/UTI; dose depende de fenótipo,<br/>idade, peso — VERIFICAÇÃO HUMANA NECESSÁRIA"]
  P4["Sem evento grave: controlar febre,<br/>repetir ECG após defervescência"]
  D4{"Padrão tipo 1/sintomas persistem<br/>ou houve evento arrítmico?"}
  C2(["Sim: avaliação especializada<br/>de risco, genética e ICD quando indicado"])
  C3(["Não: orientação de febre/fármacos<br/>e seguimento cardiológico"])

  R0 --> P1
  P1 --> D1
  D1 -->|"Sim"| P2
  D1 -->|"Não"| P4
  P2 --> D2
  D2 -->|"Sim"| C1
  D2 -->|"Não"| D3
  C1 --> D3
  D3 -->|"Sim"| P3
  D3 -->|"Não"| D4
  P3 --> D4
  P4 --> D4
  D4 -->|"Sim"| C2
  D4 -->|"Não"| C3

  classDef conduta fill:#eef6ef,stroke:#2f7a4f,color:#12301f;
  class C1,C2,C3 conduta;
```

## Regra prática

**Na criança com Brugada, febre é parte da arritmia.** Trate a temperatura como gatilho elétrico e monitore o coração enquanto trata a infecção.

Em criança com Brugada, o consenso pediátrico holandês (Peltenburg et al.) recomenda isoproterenol em infusão para arritmias ventriculares ou tempestade elétrica. Taquicardia ventricular monomórfica durante febre pode ser tratada com betabloqueador. Quinidina pode ser considerada em pacientes altamente sintomáticos, reconhecendo-se que a evidência pediátrica é limitada — reforçado pelos relatos de caso isolados citados em `source_refs`, cada um descrito com precisão, sem generalizar como diretriz graduada. A escolha e a dose devem ser definidas por eletrofisiologia pediátrica; este documento não estabelece dose fixa.