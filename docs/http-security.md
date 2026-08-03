# Segurança HTTP

Este documento descreve as defesas de transporte, navegador e abuso aplicadas
antes das rotas clínicas da Corvia.

## 1. Headers no proxy

O Caddy de produção aplica:

- HSTS por um ano, incluindo subdomínios;
- `X-Content-Type-Options: nosniff`;
- bloqueio de frames por `X-Frame-Options` e `frame-ancestors`;
- `Referrer-Policy: strict-origin-when-cross-origin`;
- `Permissions-Policy` sem câmera, microfone, geolocalização, pagamento ou USB;
- Content Security Policy com scripts apenas da própria origem;
- remoção do header `Server`;
- bloqueio de plugins/objetos e políticas cross-domain legadas.

A CSP permite estilos inline porque componentes React e Mermaid geram atributos
`style` dinamicamente. Isso não libera scripts inline.

## 2. Proteção de origem

Em `ENVIRONMENT=production`, toda operação `POST`, `PUT`, `PATCH` ou `DELETE`
que carregue o cookie `corvia_session` precisa apresentar `Origin` ou `Referer`
compatível com:

- o host efetivamente atendido pelo proxy;
- `PUBLIC_URL`;
- uma origem explicitamente cadastrada em `CORS_ORIGINS`.

Uma origem ausente, `null`, malformada ou divergente recebe HTTP 403 antes da
rota. Isso complementa `SameSite=Strict`; nenhuma dessas defesas deve ser
tratada isoladamente como suficiente.

Clientes externos com Bearer não precisam simular headers de navegador. Os
endpoints de sessão web também verificam origem quando `Sec-Fetch-Site` indica
que a chamada veio de navegador, reduzindo login-CSRF.

## 3. Rate limiting

Os contadores usam Redis, portanto são compartilhados entre os dois workers do
Uvicorn e continuam coerentes quando houver mais réplicas.

| Grupo | Limite | Janela |
|---|---:|---:|
| login de conta/caixa | 10 | 5 minutos |
| recuperação, ativação e solicitação de acesso | 5 | 1 hora |
| download por link público | 120 | 1 minuto |
| chamadas de IA | 20 | 1 minuto |

A chave usa hash truncado do IP, sem gravar o endereço bruto no Redis. Respostas
incluem `X-RateLimit-Limit`, `X-RateLimit-Remaining` e `X-RateLimit-Reset`.
Quando o limite é excedido, retornam 429 com `Retry-After`.

Se o Redis falhar em uma superfície limitada, a resposta é 503. O sistema não
faz fail-open em login, recuperação, link clínico público ou IA. As demais rotas
continuam seguindo a disponibilidade normal do backend; `/api/ready` também
indica falha do Redis ao orquestrador.

## 4. Proxy e endereço do cliente

Em produção o backend não é publicado diretamente; somente o Caddy chega à
porta interna. O middleware usa o último valor de `X-Forwarded-For`, definido
pelo proxy, e recorre a `scope.client` fora dele.

Não exponha a porta 8000 do backend à internet. Fazer isso permitiria contornar
TLS, CSP e outras políticas que pertencem ao proxy.

## 5. Verificação de release

O smoke de release envia `Origin` nas mutações e valida o ciclo completo de
cookie HttpOnly. Depois do deploy, execute:

```bash
python scripts/release_smoke.py \
  --base-url https://corvia.med.br \
  --email CONTA_DE_SMOKE \
  --password 'SENHA_EXCLUSIVA' \
  --expect-secure-cookie
```

A conta de smoke de produção, quando utilizada, deve ter privilégios mínimos,
senha exclusiva e ser removida ou desativada após a janela de validação.

## 6. Incidentes e ajuste de limite

Antes de aumentar um limite, confirme se os 429 são uso legítimo ou automação.
Não registre senha, JWT, token de documento, corpo clínico nem conteúdo de PDF
em logs de diagnóstico. Para investigar abuso, são suficientes grupo, horário,
hash do cliente, status e identificador de requisição.
