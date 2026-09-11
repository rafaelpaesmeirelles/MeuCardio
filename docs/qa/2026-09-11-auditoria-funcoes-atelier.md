# Auditoria funcional Atelier — 11/09/2026

## Retomada e mudança de escopo — 11/09/2026

O responsável retomou as correções e cancelou a integração com rede social.
A remoção operacional está descrita no complemento final deste documento;
resultados anteriores sobre o identificador social são **históricos e superados**,
não descrevem uma função oferecida ou uma pendência de integração.
Permanece o envio manual de foto. K@iros permanece como fonte temporária de
preços por edição, com contratação de outro fornecedor registrada como pendência
em `docs/pricing-architecture.md`. Nenhum contrato foi firmado nesta retomada.

## Estado e limites desta consolidação

**Auditoria local do candidato, com dados e APIs isolados. Não é certificação de produção, do corpus científico nem uma execução completa de CI.** Cobertura por rota significa as ações descritas neste documento, não aprovação irrestrita de todas as regras e integrações de cada função. As correções estão no worktree `MeuCardio-map-atelier`, branch `codex/atelier-mobility-audit-20260911`; não foram publicadas por esta auditoria.

O React real do candidato foi acessado em `http://127.0.0.1:4322`. O preview `4323` habilitou temporariamente as flags locais de Heart Team e WhatsApp para inspecionar suas telas, sem mudar configuração de produção. As requisições de API dos cenários foram interceptadas; as demais requisições externas foram bloqueadas. Os perfis e registros eram fictícios. Favoritos, progresso, mensagens e respostas existiram somente na memória da fixture. Não houve autenticação em produção, consulta de pacientes, alteração de usuários reais, envio externo de mensagens, execução de IA, publicação de conteúdo ou deploy.

Os textos e a imagem usados nas fixtures foram recortados de arquivos já existentes no repositório. O relatório JSON registra seus caminhos e SHA-256. Reutilizar um arquivo nessa fixture **não afirma que ele esteja publicado, disponível em produção ou cientificamente recertificado**. Os contadores mostrados pela interface correspondem ao recorte do teste, não ao inventário real do acervo. As respostas HTTP 503 foram deliberadas; não representam indisponibilidade de produção.

### Inventário de rotas

Inventário extraído de [clinicalRouteRegistry.ts](../../frontend/src/lib/clinicalRouteRegistry.ts), com pontos de entrada conferidos em [App.tsx](../../frontend/src/App.tsx). O script geral [atelier-route-audit.mjs](../../frontend/scripts/atelier-route-audit.mjs) mantém a asserção explícita de 78 entradas. O inventário inclui aliases e padrões parametrizados; não representa 78 telas independentes nem certificação de todas as funções.

| Área | Entradas no registro | Situação neste documento |
|---|---:|---|
| Consultório | 16 | Interface, formulários, busca, detalhes e recuperação de falhas |
| Hospital | 10 | Catálogos, protocolos, rascunhos, controles e limites descritos abaixo |
| Ensino | 12 | Interface com conteúdo e ações testadas; inclui 2 aliases |
| Pesquisa | 13 | Interface com conteúdo e ações testadas |
| Gestão | 23 | Comunicação, administração, formulários, gates e estados retirados |
| Home | 4 | Principal, tarefas, personalização, tour e redirecionamentos |
| **Total** | **78** | **16 + 10 + 12 + 13 + 23 + 4** |

## Varredura geral e leitura dos resultados

- Inventário de **78 entradas × 2 temas × 2 larguras = 312 observações de abertura/renderização**, em 1366×900 e 390×844. Inclui conteúdo vazio, serviço intencionalmente indisponível, aliases e proteções de acesso. Não são 312 testes ponta a ponta.
- A primeira rodada registrou 28 ocorrências de falha, com repetição dos mesmos defeitos entre temas/larguras. Foram separadas as causas reais das falhas de fixture/seletor. Não houve overflow horizontal global nesses estados iniciais; a rodada com conteúdo encontrou um documento móvel com overflow de 265 px.
- Após as primeiras correções, **28 observações focais** em Calculadoras, Assistente, Documentos, Prescrição, Sincronização, Verificação de identidade e Fila de receitas passaram, sem erros JavaScript registrados. Os demais defeitos têm seus próprios retestes abaixo; a matriz completa não foi repetida desnecessariamente.
- Ações com conteúdo foram distribuídas pelos cinco ambientes e componentes transversais. Formulários críticos foram exercitados com registros fictícios, cancelamento e falhas deliberadas. Serviços indisponíveis não foram apresentados como serviços concluídos.
- As imagens e medições não constituem auditoria completa WCAG, teste de leitor de tela, de todos os navegadores ou de todo conteúdo do acervo. Controles fora da primeira dobra só estão cobertos quando as ações descritas os alcançaram.

### Ensino/Pesquisa

- Foram cobertos **25 padrões de rota**, em **1440×900 e 390×844**, no tema claro. A varredura geral de temas/estados vazios é uma evidência separada.
- O consolidado contém **62 linhas de cenário/largura**, não 62 rotas. Ele retém a evidência mais recente por chave `route + width + name`; não soma as execuções iniciais às repetições corretivas.
- Na evidência consolidada desses cenários, há **zero `issues` e zero `pageErrors` registrados**. Isso significa sucesso das ações descritas abaixo; não equivale a “todas as funções certificadas”, revisão completa WCAG ou sucesso ponta a ponta dos serviços.
- As páginas parametrizadas foram exercitadas com slugs concretos selecionados, não com todos os itens do acervo. Busca, filtros e paginação operaram sobre coleções pequenas e modeladas conforme os contratos do frontend.
- Falhas do próprio runner — por exemplo, seletor com papel `textbox` quando o controle real era `searchbox` — foram corrigidas no runner e repetidas. Não foram classificadas como defeitos do produto. Os relatórios anteriores permanecem disponíveis para rastreabilidade.
- A checagem focal de acessibilidade incluiu alvos de progresso, contenção horizontal, foco e rolagem de tabela pelo teclado, além do zoom do fluxograma. Não houve ensaio com leitor de tela nem auditoria completa de contraste de todas as páginas.

## Matriz de Ensino — 12 rotas

Todas as linhas abaixo foram exercitadas nas duas larguras. “Testado” refere-se apenas às ações descritas, com os limites gerais acima.

| Rota | Ações efetivamente testadas | Limite específico |
|---|---|---|
| `/apresentacao` | Selecionar documento; preencher anotação demonstrativa; escolher PPTX; solicitar geração com 503; verificar preservação da anotação e seleção. | Não certifica geração de PDF/PPTX nem conteúdo do arquivo exportado. A anotação foi exercitada nesta tela, não em um editor independente de notas. |
| `/trilhas` | Buscar termo sem correspondência; restaurar busca; confirmar resultado canônico; abrir detalhe pelo link real. | Recorte local de trilhas, não inventário completo de aprendizagem. |
| `/trilhas/timeline` | Selecionar tema; visualizar marco existente com ano/fonte; abrir estudo correspondente. | Não verifica a completude histórica da timeline nem todas as combinações de eixos. |
| `/trilhas/:slug` | Favoritar; marcar etapa concluída; simular 503 ao desmarcar; confirmar preservação do progresso; repetir ação; verificar alvo de progresso 44×44. | Somente duas etapas do recorte e persistência em memória; não certifica progresso salvo no backend. |
| `/material-paciente` | Buscar sem correspondência; restaurar resultado; abrir material. | Não certifica cobertura de todos os temas. |
| `/material-paciente/:slug` | Ler material existente; solicitar PDF com 503; confirmar que conteúdo e ação continuam disponíveis. | Não gera PDF nem entrega material por e-mail ao paciente. |
| `/galeria` | Buscar imagem sem correspondência; restaurar resultado; abrir detalhe. | Recorte do atlas, não todas as modalidades. |
| `/galeria/:slug` | Carregar a imagem real do arquivo local; visualizar achados/fonte/licença existentes; favoritar. | Não acessa a fonte externa nem revalida licença; não usa imagem de paciente obtida de produção. |
| `/casos-clinicos` | Buscar sem correspondência; restaurar caso; abrir enunciado. | Recorte de casos existentes. |
| `/casos-clinicos/:slug` | Confirmar bloqueio sem alternativa; escolher opção do caso existente; registrar com 503; repetir; visualizar explicação canônica. | A resposta é calculada pela fixture a partir do caso existente; não constitui nova recomendação clínica nem grava tentativa real. |
| `/cursos` | Confirmar redirecionamento para `/trilhas` e catálogo com conteúdo. | Alias legado, não uma segunda implementação de cursos. |
| `/cursos/:slug` | Confirmar redirecionamento para `/trilhas`, conforme contrato atual. | O contrato atual leva ao catálogo, não ao detalhe do slug. Não foi alterado nesta auditoria. |

## Matriz de Pesquisa — 13 rotas

Todas as linhas abaixo foram exercitadas nas duas larguras, sem chamadas a serviços científicos ou de IA externos.

| Rota | Ações efetivamente testadas | Limite específico |
|---|---|---|
| `/intelligence` | Ler descoberta de fixture; mostrar monitoramento inativo; atualizar estado com 503; repetir e recuperar o estado. | Não executa monitoramento, descoberta ou cobertura científica real. |
| `/biblioteca` | Abrir catálogo com documentos; filtrar área; abrir detalhe; simular 503 na lista, nos metadados de coleções e na próxima página; recuperar por botões de repetição, preservando primeira página/cursor quando aplicável. | Coleção pequena de fixture; não certifica contagem, publicação, integridade do acervo ou desempenho em escala. |
| `/biblioteca/:slug` | Ler Markdown e referências existentes; favoritar; no documento acessado também por Fluxogramas/Diretrizes, conter tabela e fontes no celular. | Não consulta originais externos nem certifica toda a cadeia de leitura/tradução. |
| `/documentos-cientificos-ia` | Selecionar documento de fixture; abrir recorte TXT privado; alternar leitura; solicitar orçamento e upload com 503. | Acesso AI concedido apenas na fixture. Não chama `analisar`/incorporar, não consome créditos, não valida upload no backend e não produz resultado de IA. |
| `/diretrizes` | Filtrar coleção editorial; abrir documento correspondente. | Não aplica atualização clínica, aprovação editorial ou tradução. |
| `/busca` | Submeter assunto no Tudo com Tudo; mostrar resultados existentes em duas frentes; abrir documento. | Relações do grafo não foram inventadas: endpoints de relações retornam 503. Não certifica busca semântica, indexação ou grafo. |
| `/fluxogramas` | Buscar sem correspondência/restaurar; abrir documento; renderizar Mermaid existente; alternar zoom 150%/100%; focar tabela e enviar comando de rolagem pelo teclado. | Não cria/edita condutas nem testa todos os diagramas. Tela cheia não foi exercitada. |
| `/evidencias` | Buscar sem correspondência; restaurar recomendação; abrir detalhe. | Recorte local, sem varredura de todas as classes, anos ou sociedades. |
| `/evidencias/:slug` | Ler classe/nível existentes e favoritar. | Não reclassifica nem revisa a recomendação científica. |
| `/estudos` | Buscar/restaurar resultado; abrir estudo; simular 503 na listagem, filtros e próxima página; repetir com primeira página/cursor preservados. | Não certifica busca/paginação reais do backend nem todo o catálogo. |
| `/estudos/:slug` | Ler resumo, limitações e referência existentes; favoritar. | Não baixa artigo original nem executa tradução. |
| `/exportar` | Adicionar dois conteúdos; reordenar; solicitar exportação com 503; manter composição; remover item. | Não gera PDF/PPTX/DOCX, não assina e não envia e-mail. O servidor exportador não foi certificado. |
| `/favoritos` | Encontrar favorito criado na sessão; remover com 503; confirmar item preservado; repetir remoção. | Persistência somente em memória. A tela atual não oferece editor independente de notas; não se atribui cobertura a essa função inexistente na interface exercitada. |

## Cinco defeitos corrigidos e evidência de recuperação

As mudanças desta fatia ficaram restritas às cinco páginas abaixo e ao runner de QA. Não houve alteração de CSS/componentes compartilhados, corpus, backend, dependências, workflow ou produção.

| Arquivo | Evidência inicial | Correção | Verificação posterior |
|---|---|---|---|
| [Biblioteca.tsx](../../frontend/src/pages/Biblioteca.tsx) | GET de documentos com 503 gerava `ApiError` não tratado e carregamento sem fim. O mesmo padrão de ausência de tratamento existia nos metadados/paginação. | Erro explícito e repetição separados para coleções/documentos; preservação de página e cursor ao falhar próxima página; descarte de respostas atrasadas. | Lista, coleções e próxima página com 503 → repetição passaram em 1440/390, sem `pageError`. |
| [Estudos.tsx](../../frontend/src/pages/Estudos.tsx) | GET de estudos com 503 gerava `ApiError` não tratado e carregamento sem fim; metadados/paginação também não tinham tratamento. | Erros separados de filtros/resultados; repetição; cursor preservado; interrupção da paginação automática após erro; descarte de respostas atrasadas. | Listagem, filtros e próxima página com 503 → repetição passaram em 1440/390. |
| [CasoClinico.tsx](../../frontend/src/pages/CasoClinico.tsx) | POST de resposta com 503 removia enunciado/opções e impossibilitava repetir. | Manter caso/escolha e exibir erro; limpar erro na nova tentativa; bloquear mudança/reenvio durante processamento. | Escolha → 503 → repetir → explicação do caso existente passou em 1440/390. |
| [Documento.tsx](../../frontend/src/pages/Documento.tsx) | Tabela Markdown e URLs literais das fontes alargavam o documento no celular. | Tabela em região com rolagem horizontal e foco; quebra das URLs com `overflowWrap: anywhere`, sem alteração textual. | Overflow do cenário móvel caiu de 265 px para 0 px; zoom e teclado exercitados; fontes e tabela preservadas. |
| [Trilha.tsx](../../frontend/src/pages/Trilha.tsx) | Botão de progresso medido em 38×44 px no desktop e 32×44 px no celular. | Coluna e largura mínima de 44 px; altura mínima de 44 px, apenas na página. | Alvo 44×44 e sequência de progresso/503/repetição confirmados em 1440/390. |

