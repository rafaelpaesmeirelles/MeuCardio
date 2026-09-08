---
title: "Fluxograma ambulatorial: sinalizadores pós-UTI cardiológica — PS vs retorno precoce vs plano"
slug: fluxograma-ambulatorial-sinalizadores-pos-uti-cardiologia-destino
theme: "Terapia intensiva"
kind: fluxograma
fonte_producao: grok
summary: "Árvore de destino após alta de UTI/UCO ou choque cardiogênico: gate de alarme (hipoperfusão, congestão aguda, infecção, dispositivo, neurológico), braço de piora ambulatorial com retorno precoce, e braço estável com plano — sem doses."
review_status: pendente_revisao
review_note: "Irmão dos protocolos pós-UTI sinalizadores 07/09/2026. PIVOT: lacuna destino ambulatorial pós-alta UTI/choque. Anti-colisão #826–858; não reescreve SCAI/vasoativos/MCS. Fontes: HFA/ESC CS PMID 32469155; ESC HF 2021 PMID 34447992. Sem doses."
source_refs:
  - "Chioncel O, Parissis J, Mebazaa A, et al. Epidemiology, pathophysiology and contemporary management of cardiogenic shock – a position statement from the Heart Failure Association of the European Society of Cardiology. Eur J Heart Fail. 2020;22(8):1315-1341. DOI: 10.1002/ejhf.1922. PMID: 32469155"
  - "McDonagh TA, Metra M, Adamo M, et al. 2021 ESC Guidelines for the diagnosis and treatment of acute and chronic heart failure. Eur Heart J. 2021;42(36):3599-3726. DOI: 10.1093/eurheartj/ehab368. PMID: 34447992"
---

# Fluxograma ambulatorial: sinalizadores pós-UTI cardiológica — destino

Prosa: [`sinalizadores-ambulatoriais-pos-uti-choque-cardiogenico-quando-escalar`](sinalizadores-ambulatoriais-pos-uti-choque-cardiogenico-quando-escalar.md). Quatro eixos: [`sinalizadores-ambulatoriais-pos-alta-uti-infeccao-dispositivo-ic-cognicao`](sinalizadores-ambulatoriais-pos-alta-uti-infeccao-dispositivo-ic-cognicao.md).

## Árvore de decisão

```mermaid
flowchart TD
  R0["Consulta / teleatendimento<br/>pós-alta UTI/UCO ou pós-choque"] --> D1{"Alarme imediato?<br/>hipoperfusão / congestão aguda<br/>sepse / sítio agressivo<br/>alarme dispositivo / déficit focal"}

  D1 -->|"Sim ou dúvida fundamentada"| C1(["PS / urgência AGORA<br/>Avisar time UTI/UCO se possível<br/>Não ajustar em casa"])

  D1 -->|"Não"| D2{"Piora ambulatorial?<br/>IC leve-moderada / infecção sem sepse<br/>dúvida de dispositivo / PICS com impacto"}

  D2 -->|"Sim"| P1["História focada nos 4 eixos<br/>Precipitantes + exame dirigido"]
  P1 --> C2(["Retorno precoce<br/>IC avançada / rede se trajetória pós-choque<br/>Sem inventar doses neste fluxo"])

  D2 -->|"Não"| D3{"Estável?<br/>sem febre, sem congestão progressiva<br/>sem alarme de dispositivo"}

  D3 -->|"Sim"| C3(["Plano escrito de alarmes<br/>Retorno programado + continuidade IC"])
  D3 -->|"Não / dúvida"| C4(["Retorno curto prudente<br/>ou cardiologia / IC avançada"])

  C2 --> D4{"Acesso a reavaliação OK<br/>e sem piora em horas?"}
  D4 -->|"Não / piora"| C5(["Antecipar PS<br/>se surgir alarme da tabela"])
  D4 -->|"Sim"| C6(["Completar investigação dirigida<br/>Não esperar retorno longo de rotina"])

  classDef conduta fill:#eef6ef,stroke:#2f7a4f,color:#12301f;
  classDef alerta fill:#fdecea,stroke:#b3261e,color:#3b0a0a;
  class C1,C5 alerta;
  class C2,C3,C4,C6 conduta;
```

## Notas

- **D1** = gate de segurança (hipoperfusão, congestão aguda, infecção grave, dispositivo, neurológico).
- **D2** = piora ambulatorial nos eixos infecção / dispositivo / IC / cognição → retorno precoce (HFA/ESC organização de cuidado; ESC HF 2021 continuidade).
- **Não decide** doses, vasoativos, indicação de MCS nem estadiamento SCAI.
