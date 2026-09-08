# Tudo com Tudo — densificação Cardiorrenal — 2026-09-07

## Objetivo

Densificar `content/Cardiorrenal/` sem criar novo hub em `doencas/` (PR #692 já cobre `sindrome-cardiorrenal`).

## Entregas

Branch: `agent/tudo-com-tudo-cardiorrenal-densidade-20260907` ← `main`.

### Novos Markdown (3)

- `hiperpotassemia-e-farmacos-prognosticos-na-ic-com-drc-seguranca-sem-abandonar-beneficio`
- `albuminuria-e-tfge-como-eixo-transversal-de-risco-cardiovascular`
- `contraste-e-peri-procedimento-na-drc-principios-de-seguranca`

Todos: `review_status: pendente_revisao`; `fonte_producao: grok`; sem doses. Tema mantido `Insuficiência cardíaca` (como o irmão ESC 2026 da pasta).

### Omitido

Sem edição em `doencas/`; sem `material-paciente`/`evidencias`/`estudos` (JSON monolíticos; schema não claro o bastante).

## Fontes

1. ESC 2026 CVD+CKD — DOI `10.1093/eurheartj/ehag098`
2. ESC 2026 HF — DOI `10.1093/eurheartj/ehag100`
3. KDIGO 2024 CKD — DOI `10.1016/j.kint.2023.10.018`
4. DIAMOND — DOI `10.1093/eurheartj/ehac401`, PMID `35900838` (já no corpus)

## Anti-colisão

Não toca PR #692; não reescreve DIAMOND; trabalho via GitHub API apenas.
