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

Heart Team apresenta orçamento antes da execução; a confirmação e o teto aceito acompanham o trabalho até o worker. A cotação expira e depende do conteúdo do caso. Reabrir conteúdo já produzido não gera nova chamada ao provedor.

## Validação e publicação

A migration `c0aw20260909` cria registros financeiros e metadados contratuais, sem alterar conteúdo científico ou ativar vendas. Os testes usam bancos PostgreSQL isolados e provedores simulados. A comprovação com provedores pagos reais permanece separada, pois a avaliação anterior encontrou `credit_balance_exhausted`.

Validações locais concluídas em ambiente isolado:

- Cobrança e direitos: 27 testes iniciais, dois cenários complementares e dois testes finais de proporcionalidade/cancelamento.
- Carteira: reservas concorrentes, liquidação, saldo, estornos e ciclos; dois testes finais de upgrade proporcional e renovação integral.
- Recargas: sete testes, incluindo webhook com assinatura real e objetos reais do SDK Stripe, com transporte simulado.
- Instrumentação: 22 testes; Heart Team: 20 testes.
- Frontend: 18 testes e verificação TypeScript aprovados.
- Migration aplicada em PostgreSQL isolado; sintaxe Python e diferenças verificadas.

A publicação segue os gates do repositório. Este registro documenta a implementação e os testes locais; a presença no GitHub não comprova implantação em produção.

## Revisão pré-lançamento

Concluir a apresentação de orçamento prévio na interface de documentos particulares (o controle financeiro no servidor já se aplica); confirmar preços e franquia com consumo real por função/modelo; avaliar experiência das reservas conservadoras; conferir taxas de pagamento, câmbio, custo e limites do Mail/WhatsApp; reconciliar webhooks de pagamentos e estornos; confirmar configurações dos provedores e saldo; homologar casos clínicos representativos. A revisão deve considerar a contribuição variável e os demais custos, sem tratar o teto de IA como garantia de lucro líquido.

A instrumentação de custo não substitui homologação clínica. A comparação de qualidade semântica previamente preparada continua dependente do restabelecimento do provedor e da validação do índice.
