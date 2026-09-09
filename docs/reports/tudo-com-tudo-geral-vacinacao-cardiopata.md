# Tudo com Tudo — Geral: sinalizadores ambulatoriais vacinação cardiopata (2026-09-07)

## Pivô (anti-duplicação)

**Alvo:** densificar `content/Geral` com lacuna ambulatorial **além dos ensaios/metaanálises de influenza já revisados** (IAMI/Udell + geriátrica) e **além de #902** (SAMS/estatina — que listou vacinação cardiopata como lote seguinte).

**Preferidos avaliados:**
1. `sinalizadores-ambulatoriais-vacinacao-cardiopata-quando-escalar` — **escolhido** (gate consultório PS vs. prioridade pós-SCA/IC vs. oferta ASCVD).
2. `vacinacao-cardiopata-no-consultorio-pos-sca-ic-checklist` — **escolhido** (irmão operacional de uma visita).
3. `fluxograma-sinalizadores-ambulatoriais-vacinacao-cardiopata` — **escolhido** (árvore irmã #828-style).
4. Brugada adulto febre ambulatory / prótese valvar trombose / HCM sinalizadores — **não** neste PR: Brugada pediátrico já denso; valvar hub #715; HCM fica para lote seguinte.

**Evitar:** duplicar IAMI/Udell (já revisados); #838 amiodarona/digoxina; miopericardite pós-mRNA (já em Pericárdio/pediatria); inventar esquemas PCV/PPSV ou doses.

## Anti-colisão

- Open PR `vacina` in:title: **0** hits.
- Code: existem `vacinacao-contra-influenza-como-prevencao-cardiovascular-iami-e-metanalise-de-udell` e versão geriátrica — **sem** slugs `sinalizadores-ambulatoriais-vacinacao` / checklist consultório.
- #902 report explicitamente deferiu “vacinação cardiopata” para lotes seguintes.
- Open set densificação contínuo ~#826–908 (#830 closed; #838 draft).

## Arquivos

| Arquivo | Slug | Kind |
|---|---|---|
| `content/Geral/sinalizadores-ambulatoriais-vacinacao-cardiopata-quando-escalar.md` | `sinalizadores-ambulatoriais-vacinacao-cardiopata-quando-escalar` | protocolo |
| `content/Geral/vacinacao-cardiopata-no-consultorio-pos-sca-ic-checklist.md` | `vacinacao-cardiopata-no-consultorio-pos-sca-ic-checklist` | protocolo |
| `content/Geral/fluxograma-sinalizadores-ambulatoriais-vacinacao-cardiopata.md` | `fluxograma-sinalizadores-ambulatoriais-vacinacao-cardiopata` | fluxograma |

`review_status: pendente_revisao`. Sem doses/marcas. Sem auto-merge.

## Slugs relacionados (existentes)

`vacinacao-contra-influenza-como-prevencao-cardiovascular-iami-e-metanalise-de-udell`, `vacinacao-contra-influenza-como-prevencao-cardiovascular-no-idoso`, `miopericardite-associada-a-vacina-de-mrna-contra-covid-19`.

## Fontes (PMIDs reais)

- Fröbert IAMI 2021 PMID 34459211 (DOI 10.1161/CIRCULATIONAHA.121.057042)
- Udell JAMA 2013 PMID 24150467 (DOI 10.1001/jama.2013.279206)
- Visseren ESC Prevention 2021 PMID 34458905 (DOI 10.1093/eurheartj/ehab484)
- McDonagh ESC HF 2021 PMID 34447992 (DOI 10.1093/eurheartj/ehab368)

## Branch

`feat/tudo-com-tudo-geral-vacinacao-cardiopata-20260907-0324` → `main`
