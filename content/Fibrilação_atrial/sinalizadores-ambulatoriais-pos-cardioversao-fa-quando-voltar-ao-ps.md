---
title: "Sinalizadores ambulatoriais pós-cardioversão de FA: quando voltar ao pronto-socorro"
slug: sinalizadores-ambulatoriais-pos-cardioversao-fa-quando-voltar-ao-ps
theme: "Fibrilação atrial"
kind: protocolo
fonte_producao: grok
summary: "Pacote operacional pós-cardioversão elétrica ou química de FA: quais sintomas no consultório/telefone pedem retorno imediato ao PS (AVC/AIT, instabilidade, congestão aguda, isquemia, bradiarritmia sintomática), quais pedem retorno precoce por recorrência estável, e o que pode seguir com plano — sem doses e sem reabrir anticoagulação peri."
review_status: pendente_revisao
review_note: "PIVOT 07/09/2026: lacuna ambulatorial PÓS-CARDIOVERSÃO (retorno ao PS) em Fibrilação_atrial. Além de #827 (anticoag pós-ablação/DRC) e #852 (falha de frequência/IC + complicação pós-ablação). Não reescreve cardioversao-eletiva-e-anticoagulacao-periprocedimento-esc-2024 nem fluxograma peri. Fontes: ESC AF 2024 PMID 39210723; SBC/SOBRAC 2025 PMID 41294177. Sem doses; sem PMID inventado."
source_refs:
  - "Van Gelder IC, Rienstra M, Bunting KV, et al. 2024 ESC Guidelines for the management of atrial fibrillation developed in collaboration with the EACTS. Eur Heart J. 2024;45(36):3314-3414. DOI: sabidamente 10.1093/eurheartj/ehae176. PMID: 39210723"
  - "Cintra FD, Pisani CF, Rezende AGS, et al. Diretriz Brasileira de Fibrilação Atrial – 2025. Arq Bras Cardiol. 2025;122(9):e20250618. DOI: 10.36660/abc.20250618. PMID: 41294177"
---

# Sinalizadores ambulatoriais pós-cardioversão de FA: quando voltar ao PS

Este protocolo responde a uma pergunta de **consultório / teleatendimento / retorno precoce** após **cardioversão** (elétrica ou química, eletiva ou de início recente já estabilizada): **quais sintomas exigem pronto-socorro agora**, quais pedem **reavaliação ambulatorial precoce** (recorrência sem instabilidade), e o que pode **seguir com plano escrito**.

