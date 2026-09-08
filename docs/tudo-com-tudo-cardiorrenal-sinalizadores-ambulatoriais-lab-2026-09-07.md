# Tudo-com-Tudo — Cardiorrenal: sinalizadores ambulatoriais de creatinina/K (2026-09-07)

## Escopo

Lacuna fina **além de #829** (densidade conceitual: hiperpotassemia-segurança, albuminúria/TFGe, contraste) e **além de #842** (congestão IC / destino PS):
**destino ambulatorial** quando creatinina sobe sob GDMT e quando hiperpotassemia exige escalada — **sem novo hub** (#692).

## Anti-colisão (através de #894+)

| PR | Por que não colide |
|---|---|
| **#692** | Hub `doencas` síndrome cardiorrenal — **não tocado** |
| **#829** | Conceitos (segurança K, albuminúria, contraste) — este PR só **destino ambulatorial** |
| **#842 / #878** | Sinalizadores IC congestão / IC avançada — escopo diferente; #842 declara cardiorrenal fora |
| **#755** | Pacotes science IC/cardiorrenal — não ambulatory destination |
| **#894+** | Outras especialidades (lipídios, síncope, gravidez…) — sem overlap Cardiorrenal lab |

Não cria verbete em `doencas/`. Não inventa doses. Não auto-merge.

## Arquivos

| Arquivo | Slug | Kind |
|---|---|---|
| `content/Cardiorrenal/piora-de-creatinina-sob-gdmt-ambulatorial-quando-encaminhar-nefrologia.md` | `piora-de-creatinina-sob-gdmt-ambulatorial-quando-encaminhar-nefrologia` | protocolo |
| `content/Cardiorrenal/hiperpotassemia-ambulatorial-na-ic-com-drc-quando-escalar.md` | `hiperpotassemia-ambulatorial-na-ic-com-drc-quando-escalar` | protocolo |
| `content/Cardiorrenal/fluxograma-ambulatorial-creatinina-e-potassio-ic-drc-destino.md` | `fluxograma-ambulatorial-creatinina-e-potassio-ic-drc-destino` | fluxograma |

Todos: `review_status: pendente_revisao`; `fonte_producao: grok`; tema `Insuficiência cardíaca` (irmão da pasta Cardiorrenal).

## Fontes (PMIDs conferidos)

- ESC 2021 HF — PMID **34447992**
- ESC 2023 Focused Update HF — PMID **37622666**
- KDIGO 2024 CKD — PMID **38490803**
- ACC/AHA/HFSA 2022 HF — PMID **35363499**
- DIAMOND — PMID **35900838**
- ESC 2026 CVD+CKD — DOI **10.1093/eurheartj/ehag098** (já no corpus; sem PMID inventado)

## Branch

`grok/tudo-com-tudo-cardiorrenal-sinalizadores-ambulatoriais-lab-20260907` → `main`
