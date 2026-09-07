# Tudo-com-Tudo — Fibrilação_atrial: sinalizadores ambulatoriais (não-anticoagulação) (2026-09-07)

## Escopo

Lacuna fina: **destino ambulatorial** na FA — falha de controle de frequência, sintomas novos de IC, e alarmes de **complicação** pós-ablação. Explicitamente **fora**: anticoagulação, doses DOAC, bridge, CHA₂DS₂-VA como decisão antitrombótica.

## Pivô / anti-colisão

- Preferidos avaliados: (1) falha de rate-control ambulatorial → escalar; (2) sintomas novos de IC na clínica de FA; (3) red flags pós-ablação ambulatoriais se não densos.
- **Escolhido:** pacote combinando (1)+(2) + (3) complicação (não recorrência).
- Listagem `content/Fibrilação_atrial`: sem slugs de sinalizadores ambulatoriais não-anticoag; há fluxograma de escolha de droga/alvo e fluxograma de recorrência/blanking — **não** reescritos.
- Open PRs: #827 = anticoag pós-ablação/DRC (**evitar**); #826–#850 = outros temas / overnight; **nenhum** PR aberto de sinalizadores FA não-anticoag até #850 inclusive.
- Evita hubs densos de anticoag/dose já na pasta.

## Arquivos

| Arquivo | Slug | Kind |
|---|---|---|
| `content/Fibrilação_atrial/sinalizadores-ambulatoriais-falha-controle-frequencia-e-novos-sintomas-de-ic-na-fa.md` | `sinalizadores-ambulatoriais-falha-controle-frequencia-e-novos-sintomas-de-ic-na-fa` | protocolo |
| `content/Fibrilação_atrial/fluxograma-ambulatorial-sinalizadores-fa-nao-anticoag-destino.md` | `fluxograma-ambulatorial-sinalizadores-fa-nao-anticoag-destino` | fluxograma |
| `content/Fibrilação_atrial/sinalizadores-ambulatoriais-pos-ablacao-fa-alarme-complicacao-nao-recorrencia.md` | `sinalizadores-ambulatoriais-pos-ablacao-fa-alarme-complicacao-nao-recorrencia` | protocolo |

Todos com `review_status: pendente_revisao`, `fonte_producao: grok`. Sem doses. Sem PMID inventado.

## Fontes

- ESC AF 2024 PMID 39210723 (DOI 10.1093/eurheartj/ehae176) — já no corpus
- SBC/SOBRAC FA 2025 PMID 41294177 (DOI 10.36660/abc.20250618) — já no corpus

## Branch

`feat/tudo-com-tudo-fa-sinalizadores-ambulatoriais-202609070435` → `main`
