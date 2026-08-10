# Grafo de Conhecimento Clínico Universal

Registro de arquitetura — issue #52 (nova fase: Medicamentos + inteligência
regulatória/preços + Knowledge Graph), 11/08/2026.

## 1. Por que existe, e o que NÃO substitui

O produto já tinha um cruzamento por tema em tempo de consulta —
`backend/app/services/related_content.py` / `GET /api/relacionados`
(pedido do Rafael, 08/08/2026, "Tudo sobre este tema"). **Este módulo não
substitui aquele** — os dois coexistem de propósito:

| | `related_content.py` | Grafo de Conhecimento (`knowledge_graph.py`) |
|---|---|---|
| Quando calcula | Em tempo de requisição, sempre fresco | Backfill assíncrono, persistido |
| Casamento | `theme`/`tema` == exato | Arestas tipadas, com proveniência/confiança |
| Direção | Um sentido (tema → itens) | Bidirecional para navegação, direcionada no armazenamento |
| Tipos de relação | Um só ("mesmo tema") | Catálogo de 19 tipos semânticos |
| Uso pretendido | Painel "Tudo sobre este tema" nas páginas de detalhe (já em produção) | Recuperação estruturada para a IA (subgrafo), navegação "de todo lugar", futura curadoria editorial de relações mais específicas que "mesmo tema" |

O pedido explícito era **não** implementar como coluna fixa por tabela
(`related_medications`, `related_diseases`, ... espalhados não escala) — é
essa abstração genérica que as duas tabelas novas resolvem.

## 2. Schema

```
knowledge_entities: id, entity_type, canonical_id, slug, title, status,
                     created_at, updated_at
  UNIQUE(entity_type, canonical_id)

knowledge_relations: id, source_entity_id, target_entity_id, relation_type,
                      relevance_score, confidence, provenance_type,
                      evidence_source, review_status, extra (jsonb),
                      created_at, updated_at
  UNIQUE(source_entity_id, target_entity_id, relation_type)
```

Migração `5a786cb55611` (aditiva, sem coluna nova em tabela existente, sem
dado a migrar — as duas tabelas nascem vazias, populadas só pelo backfill).
Testada: DB vazio, DB com estado existente, idempotência (rerun não falha),
downgrade + re-upgrade.

## 3. Segurança — grafo global ≠ contexto de paciente (issue #52, §26-27)

**`TIPOS_ENTIDADE_PERMITIDOS`** (`app/models/knowledge.py`) é um allowlist
estrutural, não documental: `registrar_entidade()` levanta
`TipoEntidadeNaoPermitido` para qualquer `entity_type` fora dos 13 valores
de conteúdo global/editorial (documento, fluxograma, evidência, estudo,
medicamento, exame, caso clínico, trilha, galeria, checklist, material do
paciente, protocolo de emergência, calculadora). `Patient`, `Prescription`,
`Appointment`, `GeneratedDocument`, `ServiceOrder` — qualquer entidade com
dado de paciente/consulta/prescrição individual — **nunca pode entrar**,
testado em `test_registrar_entidade_rejeita_tipo_fora_do_allowlist`.

Isso fecha a mesma classe de risco que o IDOR/BOLA desta fase corrigiu na
camada REST (`app/services/clinical_ownership.py`) — só que na camada do
grafo: sem o allowlist, um backfill mal desenhado poderia transformar cada
paciente/prescrição num nó público, navegável por QUALQUER médico
autenticado (o grafo não tem — e não deve ter — noção de "dono").

**Reconciliação de conteúdo despublicado**: um item que foi retirado do ar
depois de já ter sido indexado no grafo não pode continuar aparecendo nas
consultas — mesma regra já em vigor para RAG/busca/`related_content`
(histórico documentado em `CLAUDE.md`, "RAG entregava conteúdo NÃO
PUBLICADO"). Cada `backfill_mesmo_tema()` arquiva (`status='arquivado'`,
nunca `DELETE`) o nó cujo conteúdo de origem deixou de estar publicado, e
`relacionados_de()` só considera nó com `status='ativo'` — tanto como
origem quanto como alvo da consulta. Testado (`test_backfill_arquiva_
entidade_de_conteudo_despublicado`, `test_backfill_reativa_entidade_de_
conteudo_republicado`).

