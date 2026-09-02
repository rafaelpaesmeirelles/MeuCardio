# Vincular Tudo com Tudo — QT longo em terapia oncológica — 29/08/2026

## Contexto da tarefa

A tarefa pedia para enriquecer a ficha `qt-longo-terapia-oncologica` (área
`cardiooncologia`) em `doencas/metadados.json`, que hoje "tem
`related_document_slugs` vazio/ausente, violando a regra Tudo com Tudo", e
listava 6 candidatos em `content/Cardio-oncologia/` a verificar
individualmente.

## Achado principal: a tarefa já estava resolvida antes de começar

O registro **base** de `qt-longo-terapia-oncologica` em
`doencas/metadados.json` de fato não tem `related_document_slugs` (campo
ausente) e está com `completeness: "basico"` — é isso que motivou a
descrição da tarefa, e é o que se vê ao abrir o arquivo diretamente.

Mas o registro **composto** — o que a aplicação realmente lê, via
`load_disease_records()`, que aplica `doencas/correcoes/*.json` por cima da
base — já está completo. O patch dedicado
`doencas/correcoes/zz-release36h-pr656-qt-longo-terapia-oncologica.json`
(mesclado em 28/08/2026, commit `798bb8d5`, "release: integrar e revisar
toda produção científica das últimas 36h", identificado no próprio
`review_note` do patch como "39º lote de conteúdo do dia") já eleva:

- `completeness`: `basico` → `completo`
- `review_status`: → `revisado`
- `version`: → `2`
- `related_document_slugs`: `[]` → **exatamente os 6 documentos** que o
  briefing desta tarefa listou como candidatos a verificar:
  - `prolongamento-de-qt-por-inibidores-de-cdk4-6-ribociclibe-palbociclibe-e-abemaciclibe`
  - `fluxograma-prolongamento-qt-por-ribociclibe-e-risco-de-torsades`
  - `prolongamento-de-qt-e-torsades-por-trioxido-de-arsenio`
  - `fluxograma-prolongamento-de-qt-e-torsades-por-trioxido-de-arsenio`
  - `inibidor-de-menina-revumenibe-prolongamento-de-qtc-e-sindrome-de-diferenciacao`
  - `lista-de-quimioterapicos-de-risco-de-prolongamento-do-qt-e-monitorizacao`

Além disso, o patch traz aprofundamento clínico completo (epidemiologia,
apresentação, abordagem diagnóstica, diferenciais, exames, sinais de
alarme, conduta, fluxo ambulatorial/emergência, monitorização, populações
especiais, perguntas e regras do assistente) — a ficha não é mais um
esqueleto de catalogação.

**Conclusão prática: nenhum vínculo precisou ser adicionado.** A regra
Tudo com Tudo (3-7 links) já está satisfeita no registro composto, um dia
antes de esta tarefa ter sido aberta.

## Verificação feita mesmo assim

Como pedido, os 6 documentos foram lidos por inteiro e verificados
individualmente antes de aceitar o achado acima como suficiente — não bastava
confiar no `review_note` do patch:

- `fluxograma-prolongamento-de-qt-e-torsades-por-trioxido-de-arsenio.md` —
  fluxograma de emergência dedicado a QT/torsades por trióxido de arsênio.
  Central.
- `prolongamento-de-qt-e-torsades-por-trioxido-de-arsenio.md` — protocolo
  completo de monitorização e manejo de QT no trióxido de arsênio. Central.
- `fluxograma-prolongamento-qt-por-ribociclibe-e-risco-de-torsades.md` —
  fluxograma de emergência dedicado a QT por ribociclibe. Central.
- `prolongamento-de-qt-por-inibidores-de-cdk4-6-ribociclibe-palbociclibe-e-abemaciclibe.md`
  — protocolo dedicado ao sinal de QT nos três inibidores de CDK4/6,
  concentrado no ribociclibe. Central.
