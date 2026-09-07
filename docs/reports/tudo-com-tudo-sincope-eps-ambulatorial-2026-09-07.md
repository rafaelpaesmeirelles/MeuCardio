# Tudo-com-Tudo — Síncope: EPS / ILR / CDI ambulatorial (além #859) — 2026-09-07

## Escopo

Lacuna fina **além de #859** (sinalizadores pós-alta / pós-avaliação / gate trabalho-direção):
**quando referir eletrofisiologia** na síncope recorrente inexplicada; árvore **EPS vs ILR vs PS**; gate **candidatos à avaliação de CDI** após síncope (ausente em main).

## Pivô / anti-colisão

- `#859` = destino pós-alta baixo risco (PS vs retorno precoce vs plano estável).
- Fluxograma ILR em main cobre Holter/loop/ILR, menciona EPS só de passagem — faltava o **gate ambulatorial de encaminhamento a EP** e o **gate CDI**.
- `#882` = HO geriátrica (outra pasta) — não usado como pivô ortostático vs reflexo.
- `#835` = disfunção de eletrodo/choque em CDI **já implantado** — distinto de candidatura pós-síncope.
- Open PRs re-checados até **#891+**; único Síncope ambulatory aberto = **#859** (tema distinto).
- Slugs novos (livres em main): `sinalizadores-ambulatoriais-sincope-recorrente-inexplicada-quando-referir-eletrofisiologia`, `fluxograma-ambulatorial-sincope-recorrente-eps-versus-ilr-destino`, `candidatos-ambulatoriais-avaliacao-cdi-apos-sincope-quando-encaminhar`.

## Arquivos

| Arquivo | Kind |
|---|---|
| `content/Síncope/sinalizadores-ambulatoriais-sincope-recorrente-inexplicada-quando-referir-eletrofisiologia.md` | protocolo |
| `content/Síncope/fluxograma-ambulatorial-sincope-recorrente-eps-versus-ilr-destino.md` | fluxograma |
| `content/Síncope/candidatos-ambulatoriais-avaliacao-cdi-apos-sincope-quando-encaminhar.md` | protocolo |

Todos: `review_status: pendente_revisao`, `fonte_producao: grok`, PT, **sem doses**, **sem auto-merge**.

## Fontes (reais)

- ESC 2018 syncope — PMID **29562304**, DOI 10.1093/eurheartj/ehy037
- Practical Instructions ESC 2018 — DOI 10.1093/eurheartj/ehy071 (sem PMID inventado)
- ACC/AHA/HRS 2017 syncope — PMID **28280231**, DOI 10.1161/CIR.0000000000000499

## Branch

`grok/tudo-com-tudo-sincope-eps-ambulatorial-20260907` → `main`
