# CorVIA — quatro planos, Mail e consumo de IA

Decisão comercial do Dr. Rafael em 09/09/2026. Implementação anterior à abertura de vendas; os valores serão revistos antes do lançamento.

| Plano | ID | Mensalidade | IA | CorVIA Mail |
|---|---|---:|---|---|
| Básico | basico | R$99,90 | Não | Não |
| Básico + Mail | basico_mail | R$119,90 | Não | Sim |
| IA | ia | R$149,90 | Sim | Não |
| Completo | completo | R$169,90 | Sim | Sim |

Tudo com Tudo, acervo e ferramentas do Básico estão incluídos nas quatro opções. A diferenciação de IA abrange assistentes clínico/pessoal, ECG, exames/imagens, discussões, Heart Team, documentos particulares e operações de IA do WhatsApp. Recursos operacionais continuam sujeitos às configurações, permissões e consentimentos já existentes; acesso ao plano não habilita automaticamente envio externo ou processamento clínico sem consentimento.

## Cobrança e contratos

`commercial_plans.py` é a fonte do catálogo e dos direitos no servidor. Os quatro preços mensais são configuráveis em `commercial_price_{plano}_centavos`. O Mail avulso usa a diferença entre Básico+Mail e Básico, que deve coincidir com Completo menos IA. Não são definidos novos descontos semestrais ou anuais.

Contratos existentes recebem `commercial_version=legacy_v1` e conservam a identificação anterior, preços históricos e benefícios contratados; a nova versão somente é atribuída pela confirmação do Stripe. Nenhuma assinatura existente é reajustada pela migration. Upgrades exigem pagamento; webhooks serializam alterações; Mail avulso ativo impede a contratação sobreposta de outro plano com Mail.

`subscriptions_enabled` permanece falso no pré-lançamento. Recargas também exigem `ai_credit_topups_enabled`, inicialmente falso. A página de planos permanece informativa, sem habilitar compras antes da abertura comercial.

## Carteira compartilhada

Proposta inicial configurável: R$40 de créditos de serviço por ciclo completo de IA, com multiplicador quatro e teto de R$10 para o custo protegido da franquia. Crédito de serviço não equivale a dinheiro pago ao fornecedor. Na primeira inclusão de IA durante um ciclo em andamento, cobrança e franquia são proporcionais ao restante do período. Ciclos confirmados, inadimplência e mudanças de plano não podem criar franquias duplicadas.

A carteira separa franquia e recargas. O saldo pago não vence automaticamente. Recargas avulsas propostas: R$29,90, R$59,90 e R$119,90; não há compra automática. O usuário pode definir um limite mensal menor, inclusive zero.

Uma reserva financeira persistente antecede a chamada paga, considera operações simultâneas e cobre o orçamento máximo planejado. A liquidação registra uso real e libera a parte não usada. Excluir conversas não apaga consumo. Chamadas com resultado incerto mantêm a reserva e os custos parciais conhecidos até reconciliação; consumo desconhecido nunca é considerado gratuito. Eventual excesso fica registrado integralmente e bloqueia novas chamadas, sem debitar do usuário além da reserva aprovada.

Recargas só entram após webhook assinado confirmar pagamento. A implementação trata pagamento assíncrono, repetição, discrepância de valor/moeda, estorno parcial, disputa anterior ao checkout e restauração após disputa ganha. Conciliação de pagamentos mantém histórico independente de conversas.

## Instrumentação

A medição alcança SDKs OpenAI/Anthropic, Responses HTTP, streaming, ferramentas, transcrição e todas as etapas planejadas de jornadas compostas. Novas tentativas automáticas do SDK ficam desativadas. Modelos e operações sem tarifa ou orçamento conhecido são recusados antes da chamada. Imagens e áudio são dimensionados antes da estimativa.

Recuperação semântica, indexação comum e trabalho editorial têm centros institucionais próprios, separados do saldo do assinante. O limite inicial configurável é R$100 por centro/mês. O Tudo com Tudo não debita a carteira individual por busca.

Heart Team e documentos particulares apresentam orçamento antes da execução; a confirmação e o teto aceito acompanham o trabalho até o worker. A cotação expira e depende do conteúdo do caso. Reabrir conteúdo já produzido não gera nova chamada ao provedor.

## Validação e publicação

A migration `c0aw20260909` cria registros financeiros e metadados contratuais, sem alterar conteúdo científico ou ativar vendas. Os testes usam bancos PostgreSQL isolados e provedores simulados. A comprovação com provedores pagos reais permanece separada, pois a avaliação anterior encontrou `credit_balance_exhausted`.

Validações locais concluídas em ambiente isolado:

- Cobrança e direitos: 27 testes iniciais, dois cenários complementares e dois testes finais de proporcionalidade/cancelamento.
- Carteira: reservas concorrentes, liquidação, saldo, estornos e ciclos; dois testes finais de upgrade proporcional e renovação integral.
- Recargas: sete testes, incluindo webhook com assinatura real e objetos reais do SDK Stripe, com transporte simulado.
- Instrumentação: 22 testes; Heart Team: 20 testes; orçamento de documentos: 12 testes, incluindo execução real em threadpool com transporte simulado.
- Frontend: 18 testes iniciais, quatro novos testes de orçamento de documentos e verificação TypeScript aprovados. Dez testes do tema claro, contraste e cobertura das 76 rotas passaram na integração complementar.
- Migration aplicada em PostgreSQL isolado; sintaxe Python e diferenças verificadas.

A publicação segue os gates do repositório. Este registro documenta a implementação e os testes locais; a presença no GitHub não comprova implantação em produção.

## Revisão pré-lançamento

Confirmar preços e franquia com consumo real por função/modelo; avaliar experiência das reservas conservadoras; conferir taxas de pagamento, câmbio, custo e limites do Mail/WhatsApp; reconciliar webhooks de pagamentos e estornos; confirmar configurações dos provedores e saldo; homologar casos clínicos representativos. A revisão deve considerar a contribuição variável e os demais custos, sem tratar o teto de IA como garantia de lucro líquido.

A instrumentação de custo não substitui homologação clínica. A comparação de qualidade semântica previamente preparada continua dependente do restabelecimento do provedor e da validação do índice.

## Estado de integração em 09/09/2026

Implementação enviada ao PR #917 (`codex/commercial-plans-ai-wallet-20260909`), primeiro commit `366946de382999a0046a1681ebed39bb2f5e92eb`. Testes reais de integração confirmaram upgrade no último dia do ciclo limitado a 1/30 da franquia e do teto, renovação seguinte integral e cancelamento terminal resistente a replay no mesmo segundo. A aplicação importa, gera OpenAPI e registra as novas rotas no ambiente isolado.

A publicação em produção está bloqueada pelo gate científico: o manifesto de autorização cobre 11.581 registros e o corpus atual contém 12.160. Evidência: Corpus database reconciliation, run 34417647946 do PR #917. Não houve alteração do manifesto, aprovação científica presumida ou atualização de banco em produção. As correções anteriores do Tudo com Tudo estão no PR #916, também ainda não publicado.

A etapa complementar validou 24 testes de cobrança legada e a coleta de 12 testes de PDF com dependência declarada somente no ambiente de desenvolvimento. A migration final também foi aplicada pelo comando operacional ao banco isolado do candidato integrado; as cinco tabelas financeiras e as três novas colunas contratuais correspondem aos modelos.
