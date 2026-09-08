---
title: "Fluxograma: pré-RM com CIED no ambulatório — destino"
slug: fluxograma-pre-rm-com-cied-destino-ambulatorial
theme: "Dispositivos"
kind: fluxograma
fonte_producao: grok
summary: "Árvore curta de destino quando o consultório recebe pedido de RM em portador de marca-passo/CDI/TRC: urgência clínica, integridade do sistema, condicional vs legado e encaixe com centro de dispositivos — sem substituir o documento de evidência MagnaSafe/Nazarian."
review_status: pendente_revisao
review_note: "Irmão do checklist-ambulatorial-pre-rm-em-portador-de-cied-destino (07/09/2026). Além do PR #835. PMIDs 28225684, 29281579, 28502708."
source_refs:
  - "Russo RJ, Costa HS, Silva PD, et al. Assessing the Risks Associated with MRI in Patients with a Pacemaker or Defibrillator. N Engl J Med. 2017;376(8):755-764. DOI: 10.1056/NEJMoa1603265. PMID: 28225684"
  - "Nazarian S, Hansford R, Rahsepar AA, et al. Safety of Magnetic Resonance Imaging in Patients with Cardiac Devices. N Engl J Med. 2017;377(26):2555-2564. DOI: 10.1056/NEJMoa1604267. PMID: 29281579"
  - "Indik JH, Gimbel JR, Abe H, et al. 2017 HRS expert consensus statement on magnetic resonance imaging and radiation exposure in patients with cardiovascular implantable electronic devices. Heart Rhythm. 2017;14(7):e97-e153. DOI: 10.1016/j.hrthm.2017.04.025. PMID: 28502708"
---

# Fluxograma: pré-RM com CIED no ambulatório — destino

Prosa: [`checklist-ambulatorial-pre-rm-em-portador-de-cied-destino`](checklist-ambulatorial-pre-rm-em-portador-de-cied-destino.md). Braço urgente: [`rm-urgente-em-portador-de-cied-quando-nao-esperar-o-centro`](rm-urgente-em-portador-de-cied-quando-nao-esperar-o-centro.md). Evidência: [`ressonancia-magnetica-em-pacientes-com-marcapasso-ou-cdi-nao-condicional-o-registro-magnasafe`](ressonancia-magnetica-em-pacientes-com-marcapasso-ou-cdi-nao-condicional-o-registro-magnasafe.md).

## Árvore de decisão

```mermaid
flowchart TD
  A["Consulta: paciente com CIED e pedido de RM"] --> D1{"A RM é clinicamente urgente<br/>(muda conduta em horas)?"}

  D1 -->|"Sim"| C1(["Via hospitalar / PS com protocolo CIED agora<br/>Não cancelar só por ‘legado’ — ver braço urgente"])

  D1 -->|"Não — eletiva"| D2{"Há alerta de eletrodo, erosão/infecção de bolsa,<br/>choques recentes ou instabilidade?"}

  D2 -->|"Sim"| C2(["Tratar a via clínica prioritária primeiro<br/>(eletrodo #835 / infecção / emergência)<br/>Remarcar RM após estabilizar"])

  D2 -->|"Não"| D3{"Sistema documentado como RM-condicional<br/>e pedido dentro do rótulo (em geral 1,5 T)?"}

  D3 -->|"Sim"| C3(["Agendar RM com slot de interrogação pré/pós<br/>Retorno curto ao centro se o serviço exigir<br/>equipe de dispositivos no dia"])

  D3 -->|"Não / desconhecido / legado"| D4{"Há eletrodo abandonado, fraturado<br/>ou epicárdico permanente conhecido?"}

  D4 -->|"Sim ou dúvida"| C4(["Encaminhar ao centro de CIED / EP<br/>antes de liberar o exame eletivo"])

  D4 -->|"Não — sistema íntegro aparente"| C5(["Encaminhar a serviço com protocolo HRS/MagnaSafe<br/>1,5 T preferencial; reprogramação + monitorização<br/>obrigatórias — não ‘liberar sem protocolo’"])

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
