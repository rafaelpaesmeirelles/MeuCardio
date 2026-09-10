# CorVIA Intelligence — auditoria operacional e correção de agendamento

## Evidência anterior à alteração

Leitura de produção em 10/09/2026, sem chamadas a IA ou mutações: 636 registros com data de publicação (585 em `oficial_aprovada`, 35 `analisada`, 10 `revisao_necessaria`, 6 `aplicada_auto`). A última descoberta registrada ocorreu em 08/09/2026 às 09:53:05 UTC. A existência desses registros comprova captação anterior, não comprova monitoramento contínuo atual.

O workflow `corvia-intelligence-radar.yml` declarava cron a cada hora, mas as duas execuções mais recentes ocorreram em 10/09 às 01:08 e 06:02 UTC. Não havia cron local específico nem serviço supervisionado Intelligence no Compose. A decisão normal usava `current.hour % 4 == 0`: um disparo atrasado podia pular uma varredura já devida. Sucesso do workflow também podia representar somente um skip de agendamento.

A API existente ocultava do monitor todas as descobertas sem análise IA e documento-síntese publicado. Portanto, ausência de itens na interface não distinguia radar parado de bibliografia já captada aguardando análise.

## Correção

- Serviço local `intelligence-radar`, reinício supervisionado, verificação a cada 60 segundos, varredura a cada 4 horas desde o último início. Janelas de congresso existentes ou pelo menos oito publicações confiáveis detectadas nas últimas seis horas reduzem o intervalo para uma hora.
- Trava de sessão PostgreSQL em conexão dedicada, conservada entre commits do pipeline. Worker, CLI/GitHub e descoberta/análise pendente administrativa compartilham exclusão para evitar processamento concorrente.
- Início, conclusão, cobertura e resultado da etapa de análise registrados em auditoria. Heartbeat Redis com validade de 180 segundos distingue trabalhador vivo de simples configuração.
- `GET /api/guideline-updates/status`, autenticado, expõe estado real, cadência, últimas execuções, cobertura e oito descobertas bibliográficas recentes, independentemente da disponibilidade de resumo IA. Não altera aprovação, publicação nem conteúdo.
- `health=degraded` quando há falha, cobertura parcial, análise indisponível/limitada ou uma execução presa por mais de duas horas. `last_success_at` se refere à descoberta com ao menos uma fonte acessível; `analysis_status` explicita a etapa de análise.
- Deploy inclui o worker na construção, parada antes do backup e rollback, ativação após reconciliação e conferência do heartbeat com o SHA da release. A checagem de heartbeat é somente leitura e não chama provedores.
- Mantidos as fontes, pipeline científico, limites e controles de cobrança existentes. Nenhuma chamada paga foi feita como teste; nenhuma publicação científica foi autorizada adicionalmente por esta correção.

## Validação focal

11 testes locais passaram em 88,72 segundos em banco QA exclusivo: atraso do scheduler, primeiro início, cadência normal/pico, trava real entre commits, concorrência, exceção auditada, classificação de saúde e descoberta visível sem IA. Dois casos adicionais passaram em 10,51 segundos e verificam a exclusão da análise administrativa e a visibilidade de limitação/indisponibilidade de IA. Revisão independente final não identificou bloqueios no escopo do runtime. Não foi executado CI de backend. Evidência adicional de execução e deploy deve ser anexada pelo responsável da release após publicação.


## Supervisor da biblioteca científica compartilhada

Após cada descoberta, o radar cadastra um lote de referências sem IA; falha nessa etapa não apaga a descoberta já concluída. O supervisor drena metadados em lotes de 200 por minuto enquanto `has_more=true`; após cobrir o corpus, verifica referências a cada quatro horas. Isso não aumenta a frequência nem os limites da etapa paga.

A etapa documental usa processo independente `scientific-publication-library-worker`, para que extração/tradução em fila não bloqueie a descoberta a cada 4h/1h nem seu heartbeat. O supervisor chama o serviço persistente `seed_publication_queue(db, limit=200)` e `process_one_publication()`, com no máximo uma passagem de processamento por minuto. A trava, retomada do progresso, extração autorizada e reserva do orçamento institucional pertencem ao serviço documental. Nenhum orçamento ou limite foi ampliado na infraestrutura.

O volume `scientific-publication-library` é compartilhado apenas entre backend e worker documental, montado em `/scientific-publication-library` (somente leitura na API, leitura/escrita no worker); não está montado no Caddy, nem misturado ao acervo privado de uploads do assinante. Backup padrão inclui seus bytes e checksum, com retenção de 14 dias; restauração do volume para também seu worker. Artefatos são append-only: rollback do banco pode deixar arquivos órfãos inacessíveis, mas não apaga os bytes das versões anteriormente referenciadas.

O deploy inclui ambos os supervisores no ciclo de parada antes do snapshot/rollback, inicialização depois da reconciliação e confirmação de heartbeat com SHA. O smoke documental confere somente heartbeat e montagem, sem baixar artigos, processar fila ou chamar IA adicionalmente. O processamento ordinário inicia pelo próprio supervisor após a publicação autorizada.

Dois testes puros do supervisor passaram em 2,24 segundos, verificando que falha na descoberta de referências não paralisa a fila existente e que cada rodada limita o processamento a uma passagem. Um terceiro teste focal passou em 2,24 segundos e confirmou a continuação dos lotes de metadados até `has_more=false`, mantendo uma passagem de processamento por rodada. A estrutura Compose foi validada quanto ao isolamento do volume/worker e ausência de acesso Caddy. A integração do serviço persistente é validada pelo responsável pela biblioteca científica.
