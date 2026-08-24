# Tudo com Tudo — round 6 (2026-08-21)

## Objetivo desta rodada

Densificar o grafo clínico antes de ampliar volume editorial. O inventário mostrou que duas frentes estruturadas já existentes — Guia de Doenças (`SpecialtyDisease`) e Triagem de Sintomas (`SymptomTriageGuide`) — não participavam do grafo persistido, embora sejam conteúdo científico global, versionado e publicável.

Criar novos textos sem fechar essa lacuna perpetuaria silos: uma doença poderia citar documentos e material ao paciente; uma triagem poderia listar diferenciais; mas essas relações não seriam navegáveis pelo mecanismo "Tudo com Tudo".

## Achados do inventário

1. O grafo persistido aceitava 13 tipos editoriais, mas não `doenca` nem `triagem_sintoma`.
2. O backfill automático derivava somente `same_theme` a partir de igualdade exata de `theme`/`tema`.
3. `SpecialtyDisease` já possui metadado explícito útil para relações: `related_document_slugs` e `patient_material_slug`.
4. `SymptomTriageGuide` já possui `differentials`, mas o catálogo do grafo não tinha uma relação específica para representar diagnóstico diferencial.
5. A interface do Guia de Doenças e da Triagem não exibia `GrafoRelacionados`.
6. A triagem de síncope já cobre pré-síncope; portanto criar uma segunda triagem de "tontura/presíncope" seria duplicação semântica.
7. Permanecem lacunas úteis de entrada sindrômica, em especial fadiga/intolerância ao esforço e pulso lento/bradicardia, que devem ser trabalhadas em lote científico próprio e não misturadas à mudança de infraestrutura.

## Implementação

### Novos tipos de entidade

- `doenca`
- `triagem_sintoma`

Ambos referenciam exclusivamente tabelas de conteúdo global. Nenhuma entidade de paciente, consulta, prescrição, usuário ou agenda foi adicionada ao allowlist.

### Nova relação

- `differential_for`: uma doença está explicitamente listada como diagnóstico diferencial de uma triagem/sintoma.

### Relações automáticas permitidas nesta rodada

O backfill especializado só usa metadado estruturado existente:

- `SpecialtyDisease.related_document_slugs` → `doenca -[mentioned_in]-> documento/fluxograma`;
- `SpecialtyDisease.patient_material_slug` → `material_paciente -[patient_education_for]-> doenca`;
- `SymptomTriageGuide.differentials` → `doenca -[differential_for]-> triagem_sintoma`, **somente** quando o diferencial coincide exatamente, após normalização de caixa/acento/espaços, com um nome ou alias único de doença publicada.

Não são usados fuzzy matching, embeddings, LLM, similaridade semântica ou inferência por coocorrência. Se um nome/alias é ambíguo, nenhuma aresta é criada automaticamente.

## Proveniência e revisão

Toda relação derivada nesta rodada recebe:

- `provenance_type = structured_metadata`;
- `confidence = derived`;
- `review_status = pendente_revisao`.

Derivação determinística não é tratada como revisão clínica humana. O sistema não atribui revisão a Rafael Paes Meirelles nem a qualquer outra pessoa sem registro documental correspondente.

## Publicação e reversibilidade

Somente doenças e triagens com `published = true` entram como nós ativos. Se um item for despublicado, o nó é arquivado no backfill seguinte; as arestas são preservadas para auditoria. Se o item for republicado, o mesmo nó é reativado, sem recriação destrutiva.

## Navegação

- Guia de Doenças passa a renderizar `GrafoRelacionados` com `entity_type=doenca`.
- Triagem de Sintomas passa a renderizar `GrafoRelacionados` com `entity_type=triagem_sintoma`.
- Triagens ganham deep-link por `/triagem-sintomas?slug=<slug>`, permitindo que uma aresta do grafo abra diretamente o fluxo pertinente.

## Próximos lotes científicos priorizados

A infraestrutura desta rodada deve ser validada antes de ampliar regras clínicas. O inventário atual prioriza:

1. **Pulso lento / bradicardia sintomática** — conectar instabilidade hemodinâmica, ECG, fármacos bradicardizantes, distúrbios eletrolíticos, isquemia, doença do nó sinusal, bloqueios AV e destino de emergência.
2. **Fadiga / intolerância ao esforço** — conectar insuficiência cardíaca, valvopatias, hipertensão pulmonar, arritmias/incompetência cronotrópica, anemia e causas não cardiovasculares; diferenciar avaliação ambulatorial de sinais que exigem escalada.
3. Densificação de doenças já cadastradas que possuam `related_document_slugs`/`patient_material_slug` ausentes ou incompletos.
4. Rodada de contradições/obsolescência em temas que receberam atualização de guideline após o documento de origem.

Cada lote deve continuar seguindo a regra: relação clinicamente verdadeira, rastreável e útil; ausência de evidência suficiente significa não criar a aresta ou manter a limitação explicitamente registrada.
