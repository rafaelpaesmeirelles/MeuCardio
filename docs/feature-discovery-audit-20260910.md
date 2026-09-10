# Descoberta das funções, Intelligence e identidade mobile — 10/09/2026

PR921, base `db0a3ff71a184e2d6711168427e7565d6e0c9e48`.

## Pedido

Destacar Heart Team em Clínica & Decisão, Assistente WhatsApp em Assistência e CorVIA Intelligence em Ciência & Ensino. Substituir o quadro Timeline da Home científica por Intelligence em desktop e mobile, preservando o restante do layout. Verificar e corrigir o monitor científico para 4h normalmente e 1h em períodos intensos. Corrigir nome do profissional no mobile. A instrução persistente “Sem novo ci backend” permanece vigente.

## Causas verificadas

O catálogo agrupava assistentes sob Inteligência integrada e os ocultava pelas flags de instalação. Heart Team está habilitado na produção. WhatsApp está desabilitado, usa provider sandbox e não possui os campos de integração Meta configurados. Nenhum valor secreto foi coletado ou exposto, e nenhuma mensagem foi enviada. Tornar o acesso visível não constitui ativar um canal Meta ausente; a interface mantém os controles de assinatura e apresenta a indisponibilidade de instalação de forma explícita.

O radar científico existente estava dentro de Diretrizes. A regra de frequência existe (4h/1h), mas o agendamento GitHub ocorre em horários irregulares e a seleção pelo módulo da hora pode pular varreduras esperadas. A correção usa tempo decorrido, exclusão mútua e execução supervisionada local. A interface deve indicar execução e cobertura reais, sem confundir descoberta com síntese IA nem afirmar atividade apenas com uma flag.

A identificação mobile combinava larguras de 48–58px dedicadas ao avatar com regras conflitantes de ocultação/exibição do nome. A correção posiciona o nome tratado abaixo da foto com quebra de linha; desktop permanece preservado. O teste visual passa a conferir texto real com perfil representativo, e não apenas o retângulo da identidade.

## Implementação e validação

Em andamento. O novo monitor e a rota /intelligence reutilizam o radar existente e expõem estado operacional e descobertas recentes. A Timeline permanece disponível como função própria. Registro de revisão, testes focais, gates, resultado de deploy e verificação operacional serão acrescentados quando concluídos. Nenhuma nova suíte backend CI será executada; demais gates permanecem obrigatórios. Credenciais Meta ausentes continuam sendo dependência externa para ativar o WhatsApp de produção.


## Ampliação explícita: três acessos em todo o acervo científico

O responsável esclareceu que original, tradução integral e resumo em português devem estar disponíveis para todos os documentos científicos, além do Intelligence. A auditoria encontrou botões “Traduzido” em documentos/estudos/radar apontando para sínteses, não para tradução integral. A tradução integral real existente está no fluxo privado de upload. A restauração global reutiliza o mecanismo de processamento com artefatos compartilhados por fonte científica, sem expor documentos privados e sem chamar resumo/abstract de texto integral. Traduções exigem fonte completa com permissão, cobertura completa e orçamento editorial existente; downloads e materiais indisponíveis devem ser explicitamente sinalizados. Nenhum lote pago foi disparado como teste.

## Validações locais concluídas até esta etapa

64 testes de política e2contratos exatos de PR/main aprovados.13 testes focais de cadência/runtime em banco QA exclusivo aprovados, com provedores simulados. Revisão independente confirmou concorrência, custos institucionais, heartbeat e ciclo do worker no deploy.4 testes de descoberta/menu/gate e7 testes do monitor/isolamento de coleções aprovados. TypeScript integrado aprovado antes da ampliação do leitor global. A matriz real mobile ainda será executada no Visual QA e inspecionada antes da publicação.


## Trabalho seguinte solicitado

Depois de concluir este trabalho e seu deploy, ampliar Meus Favoritos para salvar qualquer conteúdo do site e reunir os acessos ao original, resumo em português e tradução quando aplicáveis. Reutilizar a mesma identidade de conteúdo e os artefatos científicos compartilhados, sem duplicar processamento. Esta etapa é posterior ao deploy deste PR.


## Revisão integrada e verificações focais

Menus e leitores implementados; Heart Team e Intelligence destacados, WhatsApp visível com estados de instalação e assinatura distintos. O leitor compartilhado foi integrado em 14 páginas científicas, diretrizes e descobertas bibliográficas confiáveis. GET não dispara processamento pago. Alias de estudo resolve para a identidade canônica com validação exata dos downloads autenticados.