O parsing TSX das cinco páginas por `esbuild`, a verificação de sintaxe do runner e `git diff --check` passaram durante esta fatia. Isso **não substitui checagem de tipos, build ou CI**; essas etapas pertencem à consolidação da raiz.

## Evidências locais e reprodução

### Artefatos desta execução

Os arquivos de `/tmp` são evidências locais temporárias, não ativos publicados. O consolidado aponta o relatório e screenshot de origem de cada cenário; preservar esses diretórios caso seja necessário arquivar as imagens fora desta máquina.

| Evidência | Caminho |
|---|---|
| Consolidado por rota e cenário | [`/tmp/corvia-science-functional-qa-final/consolidated.json`](/tmp/corvia-science-functional-qa-final/consolidated.json) |
| Última rodada focal | [`/tmp/corvia-science-functional-qa-final/report.json`](/tmp/corvia-science-functional-qa-final/report.json) |
| Rodada corretiva intermediária | [`/tmp/corvia-science-functional-qa-corrected/report.json`](/tmp/corvia-science-functional-qa-corrected/report.json) |
| Histórico inicial, incluindo defeitos e erros de seletor já separados | [`/tmp/corvia-science-functional-qa/report.json`](/tmp/corvia-science-functional-qa/report.json) |
| Tabela móvel contida, com foco | [390-fluxogramas.png](/tmp/corvia-science-functional-qa-final/390-fluxogramas.png) |
| Caso clínico após falha e repetição | [390-caso-resposta.png](/tmp/corvia-science-functional-qa-corrected/390-caso-resposta.png) |

### Scripts

- [atelier-science-functional-qa.mjs](../../frontend/scripts/atelier-science-functional-qa.mjs): fluxos de Ensino/Pesquisa com conteúdo; saída própria; falha do processo quando há `issues` ou `pageErrors` na rodada.
- [atelier-route-audit.mjs](../../frontend/scripts/atelier-route-audit.mjs): inventário/varredura geral. Estados vazios/503 não equivalem a aprovação funcional com conteúdo. Aceita `ATELIER_QA_ROUTES`, `ATELIER_QA_THEMES` e `ATELIER_QA_WIDTHS` para repetir somente o necessário.

Reprodução da fatia funcional, somente quando solicitada e com o Vite local já disponível. O exemplo cria uma saída separada e não sobrescreve os relatórios acima:

```sh
cd "/Users/rafaelpaesmeirelles/Documents/Codex/CorVIA Cardiology Spaces/MeuCardio-map-atelier"
ATELIER_QA_URL=http://127.0.0.1:4322 \
ATELIER_SCIENCE_QA_OUT=/tmp/corvia-science-functional-qa-repro \
/Users/rafaelpaesmeirelles/.cache/codex-runtimes/codex-primary-runtime/dependencies/node/bin/node \
frontend/scripts/atelier-science-functional-qa.mjs
```

O runner usa Chrome instalado e o Playwright do runtime local; `PLAYWRIGHT_MODULE` pode indicar outro caminho já instalado. Não instala dependências nem inicia o Vite. `ATELIER_SCIENCE_QA_ONLY` restringe por nomes de cenário separados por vírgula, por exemplo `caso-resposta,biblioteca-503,estudos-503`. `ATELIER_SCIENCE_QA_PRIOR` aceita relatórios prévios para consolidação deduplicada; herdar um registro anterior não deve ser descrito como nova execução.

### Proveniência científica das fixtures

Os hashes completos estão em `provenance` no consolidado. Foram reutilizados:

- `content/Insuficiência_cardíaca/icfer-classificacao-diagnostico-quatro-pilares.md`;
- `content/Insuficiência_cardíaca/fluxograma-insuficiencia-cardiaca-cronica-por-fracao-de-ejecao-esc-2023.md`;
- `trilhas/metadados.json`, `casos-clinicos/metadados.json`, `material-paciente/metadados.json`, `estudos/metadados.json`, `evidencias/metadados.json`, `galeria/metadados.json`;
- imagem de ritmo sinusal referenciada no catálogo local da galeria.

Não foram escritas novas recomendações, relações clínicas do grafo, traduções, análises ou afirmações de completude do acervo.

## Consultório — 16 rotas

Execução em 1440×900 e 390×844. Nenhuma ação abaixo calculou uma nova recomendação clínica ou gerou documento assistencial para paciente real.

| Rota | Ações efetivamente testadas | Limites |
|---|---|---|
| `/agenda` | Abrir agendamento; confirmação bloqueada sem nome; preencher nome fictício e cancelar; abrir compromisso pessoal, preencher e cancelar; abrir configuração, editar campo local e fechar. | Não grava/exclui compromisso real nem valida sincronização/calendário externo. |
| `/prontuario` | Filtrar pacientes fictícios; selecionar segundo paciente e conferir parâmetro de URL; iniciar atendimento, preencher queixa demonstrativa e fechar. | Não salva atendimento nem vincula prontuário real. |
| `/receituario` | Alternar histórico/nova receita; filtrar histórico; clicar campo e pesquisar medicamento canônico; conferir sugestões; falha de capacidades → erro → repetição. | Não emite, assina ou envia receita; não certifica dose/interação nem cadastro completo de marcas. |
| `/documentos` | Abrir documento em branco, preencher título e cancelar; falha do catálogo → erro → repetição; conferir descrições de ações no celular. | Não certifica geração, assinatura ou entrega de arquivo. |
| `/avaliacao-preoperatoria` | Preencher identificador fictício e procedimento demonstrativo. | Não executa cálculo/parecer clínico, geração ou envio. |
| `/exames` | Pesquisar exame canônico; navegar para detalhe; busca503 → erro → repetição. | Não certifica todos os exames ou busca real do backend. |
| `/exames/:slug` | Abrir exame selecionado e conferir identidade/conteúdo. | Um slug representativo, não todas as instâncias. |
| `/doencas` | Filtrar fibrilação atrial e abrir registro revisado. | Não certifica toda taxonomia ou ligação real com grafo. |
| `/doencas/:slug` | Abrir fibrilação atrial e conferir identidade do registro. | Sem nova revisão clínica das definições. |
| `/medicamentos` | Filtrar fármaco do corpus revisado, verificar resultado e limpar filtro. | Busca real por todos os nomes comerciais permanece dependente da integração com o acervo. |
| `/interacoes` | Selecionar dois medicamentos; conferir habilitação somente com dois; remover um e conferir bloqueio. | Não executa avaliação clínica da combinação. |
| `/condicoes` | Filtrar fármaco e selecionar/desselecionar condição. | Não solicita avaliação clínica. |
| `/calculadoras` | Filtrar RCRI, abrir ferramenta; falha do catálogo → erro → repetição. | Registro-base local; módulos dinâmicos de doses/perioperatório não enumerados. |
| `/calculadoras/:slug` | Abrir RCRI e marcar/desmarcar campo booleano. | Não valida resultado numérico ou algoritmo clínico. |
| `/triagem-sintomas` | Abrir questionário revisado e modificar/reverter resposta. | Não solicita diagnóstico/avaliação. |
| `/assistente` | Disponibilidade503 → erro → repetição; abrir consentimento; provocar falha ao gravar e conferir ausência de autorização/avanço indevido. | Não executa consulta a IA nem acesso externo a agenda/e-mail. |

### Correções clínicas

| Componente | Causa corrigida | Evidência |
|---|---|---|
| `PrescricaoLivreEspecial.tsx` | Handler `err` inicializado depois do retorno antecipado: resposta assíncrona acessava variável não inicializada. Handler reposicionado; erro e repetição visíveis, capacidades não presumidas. | Prescrição e fila de assinaturas recuperam falha sem `pageError`. |
| `Calculadoras.tsx` | Rejeição sem tratamento e spinner permanente. | Recuperação após503; resposta após desmontagem descartada. |
| `Templates.tsx` | Falhas sem tratamento ao carregar, atualizar, salvar ou apagar modelos/histórico. | Erro visível, edição preservada, nova tentativa; textos explicativos restabelecidos no mobile via CSS específico. |
| `Assistente.tsx` | Spinner permanente após falha e consentimento avançando no `finally`, mesmo sem gravação. | Autorização só prossegue após sucesso; erro de disponibilidade recuperável; histórico/conversa atual preservados após falhas. |
| `Exames.tsx` | Taxonomia, busca e paginação sem tratamento de falha. | Mensagem/repetição, filtros e página preservados, respostas obsoletas ignoradas. |

Evidências: `/tmp/corvia-clinical-functional-qa/report.json`, `/tmp/corvia-clinical-functional-qa-remaining/report.json`, `/tmp/corvia-clinical-functional-qa-focal/report.json`, `/tmp/corvia-clinical-exams-recovery-qa/report.json`. A primeira consolidação clínica reteve **48 cenários únicos aprovados** (inclui Hospital), além de **9 testes focais de funções/efeitos reais em VM** em `check-clinical-error-recovery.test.mjs`. Não executa banco ou `conftest.py`.

## Hospital — 10 rotas

| Rota | Ações efetivamente testadas | Limites |
|---|---|---|
| `/cardiologia-intensiva` | Filtrar e limpar referência intensiva canônica. | Recorte local, não certificação do catálogo real. |
| `/emergencia` | Abrir protocolo revisado e conferir detalhe. | Não executa conduta, prescrição ou simulação de emergência real. |
| `/checklists` | Abrir modelo a partir do catálogo. | Sem aplicação a paciente real. |
| `/checklists/:slug` | Abrir modelo revisado e conferir título. | Sem persistência real. |
| `/checklists/alta/:id` | Abrir aplicações fictícias com zero/um item marcado, derivadas da função backend real; conferir seleção/contador; marcar/desmarcar localmente; preencher observação sem enviar; alcançar itens/link de origem. GET503 com erro visível e recuperação por reload. | Nenhuma gravação/finalização real. Não existe botão inline de repetição nesse detalhe. |
| `/heart-team` | Flag local4323; preencher rascunho; impedir remoção de agente obrigatório; alternar opcional; marcar/desmarcar revisão médica; conferir bloqueio de envio incompleto. | Nenhuma análise, orçamento ou gravação real. |
| `/heart-team/:caseId` | Abrir rascunho fictício pelo histórico; conferir erro de orçamento e ausência de execução. | Não simula análise concluída nem consumo de créditos. |
| `/exames-ia` | Preencher objetivo; adicionar/remover TXT local sem dados clínicos; conferir IA desligada. | Nenhum upload real, laudo ou análise. |
| `/ecg-ia` | Conferir alias que mantém URL e renderiza o mesmo componente de Exames IA. | Não se exige redirecionamento que não existe no contrato. |
| `/round` | Ler leito fictício; clicar Arquivar e dispensar confirmação nativa; preencher novo registro sem salvar. | Comprovada ausência de DELETE; nenhuma persistência real. |

Heart Team: `/tmp/corvia-clinical-heartteam-qa/report.json` (duas larguras, sem erros JavaScript). Os cenários de Hospital, exceto a complementação de alta, integram os 48 cenários clínicos acima e **não devem ser somados novamente**.

### Checklist de alta — contrato e acabamento

Defeito backend confirmado: `ver_aplicacao()` expandia `_pendencias()` após preencher `marcados`; o resumo sobrescrevia a lista de IDs por um número. O detalhe React esperava uma lista e falhava em `new Set` quando já havia itens marcados. Em `backend/app/api/checklists.py`, a lista passou a ser atribuída depois da expansão. Helper, verificação do proprietário e snapshot histórico foram preservados.

- **5 testes puros aprovados**, depois de reprodução vermelha: lista vazia, um/dois IDs, contador do helper inalterado, proprietário incorreto404 e aplicação histórica sem modelo. Teste `backend/tests/test_checklist_application_response.py` executável diretamente com Python, sem importar banco, aplicação ou `conftest.py`.
- **4 cenários funcionais aprovados**, zero/um item em1440/390, sem escrita. Evidência: `/tmp/corvia-clinical-applied-checklist-qa/report.json`.
- Superfícies antigas em gradiente escuro foram substituídas por área clara de leitura; textos grafite, indicação obrigatória âmbar e seleção verde legível. Na verificação focal nos dois temas/duas larguras, menor contraste selecionado do checklist **5,745:1**, considerando preenchimento efetivo e transparências; sem overflow/erroJS. Evidência: `/tmp/corvia-clinical-visual-final/report.json`.
- A alteração backend é localizada, **não foi publicada** e não certifica integração HTTP/DB. Uma futura release deve avaliar o gate pertinente, sem duplicar CI indiscriminadamente.

