# CorVIA — Tudo com Tudo, contribuição da IA e cobrança adicional

## Resultado executivo

O mecanismo de busca recebeu correções adicionais verificadas para doenças, medicamentos, marcas, índices ausentes, paginação e expansão de relações. O PR #916 contém os testes e as consultas de aceitação. A busca principal não faz chamada paga de IA por pesquisa.

A tentativa de medir o ganho dos embeddings encontrou uma limitação operacional real: o provedor recusou a única chamada de dezesseis perguntas com HTTP 429 e código `credit_balance_exhausted`. A comparação híbrida não ocorreu. Nenhum percentual de ganho semântico, qualidade de resposta gerada ou retorno financeiro da IA pode ser deduzido dessa falha. Não houve nova tentativa, recarga, troca de modelo ou reindexação.

A proposta comercial é manter Tudo com Tudo e acervo incluídos, oferecer pequena cortesia de IA na assinatura e recargas opcionais de crédito de serviço. Antes de cobrar, o CorVIA precisa de um saldo financeiro central e de contabilização que sobreviva à exclusão de conversas.

## Tudo com Tudo: o que foi concluído

- Doenças e aliases são resolvidos antes de contar e paginar. Pontuação e espaços não desfazem essa identidade.
- Medicamentos e marcas inequívocas usam o mesmo conjunto paginado. Um tema da indicação delimita candidatos, mas não torna todos eles relevantes ao fármaco.
- Títulos e slugs funcionam com vetor ausente. Siglas não correspondem a fragmentos de palavras nem às iniciais de autores em referências de calculadoras.
- A expansão do grafo parte da identidade da consulta. O limite interno oculto de mil relações foi retirado da composição paginada.
- Os testes React confirmam recuperação do botão após troca de assunto, descarte de respostas antigas, deduplicação entre páginas e ausência de busca duplicada de ecossistema para medicamento resolvido.

Na última conferência somente leitura: FA/nome completo recuperaram 712 candidatos; HAS/nome completo, 178; insuficiência cardíaca, 819; Holter, 40; apixabana/Eliquis, 59. Contagens, aliases, escores essenciais e paginação passaram nas verificações. São candidatos, não uma certificação médica individual de todos os resultados.

[Revisão e testes](tudo-com-tudo-search-followup-20260909.md) · [Resultados por consulta](tudo-com-tudo-search-expanded-20260909.json).

A auditoria estrutural percorreu 12.160 itens. Os vinte links inicialmente sinalizados no checkout têm seus quatorze destinos publicados no banco. A diferença é de sincronização Git/banco. O manifesto integral configurado espera 11.581 itens e não valida o corpus atual; ele precisa de reconciliação na preparação da release, sem inventar aprovação editorial. [Conferência do acervo](tct-corpus-reconciliation-20260909.md).

## Onde a IA contribui e o que foi efetivamente medido

| Função | Papel da IA | Evidência desta avaliação |
|---|---|---|
| Busca principal Tudo com Tudo, leitura e calculadoras | Nenhuma chamada paga por consulta | Código e consultas de aceitação verificados |
| Recuperação semântica do assistente clínico | Encontrar trechos por significado e combinar com texto | Comparação bloqueada por falta de saldo; referência textual medida separadamente |
| Assistente clínico | Sintetizar resposta com fontes | Arquitetura e tokens históricos verificados; qualidade clínica da geração não foi certificada |
| Assistente pessoal | Interpretar pedidos e escolher ferramentas | Dezesseis das dezenove respostas históricas retidas eram pessoais; esse modo não usa o RAG clínico |
| Round | Organizar apoio ao caso com fontes | Chamada identificada; retorno descarta tokens, impossibilitando custo completo retrospectivo |
| ECG e exames multimodais | Interpretar arquivo e, no multimodal, pesquisar evidências | Fluxos e controles examinados; ausência de ensaio de acurácia com casos rotulados |
| Heart Team | Produzir pareceres, contestações e consenso | Código executa até `2N−1` gerações para N participantes, além de anexos; possui componentes financeiros reutilizáveis |
| Documento privado e tradução | Sintetizar e traduzir conteúdo longo | Uma ação pode executar síntese e até 25 traduções; não há teto financeiro central nessa rota |
| WhatsApp | Transcrever áudio e gerar resumos/respostas quando necessário | Fluxos e tarifas configuráveis identificados; ações determinísticas não precisam de geração |
| Indexação e revisão editorial | Preparar conteúdo reutilizado por todos | Custo operacional da plataforma, sem nova cobrança a cada leitura |

