# ADR — Assistente Pessoal v2: agenda, rota e CorVIA Mail orientados por intenção

**Status:** implementação em branch isolada, ainda não liberada para produção.

## Problema observado

A primeira versão das ferramentas expunha conceitos internos demais para uma conversa natural:

- criar compromisso aceitava `location_id`, mas não sabia procurar/cadastrar um local por nome/endereço;
- um endereço textual nas observações não deixava o destino utilizável pela função de rota;
- recorrência semanal não estava exposta ao assistente, apesar de a Agenda já possuir `WorkRoutineIn` e `CommitmentSeriesIn` nativos;
- por isso o modelo perguntava “por quantas semanas?” para materializar vários compromissos avulsos;
- o CorVIA Mail era somente leitura, mesmo quando o médico pedia explicitamente uma ação de envio.

Isto transforma uma automação de rotina em uma conversa sobre ids internos e limitações técnicas — exatamente o oposto da experiência esperada do Assistente Pessoal.

## Decisão de produto

O médico fala em linguagem natural; ids internos são responsabilidade do CorVIA.

### 1. Local e rota

O assistente passa a poder:

1. listar locais já conhecidos;
2. resolver por nome/endereço;
3. reutilizar um local existente;
4. completar coordenadas de local existente que ainda não foi geocodificado;
5. cadastrar um local ausente e tentar geocodificá-lo no servidor;
6. vincular o `location_id` resolvido ao compromisso/rotina.

O endereço continua guardado mesmo se o provedor de geocodificação falhar, mas nenhuma latitude/longitude é inventada. Nesse caso a tool devolve `rota_pronta=false` e um aviso explícito.

A geocodificação reutiliza credenciais de Google/Mapbox já disponíveis para mobilidade. Endereço consultado não é escrito em AuditLog pela camada de IA.

### 2. Rotina semanal

Frases como:

> Toda segunda, Hospital das 10h às 12h e Medclin das 13h às 19h.

são representadas por `AvailabilityRule` via `WorkRoutineIn`, uma regra recorrente nativa da Agenda. Quando o médico não informa término, `valid_until` permanece nulo. **Não perguntar “quantas semanas?” apenas para contornar uma limitação da tool.**

Cada faixa/local vira sua própria rotina, permitindo ao planejamento do dia ordenar locais e calcular deslocamento entre eles.

### 3. Outros compromissos recorrentes

Reunião, estudo, plantão e compromisso pessoal usam `CalendarCommitmentSeries` via `CommitmentSeriesIn` (`daily`, `weekly`, `monthly`). Uma série sem término é válida quando o médico não informou data final.

### 4. Compromisso pontual inteligente

`agenda_criar_compromisso_inteligente` aceita nome/endereço do local; resolve e vincula o local antes de chamar o mesmo `create_appointment` usado pela tela. Conflitos, tenant, sincronização externa e validações continuam sendo os da Agenda real.

### 5. CorVIA Mail com escrita controlada

O Assistente Pessoal ganha:

- listagem das contas efetivamente autorizadas a enviar;
- envio de nova mensagem pela caixa nativa ou conta externa com `send_mail`;
- resposta/reply-all/forward pela caixa nativa.

A regra de segurança é semântica e backend:

- “escreva/redija um e-mail” = apenas produzir rascunho no chat;
- “envie/mande este e-mail” = pode chamar a tool de envio;
- cada tool de envio exige `confirmacao_usuario=true`; sem isso retorna `confirmacao_necessaria` e não toca o provedor;
- destinatário, assunto e corpo nunca entram no AuditLog central das tools;
- anexos permanecem fora deste fluxo até validação própria;
- resposta externa fica fora desta versão enquanto não houver um caminho backend já homologado equivalente ao da caixa nativa.

## Invariantes

- Nenhuma tool recebe `professional_id` arbitrário; o tenant é sempre o usuário autenticado.
- Investidor continua bloqueado pelo middleware read-only global antes de qualquer efeito persistente/externo.
- O modelo não deve pedir `location_id`, latitude ou longitude ao médico quando puder resolver isso pelo sistema.
- Falha de geocodificação, rota, calendário ou e-mail nunca é convertida em sucesso textual.
- Conteúdo clínico continua fora do Assistente Pessoal.

## Gate antes de produção

- testes unitários das tools novas;
- suite backend completa;
- CI/frontend/checkers verdes;
- smoke com uma conta de homologação: local -> geocodificação -> rotina -> próximo deslocamento;
- smoke de nova mensagem CorVIA Mail com pedido explícito e de tentativa sem confirmação;
- nenhuma alteração direta em produção; integração segue o fluxo oficial de Release Candidate/deploy.