## Gestão — 23 rotas

Execução em1366×900/claro e390×844/escuro, com os focais finais de login Mail também em390/claro. Consolidação: `/tmp/corvia-management-functional-final-20260911.json`, **72 observações finais selecionadas**, sem `issues` nos cenários correspondentes e com overflow global0. Não são72rotas nem uma segunda execução integral. Os snapshots antigos de campos sem nome em Admin/Gerenciar/MinhaConta foram mantidos; seus `aria-labels` foram corrigidos no código, mas não houve nova varredura completa de acessibilidade dessas telas.

| Rota | Ações efetivamente testadas | Limites |
|---|---|---|
| `/indicadores` | Métricas preenchidas; abrir metodologia; alternar30/90/365dias. | Contagens fictícias, sem comprovar receita/atividade real. |
| `/whatsapp-assistant` | Flag local4323; conexão, permissões, histórico, uso/custo; cancelar desconexão/exclusão. | Sem pareamento, mensagem, IA ou alteração de permissão real. |
| `/minha-conta` | Perfil com nome extenso, seções assinatura/certificado/fatura; validação de nome e senhas. | Sem salvar perfil, enviar certificado ou realizar cobrança. |
| `/sincronizacao` | Contas ativa/expirada; consentimento Apple; cancelar remoção;503 e repetição. | Sem OAuth, credenciais ou sincronização externa. |
| `/verificacao-identidade` | Alternar fotos/PDF;503 de status bloqueia formulário; repetir; falha de recarga auth encerra sessão pelo gate existente. | Sem câmera, documentos pessoais, submissão ou aprovação. |
| `/telediagnostico` | Ler aviso de serviço retirado e links. | Estado retirado, não uma função de telemedicina operacional. |
| `/caixa-de-email` | Buscar/favoritas; mensagem HTML sanitizada; metadados de anexo; leitura/volta; compositor; validação; Tab/Escape/foco; envio503 conserva rascunho; falha inicial/repetição; respostas de leitura em ordem invertida. | Sem envio real, upload/download, imagens remotas ou validação do servidor de e-mail. |
| `/corvia-mail` | Caixa sintética ativa, gate público, login próprio; Mostrar/Ocultar por Tab/Space44px; recuperação503 sem confirmação falsa. | Sem login no provedor ou envio de recuperação real. |
| `/usuarios-online` | Renderizar nome longo, registro profissional, presença e ausência de e-mail exposto. | Sem alterar presença; chat testado separadamente. |
| `/privacidade` | Conteúdo e links de contato/navegação. | Não é revisão jurídica; sem enviar contato. |
| `/excluir-conta` | Conteúdo e links de instruções. | Nenhuma exclusão ou solicitação enviada. |
| `/termos` | Conteúdo e links. | Não é revisão jurídica. |
| `/admin/mudancas-clinicas` | Comparar antes/depois; bloquear aprovação sem autorização; motivo obrigatório; trocar filtro descarta formulário. | Nenhuma aprovação/rejeição publicada ou revisão clínica. |
| `/admin/atividade` | Gráfico/tabela, dois períodos e filtros;503 conserva últimos dados com aviso. | Dados fictícios, não mensuração real. |
| `/admin` | Usuários, pré-autorização, solicitações/canal; abrir/fechar recuperação. | Sem concessão de acesso, convite ou e-mail. |
| `/admin/usuarios` | Dois assinantes fictícios; buscar/filtrar/limpar; abrir ficha e voltar. | Nenhum assinante alterado. |
| `/admin/usuarios/:id/gerenciar` | Abrir histórico/risco; bloquear senhas divergentes e exclusão sem confirmação correta. | Sem alterar usuário, perfil de acesso, senha ou sessão. |
| `/admin/usuarios/:id` | Percorrer cinco abas de perfil, plano e histórico. | Sem documentos pessoais, download ou aprovação. |
| `/fila-telediagnostico` | Conferir aviso de fila retirada. | Não processa fila real. |
| `/receitas-para-assinatura` | Recuperação do componente compartilhado de prescrição; abertura nos dois temas/larguras no reteste geral. | Cobertura da fatia clínica/geral, não duplicada nas72observações de Gestão; nenhuma assinatura/aprovação real. |
| `/admin/operacoes-ia` | Flag local4323; métricas de HeartTeam/WhatsApp, assinantes e custos. | Não comprova processamento clínico nem faturamento. |
| `/assinatura` | Dois planos, gasto/reserva/carteira; orçamento negativo rejeitado. | Checkout indisponível na fixture; nenhum pagamento, recarga ou alteração real. |
| `/admin/usuarios-online` | Alias conferido no registro e na varredura geral, levando à presença. | Não é segunda validação funcional independente. |

### Correções de Gestão e Mail

- **Sincronização:** estado inicial vazio em503 passou a erro explícito/repetição; dados recebidos anteriormente permanecem em falha de atualização.
- **Identidade:** rejeição de status sem tratamento passou a erro/repetição; formulário não é liberado sem status válido. A recarga de autenticação é aguardada; se falhar, o comportamento existente encerra sessão, sem presumir aprovação.
- **Mail mobile:** busca e Nova mensagem voltaram a ser acessíveis; adicionado retorno do leitor à lista; controles e superfície de leitura receberam acabamento Atelier.
- **Compositor Mail:** diálogo nativo, foco inicial, contenção de Tab, Escape, retorno ao acionador; erro dentro do compositor; falha de envio conserva rascunho.
- **Mail inicial:** falha de metadados deixou de produzir carregamento permanente, com erro/repetição explícitos.
- **Leitura Mail:** respostas atrasadas de A não substituem B; sequência também protege anexos e troca de contexto/pasta.
- **Recuperação de senha Mail:**503 antes anunciava envio e gerava rejeição sem tratamento. Agora só mostra a confirmação genérica depois de resposta bem-sucedida, preserva endereço e permite repetir em falha. Não revela existência da conta.
- **Administração/conta:** nomes acessíveis associados a controles antes sem nome; nenhuma regra de autorização alterada.

Runner reprodutível: `frontend/scripts/atelier-management-functional-qa.mjs`; fixtures embutidas, servidor obrigatório em loopback, requisições interceptadas. Aceita `QA_ROUTES`, `QA_WIDTH`, `QA_FOLLOWUP`, `QA_RACE`, `QA_AUTH` e `QA_LOGIN` para foco. O aviso de instrumentação Playwright no iframe sandbox de e-mail é identificado separadamente; a proteção sandbox permanece e os demais erros JavaScript continuam falhando o teste.

## Entradas públicas complementares

Páginas públicas foram verificadas sem sessão válida real, em1366/claro e390/escuro. Rotas públicas compartilhadas com Gestão não são somadas novamente ao inventário78.

| Entrada | Ações efetivamente testadas | Limites |
|---|---|---|
| `/entrar` | Credenciais fictícias inválidas →401visível; permanece no login. | Sem autenticação válida/cookies de servidor. |
| `/solicitar-acesso` | Campos profissionais condicionais; validações de recuperação/senha. | Nenhum cadastro enviado. |
| `/esqueci-senha` | Validar endereço e resposta genérica200simulada. | Nenhum e-mail enviado. |
| `/redefinir-senha` | Token explicitamente fictício; divergência de senhas bloqueia ação. | Nenhum token válido ou senha alterada. |
| `/validar` | Normalizar código e navegar para código inexistente;404visível. | Sem PDF/assinatura real. |
| `/validar/:codigo` | Detalhe inexistente via `/validar/QAINEXISTENTE`. | Não certifica validação criptográfica. |
| `/produto` | CTAs de entrada/cadastro com destinos corretos. | Vídeo/download não reproduzidos. |
| CorVIA Mail, Privacidade, Termos, Excluir conta | Gates, conteúdo e links conforme matriz de Gestão. | Sem caixa real, exclusão ou revisão jurídica. |

## Home — 4 rotas e controles transversais

| Rota | Ações efetivamente testadas | Limites |
|---|---|---|
| `/` | Selecionar cada um dos cinco espaços; conferir exclusividade da imagem/destaque; quinze combinações espaço/modo; atalhos12/8/8; cancelar personalização; reordenar/salvar/recarregar/restaurar; abrir Agenda, recolher arquitetura, entrar em Foco, trocar função e voltar ao espaço. | Preferências do navegador isolado, não sincronização multi-dispositivo. |
| `/tour` | Percorrer nove capítulos pelos botões reais, desde início até última etapa, com controles alcançáveis no celular. | Não certifica vídeo/áudio de divulgação nem integração de onboarding no backend. |
| `/tour/cardiology-spaces` | Conferir entrada/redirecionamento legado na varredura de rotas. | Alias não conta como segundo tour funcional independente. |
| `/em-breve` | Conferir resolução da rota/gate para perfil administrativo fictício. | Outros perfis/estados de autorização não esgotados. |

Geometria da principal conferida em **1366×650, 820×1024, 390×844 e 320×740**, incluindo notebook de pouca altura e celular estreito. Catálogo/personalização: Escape, retorno de foco e contenção do atalho Ctrl+K dentro do diálogo. Evidências: `/tmp/corvia-home-functional/report.json` e `atelier-reference.json` no mesmo diretório. São 24 registros de referência e 11 ações registradas, não novas rotas.

### Chat

Falhas reproduzidas: histórico atrasado de A substituía conversa B; envio atrasado para B entrava em A e apagava seu rascunho; Escape não fechava; resposta de histórico podia apagar mensagem chegada pelo socket; reabrir conversa não recuperava mensagens recebidas enquanto minimizada. Correção vinculou requisições/rascunhos ao destinatário, preservou mensagens novas, recuperou histórico ao reabrir e restaurou foco ao acionador.

**14 verificações aprovadas**, em1366/390: contador de não lidas; histórico trocado; envio trocado e rascunho; mensagem recebida durante carga; Escape/foco; não marcar como lida enquanto minimizado; atualização ao reabrir preservando rascunho. Fonte: `/tmp/corvia-chat-final/report.json`; runner `frontend/scripts/atelier-chat-functional-qa.mjs`. WebSocket inerte e HTTP interceptado: não certifica entrega real, reconexão de socket ou recebimento em outra conta/dispositivo.

### Ajustes de acessibilidade/legibilidade compartilhados

- Descrições das ações em Documentos deixaram de ser escondidas no celular; ícones e textos preservam a identidade Atelier.
- Label de item da prescrição ajustado de ciano para cobre legível e14px; também foi neutralizado `-webkit-text-fill-color` do tema antigo, que fazia o PNG continuar ciano mesmo com a propriedade `color` correta. Medida focal efetiva: **6,407:1** sobre superfície clara. Campos, placeholders, nota e labels aninhados receberam escopo de superfície clara de prescrição nos dois temas.
- A inspeção de prescrição foi levada até o final do formulário: 20 campos/8 placeholders por contexto, label de quantidade, nota C5, Uso contínuo e resumo. Resumo passou a superfície clara com metadados ≥14 px; seu menor contraste focal nessa etapa foi 6,093:1. A regra de posição foi depois alterada para `static`, retirando o comportamento sticky sob a topbar. As capturas de `/tmp/corvia-prescription-visual-final/report.json` e `/tmp/corvia-prescription-summary-final/report.json` antecediam a mudança de posição, e a primeira tentativa opcional em outra fixture não encontrou o resumo em 12 segundos. **Essa lacuna foi posteriormente fechada:** os quatro contextos preenchidos de `/tmp/corvia-prescription-pricing-filled-final/report.json` passaram, incluindo a asserção explícita de `position: static` e imagens do resumo populado; ver complemento de prescrição abaixo. Os relatórios antigos permanecem como histórico, não como resultado final desses contextos.
- Botão Mostrar/Ocultar senha devolvido à ordem de Tab; alvo aumentado para44px e espaço do texto reservado. Links com aparência de botão no conteúdo têm altura mínima44px.
- Causa comum de superfícies de campo inconsistentes e placeholders pouco contrastantes: o contrato legado de input possuía nove exclusões de tipos e maior especificidade que o contrato Atelier. Acrescentado contrato explícito de **cores**, sem alterar dimensões, para os campos textuais da área de trabalho. Favoritos e decisões editoriais mantêm suas exceções escuras; campos nativos não textuais foram excluídos. O pré-operatório recebeu apenas uma classe no wrapper já existente e regras de contraste de labels/títulos dentro dos cartões, sem mudança de lógica clínica.
- Verificação focal desse contrato em Pré-operatório, Biblioteca e Favoritos: escuro em 1366/390 px e claro em 390 px, com 108 medições pós-ajuste de estado normal, hover e foco. O placeholder de Pré-operatório/Biblioteca passou de **3,489:1 para 4,790:1** no antes controlado; o texto preenchido final atingiu **12,787:1**. O texto preenchido do antes controlado já tinha contraste suficiente: não foi reproduzida nele uma falha de contraste. Favoritos escuro preservou texto em **11,423:1** e placeholder em **7,092:1**. Dimensões idênticas, sem overflow adicional nem erro JavaScript. O antes foi obtido removendo apenas o bloco novo do estilo em memória, não reconstruindo produção antiga. Evidência: `/tmp/corvia-field-palette-qa/report.json`.
- O runner de contraste terminou com código 1 exclusivamente porque seu bloqueio genérico registrou nove chamadas automáticas de presença (`/api/presence/heartbeat`), todas interceptadas com 403. As medidas pós-ajuste de texto, placeholder e foco passaram. Esse resultado não é apresentado como aprovação genérica do processo, nem como falha do produto ou mutação real.
- A borda normal de campos claros ainda tinha contraste de 1,878:1, identificado nessa medição. Corrigida para `#7f8a81`, preservando foco, campos desabilitados e o estado `aria-invalid`; superfícies explicitamente escuras usam `#8aa399`. Os três focais finais passaram: Pré-operatório claro/escuro em 390 px, borda **3,554:1** e foco **5,344:1**; Favoritos escuro em 390 px, borda **4,782:1** e foco **7,692:1**. Texto e placeholder permaneceram acima de 4,5:1. Evidência: `/tmp/corvia-field-border-final/report.json`. O processo bruto registrou código 1 pelo timeout opcional de Prescrição descrito acima, não por falha nesses três checks de borda/foco.
- As medidas focais não equivalem a revisão WCAG completa nem aprovação de contraste de todo conteúdo.

