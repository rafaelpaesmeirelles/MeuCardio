# Tudo-com-Tudo — Cardiomiopatias: DCM aconselhamento + ACM rastreio familiar ambulatory (2026-09-07)

## Escopo

Lacuna fina **além de #844** (HCM + amiloide ambulatory) e **#862** (Chagas/CCC ambulatory): filtro de consultório para **quando referir aconselhamento genético na CMD/NDLVC** e **quando abrir/acelerar rastreamento familiar na ACM/ARVC**.

## Anti-colisão

- Não duplica #844 (HCM/amiloide/imagem-genética genérica de fenocópia).
- Não duplica #862 (Chagas indeterminada/CCC).
- Evita #849 Gravidez/PPCM (densidade ambulatory já na pasta Gravidez).
- Não edita hubs `doencas` **#689** (CMD) nem **#723** (ACM) — só `content/Cardiomiopatias/`.
- Não reescreve fluxograma EHRA genética MS já **revisado** — apenas linka.
- Busca em open PRs / main: zero slugs `sinalizadores*dcm*` / `sinalizadores*acm*` / ambulatory rastreio ACM.
- Anti-colisão através de **#887+** (outros temas overnight).

## Arquivos

| Arquivo | Kind |
|---|---|
| `content/Cardiomiopatias/sinalizadores-ambulatoriais-dcm-quando-referir-aconselhamento-genetico.md` | protocolo |
| `content/Cardiomiopatias/sinalizadores-ambulatoriais-acm-arvc-rastreamento-familiar-quando-escalar.md` | protocolo |
| `content/Cardiomiopatias/fluxograma-ambulatorial-dcm-acm-genetica-e-rastreio-familiar.md` | fluxograma |

Todos: `review_status: pendente_revisao`, `fonte_producao: grok`, PT, **sem doses**.

## Fontes (reais)

- ESC 2023 cardiomyopathies — PMID **37622657**
- EHRA/HRS/APHRS/LAHRS genetic testing 2022 — PMID **35373836**
- Wahbi et al. laminopathy risk — PMID **31155932** (só como ponte no doc DCM; sem doses/indicação CDI)
- Cadrin-Tourigny et al. ARVC risk model — PMID **30915475** (contexto; gate PS não depende da calculadora)

## Branch

`feat/tudo-com-tudo-cardiomiopatias-dcm-acm-ambulatorial-20260907` → `main`
