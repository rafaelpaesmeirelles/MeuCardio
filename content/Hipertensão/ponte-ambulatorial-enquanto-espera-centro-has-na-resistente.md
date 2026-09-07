---
title: "Ponte ambulatorial enquanto espera o centro de HAS na hipertensão resistente"
slug: ponte-ambulatorial-enquanto-espera-centro-has-na-resistente
theme: "Hipertensão"
kind: protocolo
fonte_producao: grok
summary: "Depois de decidir encaminhar (timing deste pacote): o que o ambulatório continua fazendo na fila — retorno curto, checklist do que anexar à referência, alarmes (#828), e o que não abandonar — sem inventar regimes farmacológicos."
review_status: pendente_revisao
review_note: "Doc 3/3 do pacote timing de encaminhamento na resistente (07/09/2026), além de #828/#865. Alinhado a BIHS referral PMID 38196000 (o que fazer enquanto espera) e Carey PMID 30354828. Sem doses."
source_refs:
  - "Lewis P, George J, Kapil V, et al. Adult hypertension referral pathway and therapeutic management: British and Irish Hypertension Society position statement. J Hum Hypertens. 2024;38(1):3-7. DOI: 10.1038/s41371-023-00882-2. PMID: 38196000"
  - "Carey RM, Calhoun DA, Bakris GL, et al. Resistant Hypertension: Detection, Evaluation, and Management: A Scientific Statement From the American Heart Association. Hypertension. 2018;72(5):e53-e90. DOI: 10.1161/HYP.0000000000000084. PMID: 30354828"
  - "Brandão AA, Rodrigues CIS, Bortolotto LA, et al. Diretriz Brasileira de Hipertensão Arterial – 2025. Arq Bras Cardiol. 2025;122(9):e20250624. DOI: 10.36660/abc.20250624. PMID: 41294179"
  - "McEvoy JW, McCarthy CP, Bruno RM, et al. 2024 ESC Guidelines for the management of elevated blood pressure and hypertension. Eur Heart J. 2024;45(38):3912-4018. DOI: 10.1093/eurheartj/ehae178. PMID: 39210715"
  - "Faconti L, et al. Investigation and management of resistant hypertension: British and Irish Hypertension Society position statement. J Hum Hypertens. 2024. DOI: 10.1038/s41371-024-00983-6. PMID: 39653728"
---

# Ponte ambulatorial enquanto espera o centro de HAS na hipertensão resistente

Cenário: já se decidiu **encaminhar** (degrau 2 ou 3 do [`timing-de-encaminhamento-ambulatorial-na-hipertensao-resistente`](timing-de-encaminhamento-ambulatorial-na-hipertensao-resistente.md)), mas a consulta especializada **não é imediata**. BIHS 2024 (PMID 38196000) é explícita: a fila não suspende o cuidado primário/ambulatorial.

## O que continuar fazendo

1. **Não abandonar o esquema oral** já em curso — ajustar só dentro da competência e dos docs de escalonamento da pasta; **sem doses neste protocolo**.
2. **Retorno curto** até a especialidade absorver (intervalo conforme fragilidade e acesso — prudência local, não marco inventado).
3. **MRPA domiciliar** se disponível, para não decidir só com uma medida de consultório — [`automedida-domiciliar-de-pressao-arterial-guiando-titulacao-tasminh4-e-home-bp`](automedida-domiciliar-de-pressao-arterial-guiando-titulacao-tasminh4-e-home-bp.md).
4. **Revisitar adesão e interferentes** (AINE, estimulantes, alcaçuz) a cada contato — causa frequente de "resistência" aparente.
5. **Orientação escrita dos alarmes** → PS se surgir lesão aguda ([#828](https://github.com/rafaelpaesmeirelles/MeuCardio/pull/828)).

## O que anexar à referência (checklist BIHS-inspirado)

| Item | Por quê |
|---|---|
| Lista atual de anti-hipertensivos (classes e se dose máxima tolerada) | Confirma se é resistente verdadeira |
| Resultado de MAPA e/ou MRPA | Exclui jaleco branco |
| Evidência de adesão (relato dirigido, farmácia, contagem) | Pseudorresistência |
| Creatinina, eletrólitos, K+ recentes | Segurança da 4ª linha / MRA |
| Pistas de secundária já pedidas e resultados | Evita repetir painel — ver [#865](https://github.com/rafaelpaesmeirelles/MeuCardio/pull/865) |
| LOA / eventos CV documentados | Priorização da fila |

## O que não fazer na ponte

- Transformar a espera em "observação passiva" sem retorno.
- Pedir angio renal + metanefrinas + cortisol + ARR no mesmo dia "para não atrasar" sem pista — ver mapa [#865](https://github.com/rafaelpaesmeirelles/MeuCardio/pull/865).
- Intensificar só com base em uma PA de consultório sem MAPA prévio.
- Inventar regime IV ou nifedipina sublingual de rotina no consultório.

## Quando reabrir o gate de PS durante a espera

Qualquer novo sinal da tabela de alarme do [#828](https://github.com/rafaelpaesmeirelles/MeuCardio/pull/828) (déficit focal, dor torácica/dorsal súbita, dispneia aguda, oligúria, alarme obstétrico, crise adrenérgica) → **PS agora**, não "adiantar a consulta de HAS".

## Armadilhas

Encaminhar e sumir; mandar o paciente "em branco"; confundir fila longa com indicação de observar PA ≥180 sem plano (#828).

## Limite da evidência

BIHS 2024 (PMID 38196000) formaliza a ideia de **otimizar enquanto espera**; o conteúdo farmacológico detalhado fica nos docs de resistente da pasta e **não é reproduzido em doses aqui**.