## Validação do conjunto e limitações operacionais

Esta rodada corrigiu defeitos reproduzidos e preservou a identidade aprovada; não mudou conteúdo científico, regras de autorização, planos comerciais ou configuração de produção. As skills de depuração, estratégia de testes e acessibilidade orientaram a separação entre causa de produto, erro de fixture, correção, repetição focal e limite de integração. As alterações de mapa/menu que já existiam neste worktree foram preservadas; suas baterias anteriores não foram repetidas.

A primeira checagem de tipos passou e o bundle foi gerado em 13,56 s. Depois dos ajustes de recuperação Mail, classe do pré-operatório e CSS, foram produzidos bundles atualizados para os arquivos modificados; isso não repetiu a matriz funcional. O aviso de tamanho de chunks do Vite não constitui certificação de desempenho; não foi executado teste de carga.

**Validação final do candidato:** `tsc -b` aprovado depois das últimas mudanças TypeScript; build Vite/PWA aprovado após o último ajuste de CSS, em **13,55 s**; `git diff --check` sem erros. O bundle inclui os arquivos finais de produto desta rodada. O inventário foi confrontado com a matriz deste relatório: **78/78 padrões registrados estão documentados**, incluindo aliases e gates. Nenhum desses resultados representa publicação ou teste ponta a ponta em produção.

Não foi executado CI integral de backend nem criada segunda execução remota. Para a alteração localizada do checklist, foram executados os cinco testes puros pertinentes, sem banco. Os testes funcionais de interface que já estavam aprovados não foram repetidos por mudanças de outro módulo; as repetições ocorreram nos casos corrigidos ou em contratos compartilhados efetivamente alterados.

Ainda precisam de ambiente de homologação, identidades fictícias autorizadas e serviços configurados para uma validação de ponta a ponta:

1. Criar/editar/excluir e reler registros persistidos de agenda, prontuário, round e checklist; verificar associação ao paciente e permissões entre usuários.
2. Emitir/baixar/assinar documentos e validar criptografia; enviar e confirmar entrega de e-mail/material ao destinatário de teste.
3. Autenticação válida, cookies/sessões reais, recuperação de senha com recebimento, KYC, OAuth, caixa postal e mensagens entre duas contas/dispositivos.
4. Busca real sobre todo o acervo, nomes comerciais, definições, indexação semântica e relações do grafo Tudo com Tudo. Esta rodada não comprova cobertura dos mais de11mil itens citados pelo usuário.
5. IA para Exames, Heart Team, WhatsApp e geração científica com provedores/orçamento reais, sem presumir sucesso de uma prévia local.
6. Cobrança, checkout e carteiras em ambiente de teste; desempenho, todos os perfis de permissão, navegadores, dispositivos e todas as instâncias parametrizadas.

Também não foram certificados resultados médicos dos algoritmos, revisão jurídica, acessibilidade WCAG completa, ampliação200% de todas as páginas ou o vídeo de divulgação. Serviços retirados e flags desabilitadas foram documentados como tais, não apresentados como funcionalidades operantes.

**Nenhum paciente, usuário ou compromisso real foi criado/alterado; nenhuma mensagem, documento clínico ou cobrança foi enviado. Não houve deploy nesta auditoria.** O próximo responsável deve partir deste worktree, preservar as alterações anteriores e confirmar o escopo/gate de uma futura release; não publicar a partir de artefatos temporários nem tratar este relatório como evidência de produção.

## Complemento solicitado — 11/09

### Administração, reflow e nomes acessíveis

Complemento **focal**, sem repetir a matriz78 nem as baterias já aprovadas. Foram reutilizados os contratos sintéticos de `frontend/scripts/atelier-management-functional-qa.mjs`; todas as APIs foram respondidas localmente, tráfego externo bloqueado e qualquer mutação recusada. As chamadas automáticas de presença bloqueadas são comportamento da fixture, não falha do produto. Um navegador isolado foi fechado ao terminar cada execução.

| Contexto adicional | Evidência efetivamente obtida | Limite |
|---|---|---|
| `/admin`,390×844,escuro | Os26controles inicialmente renderizados têm identificação associada; abrir Recuperação e Rejeitar sem submeter revelou dois campos condicionais ainda dependentes só do placeholder. | Chrome fornecia nome AX pelo placeholder; não se afirma que os campos eram inteiramente invisíveis ao leitor de tela. |
| `/admin/usuarios/990101/gerenciar`,1366×540,claro | Os24controles renderizados têm identificação associada; campos inicial/final alcançáveis por rolagem e foco; overflow horizontal global0. | Não executa alterações, exclusão ou revogação; não certifica todos os focos/controles dessa página. |
| `/minha-conta`,820×900,escuro | Os43controles renderizados têm identificação associada; campos inicial/final alcançáveis; overflow horizontal global0. | A legibilidade dos textos não foi presumida a partir dos nomes: o residual de contraste abaixo foi medido separadamente. |
| `/minha-conta`,683×450,DPR2,claro | Reflow equivalente ao espaço CSS de uma janela1366×900 ampliada200%; controles e rolagem representativos preservados, sem overflow global. | Emulação de viewport/DPR, **não acionamento do zoom nativo do navegador**, ensaio de leitor de tela ou certificação200% de todas as páginas. Os43controles são a mesma página, não43funções adicionais. |

O runner `/tmp/corvia-audit-gaps-local.mjs` e `/tmp/corvia-audit-gaps-local-20260911/report.json` preservam os quatro contextos, snapshots DOM/AX, requisições, imagens e limites. Não ocorreram erros JavaScript nesses contextos; a aprovação é restrita às verificações descritas.

**Correção pontual em `frontend/src/pages/Admin.tsx`:** o e-mail secundário recebeu `aria-label="Segundo e-mail independente para recuperação"`; o motivo recebeu label visível `Motivo da rejeição (opcional)`, associado por `htmlFor`/ID único por usuário. Lógica de recuperação, decisão, autorização e payloads não mudou. O reteste foi somente dos dois campos, em390/escuro: Enter abriu as condições, Tab alcançou os campos e depois os botões seguintes; texto fictício permaneceu; o label do motivo continuou visível após digitação. A árvore AX confirmou origem `aria-label` e `label for`, respectivamente. **Dois focais aprovados**, sem submissão nem erro JavaScript.

Evidência final: `/tmp/corvia-admin-labels-followup-final-20260911/report.json`, `admin-recovery-390-dark.png` e `admin-rejection-390-dark.png` nesse diretório. Runner: `/tmp/corvia-admin-labels-followup.mjs`. A primeira tentativa do runner conservou um locator cujo texto mudou de “Acesso e recuperação” para “Fechar recuperação”, passando a selecionar outro botão; esse erro de instrumentação foi corrigido antes do resultado final. Não foi um defeito de navegação do produto.

### Contraste focal corrigido — Minha Conta

A imagem do contexto820/escuro revelou textos pálidos nos cartões Senha/Assinatura. A medida foi limitada a **seis textos em820 e390**, sobre `.conta__grid > .cartao` com fundo sólido `#FFFDFA`, sem preencher senhas nem acionar cobrança:

- Senha atual, Nova senha, Repita a nova senha e Mostrar senhas: `color` e `-webkit-text-fill-color` `#B4CBD1`,14px, **1,667:1**.
- “Acesso administrativo”, no `p > strong` do cartão Assinatura: `#EFFBFC`,16px, **1,041:1**.
- “Acesso concedido administrativamente — sem cobrança.”: `#8BA0AE`,16px, **2,673:1**.

Falha reproduzida e **corrigida pela raiz em `corvia-atelier-content.css`**, preservando o fundo claro dos cartões. O reteste repetiu somente os mesmos seis textos em820/390: labels e “Acesso administrativo” passaram para `#263936`, com **12,018:1**; a informação de acesso concedido passou para verde `#214F45`, com **9,115:1**. `color` e `-webkit-text-fill-color` finais coincidem; tamanhos14/16px e fundo `#FFFDFA` permaneceram. **12medições finais aprovadas**, sem erro JavaScript, sem preencher senha, acionar cobrança ou enviar ação. O navegador foi fechado.

Fonte: `MinhaConta.tsx`, labels do cartão Senha e status do cartão Assinatura. Antes preservado: `/tmp/corvia-account-contrast-focal-before-20260911/report.json`. Final: `/tmp/corvia-account-contrast-focal-final-20260911/report.json`, com os PNGs `minha-conta-820-dark-password.png`, `minha-conta-390-dark-password.png` e `minha-conta-390-dark-subscription.png`. Runner: `/tmp/corvia-account-contrast-focal.mjs`; execução final com `ACCOUNT_QA_OUT=/tmp/corvia-account-contrast-focal-final-20260911`. A aprovação se restringe a esses textos e contextos, não ao contraste de toda Minha Conta.

### O que este complemento ainda não comprova

Os testes de atributos, teclado e geometria não validam autorização administrativa no servidor. As prioridades de homologação continuam sendo: persistência/associação entre pacientes e usuários; autorização cruzada entre contas; emissão/assinatura/validação criptográfica e entrega; sessão/recuperação/KYC/OAuth/mensageria reais; busca e grafo sobre o acervo publicado; provedores de IA e cobrança configurados. Simular respostas200/503 não resolve essas lacunas.

Já zoom nativo e leitor de tela permanecem verificações locais possíveis, porém não executadas neste complemento; não dependem de credenciais clínicas e não devem ser confundidas com bloqueios de homologação. Os runners científicos, gestão, clínica, Home e Chat já listados servem para focais selecionados, não como autorização para repetir suas matrizes completas.

**Fluxogramas — tela cheia:** focal adicional aprovado em1440×900 e390×844,claro, com o documento canônico local já usado no harness científico: Enter no botão acionou a API nativa do Chrome (`fullscreenElement`, `:fullscreen` e eventos `fullscreenchange` confirmados, sem simulação); o mesmo controle encerrou tela cheia e conservou o foco; Shift+Tab alcançou Zoom e Tab retornou ao botão. SVG preservado, botão101×44px, zero erros JavaScript, APIs isoladas e navegador fechado. Evidência: `/tmp/corvia-fluxogramas-fullscreen-20260911/report.json` e PNGs `fluxogramas-{1440,390}-native-fullscreen.png`/`-returned.png`; runner `/tmp/corvia-fluxogramas-fullscreen-qa.mjs`. São dois contextos da API nativa em Chrome desktop headless, **não certificação de aparelho móvel físico, atalho Escape ou leitura de todos os diagramas**.

### K@iros — correspondência conservadora e recorte disponível

O matcher de `backend/app/services/pricing/kairos_provider.py` foi corrigido para reconhecer sais/referências canônicas pertinentes sem confundir um princípio ativo isolado com uma associação fixa. A ordem dos componentes pode variar, mas o conjunto de princípios ativos deve corresponder; marcas auditadas conservam a correspondência explícita. Produto ausente ou outra marca não é inferido.

Resultado isolado já obtido e comunicado pela raiz: **7 testes novos + 6 testes existentes aprovados**, respectivamente em `backend/tests/test_kairos_matching_no_db.py` e `backend/tests/test_pricing_kairos_provider.py`. O primeiro arquivo documenta a execução direta sem banco/conftest, compilando o provider com substituição somente dos imports ORM/tipos. Essa evidência não é a suíte completa de backend nem integração real com banco, autenticação ou dados publicados. Nenhum teste foi repetido para redigir este adendo.

O snapshot existente `medicamentos/kairos-453-2026-08.json` contém **13 produtos e 52 apresentações**, edição **453**, competência **agosto de 2026**. Esses números foram conferidos no arquivo do repositório, não consultados em produção. Não foi acrescentada correspondência para ATesto, importado novo feed externo ou ampliado o catálogo. As opções mantêm valores literais, intervalo mínimo/máximo, edição, competência e página da fonte; não recebem EAN/identificador CMED inventado nem são apresentadas como atualização de preço em tempo real. K@iros permanece a camada de inteligência de mercado do arquivo, separada da referência regulatória CMED/ANVISA.

### Prescrição — catálogo, preço por apresentação e recuperação

