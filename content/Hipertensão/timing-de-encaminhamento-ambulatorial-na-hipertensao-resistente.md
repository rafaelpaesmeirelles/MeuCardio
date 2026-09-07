---
title: "Timing de encaminhamento ambulatorial na hipertensão resistente: quando ficar, quando referir cedo e quando é urgente"
slug: timing-de-encaminhamento-ambulatorial-na-hipertensao-resistente
theme: "Hipertensão"
kind: protocolo
fonte_producao: grok
summary: "Consultório: depois do gate PS vs retorno precoce (#828) e além do mapa de destino da suspeita de secundária (#865) — escada de timing para hipertensão resistente verdadeira: o que ainda cabe no ambulatório, quando encaminhar ao centro de HAS de rotina, quando antecipar, e o que não é resistência a referir. Sem doses."
review_status: pendente_revisao
review_note: "PIVOT 07/09/2026: lacuna TIMING de encaminhamento na hipertensão resistente ambulatorial, além de #828 (alarme/PS) e #865 (destino da secundária). Não reescreve pseudo×verdadeira, PATHWAY-2/quarta droga nem hub #597. Fontes: ESC 2024 PMID 39210715; SBC 2025 PMID 41294179; Carey AHA 2018 PMID 30354828; BIHS referral 2024 PMID 38196000; BIHS RH 2024 PMID 39653728. Sem doses; sem PMID inventado."
source_refs:
  - "McEvoy JW, McCarthy CP, Bruno RM, et al. 2024 ESC Guidelines for the management of elevated blood pressure and hypertension. Eur Heart J. 2024;45(38):3912-4018. DOI: 10.1093/eurheartj/ehae178. PMID: 39210715"
  - "Brandão AA, Rodrigues CIS, Bortolotto LA, et al. Diretriz Brasileira de Hipertensão Arterial – 2025. Arq Bras Cardiol. 2025;122(9):e20250624. DOI: 10.36660/abc.20250624. PMID: 41294179"
  - "Carey RM, Calhoun DA, Bakris GL, et al. Resistant Hypertension: Detection, Evaluation, and Management: A Scientific Statement From the American Heart Association. Hypertension. 2018;72(5):e53-e90. DOI: 10.1161/HYP.0000000000000084. PMID: 30354828"
  - "Lewis P, George J, Kapil V, et al. Adult hypertension referral pathway and therapeutic management: British and Irish Hypertension Society position statement. J Hum Hypertens. 2024;38(1):3-7. DOI: 10.1038/s41371-023-00882-2. PMID: 38196000"
  - "Faconti L, et al. Investigation and management of resistant hypertension: British and Irish Hypertension Society position statement. J Hum Hypertens. 2024. DOI: 10.1038/s41371-024-00983-6. PMID: 39653728"
---

# Timing de encaminhamento ambulatorial na hipertensão resistente

Pergunta de **consultório**: este paciente rotulado (ou confirmado) como **hipertensão resistente** precisa de **encaminhamento ao centro/especialista de HAS agora**, pode **seguir no ambulatório com retorno curto**, ou o problema ainda é **pseudorresistência**?