**Autorização por rota**: `GET /api/grafo/relacionados` exige assinatura
ativa (mesma régua de qualquer outra frente de conteúdo —
`Depends(assinante_ativo)`, `ROUTERS_ASSINANTES`); `POST
/api/admin/grafo/backfill` exige admin (`Depends(require_admin)`) — o
assinante comum nunca dispara o backfill, só lê o resultado. Testado pela
rota HTTP real (`test_knowledge_graph_api.py`): 401 sem token, 402 sem
assinatura, 403 backfill sem ser admin, 200 nos casos válidos.

**Injeção**: `entity_type`/`slug` chegam como query params, `entity_type`
validado contra o allowlist antes de qualquer query (422 se desconhecido);
todo acesso ao banco usa SQLAlchemy ORM parametrizado
(`select(...).where(Modelo.campo == valor)`) — nenhuma concatenação de SQL
com entrada do usuário em nenhum ponto deste módulo.

## 4. Catálogo de tipos de relação

19 valores em `TIPOS_RELACAO_PERMITIDOS` (`app/models/knowledge.py`) —
`treats`, `indicated_for`, `contraindicated_in`, `contraindicated_with`,
`interacts_with`, `monitor_with`, `diagnosed_by`, `supported_by`,
`studied_in`, `recommended_by`, `associated_with`, `causes`, `may_cause`,
`alternative_to`, `belongs_to_class`, `used_in_case`, `mentioned_in`,
`patient_education_for`, `same_theme`. `registrar_relacao()` rejeita
(`ValueError`) qualquer valor fora da lista — evita a proliferação caótica
que o pedido pediu para prevenir.

**Hoje, só `same_theme` tem implementação de backfill** (derivado do mesmo
casamento por tema de `related_content.py`). Os outros 18 tipos existem no
catálogo para relação **editorial** futura (ex.: um curador registrar
`sacubitril-valsartana --[studied_in]--> paradigm-hf`, com PMID em
`evidence_source`) — não há hoje nenhuma fonte automática que os produza
sem risco de fabricar uma afirmação clínica não verificada, e "nada
fabricado" continua sendo a régua inegociável do projeto.

## 5. Proveniência e confiança (issue #52, §23-24)

Três níveis de confiança, nunca implícitos:

- **`explicit`** (editorial, alta confiança) — relação redigida/revisada
  por humano com fonte científica declarada.
- **`derived`** (derivado estruturalmente) — calculado a partir de campo já
  existente (hoje, só `same_theme`: dois itens do mesmo `theme`/`tema`).
- **`ai_suggested`** — sugerido por IA. **Nunca promovido automaticamente a
  fato** — `review_status` nasce `pendente_revisao` para qualquer relação
  não editorial, e só vira `revisado` por ação humana (ou por regra
  determinística auditável, como a reconciliação de despublicação).

`provenance_type` (editorial | structured_metadata | imported | derived |
ai_suggested | clinical_context) documenta a ORIGEM do dado;
`evidence_source` carrega PMID/DOI/diretriz quando a relação for uma
afirmação científica — `None` para relação estrutural (`same_theme`), nunca
fabricado para preencher o campo.

## 6. `relevance_score` e patrocínio (issue #52, §25, 39)

`relevance_score` (0.0-1.0) ordena os resultados de `relacionados_de()`
(mais relevante primeiro, dentro do limite por tipo). Hoje, o único
produtor é o backfill de `same_theme` (score fixo `0.4` — estrutural, não
editorial). **Patrocínio nunca altera este campo** — não há, em nenhum
ponto do código, um caminho que leia dado de patrocínio antes de calcular
ou gravar `relevance_score`. Isto continua sendo uma decisão de
arquitetura, não apenas de política: como não existe hoje nenhuma tabela de
patrocínio ligada ao grafo, a separação é automática por ausência de
acoplamento — no dia em que patrocínio for modelado, a regra a preservar é
a mesma já documentada em `docs/pricing-architecture.md` §6: camada
comercial e camada científica permanecem estruturalmente separadas, e
`relevance_score` só é escrito por proveniência `derived`/`explicit`/
`ai_suggested`, nunca por um sinal comercial.

