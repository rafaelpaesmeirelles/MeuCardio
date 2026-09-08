# Tudo-com-Tudo — Terapia_intensiva: seguimento ambulatorial pós-tMCS (2026-09-07)

## Escopo

Lacuna fina **BEYOND #861** (sinalizadores ambulatoriais pós-UTI gerais): **destino ambulatorial após explante de tMCS** (ponte temporária — IABP / Impella / VA-ECMO). Eixos: sítio vascular de grande calibre + trajetória / re-referral a IC avançada. Explicitamente **fora**: indicação, escalonamento, desmame, anticoagulação sob suporte, doses, SCAI à beira do leito.

## Pivô / anti-colisão

- Preferidos avaliados: (1) cardiogenic shock survivor ambulatory red flags — **já coberto em #861**; (2) temporary MCS bridge outpatient follow-up — **escolhido (ausente)**; (3) delirium/PTSD post-ICU cardiac when refer — #861 já cobre PICS/cognição de forma geral; adiado para não colidir.
- Listagem `content/Terapia_intensiva`: denso em tMCS hospitalar (`choque-cardiogenico-suporte-circulatorio-mecanico-temporario`, `escalonamento-e-desmame-*`, Impella/ECMO/IABP) — **sem** slugs ambulatoriais pós-explante.
- Open PRs: único pacote Terapia_intensiva sinalizadores = **#861**; re-checados até **#894+** (outros temas: Prevenção, Síncope, Gravidez, Farmacologia, etc.) — **nenhum** PR aberto deste pacote pós-tMCS ambulatorial.
- Evita Dispositivos #835/#870 (CIED/pré-RM) — aqui só sítio pós-tMCS / large-bore.

## Arquivos

| Arquivo | Slug | Kind |
|---|---|---|
| `content/Terapia_intensiva/seguimento-ambulatorial-pos-tmcs-ponte-temporaria-quando-escalar.md` | `seguimento-ambulatorial-pos-tmcs-ponte-temporaria-quando-escalar` | protocolo |
| `content/Terapia_intensiva/sinalizadores-ambulatoriais-pos-tmcs-sitio-vascular-ic-avancada.md` | `sinalizadores-ambulatoriais-pos-tmcs-sitio-vascular-ic-avancada` | protocolo |
| `content/Terapia_intensiva/fluxograma-ambulatorial-pos-tmcs-destino.md` | `fluxograma-ambulatorial-pos-tmcs-destino` | fluxograma |

Todos com `review_status: pendente_revisao`, `fonte_producao: grok`. Sem doses. Sem PMID inventado.

## Fontes (já no corpus hospitalar / validadas)

- ACVC/ESC tMCS short-term consensus PMID 37315190 (DOI 10.1093/ehjacc/zuad064)
- ACC 2025 Concise Clinical Guidance CS PMID 40100174 (DOI 10.1016/j.jacc.2025.02.018)
- HFA/ESC cardiogenic shock position statement PMID 32469155 (DOI 10.1002/ejhf.1922)
- ESC HF 2021 PMID 34447992 (DOI 10.1093/eurheartj/ehab368)

## Branch

`feat/tudo-com-tudo-terapia-intensiva-tmcs-ambulatorial-20260907` → `main`

Sem merge automático; revisão clínica humana antes de `revisado`.
