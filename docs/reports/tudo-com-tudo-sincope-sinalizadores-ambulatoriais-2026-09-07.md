# Tudo-com-Tudo — Síncope: sinalizadores ambulatoriais pós-avaliação (2026-09-07)

## Escopo

Lacuna fina: **destino ambulatorial após avaliação / pós-alta do DE** em síncope de baixo risco — quando retornar urgentemente vs. retorno precoce vs. plano estável; mais **gate clínico** de retorno a trabalho/direção **sem inventar regra legal**.

## Pivô / anti-colisão

- Pasta `content/Síncope/` já densa (ESC 2018, EGSYS/CSRS/SFSR, tilt/ILR, alto risco ED, HSC+direção).
- **Ângulo novo:** pós-alta ambulatorial + alarmes de retorno; não reabre escores ED nem restrições legais de direção.
- Evita PRs #826–#857 (outras áreas; Síncope skip overnight). Re-busca: nenhum PR aberto `sinalizadores*sincope*` / pós-alta ambulatorial.
- Slugs novos (livres em main): `sinalizadores-ambulatoriais-sincope-pos-alta-quando-retornar`, `fluxograma-ambulatorial-sincope-pos-avaliacao-destino`, `sincope-gate-ambulatorial-retorno-atividades-trabalho-direcao`.

## Arquivos

| Arquivo | Kind |
|---|---|
| `content/Síncope/sinalizadores-ambulatoriais-sincope-pos-alta-quando-retornar.md` | protocolo |
| `content/Síncope/fluxograma-ambulatorial-sincope-pos-avaliacao-destino.md` | fluxograma |
| `content/Síncope/sincope-gate-ambulatorial-retorno-atividades-trabalho-direcao.md` | protocolo |

Todos: `review_status: pendente_revisao`, `fonte_producao: grok`, PT, sem doses.

## Fontes (reais / corpus)

- ESC 2018 syncope — PMID 29562304, DOI 10.1093/eurheartj/ehy037
- Practical Instructions ESC 2018 — DOI 10.1093/eurheartj/ehy071 (citação como no corpus; sem PMID inventado)

## Branch

`feat/tudo-com-tudo-sincope-sinalizadores-ambulatoriais-20260907-0145` → `main`
