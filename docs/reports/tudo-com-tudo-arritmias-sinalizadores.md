# Tudo com Tudo — Arritmias: sinalizadores ambulatoriais (2026-09-07)

## Pivô (anti-duplicação)

**Alvo:** densificar `content/Arritmias` com lacuna ambulatorial de red-flag / decisão de destino.

**Preferidos avaliados:**
1. `sinalizadores-ambulatoriais-de-taquicardia-ventricular-nao-sustentada-quando-escalar` — **escolhido** (ausente no main).
2. `bradicardia-ambulatorial-quando-encaminhar-urgencia-versus-eletivo` — adjacente a `fluxograma-bradicardia-sintomatica-manejo-agudo` (agudo já existe).
3. `fluxograma-palpitacoes-ambulatoriais-quando-pedir-holter-versus-ps` — não criado neste PR (manter PR pequeno).

**Evitar:** FA anticoagulação (#827); hubs densos em `Fibrilação_atrial`; overnight #826–836 (Diabetes, FA, Hipertensão, Cardiorrenal, Reabilitação, Teach-back, Aorta/DAP, Cardio-oncologia, Dispositivos, Perioperatório).

## Anti-colisão

- Listagem de `content/Arritmias`: sem slug de sinalizadores ambulatoriais de TVNS.
- Code search: zero hits para `sinalizadores` / `ambulatorial` / `palpitacoes` em Arritmias.
- Open PRs Arritmias recentes: hubs/materiais antigos (#601, #691, etc.) — nenhum overnight de TVNS ambulatorial.

## Arquivos

| Arquivo | Slug | Kind |
|---|---|---|
| `content/Arritmias/sinalizadores-ambulatoriais-de-taquicardia-ventricular-nao-sustentada-quando-escalar.md` | `sinalizadores-ambulatoriais-de-taquicardia-ventricular-nao-sustentada-quando-escalar` | protocolo |

`review_status: pendente_revisao`. Sem doses. Sem auto-merge.

## Slugs relacionados (existentes)

`arritmias-ventriculares-e-prevencao-de-morte-subita-cardiaca-esc-2022`, `fluxograma-arritmia-ventricular-e-morte-subita`, `extrassistole-ventricular-frequente-e-cardiomiopatia-induzida-carga-que-preve-disfuncao`, `taquicardia-ventricular-idiopatica-do-trato-de-saida-diagnostico-e-ablacao`, `fluxograma-bradicardia-sintomatica-manejo-agudo`.

## Fontes

- ESC 2022 VA/SCD PMID 36017572 (DOI 10.1093/eurheartj/ehac262)
- AHA/ACC/HRS 2017 VA/SCD PMID 29097296 (DOI 10.1016/j.jacc.2017.10.054)

## Branch

`feat/tudo-com-tudo-arritmias-sinalizadores-202609070418` → `main`
