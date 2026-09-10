---
slug: fluxograma-ambulatorial-capacidade-sdm-e-mas-noticias-destino
title: 'Fluxograma ambulatorial: capacidade, SDM e má notícia — pausar vs. seguir vs. retorno precoce'
kind: fluxograma
theme: Comunicação clínica
summary: 'Árvore ambulatorial: gate de capacidade/ambiente → pausar SDM; braço de má notícia com choque → retorno
  precoce; braço capacidade OK → SDM (Elwyn/AHRQ).'
tags: []
source_refs:
- 'Appelbaum PS. Clinical practice. Assessment of patients'' competence to consent to treatment. N Engl J Med. 2007;357:1834.
  DOI: 10.1056/NEJMcp074045. PMID: 17978292.'
- 'Elwyn G; Frosch D; Thomson R. Shared decision making: a model for clinical practice. J Gen Intern Med. 2012;27:1361.
  DOI: 10.1007/s11606-012-2077-6. PMID: 22618581.'
- Agency for Healthcare Research and Quality. The SHARE Approach. https://www.ahrq.gov/evidencenow/tools/share-approach.html
evidence_level: null
source_tier: A
review_status: revisado
gaps: []
published: false
---

# Fluxograma ambulatorial: capacidade, SDM e má notícia — destino

Prosa: [sinalizadores-ambulatoriais-capacidade-e-sdm-no-consultorio-cardiologico](/biblioteca/sinalizadores-ambulatoriais-capacidade-e-sdm-no-consultorio-cardiologico). Checklist: [checklist-ambulatorial-capacidade-consentimento-consulta-cardiologica](/biblioteca/checklist-ambulatorial-capacidade-consentimento-consulta-cardiologica). SPIKES (estrutura completa): [fluxograma-protocolo-spikes-mas-noticias-cardiologia](/biblioteca/fluxograma-protocolo-spikes-mas-noticias-cardiologia).

## Árvore de decisão

```mermaid
flowchart TD
 R["Decisão específica no momento atual"] --> U{"Há urgência clínica que impede adiamento?"}
 U -->|Sim| E["Suporte e avaliação no mesmo encontro;<br/>tratar causas reversíveis; equipe/representante<br/>e regras de emergência conforme lei/política local"]
 U -->|Não| A["Corrigir dor, hipoxemia, delirium, sedação,<br/>idioma, audição/visão, letramento e coerção"]
 A --> C{"Consegue compreender, apreciar,<br/>raciocinar e expressar escolha<br/>para esta decisão após suporte?"}
 C -->|Dúvida persiste| I["Avaliação clínica aprofundada/interconsulta;<br/>documentar dúvidas específicas e prazo seguro"]
 C -->|Sim| P{"Paciente deseja tempo após má notícia?"}
 P -->|Sim| T["Acolher e combinar retorno individualizado;<br/>manter plano clínico seguro"]
 P -->|Não| D{"Mais de uma opção clinicamente razoável<br/>e decisão sensível a preferências?"}
 D -->|Sim| S["SDM: choice, option e decision talk;<br/>preferências, riscos/benefícios e documentação"]
 D -->|Não| O["Consentimento informado sem menu artificial"]
```

## Interpretação da capacidade

Capacidade é específica para a decisão e o momento, não um rótulo global. Os quatro eixos orientam avaliação; uma resposta inadequada em checklist breve não comprova incapacidade. Antes de concluir, corrigir dor, hipoxemia, delirium, sedação, idioma, audição/visão, informação insuficiente, letramento, ansiedade, pressa ou coerção.

Recusa, opção de maior risco, emoção intensa ou mudança de escolha não significam incapacidade. Apreciar é aplicar a informação ao próprio caso, não concordar com a equipe. Explorar valores e informações novas; acompanhante participa conforme desejo do paciente capaz. Suspeita de violência/coerção exige proteção institucional.

Na urgência, não agendar retorno para resolver capacidade: prestar suporte, tratar causas reversíveis e escalar equipe, representante e exceções de emergência conforme lei e política local. Capacidade clínica difere de competência legal; este roteiro não estabelece regra jurídica universal.
