# Auditoria de modelos e contabilização de IA — 10/09/2026

Esta auditoria confronta código do candidato de lançamento, configuração efetiva lida sem segredos e documentação oficial consultada nesta data. Não executou chamadas pagas nem comparação clínica entre modelos. Preço, capacidade anunciada e compatibilidade de API não demonstram superioridade diagnóstica. As alterações no candidato não representam implantação em produção.

## Configuração observada e destino por função

A produção auditada seleciona OpenAI com `gpt-4o-mini`. `claude-sonnet-5` está configurado como alternativa Anthropic; isso não significa que ambas executem cada resposta. Embeddings usam OpenAI `text-embedding-3-small`, 1.536 dimensões. Limites observados: saída geral 4.096 tokens; contexto 24.000 caracteres; oito trechos recuperados; histórico seis mensagens/16.000 caracteres; Heart Team 2.200 tokens por geração e até 16 fontes. Ferramentas e multimodal estão habilitados. Campos vazios de modelos especializados acionam os defaults abaixo.

| Função | Produção observada | Decisão/candidato e próximo critério |
|---|---|---|
| Busca central Tudo com Tudo | Não exige geração paga | Preservar busca determinística; não confundir com RAG do assistente |
| Recuperação semântica do assistente | `text-embedding-3-small` | Manter como infraestrutura incluída e avaliar recuperação após restabelecer saldo do fornecedor |
| Assistente pessoal/geral | `gpt-4o-mini` global | Perfil econômico existente; comparar Haiku 4.5 ou Sonnet 5 com esforço baixo/médio quando raciocínio ou ferramentas forem necessários |
| Assistente clínico e discussões | Provedor global | Comparar Sonnet 5 médio e Sol médio em casos de referência; medir qualidade de citações, omissões e custo antes de declarar vencedor |
| ECG | Default OpenAI Sol; se Anthropic, herda Sonnet 5 | Preservar auxílio multimodal e validação profissional; corrigir parâmetros incompatíveis e não inferir qualidade de ECG a partir de benchmark geral |
| Exames/imagens | `gpt-5.6` (alias Sol) | Sol com saída limitada; contexto/imagens entram na cotação; schema nullable corrigido |
| Heart Team | Texto herda mini; visão usa Sol | Usuário autorizou modelo superior dedicado: agente responsável implementa Sol nas análises e síntese. Saída de 8.192/esforço médio em avaliação técnica; orçamento deve cobrir todas as etapas e exigir aceitação antes de consumir |
| Documentos particulares | Modelo de exames explícito ou global; hoje mini | Cotação engloba análise e tradução eventual. Separar no futuro tradução econômica e síntese complexa, somente após avaliar fidelidade |
| Áudio WhatsApp | `gpt-4o-mini-transcribe` | Manter transcrição específica e medição por tokens; reserva de saída corrigida para 2.000 |

