# Ativação do CorvIA Mail / Mail360

## Regra de segredo

`MAIL360_CLIENT_ID`, `MAIL360_CLIENT_SECRET` e `MAIL360_REFRESH_TOKEN` são segredos de produção. Não devem aparecer em Git, pull requests, issues, logs, artefatos de CI, capturas ou documentação.

`MAIL360_TRANSACTIONAL_ACCOUNT_KEY` identifica a caixa Native institucional `contato@corvia.med.br`. Não é credencial OAuth, mas também permanece em configuração de ambiente e não deve ser exibida pelo painel administrativo ou por logs.

Credenciais compartilhadas por mensagem ou outro canal não controlado devem ser revogadas e substituídas no painel Mail360 antes do deploy.

## Configuração de produção

No servidor de produção, editar `/opt/meucardio/.env` ou o secret store equivalente, sem imprimir valores:

```dotenv
MAIL360_CLIENT_ID=<client-id>
MAIL360_CLIENT_SECRET=<client-secret>
MAIL360_REFRESH_TOKEN=<refresh-token>
MAIL360_DOMINIO=corvia.med.br
MAIL360_TRANSACTIONAL_ACCOUNT_KEY=<account-key-da-conta-Native-contato>
EMAIL_TRANSACIONAL_PROVIDER=mail360
SMTP_FROM=CorVIA <contato@corvia.med.br>
```

Não copiar valores reais para `.env.example`.

Para o provider `mail360`, `SMTP_HOST`, `SMTP_USER` e `SMTP_PASSWORD` não são necessários. SMTP permanece apenas como provider alternativo compatível.

## Aplicação

Em produção, não aplicar configuração reconstruindo serviços manualmente e não executar migrações à parte. Depois da certificação do SHA final, usar exclusivamente o fluxo oficial do repositório:

```bash
cd /opt/meucardio
bash ./deploy.sh
```

## Diagnóstico seguro do Mail360

Autenticado como administrador:

```http
POST /api/mail360-status/admin/probe
```

Resposta esperada:

```json
{
  "configured": true,
  "connected": true,
  "error_code": null
}
```

Nenhum token é retornado. Os códigos possíveis são:

- `missing_environment_variables`: variáveis ausentes;
- `provider_rejected_credentials`: credencial recusada pelo Mail360;
- `provider_unreachable`: indisponibilidade de rede ou provedor.

Também confirmar no provedor que `contato@corvia.med.br`:

- existe como conta Native/Hosted;
- está habilitada;
- não possui bloqueio de saída;
- corresponde ao `MAIL360_TRANSACTIONAL_ACCOUNT_KEY` configurado.

## Diagnóstico seguro do canal transacional

Autenticado como administrador, consultar:

```http
GET /api/admin/account-access/email-status
```

O resultado deve indicar:

- `email_transacional_configurado: true`;
- `email_transacional_provider: "mail360"`;
- `mail360_configurado: true`;
- `mail360_transacional_configurado: true`;
- `smtp_from_canonico: true`.

O endpoint não retorna Client ID, Client Secret, Refresh Token nem account_key.

Para o smoke real, enviar para uma caixa externa controlada:

```http
POST /api/admin/account-access/email-probe
```

O sucesso só é aceito quando o provider confirma o envio. Em seguida, conferir entrega real na caixa externa e o `EmailLog`; resposta HTTP bem-sucedida isolada não substitui a verificação de recebimento.

## Validação funcional do CorVIA Mail

1. confirmar assinatura de CorVIA Mail ativa no banco/Stripe;
2. abrir `/corvia-mail` como assinante;
3. aceitar o termo LGPD e criar uma caixa de teste quando aplicável;
4. entrar com a senha própria da caixa;
5. listar pastas;
6. enviar e receber uma mensagem;
7. abrir o corpo da mensagem;
8. enviar anexo;
9. excluir a mensagem;
10. confirmar que nenhum segredo aparece nos logs.

## Validação funcional dos e-mails transacionais

Antes de declarar release pronta, testar pelo menos:

1. e-mail de primeiro acesso/boas-vindas para endereço externo controlado;
2. recuperação de senha para o segundo e-mail externo;
3. remetente visível `contato@corvia.med.br`;
4. link e token de redefinição funcionais;
5. `EmailLog.sucesso=true` apenas para envio confirmado pelo provider;
6. falha do Mail360 produz falha explícita, nunca falso sucesso.

## Rollback

Se o Mail360 transacional apresentar falha após uma release, o rollback deve seguir o procedimento oficial do projeto. Não remover credenciais nem reconstruir apenas o backend de forma ad hoc. SMTP pode ser selecionado explicitamente como provider alternativo somente se estiver previamente configurado e validado; não usar fallback não testado em produção.
