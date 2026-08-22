# Grafo de Conhecimento Clínico Universal

Registro de arquitetura — issue #52, iniciado em 11/08/2026 e atualizado em
21/08/2026 na rodada "Tudo com Tudo" que incorporou doenças especializadas e
triagem por sintomas ao grafo persistido.

## 1. Por que existe, e o que NÃO substitui

O produto já tinha um cruzamento por tema em tempo de consulta —
`backend/app/services/related_content.py` / `GET /api/relacionados`
("Tudo sobre este tema"). **Este módulo não substitui aquele** — os dois
coexistem de propósito:

| | `related_content.py` | Grafo de Conhecimento (`knowledge_graph.py`) |
|---|---|---|
| Quando calcula | Em tempo de requisição, sempre fresco | Backfill persistido |
| Casamento | `theme`/`tema` exato | Arestas tipadas, com proveniência/confiança |
| Direção | Tema → itens | Bidirecional para navegação, direcionada no armazenamento |
| Relações | Mesmo tema | Catálogo semântico + `same_theme` |
| Uso | Painel "Tudo sobre este tema" | Navegação entre objetos específicos, recuperação estruturada e curadoria futura |

A arquitetura evita colunas fixas espalhadas por tabela (`related_medications`,
`related_diseases`, `related_studies`, etc.). Nós e arestas ficam em duas tabelas
genéricas e o conteúdo canônico continua pertencendo às tabelas de origem.

## 2. Schema

```text
knowledge_entities: id, entity_type, canonical_id, slug, title, status,
                    created_at, updated_at
  UNIQUE(entity_type, canonical_id)

knowledge_relations: id, source_entity_id, target_entity_id, relation_type,
                     relevance_score, confidence, provenance_type,
                     evidence_source, review_status, extra (jsonb),
                     created_at, updated_at
  UNIQUE(source_entity_id, target_entity_id, relation_type)
```

Migração `5a786cb55611`: aditiva, sem coluna nova nas tabelas editoriais. A
expansão de tipos desta rodada não exige nova migração porque `entity_type` e
`relation_type` são strings validadas por catálogo em código, não enums SQL.

## 3. Segurança — grafo global ≠ contexto de paciente

`TIPOS_ENTIDADE_PERMITIDOS` (`app/models/knowledge.py`) é um **allowlist
estrutural**, não apenas documentação. `registrar_entidade()` rejeita qualquer
`entity_type` fora do catálogo.

Os **15 tipos permitidos** são conteúdo global/editorial:

1. `documento`
2. `fluxograma`
3. `evidencia`
4. `estudo`
5. `medicamento`
6. `exame`
7. `caso_clinico`
8. `trilha`
9. `galeria`
10. `checklist`
11. `material_paciente`
12. `protocolo_emergencia`
13. `calculadora`
14. `doenca`
15. `triagem_sintoma`

`Patient`, `Prescription`, `Appointment`, `GeneratedDocument`, `ServiceOrder`,
usuário, consulta, agenda ou qualquer outro dado individual **nunca pode virar
nó do grafo global**. O grafo não possui noção de proprietário e, portanto,
inserir dado clínico individual nele produziria risco de exposição entre
usuários.

### Reconciliação de publicação

Um conteúdo retirado do ar não pode continuar navegável pelo grafo. Cada
backfill reconcilia os IDs publicados:

- conteúdo publicado → nó `ativo`;
- conteúdo despublicado/ausente → nó `arquivado`;
- conteúdo republicado → o mesmo nó volta a `ativo`.

As arestas não são apagadas fisicamente: a auditoria de proveniência é
preservada, mas `relacionados_de()` só devolve nós ativos e relações não
rejeitadas.

### Autorização por rota

- `GET /api/grafo/relacionados` exige assinatura ativa;
- `POST /api/admin/grafo/backfill` exige administrador;
- o assinante consulta o resultado, mas não dispara o backfill.

`entity_type` é validado contra o allowlist e consultas ao banco usam SQLAlchemy
parametrizado.

## 4. Catálogo de tipos de relação

A rodada de 21/08/2026 ampliou o catálogo para **20 relações**:

- `treats`
- `indicated_for`
- `contraindicated_in`
- `contraindicated_with`
- `interacts_with`
- `monitor_with`
- `diagnosed_by`
- `supported_by`
- `studied_in`
- `recommended_by`
- `associated_with`
- `causes`
- `may_cause`
- `alternative_to`
- `belongs_to_class`
- `used_in_case`
- `mentioned_in`
- `patient_education_for`
- `differential_for`
- `same_theme`