**Fora de escopo deliberado:** escolha de via peri-procedimento (3 semanas vs TEE), doses de anticoagulante, bridge, e decisão de manter anticoagulação além da janela peri — ver [`cardioversao-eletiva-e-anticoagulacao-periprocedimento-esc-2024`](cardioversao-eletiva-e-anticoagulacao-periprocedimento-esc-2024.md) e [`fluxograma-cardioversao-eletiva-anticoagulacao-periprocedimento`](fluxograma-cardioversao-eletiva-anticoagulacao-periprocedimento.md). Anticoagulação pós-ablação/DRC — [#827](https://github.com/rafaelpaesmeirelles/MeuCardio/pull/827). Falha de frequência / sintomas novos de IC / complicação pós-ablação — [#852](https://github.com/rafaelpaesmeirelles/MeuCardio/pull/852).

Não substitui:
- FA de início recente no PS (wait-and-see vs precoce) — [`wait-and-see-versus-cardioversao-precoce-na-fa-de-inicio-recente-race-7-acwas`](wait-and-see-versus-cardioversao-precoce-na-fa-de-inicio-recente-race-7-acwas.md);
- pill-in-the-pocket — [`pill-in-the-pocket-cardioversao-quimica-ambulatorial-na-fa-de-inicio-recente`](pill-in-the-pocket-cardioversao-quimica-ambulatorial-na-fa-de-inicio-recente.md);
- AF-CARE / hub ESC — [`esc-2024-diretriz-fibrilacao-atrial-af-care`](esc-2024-diretriz-fibrilacao-atrial-af-care.md).

Árvore: [`fluxograma-ambulatorial-pos-cardioversao-fa-destino`](fluxograma-ambulatorial-pos-cardioversao-fa-destino.md). Braço recorrência estável: [`recorrencia-leve-pos-cardioversao-fa-retorno-precoce-nao-ps`](recorrencia-leve-pos-cardioversao-fa-retorno-precoce-nao-ps.md).

## Princípio

**Sucesso imediato da cardioversão não equivale a “alta sem alarmes”.** ESC 2024 AF-CARE (PMID 39210723) e SBC/SOBRAC 2025 (PMID 41294177) enquadram cardioversão no contexto de risco tromboembólico peri, estabilidade clínica e reavaliação dinâmica (braço **E**). No ambulatorial, o primeiro filtro é **sintoma de alarme neurológico / hemodinâmico / congestivo / isquêmico**, não o “ECG já mostrou sinus”.

Este documento **não protocola miligramas** nem decide suspender ou reiniciar anticoagulação.

## Sinalizadores → PS / urgência agora

| Domínio | Sinais |
|---|---|
| Neurológico / embolia | Déficit focal, fala alterada, amaurose, confusão súbita, cefaleia em trovão com déficit — tratar como via AVC/AIT |
| Hemodinâmico | Hipotensão sintomática, síncope / pré-síncope recorrente, choque, confusão por baixo débito |
| Congestão aguda | Dispneia súbita, ortopneia nova, edema agudo de pulmão, saturação baixa nova |
| Isquemia | Dor torácica anginosa em curso, equivalente isquêmico pós-procedimento |
| Bradiarritmia / condução | Bradicardia sintomática grave, pausas, BAV avançado suspeito (especialmente após estratégia química recente) — **não** “só ajustar em casa” |
| Sangramento maior | Sangramento ativo com instabilidade / hematoma expansivo (contexto peri / anticoagulado) — estabilizar via PS; **não** decidir bridge neste texto |
| Recorrência com instabilidade | FA (ou flutter) de retorno **com** qualquer linha acima |

**Conduta:** orientar PS; documentar ECG/sinais vitais quando disponíveis; avisar o serviço que cardioverteu quando possível. **Não improvisar doses** nem suspender anticoagulação peri neste protocolo.

## Sem alarme de PS → retorno precoce / plano

1. Recorrência de FA/flutter **sem** instabilidade, sem congestão aguda, sem déficit → ver braço [`recorrencia-leve-pos-cardioversao-fa-retorno-precoce-nao-ps`](recorrencia-leve-pos-cardioversao-fa-retorno-precoce-nao-ps.md).
2. Lembrar a janela de **atordoamento atrial** e a regra peri de anticoagulação pós-cardioversão — apontar o documento peri; **não** “liberar sem anticoagulante porque o ritmo voltou”.
3. Orientação escrita dos alarmes da tabela + canal de retorno.
4. Se a pergunta for só anticoagulação / dose / 4 semanas → **documento peri**, não este.

## Pode seguir com plano (retorno habitual)

- Ritmo estável, assintomático ou com sintomas leves estáveis, sem congestão, sem déficit, com educação de alarmes e plano peri já definido no documento de anticoagulação.
- Ajuste de estilo de vida / comorbidade em curso, sem red flag.

Ainda assim: qualquer linha da tabela → PS.

## Checklist de 90 segundos

1. Déficit neurológico / congestão aguda / instabilidade / isquemia / bradi sintomática grave? → **PS agora**.
2. Recorrência de FA sem instabilidade? → **retorno precoce** (não este = “só esperar meses”).
3. Pergunta de anticoagular / 4 semanas / dose? → **documento peri de cardioversão**, não este.
4. Ablação recente + alarme estrutural? → pacote pós-ablação (#852), não este.
5. Não inventar miligramas neste texto.

## Armadilhas

Tratar toda palpitação pós-CVE como emergência; atrasar PS por “é só recorrência do blanking da cardioversão”; suspender anticoagulação porque o ECG está em sinus; confundir este pacote com complicação pós-ablação; usar este texto para decidir CHA₂DS₂-VA ou dose de DOAC.

## Limite da evidência

ESC 2024 e SBC 2025 orientam **princípios** de segurança peri e reavaliação — não um limiar único de horas que separe sempre PS de retorno após cardioversão ambulatorial. O destino combina sintoma, estabilidade e contexto — não o “sucesso” isolado no traçado da alta.

## Slugs relacionados (existentes)

- `cardioversao-eletiva-e-anticoagulacao-periprocedimento-esc-2024`
- `fluxograma-cardioversao-eletiva-anticoagulacao-periprocedimento`
- `wait-and-see-versus-cardioversao-precoce-na-fa-de-inicio-recente-race-7-acwas`
- `pill-in-the-pocket-cardioversao-quimica-ambulatorial-na-fa-de-inicio-recente`
- `esc-2024-diretriz-fibrilacao-atrial-af-care`
- `diretriz-brasileira-de-fibrilacao-atrial-2025-sbc-sobrac`
- `controle-de-ritmo-vs-frequencia-na-fibrilacao-atrial-affirm-east-afnet-4-e-castle-af`
