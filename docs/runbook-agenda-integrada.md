# Runbook — Agenda Integrada

## Configuração sem segredos no repositório

Variáveis suportadas (registrar os valores somente no gerenciador de segredos/`.env` de produção):

- `AGENDA_INTEGRATIONS_ENABLED`
- `AGENDA_EXTERNAL_WRITES_ENABLED`
- `AGENDA_BACKGROUND_SYNC_ENABLED`
- `AGENDA_SYNC_LOOKBACK_DAYS`
- `AGENDA_SYNC_HORIZON_DAYS`
- `AGENDA_SYNC_BATCH_SIZE`
- `AGENDA_OUTBOX_MAX_ATTEMPTS`
- `TRAFFIC_PROVIDER` (`google_routes` ou `mapbox`)
- `GOOGLE_ROUTES_API_KEY`
- `MAPBOX_ACCESS_TOKEN`
- `STORAGE_ENCRYPTION_KEY`

Nunca imprimir valores, executar `cat .env`, colocar token em parâmetro de linha de comando ou incluir credencial em diagnóstico. As rotas retornam apenas `has_credentials` e disponibilidade booleana.

## Ordem de ativação

1. Publicar com escrita externa e sincronização em segundo plano desligadas.
2. Criar local, serviço e rotina; validar o plano diário sem integração.
3. Configurar provedor de trânsito e testar com uma conta técnica sem registrar coordenadas.
4. Conectar uma conta OAuth de homologação Google ou Microsoft com o menor escopo necessário.
5. Executar diagnóstico, sincronização completa e depois incremental.
6. Habilitar escrita somente para o tenant piloto e validar create/reschedule/cancel + idempotência.
7. Habilitar o processador de outbox e monitorar erros, limites e reautenticação.

Feegow e outros PEP/PMS permanecem bloqueados até contrato/documentação oficial. Não preencher URL customizada e não criar adaptador por tentativa e erro.

## Operação e alertas

Monitorar:

- integrações em `error` ou `reauth_required`;
- cursor expirado e ressincronização completa;
- eventos da outbox em `failed`/`dead_letter`;
- agendamentos `pending_external` por tempo excessivo;
- comunicações em `retry`;
- conflitos de versão e rotinas sobrepostas;
- local presencial sem latitude/longitude;
- indisponibilidade ou rate limit do provedor de trânsito.

Coordenadas de origem e rotas não podem aparecer em auditoria ou logs. O evento de auditoria registra somente provedor, status, usuário e destino cadastrado.

## Resposta a falhas

- **OAuth 401/403:** suspender integração, marcar reautenticação e não apagar cursor/compromissos.
- **Cursor 404/410:** executar full sync dentro da janela configurada; manter identidades externas.
- **Conflito 409/412:** não sobrescrever silenciosamente; registrar conflito para decisão humana.
- **Rate limit/5xx:** retentativa exponencial pela outbox até o limite; depois dead-letter.
- **Falha no trânsito:** preservar agenda e rotina, informar indisponibilidade; nunca estimar por valor inventado.
- **Falha de e-mail:** manter confirmação clínica e comunicação pendente; não reenviar duplicado.
- **Falha de migração/deploy:** interromper, preservar evidências de erro sem segredos e restaurar o backup pré-deploy.

## Validação pós-publicação

1. Confirmar SHA publicado e árvore Git limpa, exceto artefatos operacionais previamente conhecidos.
2. Conferir `/api/version` e `/api/ready`.
3. Conferir todos os serviços em `docker compose ps` como saudáveis.
4. Criar local e rotina em tenant de teste; conferir `/api/agenda/workday/plan`.
5. Criar e cancelar agendamento; conferir conflito e `version`.
6. Confirmar que resposta de mobilidade não contém a origem enviada.
7. Confirmar que conectores não homologados não geram chamada de rede.
8. Consultar logs por erro novo, sem expor o `.env`.

