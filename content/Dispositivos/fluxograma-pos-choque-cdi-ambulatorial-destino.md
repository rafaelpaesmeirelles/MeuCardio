---
title: 'Fluxograma: pós-choque de CDI no ambulatório — destino'
slug: fluxograma-pos-choque-cdi-ambulatorial-destino
theme: Dispositivos
kind: fluxograma
fonte_producao: grok
summary: 'Árvore curta de destino após choque de CDI visto no ambulatório: estabilidade, número de terapias, disponibilidade de eletrograma e pistas de
  hardware — encaminha para emergência/centro urgente ou retorno programado. Não substitui o fluxograma de investigação de choque inapropriado já existente.'
review_status: revisado
source_refs:
- 'Zeppenfeld K; Tfelt-Hansen J; de Riva M. 2022 ESC Guidelines for the management of patients with ventricular arrhythmias and the prevention of sudden
  cardiac death. Eur Heart J. 2022;43:3997. DOI: 10.1093/eurheartj/ehac262. PMID: 36017572.'
- 'Moss AJ; Schuger C; Beck CA. Reduction in inappropriate therapy and mortality through ICD programming. N Engl J Med. 2012;367:2275. DOI: 10.1056/NEJMoa1211107.
  PMID: 23131066.'
- 'Kusumoto FM; Schoenfeld MH; Wilkoff BL. 2017 HRS expert consensus statement on cardiovascular implantable electronic device lead management and extraction.
  Heart Rhythm. 2017;14:e503. DOI: 10.1016/j.hrthm.2017.09.001. PMID: 28919379.'
review_note: 'Revisão clínica e editorial focal em 08/09/2026 do PR #835, desde seu HEAD remoto. Correções e fontes verificadas registradas em docs/revisao-cientifica-pr826-859-20260908.md.
  Prazos operacionais não equivalem a recomendações normativas; preservar avaliação individual e vias de emergência.'
---

# Fluxograma: pós-choque de CDI no ambulatório — destino

Recorte deliberadamente estreito: **só o destino** após a primeira avaliação ambulatorial. A investigação completa de choque inapropriado e a árvore de disfunção de eletrodo já existem neste tema.

## Árvore de decisão

```mermaid
flowchart TD
  A["Paciente com choque de CDI avaliado no ambulatório"]
  A --> D1{"Estável, sem arritmia sustentada em curso,<br/>qualquer síncope associada, dor isquêmica ou IC aguda?"}
  D1 -->|"Não"| C1(["Encaminhar agora para emergência / unidade com telemetria"])
  D1 -->|"Sim"| D2{"Houve 2 ou mais choques (ou cascata ATP+choque) nas últimas horas?"}
  D2 -->|"Sim — terapias recorrentes; confirmar mecanismo"| C2(["Encaminhar agora ao centro de CIED / emergência; não alta ambulatorial"])
  D2 -->|"Não — choque único"| D3{"Há alerta de integridade de eletrodo, noise ou mudança abrupta de impedância na mesma janela?"}
  D3 -->|"Sim"| C3(["Encaminhar urgente ao centro de dispositivos — via disfunção de eletrodo"])
  D3 -->|"Não / desconhecido"| D4{"Eletrograma do episódio está disponível para revisão?"}
  D4 -->|"Não"| C4(["Contato e revisão do episódio no mesmo dia ou próximo dia útil; orientar retorno imediato se novo choque"])
  D4 -->|"Sim"| D5{"Leitura preliminar favorece TV/FV tratada vs. FA rápida / sobredetecção / ruído?"}
  D5 -->|"TV/FV ou indeterminado com sintomas graves"| C5(["Contato ainda hoje com EP/centro; considerar observação se primeiro evento sintomático"])
  D5 -->|"Ruído ou suspeita de falha de eletrodo, mesmo sem alerta prévio"| C3
  D5 -->|"FA rápida ou sobredetecção conhecida, sem ruído/falha e estável"| C6(["Retorno programado ao centro para reprogramação / otimização; alta com rede de alerta remoto ativa"])
  classDef conduta fill:#eef6ef,stroke:#2f7a4f,color:#12301f;
  class C1,C2,C3,C4,C5,C6 conduta;
```

## O que a árvore não decide

- Diagnóstico definitivo apropriado vs. inapropriado sem EP.
- Se desligar o choque ou indicar colete vestível.
- Antiarrítmico, ablação ou troca de gerador.

Essas decisões ficam com o centro de dispositivos e com os fluxogramas irmãos deste catálogo.

## Lembrete de evidência

Terapia inapropriada não é evento cosmético: MADIT-RIT (PMID 23131066) associou estratégias de programação a menos terapia inapropriada e menor mortalidade em prevenção primária. Por isso o ramo “inapropriado estável” ainda exige **retorno programado**, não alta definitiva sem plano.

### Terapias recorrentes e tempestade elétrica

Duas terapias próximas justificam avaliação urgente, mas não definem tempestade elétrica. A definição exige pelo menos três episódios distintos de arritmia ventricular sustentada em 24 horas, separados por pelo menos 5 minutos e requerendo intervenção. Múltiplas terapias do mesmo episódio ou choques inapropriados não satisfazem esse critério.