## 7. Backfill — o que faz, o que não faz

`backfill_mesmo_tema()` (`POST /api/admin/grafo/backfill`, admin):

1. Lê as mesmas 12 frentes de conteúdo de `related_content.py` (documento,
   fluxograma, evidência, estudo, medicamento — convenção Farmacologia,
   exame, caso clínico, trilha, galeria, calculadora, protocolo de
   emergência, checklist, material do paciente), só itens `published=True`.
2. Registra/atualiza um `KnowledgeEntity` por item (upsert idempotente).
3. Cria arestas `same_theme` entre itens do mesmo tema, **limitadas a 5 por
   par de tipos vizinhos** (`LIMITE_BACKFILL_POR_TIPO_VIZINHO`) — evita
   explosão cartesiana num tema com centenas de itens; "tudo relacionado
   com tudo" não significa conectar cada nó a todos os outros do mesmo
   tema (issue #52, §42).
4. Arquiva (nunca apaga) nó cujo conteúdo de origem deixou de ser
   publicado; reativa nó cujo conteúdo voltou a ser publicado.
5. Idempotente e não-destrutivo do início ao fim: rodar de novo nunca
   duplica aresta/nó (`UniqueConstraint`), nunca `DELETE`, e uma relação já
   marcada `revisado` por curadoria humana sobrevive a qualquer rerun
   (testado em `test_backfill_nunca_apaga_relacao_existente`).

**O que o backfill explicitamente não faz**: não gera nenhum dos 18 tipos
de relação semântica além de `same_theme` — fazer isso automaticamente
exigiria inferir uma afirmação clínica (ex.: "medicamento X trata doença
Y") a partir de texto livre, o que é exatamente o tipo de fabricação que a
régua de qualidade do projeto proíbe. Esse trabalho fica para curadoria
editorial futura, alimentando o mesmo catálogo de tipos já pronto.

## 8. API

- `GET /api/grafo/relacionados?entity_type=&slug=&limite_por_tipo=` —
  leitura, exige assinatura ativa. Devolve `{entity_type, slug, titulo,
  grupos: [{tipo, rota_lista, total_disponivel, itens: [...]}], total}`,
  ordenado por `relevance_score` decrescente dentro de cada grupo, paginado
  por `limite_por_tipo` (padrão 5, máx. 20). Item fora do grafo (ou
  arquivado) devolve `grupos: []`, nunca erro.
- `POST /api/admin/grafo/backfill` — admin, dispara o backfill descrito
  acima, grava `AuditLog` (`action="grafo_backfill"`).

## 9. Deliberadamente fora do escopo desta fase

- **Frontend "Relacionados" dedicado ao grafo.** O painel `TudoSobreEsteTema`
  já em produção continua sendo a superfície visível do usuário; a API do
  grafo está pronta para alimentar uma versão futura mais rica (ordenada
  por relevância, com tipos de relação semânticos), mas plugar isso na UI
  não estava no crítico desta rodada de reconciliação — é o próximo passo
  natural, não um requisito de segurança/correção do RC.
- **Retrieval por subgrafo para a IA** (issue #52, §32) — a API de leitura
  já existe e pode ser chamada pelo mesmo serviço de RAG; a integração em
  si (trocar/complementar a busca textual do assistente por uma consulta ao
  grafo) fica para uma iteração dedicada, para não introduzir risco de
  regressão no Assistente Clínico já em produção sem tempo de regressão
  completa dedicado a essa mudança específica.
- **Visualização "Mapa Clínico"** (§33) — o modelo já suporta (nós/arestas
  tipados, paginação, relevância); nenhuma UI de grafo interativo foi
  construída nesta fase, por não ser requisito do release.
- **Relações semânticas além de `same_theme`** — ver seção 7.
