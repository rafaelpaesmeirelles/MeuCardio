# Tudo-com-Tudo — Tromboembolismo: sinalizadores ambulatoriais TVP (além #837) (2026-09-07)

## Escopo

Lacuna fina: **destino ambulatorial na TVP** — quando escalar à urgência (TEP associado, isquemia de membro, sangramento, falha crítica) versus caminho Wells/US versus home treatment — **além** do pacote pós-TEP do **#837**. Explicitamente **fora**: checklist pós-alta de TEP (#837); árvore Wells/D-dímero/US já publicada; escolha/doses de anticoagulante; TEV do câncer (ensaios/escolha); FA anticoag (#827/#852); Endocardite (#853).

## Pivô / anti-colisão

- Preferidos sugeridos: (1) DVT ambulatory red flags when escalate; (2) cancer-associated VTE ambulatory; (3) post-provoked VTE duration red flags; (4) PE rule-out ambulatory suspicion.
- **Escolhido:** (1) — único gap limpo: `sinalizadores` em `content/Tromboembolismo` = 0 em main; #837 cobre só pós-TEP; fluxograma Wells/US existe mas **não** é pacote de destino PS vs home treatment.
- (2) já denso (Caravaggio, Hokusai-Cancer, Khorana, AVERT/CASSINI). (3) parcialmente coberto por `fluxograma-duracao-da-anticoagulacao-apos-tev-nao-provocado` / HERDOO2 / PADIS-PE. (4) coberto por YEARS + fluxograma diagnóstico ESC.
- Open PRs Tromboembolismo ambulatory: **#837** apenas (sinalizadores pós-TEP). Evita #826–867 especialmente #837, #853, #827/#852.

## Arquivos

| Arquivo | Slug | Kind |
|---|---|---|
| `content/Tromboembolismo/sinalizadores-ambulatoriais-tvp-quando-escalar-urgencia.md` | `sinalizadores-ambulatoriais-tvp-quando-escalar-urgencia` | protocolo |
| `content/Tromboembolismo/fluxograma-sinalizadores-ambulatoriais-tvp-destino.md` | `fluxograma-sinalizadores-ambulatoriais-tvp-destino` | fluxograma |
| `content/Tromboembolismo/tvp-confirmada-no-consultorio-ambulatorial-versus-internacao.md` | `tvp-confirmada-no-consultorio-ambulatorial-versus-internacao` | protocolo |
| `docs/reports/tudo-com-tudo-tromboembolismo-tvp-sinalizadores-2026-09-07.md` | — | relatório |

Todos com `review_status: pendente_revisao`, `fonte_producao: grok`. Sem doses. Sem PMID inventado. Sem auto-merge.

## Fontes (reais)

- ASH 2018 diagnosis VTE — PMID 30482764
- ASH 2020 treatment VTE — PMID 33007077
- CHEST 2021 VTE update — PMID 34352278
- ESC/ERS 2019 PE — PMID 31504429

## Branch

`feat/tudo-com-tudo-tromboembolismo-tvp-sinalizadores-20260907` → `main`
