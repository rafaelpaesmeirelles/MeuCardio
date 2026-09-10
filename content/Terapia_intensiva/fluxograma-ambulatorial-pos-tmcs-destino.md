---
slug: fluxograma-ambulatorial-pos-tmcs-destino
title: 'Fluxograma ambulatorial: pós-tMCS — PS vs avaliação vascular vs reavaliação pós-ponte'
kind: fluxograma
theme: Terapia intensiva
summary: 'Árvore pós-explante de tMCS: gates independentes de hipoperfusão, congestão, isquemia/arritmia, complicação
  vascular e continuidade com o time implantador/IC avançada.'
tags: []
source_refs:
- 'Møller JE, Sionis A, Aissaoui N, et al. ACVC/ESC short-term MCS consensus. PMID: 37315190'
- 'Sinha SS, Morrow DA, Kapur NK, Kataria R, Roswell RO. ACC cardiogenic shock guidance 2025. PMID: 40100174'
- 'Chioncel O, Parissis J, Mebazaa A, et al. HFA/ESC cardiogenic shock statement. PMID: 32469155'
- 'McDonagh TA, Metra M, Adamo M, et al. ESC HF 2021. PMID: 34447992'
evidence_level: null
source_tier: A
review_status: revisado
gaps: []
published: true
---

# Fluxograma ambulatorial: pós-tMCS — destino

```mermaid
flowchart TD
  R0["Após desmame/explante de tMCS"] --> D1{"Hipoperfusão, congestão aguda,<br/>isquemia miocárdica, arritmia instável<br/>ou déficit neurológico?"}
  D1 -->|"Sim/dúvida"| C1(["PS / urgência AGORA"])

  D1 -->|"Não"| D2{"Complicação vascular grave?<br/>sangramento/hematoma expansivo · isquemia de membro<br/>sepse · ou pós-femoral large-bore:<br/>dor flanco/lombar/abdome, distensão ou hipotensão inexplicada"}
  D2 -->|"Sim"| C2(["PS / emergência vascular<br/>suspeitar hemorragia retroperitoneal mesmo com virilha seca"])

  D2 -->|"Não"| D3{"Alteração local de acesso sem alarme?<br/>dor/equimose, pseudoaneurisma/trombose suspeitos"}
  D3 -->|"Sim"| C3["Avaliação vascular/de acesso precoce<br/>considerar tipo e local do dispositivo"]
  C3 --> D4

  D3 -->|"Não"| D4{"Trajetória pós-ponte preocupante?<br/>congestão leve/moderada, queda funcional,<br/>bridge-to-decision sem plano"}
  D4 -->|"Sim"| C4(["Reavaliação prioritária com time implantador<br/>ou programa local de IC avançada/choque"])

  C4 --> D5{"Reavaliação acessível e quadro estável?"}
  D5 -->|"Não / piora"| C5(["Rota alternativa presencial urgente<br/>serviço de referência ou PS conforme gravidade"])
  D5 -->|"Sim"| C6(["Completar investigação dirigida<br/>sem inferir LVAD/transplante/novo tMCS"])

  D4 -->|"Não"| C7(["Plano escrito + seguimento já definido<br/>com cardiologia/time responsável"])

  classDef alerta fill:#fdecea,stroke:#b3261e,color:#3b0a0a;
  classDef conduta fill:#eef6ef,stroke:#2f7a4f,color:#12301f;
  class C1,C2,C5 alerta;
  class C3,C4,C6,C7 conduta;
```

## Limite
Este é um fluxo operacional de segurança pós-alta; não há protocolo universal ambulatorial pós-tMCS diretamente validado nos consensos citados. Não decide dispositivo, doses, LVAD/transplante ou reimplantação de tMCS.

## Continuidade e avaliação dirigida

Alteração do acesso e piora cardíaca podem coexistir: organizar avaliação vascular e cardiológica em paralelo. Suspeita de pseudoaneurisma/trombose exige exame e imagem dirigidos com prioridade; não esperar consulta rotineira. A ausência de sangramento externo não exclui hemorragia retroperitoneal. Sem acesso rápido à avaliação necessária, usar serviço presencial urgente.

[Complicações do acesso large-bore](/biblioteca/acesso-vascular-large-bore-em-tmcs-prevencao-de-sangramento-isquemia-e-fechamento) · [Seguimento após ponte](/biblioteca/seguimento-ambulatorial-pos-tmcs-ponte-temporaria-quando-escalar).
