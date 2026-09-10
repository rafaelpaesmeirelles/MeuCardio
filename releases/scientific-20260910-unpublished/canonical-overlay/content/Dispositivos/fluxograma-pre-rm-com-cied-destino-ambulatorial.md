---
slug: fluxograma-pre-rm-com-cied-destino-ambulatorial
title: 'Fluxograma: pré-RM com CIED no ambulatório — destino'
kind: fluxograma
theme: Dispositivos
summary: 'Árvore curta de destino quando o consultório recebe pedido de RM em portador de marca-passo/CDI/TRC: urgência
  clínica, integridade do sistema, condicional vs legado e encaixe com centro de dispositivos — sem substituir o
  documento de evidência MagnaSafe/Nazarian.'
tags: []
source_refs:
- 'Kim D et al. SCMR expert consensus statement for cardiovascular magnetic resonance of patients with a cardiac
  implantable electronic device. J Cardiovasc Magn Reson. 2024;26:100995. DOI: 10.1016/j.jocmr.2024.100995. PMID:
  38219955.'
- 'Russo RJ, Costa HS, Silva PD, et al. Assessing the Risks Associated with MRI in Patients with a Pacemaker or
  Defibrillator. N Engl J Med. 2017;376(8):755-764. DOI: 10.1056/NEJMoa1603265. PMID: 28225684'
- 'Nazarian S, Hansford R, Rahsepar AA, et al. Safety of Magnetic Resonance Imaging in Patients with Cardiac Devices.
  N Engl J Med. 2017;377(26):2555-2564. DOI: 10.1056/NEJMoa1604267. PMID: 29281579'
- 'Indik JH, Gimbel JR, Abe H, et al. 2017 HRS expert consensus statement on magnetic resonance imaging and radiation
  exposure in patients with cardiovascular implantable electronic devices. Heart Rhythm. 2017;14(7):e97-e153. DOI:
  10.1016/j.hrthm.2017.04.025. PMID: 28502708'
evidence_level: null
source_tier: A
review_status: revisado
gaps: []
published: false
---

# Fluxograma: pré-RM com CIED no ambulatório — destino

Prosa: [`checklist-ambulatorial-pre-rm-em-portador-de-cied-destino`](/biblioteca/checklist-ambulatorial-pre-rm-em-portador-de-cied-destino). Braço urgente: [`rm-urgente-em-portador-de-cied-quando-nao-esperar-o-centro`](/biblioteca/rm-urgente-em-portador-de-cied-quando-nao-esperar-o-centro). Evidência: [`ressonancia-magnetica-em-pacientes-com-marcapasso-ou-cdi-nao-condicional-o-registro-magnasafe`](/biblioteca/ressonancia-magnetica-em-pacientes-com-marcapasso-ou-cdi-nao-condicional-o-registro-magnasafe).

## Árvore de decisão

```mermaid
flowchart TD
  A["Consulta: paciente com CIED e pedido de RM"] --> D1{"A RM é clinicamente urgente<br/>(muda conduta em horas)?"}

  D1 -->|"Sim"| C1(["Via hospitalar/radiologia + dispositivos agora<br/>Não cancelar só por ‘legado’ — ver braço urgente"])

  D1 -->|"Não — eletiva"| D2{"Há alerta de eletrodo, erosão/infecção de bolsa,<br/>choques recentes ainda não avaliados ou instabilidade?"}

  D2 -->|"Sim"| C2(["Tratar a via clínica prioritária primeiro<br/>(disfunção de eletrodo / infecção / emergência)<br/>Remarcar RM após estabilizar"])

  D2 -->|"Não"| D3{"Sistema completo (gerador e eletrodos)<br/>documentado como RM-condicional<br/>e pedido dentro do rótulo (1,5 T e/ou 3 T conforme rótulo completo)?"}

  D3 -->|"Sim"| C3(["Agendar RM com slot de interrogação pré/pós<br/>Programação de RM obrigatória antes do exame<br/>equipe de dispositivos no dia"])

  D3 -->|"Não / desconhecido / legado"| D4{"Há eletrodo abandonado, fraturado<br/>ou epicárdico permanente conhecido?"}

  D4 -->|"Sim ou dúvida"| C4(["Encaminhar ao centro de CIED / EP<br/>antes de liberar o exame eletivo"])

  D4 -->|"Não — sistema íntegro aparente"| C5(["Encaminhar a serviço com protocolo HRS/MagnaSafe<br/>1,5 T recomendado para não condicionais; reprogramação + monitorização<br/>obrigatórias — não ‘liberar sem protocolo’"])

  classDef conduta fill:#eef6ef,stroke:#2f7a4f,color:#12301f;
  classDef alerta fill:#fdecea,stroke:#b3261e,color:#3b0a0a;
  class C1,C2 alerta;
  class C3,C4,C5 conduta;
```

## O que a árvore não decide

- Modo de estimulação (DOO/VOO vs ODO) no dia do exame.
- Se desligar ou não terapias de CDI minuto a minuto.
- Se 3 T é aceitável no caso concreto.
- Extração de eletrodo abandonado só para viabilizar RM.

Essas decisões ficam com o centro de dispositivos e com a radiologia sob o consenso HRS (PMID 28502708).

## Lembrete de evidência

Segurança em legado a 1,5 T foi demonstrada **com protocolo** (MagnaSafe PMID 28225684; Nazarian PMID 29281579). O ramo “legado íntegro” ainda exige **serviço preparado**, não alta com “pode fazer RM em qualquer clínica”.

## Segurança do processo (SCMR 2024)

Em todo sistema: interrogar antes/depois, programar modo apropriado por equipe de dispositivos, monitorizar e garantir pessoal/equipamento de resposta. Dependência orienta estratégia de estimulação; o ambulatório geral não escolhe DOO/VOO. Em CDI/TRC-D, desativar terapias de taquicardia durante exame e restaurá-las obrigatoriamente após. RM urgente não é PS automaticamente: a doença subjacente define emergência; organizar hospital/radiologia e equipe de CIED sem substituir RM clinicamente superior por TC apenas pela etiqueta do aparelho.

[Disfunção de eletrodo](/biblioteca/fluxograma-disfuncao-de-eletrodo-fratura-e-falha-de-isolamento-conduta) · [Choque inapropriado de CDI](/biblioteca/fluxograma-choque-inapropriado-de-cdi-investigacao-e-manejo).
