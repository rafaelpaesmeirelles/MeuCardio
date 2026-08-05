# ADR — Agenda Integrada, rotina profissional e mobilidade

**Status:** aceito para implantação protegida  
**Data:** 2026-08-05  
**Escopo:** agenda Corvia, sincronização externa, planejamento diário e deslocamento.

## Contexto

O Corvia precisa reunir agenda própria, calendários externos, rotina recorrente e deslocamentos sem inventar contratos de terceiros, misturar dados entre profissionais ou confirmar ao paciente um horário que o sistema externo ainda possa rejeitar. A posição atual do profissional é um dado altamente sensível e não é necessária para persistência: o servidor precisa apenas processá-la durante o cálculo solicitado.

Os conceitos de `Appointment`, `Schedule` e `Slot` são inspirados no FHIR R4 para facilitar interoperabilidade futura. Isso não constitui declaração de conformidade FHIR; não há endpoint FHIR público nesta entrega.

## Decisão

1. O usuário profissional é o tenant da agenda. Delegação para secretária é explícita e separada por capacidade (`view`, `create`, `reschedule`, `cancel`, `configure`). Operações sensíveis geram `AuditLog`.
2. A rotina profissional usa regras recorrentes por dia, local, entrada, saída, modalidade, serviço, antecedência e vigência. Dois períodos no mesmo dia representam intervalos. Exceções bloqueiam férias, feriados ou eventos sem apagar a rotina-base.
3. O planejamento diário materializa as regras no fuso do local, combina compromissos futuros e produz alertas de sobreposição/local sem coordenadas. A posição atual e a rota nunca são gravadas.
4. Cada integração declara capacidades. Google Calendar/People e Microsoft Graph usam OAuth 2.0 delegado com PKCE, menor escopo e renovação de token. Apple usa CalDAV/CardDAV e senha específica de app; a senha principal é proibida. Feegow, Amplimed, iClinic, Tasy, MV e Pixeon permanecem sem tráfego de rede até documentação e homologação verificáveis.
5. Sincronização incremental é idempotente. A identidade externa é única por profissional, integração e compromisso. Exclusões externas são cancelamentos lógicos; não há exclusão física automática.
6. Escritas externas usam outbox transacional, chave de idempotência, controle de versão e retentativa limitada. O agendamento permanece `pending_external` até confirmação do provedor. Somente depois disso uma comunicação de confirmação pode ser enfileirada.
7. Credenciais, cursores e dados dos contatos são cifrados por tenant com o cofre do servidor. Estados OAuth têm digest, expiração curta e uso único. APIs nunca retornam tokens, senhas específicas de app ou coordenadas recebidas no cálculo.
8. Contatos sincronizados são disponibilizados somente ao CorvIA Mail do mesmo titular. A busca ocorre após decifragem limitada, sem índice de e-mail em texto claro. Desconectar apaga credenciais/cursores e retira os contatos da exibição.
9. Mobilidade exige consentimento revogável e permissão do sistema operacional. A PWA atualiza automaticamente enquanto está aberta ou quando volta ao primeiro plano. Rastreamento persistente em segundo plano só poderá existir em aplicativo nativo, com permissão específica do sistema operacional e nova avaliação de privacidade.
10. Google Routes ou Mapbox Directions podem fornecer ETA com trânsito. Sem chave real, coordenadas do destino ou consentimento, a interface informa a indisponibilidade e não inventa estimativas.

## Estratégias de sincronização

| Estratégia | Origem de verdade | Escrita Corvia | Conflitos |
|---|---|---:|---|
| `external_authoritative` | sistema externo | bloqueada | corrigir na origem |
| `bidirectional` | Corvia + externo | via outbox | versão, estado e auditoria |
| `meucardio_authoritative` | Corvia | via outbox | Corvia prevalece após homologação |

As flags `AGENDA_EXTERNAL_WRITES_ENABLED` e `AGENDA_BACKGROUND_SYNC_ENABLED` iniciam desligadas. A existência de um adaptador não autoriza escrita sem consentimento, credencial e homologação operacional.

## Matriz de conectores

| Provedor | Leitura incremental | Criar/reagendar/cancelar | Situação |
|---|---:|---:|---|
| Google Calendar + Contacts | sim | sim | OAuth oficial por conta; Calendar API + People API |
| Microsoft 365 + Contacts | sim | sim | OAuth delegado por conta; Microsoft Graph |
| Apple iCloud Calendar + Contacts | completa por janela | não | CalDAV/CardDAV oficial; senha específica de app; leitura protegida |
| Feegow | não | não | homologação/documentação oficial necessária |
| Amplimed, iClinic, Tasy, MV, Pixeon | não | não | catálogo; nenhuma chamada externa |
| ICS/CSV | planejado, somente leitura | não | importador ainda não liberado |

## Alternativas rejeitadas

- **Scraping ou endpoint privado de PEP/PMS:** inseguro, instável e sem base contratual verificável.
- **Sincronização direta dentro da requisição clínica:** aumenta latência e pode deixar banco e provedor em estados divergentes.
- **Persistir posição atual para “facilitar” ETAs:** desnecessário para a finalidade e amplia o risco LGPD.
- **Marcar confirmação antes do retorno externo:** pode enviar ao paciente uma confirmação inexistente na origem.
- **Unificar todos os provedores em um menor denominador comum:** esconderia diferenças importantes de capacidade, versão e cancelamento.

## Consequências

O núcleo funciona imediatamente como agenda própria, rotina e planejamento diário. Integrações e trânsito passam a funcionar progressivamente quando houver credenciais reais, consentimento e homologação. O custo é uma operação assíncrona mais sofisticada, compensada por consistência, rastreabilidade e rollback seguro.

## Critérios obrigatórios de liberação

- migração sobe e desce em banco isolado;
- testes de tenant, consentimento, conflito, idempotência e outbox aprovados;
- build do frontend aprovado e agenda utilizável em desktop e celular;
- nenhuma credencial ou conteúdo do `.env` em logs, resposta HTTP ou commit;
- backup verificado antes da migração de produção;
- `/api/version`, `/api/ready`, `docker compose ps` e smoke autenticado aprovados;
- falha em qualquer validação interrompe a publicação ou aciona rollback.
