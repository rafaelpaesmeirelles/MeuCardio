# Auditoria semântica do Tudo com Tudo — 01/09/2026

## Resultado executivo

A auditoria identificou **duas causas independentes** de falso nexo clínico:

1. **Expansão temática no grafo:** membros de um mesmo tema canônico podiam
   ser expandidos em segundo salto. Tema é taxonomia de navegação, não prova
   de relação clínica par a par. O risco é máximo no tema amplo `Geral`.
2. **Matcher contextual lexical:** em `connected_content.py`, um único token
   não bloqueado bastava para aceitar o candidato. A stoplist anterior não
   continha `pressão`, `frequência`, `insuficiência`, `prevenção`, `dor` e
   `imagem`.

O conjunto sentinela separa esses caminhos. A política corrigida alcançou
100% de precisão e recall, sem falsos positivos ou falsos negativos.

## Escopo e reprodutibilidade

- Base anterior auditada: `e16c73c0`.
- Script: `scripts/audit_tudo_com_tudo_semantics.py`.
- Dataset: `scripts/fixtures/tudo_com_tudo_semantic_cases.json`.
- SHA-256: `ce1291f392578754710af81b878f94988fb948c314aaeb2128bca7bd9ba0bf18`.
- Execução determinística, sem banco, rede, IA ou dados de paciente.
- Comando integrado: `python3 scripts/audit_tudo_com_tudo_semantics.py --require-actual-mechanisms`.
- Para auditar um worktree candidato antes da integração, usar
  `--mechanism-root <raiz-do-worktree>`.

O dataset tem 20 pares balanceados por desfecho e separados pelo mecanismo:

| Dimensão | Grupo | Casos |
|---|---|---:|
| Validade | Corretas óbvias | 5 |
| Validade | Corretas difíceis | 5 |
| Validade | Semelhantes, porém erradas | 5 |
| Validade | Semanticamente absurdas | 5 |
| Caminho | Grafo/taxonomia | 12 |
| Caminho | Matcher contextual lexical | 8 |

## Antes e depois

| Métrica | Antes | Depois |
|---|---:|---:|
| Precisão | 47,37% | 100,00% |
| Sensibilidade/recall | 90,00% | 100,00% |
| Acurácia | 45,00% | 100,00% |
| F1 | 62,07% | 100,00% |
| Falsos positivos | 10 | 0 |
| Falsos negativos | 1 | 0 |

Impacto quantitativo:

- 9 relações corretas foram preservadas;
- 10 relações falsas foram eliminadas;
- 1 relação difícil correta foi recuperada;
- 0 erros residuais permaneceram nas 20 sentinelas.

### Resultado por caminho

| Caminho | Casos | Antes | Depois |
|---|---:|---|---|
| Grafo/taxonomia | 12 | precisão 54,55%; recall 85,71%; FP 5; FN 1 | precisão/recall 100%; FP/FN 0 |
| Matcher contextual lexical | 8 | precisão 37,50%; recall 100%; FP 5; FN 0 | precisão/recall 100%; FP/FN 0 |

Essa decomposição impede que a correção de uma causa mascare a outra.

## Evidência da causa 1 — expansão de tema

O baseline `e16c73c0` continha:

- relação `same_theme`;
- expansão em segundo salto por `vizinhos_de_tema`;
- relação taxonômica derivada com score `0,35`.

As cinco sentinelas absurdas compartilhavam apenas o tema amplo `Geral` e
eram aceitas no baseline: fibrilação atrial ↔ radiografia de joelho,
pericardite ↔ protetor solar, estenose aórtica ↔ escala de ansiedade dentária,
hipertensão ↔ fototipo de Fitzpatrick e atorvastatina ↔ checklist de catarata.

Na implementação corrigida, a auditoria carrega a política real
`knowledge_relation_policy.py` e certifica quatro invariantes do código:

- tipo e direção são validados pela matriz fechada antes da persistência e
  novamente na leitura de relações legadas;
- expansão temática é `False` por padrão;
- `same_theme` nunca sai como relação clínica direta;
- a API pública rejeita a tentativa de habilitar expansão temática ampla.

A navegação temática permanece disponível apenas como mecanismo interno e
opt-in. Isso preserva a taxonomia auditável sem converter coocorrência de tema
em evidência clínica.

## Evidência da causa 2 — um token lexical

O matcher anterior aceitava qualquer overlap restante. A stoplist já continha
termos como `risco`, `tratamento`, `diagnóstico`, `agudo` e `crônico`, mas
faltavam precisamente seis termos genéricos exercitados pelas sentinelas:

| Token | Falso par aceito antes |
|---|---|
| `pressão` | pressão arterial no choque ↔ pressão intraocular |
| `frequência` | frequência cardíaca ↔ frequência de ultrassom |
| `insuficiência` | insuficiência cardíaca ↔ insuficiência adrenal |
| `dor` | dor torácica ↔ dor neuropática |
| `imagem` | imagem cardíaca ↔ imagem retiniana |
| `prevenção` | ausente na stoplist anterior e agora protegida por invariante |

## Invariantes reais do matcher corrigido

A auditoria carrega `topic_relevance.py` do worktree candidato e verifica a
implementação real, não apenas uma decisão fictícia:

- `CONTEXT_MIN_RELEVANCE_SCORE = 3`;
- peso de token discriminativo em título/slug = 3;
- peso de tag estruturada = 5;
- todos os 11 termos genéricos sentinela pontuam zero;
- os seis termos ausentes na stoplist anterior agora estão presentes;
- um termo verdadeiramente discriminativo, como `brugada`, continua aceito e
  explicado;
- `connected_content.py` usa `score_contextual_relevance` e expõe threshold e
  razões do match.

O objetivo não é exigir arbitrariamente dois tokens: um único termo clínico
específico pode ser suficiente. Um termo genérico nunca pode ser suficiente.

## Relações preservadas ou recuperadas

Foram preservadas relações como sacubitril/valsartana → ICFER, apixabana →
fibrilação atrial, SCA → troponina, endocardite → ecocardiograma e
espironolactona → potássio. O matcher lexical preservou termos discriminativos
como `Fabry`, `catecolaminérgica` e `Lake Louise`. A política tipada recuperou
amiodarona → TSH/T4 livre, sem abrir exceção para pares tematicamente parecidos.

## Full text e embeddings: recuperação, não arestas

- `/api/search` usa full text para recuperar resultados de busca.
- O RAG usa embeddings e recuperação híbrida para responder perguntas.
- `knowledge_graph.py` e `connected_content.py` não usam `tsquery`, distância
  vetorial ou embeddings para criar relações.

Portanto, full text e embeddings existem no produto, mas não são a origem das
arestas ou dos matches contextuais auditados.

## Regra de correção certificada

1. Relações editoriais explícitas e revisadas são preservadas.
2. `same_theme`/`belongs_to_topic` permanecem taxonomia, não prova clínica.
3. Relação derivada do grafo exige tipo/direção, proveniência, score e âncora
   clínica estruturada compatíveis.
4. Matcher contextual usa stoplist clínica e scorer auditável real.
5. Sugestão por IA nunca é promovida automaticamente.
6. Ausência de metadado suficiente resulta em omissão, não invenção.

Este é um gate sentinela de regressão; ele não substitui revisão científica
humana do corpus completo.
