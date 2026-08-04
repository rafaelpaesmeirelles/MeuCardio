# Ativação do CorvIA Mail / Mail360

## Regra de segredo

`MAIL360_CLIENT_ID`, `MAIL360_CLIENT_SECRET` e `MAIL360_REFRESH_TOKEN` são segredos de produção. Não devem aparecer em Git, pull requests, issues, logs, artefatos de CI, capturas ou documentação.

Credenciais compartilhadas por mensagem ou outro canal não controlado devem ser revogadas e substituídas no painel Mail360 antes do deploy.

## Instalação

No servidor de produção, editar `/opt/meucardio/.env` ou o secret store equivalente:

```dotenv
MAIL360_CLIENT_ID=<novo-client-id>
MAIL360_CLIENT_SECRET=<novo-client-secret>
MAIL360_REFRESH_TOKEN=<novo-refresh-token>
MAIL360_DOMINIO=corvia.med.br
```

Não copiar valores para `.env.example`.

## Aplicação

```bash
cd /opt/meucardio
docker compose -f docker-compose.prod.yml up -d --build backend
```

## Diagnóstico seguro

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

## Validação funcional

1. confirmar assinatura de CorvIA Mail ativa no banco/Stripe;
2. abrir `/corvia-mail` como assinante;
3. aceitar o termo LGPD e criar uma caixa de teste;
4. entrar com a senha própria da caixa;
5. listar pastas;
6. enviar e receber uma mensagem;
7. abrir o corpo da mensagem;
8. enviar anexo;
9. excluir a mensagem;
10. confirmar que nenhum segredo aparece nos logs.

## Rollback

Remover temporariamente as três variáveis Mail360 e reiniciar o backend desativa o provisionamento com erro 503 controlado, sem apagar caixas ou mensagens existentes no provedor.
