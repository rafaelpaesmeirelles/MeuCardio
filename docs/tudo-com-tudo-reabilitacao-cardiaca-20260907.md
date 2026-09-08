# Tudo com Tudo — hub Reabilitação cardíaca (adulto) — 07/09/2026

## Lacuna

`content/Reabilitação_cardíaca/` tinha essencialmente 1 documento (`esc-2026-reabilitacao-cardiaca-sintese-pratica-corvia`). Não havia verbete-hub adulto em `doencas/fragmentos/` para RC. O documento geriátrico `reabilitacao-cardiaca-no-muito-idoso-seguranca-fragilidade-e-adesao` já existia e foi **vinculado, não duplicado**.

## Anti-colisão

- Não criado hub de síndrome cardiorrenal (PR #692 aberto).
- Busca de PRs abertos por reabilitação: sem PR de hub adulto de RC em conflito.
- Tema dos novos markdowns: **Prevenção e lipídios** (canônico). “Reabilitação cardíaca” como `theme` é anomalia (PR #709).

## Entregáveis

1. `doencas/fragmentos/reabilitacao-cardiaca.json` — hub completo, `review_status=pendente_revisao`, `fonte_producao=grok`, `patient_material_slug=null`.
2. `content/Reabilitação_cardíaca/indicacoes-contraindicacoes-e-fases-da-reabilitacao-cardiaca.md`
3. `content/Reabilitação_cardíaca/estratificacao-de-risco-para-exercicio-na-reabilitacao-cardiaca.md`
4. Este relatório.

## related_document_slugs (verificados)

- esc-2026-reabilitacao-cardiaca-sintese-pratica-corvia
- reabilitacao-cardiaca-no-muito-idoso-seguranca-fragilidade-e-adesao
- reabilitacao-cardiaca-e-prescricao-de-exercicio-na-prevencao-secundaria
- exercicio-supervisionado-na-icfer-o-ensaio-hf-action
- prevencao-secundaria-integrada-apos-sindrome-coronariana-aguda
- fluxograma-alta-apos-sca-os-cinco-pilares-modificaveis
- fluxograma-cessacao-do-tabagismo-no-cardiopata-farmacoterapia-e-seguimento
- exercicio-e-intervencao-psicologica-na-depressao-do-cardiopata-upbeat-e-as-revisoes-cochrane
- indicacoes-contraindicacoes-e-fases-da-reabilitacao-cardiaca (novo)
- estratificacao-de-risco-para-exercicio-na-reabilitacao-cardiaca (novo)

## Relações recusadas

- Hub/síndrome cardiorrenal (colisão PR #692)
- Documento pediátrico de RC pós-cirurgia congênita (população distinta do hub adulto)
- Vínculos só por proximidade lexical sem porta clínica de prevenção secundária/RC

## Limitações

- Conteúdo `pendente_revisao` — não publicar até revisão humana.
- Sem doses de fármaco no hub.
- Modelo híbrido/remoto ficou resumido nos docs de indicação/risco + ESC 2026; terceiro markdown opcional não incluído para acelerar entrega.
- Gates de allowlist/editorial-approvals para `pendente_revisao` podem exigir follow-up se CI exigir (padrão atual do repo).

## Gates previstos

- Fragmento via `doencas/fragmentos/` (não edita `metadados.json` gigante).
- Slugs novos resolvem para markdowns deste PR.
- Sem hub cardiorrenal.
