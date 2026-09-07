# Correção de 3 anomalias de tema no mecanismo "Tudo com Tudo" — 29/08/2026

## Contexto

O mecanismo "Tudo com Tudo" (`backend/app/services/related_content.py`,
`GET /api/relacionados?tema=...`) cruza conteúdo publicado de onze frentes do
ecossistema Corvia (documentos, evidências, estudos, casos clínicos, trilhas,
galeria, exames, checklists de alta, materiais do paciente, calculadoras,
protocolos de emergência) sempre pela mesma regra: `campo == tema`, string
exata, sem normalização de acento, maiúscula/minúscula ou espaço (ver
`CLAUDE.md`, "Regra permanente: todo conteúdo novo precisa nascer com tema").

Uma auditoria completa do corpus, em 29/08/2026, comparou todos os valores de
`theme`/`tema` em uso contra o vocabulário canônico e encontrou 3 registros
grafados fora dele — cada um o único item do repositório usando aquele
valor, portanto invisível ao próprio painel "Tudo sobre este tema": um silo
de 1 item cada, exatamente o efeito que a regra do CLAUDE.md existe para
prevenir. A auditoria também encontrou que o comentário de módulo de
`related_content.py` (linhas ~34-42, antes desta correção) descrevia duas
anomalias antigas — já corrigidas nos commits `fa69c196` (20/08/2026) e
`ad987532` (25/08/2026) — como se ainda estivessem pendentes, e citava "29
temas canônicos" quando o total real hoje é 30 (a área "Cardiologia do
Esporte e do Exercício", formalizada em 08/08/2026, é tema legítimo, usado
consistentemente em 221 registros — não é anomalia, só não tinha sido
somada ao número do comentário).

## Como a contagem de 30 temas canônicos foi confirmada

Contagem de todos os valores distintos de `theme`/`tema` em uso em
`content/**/*.md` (front-matter) e nos manifestos JSON de
`evidencias`, `estudos`, `casos-clinicos`, `trilhas`, `checklists`,
`exames`, `galeria` e `material-paciente`: 33 valores distintos. Descontados
os 3 valores de uso único e fora do padrão corrigidos abaixo (`Cardiorrenal`,
`Reabilitação cardíaca`, `Emergências cardiovasculares`), restam **30**
temas canônicos — cada um usado de forma consistente por dezenas a
centenas de registros em várias frentes.

## Os 3 achados e a correção aplicada

### 1. `documents` — `esc-2026-doenca-cardiovascular-e-doenca-renal-cronica-stamp-on-ckd`

- Arquivo: `content/Cardiorrenal/esc-2026-doenca-cardiovascular-e-doenca-renal-cronica-stamp-on-ckd.md`
- `theme` antes: `"Cardiorrenal"` (único uso desse valor em todo o repositório)
- `theme` depois: **`"Insuficiência cardíaca"`**
- Justificativa: o documento trata da interação DCV/DRC e do impacto no
  manejo da insuficiência cardíaca (dose de fármacos, uso de contraste,
  diálise); "Cardiorrenal" nunca foi formalizado como tema — a pasta em
  `content/` foi criada apenas para este arquivo isolado.

### 2. `documents` — `esc-2026-reabilitacao-cardiaca-sintese-pratica-corvia`

- Arquivo: `content/Reabilitação_cardíaca/esc-2026-reabilitacao-cardiaca-sintese-pratica-corvia.md`
- `theme` antes: `"Reabilitação cardíaca"` (único uso desse valor em todo o repositório)
- `theme` depois: **`"Prevenção e lipídios"`**
- Justificativa: há precedente direto — o documento irmão sobre o mesmo
  assunto, `content/Prevenção_e_lipídios/reabilitacao-cardiaca-e-prescricao-de-exercicio-na-prevencao-secundaria.md`,
  já usa `"Prevenção e lipídios"` como tema canônico.

### 3. `patient_materials` — `colapso-subito-como-reconhecer-parada-e-usar-o-dea`

- Arquivo: `material-paciente/metadados.json`
- `tema` antes: `"Emergências cardiovasculares"` (único uso desse valor em todo o repositório)
- `tema` depois: **`"Terapia intensiva"`**
- Justificativa: o `documento_slug` referenciado,
  `parada-cardiorrespiratoria-no-adulto-suporte-avancado-sbc-2019`
  (`content/Terapia_intensiva/`), usa `theme: "Terapia intensiva"`; os
  outros 13 materiais do paciente sobre parada cardíaca/UTI já usam esse
  mesmo valor.

Nenhum texto clínico foi alterado — as três correções tocam exclusivamente o
campo `theme`/`tema`.

## Comentário de módulo atualizado

`backend/app/services/related_content.py` (bloco de abertura) foi ajustado
para:
- contar 30 temas canônicos, não mais 29, e explicar a inclusão de
  "Cardiologia do Esporte e do Exercício" como tema legítimo (formalizado
  08/08/2026, 221 registros);
- registrar que as duas anomalias antigas documentadas ali (`patient_materials`
  com `"Doença arterial coronariana"` e `documents` com `"Choque
  cardiogênico"`) já foram corrigidas, nos commits `fa69c196` (20/08/2026) e
  `ad987532` (25/08/2026) respectivamente — em vez de descrevê-las como
  pendentes;
- registrar esta nova auditoria (29/08/2026) e os 3 silos que ela encontrou
  e corrigiu.

## Verificação

- `python3 scripts/content_inventory.py` — sem arquivos/coleções ausentes ou
  inválidos; contagem de registros de `content/` e `material-paciente/`
  inalterada (a correção não adiciona nem remove item algum, só corrige um
  valor de campo em 3 registros existentes).
- Suíte de testes do backend relacionada a `related_content.py`/"tudo com
  tudo" (`pytest tests/test_relacionados.py` e demais `test_tudo_com_tudo_*`,
  `test_vinculo_tudo_com_tudo_*`) — sem regressão.
- Novo teste de regressão dedicado:
  `backend/tests/test_correcao_anomalias_tema_tudo_com_tudo_20260829.py` —
  lê os 3 registros corrigidos diretamente do disco e trava o valor de tema
  esperado, além de confirmar que os 3 valores anômalos não sobrevivem em
  nenhum outro lugar do corpus.

## Escopo

Correção de metadado puro. Nenhum conteúdo clínico novo foi fabricado, nenhum
texto de documento ou material foi reescrito — apenas o campo de tema dos 3
registros listados acima e o comentário de módulo desatualizado em
`related_content.py`.
