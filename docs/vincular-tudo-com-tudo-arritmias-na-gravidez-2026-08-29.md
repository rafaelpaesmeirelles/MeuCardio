# Vincular Tudo com Tudo — Arritmias na gravidez — 29/08/2026

## Achado principal: a violação relatada não existe no registro composto

A tarefa foi aberta a partir da leitura do registro-base `arritmias-na-gravidez`
(área `gravidez`) diretamente em `doencas/metadados.json`, onde o campo
`related_document_slugs` está de fato **ausente**.

Mas o registro efetivamente servido pela aplicação (e pelos gates de
auditoria) passa por `load_disease_records`, que aplica correções aditivas
de `doencas/correcoes/*.json` por cima da base. Já existe, mesclada em
`origin/main`, a correção `doencas/correcoes/zz-release36h-pr663-arritmias-na-gravidez.json`
— parte da PR #663, integrada no commit "release: integrar e revisar toda
produção científica das últimas 36h" (`798bb8d5`). Essa correção faz `set`
(substituição incondicional) de praticamente todo o registro, incluindo:

- `completeness: "completo"` (era `"intermediario"` na base)
- `review_status: "revisado"`, `version: 2`
- `related_document_slugs` com **7 vínculos** — dentro do teto de 3 a 7 da
  regra Tudo com Tudo

Verificado diretamente via `load_disease_records`:

```
related_document_slugs: [
  'taquiarritmia-na-gestacao-com-instabilidade-hemodinamica',
  'fibrilacao-atrial-de-inicio-na-gestacao-incidencia-causas-e-controle-agudo',
  'bradicardia-sintomatica-e-bloqueio-av-de-alto-grau-na-gestacao',
  'taquicardia-ventricular-polimorfica-catecolaminergica-na-gestacao-e-puerperio',
  'sindrome-do-qt-longo-e-risco-arritmico-no-puerperio',
  'arritmias-maternas-desfechos-cardiacos-perinatais-epic-cosmos-2026',
  'pre-eclampsia-grave-hellp-e-arritmias-supraventriculares-na-gestacao',
]
```

Ou seja: **a regra "Tudo com Tudo" já estava satisfeita** antes deste lote
começar. `scripts/audit_tudo_com_tudo.py` e `scripts/content_inventory.py
--strict` já passavam limpos para este slug na baseline (`origin/main`
antes de qualquer mudança deste lote), e `test_canonical_content_review_status.py`
já via o registro como `revisado`.

## Por que nenhuma edição de conteúdo foi feita

Editar `related_document_slugs` (ou qualquer outro campo coberto pelo `set`
da correção) diretamente na base `doencas/metadados.json` seria **inócuo**:
a mecânica de composição (`_apply_corrections` em
`backend/app/services/disease_manifest.py`) sobrescreve incondicionalmente
qualquer chave presente em `set`, na ordem dos arquivos de
`doencas/correcoes/`. Qualquer valor que eu escrevesse na base para essa
chave seria descartado na composição final servida pela aplicação e pelos
gates — daria a falsa impressão de trabalho novo sem nenhum efeito real.

Verificação dos 6 candidatos apontados na tarefa (todos lidos por completo,
confirmando foco em arritmia **materna**, não fetal):

| Candidato | Já vinculado pela correção pr663? |
|---|---|
| `pre-eclampsia-grave-hellp-e-arritmias-supraventriculares-na-gestacao` | Sim |
| `arritmias-maternas-desfechos-cardiacos-perinatais-epic-cosmos-2026` | Sim |
| `taquiarritmia-na-gestacao-com-instabilidade-hemodinamica` | Sim |
| `taquicardia-ventricular-polimorfica-catecolaminergica-na-gestacao-e-puerperio` | Sim |
| `fluxograma-taquiarritmia-na-gestacao-com-instabilidade-hemodinamica` | Não — par irmão do item acima (mesmo caso clínico, formato de árvore de decisão) |
| `fluxograma-taquicardia-ventricular-polimorfica-catecolaminergica-na-gestacao-e-puerperio` | Não — par irmão do item acima |

Os 2 fluxogramas não entraram porque o registro composto já está no **teto
de 7 vínculos** da regra Tudo com Tudo. Adicioná-los exigiria remover um
vínculo já revisado e publicado, o que está fora do escopo deste lote (o
mandato era só adicionar, não substituir vínculos existentes).

Os 2 vínculos restantes da correção pré-existente
(`fibrilacao-atrial-de-inicio-na-gestacao-incidencia-causas-e-controle-agudo`
e `bradicardia-sintomatica-e-bloqueio-av-de-alto-grau-na-gestacao`) não
estavam na lista de candidatos da tarefa, mas foram conferidos por leitura
direta: ambos centrais em arritmia materna na gestação, ambos em
`content/Gravidez/`, nenhum em `Farmacologia/Calculadoras/Exames`.

## O que este lote entrega

Apenas um teste de regressão novo,
`backend/tests/test_vincular_tudo_com_tudo_arritmias_na_gravidez.py` (7
testes), que trava o estado já correto e documenta o mecanismo de
composição — para que trabalho futuro não tente "consertar" de novo algo
que já está corrigido, e para detectar se algum dia a correção pr663 for
removida/alterada sem que o vínculo seja preservado.

Nenhum campo de `doencas/metadados.json` foi alterado.
`review_status` e `completeness` não foram tocados (nem precisariam: já
estavam corretos no registro composto).

## Gates

- `scripts/audit_tudo_com_tudo.py`: `broken_references: []` (baseline e
  após o lote, sem diferença).
- `scripts/content_inventory.py --strict`: `invalid: []`, `missing: []`
  (baseline e após o lote, sem diferença).
- `backend/tests/test_vincular_tudo_com_tudo_arritmias_na_gravidez.py`: 7
  testes, todos passando.
- `backend/tests/test_disease_fragments_canonical.py`: 3 testes, passando
  (baseline, sem alteração).
- `backend/tests/test_canonical_content_review_status.py`: 3 testes,
  passando (baseline, sem alteração — o slug já era `revisado`
  antes deste lote, nenhuma allowlist de pendência foi necessária).
- `app.main` importa sem erro.
- Sem drift contra `origin/main` (branch aberta a partir do HEAD atual).

Total: 13 testes executados neste lote, 13 passando. Nenhuma falha
preexistente encontrada nos gates para este slug.
