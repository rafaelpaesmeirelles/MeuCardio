# Verbete novo — Emergência hipertensiva — 29/08/2026

## Contexto

A ficha existente `hipertensao-arterial-sistemica` trata exclusivamente da
HAS crônica ambulatorial. A crise/emergência hipertensiva aguda — lesão de
órgão-alvo em curso, tema central de UCO/emergência — não tinha ficha
própria em `doencas/metadados.json`, apesar de corpus já rico e existente
em `content/Hipertensão/` (protocolo geral de emergência hipertensiva e
triagem de hipertensão secundária, fluxograma detalhado por síndrome-alvo,
fluxograma de crise adrenérgica do feocromocitoma, testes confirmatórios
de aldosteronismo primário/feocromocitoma, tetos e toxicidade de
nitroprussiato pela bula brasileira).

Criado via `doencas/fragmentos/emergencia-hipertensiva.json` — **não** via
edição direta do arquivo `doencas/metadados.json` — para minimizar colisão
com outras frentes de produção concorrentes rodando em paralelo no mesmo
checkout nesta data.

## Conteúdo produzido (verbete completo, do zero)

- `summary`/`epidemiology`: distinção operacional emergência (lesão aguda
  de órgão-alvo) vs. urgência hipertensiva (sem lesão aguda), sem
  extrapolar prevalência internacional para o Brasil.
- `presentation` (10): fenótipos de lesão de órgão-alvo — encefalopatia
  hipertensiva, edema agudo de pulmão hipertensivo, dissecção aórtica,
  síndrome coronariana aguda, lesão renal aguda, eclâmpsia, déficit
  neurológico focal, alteração visual aguda, crise adrenérgica por
  catecolaminas.
- `diagnostic_approach` (dict aninhado, 3 eixos): diferenciação
  emergência/urgência, avaliação inicial e investigação etiológica
  dirigida quando sugerido (feocromocitoma/paraganglioma, aldosteronismo
  primário, estenose de artéria renal por displasia fibromuscular).
- `differentials` (8), `tests` (9), `red_flags` (8).
- `ambulatory_flow` (5, para a urgência hipertensiva) e `emergency_flow`
  (14, detalhado por síndrome-alvo — cerne da ficha).
- `treatment_summary`: lógica de redução gradual e controlada da pressão
  por síndrome-alvo (dissecção exige queda rápida com controle de FC
  primeiro; AVC isquêmico tolera mais; HIC tem janela estreita de
  evidência; EAP evita betabloqueio na descompensação instável; gestação
  associa magnésio; catecolaminas nunca recebem betabloqueio antes do
  bloqueio alfa) — sem nenhum valor numérico de infusão de fármaco.
- `monitoring` (6), `special_populations` (6, incluindo gravidez/eclâmpsia
  e feocromocitoma).
- `assistant_questions` (9), `assistant_rules` (10, a maioria com
  `risk: "emergencia"` dado o tema; prioridades até 100).
- `related_document_slugs` (5, do zero).
- `patient_material_slug` preenchido:
  `quando-a-pressao-alta-e-uma-emergencia`.

## Verificação de citações

11 referências / 12 PMIDs verificados individualmente via NCBI e-utils
(`esummary.fcgi`) antes de persistir: diretriz AHA/ACC 2025 de HAS,
posicionamento da ESC 2019 sobre emergências hipertensivas (+ corrigendum
de doses), diretriz ACC/AHA 2022 de doença da aorta, diretrizes AHA/ASA de
AVC isquêmico (2019) e hemorragia intracerebral (2022), ACOG Committee
Opinion 767, diretriz da Endocrine Society 2014 de PPGL (confirmada como
**formalmente retirada** em 02/12/2022, sem diretriz de reposição — aviso
de retratação também verificado individualmente), Whitelaw et al. 2014 e
Scholten et al. 2013 sobre crise de feocromocitoma, e o ensaio CLUE
(nicardipina vs. labetalol) — cujo PMID foi obtido por conversão do PMCID
citado na fonte secundária local e então verificado individualmente.

## Verificações feitas na montagem

- Os 5 `related_document_slugs` foram lidos por completo e verificados
  individual e programaticamente quanto à resolução, ao escopo (nenhum em
  `content/Farmacologia/`, `content/Calculadoras/` ou `content/Exames/`) e
  à menção explícita ao tema no texto.
- **Nitroprussiato**: o documento
  `nitroprussiato-na-emergencia-hipertensiva-tetos-e-toxicidade-pela-bula-brasileira.md`
  está fisicamente em `content/Hipertensão/` (não em `content/Farmacologia/`,
  onde existe apenas o verbete geral `nitroprussiato-de-sodio.md`, não
  usado como link) — incluído por discutir centralmente segurança e
  retirada do fármaco no contexto da emergência hipertensiva, sem que
  nenhuma dose sua tenha sido reproduzida na ficha.
- **Excluído por centralidade insuficiente**:
  `feocromocitoma-preparo-pre-operatorio-com-bloqueio-alfa-o-ensaio-prescript.md`
  trata do preparo pré-operatório **eletivo** (fase distinta da crise
  aguda) — mais periférico ao tema "emergência hipertensiva"
  propriamente dito; não foi necessário nem como leitura de apoio para
  nenhum campo desta ficha.
- Sem overlap de `related_document_slugs` com `hipertensao-arterial-sistemica`
  (que lista apenas documentos sobre diagnóstico/classificação/metas
  crônicas) — verificado programaticamente via `load_disease_records()`.
- `patient_material_slug` confirmado por correspondência exata em
  `material-paciente/metadados.json` (`documento_slug` do material aponta
  para o protocolo geral desta mesma ficha).
- Nenhuma dose de fármaco (nem de nitroprussiato) em nenhum campo — apenas
  metas de pressão (mmHg) e frequência cardíaca (bpm) definidas por
  diretriz, sem velocidade de infusão nem dose de ataque/máxima.

## Riscos e limitações

- Registro fica `review_status: "pendente_revisao"` — não publica até
  revisão humana; aval de publicação deste lote não foi obtido.
- `test_canonical_content_review_status.py::test_manifestos_canonicos_so_tem_pendencias_explicitamente_aprovadas_para_rc`
  **falha intencionalmente** para este registro — comportamento esperado
  e documentado, não contornado. O slug foi adicionado a
  `PENDENTES_LOTES_TUDO_COM_TUDO` apenas para uso por
  `test_disease_fragments_canonical.py`, seguindo exatamente o padrão do
  PR #698 (`cardiomiopatia-de-takotsubo`, 29/08/2026).
- A diretriz da Endocrine Society de 2014 sobre PPGL está formalmente
  retirada (sem diretriz de reposição publicada); usada apenas para a
  regra de segurança "nunca betabloqueador antes de bloqueio alfa" e
  conduta cirúrgica diferida, corroboradas por fontes independentes
  posteriores (Whitelaw 2014, Scholten 2013).

## Gates

- `scripts/audit_tudo_com_tudo.py`: sem referências quebradas para este
  registro.
- `scripts/content_inventory.py --strict`: sem entradas inválidas/faltantes
  para este registro.
- `backend/tests/test_novo_verbete_emergencia_hipertensiva.py`: 13 testes
  dedicados.
- `backend/tests/test_disease_fragments_canonical.py`: passando.
- `backend/tests/test_canonical_content_review_status.py`: **1 falha
  esperada e documentada** (`emergencia-hipertensiva`, `pendente_revisao`).
- `python -c "import app.main"`: importa sem erro.

## Branch e PR

Branch `claude/novo-verbete-emergencia-hipertensiva-20260829`, baseada em
`origin/main` no momento do commit.
