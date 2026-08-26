---
title: "Fluxograma: Takotsubo associado ao câncer e terapia antineoplásica"
slug: fluxograma-sindrome-de-takotsubo-associada-ao-cancer-e-terapia-antineoplasica
theme: "Cardio-oncologia"
kind: fluxograma
summary: "Árvore de decisão para suspeita de Takotsubo em paciente oncológico, excluindo SCA e overlap com miocardite por ICI."
review_status: revisado
source_refs: ["Lyon AR, López-Fernández T, Couch LS, et al. 2022 ESC Guidelines on cardio-oncology. Eur Heart J. 2022;43(41):4229-4361. DOI: 10.1093/eurheartj/ehac244. PMID: 36017568."]
review_note: "Revisado em 26/08/2026 contra a seção de Takotsubo relacionado ao câncer, a Figura 29 e a Tabela de Recomendação 27 da diretriz ESC 2022 de cardio-oncologia (PMID 36017568). Corrigido o ramo que encaminhava toda pessoa em ICI ao protocolo de miocardite: o papel da imunossupressão no TTS associado a ICI permanece desconhecido; metilprednisolona IV é recomendada quando a CMR demonstra inflamação miocárdica no padrão de TTS. Mantidas exclusão de SCA, interrupção temporária do agente causal e prevenção de fármacos que prolongam QT. Se o tratamento causal for reiniciado após recuperação, foram incluídos biomarcadores antes de cada ciclo de ICI e TTE diante de nova elevação. Pendente revisão médica independente antes de uso assistencial."
---

# Takotsubo associado ao câncer

```mermaid
flowchart TD
  R0["Paciente oncológico com dor torácica,<br/>alteração ECG/troponina ou nova disfunção VE"]
  P1["ECG + TTE + troponina/NP<br/>+ monitorização + CMR quando possível"]
  D1{"SCA obstrutiva ainda precisa<br/>ser excluída?"}
  P2["Coronariografia invasiva;<br/>CCTA se invasiva contraindicada"]
  D2{"Padrão compatível com TTS<br/>e coronárias sem causa suficiente?"}
  C1(["Não: migrar para diagnóstico identificado<br/>SCA/miocardite/CTRCD/etc."])
  P3["Sim: interromper temporariamente<br/>o tratamento oncológico causal"]
  D3{"Paciente em ICI E CMR demonstra<br/>inflamação miocárdica em padrão de TTS?"}
  P4["Metilprednisolona IV + avaliar overlap<br/>e seguir protocolo de miocardite por ICI"]
  P5["Evitar fármacos QT-prolongadores;<br/>corrigir eletrólitos e monitorar arritmias"]
  D4{"Choque/IC grave?"}
  P6["Tratamento hemodinâmico guiado por eco;<br/>verificar obstrução dinâmica de VSVE"]
  C2(["Repetir imagem até recuperação;<br/>rechallenge apenas após discussão MDT.<br/>Se ICI reiniciado: cTn/NP antes de cada ciclo"])

  R0 --> P1
  P1 --> D1
  D1 -->|"Sim"| P2
  D1 -->|"Não"| D2
  P2 --> D2
  D2 -->|"Não"| C1
  D2 -->|"Sim"| P3
  P3 --> D3
  D3 -->|"Sim"| P4
  D3 -->|"Não"| P5
  P4 --> P5
  P5 --> D4
  D4 -->|"Sim"| P6
  D4 -->|"Não"| C2
  P6 --> C2

  classDef conduta fill:#eef6ef,stroke:#2f7a4f,color:#12301f;
  class C1,C2 conduta;
```

## Regra prática

No câncer, TTS precisa ser separado de **SCA e miocardite por ICI** antes de ser tratado como simples disfunção ventricular por estresse. Se houver nova elevação de troponina ou peptídeo natriurético após reinício do ICI, repetir TTE. Inflamação miocárdica deve seguir o [fluxograma de miocardite por ICI](fluxograma-miocardite-por-inibidor-de-checkpoint-imune-emergencia-esc-2025.md); exposição ao ICI sem inflamação não basta para indicar imunossupressão.
