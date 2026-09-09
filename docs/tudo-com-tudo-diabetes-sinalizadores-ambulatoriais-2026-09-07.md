# Tudo-com-Tudo — Diabetes_e_cardiologia: sinalizadores ambulatoriais (além #826) (2026-09-07)

## Escopo

Lacuna fina: **destino ambulatorial** no diabético visto na cardiologia — hipoglicemia grave, intolerância/alarmes de iSGLT2–GLP-1RA, e gate de pé/infecção. Explicitamente **fora**: lesão de órgão-alvo / SCORE2 e rastreamento IC/FA (**#826**); doses; PMIDs inventados.

## Pivô / anti-colisão

- Preferidos avaliados: (1) hipoglicemia alarms na clínica de cardiologia; (2) SGLT2/GLP1 intolerância escalate **sem doses**; (3) foot/infection red flags quando o cardio vê o diabético.
- **Escolhido:** (1)+(2) + fluxograma de destino (gate de pé/infecção no D1).
- Listagem `content/Diabetes_e_cardiologia`: há mecanismo de hipoglicemia/NAC e CAD euglicêmica longa / DAP-pé IWGDF — **não** reescritos; faltava pacote de **destino** PS vs retorno precoce.
- Open PRs: **#826** = lesão órgão-alvo + IC/FA (**evitar**); #828–#854 = outros temas sinalizadores / overnight; **nenhum** PR aberto de sinalizadores Diabetes_e_cardiologia ambulatoriais além de #826 até #854.
- Evita hubs densos de CVOT e peri-op iSGLT2.

## Arquivos

| Arquivo | Slug | Kind |
|---|---|---|
| `content/Diabetes_e_cardiologia/sinalizadores-ambulatoriais-hipoglicemia-grave-no-consultorio-de-cardiologia.md` | `sinalizadores-ambulatoriais-hipoglicemia-grave-no-consultorio-de-cardiologia` | protocolo |
| `content/Diabetes_e_cardiologia/sinalizadores-ambulatoriais-intolerancia-e-alarme-sglt2-glp1-sem-doses.md` | `sinalizadores-ambulatoriais-intolerancia-e-alarme-sglt2-glp1-sem-doses` | protocolo |
| `content/Diabetes_e_cardiologia/fluxograma-ambulatorial-sinalizadores-diabetes-cv-destino.md` | `fluxograma-ambulatorial-sinalizadores-diabetes-cv-destino` | fluxograma |

Todos com `review_status: pendente_revisao`, `fonte_producao: grok`. Sem doses. Sem PMID inventado.

Nota: `docs/tudo-com-tudo-diabetes-sinalizadores-ambulatoriais-2026-09-07.md`

## Fontes

- ESC 2023 CVD in diabetes — DOI 10.1093/eurheartj/ehad192; PMID 37622656
- ADA Standards of Care 2026 Cap. 10 — DOI 10.2337/dc26-S010; PMID 41358899

## Branch

`feat/tudo-com-tudo-diabetes-sinalizadores-202609070439` → `main`
