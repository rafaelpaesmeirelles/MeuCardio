# Tudo-com-Tudo — Terapia_intensiva: sinalizadores ambulatoriais pós-UTI (2026-09-07)

## Escopo

Lacuna fina: **destino ambulatorial** após alta de UTI/UCO ou pós-**choque cardiogênico** — quando a clínica deve escalar por infecção, IC, dispositivo ou cognição/PICS. Explicitamente **fora**: vasoativos, doses, MCS, estadiamento SCAI à beira do leito.

## Pivô / anti-colisão

- Preferidos avaliados: (1) pós-alta após choque cardiogênico — quando escalar; (2) red flags ambulatoriais pós-UTI (infecção, HF, cognitivo, device).
- **Escolhido:** pacote combinando (1)+(2) com fluxograma de destino.
- Listagem `content/Terapia_intensiva`: **sem** slugs de sinalizadores ambulatoriais / pós-alta UTI; densos em choque/SCAI/vasoativos/MCS — **não** reescritos.
- Open PRs re-checados através de **#860**: #826–858 evitados por instrução; #859 Síncope; #860 Farmacologia DOAC — **nenhum** PR aberto de sinalizadores Terapia_intensiva pós-UTI.
- Evita #835 Dispositivos (eletrodo/CDI crônico) — aqui só eixo pós-UTI/sítio/MCS recente.

## Arquivos

| Arquivo | Slug | Kind |
|---|---|---|
| `content/Terapia_intensiva/sinalizadores-ambulatoriais-pos-uti-choque-cardiogenico-quando-escalar.md` | `sinalizadores-ambulatoriais-pos-uti-choque-cardiogenico-quando-escalar` | protocolo |
| `content/Terapia_intensiva/sinalizadores-ambulatoriais-pos-alta-uti-infeccao-dispositivo-ic-cognicao.md` | `sinalizadores-ambulatoriais-pos-alta-uti-infeccao-dispositivo-ic-cognicao` | protocolo |
| `content/Terapia_intensiva/fluxograma-ambulatorial-sinalizadores-pos-uti-cardiologia-destino.md` | `fluxograma-ambulatorial-sinalizadores-pos-uti-cardiologia-destino` | fluxograma |

Todos com `review_status: pendente_revisao`, `fonte_producao: grok`. Sem doses. Sem PMID inventado.

## Fontes

- HFA/ESC cardiogenic shock position statement PMID 32469155 (DOI 10.1002/ejhf.1922) — já no corpus
- ESC HF 2021 PMID 34447992 (DOI 10.1093/eurheartj/ehab368)

## Branch

`feat/tudo-com-tudo-terapia-intensiva-sinalizadores-202609070448` → `main`
