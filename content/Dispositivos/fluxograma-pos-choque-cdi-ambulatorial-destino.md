---
title: "Fluxograma: pós-choque de CDI no ambulatório — destino"
slug: fluxograma-pos-choque-cdi-ambulatorial-destino
theme: "Dispositivos"
kind: fluxograma
fonte_producao: grok
summary: "Árvore curta de destino após choque de CDI visto no ambulatório: estabilidade, número de terapias, disponibilidade de eletrograma e pistas de hardware — encaminha para emergência/centro urgente ou retorno programado. Não substitui o fluxograma de investigação de choque inapropriado já existente."
review_status: pendente_revisao
source_refs:
  - "Moss AJ, Schuger C, Beck CA, et al; MADIT-RIT Trial Investigators. Reduction in inappropriate therapy and mortality through ICD programming. N Engl J Med. 2012;367(24):2275-2283. PMID: 23131066"
  - "2017 HRS expert consensus statement on cardiovascular implantable electronic device lead management and extraction · Heart Rhythm · 2017 · 14(12):e503-e551 · PMID: 28919379"
---

# Fluxograma: pós-choque de CDI no ambulatório — destino

Recorte deliberadamente estreito: **só o destino** após a primeira avaliação ambulatorial. A investigação completa de choque inapropriado e a árvore de disfunção de eletrodo já existem neste tema.

## Árvore de decisão

```mermaid
flowchart TD
  A["Paciente com choque de CDI avaliado no ambulatório"]
  A --> D1{"Estável hemodinamicamente e sem síncope recorrente / dor torácica isquêmica / ICC aguda?"}
  D1 -->|"Não"| C1(["Encaminhar agora para emergência / unidade com telemetria"])
  D1 -->|"Sim"| D2{"Houve 2 ou mais choques (ou cascata ATP+choque) nas últimas horas?"}
  D2 -->|"Sim — tempestade elétrica ou terapias em salva"| C2(["Encaminhar agora ao centro de CIED / emergência; não alta ambulatorial"])
  D2 -->|"Não — choque único"| D3{"Há alerta de integridade de eletrodo, noise ou mudança abrupta de impedância na mesma janela?"}
  D3 -->|"Sim"| C3(["Encaminhar urgente ao centro de dispositivos — via disfunção de eletrodo"])
  D3 -->|"Não / desconhecido"| D4{"Eletrograma do episódio está disponível para revisão?"}
  D4 -->|"Não"| C4(["Agendar centro de CIED em dias úteis curtos; orientar retorno imediato se novo choque"])
  D4 -->|"Sim"| D5{"Leitura preliminar favorece TV/FV tratada vs. FA rápida / sobredetecção / ruído?"}
  D5 -->|"TV/FV ou indeterminado com sintomas graves"| C5(["Contato ainda hoje com EP/centro; considerar observação se primeiro evento sintomático"])
  D5 -->|"Fortemente sugestivo de inapropriado e paciente estável"| C6(["Retorno programado ao centro para reprogramação / otimização; alta com rede de alerta remoto ativa"])
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