O resultado comercial que trazia marca sem apresentação preenchida ocultava o seletor. O frontend de `Receituario.tsx` passou a manter as apresentações disponíveis para seleção explícita, sem escolher automaticamente um produto comercial. A seleção exata conserva o intervalo de preço e a proveniência; mudar o medicamento ou editar a apresentação invalida a referência comercial anterior. Falha503 da consulta de apresentações é mostrada com ação própria de repetição. A sequência da requisição impede que uma resposta atrasada do medicamento anterior preencha o item atual.

Ao recriar uma prescrição a partir do histórico, medicamento e apresentação são preservados, mas **preço e sua proveniência são limpos e exigem nova consulta**. Os novos campos de preço não são persistidos pelo backend atual. A leitura dessa regra no código não equivale a testar salvar/reabrir uma receita contra o servidor real.

Foram consolidadas **3 variantes × 4 contextos = 12 observações finais aprovadas**, em desktop1366×900 e mobile390×844, claro/escuro. Não são 12 rotas nem nova matriz completa:

| Variante | Evidência final selecionada | Resultado e limite |
|---|---|---|
| Catálogo comercial sem apresentação inicial | `/tmp/corvia-prescription-pricing-patched/report.json`, somente os quatro casos `prescription-pricing-catalogue` | 4 aprovados: apresentações com preço continuam expostas, sem escolha comercial automática. Os quatro casos `filled` antigos desse mesmo arquivo ainda falhavam antes do ajuste seguinte e **não** foram contados como aprovados. |
| Apresentação exata e resumo preenchido | `/tmp/corvia-prescription-pricing-filled-final/report.json` | 4 aprovados: faixa literal/proveniência, limpeza do preço ao alterar apresentação/medicamento, resumo populado e `position: static`. Em cada contexto foram medidos 24 textos, todos mensuráveis no relatório final; menor contraste **5,778:1**. |
| Falha503, repetição e resposta atrasada | `/tmp/corvia-prescription-pricing-recovery-confirmed/report.json` | 4 aprovados: erro explícito recupera pela própria ação de repetição; resposta atrasada não transfere preço para outro medicamento. Sem consulta a provedor externo. |

Runner existente: `frontend/scripts/atelier-clinical-functional-qa.mjs`, variantes `prescription-pricing-catalogue`, `prescription-pricing-filled` e `prescription-pricing-recovery`. Os respectivos diretórios preservam imagens, requisições interceptadas e a proveniência do recorte. Campos e valores foram exercitados na interface React com APIs isoladas; a fonte do preço e a ausência de envio real não foram omitidas.

### Validação posterior e escopo ainda pendente

A raiz registrou **`tsc` aprovado** em `/tmp/corvia-prescription-final-types.log` e **build Vite/PWA aprovado em 15,11 s** em `/tmp/corvia-prescription-final-build.log`, após os ajustes de prescrição. Esse é o resultado posterior ao build de13,55 s descrito na etapa anterior; não foi executado novo build ou CI nesta consolidação documental.

Continuam pendentes a integração autenticada, persistir/reler receitas contra o backend, envio/recebimento e assinatura/validação criptográfica em homologação. A revisão adicional dos dados da operadora e dos PDFs está registrada abaixo. Nenhum resultado local acima comprova deploy, preço vigente em produção, cobertura integral do catálogo ou fluxo ponta a ponta.

## Complemento — identidade institucional em receitas, atestados e laudos

Pedido adicional de 11/09: imprimir razão social, CNPJ e endereço completo da operadora CorVIA juntamente com os dados profissionais. A identidade foi transferida literalmente de `pdf_documento.EMPRESA` para `backend/app/services/pdf/identidade_institucional.py`; a importação anterior continua compatível por reexportação. Não houve consulta cadastral à Receita Federal, alteração dos valores empresariais, acesso a cadastro privado de paciente ou emissão real.

- **Razão social:** Meirelles e Maluf Serviços Médicos e Biomédicos Ltda.
- **CNPJ:** 53.382.596/0001-06.
- **Endereço:** Av. 11, nº 423, Centro, Itapagipe/MG, CEP 38240-000.
- **Rótulo:** “Operadora da plataforma CorVIA”, distinto da identificação do profissional emitente.

Nas receitas comum e de controle especial, a identificação institucional agora integra uma seção própria dentro do quadro de identificação, abaixo das marcas e dos dados profissionais. O logo CorVIA usa 60×16 mm; o logotipo profissional preserva a proporção dentro de 38×34 mm (34×34 mm no caso quadrado). Na RCE, eram respectivamente 30×8 mm e 14×14 mm antes desta correção. Atestados e laudos mantêm sua composição, com a operadora identificada na coluna institucional ao lado do médico; os tamanhos de marca desses documentos não foram alterados neste complemento.

