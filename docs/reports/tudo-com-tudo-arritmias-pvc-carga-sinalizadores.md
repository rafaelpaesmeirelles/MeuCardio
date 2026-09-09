# Tudo com Tudo — Arritmias: sinalizadores ambulatoriais de carga de PVC → ablação (2026-09-07)

## Pivô (anti-duplicação)

**Alvo:** densificar `content/Arritmias` com lacuna ambulatorial **além de TVNS (#839), SVT/WPW (#864) e bradicardia/BAV (#867)**.

**Preferidos avaliados:**
1. `sinalizadores-ambulatoriais-de-carga-de-pvc-quando-escalar-ablacao` — **escolhido** (estudo Baman/Olgun e fluxograma de indicação Classe I/IIa existem; faltava gate consultório PS vs. EP eletiva vs. vigilância).
2. `pvc-frequente-no-consultorio-sinais-vermelhos-quando-ir-ao-ps` — **escolhido** (irmão de segurança).
3. `fluxograma-sinalizadores-ambulatoriais-pvc-frequente` — **escolhido** (árvore irmã #828-style).
4. QT longo ambulatorial / flutter vs FA destino — **não** neste PR: QT psicofármaco já em #881; FA pastas evitadas (#827/#852/#883); flutter típico já tem fluxograma de anticoagulação/cardioversão/ablacão.

**Evitar:** TVNS (#839); SVT/WPW (#864); bradicardia/BAV (#867); FA (#827/#852/#883); #881 QT/psicofármaco.

## Anti-colisão

- Listagem de `content/Arritmias`: há estudo de carga + fluxograma de indicação de ablação — **sem** slugs `sinalizadores-ambulatoriais` de PVC / `pvc-frequente-no-consultorio`.
- Open PRs Arritmias overnight: #839 TVNS; #864 SVT/pré-excitação; #867 bradicardia/BAV — nenhum PVC ambulatory red-flag.
- Anti-colisão através de #898+ (outros temas IC ferro, cardiorrenal, etc.).

## Arquivos

| Arquivo | Slug | Kind |
|---|---|---|
| `content/Arritmias/sinalizadores-ambulatoriais-de-carga-de-pvc-quando-escalar-ablacao.md` | `sinalizadores-ambulatoriais-de-carga-de-pvc-quando-escalar-ablacao` | protocolo |
| `content/Arritmias/pvc-frequente-no-consultorio-sinais-vermelhos-quando-ir-ao-ps.md` | `pvc-frequente-no-consultorio-sinais-vermelhos-quando-ir-ao-ps` | protocolo |
| `content/Arritmias/fluxograma-sinalizadores-ambulatoriais-pvc-frequente.md` | `fluxograma-sinalizadores-ambulatoriais-pvc-frequente` | fluxograma |

`review_status: pendente_revisao`. Sem doses. Sem auto-merge.

## Slugs relacionados (existentes)

`extrassistole-ventricular-frequente-e-cardiomiopatia-induzida-carga-que-preve-disfuncao`, `fluxograma-extrassistole-ventricular-frequente-cardiomiopatia-induzida-e-indicacao-de-ablacao`, `suprimir-extrassistole-nao-e-tratar-o-paciente-cast-e-sword`, `arritmias-ventriculares-e-prevencao-de-morte-subita-cardiaca-esc-2022`.

## Fontes (PMIDs verificados Europe PMC)

- Baman 2010 PMID 20348027 (DOI 10.1016/j.hrthm.2010.03.036)
- Olgun 2011 PMID 21376837 (DOI 10.1016/j.hrthm.2011.02.034)
- HRS/EHRA/APHRS/LAHRS 2019 PMID 32071620 (DOI 10.1002/joa3.12264)
- ESC 2022 VA/SCD PMID 36017572 (DOI 10.1093/eurheartj/ehac262)

## Branch

`feat/tudo-com-tudo-arritmias-pvc-carga-sinalizadores-20260907` → `main`
