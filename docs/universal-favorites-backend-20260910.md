# Favoritos universais e leitura do original — backend

## Problemas corrigidos

O favorito anterior aceitava apenas seis tipos com ID numérico. Calculadoras e funções identificadas por slug não podiam ser salvas. A listagem fazia uma consulta por favorito e devolvia títulos de itens que haviam deixado de estar publicados. Os registros existentes foram preservados.

## Identidades e acesso

A migração `c2fv20260910` acrescenta `item_slug`, mantém os IDs anteriores e permite referências sem ID numérico. As restrições únicas por usuário/tipo/ID e usuário/tipo/slug continuam protegendo inclusões concorrentes. A inclusão usa identidade canônica e trava transacional; ID e slug conflitantes são recusados. Aliases de estudos consolidados e documentos/fluxogramas não criam favoritos duplicados.

O catálogo de favoritos cobre os objetos científicos acessíveis, calculadoras, descobertas bibliográficas confiáveis, publicações originais licenciadas, documentos científicos privados do próprio usuário e funções ativas do registro de navegação. Funções não aceitam URL ou título arbitrários: os 44 atalhos vêm de `clinicalRouteRegistry.ts`, com gates de assinatura e instalação preservados. Cursos e aulas legados, cujas rotas foram desativadas anteriormente, não foram reativados.

Conteúdo compartilhado exige publicação vigente; trilhas também exigem revisão concluída, reproduzindo a política do leitor correspondente. Documento científico privado exige proprietário correto e acesso vigente ao recurso de IA, antes de decifrar o título. Não são criadas referências a pacientes, prontuários ou dados clínicos privados como se fossem conteúdo científico compartilhado.

Listagens consultam os modelos em lotes e carregam somente os campos de metadados necessários. Conteúdo indisponível permanece removível, com título genérico, sem link, resumo ou metadados privados. Excluir um favorito por ID sempre verifica o usuário proprietário.

## Contrato de API

- `POST /api/favorites`: `item_type` e pelo menos um de `item_id`/`item_slug`. Ambos, quando enviados, precisam resolver a mesma identidade.
- `GET /api/favorites/status`: consulta pontual, retorna `favorited`, `favorite_id`, `available` e identidade canônica.
- `GET /api/favorites`: mantém os campos anteriores e acrescenta `item_slug`, `available`, `unavailable_reason`, `reading` e `private_reading`.
- `DELETE /api/favorites/by-id/{favorite_id}` remove inclusive favoritos de conteúdo retirado. Os caminhos anteriores por tipo/ID continuam válidos; também existe remoção por tipo/slug.
- `reading` contém `{entity_type, slug}` para reutilizar a API científica compartilhada. `private_reading` contém somente `{document_id}`, resolvido pela biblioteca privada existente, sem passar pelo leitor público.

A publicação original usa `source_key` como identidade e abre `/intelligence?fonte={source_key}`. Sua disponibilidade deriva do mesmo predicado usado pelo catálogo e pelo Tudo com Tudo: original armazenado, hash e identidade válidos, licença permitida e proveniência em fontes públicas vigentes. Não é criado um Documento editorial duplicado nem uma revisão científica fictícia.

## Original dentro do CorVIA

O manifesto científico agora fornece `original.read_url`. A variante `/original-text` lê exclusivamente o XML cifrado que já foi adquirido, verifica o hash, revalida DOI/licença e apresenta o texto original com atribuição. A variante `/original` mantém o arquivo XML original para download. Não se apresenta XML como PDF; figuras gráficas e suplementos são diferenciados do texto e das legendas.

Salvar um favorito ou abrir qualquer dessas leituras não chama IA, não dispara downloads externos, não enfileira processamento e não duplica o arquivo científico.

A observabilidade também foi corrigida: `ai_processing` significa execução ativa e não é contado como falha. Custos incertos continuam separados e aguardam reconciliação.

## Validação

- Migração real em banco exclusivo de QA: `c0aw20260909 → c1sp20260910 → c2fv20260910`, concluída.
- Oito testes focais de favoritos: 41,76 segundos, aprovados. Cobrem legado, aliases sem registro antigo, conflitos, publicação, privacidade, remoção por proprietário, calculadoras, funções e consultas em lote.
- Leitor interno do original e verificação de integridade: aprovado, 3,73 segundos. Um ajuste de expectativa de espaço final na fixture foi necessário; o parser conserva o conteúdo textual, removendo espaços exteriores.
- Contador de processamento ativo versus falha/reconciliação: aprovado.
- A integração com a nova frente de originais usa o predicado compartilhado e possui teste focal adicional de disponibilidade e retirada de proveniência pública.

Nenhuma suíte completa ou CI backend foi executado. Nenhuma chamada paga de IA ou alteração de produção foi feita nesta implementação.

Validação final da integração do original ao acervo: `test_original_asset_manifest_and_favorite_require_current_public_origin` passou no PostgreSQL QA isolado (1 passed, 2 deselected, 4.48s). O caso confirma manifesto, identidade canônica por ID/source_key, ausência de resumo editorial fabricado e indisponibilidade após retirada da única origem pública. Total dos casos focais deste backend: 8 de Favoritos + 3 de original/status aprovados; nenhuma suíte completa de backend, chamada paga ou mutação de produção.
