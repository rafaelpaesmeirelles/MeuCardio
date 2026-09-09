# Tudo com Tudo: correção de recuperação e pertinência — 09/09/2026

## Regra de produto

Todo conteúdo deve se conectar ao assunto consultado quando houver uma relação útil. A busca deve atravessar as frentes do CorVIA, preservar a natureza da relação e permitir chegar ao conjunto completo de candidatos elegíveis. A existência de uma ligação indireta no grafo, isoladamente, não comprova pertinência à consulta.

## Defeitos reproduzidos

Na implementação anterior, a busca de doença filtrava resultados depois da paginação, limitava a lista a 36 e substituía a contagem pelo tamanho dessa lista, sem próxima página. Conteúdos úteis com títulos diferentes do nome da doença ficavam inacessíveis. A busca por siglas em calculadoras aceitava fragmentos de palavras: FA recuperava 24 calculadoras, incluindo ventilação protetora, acidose metabólica e DAPT. O frontend expandia vizinhos dos primeiros resultados de até oito tipos, adicionando relações que não necessariamente respondiam à consulta.

A revisão também identificou colisões entre HAS e HAS-BLED, IC e intervalos de confiança, além de consultas sem termos válidos no catálogo de exames devolvendo todo o catálogo.

## Alterações

- Resolver a doença e seus aliases antes da recuperação; sigla e nome canônico usam os mesmos candidatos.
- Reutilizar as conexões elegíveis do serviço de conteúdo conectado, com sua política existente de relações. Conteúdo apenas contextual não entra automaticamente como ligação direta. O catálogo publicado continua determinando quais entidades podem aparecer.
- Combinar ligações elegíveis com identidade textual de título/slug, antes de ordenar, contar e paginar. Não inferir indicação clínica de uma simples ocorrência no corpo do texto.
- Distribuir as frentes na ordenação de doenças, preservando relevância e identidade estável. Remover o teto silencioso de 36 resultados.
- Exigir tokens inteiros para siglas curtas nas calculadoras e tratar as colisões verificadas. Preservar os escores ligados à doença e os registros reais do catálogo.
- Expandir o grafo na busca livre somente a partir de uma identidade exata da consulta. Reutilizar a resposta de doença da API para evitar duplicação de conteúdo e de requisições.
- Mostrar a natureza de relações como contraindicação, interação, monitorização e citação quando essa informação estiver disponível.
- Calcular página e contagens na mesma consulta. Projetar somente as colunas necessárias e produzir snippets após o limite da página.
- Retornar zero exames quando uma consulta fornecida não contém termos válidos.

Não houve alteração de esquema, publicação de conteúdo, backfill ou alteração de dados de produção.

## Validação executada

Base de código: `1c8454d132bfc6ecedec802c731dbb26b4d1e6da`. Trabalho em branch e worktree isoladas.

- Nove testes direcionados de backend passaram em banco de teste exclusivo. Cobrem paginação completa de 125 documentos, equivalência de aliases, ligação útil sem o nome da doença no título, conteúdo despublicado, vetor ausente, colisões de siglas, exames, múltiplas frentes, fallback literal e paginação de calculadoras.
- Após a otimização final da consulta comum, os três testes afetados de múltiplas frentes, fallback e calculadoras foram repetidos e passaram.
- Dois testes do frontend passaram para identidade exata, normalização e exclusão de âncoras de outros assuntos. A compilação TypeScript também passou.
- O script `scripts/audit_search_launch.py` foi executado com o código candidato em processo efêmero contra o catálogo publicado, em transações explicitamente somente leitura. O relatório anexo registra seis consultas e dez verificações técnicas. Não houve deploy do candidato durante essa execução.

O relatório é reproduzível com o ambiente do backend configurado: `python scripts/audit_search_launch.py --output acceptance.json`. O script usa as permissões do ambiente fornecido e impõe transação somente leitura e timeout SQL; não necessita de dados de pacientes.

## Alcance e pendências para lançamento

Os totais representam candidatos recuperados pelas regras implementadas, não uma revisão médica individual de cada resultado. Os testes confirmam os defeitos corrigidos e as jornadas especificadas; não certificam todos os assuntos e todas as relações do acervo.

Para avaliar o Tudo com Tudo continuamente, cada jornada clínica precisa de uma lista versionada de itens obrigatórios, itens úteis opcionais e itens indevidos, com revisão de domínio. A avaliação deve medir cobertura dos obrigatórios, pertinência no topo, diversidade útil de frentes, duplicação, estabilidade entre aliases e tempo de resposta. O conjunto inicial automatizado inclui FA, HAS, insuficiência cardíaca e Holter; os demais assuntos devem ampliar esse conjunto sem recorrer a ligações indiscriminadas.

A latência observada está registrada no relatório e ainda requer atenção antes de assumir uma experiência comercial rápida. Medidas isoladas sob carga do servidor não constituem benchmark de capacidade. A publicação do PR, a conferência das jornadas na interface publicada e a validação clínica mais ampla permanecem pendentes.
