# Reconciliação autorizada e modelo dedicado do Heart Team — 10/09/2026

## Reconciliação do corpus

O caminho normal `python -m app.commands.reconcile_content --publish-reviewed` usa
`editorial-approvals/scoped-corpus-release-20260910.json`. O manifesto schema 2
autoriza exatamente 12.154 identidades e mantém 56 em quarentena, num snapshot de
12.210 registros. A autorização não inventa revisão humana nem promove o complemento.

Antes de qualquer carga, o reconciliador copia as fontes e as evidências para uma
árvore privada, valida os hashes dessa cópia e fecha a publicação canônica e os
respectivos nós. Os loaders consomem essa cópia com uma proteção de publicação
ativa, inclusive quando o JSON original ou uma aprovação genérica informa
`published:true`. A promoção final exige igualdade das identidades publicadas
com a lista aprovada, e não apenas igualdade das contagens.

As mídias referenciadas são cópias regulares; os campos persistidos de caminho
continuam com o valor canônico do JSON. O backfill lê os três manifestos curados
(interações de medicamentos, relações explícitas e relações transversais) da
mesma cópia, sem fallback para arquivos vivos. Itens estáticos ausentes seguem
a regra anterior de arquivamento; exceções de conteúdo privado/runtime são preservadas.

Schema 2 sem `--publish-reviewed` falha antes de abrir o banco.
`publish_preserved_content` rejeita schema 2 porque não recarrega bytes autorizados;
orienta o operador ao reconciliador. Schema 1 continua estrito quando selecionado
explicitamente por `--authorization-manifest` ou seu alias `--full-authorization`.

Validação em PostgreSQL isolado:
- 12 testes focais de publicação v1/v2: aprovados em 68,80 s.
- 8 testes schema 2 mais a reconciliação integral do corpus real: 9 aprovados em 352,45 s.
- Seleção da mídia congelada e preservação do caminho canônico: 1 aprovado em 17,15 s.
- Nenhum banco produtivo, nova produção científica ou chamada paga participou.

## Heart Team com modelo superior dedicado

Configuração padrão exclusiva:

| Configuração | Valor |
| --- | --- |
| HEART_TEAM_AI_PROVIDER | openai |
| HEART_TEAM_CLINICAL_MODEL | gpt-5.6-sol |
| HEART_TEAM_MAX_OUTPUT_TOKENS | 8192 |
| HEART_TEAM_REASONING_EFFORT | medium |
| Conteúdo estruturado máximo de cada parecer | 32 KiB UTF-8 |

Especialistas, revisão de evidências, red team, contestação e consenso usam a
mesma configuração dedicada. O modelo geral do chat permanece independente.
A extração visual usa o builder multimodal do provedor: Sol com raciocínio high,
limite 8192 e tentativas de compatibilidade declaradas pelo builder, incluindo
fallback visual. Não existe fallback silencioso das deliberações textuais para mini.

O coordenador recebe o conteúdo integral de cada parecer uma vez, identificado
por agente e rodada. Metadados de execução, posições já presentes nas claims e
cópias repetidas das revisões obrigatórias não são reenviados. Divergências,
pareceres individuais e trilha de auditoria continuam íntegros no resultado.
JSON acima de 32 KiB ou resposta truncada falha explicitamente; não há corte
silencioso de achados para caber no orçamento.

Cotação e execução usam o mesmo provedor/modelo, os mesmos limites e as mesmas
variantes visuais. Cache e aceite incluem a configuração: mudar modelo, limite
ou raciocínio invalida o aceite anterior. A cotação expira em 15 minutos.
O teto técnico da jornada Heart Team passou a R$100 de custo de provedor por
operação, configurável; isso não cria saldo nem amplia a franquia de 40 créditos.
Uma cotação acima do saldo exige recarga ou menor composição de especialistas
antes de qualquer chamada. O usuário continua protegido pelo valor que aceitou.

Os valores apresentados são limites conservadores de reserva calculados pelos
bytes de entrada e saída máxima, não um custo efetivo observado. Nenhuma chamada
paga foi feita nesta validação; consumo final é apurado pelo medidor compartilhado.

Validação: 94 testes de seleção, orçamento, consentimento, cache e orquestração
aprovados em 5,73 s, sem rede/banco. O ajuste posterior de saída visual 8192 tem
teste focal separado aprovado (1 teste em 3,43 s), no log
`/tmp/corvia-heart-team-frontier-visual-test.log`.
Os quatro novos valores não estavam definidos no ambiente produtivo conforme
verificação da equipe; defaults do código e conferência dos valores no container
bastam, sem alteração desnecessária de credenciais/configuração produtiva.
