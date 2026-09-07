# Tudo com Tudo — Farmacologia: sinalizadores ambulatoriais de varfarina/INR (2026-09-07)

## Pivô (anti-duplicação)

**Alvo preferido do brief:** digoxina toxicidade ambulatorial → PS (sintomas/ECG).

**Achado:** já coberto pelo draft **#838** (`sinalizadores-ambulatoriais-de-toxicidade-da-digoxina.md` + hub amiodarona) e, em `main`, por `intoxicacao-digitalica-fatores-precipitantes-e-manifestacoes-clinicas.md`. Evitei colisão.

**Pivô escolhido:** AVK/varfarina ambulatorial — **INR elevado sem sangramento** + **sangramento menor vs. maior** → destino PS vs. retorno precoce. Paralelo ao pacote DOAC **#860**, classe distinta.

## Anti-colisão

| PR / tema | Relação |
|---|---|
| #838 amiodarona/digoxina (draft) | **Não tocado** |
| #860 DOAC sangramento | Paralelo; slugs distintos |
| #887 AINE | Não tocado |
| #891 PDE5 × nitrato | Não tocado |
| #902 SAMS/estatina (Prevenção) | Outro tema |
| #897 creatinina/K (Cardiorrenal) | Outro tema |
| Open set ~#826–#910+ | Nenhum PR `varfarina`/`INR` sinalizadores ambulatoriais em Farmacologia |
| `search_code` | Monografias/interações/farmacogenômica/reversão — **sem** slug `sinalizadores-ambulatoriais-varfarina*` |

## Arquivos (3 content + report)

| Arquivo | Slug | Kind |
|---|---|---|
| `content/Farmacologia/sinalizadores-ambulatoriais-varfarina-inr-sangramento-quando-encaminhar.md` | `sinalizadores-ambulatoriais-varfarina-inr-sangramento-quando-encaminhar` | protocolo |
| `content/Farmacologia/fluxograma-sinalizadores-ambulatoriais-varfarina.md` | `fluxograma-sinalizadores-ambulatoriais-varfarina` | fluxograma |
| `content/Farmacologia/inr-elevado-sem-sangramento-no-consultorio-conduta-ambulatorial.md` | `inr-elevado-sem-sangramento-no-consultorio-conduta-ambulatorial` | protocolo |

Todos com `review_status: pendente_revisao`, `fonte_producao: grok`, frontmatter no padrão #828/#860.

## Fontes (reais)

- ASH 2018 anticoagulation management — PMID **30482765**
- CHEST 2012 Holbrook et al. — PMID **22315259**
- ESC AF 2024 — PMID **39210723**

Sem doses de varfarina/vitamina K. Sem PMIDs fabricados. **Sem merge automático.**

## Branch

`feat/tudo-com-tudo-farmacologia-varfarina-sinalizadores-20260907-0328` → `main`
