---
title: "Fluxograma: endocardite infecciosa na gestação e puerpério"
slug: fluxograma-endocardite-infecciosa-na-gestacao-e-puerperio
theme: "Gravidez"
kind: fluxograma
summary: "Árvore de emergência para suspeita de endocardite na gestante/puérpera, integrando culturas, eco, antibiótico e decisão cirúrgica materno-fetal."
review_status: revisado
review_note: "Revisado contra a seção 12.5.4 e a seção de cirurgia cardíaca da ESC 2025 (PMID 40878294), além da ESC 2023 de endocardite (PMID 37622656). Corrigida mistura de população: a puérpera não segue decisão de viabilidade fetal/parto antes da cirurgia nem monitorização materno-fetal; após o parto, mantém critérios maternos usuais de antibiótico e cirurgia, com revisão de compatibilidade na lactação."
source_refs: ["De Backer J, Haugaa KH, Hasselberg NE, et al. 2025 ESC Guidelines for the management of cardiovascular disease and pregnancy. DOI: 10.1093/eurheartj/ehaf193. PMID: 40878294.", "Delgado V, Ajmone Marsan N, de Waha S, et al. 2023 ESC Guidelines for the management of endocarditis. DOI: 10.1093/eurheartj/ehad193. PMID: 37622656."]
---

# Endocardite infecciosa na gestação/puerpério

```mermaid
flowchart TD
  R0["Gestante/puérpera com suspeita de EI<br/>febre/bacteremia + sopro, embolia,<br/>IC ou prótese/dispositivo"]
  P1["Hemoculturas + TTE/TEE conforme indicação<br/>+ Endocarditis Team + Pregnancy Heart Team"]
  D1{"Sepse/choque ou deterioração rápida?"}
  P2["Antibiótico empírico imediato<br/>após culturas se possível sem atraso"]
  P3["Estável: culturas antes do antibiótico<br/>e estratificação anatômica/microbiológica"]
  D2{"IC por lesão valvar, infecção não controlada,<br/>abscesso ou alto risco embólico com indicação cirúrgica?"}
  D4{"Gestação em curso<br/>ou puerpério?"}
  C1(["Gestação: antibiótico dirigido<br/>+ monitorização materno-fetal"])
  C4(["Puerpério: antibiótico dirigido + monitorização<br/>materna; revisar compatibilidade com lactação"])
  P4["Sim: cirurgia cardíaca precisa<br/>ser discutida imediatamente"]
  D5{"Gestação em curso<br/>ou puerpério?"}
  D3{"Feto viável e parto antes da cirurgia<br/>é seguro para a mãe?"}
  C2(["Sim: considerar parto antes da cirurgia<br/>conforme equipe e capacidade neonatal"])
  C3(["Não: priorizar cirurgia materna<br/>sem atraso indevido"])
  C5(["Puerpério: aplicar a indicação cirúrgica materna<br/>sem ramo obstétrico nem atraso por decisão de parto"])

  R0 --> P1
  P1 --> D1
  D1 -->|"Sim"| P2
  D1 -->|"Não"| P3
  P2 --> D2
  P3 --> D2
  D2 -->|"Não"| D4
  D4 -->|"Gestação"| C1
  D4 -->|"Puerpério"| C4
  D2 -->|"Sim"| P4
  P4 --> D5
  D5 -->|"Gestação"| D3
  D5 -->|"Puerpério"| C5
  D3 -->|"Sim"| C2
  D3 -->|"Não"| C3

  classDef conduta fill:#eef6ef,stroke:#2f7a4f,color:#12301f;
  class C1,C2,C3,C4,C5 conduta;
```

## Regra prática

A gestação muda a escolha do antimicrobiano e o planejamento de cirurgia/parto,
mas **não deve reduzir a urgência de tratar EI com insuficiência cardíaca, sepse
ou complicação estrutural grave**. No puerpério, já não existe decisão de parto
ou monitorização fetal: aplicam-se os critérios maternos de cirurgia da
endocardite, acrescentando apenas a reconciliação do antimicrobiano com a
lactação quando houver amamentação.