- `lista-de-quimioterapicos-de-risco-de-prolongamento-do-qt-e-monitorizacao.md`
  — revisão sistemática (Porta-Sánchez et al. 2017) com lista de risco de QT
  por quimioterápico/terapia-alvo e limiares práticos de conduta. Central,
  e **confirmado em `content/Cardio-oncologia/`** (não é tabela de
  referência em `Farmacologia/`, apesar do nome sugerir isso à primeira
  vista — o aviso do briefing sobre esse candidato específico procedia
  como cautela, mas o caminho real do arquivo está correto).
- `inibidor-de-menina-revumenibe-prolongamento-de-qtc-e-sindrome-de-diferenciacao.md`
  — protocolo do revumenibe com alerta em quadro da FDA para QTc/torsades.
  Central.

Nenhum dos 6 resolve para `Farmacologia/`, `Calculadoras/` ou `Exames/` —
todos estão em `content/Cardio-oncologia/`.

## Overlap legítimo com outras fichas

`lista-de-quimioterapicos-de-risco-de-prolongamento-do-qt-e-monitorizacao`
também é `related_document_slugs` de `cardiotoxicidade-bcr-abl`,
`cardiotoxicidade-inibidor-proteassoma` e `cardiotoxicidade-raf-mek` — é
uma referência transversal de risco de QT por classe de fármaco, faz
sentido estar linkada de várias fichas de cardiotoxicidade.

## O que este lote de fato mudou

Nenhuma alteração em `doencas/metadados.json` nem em
`doencas/correcoes/`. Foi adicionado apenas um teste dedicado,
`backend/tests/test_vincular_tudo_com_tudo_qt_longo_terapia_oncologica.py`,
que:

1. documenta o estado da base (sem `related_document_slugs`,
   `completeness: basico`) como ponto de partida factual;
2. trava a existência e o conteúdo exato do patch de correção dedicado
   (`zz-release36h-pr656-qt-longo-terapia-oncologica.json`) que resolve a
   regra por composição;
3. valida o registro composto final (via `load_disease_records`): 6
   `related_document_slugs`, todos resolvendo para documentos narrativos
   reais em `content/Cardio-oncologia/`, sem duplicata, cada um mencionando
   QT/QTc/torsades no texto, e sem sobreposição não documentada com outra
   ficha.

O objetivo é regressão: se o patch de correção for removido, renomeado ou
tiver seu `related_document_slugs` reduzido para menos de 3 no futuro, este
teste falha e sinaliza que a ficha voltou a violar Tudo com Tudo — em vez
de o problema ser descoberto de novo só quando alguém reabrir esta mesma
tarefa.

## Gates

- `scripts/audit_tudo_com_tudo.py` (baseline, sem alteração de conteúdo):
  `broken_references: []`.
- `scripts/content_inventory.py --strict` (baseline): `invalid: []`,
  `missing: []`.
- `backend/tests/test_vincular_tudo_com_tudo_qt_longo_terapia_oncologica.py`:
  8 testes, todos passando.
- `backend/tests/test_disease_fragments_canonical.py`: passando, sem
  necessidade de allowlist (ficha já `revisado`).
- `backend/tests/test_canonical_content_review_status.py`: passando, sem
  necessidade de allowlist (ficha já `revisado`, sem exceção).
- `app.main` importa sem erro.
- `review_status` e `completeness` não foram alterados por este lote — já
  estavam corretos via o patch de 28/08/2026, e a instrução explícita desta
  tarefa era não tocar neles.

## Nota para decisão editorial

Diferente das duas outras PRs de hoje desta frente (persistência do canal
arterial, atresia pulmonar), aqui não há falha de gate a documentar nem
vínculo novo a revisar — o trabalho de vínculo já havia sido feito e
revisado no lote científico de 28/08/2026. Sinalizo apenas que o texto da
tarefa (baseado em inspeção do arquivo base) ficou desatualizado em relação
ao estado real do produto assim que o patch de correção foi mesclado;
pode valer a pena, para tarefas futuras desta frente, checar o registro
composto (via `load_disease_records`) antes de listar uma ficha como
pendente, em vez de inspecionar apenas `doencas/metadados.json` bruto.