`registrar_relacao()` rejeita qualquer valor fora desse catálogo.

`differential_for` representa uma relação direcionada do tipo:

```text
(doenca) -[differential_for]-> (triagem_sintoma)
```

Ela significa apenas que a doença está explicitamente listada como diagnóstico
diferencial daquele fluxo/sintoma. Não equivale a probabilidade, indicação de
exame, diagnóstico confirmado ou recomendação terapêutica.

## 5. Proveniência, confiança e revisão

Nenhuma relação deve parecer mais certa do que sua origem permite.

### `confidence`

- `explicit` — relação editorial explicitamente curada;
- `derived` — relação derivada de metadado estruturado determinístico;
- `ai_suggested` — sugestão de IA, nunca promovida automaticamente a fato.

### `provenance_type`

- `editorial`
- `structured_metadata`
- `imported`
- `derived`
- `ai_suggested`
- `clinical_context`

### `review_status`

- `revisado`
- `pendente_revisao`
- `rejeitado`

**Regra desta rodada:** uma relação criada automaticamente a partir de metadado
estruturado permanece `pendente_revisao`, mesmo quando a derivação é totalmente
determinística. Derivação de software não é revisão clínica humana e nunca deve
ser atribuída a uma pessoa específica sem registro documental real.

`evidence_source` recebe PMID/DOI/diretriz quando a aresta representa uma
afirmação científica que exige fonte. Relações puramente estruturais podem ter
`evidence_source=None`; o sistema não inventa uma referência para preencher o
campo.

## 6. `relevance_score` e separação comercial

`relevance_score` (0–1) ordena resultados dentro de cada tipo. Ele expressa
relevância editorial/estrutural — **nunca patrocínio**.

Valores usados pelos backfills atuais:

- `same_theme`: `0.4`;
- doença → documento/fluxograma via `related_document_slugs`: `0.85`;
- material ao paciente → doença via `patient_material_slug`: `0.9`;
- doença → triagem via diferencial exato não ambíguo: `0.8`.

Esses números são pesos de navegação internos, não probabilidades clínicas,
força de recomendação, nível de evidência ou magnitude de efeito.

Camada comercial e camada científica permanecem separadas. Nenhum sinal de
patrocínio participa do cálculo/gravação de `relevance_score`.

## 7. Backfill — duas camadas complementares

`backfill_mesmo_tema()` mantém o nome histórico por compatibilidade, mas agora
executa duas camadas.

### 7.1 Camada clássica: `same_theme`

1. Lê as frentes já cruzadas por `related_content.py`, somente itens
   `published=True`.
2. Registra/atualiza um `KnowledgeEntity` por item.
3. Cria `same_theme` entre tipos diferentes com o mesmo `theme`/`tema`.
4. Limita a densidade a 5 vizinhos por par de tipos para evitar explosão
   cartesiana.
5. Usa `provenance_type=structured_metadata`, `confidence=derived` e
   `review_status=pendente_revisao`.

O casamento continua sendo igualdade de tema; não há heurística de linguagem.

### 7.2 Camada especializada: doença e triagem

Registra todo `SpecialtyDisease` e `SymptomTriageGuide` publicado como nó do
grafo. Em seguida cria **somente** arestas suportadas por campos estruturados já
existentes.

#### Doença → documento/fluxograma

Se `SpecialtyDisease.related_document_slugs` contém um slug que já corresponde a
um nó publicado:

```text
(doenca) -[mentioned_in]-> (documento|fluxograma)
```

A relação é derivada do campo explícito; não é inferida lendo o texto.

#### Material ao paciente → doença

Se `SpecialtyDisease.patient_material_slug` aponta para material publicado:

```text
(material_paciente) -[patient_education_for]-> (doenca)
```

#### Doença → triagem por sintoma

O backfill lê `SymptomTriageGuide.differentials`. Uma aresta automática só é
criada quando o texto do diferencial coincide, após normalização **apenas** de
caixa, acento e espaços, com o nome ou um alias de **uma única** doença
publicada:

```text
(doenca) -[differential_for]-> (triagem_sintoma)
```

Se houver zero correspondências, nada é criado. Se houver mais de uma doença
com o mesmo nome/alias normalizado, a correspondência é ambígua e **nenhuma
aresta automática é criada**.

