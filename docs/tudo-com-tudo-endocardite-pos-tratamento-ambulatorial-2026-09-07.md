# Tudo-com-Tudo — Endocardite: sinalizadores ambulatoriais pós-tratamento (2026-09-07)

## Escopo / pivô

**Alvo:** densificar `content/Endocardite` com **FOLLOW-UP ambulatorial pós-EI** (alarmes → PS/hemoculturas + educação odontológica **sem regimes**), **além** do pacote de **suspeita** pré-diagnóstico (**#853**).

**Por que não outros gaps sugeridos:**
- Febre + prótese ambulatorial de **suspeita** → já em **#853**.
- Disfunção de prótese valvar ambulatorial → **#866** (Valvopatias), não Endocardite.
- Profilaxia odontológica com regimes → já densa em main; aqui só **counseling/coordenação**.

## Anti-colisão

- Listagem de `content/Endocardite/`: sem slugs prévios de pós-tratamento/follow-up ambulatorial operacional.
- PRs abertos Endocardite sinalizadores: só **#853** (suspeita). Nenhum pós-tratamento até #887+.
- Não toca: Duke, esquemas por agente, timing cirúrgico/AVC, profilaxia com doses, definições longas de relapso/reinfecção (slug existente; linkado).
- Não compete com **#866** (Valvopatias).

## Arquivos

| Arquivo | Slug | Kind |
|---|---|---|
| `content/Endocardite/sinalizadores-ambulatoriais-pos-tratamento-endocardite-quando-escalar.md` | `sinalizadores-ambulatoriais-pos-tratamento-endocardite-quando-escalar` | protocolo |
| `content/Endocardite/fluxograma-ambulatorial-pos-tratamento-endocardite-destino.md` | `fluxograma-ambulatorial-pos-tratamento-endocardite-destino` | fluxograma |
| `content/Endocardite/checklist-ambulatorial-pos-ei-higiene-oral-e-alarmes.md` | `checklist-ambulatorial-pos-ei-higiene-oral-e-alarmes` | protocolo |

Todos com `review_status: pendente_revisao`, `fonte_producao: grok`.

## Fontes (somente PMID conferido)

- ESC 2023 endocarditis PMID **37622656** (Delgado et al., Eur Heart J; DOI 10.1093/eurheartj/ehad193) — follow-up pós-alta, educação, higiene oral, recidiva.

Sem PMID inventado. Sem doses/regimens.

## Branch

`feat/tudo-com-tudo-endocardite-pos-tratamento-ambulatorial-20260907` → `main`
