# CorVIA — proposta de cobrança de IA

Data de referência: 09/09/2026. Proposta para decisão comercial; nenhum preço, produto, saldo, assinatura ou cobrança foi alterado. As tarifas de fornecedores foram consultadas em fontes oficiais nesta data. Exemplos abaixo são simulações, não a fatura nem o consumo médio dos assinantes.

**Resultado da tentativa de comparação da IA:** uma única chamada de embeddings para o lote de 16 perguntas foi recusada pelo provedor com HTTP 429, código `credit_balance_exhausted`, após aproximadamente 2,65 segundos. Não houve novas tentativas. O braço híbrido não pôde ser executado; **não existe percentual de ganho semântico medido nesta avaliação**. O fallback textual permite continuidade da recuperação, mas, neste teste, a contribuição da camada semântica paga estava indisponível. Isso não comprova indisponibilidade de todos os modelos ou provedores.

A inspeção prévia de 18 documentos publicados encontrou chunks marcados `LEGACY_UNVERIFIED` em 14 deles e quatro sem embedding; a representação do índice também precisa ser validada antes da comparação conclusiva. Nenhum índice foi atualizado para contornar a falta de saldo. A proposta econômica está fundamentada na arquitetura, configuração observada, registros retidos e preços oficiais; a aprovação por qualidade/ganho da IA permanece pendente de execução válida da comparação.

## Decisão recomendada

Manter busca Tudo com Tudo, leitura do acervo, calculadoras determinísticas e navegação nas conexões dentro da assinatura, sem cobrança por pesquisa. Cobrar consumo adicional nas tarefas que efetivamente geram conteúdo, interpretam imagens, transcrevem áudio ou executam vários agentes. Exibir orçamento e saldo em reais de **crédito de serviço CorVIA**, evitando uma promessa de quantidade fixa de perguntas.

A mesma pergunta pode executar uma geração curta ou várias gerações longas. Quantidade de mensagens, isoladamente, não controla custo. Um usuário precisa poder continuar consultando o acervo mesmo quando seu crédito de IA acabar.

Os valores de assinatura encontrados no código são R$49,90/mês (Básico) e R$59,90/mês (Completo). Não equivalem a uma confirmação dos produtos/preços ativos no processador de pagamentos.

## O que o consumo observado permite concluir

A leitura agregada e sem alterações no ambiente de produção foi concluída em 09/09/2026 às 22:13 UTC. O chat estava configurado em **OpenAI/GPT-4o mini**, embeddings em `text-embedding-3-small`, limite diário numérico 1.000 e saída máxima 4.096 tokens. As configurações específicas de ECG/multimodal estavam vazias, usando os padrões do código. Heart Team usa o provedor padrão quando não há modelo específico. `subscriptions_enabled` estava falso. [Dados agregados auditados](ai-usage-aggregate-20260909.json).

Nos 30 dias anteriores havia **19 respostas de chat retidas**, 312.870 tokens de entrada e 15.810 de saída: 13 Haiku 4.5, cinco Sonnet 5 e uma Opus 5. Três eram do modo clínico e 16 do pessoal, portanto esse histórico não representa uma amostra adequada da recuperação semântica clínica. Aplicar apenas as tarifas padrão consultadas hoje aos tokens retidos produz o cenário abaixo; tarifas históricas, cache, ferramentas, chamadas omitidas e mensagens apagadas impedem tratá-lo como fatura real.

| Modelo histórico | Respostas retidas | Tokens entrada/saída | Cenário com tarifas atuais |
|---|---:|---:|---:|
| Haiku 4.5 | 13 | 114.746 / 4.427 | US$0,136881 |
| Sonnet 5 | 5 | 73.782 / 7.318 | US$0,220744 |
| Opus 5 | 1 | 124.342 / 4.065 | US$0,723335 |
| Total | 19 | 312.870 / 15.810 | US$1,080960 |

O registro Opus sozinho corresponde a cerca de 67% desse cenário de custo. Isso mostra por que tamanho do contexto e modelo importam, mas **não permite estimar gasto médio de um assinante**. As tabelas financeiras das demais funções estavam vazias, enquanto os eventos técnicos registravam Round, tentativas de ECG e multimodal; ausência de registro financeiro não comprova ausência de gasto. [Relatório de uso](ai-usage-aggregate-20260909.json).

