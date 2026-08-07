---
title: "Fluxograma: endocardite infecciosa na gestação e puerpério"
slug: fluxograma-endocardite-infecciosa-na-gestacao-e-puerperio
theme: "Gravidez"
kind: fluxograma
summary: "Árvore de emergência para suspeita de endocardite na gestante/puérpera, integrando culturas, eco, antibiótico e decisão cirúrgica materno-fetal."
review_status: revisado
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
  C1(["Não: antibiótico dirigido<br/>+ monitorização materno-fetal"])
  P4["Sim: cirurgia cardíaca precisa<br/>ser discutida imediatamente"]
  D3{"Feto viável e parto antes da cirurgia<br/>é seguro para a mãe?"}
  C2(["Sim: considerar parto antes da cirurgia<br/>conforme equipe e capacidade neonatal"])
  C3(["Não: priorizar cirurgia materna<br/>sem atraso indevido"])

  R0 --> P1
  P1 --> D1
  D1 -->|"Sim"| P2
  D1 -->|"Não"| P3
  P2 --> D2
  P3 --> D2
  D2 -->|"Não"| C1
  D2 -->|"Sim"| P4
  P4 --> D3
  D3 -->|"Sim"| C2
  D3 -->|"Não"| C3

  classDef conduta fill:#eef6ef,stroke:#2f7a4f,color:#12301f;
  class C1,C2,C3 conduta;
```

## Regra prática

A gestação muda a escolha do antimicrobiano e o planejamento de cirurgia/parto, mas **não deve reduzir a urgência de tratar EI com insuficiência cardíaca, sepse ou complicação estrutural grave**.