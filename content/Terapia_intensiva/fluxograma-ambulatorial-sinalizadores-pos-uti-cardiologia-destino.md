---
title: "Fluxograma: Seguimento pós-choque cardiogênico: destino e continuidade"
slug: fluxograma-ambulatorial-sinalizadores-pos-uti-cardiologia-destino
theme: "Terapia intensiva"
kind: fluxograma
fonte_producao: grok
summary: "Roteador pós-choque cardiogênico: instabilidade atual, continuidade individualizada e encaminhamento aos protocolos específicos de IC, dispositivos e intercorrências."
review_status: revisado
review_note: "Revisão científica/adversarial 08/09/2026: findings PR861 reconstruídos no HEAD remoto; escopo, urgência, referências e handoffs revistos; fonte grok preservada."
source_refs:
  - "Chioncel O, Parissis J, Mebazaa A, et al. Epidemiology, pathophysiology and contemporary management of cardiogenic shock – a position statement from the Heart Failure Association of the European Society of Cardiology. Eur J Heart Fail. 2020;22(8):1315-1341. DOI: 10.1002/ejhf.1922. PMID: 32469155"
  - "McDonagh TA, Metra M, Adamo M, et al. 2021 ESC Guidelines for the diagnosis and treatment of acute and chronic heart failure. Eur Heart J. 2021;42(36):3599-3726. DOI: 10.1093/eurheartj/ehab368. PMID: 34447992"
---

# Seguimento pós-choque cardiogênico

```mermaid
flowchart TD
 A["Retorno após choque cardiogênico"] --> B{"Instabilidade ou ameaça aguda?"}
 B -->|Sim| C["Emergência imediata"]
 B -->|Não| D{"Intercorrência específica ou piora?"}
 D -->|Sim| E["Protocolo específico + reavaliação prioritária"]
 D -->|Não| F["Continuidade individualizada com equipe de referência"]
 E --> G{"Acesso em prazo seguro?"}
 G -->|Não| H["Via de urgência"]
 G -->|Sim| F
```

## Aplicação

Aplicar os critérios do protocolo irmão antes de escolher o ramo. Estabilidade atual, evolução e acesso determinam o prazo; o fluxograma não estabelece doses nem substitui o algoritmo específico.

## Navegação

- [`sinalizadores-ambulatoriais-pos-uti-choque-cardiogenico-quando-escalar`](/biblioteca/sinalizadores-ambulatoriais-pos-uti-choque-cardiogenico-quando-escalar)
- [`sinalizadores-ambulatoriais-pos-alta-uti-infeccao-dispositivo-ic-cognicao`](/biblioteca/sinalizadores-ambulatoriais-pos-alta-uti-infeccao-dispositivo-ic-cognicao)

## Limites

HFA/ESC 2020 e ESC IC 2021 sustentam organização e continuidade cardiológica. Diagnóstico de PICS e regras próprias de CIED/MCS foram retirados; intercorrências usam documentos canônicos, sem nova relação forte por similaridade de tema.
