# CorVIA — operação de mapas e geocodificação

## Objetivo

Evitar que uma chave aparentemente válida para rotas esteja proibida de usar Geocoding, situação que produz `REQUEST_DENIED` somente quando o usuário tenta salvar um local.

## Chave de servidor

O backend usa `GOOGLE_ROUTES_API_KEY`. A chave permanece somente no servidor e não deve ser copiada para frontend, logs, issues ou screenshots.

Quando o provedor Google Maps estiver ativo, a mesma chave precisa ter, no mínimo, acesso às APIs efetivamente usadas pelo backend:

- **Geocoding API** — converter endereço em latitude/longitude;
- **Routes API** — cálculo de deslocamentos e alternativas de rota.

A conta/projeto também precisa estar com billing/quota compatíveis. Se forem usadas restrições por API na chave, as duas APIs acima devem estar explicitamente autorizadas.

## Preflight não destrutivo

Antes de um deploy ou depois de alterar restrições no Google Cloud, execute dentro da imagem/backend configurado:

```bash
python -m app.commands.check_maps_configuration
```

Em produção, sem abrir shell interativo:

```bash
docker compose -f docker-compose.prod.yml exec -T backend \
  python -m app.commands.check_maps_configuration
```

O comando:

- não consulta banco;
- não cria local;
- não persiste coordenadas;
- não imprime a chave;
- usa apenas um endereço/rota pública genérica em Ribeirão Preto;
- falha de forma explícita em `REQUEST_DENIED`, quota/billing e autorização de API;
- trata indisponibilidade transitória de rede como aviso, para não confundir outage externa com configuração inválida.

## Resultado esperado

```text
Geocoding API: OK
Routes API: OK
Maps preflight: PASS
```

Se aparecer `REQUEST_DENIED`, abrir **Google Cloud → APIs e serviços / Google Maps Platform → Credenciais → GOOGLE_ROUTES_API_KEY** e revisar as restrições de API. Não contornar o erro desabilitando a validação no CorVIA e não inventar coordenadas.

## Segurança

Nunca colocar a chave em query string exibida ao usuário, logs de aplicação ou código versionado. O preflight mascara o segredo por design e deve continuar assim em alterações futuras.
