# Tudo-com-Tudo — Perioperatório: sintomas cardíacos pós-op ambulatoriais (2026-09-07)

## Escopo

Lacuna fina **além de #836** (sinalizadores ambulatoriais **pré-op** / adiar eletiva / janela stent): **destino ambulatorial pós-cirurgia não cardíaca** — sintomas cardíacos → PS agora vs. retorno precoce vs. seguimento após MINS — **sem doses**.

Não densifica RCRI, DAPT/stent timing, nem a árvore hospitalar completa de MINS.

## Anti-colisão

- **#836** Perioperatório pré-op (adiar eletiva, escalar, stent ambulatorial) — ângulo diferente (pré vs pós).
- Existentes: `mins-lesao-miocardica-pos-operatoria-vigilancia-e-arvore-de-decisao`, `fluxograma-mins-lesao-miocardica-pos-operatoria`, `sbc-2024-monitorizacao-troponina-ecg-bnp-pos-operatorio`, `fibrilacao-atrial-perioperatoria-pos-operatoria-arvore-aha-acc-2024`.
- Search PRs abertos (Perioperatório / MINS / pós-op ambulatorial): sem pacote aberto com este framing de **sintomas pós-alta → destino**.
- Evita reabrir #826–869 de outros hubs; não toca bridge com doses (#860 DOAC é Farmacologia).

## Arquivos

| Arquivo | Slug | Kind |
|---|---|---|
| `content/Perioperatório/sinalizadores-ambulatoriais-sintomas-cardiacos-pos-cirurgia-nao-cardiaca-quando-encaminhar.md` | `sinalizadores-ambulatoriais-sintomas-cardiacos-pos-cirurgia-nao-cardiaca-quando-encaminhar` | protocolo |
| `content/Perioperatório/fluxograma-ambulatorial-sintomas-cardiacos-pos-operatorios-destino.md` | `fluxograma-ambulatorial-sintomas-cardiacos-pos-operatorios-destino` | fluxograma |
| `content/Perioperatório/mins-apos-alta-seguimento-ambulatorial-alarme-e-retorno.md` | `mins-apos-alta-seguimento-ambulatorial-alarme-e-retorno` | protocolo |

Todos com `review_status: pendente_revisao`.

## Fontes (PMIDs conferidos)

- AHA/ACC 2024 perioperatório PMID **39316661**
- ESC 2022 non-cardiac surgery PMID **36017553**
- VISION JAMA 2017 PMID **28444280**
- MANAGE Lancet 2018 PMID **29900874** (citado; **sem doses** neste pacote)
- SBC 2024 DOI **10.36660/abc.20240590**

Sem PMID inventado. Sem auto-merge.

## Branch

`feat/tudo-com-tudo-perioperatorio-sintomas-pos-op-ambulatorial-20260907` → `main`