A referência foi congelada antes de observar resultados: dezesseis perguntas, oito consultas curtas e oito paráfrases, com dezoito documentos identificados no acervo. Todos os dezoito estavam publicados; quatro não tinham chunks de embedding. Os outros quatorze tinham somente chunks classificados como `LEGACY_UNVERIFIED`, sem confirmação histórica de modelo/proveniência. Esses índices são aceitos pelo mecanismo atual, mas não podem ser chamados de índices atuais verificados.

[Medição reproduzível](ai-contribution-20260909.json) · [Protocolo e rótulos](ai-retrieval-reference-cases-20260909.md) · [Script de comparação](../scripts/audit_ai_contribution.py).

A referência textual foi executada para as dezesseis perguntas, sem chamada de rede de embeddings. Cinco das oito consultas curtas encontraram ao menos um dos documentos previamente rotulados entre os oito trechos devolvidos. As oito paráfrases retornaram **zero trechos**. O Hit@8 global dos rótulos foi 5/16; não representa precisão clínica, porque outros resultados úteis não foram todos rotulados. As três consultas curtas sem acerto de rótulo retornaram conteúdo, portanto também não devem ser chamadas de buscas vazias.

Essa medição corresponde ao RAG que prepara fontes para o assistente, não ao endpoint `/api/search` corrigido. A mediana da recuperação textual foi 6,475 segundos; foram observados 29 slots com identidade documental repetida, que podem corresponder a trechos diferentes do mesmo documento. O híbrido permanece `null` no relatório. A diferença entre os dois modos não foi medida. Retirar embeddings por causa de sua indisponibilidade atual seria uma decisão sem evidência de qualidade; restaurar a disponibilidade e verificar a indexação é necessário para completar a comparação.

## Risco econômico confirmado

O chat estava configurado em OpenAI/GPT-4o mini, com limite numérico de mil respostas diárias. Outros módulos possuem cotas separadas. Esse número não é um limite financeiro global.

Há lacunas que precisam ser resolvidas antes de vender uso extra:

- Excluir conversas elimina as mensagens usadas para contar a cota do chat e apaga tokens históricos.
- Algumas funções contam antes de chamar o provedor, sem reservar orçamento contra concorrência.
- Round e documentos privados perdem dados de consumo; busca web, transcrição, embeddings e falhas com consumo não estão integralmente reconciliados.
- Uma tarefa pode conter muitas chamadas. Cobrar a mesma quantidade de créditos por toda e qualquer pergunta não representa seu custo.

Os registros retidos dos últimos trinta dias somam apenas dezenove respostas, três clínicas e dezesseis pessoais, com 312.870 tokens de entrada e 15.810 de saída. Não são uma fatura completa nem amostra suficiente para definir gasto médio de assinante. [Uso agregado e configurações](ai-usage-aggregate-20260909.json).

## Proposta de assinatura e saldo

| Componente | Proposta inicial |
|---|---|
| Tudo com Tudo e acervo | Incluídos; continuam acessíveis com saldo de IA zerado |
| Básico | R$3 de cortesia de serviço IA por ciclo |
| Completo | R$5 de cortesia de serviço IA por ciclo |
| Recarga opcional | R$29,90, R$59,90 ou R$119,90, convertidos no mesmo valor de crédito de serviço |
| Débito | Por tarefa completa, segundo tarifa divulgada e consumo dos estágios |
| Proteção | Orçamento prévio, reserva atômica, limite rígido de saldo e nenhuma recarga automática por padrão |
| Resultado já gerado | Reabrir sem novo débito |

Os valores são propostas, não produtos ativados. A tarifa precisa incluir fornecedor, câmbio, ferramentas, novas tentativas, custos variáveis e margem. O memo usa hipóteses explícitas para simular contribuição variável, sem chamar isso de lucro líquido. [Plano comercial, fontes oficiais e cálculos](ai-pricing-proposal-20260909.md).

Ordem de implementação recomendada: medição financeira central; reserva e liquidação idempotentes em todas as funções; limites e extrato; piloto com uso real reconciliado; então oferta comercial das recargas. O ledger existente do Heart Team e os controles de ECG oferecem componentes que podem ser reutilizados.

## Estado da entrega

Correções e documentos estão preparados para revisão no GitHub. Não houve deploy, mudança de assinatura, cobrança de clientes, recarga no fornecedor ou redução de limites em produção.

Para concluir a comparação semântica, é necessário regularizar o saldo do provedor de embeddings e executar o script com o mesmo conjunto congelado. A publicação do código continua dependendo da integração da release e da conferência autenticada da interface publicada. Esses passos não devem ser confundidos com as verificações de código, componente e leitura do acervo já executadas.
