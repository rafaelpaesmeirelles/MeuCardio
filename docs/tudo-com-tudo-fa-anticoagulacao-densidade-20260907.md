# Tudo com Tudo — densificação FA / anticoagulação (alta prevalência), 07/09/2026

## Objetivo
Um PR pequeno de densificação clínica em `content/Fibrilação_atrial/` para dois eixos habitualmente finos no corpus narrativo, apesar da alta prevalência:

1. **FA pós-ablação — princípios de anticoagulação de retorno** (sem doses).
2. **FA e DRC — enquadramento de ajuste** (sem inventar doses) e **quando escalar**.

Fonte primária exclusiva declarada: **ESC 2024 AF Guidelines** (Van Gelder et al., Eur Heart J 2024; PMID 39210723).

## Anti-colisão
- `search_pull_requests` (is:open) para hubs FA/anticoagulação/densidade/pós-ablação/DRC: **nenhum PR aberto** tocando estes dois slugs ou o mesmo recorte de densificação.
- PR #725 (Guia de Doenças: completar Tudo com Tudo em fibrilação atrial) altera apenas overlay de `related_document_slugs` em `doencas/correcoes/` — **não** cria estes markdowns clínicos; sem sobreposição de arquivos.
- Já existentes e deliberadamente **não reescritos**: ALONE-AF (suspensão pós-ablação em selecionados), OCEAN, fluxograma de dose por função renal, FA em diálise (RENAL-AF / AXADIA). Este lote **complementa** com hubs de princípios.

## Conteúdo produzido
Dois documentos novos, ambos `review_status: pendente_revisao`, `theme: "Fibrilação atrial"`, `kind: protocolo`:

| Arquivo | Slug | Ângulo |
|---|---|---|
| `content/Fibrilação_atrial/fa-pos-ablacao-principios-de-anticoagulacao-de-retorno-esc-2024.md` | `fa-pos-ablacao-principios-de-anticoagulacao-de-retorno-esc-2024` | Peri-procedimento ininterrupto + longo prazo pelo CHA2DS2-VA independentemente do ritmo; gatilhos de escalonamento; sem doses |
| `content/Fibrilação_atrial/fa-e-drc-anticoagulacao-enquadramento-de-ajuste-sem-doses-esc-2024.md` | `fa-e-drc-anticoagulacao-enquadramento-de-ajuste-sem-doses-esc-2024` | Princípios ESC FA+DRC; rejeição de subdose empírica; quando escalar; aponta fluxograma/diálise existentes; **zero miligramas inventados** |

## Fontes
- Van Gelder IC, Rienstra M, Bunting KV, et al. 2024 ESC Guidelines for the management of atrial fibrillation developed in collaboration with the EACTS. Eur Heart J. 2024;45(36):3314-3414. DOI: 10.1093/eurheartj/ehae176. PMID: 39210723.

Nenhuma dose inventada. Nenhuma extrapolação de ensaio sem marcar o limite. Revisão clínica humana obrigatória antes de `review_status: revisado`.

## Branch e PR
- Branch: `grok/tudo-com-tudo-fa-anticoagulacao-densidade-20260907` a partir de `main` (`45ac7889608044b27bc70080dc4642daedc07ecb`).
- Sem clone local; commits via GitHub MCP.
- Sem merge, sem deploy, sem publicação automática.