Anthropic não fornece modelo próprio de embeddings; combinar geração Claude com embeddings OpenAI é uma arquitetura válida. Isso não obriga a pagar duas gerações. [Documentação de embeddings Claude](https://platform.claude.com/docs/en/build-with-claude/embeddings).

O teste anterior de embeddings foi recusado por `429 credit_balance_exhausted`. O híbrido não executou. Na amostra lexical de 16 consultas, cinco das oito consultas curtas recuperaram ao menos um documento rotulado entre oito trechos; oito paráfrases retornaram zero trechos. São rótulos parciais, não precisão nem ganho semântico medido. A indisponibilidade semântica expôs uma lacuna em perguntas livres; não justifica retirar embeddings.

## Capacidades e tarifas verificadas

Valores padrão em USD por milhão de tokens, entrada/saída, sem ferramentas, impostos, câmbio, imagens adicionais ou descontos contratuais.

| Modelo | Entrada / saída | Contexto / saída máxima | Fonte oficial |
|---|---:|---:|---|
| GPT-4o mini | 0,15 / 0,60 | 128 mil / 16.384 | [Modelo](https://developers.openai.com/api/docs/models/gpt-4o-mini) |
| GPT-5.6 Sol; alias GPT-5.6 | 4 / 20 | 1,05 milhão / 128 mil | [Modelo](https://developers.openai.com/api/docs/models/gpt-5.6-sol) |
| Claude Haiku 4.5 | 1 / 5 | 200 mil / 64 mil | [Catálogo Claude](https://platform.claude.com/docs/en/models/overview) |
| Claude Sonnet 5 | 2 / 10 | 1 milhão / 128 mil | [Sonnet 5](https://platform.claude.com/docs/en/models/sonnet-5/overview) |
| Claude Sonnet 4.6 | 3 / 15 | Consultar variante antes de alteração | [Preços Claude](https://platform.claude.com/docs/en/about-claude/pricing) |
| Claude Opus 5 | 5 / 25 | 1 milhão / 128 mil | [Catálogo Claude](https://platform.claude.com/docs/en/models/overview) |
| Embedding 3 small | 0,02 / não aplicável | Embedding, não geração | [Modelo](https://developers.openai.com/api/docs/models/text-embedding-3-small) |
| GPT-4o mini transcribe | 1,25 / 5 | 16 mil / 2 mil | [Modelo](https://developers.openai.com/api/docs/models/gpt-4o-mini-transcribe) |
| GPT-4o transcribe | 2,50 / 10 | 16 mil / 2 mil | [Modelo](https://developers.openai.com/api/docs/models/gpt-4o-transcribe) |

Sol cobra entrada dobrada e saída 1,5 vez acima de 272 mil tokens de entrada, sobre a requisição completa. Sua promoção atual é garantida pelo menos até 21/11/2026; revisar tarifa antes desse marco. O limite máximo de saída do modelo não é uma recomendação de liberar esse volume ao assinante. [Modelo Sol](https://developers.openai.com/api/docs/models/gpt-5.6-sol).

Sonnet 5 usa pensamento adaptativo e rejeita temperatura/top_p/top_k não padrão; a configuração antiga de temperatura zero no ECG causava erro e fallback. O agente financeiro corrigiu essa incompatibilidade. Esforço altera comportamento, mas não substitui `max_tokens` nem teto financeiro. [Sonnet 5](https://platform.claude.com/docs/en/models/sonnet-5/overview), [esforço Claude](https://platform.claude.com/docs/en/build-with-claude/effort).

Sol aceita níveis explícitos de raciocínio; tokens internos também consomem o limite de saída. Uma resposta pode terminar incompleta sem texto final se o teto for insuficiente. Ajustar com testes de casos, não elevando o limite global indiscriminadamente. [Raciocínio OpenAI](https://developers.openai.com/api/docs/guides/reasoning).

`claude-fable-5` existe e custa 10/50, porém não possui tarifa homologada no candidato. Não habilitar seleção até incorporar tarifa, limites e avaliação. Terra/Luna também existem, mas não devem ser introduzidos automaticamente nesta correção. Nenhum modelo novo foi adicionado ao registro de cobrança. [Preços Claude](https://platform.claude.com/docs/en/about-claude/pricing), [preços OpenAI](https://developers.openai.com/api/docs/pricing).

## Correções implementadas em usage_control.py

- Versão de preço/cotação passa a `2026-09-10-cache-v2`, invalidando aceites antigos quando o consumidor usa a versão na impressão digital.
- OpenAI distingue entrada comum, leitura de cache e escrita de cache. Sol: leitura 0,1 vez e escrita 1,25 vez a tarifa normal; mini/4o: leitura 0,5 vez. Contagens de cache são subconjuntos da entrada total. A reserva Sol cobre escrita integral; a liquidação usa a combinação efetiva. [Cache OpenAI](https://developers.openai.com/api/docs/guides/prompt-caching).
- Anthropic soma tokens brutos comuns, lidos e escritos, sem inflar o contador de tokens com multiplicadores monetários. Leitura: 0,1 vez; escrita de cinco minutos: 1,25 vez; uma hora: duas vezes. Usa o detalhamento do recibo; admite inferência de TTL somente quando a requisição tem um único TTL inequívoco. Ambiguidade ou inconsistência retém a reserva para reconciliação. Reserva cobre conservadoramente a tarifa de uma hora, inclusive em planos por etapas. [Cache Claude](https://platform.claude.com/docs/en/build-with-claude/prompt-caching).
- Planejamento das rodadas reconhece `max_tokens`, `max_completion_tokens` e `max_output_tokens`; recalcula a requisição completa ao cruzar limiar de contexto. Histórico gerado é contado em tokens, retorno de ferramenta por limite em bytes e margem de estrutura. A requisição serializada é novamente conferida antes de cada chamada; crescimento acima da reserva bloqueia a próxima chamada.
- Transcrição conserva duração local validada e estimativa conservadora de entrada, mas reserva 2.000 tokens de saída, conforme ambos os modelos suportados. Liquidação utiliza tokens informados, não transforma o preço estimado por minuto em fatura exata. [Preços de transcrição](https://developers.openai.com/api/docs/pricing).
- Campos JSON Schema com `type: ['string','null']` agora são estimados sem `TypeError`; imagens/documentos continuam exigindo seus formatos e limites.

O teto técnico configurável por operação Heart Team passa a R$100 de custo para permitir casos grandes com saldo pré-pago suficiente. Isso não concede crédito: a franquia nominal permanece R$40 em créditos (R$10 de custo no fator4), e a reserva exige saldo integral antes de qualquer chamada. A cotação e seu aceite continuam obrigatórios.

Não foram alterados débito máximo, proibição de overdraft, autorização por conta, saldo, aprovação da cotação nem política de chamadas incertas. Valores observados inválidos não são liquidados como zero. A carteira continua registrando responsabilidade integral do fornecedor, limitando débito ao valor reservado e bloqueando uso diante de divergência.

Verificação focal: 23 novos casos em `test_ai_cache_accounting.py`, mais 22 casos existentes de fronteira do provedor: **45 passaram em 1,07 s**. Incluem valores monetários independentes, leitura/escrita/TTL misto, recibos ambíguos, limiar de contexto, três chaves de saída, schema nullable e transcrição. Providers e carteira simulados; nenhuma chamada paga.

## Custo ilustrativo e configuração por qualidade

Uma geração com 8.000 tokens de entrada e 1.200 de saída, sem cache, ferramentas ou imagens, custa aproximadamente USD 0,00192 no mini; 0,014 no Haiku; 0,028 no Sonnet 5; 0,056 no Sol; 0,070 no Opus. Isso é cálculo de cenário, não consumo médio observado de assinantes. Com câmbio hipotético de R$6/USD, Sol corresponde a R$0,336 de custo do fornecedor por geração desse perfil, antes das demais despesas.

Heart Team faz múltiplas gerações: para N participantes, a arquitetura atual pode executar 2N−1, além de visão eventual. Com N=3 e cinco gerações idênticas ao perfil anterior em Sol, o custo ilustrativo é USD0,28/R$1,68. Se cada uma atingir 8.192 tokens de saída com os mesmos 8.000 de entrada, o cenário sobe a USD0,9792/R$5,8752, sem cache/ferramentas/imagens. Entradas reais crescem com pareceres anteriores; esses cenários não são teto de caso. A cotação individual usa o plano completo e o saldo disponível.

Manter limite por operação, aceite prévio em tarefas grandes, franquia e recarga voluntária. A mistura de fornecedores deve ser explícita por função, com fallback homologado visível na auditoria. Avaliar candidatos em amostra clínica revisada: fidelidade às fontes, omissões essenciais, citações sustentadas, completude estruturada, latência e custo total por tarefa. Ainda não há avaliação comparativa paga que permita afirmar qual é o melhor modelo para cada função.

Configuração operacional observada: SDK OpenAI 1.59.6 e Anthropic 0.120.2; clientes sem timeout explícito, com retries desativados. Definir timeout por jornada e verificar compatibilidade do SDK são recomendações separadas, não mudanças deste arquivo. O candidato inclui ffmpeg para validar áudio; a instalação antiga de produção não o possuía. A evidência de implantação deve ser obtida após publicação autorizada.

## Fechamento da configuração dedicada do Heart Team

A implementação final está documentada em `heart-team-frontier-and-scoped-reconciliation-20260910.md`: GPT-5.6 Sol dedicado, raciocínio médio nas deliberações, saída de 8.192 tokens e cotação vinculada à configuração. A extração visual também utiliza limite de 8.192, com seu esforço específico já previsto no construtor visual. A mudança passou em 94 testes e uma verificação focal visual posterior, sem chamadas pagas. Os valores de produção anteriores acima registram o estado auditado antes do deploy; os novos defaults serão conferidos no backend e worker após a publicação.
