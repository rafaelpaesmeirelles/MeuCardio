# Tudo com Tudo — revisão ampliada de 09/09/2026

Esta revisão continua o PR #916. O mecanismo foi verificado com uma revisão independente, testes dirigidos, interação do componente React real e consultas ao acervo publicado em transações somente leitura. Não houve merge, deploy nem alteração do banco de produção.

## Correções adicionais

1. Medicamentos e marcas comerciais inequívocas são resolvidos antes da recuperação. Apixabana e Eliquis compartilham candidatos, contagem e paginação. O ecossistema de medicamentos usa identidade e relações elegíveis; a indicação não inclui automaticamente todo o conteúdo de uma doença.
2. Título e slug continuam recuperáveis com vetor textual ausente, mesmo quando outro resultado impede o fallback literal. A análise linguística do slug acompanha a da consulta.
3. Doenças aceitam normalização de espaços, acentos e pontuação. `FA?` e `fibrilacao  atrial` mantêm a identidade clínica.
4. Uma menção isolada à hipertensão pulmonar não se transforma em hipertensão sistêmica; um documento comparando explicitamente as duas continua elegível.
5. Siglas curtas de calculadoras não são sustentadas por iniciais de autores. A referência `Klok FA` havia incluído o escore de Genebra simplificado na busca de fibrilação atrial. Esse falso positivo foi removido.
6. A composição interna admite todas as relações elegíveis, sem o teto oculto de mil por tipo. Os limites públicos explícitos permanecem disponíveis.
7. Trocar de assunto durante a paginação redefine o estado de carregamento e descarta respostas antigas. Novas páginas eliminam duplicação com os grupos conectados. A identidade de calculadoras preserva dígitos subscritos.

## Evidência de execução

O relatório `tudo-com-tudo-search-expanded-20260909.json` registra oito consultas, nove verificações técnicas aprovadas e as primeiras páginas para inspeção. Resultados finais:

| Consulta | Total recuperado | Verificação |
|---|---:|---|
| FA / fibrilação atrial | 712 | Mesmo conjunto; cinco calculadoras; escores essenciais presentes; Genebra por iniciais excluído |
| HAS / hipertensão arterial | 178 | Mesmo conjunto e paginação |
| Insuficiência cardíaca | 819 | Contagem coerente e paginação disponível |
| Holter 24h | 40 | Exame canônico na primeira posição |
| Apixabana / Eliquis | 59 | Mesmo conjunto, identidade do medicamento e frentes conectadas |

Os tempos individuais ficaram entre 3,5 e 9,1 segundos. São medidas sob a carga do servidor naquele momento, não um benchmark de capacidade nem uma promessa comercial de latência.

A bateria ampliada de onze testes de backend apresentou dez aprovações e uma falha que revelou a diferença entre a análise linguística do slug e da consulta. Após a correção, o teste falho e três verificações diretamente afetadas passaram. Não foi reexecutada uma suíte completa: foram validados todos os onze cenários, com repetição focal após a alteração. Outros cinco testes puros cobriram precisão de medicamento e 1.001 relações. Seis testes de frontend passaram, sendo três de identidade e três de interação do componente React. A compilação TypeScript completa passou.

O navegador público chegou à tela de login, sem sessão autenticada disponível. A revisão de interface desta entrega corresponde aos testes de interação do componente real; não deve ser descrita como conferência autenticada do site publicado.

## Alcance da conclusão

As regressões técnicas encontradas e os cenários especificados foram corrigidos e verificados. Os totais são candidatos recuperados, não itens individualmente certificados como clinicamente necessários. Relações explícitas e metadados existentes continuam dependendo da qualidade editorial do acervo.

A auditoria estrutural percorreu 12.160 itens versionados e sinalizou vinte links sem destino no checkout. A conferência no banco publicado confirmou os quatorze alvos únicos: os vinte links têm destino em produção. Há uma lacuna de sincronização entre Git e banco, não vinte links quebrados na aplicação. Também há divergência entre o manifesto editorial configurado (11.581 itens) e o corpus versionado atual (12.160). Não foram inventadas aprovações nem alterados estados editoriais para fazer o gate passar. A publicação exige reconciliar o manifesto de release com o conteúdo efetivamente autorizado.

Consultas abreviadas sem alias explícito inequívoco, como o nome parcial de um exame, não são convertidas automaticamente em uma entidade pela posição do primeiro resultado. Sua ampliação depende de aliases estruturados e verificados. Isso evita restabelecer a expansão indiscriminada que causava ruído.

## Atualização da reconciliação — 10/09/2026

A presença dos 14 destinos no banco observado em 09/09 não comprova autorização para a nova publicação. A conferência do snapshot exato identificou sete correspondências integrais com entidades ou ensaios aprovados, uma correspondência parcial e seis sem equivalente integral aprovado. As versões Markdown aparecem em outra linha Git que não é ancestral do candidato; não foram tratadas como remoções comprovadas da linha atual. O relatório `tct-missing-link-destination-review-20260910.md` registra as identidades e limitações. A disponibilidade de navegação deve obedecer ao snapshot aprovado e à quarentena, preservando os rótulos científicos sem inventar substituições.
