# Tudo-com-Tudo — Fibrilação_atrial: pós-cardioversão ambulatorial → PS (além #827/#852) (2026-09-07)

## Escopo / pivô

**Lacuna:** destino ambulatorial após **cardioversão** de FA (elétrica ou química) — **quando voltar ao PS** vs retorno precoce por recorrência estável vs plano — **sem doses**.

**Já coberto (não duplicar):**
- `#827` — anticoagulação pós-ablação + FA+DRC (ESC 2024)
- `#852` — falha de controle de frequência / sintomas novos de IC + alarme de **complicação** pós-ablação (não recorrência)
- `cardioversao-eletiva-e-anticoagulacao-periprocedimento-esc-2024` (+ fluxograma) — via peri / 3 semanas / TEE / 4 semanas (**não** red flags de retorno ao PS)
- RACE 7 / pill-in-the-pocket — cenário de início recente / elegibilidade, não pós-alta ambulatorial de alarmes

**Pivô escolhido:** post-cardioversion ambulatory when return to ED (ausente em `main` e nos PRs abertos de FA até a checagem pré-commit).

**Alternativas avaliadas e adiadas:**
- rate vs rhythm → escalar a centro de ablação: parcialmente aludido em #852 + `fluxograma-indicacao-ablacao-cateter-fa-esc-2024` já denso
- AF+HF red flags sem cardiorrenal: overlap forte com #852 (sintomas novos de IC)

## Anti-colisão

- Evita `#827` e `#852` (slugs distintos; não reabre anticoag peri nem pós-ablação estrutural).
- Evita `#826–#882+` de outras pastas.
- Não protocola doses nem reescreve fluxogramas peri / indicação de ablação.

## Arquivos

| Arquivo | Slug | Kind |
|---|---|---|
| `content/Fibrilação_atrial/sinalizadores-ambulatoriais-pos-cardioversao-fa-quando-voltar-ao-ps.md` | `sinalizadores-ambulatoriais-pos-cardioversao-fa-quando-voltar-ao-ps` | protocolo |
| `content/Fibrilação_atrial/fluxograma-ambulatorial-pos-cardioversao-fa-destino.md` | `fluxograma-ambulatorial-pos-cardioversao-fa-destino` | fluxograma |
| `content/Fibrilação_atrial/recorrencia-leve-pos-cardioversao-fa-retorno-precoce-nao-ps.md` | `recorrencia-leve-pos-cardioversao-fa-retorno-precoce-nao-ps` | protocolo |

Todos com `review_status: pendente_revisao`, `fonte_producao: grok`.

## Fontes (somente refs conferidas)

- ESC AF 2024 — Van Gelder et al., PMID **39210723** (DOI 10.1093/eurheartj/ehae176) — já no corpus
- SBC/SOBRAC FA 2025 — Cintra et al., PMID **41294177** (DOI 10.36660/abc.20250618) — já no corpus

Sem PMID inventado. Sem doses. Sem auto-merge.

## Branch

`feat/tudo-com-tudo-fa-pos-cardioversao-ambulatorial-20260907` → `main`
