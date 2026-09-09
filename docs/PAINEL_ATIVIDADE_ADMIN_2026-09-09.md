# Atividade administrativa

O administrador encontra **Atividade e crescimento** em Minha conta, na administração e nos menus de navegação. A rota é `/admin/atividade`.

O mesmo seletor de dia, semana, mês ou ano controla os novos cadastros, primeiras ativações de assinaturas CorVIA confirmadas pelo Stripe e logins bem-sucedidos. O calendário usa America/Sao_Paulo; semanas começam na segunda-feira. Há séries, tabela detalhada e contagem de contas distintas.

Pessoas ativas são contas autenticadas com página visível e heartbeat nos últimos 90 segundos. Abas da mesma conta não duplicam a contagem. O painel atualiza a cada 30 segundos e apresenta indisponibilidade quando o Redis não responde.

Os cadastros e acessos usam registros existentes. O histórico das ativações começa no marco gravado pela aplicação, sem presumir que checkout iniciado, teste ou renovação seja uma nova assinatura. Períodos anteriores à coleta aparecem como parciais ou indisponíveis. Não se reconstrói atividade de contas excluídas.

O endpoint exige administrador e retorna somente agregados. Webhooks verificados registram a primeira ativação uma única vez por contrato Stripe, na própria transação, com deduplicação protegida por trava. Não há migration nova.

Validação: compilação TypeScript e build de frontend; leitura independente de autorização, contratos, calendário e deduplicação. Sem suítes de CI ou testes de backend.
