---
title: "Sessão Grok — produção científica 29/08/2026"
slug: grok-science-overnight-20260829
---

# Sessão Grok — produção científica 29/08/2026

Branch: `grok/science-overnight-20260829`
Base: `origin/main` SHA `1945e11197bb9a1708469498c1317bae607540e3`

Escopo: conteúdo científico original, status inicial `pendente_revisao`. Sem merge, sem deploy, sem alteração de produto.

Território: DAC, IC, hipertensão/prevenção, intensiva/emergência, cardio-oncologia/sistêmico. Sem invadir arritmias, congênitas, pediatria, valvopatias, aorta ou imagem avançada salvo lacuna explícita.

PRs abertas deliberadamente não duplicadas: #713 emergência hipertensiva, #697 MINOCA/SCAD, #692 cardiorrenal, #684 obesidade, #700 amiloidose AL, #719 sarcoidose, #594 IC avançada, #590 choque, #597 HAS resistente, #570 dislipidemia, #572 diabetes.

## Lotes já no disco (lote 1)

Todos os markdown novos com `review_status: pendente_revisao`. Evidências/estudos novos com `published: false`.

### Doença coronariana

- `angina-microvascular-endotipo-cmd-na-pratica.md`
- `angina-vasoespastica-criterios-covadis-diagnostico-e-tratamento.md`
- `fluxograma-angina-vasoespastica-teste-provocativo-e-tratamento.md`
- `comunicacao-interventricular-pos-infarto-diagnostico-e-decisao.md`
- `fluxograma-complicacao-mecanica-pos-iam-civ-e-ruptura-papilar.md`
- `infarto-tipo-2-versus-lesao-miocardica-nao-isquemica.md` (sem segundo fluxograma: o canônico de troponina já existe)
- `prevencao-secundaria-integrada-apos-sindrome-coronariana-aguda.md`
- `fluxograma-alta-apos-sca-os-cinco-pilares-modificaveis.md`

### Insuficiência cardíaca

- `icfei-historica-e-a-reclassificacao-esc-2026.md`
- `fluxograma-feve-esc-2021-versus-esc-2026.md`
- `ic-descompensada-esc-2026-e-titulacao-pos-alta.md`
- `indicacoes-de-transplante-cardiaco-adulto-ishlt-2016.md`
- `fluxograma-quando-encaminhar-para-listagem-de-transplante-cardiaco.md`
- `summit-tirzepatida-icfep-com-obesidade.md` (card de eventos; não clona o SUMMIT de Diabetes)
- `agonistas-incretina-na-icfep-com-obesidade-step-e-summit.md` (ESC 2026 Tabela 18 IIa B1 para peso/exercício/QoL, não mortalidade)

### Prevenção, diabetes, HAS, emergência

- `select-semaglutida-desfechos-cardiovasculares-obesidade-sem-diabetes.md`
- `sglt2-na-doenca-renal-cronica-dapa-ckd-empa-kidney-e-flow.md` (comparativo; não reescreve os cards)
- `prescricao-de-exercicio-em-prevencao-primaria-cardiovascular.md`
- `fluxograma-avaliacao-pre-participacao-exercicio-adulto-assintomatico.md`
- `hipertensao-secundaria-causas-rastreaveis-no-adulto.md` (não clona emergência hipertensiva / PR #713)
- `edema-agudo-de-pulmao-cardiogenico-protocolo-inicial.md`
- `dispneia-aguda-de-origem-cardiovascular-abordagem-inicial.md`
- `fluxograma-dispneia-aguda-cardiogenica-versus-nao-cardiogenica.md`

## Importação JSON (lote 1)

Sidecars em `.science-staging/lote-*.json` fundidos nos metadados. Slugs duplicados do lote-hf-incretina (já importado antes) foram pulados.

Contagens após merge:

| Corpus | n | novos neste merge |
|---|---:|---:|
| evidencias | 2807 | +47 |
| estudos | 1644 | +8 |
| casos-clinicos | 848 | +14 |
| checklists | 379 | +12 |
| material-paciente | 402 | +12 |
| trilhas | 531 | +2 |
| emergencia | 75 | +1 |

### Itens retidos na importação (não viraram evidência classificada)

- `esc-2026-hfmrEF-categoria-removida` e `esc-2026-icfer-feve-menor-50-com-sinais-sintomas` — mudança de nomenclatura, sem classe/nível
- `pcdt-2024-dapagliflozina-exige-feve-menor-40` — critério administrativo, sem classe ESC
- ACSM 2015 “inicia exercício leve/moderado sem liberação” — consenso de algoritmo, sem classe
- Três linhas KDIGO 2024 com GRADE 1/2 numérico — o corpus não usa esse sistema; não convertidas silenciosamente para I/IIa

## Próxima leva (em produção paralela)

Lacunas ainda reais neste território: ADVOR/CLOROTIC, TEP intermediário-alto/PEITHO, pós-ROSC 24 h integrado, Lp(a) conduta prática, dor torácica no PS (se não houver canônico), miocardite aguda do adulto não-ICI (se lacuna).

## Não fazer

Não merge. Não deploy. Não push para `main`. Não alterar frontend, CI, Cloudflare, Docker, migrations.
