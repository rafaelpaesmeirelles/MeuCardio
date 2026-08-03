# Observabilidade e correlação de requisições

## Formato

Cada requisição HTTP relevante produz uma linha JSON em `stdout`. Os campos são:

- `timestamp` UTC;
- `level`;
- `service=corvia-api`;
- `event=http_request`;
- `request_id`;
- `method`;
- `path` normalizado ou template da rota;
- `status_code`;
- `duration_ms`;
- `environment`;
- `error_type`, somente em falha não tratada.

O nível é `info` para sucesso, `warning` para 4xx e `error` para 5xx. Health e
readiness bem-sucedidos são omitidos para não gerar ruído a cada probe; falhas
desses endpoints continuam registradas.

`LOG_LEVEL` controla o nível mínimo do logger e usa `INFO` por padrão.

## Request ID

O backend aceita `X-Request-ID` quando o valor é curto, ASCII e compatível com o
formato permitido. Valores ausentes ou inválidos são substituídos por UUID
aleatório. O mesmo identificador é:

- devolvido no header `X-Request-ID`;
- exposto ao navegador por CORS;
- colocado no contexto da requisição;
- incluído no log estruturado;
- devolvido no corpo da resposta 500 genérica.

Ao relatar uma falha, o usuário ou suporte deve informar esse identificador, não
o conteúdo clínico que estava na tela.

## Minimização de dados

O logger não lê nem registra:

- query string;
- corpo de requisição ou resposta;
- headers;
- cookies;
- JWT ou credenciais;
- endereço IP;
- e-mail ou identidade do usuário;
- prontuário, CPF ou nome do paciente.

Quando o framework já reconheceu a rota, o log usa o template, por exemplo
`/api/round/patients/{pid}`. Em caminhos não reconhecidos, segmentos numéricos,
UUIDs, e-mails e tokens longos são mascarados.

Erros não tratados registram somente o tipo da exceção. A mensagem da exceção e
o traceback não entram no log de requisição porque podem conter parâmetros de
SQL, dados clínicos ou conteúdo recebido de serviços externos.

## Uvicorn e containers

O access log padrão do Uvicorn é desativado nos dois arquivos Compose para evitar
duplicidade e caminhos sem normalização. Logs internos de inicialização e erro
do servidor permanecem disponíveis.

Os JSONs podem ser coletados diretamente pelo runtime de containers e enviados
a Loki, Elasticsearch, CloudWatch ou outro backend sem parser de texto livre.

## Limites

Este pacote fornece correlação e logs locais estruturados. Métricas agregadas,
tracing distribuído e coleta externa exigem infraestrutura própria e devem ser
adicionados separadamente, com revisão específica de retenção e acesso por se
tratar de uma plataforma clínica.
