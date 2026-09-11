# Verificação visual e contraste — 11/09/2026

Verificação local do frontend real, servido por Vite em `127.0.0.1:4785`. Base d48df1a9 com patches desta correção. Perfil administrador, usuários, busca, evidências e dados de agenda são fixtures sintéticas. Todas as URLs `/api/` foram interceptadas; hosts externos foram bloqueados. Não houve chamada à IA, gravação em banco ou uso de dados de usuários reais.

## Cobertura

- Tema claro em 1366×900 e 390×900: busca por fibrilação atrial, evidências com cards/classes/níveis, administração com formulário inferior, listagem de usuários, IA para exames, Assistente Pessoal, início e catálogo Todas as funções.
- Tema escuro em 1440×900: início e catálogo, como inspeção complementar à geometria de cabeçalho. A geometria em 901/1024/1280/1440 e mobile390 foi validada separadamente em `header/`.
- 18 cenários de página/painel. Zero erro JavaScript e zero overflow horizontal do documento nas capturas finais.
- `final-report.json`: rodada final das páginas. `final-focused-report.json`: substitui apenas início/catálogo após ajuste dos rótulos laterais, e exames/assistente após exigir explicitamente o formulário carregado.
- Capturas `final-evidence-cards-*` e `final-admin-form-*` incluem conteúdo abaixo da dobra do contêiner de rolagem. Uma captura inicial de exames desktop pegou o carregamento: `final-exams-light-1366.png` foi descartada como evidência; usar `final-focused-exams-light-1366.png` ; a evidência definitiva de exames é `final-privacy-exams-light-1366.png` e `final-privacy-exams-light-390.png`.

## Medição

`visual-contrast.mjs` recolhe cores computadas, família de seletores, tamanho, transparência e cores de fundo compostas dos nós de texto e placeholders. Compara a relação de luminância a 4,5:1 para texto normal e 3:1 para texto grande. Registra botões desabilitados separadamente. Inclui conteúdo abaixo da dobra e alguns rótulos de tooltip; não equivale a certificação WCAG de todo o produto.

Gradientes e imagens de fundo não são reduzidos a uma cor por este algoritmo. Por isso as capturas foram examinadas visualmente: essa inspeção detectou fundo escuro de exames mesmo quando a medição teórica da cor de fundo passava. Um único alerta no logo do catálogo claro desktop decorre de ignorar o gradiente branco que cobre o backdrop; a captura `final-focused-catalog-light-1366.png` mostra texto grafite sobre superfície branca legível. Este caso está registrado, não foi apagado do relatório.

No tema claro, as páginas e painéis finais não apresentaram outros alertas de contraste computado. No tema escuro permanecem seis alertas computados dos rótulos legados Hospital/Ensino/Pesquisa da navegação/portas (3,32–4,35:1); esta correção no escuro verificou o posicionamento do miniuniverso, sem declarar auditoria completa de contraste escuro.

## Evidência intermediária

Arquivos `initial-*` são capturas de versões intermediárias desta correção, não uma reprodução certificada da versão de produção. Preservam os defeitos encontrados: botões secundários ~2:1, classe/nível de evidência ~1,2:1 e painéis de exames ainda escuros. Não são capturas finais.

## Limites

Fixtures exercitam apresentação e contraste, sem validar autenticação, persistência, envios, cálculos médicos ou respostas da IA. A agenda está vazia; o drawer mostra seu estado vazio. Não foram repetidas suítes de backend nem iniciado CI por este trabalho de QA.

## Fechamento da faixa de privacidade

`final-privacy-report.json` e as quatro capturas `final-privacy-*` substituem somente exames/assistente após corrigir o gradiente hospitalar herdado na faixa de privacidade. Zero erros JavaScript, zero overflow, zero alertas de contraste computado. A imagem desktop foi aberta e inspecionada: cabeçalho da IA, formulário, área de upload e aviso de privacidade agora têm fundos brancos/cinza neutro e texto escuro legível. A recaptura foi limitada às duas larguras já cobertas.