### O que o backfill NÃO faz

Não usa:

- fuzzy matching;
- embeddings;
- LLM;
- similaridade semântica;
- coocorrência textual como prova clínica;
- geração automática de `treats`, `contraindicated_in`, `diagnosed_by`,
  `recommended_by`, `causes` ou outra afirmação clínica forte.

A existência desses tipos no catálogo não autoriza fabricação automática. Eles
só devem ser preenchidos quando houver metadado/fonte apropriada e processo de
curadoria correspondente.

## 8. Limitação conhecida do corpus — 21/08/2026

A infraestrutura suporta `related_document_slugs` e `patient_material_slug`, mas
o inventário desta rodada encontrou **ausência desses campos no manifesto
canônico atual de doenças**. Portanto, a existência do suporte no grafo não deve
ser confundida com conectividade já preenchida.

Isso é uma lacuna editorial real a ser atacada em rodadas de densificação:

- mapear doenças existentes para documentos/fluxogramas já publicados;
- mapear material ao paciente pertinente;
- deduplicar por slug e conceito antes de gravar qualquer vínculo;
- manter links sem fonte/semântico duvidoso fora do corpus publicável.

## 9. API

### Leitura

`GET /api/grafo/relacionados?entity_type=&slug=&limite_por_tipo=`

Devolve:

```text
{
  entity_type,
  slug,
  titulo,
  grupos: [
    {
      tipo,
      rota_lista,
      total_disponivel,
      itens: [...]
    }
  ],
  total
}
```

A consulta lê arestas nas duas direções, deduplica o mesmo vizinho, ordena por
`relevance_score` e exclui nó arquivado/relação rejeitada.

### Backfill

`POST /api/admin/grafo/backfill`

Exige administrador e registra auditoria `action="grafo_backfill"`.

## 10. Navegação frontend

`frontend/src/components/GrafoRelacionados.tsx` é o painel reutilizável do grafo.
Além das páginas já integradas originalmente, a rodada de 21/08/2026 adiciona:

- `GuiaDoenca.tsx` → `entityType="doenca"`;
- `TriagemSintomas.tsx` → `entityType="triagem_sintoma"`.

A triagem aceita deep-link:

```text
/triagem-sintomas?slug=<slug>
```

Assim uma relação do grafo pode abrir diretamente o fluxo sintomático correto e
o usuário consegue navegar no sentido inverso para os diagnósticos relacionados.

O painel continua complementar: se a consulta falhar ou não houver vizinhos, ele
não substitui nem quebra o conteúdo clínico principal da página.

## 11. Testes e invariantes desta expansão

`backend/tests/test_knowledge_graph_specialty.py` cobre:

- criação de nós `doenca` e `triagem_sintoma`;
- relações derivadas de metadado estruturado;
- `confidence=derived`;
- `review_status=pendente_revisao`;
- navegação para a rota correta;
- recusa de vínculo automático quando alias é ambíguo;
- despublicação arquivando o nó sem apagar a trilha de auditoria;
- independência de publicação entre doença e triagem.

Os testes históricos do grafo continuam cobrindo allowlist de segurança,
idempotência, despublicação/republicação e leitura agrupada.

## 12. Próximas expansões seguras

Prioridades de densificação, sem criar novos silos:

1. preencher `related_document_slugs` e `patient_material_slug` das doenças com
   deduplicação e validação de existência;
2. criar triagens ausentes somente quando representam uma porta sindrômica real
   — por exemplo, bradicardia/pulso lento e fadiga/intolerância ao esforço —
   reutilizando documentos já existentes em vez de duplicá-los;
3. modelar relações de exame → decisão, medicamento → indicação/interação e
   guideline → objeto derivado somente quando a fonte estruturada sustentar a
   afirmação;
4. executar rodadas periódicas de contradição/obsolescência contra diretrizes e
   documentos regulatórios atuais;
5. integrar recuperação por subgrafo ao assistente em uma iteração separada,
   com regressão específica de segurança antes de substituir/complementar RAG;
6. construir visualização de mapa clínico apenas depois que a densidade e a
   qualidade das arestas forem suficientes para que a visualização tenha valor
   clínico, e não apenas efeito visual.

A regra permanece: **Tudo com Tudo, desde que a conexão seja clinicamente
verdadeira, rastreável, útil e proporcional à qualidade da evidência.**
