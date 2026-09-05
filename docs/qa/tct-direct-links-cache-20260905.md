# Tudo com Tudo: recuperação de vínculos diretos e retirada de cache clínico

## Escopo e base

Base de implementação: `2a75adeaaf9c3f707f8352912178d5f6e1c0f9df`.
Branch: `fix/tct-recovery-cache-20260905-chatgpt`.
O avanço concorrente da main para `bb13cf23` altera somente o CSS da marca;
este lote não altera CSS, JSX, imagens, conteúdo clínico ou migrations.

## Correções implementadas

O adaptador contextual aproveitava os vínculos do grafo somente para doenças
ou triagens. Agora preserva vínculos diretos nas 15 categorias de conteúdo,
sempre mediante o mesmo serviço e a mesma política de publicação do grafo.
Não há expansão temática de segundo salto, inferência clínica nova nem
promoção de revisão pendente. As consultas livres não herdam o grafo de um
item informado apenas como exclusão.

A composição prioriza vínculos diretos antes do limite de resultados,
deduplica por tipo e slug, preserva proveniência/status e mantém a ordem e os
rótulos das categorias existentes. Medicamentos sem tema reconhecido ainda
podem mostrar vínculos diretos; sem vínculo seguro, continuam sem resultados.

A API de emergência deixa de usar StaleWhileRevalidate. A regra NetworkOnly
já existente cobre a rota. Um script importado pelo Workbox remove caches
legados `corvia-emergencia` e `corvia-emergencia-*` na ativação do novo worker,
sem apagar os caches de cenas, assets e precache do shell.

## Validação executada nesta implementação

- 28 testes Python de regressão aprovados em execução isolada, com dependências
  de app/ORM simuladas. O módulo de serviço executado é o arquivo integral,
  não uma reimplementação das funções testadas.
- O mesmo conjunto contra o código-base: 18 falhas e 10 sucessos. Essas falhas
  reproduzem os comportamentos corrigidos e a ausência dos novos helpers;
  não correspondem a 18 defeitos clínicos independentes.
- 6 testes Node aprovados: remoção seletiva de caches, espera por conclusão,
  idempotência, erro de armazenamento, configuração e matchers reais de rotas.
- A configuração Vite foi avaliada com os plugins substituídos por stubs;
  isso não equivale a um build Vite/Workbox nem a um navegador real.
- Hashes Git dos arquivos-base reconstruídos e dos arquivos alterados
  conferidos contra os blobs retornados pelo GitHub.

## Testes dirigidos no ambiente padrão do projeto

Usar exclusivamente o banco de testes configurado pelo projeto, nunca um DSN
clínico de produção:

```sh
cd backend
pytest -q tests/test_connected_content_direct_graph_coverage.py tests/test_connected_content_clinical_relevance.py
```

```sh
cd frontend
node --test scripts/check-clinical-cache-retirement.test.mjs
npm run build
```

## Critérios ainda necessários antes da publicação

Validar os vínculos com PostgreSQL e o grafo real, nas duas direções, incluindo
relação forte pendente, rejeitada, conteúdo despublicado e destino sem relação
lexical com a origem. Confirmar no frontend autenticado a renderização e o
destino de todas as categorias recuperadas, em desktop e mobile.

Executar build e gates do SHA exato. No navegador, atualizar a partir do worker
antigo com cache de emergência preenchido, confirmar a exclusão desse cache,
sair da sessão, entrar com outra conta e verificar que a API não é servida pelo
Cache Storage. Ausência de rede deve resultar em indisponibilidade explícita,
nunca em dose/protocolo antigo apresentado como atualizado.

Este lote não certifica a revisão editorial do corpus, a cobertura integral do
Tudo com Tudo, recuperação de backup, infraestrutura ou disponibilidade em
produção. Timeline do conhecimento e novas funções PDF permanecem fora deste
lote. Nenhum merge, deploy ou alteração de banco foi realizado nesta execução.
