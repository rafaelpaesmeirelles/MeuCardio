# Observabilidade e resposta a incidentes

Este runbook cobre indisponibilidade, erro de aplicação, suspeita de acesso
indevido, falha de backup e comprometimento de credenciais. Ele não substitui o
plano organizacional de segurança e privacidade, mas define os passos técnicos
reproduzíveis do repositório.

## Regra de minimização

Nunca registrar ou copiar para ticket, chat ou canal de incidente:

- corpo de requisição ou resposta clínica;
- query string;
- `Authorization`, cookies ou `Set-Cookie`;
- CPF, e-mail, nome de paciente ou profissional;
- token de documento público, ativação ou redefinição;
- laudo, prescrição, exame ou conteúdo de prontuário;
- chaves de IA, Stripe, Mail360, SMTP, JWT ou criptografia do armazenamento.

Os logs próprios da API possuem allowlist fechada de campos. Exceções registram
somente o tipo e a sequência de arquivo/linha/função, sem mensagem e sem
variáveis locais.

## Identificador de requisição

Toda resposta HTTP recebe `X-Request-ID`.

- um identificador enviado pelo proxy é preservado somente quando contém de 8 a
  64 caracteres alfanuméricos, ponto, sublinhado ou hífen;
- valores ausentes ou inválidos são substituídos por UUID opaco;
- o mesmo valor fica disponível no contexto da aplicação;
- novas linhas de `audit_logs` recebem o valor automaticamente;
- rotas são registradas pelo template, por exemplo
  `/api/documentos-publicos/{token}`, nunca pelo token real.

Ao receber relato de erro, solicitar **apenas** o `X-Request-ID`, horário
aproximado e ação realizada. Não solicitar captura contendo dados clínicos.

## Eventos estruturados

| Evento | Uso |
|---|---|
| `http_request_completed` | método, template da rota, status e duração |
| `http_request_failed` | falha não tratada, tipo e stack minimizado |
| `readiness_failed` | PostgreSQL ou Redis indisponível |

Campos esperados: `timestamp`, `level`, `service`, `environment`, `event`,
`request_id`, `method`, `route`, `status_code` e `duration_ms`. Campos de erro
aparecem somente quando aplicáveis.

Exemplo de correlação em arquivo JSON Lines:

```bash
jq 'select(.request_id == "ID-INFORMADO")' /var/log/corvia/api.jsonl
```

Consulta correspondente da auditoria, usando usuário de banco somente leitura:

```sql
SELECT created_at, user_id, action, entity, entity_id, request_id
FROM audit_logs
WHERE request_id = 'ID-INFORMADO'
ORDER BY created_at;
```

O campo `detail` deve ser aberto apenas quando necessário e em ambiente
controlado, pois auditorias antigas podem conter informações administrativas.

## Classificação inicial

### Prioridade 1

- exposição confirmada ou suspeita de dados;
- uso indevido de conta administrativa;
- chave de criptografia, JWT ou credencial de provedor comprometida;
- corrupção ou perda de banco/volume clínico;
- indisponibilidade generalizada sem alternativa operacional.

### Prioridade 2

- erro recorrente em fluxo clínico ou de cobrança;
- readiness intermitente;
- backup ausente, vencido ou com checksum inválido;
- aumento sustentado de respostas 500/503.

### Prioridade 3

- erro isolado sem perda de dados;
- latência elevada localizada;
- bloqueio legítimo por rate limit ou política de upload.

## Procedimento técnico

1. **Conter:** interromper o componente afetado ou revogar a credencial exposta.
   Não apagar logs, registros de auditoria ou arquivos envolvidos.
2. **Preservar:** registrar horário UTC, versão/commit implantado e identificadores
   de requisição. Fazer backup antes de alteração destrutiva quando o banco estiver
   íntegro e acessível.
3. **Confirmar dependências:** consultar `/api/health` e `/api/ready`. Readiness
   503 indica qual componente está indisponível sem expor a configuração.
4. **Correlacionar:** localizar o evento pelo `request_id` e consultar a auditoria
   correspondente. Procurar primeiro evento de falha, não apenas o último efeito.
5. **Mitigar:** rollback de código, isolamento do worker, restauração ou rotação de
   segredo conforme a causa. Nunca restaurar por cima do banco ativo sem destino
   explicitamente confirmado.
6. **Validar:** repetir health, readiness, smoke HTTP, fluxo afetado e verificação
   de backup. Confirmar que os novos eventos não contêm dados sensíveis.
7. **Encerrar:** documentar causa raiz, intervalo afetado, contenção, recuperação,
   evidências preservadas e ação preventiva.

## Backup e alerta

O comando abaixo valida existência, idade e checksum do backup PostgreSQL mais
recente:

```bash
BACKUP_DIR=/caminho/seguro \
MAX_BACKUP_AGE_SECONDS=93600 \
bash ops/check-backup-freshness.sh
```

Códigos de saída:

- `0`: backup recente e checksum válido;
- `2`: ausente, vencido ou corrompido — deve gerar alerta;
- `3`: configuração inválida do verificador.

A saída é JSON de uma linha e pode ser consumida por cron, systemd, monitor de
container ou plataforma de observabilidade. O repositório fornece o probe, mas
não configura destinatário externo de alerta; essa integração pertence à
infraestrutura de produção.

A aprovação do probe não substitui o exercício periódico de restauração. O fluxo
completo permanece em `docs/release-and-recovery.md` e nos scripts
`backup-postgres.sh` e `restore-postgres.sh`.

## Rotação de credenciais

Quando houver suspeita de comprometimento:

1. revogar a credencial no provedor antes de gerar a substituta;
2. atualizar o secret no ambiente, nunca no Git;
3. reiniciar somente os serviços dependentes;
4. executar readiness e smoke;
5. invalidar sessões quando JWT ou credencial de autenticação estiver envolvida;
6. preservar o intervalo de auditoria para investigação.

A `STORAGE_ENCRYPTION_KEY` exige procedimento específico: perder a chave impede
ler os arquivos cifrados; trocá-la sem recifrar os blobs também os torna
ilegíveis. Ela deve permanecer em backup separado, restrito e testado.

## Critérios de recuperação

Um incidente técnico só está recuperado quando:

- health e readiness permanecem estáveis;
- o fluxo afetado passa no smoke ou teste reproduzível;
- banco e volumes necessários estão acessíveis;
- existe backup recente com checksum válido;
- não surgem novos eventos 500/503 relacionados;
- a ação administrativa correspondente pode ser correlacionada por
  `request_id`, quando aplicável.