## Estresse financeiro hipotético, sem confundir com consumo observado

Usar **1.000 respostas por dia durante 30 dias** dá 30 mil gerações. A configuração numérica de 1.000/dia foi observada; sua utilização integral **não** foi observada. Além disso, quotas espalhadas por funções não constituem uma carteira financeira central, e rotas sem medição podem produzir custos adicionais.

Mantendo, apenas para comparação, 8.000 tokens de entrada e 1.200 de saída em cada geração, sem cache, imagens, ferramentas ou tentativas adicionais, e **câmbio hipotético de R$6,00/US$**:

| Modelo no cenário | Custo fornecedor por geração | Custo mensal fornecedor USD | Custo mensal convertido | Relação com mensalidade R$59,90 |
|---|---:|---:|---:|---:|
| GPT-4o mini, modelo de chat observado | US$0,00192 | US$57,60 | R$345,60 | 5,77 vezes |
| GPT-5.6 Sol, cenário de modelo mais caro | US$0,05600 | US$1.680,00 | R$10.080,00 | 168,28 vezes |

Cálculos próprios com [tarifa oficial GPT-4o mini](https://developers.openai.com/api/docs/models/gpt-4o-mini) e [tarifa oficial GPT-5.6 Sol](https://developers.openai.com/api/docs/models/gpt-5.6-sol). Estes valores representam apenas o fornecedor: não incluem a margem CorVIA, a proteção cambial, infraestrutura ou outros custos. Não significam que Sol esteja sendo usado no chat atual nem que um assinante produza esse volume. Demonstram que um limite de mensagens alto pode superar a receita mesmo no modelo econômico. A saída máxima configurada, 4.096 tokens, é maior que a usada nesta simulação; o pior custo autorizado precisa considerar o teto real de cada execução.

## Carteira e cortesia propostas

| Componente proposto | Valor pago | Crédito de serviço | Regra |
|---|---:|---:|---|
| Cortesia mensal no Básico | Dentro da assinatura | R$3,00 | Renova no ciclo, sem acumulação |
| Cortesia mensal no Completo | Dentro da assinatura | R$5,00 | Renova no ciclo, sem acumulação |
| Recarga opcional inicial | R$29,90 | R$29,90 | Compra avulsa, sem renovação automática |
| Recarga opcional intermediária | R$59,90 | R$59,90 | Mesma tarifa de consumo |
| Recarga opcional ampliada | R$119,90 | R$119,90 | Mesma tarifa de consumo |

O saldo pago deve ser separado da cortesia, com consumo da cortesia primeiro. Proposta inicial: saldo pago sem vencimento comercial automático; política de encerramento/estorno a definir antes da oferta. Não conceder bônus por volume no lançamento: primeiro medir custo real, uso intenso e perdas. Limite extra padrão R$0; nenhuma recarga automática sem opção expressa do assinante. Um pacote recorrente poderá ser oferecido depois, com consentimento e limite explícitos.

## Tarifas oficiais verificadas

Valores em USD por milhão de tokens, entrada sem cache/saída, processamento padrão. Acesso efetivo depende da conta do fornecedor.

| Modelo | Entrada | Saída | Fonte |
|---|---:|---:|---|
| GPT-4o mini | US$0,15 | US$0,60 | [OpenAI — GPT-4o mini](https://developers.openai.com/api/docs/models/gpt-4o-mini) |
| GPT-4o | US$2,50 | US$10,00 | [OpenAI — GPT-4o](https://developers.openai.com/api/docs/models/gpt-4o) |
| GPT-5.6 Sol | US$4,00 | US$20,00 | [OpenAI — GPT-5.6 Sol](https://developers.openai.com/api/docs/models/gpt-5.6-sol) |
| Claude Haiku 4.5 | US$1,00 | US$5,00 | [Anthropic — preços](https://platform.claude.com/docs/en/about-claude/pricing) |
| Claude Sonnet 5 | US$2,00 | US$10,00 | [Anthropic — preços](https://platform.claude.com/docs/en/about-claude/pricing) |
| Claude Sonnet 4.6 | US$3,00 | US$15,00 | [Anthropic — preços](https://platform.claude.com/docs/en/about-claude/pricing) |
| Claude Opus 5 | US$5,00 | US$25,00 | [Anthropic — preços](https://platform.claude.com/docs/en/about-claude/pricing) |

`gpt-5.6` é um alias documentado de GPT-5.6 Sol. A tarifa promocional de Sol está anunciada pelo menos até 21/11/2026; contextos acima de 272 mil tokens têm outra tarifa. Revisar a versão da tabela antes de cada novo ciclo comercial, preservando o orçamento já aceito. [Modelo e condições](https://developers.openai.com/api/docs/models/gpt-5.6-sol).

Sonnet 5 está documentado a US$2/10 como tarifa padrão; o aumento anteriormente anunciado para setembro foi cancelado. Tokenizadores podem diferir entre modelos: comparar o custo efetivamente registrado, sem assumir que o mesmo texto gera a mesma quantidade de tokens. [Preços Anthropic](https://platform.claude.com/docs/en/about-claude/pricing).

`text-embedding-3-small` custa US$0,02 por milhão de tokens. Uma consulta hipotética de 100 tokens custa US$0,000002 de embedding; 100 mil consultas iguais custariam US$0,20, excluindo infraestrutura e eventuais gerações. Indexar uma vez 24 milhões de tokens custaria US$0,48; 24 milhões é exemplo aritmético, não uma medição do acervo CorVIA. [Modelo de embeddings](https://developers.openai.com/api/docs/models/text-embedding-3-small).

Transcrição `gpt-4o-mini-transcribe`: estimativa oficial US$0,003/minuto. Web search padrão: US$0,01/chamada, mais tokens do conteúdo pesquisado. Não pressupor uma única chamada por execução. As tarifas efetivas de imagens dependem da representação/tamanho e do modelo. [Preços OpenAI](https://developers.openai.com/api/docs/pricing).

## Formação da tarifa e margem

Proposta de piloto, a recalibrar com telemetria: câmbio de orçamento **R$6,00/US$**, proteção adicional **15%**, parcela operacional variável **R$0,01 por chamada de provedor**, multiplicador comercial **4**. R$6,00 é hipótese conservadora de simulação, não cotação de mercado. A parcela de R$0,01 também é hipótese, não custo medido. A proteção de 15% é reserva gerencial, não imposto identificado.

```text
USD_real = soma do custo de todos os tokens e ferramentas de todos os estágios
Custo_protegido_R$ = USD_real × 6,00 × 1,15 + 0,01 × chamadas_do_provedor
Débito_CorVIA_R$ = arredondar_para_cima_em_centavos(4 × Custo_protegido_R$)
```

Os estágios de uma tarefa devem ser somados antes do arredondamento. Usar tarifa de cache quando realmente houver cache; incluir raciocínio faturável, imagens, áudio e pesquisa web sem contá-los duas vezes. Consultas do catálogo e indexação editorial comum não recebem este débito. Uma resposta já armazenada e apenas reaberta não gera nova cobrança. Valores do orçamento devem ter tabela/versionamento identificáveis para auditoria.

Simulação comparável: **8.000 tokens de entrada e 1.200 de saída em uma única chamada**, sem cache, ferramentas, imagem nem áudio. Não é uma afirmação de que todos os modelos entregam qualidade clínica equivalente ou de que uma tarefa típica possui esse tamanho.

| Modelo | Custo fornecedor USD | Débito simulado na carteira |
|---|---:|---:|
| GPT-4o mini | US$0,00192 | R$0,10 |
| Claude Haiku 4.5 | US$0,01400 | R$0,43 |
| Claude Sonnet 5 | US$0,02800 | R$0,82 |
| GPT-4o | US$0,03200 | R$0,93 |
| Claude Sonnet 4.6 | US$0,04200 | R$1,20 |
| GPT-5.6 Sol | US$0,05600 | R$1,59 |
| Claude Opus 5 | US$0,07000 | R$1,98 |

Cálculos próprios com as tarifas citadas. Uma consulta complexa pode exceder esses valores; estimativa deve considerar entrada completa, saída máxima, quantidade de estágios e ferramentas. Não divulgar “R$0,82 por Heart Team”: ele pode chamar o provedor várias vezes e ampliar o histórico.

Para uma recarga totalmente consumida, o orçamento protegido é no máximo 25% do valor debitado sob esta fórmula. Para visualizar margem, suponha uma dedução conjunta de pagamentos/encargos de 10% da receita e R$0,40 fixos por transação — **hipóteses de simulação, sem equivalência a alíquotas legais ou contrato real**.

```text
Contribuição = receita × (1 − deduções_percentuais) − tarifa_fixa − custo_variável
Margem_de_contribuição = contribuição / receita
Preço_mínimo = (custo_variável + tarifa_fixa) / (1 − deduções_percentuais − margem_alvo)
```

| Recarga consumida | Orçamento protegido máximo | Contribuição conservadora simulada | Margem simulada |
|---|---:|---:|---:|
| R$29,90 | R$7,48 | R$19,04 | 63,66% |
| R$59,90 | R$14,98 | R$38,54 | 64,33% |
| R$119,90 | R$29,98 | R$77,54 | 64,67% |

Essa contribuição ainda precisa pagar custos fixos, suporte não incluído na parcela variável, aquisição de clientes e demais despesas. Não é lucro líquido. Reserva de câmbio não consumida melhora o resultado; tarifas superiores, falhas, fraude e ressarcimentos podem piorá-lo. Antes de fixar preços, substituir as hipóteses pelos contratos e dados reais.

Como meta inicial, trabalhar com **60% de margem de contribuição variável** nas recargas após custos reais reconciliados, sem anunciar essa porcentagem como margem garantida. A simulação acima resulta em 63,66% a 64,67%; a diferença de aproximadamente 3,7 a 4,7 pontos percentuais oferece espaço para perdas e despesas variáveis ainda não medidas. Se elas excederem esse espaço, revisar preços ou orçamento. Multiplicador 4 não significa 300% de lucro: antes das demais deduções, corresponde a custo protegido de 25% do débito.

A cortesia de R$3/5 admite orçamento protegido máximo de R$0,75/R$1,25 por assinante. Em mil assinantes Completo que consumam toda a cortesia, isso corresponde a até R$1.250 do orçamento protegido, além dos demais custos da plataforma. Não calcular sustentabilidade pela quantidade média de perguntas apenas: simular percentil 95, percentil 99 e consumo simultâneo no limite.

| Cortesia mensal | Máximo de custo protegido sob a fórmula | Parcela da mensalidade indicada no código |
|---|---:|---:|
| R$3,00 no Básico de R$49,90 | R$0,75 | 1,50% |
| R$5,00 no Completo de R$59,90 | R$1,25 | 2,09% |

São limites de desenho da proposta. Para valerem na prática, a reserva e o bloqueio precisam abranger todos os estágios e todas as rotas pagas. Não são limites já implementados nem estimativas extraídas da fatura.

## Quais funções entram na carteira

| Função | Tratamento proposto |
|---|---|
| Busca Tudo com Tudo e relações cadastradas | Incluída, sem débito de IA |
| Embeddings comuns do acervo e atualizações editoriais | Custo operacional central, separado do saldo individual |
| Recuperação semântica sem geração | Manter incluída inicialmente; custo e ganho medidos separadamente |
| Resposta do assistente, síntese, redação personalizada | Débito pelos estágios efetivamente executados |
| Round e apoio multimodal/ECG | Débito pela execução completa, orçamento prévio e limite de saída |
| Heart Team Virtual | Orçamento agregado de todos os participantes, comparação e síntese |
| Documento particular longo, tradução e reanálise | Orçamento por arquivo com teto de páginas/tokens/estágios |
| Áudio do WhatsApp | Transcrição + eventual resposta/ação geradora, em um mesmo orçamento |
| Reabrir resultado já gerado | Sem novo débito |
| Falha técnica sem resultado útil | Estorno ao assinante; custo eventualmente faturado fica registrado internamente |

Custos externos do canal WhatsApp/BSP, caso existam no contrato efetivo, precisam de linha própria e não podem ser inferidos apenas pelo preço da transcrição. Não criar cobrança de canal até conferir contrato/configuração.

## O que precisa existir antes de vender a carteira

1. **Um registro financeiro independente das conversas.** Apagar uma conversa não apaga consumo nem restaura saldo. Guardar IDs técnicos e custos; não copiar conteúdo clínico para o registro financeiro.
2. **Reserva atômica antes da chamada**, incluindo solicitações concorrentes. Considerar saldo disponível menos reservas abertas. Não permitir saldo negativo.
3. **Orçamento da tarefa inteira.** Heart Team, visão, traduções, pesquisas e novas tentativas pertencem à mesma tarefa. Limitar chamadas, tokens, duração e quantidade de ferramentas. Reservar o pior custo permitido, não apenas o custo médio histórico.
4. **Liquidação pelo uso real.** Liberar parte não utilizada da reserva; registrar provedor/modelo/tarifa/versão/entrada/cache/saída/ferramentas e identificador idempotente. Webhooks repetidos não duplicam créditos; retomadas não duplicam débitos.
5. **Reconciliação de falhas e interrupções.** A desconexão do navegador não garante cancelamento no provedor. Manter reserva até término/reconciliação; não descartar custo desconhecido como zero. Se o resultado não for entregue, aplicar política clara de estorno e registrar a perda interna.
6. **Bloqueio duro** quando faltar saldo ou orçamento, inclusive em workers e integrações. Todas as rotas pagas, usuários administrativos de teste e tarefas agendadas têm orçamento ou centro de custo; nenhuma rota pode contornar o controle.
7. **Limites globais e por função.** Um teto financeiro central complementa o individual; atingir o teto interrompe novas execuções pagas e preserva consulta ao acervo. Rate limit por minuto serve para abuso, mas não substitui orçamento.
8. **Tela compreensível.** Mostrar saldo, estimativa e teto antes de ações caras: “Até R$X; cobraremos o valor efetivamente utilizado”. Ao exceder o orçamento aprovado, pausar e oferecer continuação opcional. Não migrar para um modelo mais caro automaticamente fora do teto.

O inventário técnico encontrou lacunas que tornam prematura a cobrança comercial: consumo de chat vinculado a mensagens apagáveis; Round descarta tokens; documentos privados podem executar síntese e até 25 traduções sem uma quota financeira própria; multimodal inclui pesquisa web sem teto de ferramentas; quotas locais não formam uma carteira central. Esses achados devem ser confrontados com o relatório técnico e corrigidos antes de ativar a proposta.

## Como aprovar preço com evidência

Primeiro finalizar as correções do Tudo com Tudo. Depois comparar recuperação textual e híbrida nas mesmas perguntas com rótulos de pertinência: cobertura de itens essenciais, precisão no topo, duplicações e latência. O ganho de embeddings se mede nessa comparação; o ganho de geração se mede separadamente por fidelidade às fontes, utilidade da resposta e tempo poupado. Benchmark de recuperação não certifica a qualidade clínica da resposta gerada.

A tentativa atual foi interrompida pelo saldo esgotado do provedor de embeddings, conforme descrito na abertura. Medir o braço textual isoladamente serve de referência; não permite inferir melhoria da IA. Para retomar a comparação, é necessário restabelecer o acesso pago e confirmar a elegibilidade/atualidade do índice. Esta proposta não recarrega o provedor, não muda seus limites e não declara a avaliação de qualidade concluída.

Em paralelo à validação funcional da IA, consolidar uso real por função/modelo, custo por tarefa entregue, estágios e novas tentativas. O período piloto deve ser observado até haver amostra suficiente para as funções caras; sete a quatorze dias é proposta operacional, não calendário já agendado. A carteira só entra em oferta após reconciliar o consumo com o fornecedor, testar concorrência/estorno/retomada e confirmar que nenhuma rota paga contorna o saldo.

O preço final e a escolha de modelos dependem desses resultados. A recomendação comercial concreta é **assinatura + pequena cortesia + recarga pré-paga opcional**, preservando o Tudo com Tudo acessível e impedindo gasto adicional inesperado.
