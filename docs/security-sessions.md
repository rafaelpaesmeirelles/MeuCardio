# Sessões e credenciais da Corvia

## Sessão da plataforma no navegador

O navegador autentica a conta Corvia por cookie `corvia_session` com as
seguintes propriedades:

- `HttpOnly`: JavaScript não consegue ler o JWT;
- `SameSite=Strict`: o cookie não acompanha navegação ou requisição iniciada por
  outro site;
- `Secure` em produção: transmissão somente por HTTPS;
- `Path=/`: disponível para as rotas HTTP e para o handshake do WebSocket no
  mesmo domínio;
- expiração alinhada a `JWT_EXPIRE_MINUTES`.

O login web usa `POST /api/auth/sessao`. A resposta contém apenas
`{"authenticated": true}`; o token não aparece no corpo, `localStorage`,
`sessionStorage`, URL ou estado React.

O logout usa `POST /api/auth/sair`. A rota não exige uma sessão válida porque
precisa conseguir apagar um cookie expirado, corrompido ou já revogado.

## Clientes externos

`POST /api/auth/login` continua emitindo Bearer para integrações, testes e
clientes não-browser. As rotas autenticadas aceitam:

1. header `Authorization: Bearer ...`, quando fornecido explicitamente;
2. cookie HttpOnly, no navegador.

Essa compatibilidade não autoriza o frontend oficial a persistir Bearer. A CI
executa `frontend/scripts/check-auth-storage.mjs` e falha se o cliente web voltar
a ler/gravar `meucardio.token` ou montar o header Bearer da sessão principal.

## WebSocket do chat

O navegador abre `/api/chat/ws` no mesmo domínio. O handshake envia o cookie
HttpOnly automaticamente; nenhum JWT real é colocado na query string.

A query `token` permanece somente como fallback para clientes não-browser. O
backend sempre prioriza o cookie e aplica a mesma validação de escopo, expiração
e `sessions_valid_after` usada nas requisições HTTP.

## Revogação

Cada JWT contém `session_iat`. O usuário mantém `sessions_valid_after` no banco.
Tokens emitidos antes ou no instante desse marco são recusados.

O marco é atualizado quando:

- a senha da conta muda;
- a senha é redefinida por recuperação;
- o usuário executa `POST /api/auth/encerrar-todas-sessoes`.

Encerrar todas as sessões também apaga o cookie do navegador atual.

## CSRF e origem

A aplicação web e a API são servidas no mesmo domínio. O cookie usa
`SameSite=Strict`, e o CORS de produção deve listar apenas origens explícitas;
credenciais nunca devem ser combinadas com origem curinga.

Endpoints servidor-a-servidor públicos, como o webhook do Stripe, não dependem
do cookie e mantêm autenticação criptográfica própria.

## CorvIA Mail

A caixa CorvIA Mail possui credencial, escopo e sessão separados da conta da
plataforma. Esta migração protege a sessão principal. A sessão da caixa deve ser
tratada em pacote próprio para não misturar ciclos de autenticação distintos.
