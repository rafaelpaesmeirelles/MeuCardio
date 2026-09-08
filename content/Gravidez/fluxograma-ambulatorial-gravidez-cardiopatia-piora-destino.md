---
title: 'Fluxograma ambulatorial: gestação/puerpério com piora cardiovascular — PS agora vs. retorno precoce vs. pregnancy heart team'
slug: fluxograma-ambulatorial-gravidez-cardiopatia-piora-destino
theme: Gravidez
kind: fluxograma
fonte_producao: grok
summary: 'Árvore ambulatorial de destino na gestante ou puérpera: gate de alarme para PS, braço de sintoma equívoco com retorno precoce, e braço de risco
  mWHO/desfecho adverso para pregnancy heart team.'
review_status: revisado
review_note: 'Revisão clínica e editorial focal em 08/09/2026 do PR #849, desde seu HEAD remoto. Correções e fontes verificadas registradas em docs/revisao-cientifica-pr826-859-20260908.md.
  Prazos operacionais não equivalem a recomendações normativas; preservar avaliação individual e vias de emergência.'
source_refs:
- 'De Backer J, Haugaa KH, Hasselberg NE, et al. 2025 ESC Guidelines for the management of cardiovascular disease and pregnancy. Eur Heart J. 2025. DOI:
  10.1093/eurheartj/ehaf193'
- 'Lindley KJ; Bello NA; Berlacher KL. Optimization of Postpartum Care for Patients With and at Risk for Premature and Long-Term Cardiovascular Disease:
  2026 ACC Expert Consensus Decision Pathway: A Report of the American College of Cardiology Solution Set Oversight Committee. J Am Coll Cardiol. 2026;.
  DOI: 10.1016/j.jacc.2025.11.001. PMID: 42171544.'
---

# Fluxograma ambulatorial: gestação/puerpério com piora — destino

Prosa: [[sinalizadores-ambulatoriais-gravidez-cardiopatia-quando-encaminhar](/biblioteca/sinalizadores-ambulatoriais-gravidez-cardiopatia-quando-encaminhar)](/biblioteca/sinalizadores-ambulatoriais-gravidez-cardiopatia-quando-encaminhar). Checklist: [[gravidez-checklist-ambulatorial-de-alarme](/biblioteca/gravidez-checklist-ambulatorial-de-alarme)](/biblioteca/gravidez-checklist-ambulatorial-de-alarme).

## Árvore de decisão

```mermaid
flowchart TD
 R["Gestação/puerpério com sintoma cardiovascular"] --> E{"Instabilidade/hipoperfusão, piora rápida,<br/>dispneia importante/hipoxemia, dor suspeita,<br/>déficit focal/convulsão, síncope/TV sustentada,<br/>PAS ≥160 OU PAD ≥110, prótese trombosada<br/>ou febre com novo sopro/embolia?"}
 E -->|Sim ou dúvida clínica relevante| PS["Emergência obstétrica/cardiológica agora;<br/>seguir protocolo específico"]
 E -->|Não| V{"Edema ou dor unilateral de membro?"}
 V -->|Sim| U["Avaliação no mesmo dia com investigação de TVP;<br/>sinais pulmonares não são necessários"]
 V -->|Não| C["Avaliar tendência, sinais vitais e hipótese clínica;<br/>exames dirigidos, não painel automático"]
 C --> S{"Sintoma leve estável e acesso seguro?"}
 S -->|Não| U
 S -->|Sim| F["Seguimento proporcional ao risco;<br/>orientações de alarme e canal de contato"]
 F --> H["mWHO 2.0 orienta Pregnancy Heart Team;<br/>transição pós-parto e prevenção no primeiro ano"]
```

## Notas

- **D1** = gate de segurança (PPCM, PA grave/eclâmpsia, SCAD/aorta, TEP, HAP — ESC 2025 + ACC 2026).
- **D2** = sintoma equívoco ambulatorial → destino clínico precoce (primeiras semanas do puerpério).
- **D3** = ponte para pregnancy heart team / transição do 1º ano (ACC 2026), **sem** decidir fármaco aqui.
- Não decide doses de anti-hipertensivo, anticoagulação, bromocriptina nem suporte avançado.

## Precisão da triagem

Hipertensão grave é PAS ≥160 OU PAD ≥110 mmHg, independentemente de sintomas: confirmar prontamente a medida correta sem atrasar atendimento hospitalar. Cefaleia grave persistente, alteração visual, dor epigástrica/HCD ou edema pulmonar são sinais de gravidade; eclâmpsia designa convulsão nesse contexto. Déficit neurológico focal, hipoperfusão, TV sustentada mesmo normotensa, hipoxemia relevante de qualquer início e piora rápida exigem avaliação imediata.

Edema simétrico isolado pode ser fisiológico. Edema/dor unilateral pede investigação de TVP no mesmo dia, sem exigir taquicardia ou hipoxemia. Suspeitar de PPCM com dispneia/ortopneia progressiva e congestão; SCAD/SCA com dor isquêmica; aorta com dor abrupta intensa; TEP com quadro respiratório/pleurítico ou sinais de TEV. Sintoma leve inespecífico sozinho não confirma essas síndromes.

mWHO 2.0 organiza planejamento e intensidade do cuidado, não determina emergência isoladamente. As janelas de duas semanas, 12 semanas e primeiro ano guiam vigilância/transição, não adiam sintomas graves nem tornam toda queixa leve emergência. Medicação, lactação e contracepção exigem consulta aos protocolos específicos.