A biblioteca mantém fontes por DOI/hash, aquisição de XML integral oficial com identidade e licença verificadas, arquivos cifrados em volume próprio, tradução retomável por segmentos e orçamento editorial existente. Só publica a tradução textual após a cobertura de todos os segmentos; não substitui artigo por abstract. Figuras gráficas e suplementos permanecem no original e essa limitação aparece na leitura. Fórmulas que não podem ser preservadas e textos acima da capacidade atual são sinalizados, sem truncamento silencioso. Documentos privados e decisões de publicação clínica não são modificados. Os materiais preparados são compartilhados para leitura, independentemente de chamadas de IA individuais.

O processamento documental tem worker separado do radar e conclui traduções em andamento antes de abrir novas, dentro do limite existente. A fila registra todo o acervo em lotes de 200, drenando os lotes pendentes sem esperar quatro horas entre eles. Descobertas oficiais confiáveis entram sem depender da síntese anterior; o acesso bibliográfico não publica texto clínico ainda não liberado. Backup, restauração e deploy incluem o volume, o worker e verificação de heartbeat/SHA. A interface informa totais disponíveis, pendências de aquisição e orçamento.

Validações adicionais: 7 testes React do leitor global; 3 casos focais de alias/identidade; TypeScript integrado aprovado após integração nos leitores; 8 testes finais de monitor/isolamento, incluindo contagem verdadeira e acesso sob demanda. Inventário estrito aprovado: 84 rotas React, 55 destinos de menu, 70 routers, 79 páginas e 117 artefatos. Worker documental: 3 testes focais; status/heartbeat: 1 teste focal. Revisão independente cobre autorização, isolamento privado, aquisição limitada, integridade da tradução, cobrança e recuperação sem duplicar chamadas. Resultados finais do backend documental e Visual QA serão anexados antes do merge.

Consulta financeira somente leitura: teto institucional editorial configurado em R$100/mês; nenhum período de consumo institution:editorial materializado no mês atual na consulta. Nenhum teto ampliado e nenhuma chamada paga de teste. A disponibilidade em todo o acervo é progressiva e depende de licença, fonte integral e orçamento; este PR não declara milhares de traduções previamente concluídas.


## Verificação de aquisição real

Aquisição gratuita pela API oficial validada com DOI `10.1002/prca.70052`, PMCID `PMC13449635`, artigo “Proteomic Remodeling in the Failing Left Ventricle Adapting to Dyssynchrony”. O XML real contém licença CC BY 4.0, 99.476 bytes e 44.882 caracteres de texto extraído, com corpo, referências, tabelas e legendas. Nenhuma chamada de IA ou gravação em produção foi realizada. Esta verificação confirma aquisição e extração dessa fonte, não fidelidade de uma tradução ainda não gerada. Migração c0aw20260909 → c1sp20260910 aplicada em banco QA exclusivo com sucesso.


Validação documental concluída antes do commit: 11 testes focais aprovados em três grupos necessários (6 de extração/integridade, 3 de persistência/vínculo e preservação numérica, 2 de autenticação HTTP e truncamento). Migração em QA, aquisição real gratuita e revisão independente aprovadas. Detalhes em scientific-reading-library-20260910.md. Nenhum teste backend CI executado.


## Primeira rodada de gates e correções

PR head caa00bd4: inventário, reconciliação de corpus, cobertura de rotas, Visual QA e referência aprovada passaram. Backend CI completo/focal ficaram skipped. O frontend compilou, mas o precache excedeu o teto por cerca de 11 KB. Foi corrigida a política de carregamento das telas dependentes de conexão, preservando o monitor no shell e as APIs sem cache. Um build focal confirmou precache de 3.113.859 bytes, abaixo de 3.135.488 bytes, sem ampliar o limite.

A inspeção humana das capturas encontrou títulos escuros sobre o fundo escuro do novo monitor, apesar do gate geométrico aprovado. As cores dos títulos passaram a ser explícitas por tema; o gate visual foi ampliado para esse contraste. A área lateral desktop já possui rolagem própria, preservada nesta correção. Originais XML também oferecem link direto à página da publicação. A publicação aguarda os gates da revisão final, sem reutilizar o resultado da geometria como prova de contraste.


Revisão 73088cfb: build e demais gates funcionais/corpus aprovados. Os 30 títulos medidos no monitor tiveram contraste mínimo acima de 9:1 no claro e 14:1 no escuro; os 20 controles ficaram acessíveis após rolagem real. O gate visual detectou comparação incorreta da escolha mobile 320: todas as seis posições verticais do tema escuro estavam deslocadas exatamente -58 px, com larguras, alturas e posições horizontais idênticas. A captura anterior havia alinhado a marca, deixando rolagem residual. O runner agora restaura o topo real antes da comparação e registra a rolagem, sem afrouxar tolerância ou remover a verificação do cabeçalho.