**Fora de escopo deliberado:**
- tabela de lesão aguda / PA ≥180 sem lesão aguda → [`sinais-de-alarme-ambulatoriais-na-hipertensao-quando-encaminhar`](sinais-de-alarme-ambulatoriais-na-hipertensao-quando-encaminhar.md) e [#828](https://github.com/rafaelpaesmeirelles/MeuCardio/pull/828);
- mapa de destino da **suspeita de secundária** (endocrino/nefrologia/sono) → [#865](https://github.com/rafaelpaesmeirelles/MeuCardio/pull/865);
- exclusão passo a passo de pseudorresistência → [`hipertensao-resistente-verdadeira-versus-pseudorresistente-tecnica-adesao-avental-branco`](hipertensao-resistente-verdadeira-versus-pseudorresistente-tecnica-adesao-avental-branco.md);
- algoritmo da quarta droga / doses → [`fluxograma-hipertensao-resistente-quarta-droga`](fluxograma-hipertensao-resistente-quarta-droga.md) e Cap. 12 SBC 2025.

Árvore: [`fluxograma-timing-encaminhamento-ambulatorial-hipertensao-resistente`](fluxograma-timing-encaminhamento-ambulatorial-hipertensao-resistente.md). Ponte enquanto espera: [`ponte-ambulatorial-enquanto-espera-centro-has-na-resistente`](ponte-ambulatorial-enquanto-espera-centro-has-na-resistente.md).

## Princípio

**Resistente verdadeira não é sinônimo automático de "encaminhar hoje".** SBC 2025 (PMID 41294179) recomenda acompanhamento idealmente em **centros especializados**; Carey/AHA 2018 (PMID 30354828) aconselha referir ao especialista se a PA permanece não controlada após otimização; BIHS 2024 (PMID 38196000 / 39653728) separa **encaminhamento de emergência** (lesão aguda) de **encaminhamento de rotina** (resistente / secundária / polifarmácia complexa) e enfatiza não abandonar o paciente na fila.

## Escada de timing (ambulatório)

| Degrau | Situação | Timing |
|---|---|---|
| 0 | Técnica / adesão / jaleco branco ainda não excluídos | **Não referir como resistente** — corrigir primeiro (docs de pseudorresistência + MAPA/MRPA) |
| 1 | Resistente verdadeira confirmada; serviço local tem capacidade de otimizar tripla + 4ª linha e monitorar K+/função renal | **Pode ficar no ambulatório** com retorno curto; referir se falhar ou se complexidade subir |
| 2 | Resistente verdadeira + necessidade de expertise (painel de secundária além do serviço; polifarmácia complexa; dúvida de adesão objetiva) | **Encaminhamento de rotina** ao centro de HAS / especialista |
| 3 | Refratária (≥5 fármacos não controlada) ou candidata a denervação / procedimento | **Antecipar** encaminhamento especializado (SBC Cap. 12 / fluxograma local) |
| PS | Lesão aguda de órgão-alvo ou dúvida fundamentada de emergência | **PS agora** — [#828](https://github.com/rafaelpaesmeirelles/MeuCardio/pull/828), não fila de HAS |

## Quando ficar no ambulatório (degrau 1)

1. Pseudorresistência já excluída (técnica + adesão + MAPA/MRPA).
2. Esquema triplo adequado documentado ≥30 dias (definição SBC/Carey).
3. Equipe local segura para otimização da 4ª linha **sem inventar dose neste documento** — ver fluxograma/PATHWAY-2 da pasta.
4. Retorno curto combinado; orientação escrita dos alarmes (#828).

## Quando encaminhar de rotina (degrau 2)

- PA não controlada após confirmação de resistente verdadeira e otimização local razoável (Carey 2018; BIHS 2024).
- Suspeita de secundária que ultrapassa o serviço — articular com [#865](https://github.com/rafaelpaesmeirelles/MeuCardio/pull/865), não duplicar o mapa endocrino/nefrologia.
- Polifarmácia complexa, interações, ou necessidade de tipagem objetiva de adesão (urina/DOT) indisponível no local (BIHS RH PMID 39653728).
- SBC 2025: preferência por centro especializado com equipe multidisciplinar.

## Quando antecipar (degrau 3)

- Hipertensão **refratária** (não controlada com ≥5 classes adequadas) — SBC Cap. 12; fluxograma local aponta centro para avaliar denervação.
- Lesão de órgão-alvo progressiva **sem** critério de emergência — não esperar fila longa.
- Fragilidade / barreiras de acesso que tornam o "retorno curto" inviável — documentar e antecipar referência.

## O que NÃO é timing de "resistente"

- Déficit neurológico, dor torácica/dorsal súbita, oligúria aguda, alarme obstétrico → **PS** (#828).
- PA ≥180/110 sem lesão aguda → oral + retorno precoce (#828); só depois reavaliar se é resistente verdadeira.
- Encaminhar como "resistente" sem MAPA/MRPA e sem checar adesão → engorda fila e atrasa o diagnóstico real.

## Checklist de 90 segundos

1. Alarme de lesão aguda? → **#828 / PS**.
2. Pseudorresistência excluída? → se não, **degrau 0**.
3. Capacidade local de otimizar + monitorar? → **degrau 1** com retorno curto.
4. Falhou otimização / secundária complexa / polifarmácia? → **degrau 2** (rotina).
5. Refratária / denervação / LOA progressiva? → **degrau 3** (antecipar).
6. Dose / escolha da 4ª droga? → **não este documento**.

## Armadilhas

Referir antes de MAPA; tratar fila de HAS como substituto de PS; abandonar o paciente após encaminhar; confundir destino de secundária (#865) com timing de resistente (este doc).

## Limite da evidência

Diretrizes e statements definem **quando** referir ao especialista; o prazo exato em dias é organizacional (rede local). Intervalos de retorno enquanto espera são prudência clínica — ver doc irmão de ponte ambulatorial.