O dado empresarial é complementar, não substitui nome, CRM/UF, RQE quando houver, contato, endereço e assinatura do profissional. Essa distinção foi conferida na [Resolução CFM 2.381/2024, art. 2º](https://sistemas.cfm.org.br/normas/visualizar/resolucoes/BR/2024/2381). A presente revisão de diagramação **não é uma certificação jurídica integral** de todos os fluxos de emissão nem transforma uma análise assistiva por IA em laudo assinado.

### Caminhos cobertos

| Caminho | Implementação |
|---|---|
| Receituário comum | `receituario.py` → `receituario_comum`, quadro com operadora e profissional |
| Receita de Controle Especial | `receituario.py` → `receita_controle_especial`, quadro com operadora e profissional; medição/paginação inclui a altura institucional |
| Atestados e laudos por modelo; atestado rápido; documento livre; documentos do Round | `GeneratedDocument` → `documento_generico`, cabeçalho institucional compartilhado |
| Prescrição livre/especial encaminhada para assinatura | `prescricao_especial.py` → `documento_generico` |
| Documentos de calculadora e avaliação pré-operatória | `GeneratedDocument` → o mesmo `documento_generico` |
| Impressão manual legada no Round | Caminho HTML independente localizado: `/prescriptions/{id}/imprimir` → `PatientPrescricao` → `CabecalhoDocumento`; acrescentado retorno canônico `operadora` e bloco institucional no cabeçalho |

A auditoria estática dos cinco pontos de criação de `GeneratedDocument` não encontrou outro gerador clínico independente. Exportação universal do catálogo não é emissão de documento de paciente. IA de ECG/exames e `service_orders` não foram tratados como emissores de laudo: os fluxos inspecionados não emitem esse documento assinado.

Arquivos já persistidos/assinados continuam sendo servidos com seus bytes originais; não houve reescrita ou reassinatura. A exceção preexistente são documentos legados sem arquivo persistido, que podem ser regenerados na leitura usando o gerador atualizado.

### Evidência focal dos PDFs e do contrato de impressão

`backend/tests/test_prescription_branding_layout.py`: **8 testes isolados aprovados em 7,685 s**, executados diretamente sem aplicação, ORM, banco ou `conftest`. Incluem dados canônicos e reexportação; razão social/CNPJ/endereço e profissional em cada página dos quatro tipos, curtos e longos; proporções de marca; ausência de sobreposição; duas vias; conteúdo e campos C5; reserva de assinatura; e rejeição do cabeçalho que exceda o espaço seguro. O teste inicial de cinco casos foi ampliado devido ao pedido institucional novo, não repetido sem mudança de código.

Quatro prévias finais em `/tmp/corvia-institutional-identity-demo/report.json`: RCE longa com 8 páginas (4 por via), receita comum longa com 2, atestado curto com 1 e laudo longo com 3. **14 páginas renderizadas e inspecionadas.** A RCE longa ganhou uma página por via por reservar 15,8 mm para a operadora; conteúdo e área de assinatura foram preservados. Os dados da operadora são canônicos; paciente, profissional, item clínico e logotipo profissional são explicitamente demonstrativos. O código real continua utilizando o upload existente do profissional, que não foi acessado nesta revisão.

`backend/tests/test_prescription_print_identity_no_db.py`: **3 testes isolados aprovados em 0,007 s**. A função real de impressão é compilada por AST com dependências controladas: confirma operador como cópia do cadastro canônico, busca e autorização do paciente antes de serializar, resposta 404 sem registro e negação de acesso sem serializar dados. Não equivale a autenticação/consulta contra banco real.

Na impressão HTML, ausência de qualquer um dos oito campos institucionais essenciais bloqueia a abertura da impressão e apresenta erro. A preparação aguarda o cabeçalho e os recursos de imagem/fonte; a troca de paciente ou desmontagem invalida a solicitação pendente. A alteração não modifica o cadastro clínico nem torna a impressão legada, que usa a identificação resumida do paciente, equivalente ao fluxo completo de receita revisada e assinada.

### Impressão manual — defeitos reproduzidos e corrigidos

O fluxo React real `/round` → paciente fictício → histórico de prescrição → “Imprimir para assinatura manual” foi exercitado em 1440 e 390 px, com todas as APIs isoladas e sem impressão física. A primeira execução produziu **cinco páginas A4 para um item**, com três páginas vazias, cabeçalho na quarta e paciente/item na quinta. O logotipo profissional tinha caixa 0×0 apesar do arquivo carregado. Evidência anterior: `/tmp/corvia-round-manual-print-20260911/`.

Correções em `PatientPrescricao.tsx` e `document-header.css`: folha montada em portal diretamente no `body`; mídia de impressão remove o layout da aplicação em vez de apenas torná-lo invisível; página branca com dimensões A4 e margens próprias; slot explícito para o logo profissional com preservação de proporção. Não foram alterados texto clínico, esquema de assinatura ou registros de pacientes.

**Reteste final aprovado nos dois contextos**, em `/tmp/corvia-round-manual-print-final-20260911/report.json`: uma página A4 por PDF, com identificação institucional, profissional/CRM, paciente e item na mesma página; logos não nulos e contidos; sem cortes ou páginas vazias; contraste mínimo do cabeçalho de **12,203:1**; zero erros JavaScript. `window.print` foi interceptado e contado (uma chamada), enquanto o PDF A4 foi renderizado efetivamente pelo Chrome. Não equivale a imprimir em equipamento físico ou testar um celular físico.

Os quatro casos negativos (operadora ausente e falha503 × duas larguras) passaram antes do ajuste de portal: alerta, folha ausente e nenhuma chamada de impressão. Não foram repetidos após a correção visual; o reteste cobriu somente os dois casos válidos que tinham falhado. Runner: `frontend/scripts/atelier-round-manual-print-qa.mjs`.

### Fechamento desta rodada local

- TypeScript `tsc -b`: aprovado após a inclusão do portal e da identificação institucional no frontend.
- Build Vite/PWA: aprovado em **14,59 s** após as últimas alterações de produto, posterior ao build de 15,11 s da fatia anterior. Saída registrada nesta tarefa, sessão local `17133`, código0. Aviso preexistente de chunks acima de500 kB continua presente; esta rodada não certifica desempenho global.
- `git diff --check`: aprovado.
- Nenhuma suíte integral/CI backend repetida, acesso a banco real, emissão/assinatura/envio real, commit, push ou deploy nesta rodada.

A matriz de 78 rotas e 312 observações iniciais continua sendo **cobertura local de renderização/estados**, complementada pelos fluxos focais documentados, não 312 testes completos ponta a ponta. Para concluir gravação/leitura, permissões reais, entrega de mensagens/documentos, preços efetivamente publicados e assinatura criptográfica, permanece necessária uma sessão autorizada de homologação com dados fictícios. A sessão de navegador disponível foi encontrada na tela de login; não foram solicitadas senhas nem usados dados dos pacientes fotografados. Zoom nativo ampliado e leitor de tela também não foram certificados. Não há afirmação de “nenhum defeito em todo o sistema” nem de publicação destas correções.

## Refinamento aprovado — RCE com empresa abaixo do logo

Pedido subsequente de 11/09: manter os demais documentos e mover somente a identificação da operadora na Receita de Controle Especial. O estado mais recente **substitui a faixa transversal da RCE descrita acima**: razão social, CNPJ e endereço ficam diretamente abaixo do logo CorVIA, contidos na coluna esquerda de60 mm. As marcas mantêm centros verticais alinhados; a altura do quadro considera a coluna institucional inteira, o símbolo e os dados profissionais. Receita comum, atestados, laudos, cabeçalho HTML e helper institucional não foram alterados nesse refinamento.

Somente `receita_controle_especial.py` e o teste de branding foram modificados nessa fatia. **3 testes focais da RCE aprovados em5,029 s**, cobrindo documentos curtos/longos com três proporções do símbolo; coluna jurídica abaixo do logo e sem faixa transversal; C5, duas vias, conteúdo, margens e reserva para assinatura; bloqueio de cabeçalho excessivo. Não se repetiram os oito testes de todos os documentos por uma alteração restrita à RCE.

Prévia final curta: `/tmp/corvia-rce-left-column-demo/receita-rce-curto-DEMONSTRATIVO.pdf`, duas páginas, uma por via. As duas páginas foram renderizadas e inspecionadas; relatório de geometria em `/tmp/corvia-rce-left-column-demo/report.json`. Paciente/profissional/símbolo permanecem demonstrativos, sem validade clínica; a operadora usa os dados canônicos. Nada foi emitido, assinado ou publicado em produção.

## Continuação — modelos e finalização dos documentos do Round

Quatro cenários novos, não repetição da matriz de rotas: catálogo/geração com falha503 em1366×900/claro; troca de modelo durante geração em390×844/escuro; PDF/e-mail indisponíveis em1366/claro; fechamento durante preparação do PDF em390/escuro. A execução anterior reproduziu catálogo preso em carregamento após erro, campos sem rótulos associados, resultado atrasado do modelo A aparecendo depois da seleção de B e tentativa de download depois de fechar o finalizador.

Correções restritas a `PatientDocumentos.tsx` e `FinalizarDocumentoGerado.tsx`: erro acessível e recarregamento explícito do catálogo por GET; labels persistentes associados; controle da sequência e do contexto de paciente/modelo/documento; nenhuma repetição automática de POST. Erros de PDF/e-mail permanecem explícitos, sem falsa confirmação de envio. Fechar/trocar o contexto descarta somente os efeitos tardios na interface: **não desfaz operação já aceita pelo servidor**.

**Quatro cenários / sete checks funcionais aprovados**, sem `pageerror` e sem download depois do fechamento. Os campos de entrada permanecem após erro; navegação por Tab e associação de labels foram verificadas nos cenários indicados. Evidência: `/tmp/corvia-document-finalization-final-20260911/report.json`. Runner reutilizável: `frontend/scripts/atelier-document-finalization-qa.mjs`, com filtro de cenário para reteste focal.

A inspeção mobile identificou que dois labels novos herdavam ciano claro sobre o cartão perolado: contraste1,667:1. Ajuste local para o token de texto Atelier elevou o contraste a12,710:1. Somente os labels afetados foram retestados em `/tmp/corvia-document-labels-final-20260911/report.json`; não se repetiu o conjunto funcional por essa mudança de cor.

As APIs foram substituídas por fixtures, os bytes do PDF eram inertes e downloads foram interceptados. Isso valida o comportamento da interface sob os estados descritos, **não emissão, assinatura, envio ou persistência reais**. Os títulos legados e o estado vazio da Timeline identificados na mesma captura motivaram uma medição visual adicional, registrada quando concluída.

### Histórico do Round — isolamento entre seleções e falha de leitura

Na leitura de `PatientTimeline.tsx`, a raiz encontrou GET sem tratamento de rejeição e sem invalidação ao trocar `patientId`. A implementação passou a associar o estado ao paciente solicitado, remover os eventos anteriores enquanto carrega, descartar respostas de efeitos encerrados e apresentar alerta com repetição explícita por GET. Não há POST, alteração de eventos nem consulta ao histórico de pessoa real.

**3 testes focais React aprovados em0,712 s**, em `frontend/scripts/check-patient-timeline-isolation.test.mjs`: falha503 com recuperação única e sem confundir indisponibilidade com histórico vazio; troca de pacientes com descarte de resposta atrasada de sucesso e de erro; desmontagem com rejeição pendente tratada. O componente real é transpilado e montado com React Test Renderer, substituindo somente o cliente API. A evidência é de isolamento da interface; não demonstra um incidente em produção nem substitui testes de autorização do endpoint.

### Round — contraste conjunto dos cartões

A inspeção da captura mobile confirmou que a herança de texto claro afetava outros textos além dos quatro títulos/vazios inicialmente medidos. A verificação foi consolidada em **vazio/populado × claro/escuro,390 px**, incluindo os textos alcançáveis por rolagem, valores de campo, placeholders e controles ativos dos cartões de `#pc-round-editor`.

| Estado | Amostras ativas | Falhas anteriores | Falhas finais |
|---|---:|---:|---:|
| Vazio, claro | 60 | 0 | 0 |
| Vazio, escuro | 60 | 41 | 0 |
| Populado, claro | 77 | 0 | 0 |
| Populado, escuro | 77 | 50 | 0 |

Menor contraste final4,790:1. Os avisos do assistente ficaram em5,728:1; estados vazios5,870:1; link “Criar um modelo”5,312:1, também sublinhado. Em cada contexto havia um botão realmente desabilitado, registrado separadamente como isento e não contado entre os controles ativos aprovados. Cores e fundos do claro permaneceram exatamente iguais ao baseline.

`patient-round-text.css` limita as correções ao tema escuro, Atelier e cartões do editor. A marcação auxiliar evita o fragmento `-card`, que acionava regras legadas de fundo em um estado intermediário já corrigido. Alertas/feedback semântico não foram convertidos em texto neutro; seus estados transitórios não foram acionados por este teste e não são certificados por ele. Folha de impressão em portal, PDFs e lógica clínica ficam fora dos seletores.

Evidência conjunta final: `/tmp/corvia-round-all-text-final-20260911/report.json`; imagens `{empty,populated}-390-{light,dark}.png`. São amostras visuais, não funcionalidades distintas. A captura populada revelou ainda uma linha do histórico de prescrição sem quebra horizontal; sua correção geométrica e seu reteste são registrados separadamente quando concluídos.

**Geometria do histórico corrigida:** `PatientPrescricao.tsx` passou a conter o nome longo e agrupar as duas ações com quebra, espaçamento e alvos mínimos de44 px. Nenhum evento, caminho de impressão ou portal foi alterado nessa fatia. Reteste apenas geométrico com conteúdo DEMO longo: em390/escuro, ações empilhadas de252 px, alturas63,19/44 px; em1366/claro, ações lado a lado de306,22×44 px. Documento limitado exatamente à largura do viewport em ambos. **Dois contextos aprovados**, sem acionar impressão, assinatura ou envio. Evidência `/tmp/corvia-round-history-geometry-final-20260911/report.json`; a raiz também inspecionou a captura mobile corrigida. Não se repetiram os testes funcionais ou de contraste por essa alteração de composição.

## Pesquisa — ofertas reais de medicamentos

A inspeção de providers, catálogo, contrato do receituário e fontes primárias foi consolidada em `docs/pricing-architecture.md`, seção datada de11/09/2026. O arquivo distingue o estado atual local dos registros históricos de agosto e corrige a afirmação antiga de que a dataclass `PriceObservation` já seria uma tabela persistida.

Conclusão: não há feed ativo de ofertas de farmácia no código inspecionado. O snapshot K@iros é PF/PMC por alíquota, BPS é compra institucional, CMED é teto regulatório. Ofertas licenciadas por apresentação/EAN, região, data e condições constituem o caminho proposto para preço de varejo atualizado. Comparadores, inteligência de mercado e notas fiscais foram avaliados separadamente; acesso de saída, licença, cobertura e SLA precisam ser comprovados antes da integração. Nenhum novo provedor, contrato, cadastro, scraping ou atualização automática foi ativado nesta pesquisa.

## Cadastro profissional — conta administrativa própria

Pedido com foto da rota `/admin/usuarios/1/gerenciar`: erro genérico ao salvar. O código reproduz duas incompatibilidades: `AtualizarUsuario` rejeita `role="admin"` com422, embora o GET de gestão possa retornar essa conta; o handler administrativo também bloqueia editar a própria conta ou outro administrador com409. Além disso, `api.ts` ignorava a lista de validações FastAPI `detail: [{loc, msg}]`, exibindo somente o fallback. Não foi consultado o cadastro do usuário1 em produção; a reprodução usou a conta fictícia99001.

`AdminGerenciarUsuario.tsx` agora usa **PATCH `/auth/me`** para dados profissionais da própria conta administrativa. Confere o titular por GET fresco, preserva endereço residencial/profissional, telefone e preferência documental não exibidos, impede envio duplicado e mantém o rascunho após falha. E-mail, CPF/data já registrados, perfil, ativação e tipo de acesso não são enviados e ficam bloqueados nessa tela. Outro administrador permanece somente leitura; usuários comuns continuam no endpoint administrativo anterior. O Instagram é omitido nesse formulário e preservado pela semântica específica do novo campo no backend.

O parser compartilhado passa a reconhecer validações por campo: usa apenas nomes de campos mapeados e mensagens explicitamente permitidas. Não imprime `input`, `ctx`, chaves arbitrárias ou valores pessoais que um validador possa embutir em `msg`; respostas estruturadas anteriores e status HTTP são preservados. O mapa inclui o Instagram.

Evidência focal:

- `frontend/scripts/check-admin-profile-update.test.mjs`: **14 testes aprovados**, cerca de0,33 s, incluindo função real de salvar, endpoint/verbo, preservação de dados/rascunho, envio duplicado, proteção de outro administrador e respostas401/403/409/422/500.
- `backend/tests/test_admin_profile_update_no_db.py`: **5 testes aprovados**, cerca de0,095 s, com schemas/handlers reais compilados por AST; sem aplicação, banco ou conftest. Os guards administrativos não foram alterados. Objetos e unidade de persistência são fictícios; tarefas de e-mail são registradas, nunca executadas.
- Navegador1366/390: validação422 legível, rascunho mantido, tentativa seguinte por PATCH `/auth/me`, releitura da fixture, controles de governança bloqueados e outro administrador somente leitura. **Zero overflow horizontal e zero pageerror.** Relatório `/tmp/corvia-admin-profile-qa/report.json`, capturas `self-admin-saved-{1366,390}.png`. A raiz inspecionou a captura mobile.

As provas são locais e isoladas. Não houve gravação na conta do usuário, alteração de permissões reais, envio de notificação, CI completo ou deploy.

## Histórico superado — identificador social e foto explícita

**Esta função foi cancelada e removida na retomada solicitada em11/09.** O texto
e as evidências deste bloco registram apenas o estado anterior à decisão.
Os testes específicos abaixo foram substituídos pelos contratos de perfil/foto
manual descritos ao final; os arquivos removidos têm cópia recuperável local.

Minha Conta passa a oferecer **Instagram pessoal ou profissional (opcional)**, aceitando identificador, `@usuario` ou URL de perfil do domínio Instagram. O normalizador puro compartilhado pelo cadastro e pela edição rejeita URL externa, credenciais/porta, caminho de publicação, caracteres inválidos e segmentos `.`/`..`; remove parâmetros de compartilhamento e não consulta a rede. O campo existente `instagram_handle` é reutilizado, sem migração.

No PATCH `/auth/me`, omitir o campo mantém seu valor; `null`/vazio explícito remove somente o identificador, preservando as fotos existentes. O link abre apenas o perfil salvo e validado. Durante o salvamento o campo fica desabilitado e a reconciliação é condicional ao snapshot enviado, evitando apagar uma edição mais recente na resposta. Uma revisão independente identificou essa corrida antes da liberação; o reteste foi somente do caso afetado.

A importação antiga de foto usava endpoint não documentado e era agendada silenciosamente no cadastro. Esse agendamento foi removido; serviço legado e imagens já armazenadas não foram apagados. Não foi ativado OAuth, scraping ou chamada a Meta. O cadastro e Minha Conta agora descrevem honestamente a ausência de importação automática. O upload explícito existente `/auth/me/foto` permanece, com botão acionável por teclado; nome de usuário não é prova de titularidade nem autorização para importar a foto.

A documentação oficial consultada descreve APIs de Instagram para contas profissionais Business/Creator e tokens/autorização; não comprova importação por simples `@` de conta pessoal. A configuração por Instagram Login não exige Facebook Page, diferentemente do fluxo por Facebook Login. [Workspace oficial Meta](https://www.postman.com/meta/instagram/overview), [Instagram Login](https://www.postman.com/meta/instagram/folder/6raa77c/instagram-api-with-instagram-login), [limitações de Facebook Login](https://www.postman.com/meta/instagram/folder/u4g5a2a/instagram-api-with-facebook-login). Integração oficial de foto continua pendente de configuração/autorização aplicáveis; não há botão de conexão fictício.

Evidência executada nesta fatia:

- `backend/tests/test_instagram_profile_edit_no_db.py`: **10 casos puros aprovados em0,174 s**, usando normalizador e schemas/handler reais via AST, com persistência e notificações substituídas. Após acrescentar o bloqueio de segmentos de caminho, somente o teste de rejeição foi repetido: **1 aprovado em0,001 s**. O teste legado de cadastro foi atualizado para não esperar scraping; não foi executada sua suíte com banco.
- `frontend/scripts/atelier-instagram-profile-qa.mjs`: **5 cenários ×1366/claro e390/escuro aprovados**: salvar URL e recarregar fixture; limpar campo; validação422 mantém input; upload via teclado/busy/503 conserva foto e rascunho; upload bem-sucedido. Zero pageerror, overflow horizontal ou requisição à Meta. Todas as APIs do app estavam interceptadas.
- Resposta atrasada,390/escuro: campo bloqueado durante PATCH, tentativa de digitação não altera o valor enviado; erro422 tardio preserva rascunho e libera edição. Evidência `/tmp/corvia-instagram-save-delay/report.json`.

A inspeção visual motivou quebra própria e alvo44 px para o link salvo, além de correção de contraste dos dois novos textos de ajuda no tema escuro. O override é restrito aos IDs desses textos em `corvia-atelier-content.css`; não altera os demais cartões. O reteste visual final é registrado ao ser concluído.

**Visual final aprovado** em1366/claro e390/escuro: ajuda com contraste6,87:1 e12,71:1, respectivamente; link de44 px e intervalo de8 px; sem overflow ou pageerror. Relatório `/tmp/corvia-instagram-profile-visual-final/report.json`, capturas `instagram-{1366-light,390-dark}.png`; funcional anterior em `/tmp/corvia-instagram-profile-qa/report.json`. Foram repetidas apenas as medidas e capturas afetadas pelo acabamento, não os fluxos já aprovados.

## Fechamento técnico do complemento — 11/09/2026

- `tsc -b`: **aprovado**, sessão local18710/código0, após congelamento das alterações de cadastro, Instagram, documentos e histórico.
- Build Vite/PWA: **aprovado em13,69 s**, sessão local67839/código0;2.651 módulos transformados e service worker gerado. O aviso preexistente de chunks acima de500 kB permanece; não é validação de desempenho global.
- Nenhuma suíte integral de backend/CI foi repetida. As falhas encontradas foram retestadas de forma focal; os resultados e limites de cada camada estão acima.
- Não houve commit, push, deploy, edição de cadastro real, emissão/assinatura, envio de e-mail real ou coleta de foto da Meta.

**Pendências após a retomada:** contratação futura de outro fornecedor de preços; homologação autenticada dos fluxos ponta a ponta, incluindo autorização, gravação/leitura, assinatura, entrega e serviços externos. O PDF K@iros foi posteriormente localizado no caminho informado pelo responsável; a extração e a ampliação estão documentadas ao final. A integração social foi cancelada, não está pendente. A matriz de renderização e os focais locais não certificam todas as funções de produção como perfeitas.

## Retomada — remoção da integração social e foto manual

Foram retirados os campos, links, textos e tipos de Minha Conta, cadastro e ficha
administrativa; entradas/respostas de API; normalizador e serviço de coleta;
e os mapeamentos ORM dos dois campos descontinuados. **Zero referências
operacionais em `frontend/src` e `backend/app`**, verificado por busca e teste.
A migração histórica foi preservada: não houve DROP de colunas, consulta/mutação
de banco nem exclusão de fotos existentes. As antigas colunas físicas ficam
inativas e não são expostas ou escritas pelo código. Referências negativas nos
testes de remoção e registros históricos não são integração ativa.

Excluídos os dois serviços específicos, os dois testes da integração e seu
runner de navegador; cópia recuperável em `/tmp/corvia-retired-social-aP8Qnf`.
Os substitutos são `backend/tests/test_profile_photo_contract_no_db.py` e
`frontend/scripts/atelier-profile-photo-qa.mjs`. A foto manual e a correção de
salvamento profissional permanecem, com validação de upload e mensagens seguras.

**26 testes focais aprovados:**6 de perfil/foto/ausência,5 de dados profissionais
administrativos,14 Node de salvamento/parser e1 contrato de cadastro executado
diretamente. Nenhuma suíte integral/conftest/banco. Navegador1366/claro e390/escuro:
upload acionado por teclado,503 preservando foto/rascunho,200,422 e resposta
atrasada preservando edição, salvar e reler fixture. Dois cenários com cinco
fluxos cada, sem `issues`, `pageErrors` ou overflow. Relatório
`/tmp/corvia-profile-photo-qa/report.json`; navegador encerrado. São contratos
reais de interface com APIs isoladas, não persistência em servidor real.

## Retomada — Agenda, exclusão e foco do modal

Uma lacuna anterior foi exercitada: cancelamento da confirmação nativa,DELETE204,
DELETE503 e204 seguido de falha na releitura, usando compromissos fictícios.
Foram corrigidos o erro oculto atrás do modal e o retorno de foco ao compromisso
após Escape. O alerta ficou dentro das ações do diálogo, sem anúncio duplicado,
sem ser encoberto pelo rodapé; contraste6,595:1 e hit-test em três pontos.
Nenhuma regra de exclusão/endpoint/sincronização foi modificada.

Três cenários baseline aprovados (204 desktop/mobile e204 com releitura503) não
foram repetidos. O cenário503 mobile foi repetido após correção: valores e item
preservados, confirmação cancelada sem DELETE, nenhum retry automático,Escape
retorna ao acionador. Contrato estático de ID/soft-delete aprovado isoladamente.
Runner `frontend/scripts/atelier-agenda-delete-qa.mjs`; baseline
`/tmp/corvia-agenda-delete-before-20260911/report.json` e resultado final
`/tmp/corvia-agenda-delete-release-20260911/report.json`. Browser encerrado.

## Retomada — prontuário e isolamento de contexto

Reprodução focal com o componente React real e APIs fictícias confirmou:
histórico atrasado deA aparecia sobB;GET503 era exibido como histórico vazio;
salvamento deA podia preencher o editor deB e iniciar a etapa de finalização
após trocar de paciente. A correção associa respostas à seleção/contexto do
paciente e versão do editor, incluindo navegação por URL, troca rápida e saída.
Nenhum registro real foi lido ou alterado.

O histórico ganhou estado de carregamento/erro/repetição porGET; artefatos não
atravessam seleção de atendimento; envios simultâneos são bloqueados por trava
síncrona e campos ficam desabilitados durante processamento. Salvar/finalizar
mantém o ID do rascunho persistido na fixture, evitando criar outro registro
ao repetir a finalização que falhou. Uma operação já aceita no servidor **não é
desfeita** por mudar de paciente: apenas as etapas seguintes/efeitos de interface
obsoletos são descartados.

A revisão independente identificou três regressões durante a correção, todas
ajustadas antes do fechamento: releitura completa após salvar durante carregamento;
clicar novamente em Continuar preserva documentos/rascunho; iniciar pela fila
no paciente atual atualiza o histórico. `check-prontuario-context-isolation.test.mjs`
contém nove casos. Seis passaram na rodada ampliada e três na rodada focal final
(falha de instrumento por `Error` de outro contextoVM foi corrigida no harness).
Os nove casos são cenários distintos, não nove validações de banco.

O agrupamento de campos conserva grid e labels; a inspeção nos dois temas
encontrou seis labels de sinais vitais com fundo legado cinza e contraste3,226:1.
Foi removido somente esse fundo no escopo de Prontuário/Atelier, preservando
superfície perolada e texto. A seleção Tipo recebeu nome acessível explícito.
Validação visual posterior e fechamento de tipos/build são registrados abaixo.

### Fechamento visual focal da retomada

- **Prontuário:** quatro contextos aprovados,1440×900 e390×844, claro/escuro.
  Quarenta e oito medições de labels, todas16px e contraste mínimo12,710:1;
  grid preservado, controles alcançáveis, sem overflow horizontal ou erroJS.
  Texto longo fictício foi preenchido sem salvar. Relatório
  `/tmp/corvia-prontuario-context-visual-final-20260911/report.json`; capturas
  desktop claro e celular escuro inspecionadas. APIs interceptadas, não banco.
- **Minha Conta:**67 ajudas/rótulos e marcador Sem logo,1366/390 em ambos os
  temas. Notas de12px e2,05:1 e ajudas com2,67:1 foram corrigidas com regras
  restritas à página. Textos medidos com mínimo14px e4,99:1; notas agora5,87:1.
  Sem overflow, erroJS ou corte horizontal nos textos medidos. Relatórios
  `/tmp/corvia-profile-legibility-after/report.json` e
  `/tmp/corvia-profile-legibility-logo-after/report.json`. Nenhum funcional repetido.
- **Modal de ajuste da Agenda:**quatro contextos390/1366, claro/escuro,
 16 textos/valores por contexto com mínimo5,312:1 e nove controles≥44×44px.
  Labels escuros corrigidos de1,667 para12,710:1; explicação de2,468 para5,419:1;
  legenda sobre cabeçalho grafite de2,297 para12,544:1. Largura do Fechar40→44px.
  Sem extravasamento horizontal; `text-fill-color` considerado. Relatório
  `/tmp/corvia-agenda-adjust-final-20260911/report.json`. Somente cores e alvo
  de toque; sem alteração do fluxo ou DELETE/PUT/PATCH nesta rodada visual.

Todos os browsers focais foram encerrados. Essas medidas não constituem uma
certificação WCAG geral nem comprovam integração com os serviços externos.

### Tipos e build após remoção social e correções de contexto

`tsc -b` aprovado, sessão2530/código0. Build Vite/PWA aprovado, sessão1427/código0,
2.652 módulos,15,76s e service worker gerado. Executados uma vez após congelar
os fontes desta retomada, sem suíte integral de backend/CI. Aviso preexistente
de chunks>500kB permanece; desempenho global não foi certificado.

### Fonte K@iros localizada com o caminho fornecido pelo usuário

A pendência de localização foi resolvida: leitura SSH de
`/opt/meucardio/medicamentos/kairos-453-2026-08-fontes/` confirmou revista editorial,
suplemento de preços e planilha. Nenhum arquivo remoto foi alterado.
O suplemento `08-ago-2026-suplemento-precos-kairos-453.pdf` tem80páginas,
edição453/agosto2026 eSHA256
`32e4dff5205f7387040900df9820a65b78825e12028db698aa11c482297bc142`.
Suplemento e planilha foram copiados para `/tmp/corvia-kairos-source-kloEeP/`
para inspeção. A ampliação do snapshot depende da validação de colunas,
apresentações, preços e correspondência ao catálogo; não foi declarada completa
apenas por localizar os originais. A contratação de outro fornecedor permanece pendente.

## Próxima prioridade solicitada — e-mails transacionais de acesso

Após concluir o trabalho em andamento, investigar e corrigir o relato de ausência
de e-mails de primeiro acesso, convite e recuperação/troca de senha para novos
usuários, incluindo convidados e investidores. Pedido adicionado pelo usuário
nesta retomada. Verificar elegibilidade por perfil, disparo, execução assíncrona,
resposta do provedor e evidência de entrega sem confundir aceite com recebimento.
Não enviar convites/redefinições inesperados a usuários reais durante os testes.
Estado: **investigação iniciada após concluir a ampliação local K@iros; evidências e correções abaixo**.

## Fila solicitada — Gupta MICA na avaliação pré-operatória

No segundo item da avaliação cardiológica pré-operatória, adicionar a opção
solicitada **Outras (Baixo Risco)** ao tipo de procedimento do Gupta MICA.
Antes da implementação, conferir a publicação e as categorias/coeficientes do
modelo validado e documentar o enquadramento adequado; não criar coeficiente
ou classificar automaticamente um procedimento não contemplado como baixo risco.
Verificar também a clareza da seleção e das limitações na interface.
Estado inicial: registrado na fila. **Implementado nesta retomada como opção
clínica sem estimativa numérica MICA**, após conferência da fonte primária;
detalhamento e evidências ao final deste registro.

## K@iros — menor PMC solicitado pelo responsável

A busca, a escolha de apresentação e o resumo de Prescrever agora mostram o
menor PMC publicado, conservando mínimo/máximo, edição, competência e página
como dados de origem. Nenhuma UF é presumida; o texto deixa claro que a
referência não é uma oferta de farmácia. PF não substitui preço ao consumidor.

Três contratos Node novos passaram: mínimo versus máximo/PF/rótulo antigo;
ausência e comportamento CMED preservados; seleção conserva apresentação e
faixa original, sem alterar outro item ou introduzir preço CMED/UF fictícios.
Runner `frontend/scripts/check-kairos-minimum-price.test.mjs`.

Oito verificações de navegador passaram: escolha no catálogo e sugestão de
apresentação exata, desktop/celular e claro/escuro, valores do item e da soma,
identificação da fonte e legibilidade do resumo. Relatório
`/tmp/corvia-kairos-minimum-ui-20260911/report.json`; browser encerrado,
APIs interceptadas e nenhuma receita/paciente real criado.

O provider ganhou validação monetária/estrutural e índice privado mantendo o
matcher estrito. Vinte e sete testes isolados passaram (14 novos e13 históricos
com fixture original explícita); nenhum conftest/DB/CI. Benchmark sintético de
6.000 registros×176 metadados:12,9133s linear versus0,4868s incluindo validação,
índice e matching; mesmas6.462 correspondências e ordem. Não é medida de carga
de produção. Sem cache de arquivo: cada carga lê e valida o snapshot solicitado.

### Ampliação do snapshot incorporada ao candidato local

`medicamentos/kairos-453-2026-08.json` passou a conter 6.320 apresentações
em 3.063 registros/3.025 pares marca-laboratório, com 46.180 preços literais.
Há 5.360 apresentações com PMC e 960 somente com PF. SHA-256 final:
`ff070fdf46b257253d9e618de56bfb63f3e2b33333bab332e734537d05ec8363`.
O arquivo gerado foi promovido somente no worktree; o remoto não foi alterado.

As 6.371 apresentações extraídas se reconciliam como 6.320 selecionadas,
14 segregadas por identidade ambígua e 37 ocorrências duplicadas não escolhidas.
O preparador preserva literalmente as 52 apresentações anteriores; origem e
curadoria não fingem que as substâncias históricas foram transcritas do PDF.
O resumo `medicamentos/kairos-453-2026-08-curation-audit.json` guarda 47 decisões:
14 quarentenas e 33 grupos duplicados, incluindo vetores originais e coordenadas.

No catálogo de metadados local revisado, a cobertura passou de 14 entradas/
56 opções (52 apresentações distintas) para 84 entradas/541 opções
(537 apresentações distintas). Não é consulta de Drug.published no banco e
não implica que todas as 6.320 apresentações estejam ligadas a Prescrever.
Não se adicionaram associações aproximadas nem conteúdo clínico inventado.

Verificações específicas de dados: 18 testes novos de preparação passaram;
após revisão independente, um guard adicional exige o hash exato do candidato
V3 e rejeitou a alteração simulada de um preço novo (1 teste focal). O teste
CLI de dry-run/gravação explícita também passou após ajustar a fixture desse
guard. Não se repetiram os outros 18 nem a suíte prévia do provider.

A revisão de integração encontrou 51 referências globais que colidiam entre
apresentações; seis afetavam HEPTRIS/NIMEGON MET em dois Drug locais. As linhas
novas agora usam edição/página/lado/linha, com validação das coordenadas.
Quatro testes focais passaram. Checagem das 46.180 observações reais do arquivo:
6.320 referências distintas, nenhuma colisão e 52 referências antigas mantidas.

TypeScript passou após a mudança do menor PMC. Build Vite/PWA passou em 14,61s,
2.652 módulos e service worker gerado. Aviso preexistente de chunks >500kB
permanece. Não se executou CI backend, pytest com conftest, banco ou deploy.
Essas verificações antecedem as alterações posteriores de e-mail/rotas.

## Investigação seguinte — e-mails de acesso e recuperação

Leitura do contêiner backend ativo e consulta SQL com transação **READ ONLY**,
timeout e saída agregada: provider efetivo Mail360 configurado; SMTP não
configurado. Os hashes de config.py, emails.py, emails_legacy.py e mail360.py
coincidiram com o código local anterior às correções desta etapa. Nenhum
destinatário, corpo, credencial ou token foi exportado; nenhum envio foi feito.

Nos últimos 30 dias, EmailLog registrou 16 primeiros acessos, 18 recuperações
e nove acessos aprovados como sucesso; não havia falha recente nesses tipos.
Isso registra a resposta tratada como sucesso pelo aplicativo, **não comprova
entrega nem leitura**, e não cobre caminhos que não geravam EmailLog.

Defeitos confirmados e em correção focal:

- Reenvio administrativo usava a chave idempotente da aprovação original;
  retornava sucesso sem novo dispatch após o primeiro envio. O serviço agora
  tem `reenvio=False` por padrão e a rota manual passa `True`; preserva a
  deduplicação automática e os bloqueios administrativos. Sete testes puros
  passaram, incluindo destino corrigido, transporte falho e conta inelegível.
- Recuperação de CorVIA Mail e alertas administrativos ainda usavam SMTP
  legado, embora o transporte configurado seja Mail360. Não confundir com
  ausência de tentativas na tabela de logs.
- Links legados `/ativar-conta` não tinham rota frontend correspondente;
  a tela de recuperação também confirmava envio no `finally` após erro.
- HTTP 2xx com envelope de erro ou sem identificador de mensagem podia
  virar sucesso transacional. `_chamar` agora verifica `status.code`, e o
  transporte institucional exige `messageId` não vazio antes de registrar
  aceite. Sete testes puros passaram; requisições HTTP foram substituídas
  integralmente por objetos locais. A tentativa inicial do runner não tinha
  httpx disponível e não executou casos; o runner foi isolado dessa dependência.
  O contrato foi conferido na [documentação oficial de envio Mail360](https://www.zoho.com/mail360/help/api/sending-email-messages.html).

**Investidores e pré-autorização não enviam convite no desenho atual.**
Investidores usam a credencial global de demonstração e recebem instruções
manualmente; pré-autorização concede aprovação no autocadastro posterior,
não é um envio por si só. Não foi criada entrega automática da senha global
nem recuperação individual incompatível com esse perfil.

O exame encontrou ainda reativação pública por token de contas administrativamente
desativadas e reset pessoal inconsistente para investidor. Não há campo que
distinga uma conta aguardando ativação de outra desativada por administração.
A correção deve manter aprovação/reativação administrativa, sem mudar `is_active`
por token público, e preservar o modelo da demonstração. Em verificação focal.

Para comprovar o caso relatado de não recebimento, foi solicitado ao responsável
um destinatário/horário/tipo de envio. Ainda não houve envio controlado nem
acesso à caixa do destinatário, nem prova de entrega pelo provedor.

### Encerramento das correções locais de recuperação e notificações

As correções acima foram concluídas no candidato local, sem publicação:

- Recuperação da caixa CorVIA Mail e avisos administrativos de cadastro/KYC
  agora usam o transporte transacional configurado, com uma sessão própria
  para registrar o envio, sem confirmar ou desfazer a transação do chamador.
  O helper SMTP legado permanece para chamadores não abrangidos pela mudança.
  Quinze testes isolados passaram. Na revisão final, o reset da caixa de
  investidor passou a parar antes de criar token ou enviar; somente esse novo
  caso e a regressão normal foram executados depois: dois testes passaram.
- A ativação pública exige conta já aprovada, ativa e não investidora e nunca
  altera `is_active`. Tokens antigos também revalidam o estado. Recuperação
  pessoal de investidor é bloqueada nos pontos públicos, administrativos e
  jobs pertinentes, preservando a credencial global da demonstração.
  Doze testes isolados passaram, incluindo tokens de uso único e reset normal.
- `/ativar-conta` encaminha para `/redefinir-senha` preservando query e fragmento,
  inclusive com sessão aberta e barra final. A exceção pública está restrita às
  rotas de token; os demais controles de acesso permanecem. A recuperação só
  mostra confirmação após resposta bem-sucedida, mantém o endereço em falhas,
  permite repetição consciente e impede duplo envio simultâneo. Nove casos
  distintos de componentes/rotas reais com API simulada passaram.

A verificação visual posterior encontrou contraste insuficiente no alerta de
falha sobre pérola. A correção CSS é restrita a esse alerta. Nova conferência
aprovada em desktop de 1.366px e celular de 390px, com preferências clara e
escura respectivamente: texto 16px, contraste calculado 7,83:1, controles com
altura mínima de 45px, sem transbordamento horizontal ou erros de página.
Os dois cenários exercitaram erro 503 seguido de nova tentativa e confirmação
202, mantendo o rascunho; todas as APIs foram interceptadas e a rede externa
bloqueada. Evidência: `/tmp/corvia-recovery-visual-20260911/report.json`.

TypeScript passou após as alterações de componentes/rotas. O build Vite/PWA
passou e foi atualizado após a correção final de CSS; permaneceu apenas o aviso
preexistente de chunks grandes. Não houve suíte integral/repetida de backend,
banco de teste conectado à produção, envio real, commit, push ou deploy nesta
etapa. A verificação de contratos e a resposta do provedor não certificam entrega
na caixa postal. O caso de não recebimento ainda depende de identificação do
envio e evidência específica; convite automático de investidor não foi criado.

## Retomada autorizada — Gupta e fechamento do candidato

### Procedimento não contemplado no Gupta MICA

Conferência do artigo original Gupta et al., Circulation 2011;124:381–387,
DOI 10.1161/CIRCULATIONAHA.110.015701: Tabela 1 delimita 21 grupos, Tabela 2
define os coeficientes. Não há coeficiente genérico de outras cirurgias de
baixo risco. Hérnia é referência, não fallback; "Other abdomen" é somente
abdominal. Fonte integral com suplemento:
https://d1xe7tfg0uwul9.cloudfront.net/cbc-portal/wp-content/uploads/2013/08/062013-CIRC2.pdf
e registro https://pubmed.ncbi.nlm.nih.gov/21730309/ .

- O segundo item do formulário agora oferece **Outras (Baixo Risco)**,
  explicitamente como classificação do procedimento pelo profissional, não
  risco global do paciente. Sem categoria correspondente, não chama a API MICA
  e continua os demais métodos aplicáveis. Não há coeficiente ou percentual
  zero fictício nem associação automática a uma cirurgia diferente.
- O documento e a auditoria guardam `gupta_nao_estimado=true`, com nota sem
  percentual e `gupta=null`. Flag contraditória com payload Gupta é rejeitada.
  Continua necessário ao menos um método efetivamente calculado; um dicionário
  vazio não satisfaz esse requisito. As 21 categorias e fórmulas não mudaram.
- Alterações dos dados invalidam a exibição do cálculo/documento anterior;
  respostas tardias não habilitam geração para entradas diferentes. Falha
  parcial não deixa uma avaliação aparentemente concluída. Bloqueios síncronos
  evitam duplo cálculo/geração. Documentos já persistidos não são apagados.

Evidência: oito testes backend isolados aprovados em 0,156s, sete cenários React
distintos aprovados (uma correção de regex do próprio teste repetida isoladamente),
quatro contextos de navegador: 1.440×900 e 390×844, preferências clara e escura.
Aviso com 16px, contraste 9,69:1, seletor ≥44px e sem transbordamento horizontal;
fluxo até geração simulado sem chamadas reais. Relatório:
`/tmp/corvia-preop-unlisted-qa-20260911/report.json`.
TypeScript aprovado; build Vite/PWA 15,33s, 2.652 módulos, 90 itens/2.197,22KiB
no precache. Aviso preexistente de chunks grandes permanece.

### Canal independente na recuperação da caixa Mail

A revisão cruzada encontrou um caso adicional real: `users.email` também pode
ser a própria caixa cujo acesso foi perdido. O endpoint agora usa o helper de
segundo canal cadastrado; mantém o fallback principal somente quando diferente
da caixa bloqueada, com comparação normalizada. Sem canal independente, não
cria token nem envia para a caixa inacessível; resposta pública neutra preservada.
Três testes novos e uma regressão focal do destinatário legado passaram (4/4,
0,057s). Não se repetiram os testes anteriores de transporte/ativação nem se
enviaram mensagens reais.

### Preflight da publicação

Fetch coordenado confirmou base local, main remoto e `/api/version` em
`524cbeb7eb7cb3c9058eabe4a70afc27ce5a4141`, antes do novo commit. Nenhuma outra
tarefa Codex ativa de deploy apareceu na listagem. Conector GitHub autenticado
com permissão admin; main sem proteção/rulesets no momento da consulta. Uma
promoção fast-forward normal do SHA certificado preserva a possibilidade de
reuso da suíte; não usar force-push nem alterar proteções para publicar.

O classificador atual exige backend full para este conjunto de autenticação,
documentos, modelo e preços. Não aplicar exceções históricas de outros PRs.
O dispatcher de main já inicia os cinco gates complementares: não duplicar
dispatch manual. O certificador exige CI mais esses cinco gates no SHA final.
`frontend/node_modules` é symlink local não versionável e será excluído do stage.

Limitações operacionais verificadas: o script atual não reconhece o antigo
`CORVIA_SKIP_RAG_REINDEX`; não assumir que esse flag suprime reindexação. O
backup automático conhecido é operacional no host; seu marker não comprova
criptografia/cópia externa nem cobertura de todos os volumes. Essas condições
não serão descritas como certificadas sem evidência adicional. A publicação
ainda depende do novo commit e dos gates remotos; esta seção não atesta deploy.

### Correções identificadas pelos gates do PR934

O candidato inicial `7201d737` foi enviado ao PR934 e recebeu aprovação nos
gates Visual QA, Approved Reference, Pre-home, Route Coverage e Pixel lock.
O backend completo foi iniciado uma única vez no run `34635195463`; seu
resultado ainda estava pendente ao registrar este adendo.

- O contrato de contraste só enumerava três folhas Atelier; passou a exigir
  exatamente quatro, incluindo deslocamento, na ordem efetivamente aprovada.
  As asserções de contraste, autofill e escopo permanecem intactas. O checker
  falho passou após o ajuste.
- O inventário Deep deixou de capturar um generic TypeScript inline com
  ponto e vírgula. Um tipo nomeado preservou a chamada real de impressão e
  restaurou a contagem de 292 referências, sem baixar limiares do inventário.
- O snapshot Káiros ampliado foi separado do sidecar histórico: preços e
  auditoria operacionais foram movidos intactos para `backend/app/data/pricing/`;
  a prova científica antiga foi restaurada byte a byte. O provider não usa o
  sidecar histórico como fallback. Composição real de 440 sidecars, inventário
  e autorização de 12.549 registros passaram sem banco. Foram aprovados 32
  focais de carregamento, empacotamento, fronteira do corpus e preparação.
  Não houve alteração de manifesto, validação de publicação ou preço para
  acomodar a falha.
- Os contratos frontend ainda não alcançados no CI passaram localmente:
  47 casos de identidade/temas/ficha/marcadores, 30 de frame/navegação,
  ficha real e divisão por rota. Não foram repetidos os casos anteriores
  já aprovados nesse job.
- O orçamento revelou entrada inicial de 314.925 B (limite 307.200 B).
  A primeira hipótese, separar o shell legado, foi refutada pelo build e
  integralmente revertida. A correção final carrega apenas o mapa opcional do
  Apoio sob demanda; estado, notificações, APIs e foco do painel permanecem.
  Build de 13,30 s aprovado: entrada 303.298 B; chunk do mapa 12.366 B incluído
  no precache. Nenhum orçamento ou política de cache foi ampliado.
  Três casos React do carregador passaram (props atuais/reabertura,
  falha/repetição/foco e desmontagem antes da resposta). Oito estados de
  loading/erro com CSS real, nas duas aparências e larguras 1.366/320, passaram:
  texto 16px, botão de repetição inteiro e sem transbordamento horizontal.

Estratégia da continuação: reter somente evidência remota realmente concluída;
validar o delta exato e executar testes focais dos insumos/empacotamento
alterados. O perfil de continuidade deve falhar fechado sem baseline completo
ou com mudança não revisada. Certificado focal não será descrito como nova
execução integral. Corpus/RC2 e frontend conservam seus gates próprios. Isso
não comprova entrega de e-mail nem outras integrações externas ponta a ponta.
