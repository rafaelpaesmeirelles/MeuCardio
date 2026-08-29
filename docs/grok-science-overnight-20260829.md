---
title: "Sessão Grok — produção científica 29/08/2026 (encerrada)"
slug: grok-science-overnight-20260829
---

# Sessão Grok — produção científica 29/08/2026

**Status: ENCERRADA a pedido do usuário (salvar, finalizar, interromper produção).**

Branch: `grok/science-overnight-20260829`
Base: `origin/main` SHA `1945e11197bb9a1708469498c1317bae607540e3`
HEAD local (antes dos commits finais do lote 2): `4d26221867a2c4f417579f6bf6f8c087a8169885`

Escopo: conteúdo científico original, status inicial `pendente_revisao`. Sem merge, sem deploy, sem alteração de produto, sem push para `main`.

Território: DAC, IC, hipertensão/prevenção, intensiva/emergência, cardio-oncologia/sistêmico. Sem invadir arritmias, congênitas, pediatria, valvopatias, aorta ou imagem avançada salvo lacuna explícita.

PRs abertas deliberadamente não duplicadas: #713 emergência hipertensiva, #697 MINOCA/SCAD, #692 cardiorrenal, #684 obesidade, #700 amiloidose AL, #719 sarcoidose, #594 IC avançada, #590 choque, #597 HAS resistente, #570 dislipidemia, #572 diabetes.

## Produção

### Lote 1 — 23 markdown

**Insuficiência cardíaca**
- `icfei-historica-e-a-reclassificacao-esc-2026` + `fluxograma-feve-esc-2021-versus-esc-2026`
- `summit-tirzepatida-icfep-com-obesidade` + `agonistas-incretina-na-icfep-com-obesidade-step-e-summit`
- `indicacoes-de-transplante-cardiaco-adulto-ishlt-2016` + `fluxograma-quando-encaminhar-para-listagem-de-transplante-cardiaco`
- `ic-descompensada-esc-2026-e-titulacao-pos-alta`

**Doença coronariana**
- `angina-vasoespastica-criterios-covadis-diagnostico-e-tratamento` + fluxograma
- `angina-microvascular-endotipo-cmd-na-pratica`
- `comunicacao-interventricular-pos-infarto-diagnostico-e-decisao` + fluxograma mecânico
- `infarto-tipo-2-versus-lesao-miocardica-nao-isquemica`
- `prevencao-secundaria-integrada-apos-sindrome-coronariana-aguda` + fluxograma alta

**Prevenção / diabetes**
- `select-semaglutida-desfechos-cardiovasculares-obesidade-sem-diabetes`
- `prescricao-de-exercicio-em-prevencao-primaria-cardiovascular` + fluxograma pré-participação
- `sglt2-na-doenca-renal-cronica-dapa-ckd-empa-kidney-e-flow`

**Emergência / HAS**
- `dispneia-aguda-de-origem-cardiovascular-abordagem-inicial` + fluxograma
- `hipertensao-secundaria-causas-rastreaveis-no-adulto`
- `edema-agudo-de-pulmao-cardiogenico-protocolo-inicial`

### Lote 2 — 12 markdown novos + 1 retain

- ADVOR/CLOROTIC: acetazolamida e tiazídico na resistência diurética + fluxograma
- TEP intermediário-alto: PEITHO e quando não trombolisar + fluxograma
- Pós-ROSC primeiras 24 h + fluxograma ECG/temperatura/PA/cateterismo
- Lp(a) conduta prática enquanto CVOTs não chegam + fluxograma
- Dor torácica aguda primeira hora no PS + fluxograma ECG/troponina
- Wellens: reconhecimento e por que não fazer teste ergométrico + fluxograma
- Miocardite aguda do adulto: **RETIDO** — protocolo/fluxograma ESC 2025 já canônicos

### QC lote 1

Arquivo `docs/grok-science-overnight-20260829-qc.md`. Flags mandatórias PASS (SUMMIT não é mortalidade; incretina é AMT IIa B1; VO2 ISHLT 12/14). PMIDs âncora conferidos. Nada promovido a `revisado`.

## Corpus após importação lote 1 + lote 2

| Corpus | n final | Δ sessão |
|---|---|---|
| evidencias | 2827 | +67 |
| estudos | 1648 | +12 |
| casos-clinicos | 854 | +20 |
| checklists | 385 | +18 |
| material-paciente | 408 | +18 |
| trilhas | 531 | +2 |
| emergencia | 77 | +3 (dispneia 124, pós-ROSC 125, dor torácica 126) |

Todos os novos: `review_status: pendente_revisao`. Evidências/estudos: `published: false`.

## Itens retidos (não inventados)

- Classe de CCB/nitrato/BB na VSA; Classe III de BB na VSA
- SUMMIT como redução de mortalidade
- Incretina como FMT ou classe de morte
- KDIGO GRADE 1/2 numérico (corpus não usa esse formato)
- Nomenclatura ESC 2026 HFmrEF removida / ICFEr <50% sem classe de tabela
- PCDT administrativo FEVE <40% como evidência classificada
- ACSM sem classe ESC/AHA
- Classe I de MACE para pelacarsena/olpasirana (HORIZON sem resultado publicado em 29/08/2026)
- COR/LOE AHA 2025 Parte 11 (PDF 403)
- Classe ESC 2019 de reperfusão no TEP intermediário: restage do corpus; tabela PDF não relida nesta sessão
- Protocolo adulto de miocardite aguda (já existe)
- Emergência hipertensiva (PR #713), MINOCA/SCAD (#697), cardiorrenal (#692), obesidade (#684), amiloidose AL (#700), sarcoidose (#719), IC avançada (#594), choque (#590), HAS resistente (#597)

## Tudo com Tudo

Arestas clínicas via `document_slug` nas evidências/estudos/casos/checklists/materiais novos. Sem arestas fictícias. Sem dado de paciente no grafo global. Sem verbete novo em `doencas/metadados.json`. Emergências novas ligadas aos protocolos/fluxogramas correspondentes.

## Push

Tentativa de `git push origin grok/science-overnight-20260829` e de create-branch via conector GitHub: **403**. Token com `X-OAuth-Scopes` vazio (sem `contents:write`). Branch existe só no workspace até reconectar o GitHub com escrita. **Não foi aberto PR. Não houve merge. Não houve deploy.**

## Commits lote 1

- `cfced81` content(ic): ESC 2026 ICFEi, SUMMIT/incretina, transplante ISHLT 2016
- `e0a4aea` content(dac): VSA/COVADIS, CMD, CIV pós-IAM, tipo 2 e alta pós-SCA
- `237a407` content(prevencao): SELECT dedicado, exercício primário e SGLT2 na DRC
- `4fbf541` content(emergencia): dispneia aguda, HAS secundária rastreável e EAP inicial
- `91ba2fb` content(corpus): importar lotes overnight 20260829 em pendente_revisao
- `4d26221` docs: log da sessão científica grok/science-overnight-20260829
