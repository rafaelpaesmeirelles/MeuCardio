# Plano técnico do PR #47

Última atualização: 04/08/2026

Branch: `agent/pr47-apresentacao-conteudo-operacao`

Base inicial: `agent/corrige-rce-historicos-emergencia-docs` — PR #46, SHA certificado `d862886d842f1c4afbbc32cfad4fd41dfcd5f145`.

## Objetivo

Corrigir os fluxos de apresentação e navegação científica, enriquecer Evidências, Exames e Medicamentos, reorganizar Checklists, padronizar os PDFs, automatizar alertas de novas diretrizes com segurança, habilitar o CorvIA Mail por configuração protegida e ajustar módulos operacionais antes de uma única janela de publicação dos PRs #46 e #47.

## Estratégia de integração

O PR #47 é empilhado sobre o PR #46 para que seu diff contenha apenas as mudanças novas. A publicação não será feita por dois deploys independentes:

1. manter os dois PRs em rascunho durante a implementação;
2. certificar o PR #47 sobre o SHA aprovado do PR #46;
3. mesclar o PR #46 em `main`;
4. retargetar/rebasear o PR #47 para `main` sem alterar o conteúdo validado;
5. executar novamente CI, reconciliação do corpus, migrations, smoke HTTP e backup/restauração sobre a composição final;
6. mesclar o PR #47;
7. realizar um único deploy do SHA final da `main`;
8. validar produção e manter rollback para o SHA anterior.

Isso entrega os dois conjuntos de correções na mesma janela de publicação, sem colocar em produção um estado intermediário não certificado.

## 1. Modo Apresentação

### Causa identificada

O cartão do Painel chamado “Modo Apresentação” aponta diretamente para `/biblioteca`. A geração só existe dentro de um documento aberto. Além disso, o gerador atual ignora tabelas e pode produzir apresentação praticamente vazia quando o documento não está dividido em títulos/listas no formato esperado.

### Implementação

- criar uma página própria `/apresentacao` com pesquisa e seleção de documento/fluxograma;
- trocar o cartão do Painel para essa rota;
- permitir pré-visualização do conteúdo selecionado antes de gerar;
- garantir fallback para corpo sem títulos, tabelas e documentos de estrutura incomum;
- nunca gerar PDF sem ao menos capa, conteúdo clínico e procedência;
- incluir a marca Corvia, os dados profissionais do assinante e a logo profissional;
- repetir rodapé/identidade visual nas páginas internas sem reduzir a área útil;
- conservar a anotação do apresentador em página separada e não persistida;
- testar conteúdo com parágrafos, listas, tabelas e Mermaid.

### Critérios de aceite

- o cartão abre o catálogo de apresentações, não a Biblioteca genérica;
- PDF possui conteúdo clínico legível e mais de uma página quando aplicável;
- capa contém logo Corvia, nome, conselho/UF, RQE, local de trabalho e logo profissional quando cadastrada;
- nenhuma página em branco causada pelo parser;
- falha de geração aparece como mensagem legível, sem redirecionamento silencioso.

## 2. Biblioteca científica — Documentos científicos

### Causa identificada

O cartão “Documentos científicos” no catálogo aponta para `/biblioteca`, que já é a página atual; por isso o clique não produz mudança visível.

### Implementação

- transformar a coleção em aba/âncora navegável própria;
- usar rota ou query estável, por exemplo `/biblioteca?colecao=documentos#documentos`;
- ao clicar, rolar e mover foco para a listagem;
- manter tema, paginação e estado na URL;
- adicionar teste de navegação e acessibilidade por teclado.

## 3. Evidências com resumo e documento original

### Estado atual

O modelo guarda apenas recomendação, classe/nível, diretriz e referência textual. Não existe resumo clínico nem URL original estruturada.

### Implementação

- migration para `summary`, `source_url` e `doi` quando aplicável;
- atualizar importador e metadados versionados;
- criar validação de URL segura e domínio HTTP/HTTPS;
- exigir conteúdo mínimo antes da publicação;
- mostrar resumo na lista e no detalhe;
- fornecer botão “Abrir documento original” em nova aba, com `noopener noreferrer`;
- manter link interno para o documento relacionado da Biblioteca;
- registrar fonte e status de revisão.

### Regra editorial

Nenhuma IA ou rotina automática poderá inventar resumos. Registros sem resumo curado ou link verificável permanecem retidos até revisão.

## 4. Exames por tipo e subtipo

### Estado atual

`category` já representa o tipo e `theme` pode representar o subtipo, mas a tela filtra somente por categoria e a busca consulta apenas o nome.

### Implementação

- expor contagens por tipo e subtipo;
- permitir filtros simultâneos `category` e `theme`;
- buscar em nome, tipo, subtipo/tema e tags;
- agrupar visualmente por tipo e subtipo;
- manter os filtros na URL;
- paginar resultados e preservar ordenação alfabética.

## 5. Medicamentos — visualizar ou comparar

### Estado atual

A comparação de até quatro medicamentos, meia-vida e redução média de PAS/PAD já existem, porém o clique apenas alterna seleção e a ação muda implicitamente. Não há tempo de ação estruturado, e os dados CMED não estão integrados à visualização individual/comparativa.

### Implementação

- ao clicar no medicamento, abrir duas ações explícitas: `Visualizar` e `Comparar`;
- `Visualizar`: abrir detalhe individual completo;
- `Comparar`: adicionar à seleção de dois a quatro medicamentos;
- acrescentar `duration_of_action_hours` e nota/fonte por migration;
- integrar nomes comerciais, apresentações, laboratório, PMC e versão CMED;
- calcular “preço médio” somente a partir das apresentações CMED disponíveis, mostrando método, UF e data da lista;
- mostrar potência anti-hipertensiva apenas quando existir dado revisado e fonte;
- manter gráficos de barras para PAS/PAD e meia-vida;
- adicionar gráfico de duração de ação;
- impedir comparação enganosa entre grandezas com escalas/unidades incompatíveis;
- mostrar avisos de heterogeneidade entre ensaios e ausência de dados.

### Conteúdo individual mínimo

- nome genérico e classe;
- mecanismo, indicações, doses, ajustes, contraindicações, interações e monitorização;
- potência anti-hipertensiva, quando aplicável;
- meia-vida e tempo de ação;
- marcas, apresentações e laboratórios;
- preço CMED de referência e média calculada, com UF/data;
- fontes.

## 6. Checklist de Alta por doença/procedimento

### Implementação

- adicionar metadado explícito `scope_type`: `doenca` ou `procedimento`;
- migrar/classificar os modelos existentes sem alterar os itens clínicos;
- separar a tela em “Doenças” e “Procedimentos”;
- adicionar busca por nome, resumo, tema e conteúdo dos itens;
- permitir filtro por tipo;
- manter as aplicações em andamento/finalizadas separadas da busca dos modelos.

## 7. Material para o paciente — cabeçalho e paginação

### Causa identificada

A logo profissional entra no fluxo do corpo, à esquerda, depois da capa. Ela não ocupa um cabeçalho fixo e pode deslocar ou colidir com o conteúdo.

### Implementação

- criar cabeçalho reutilizável semelhante ao dos documentos/receitas;
- logo Corvia e identificação de origem;
- nome, conselho, número/UF, RQE e local profissional;
- logo profissional no canto superior direito;
- reservar área do cabeçalho em todas as páginas;
- repetir cabeçalho/rodapé quando o material tiver várias páginas;
- evitar linhas órfãs, títulos isolados e caixas cortadas;
- testes com e sem logo, logo clara/escura e documento multipágina.

## 8. Alertas automáticos de diretrizes a partir de 10/08/2026

### Regra temporal

A interface e as notificações deverão considerar somente novas publicações ou mudanças cuja data oficial seja igual ou posterior a **10/08/2026**. Registros históricos anteriores permanecem no banco para rastreabilidade, mas não aparecem como novidade nem geram notificação.

### Implementação

- migration para data oficial de publicação, data de descoberta, fonte, fingerprint e estado de processamento;
- comando idempotente de descoberta;
- execução agendada por GitHub Actions/cron operacional;
- consultar somente fontes oficiais e estáveis de sociedades científicas;
- deduplicar por DOI, URL canônica e fingerprint;
- publicar automaticamente apenas o alerta factual de que uma nova diretriz foi identificada;
- nunca alterar automaticamente recomendações, doses ou conteúdo clínico já publicado;
- vincular a diretriz nova aos conteúdos potencialmente afetados e colocar revisão clínica na fila;
- notificar assinantes por canal interno e e-mail quando houver vínculo relevante;
- registrar envio idempotente por usuário/diretriz/canal;
- painel administrativo de falhas, fontes consultadas e itens aguardando revisão.

### Segurança editorial

A automação detecta e comunica a publicação; a incorporação da mudança ao conteúdo clínico continua dependendo de revisão humana.

## 9. CorvIA Mail / Mail360

### Regra de segredo

Client ID, client secret e refresh token nunca entram em Git, PR, issue, teste, artefato ou log. As credenciais fornecidas fora do secret store devem ser consideradas expostas e rotacionadas antes do deploy.

### Implementação

- manter leitura por variáveis de ambiente já existente;
- adicionar diagnóstico administrativo que reporte apenas `configurado`, conectividade e código de erro sanitizado;
- criar teste de troca de token com mock e smoke opcional de produção sem imprimir token;
- documentar instalação das credenciais rotacionadas no `.env`/secret store;
- conferir a assinatura ativa e corrigir a lógica de `status-email` para assinantes já pagos;
- habilitar a criação/login da caixa quando assinatura e LGPD estiverem válidos;
- bloquear ativação com configuração incompleta;
- validar envio, recebimento, listagem, leitura e exclusão com conta de teste antes do go-live.

## 10. Cursos parceiros

- desativar o curso demonstrativo `Corvia Curso` sem apagar histórico de banco;
- remover/desabilitar a rota de semeadura de demonstração em produção;
- quando não houver parceiro real ativo, mostrar exclusivamente `Em breve`;
- impedir checkout do curso demonstrativo;
- manter cursos reais versionados e administráveis.

## 11. Fluxogramas clínicos

### Causa identificada

O documento usa largura máxima de `72ch`, enquanto o SVG força largura mínima de 760 px. Em telas menores, o diagrama fica preso num cartão estreito e corta o lado direito.

### Implementação

- usar layout largo quando o documento contiver Mermaid;
- remover a largura mínima rígida como requisito de visualização padrão;
- ajustar `viewBox`, `preserveAspectRatio` e dimensões responsivas;
- oferecer zoom, tela cheia e rolagem horizontal apenas como fallback;
- ampliar o quadro de conteúdo ao tamanho disponível;
- testar árvores largas, profundas e com rótulos extensos;
- revisar paginação da árvore no PDF de apresentação para evitar corte lateral.

## 12. Round hospitalar — excluir paciente

- adicionar ação `Remover do round` com confirmação explícita;
- implementar exclusão lógica/arquivamento, preservando auditoria e dados relacionados;
- impedir acesso transversal: somente o proprietário remove;
- registrar motivo opcional, horário e usuário;
- permitir listar arquivados e restaurar quando necessário;
- não executar exclusão física em cascata de dados clínicos.

## 13. Telediagnóstico — Em breve

- adicionar feature flag `telediagnostico_enabled`, padrão desligado;
- substituir a tela ativa por página `Em breve`;
- remover ações de upload, checkout e criação de pedido enquanto desligado;
- backend deve recusar novas solicitações com 503 acionável;
- ocultar fila administrativa quando o recurso estiver desativado;
- preservar pedidos históricos e não apagar arquivos/dados existentes.

## 14. Presença online com consentimento

### Privacidade por padrão

A visibilidade nasce desativada. Nenhum assinante aparece para outro até autorizar explicitamente.

### Implementação

- migration para preferência de visibilidade de presença;
- controle em `Minha conta`, alterável a qualquer momento;
- endpoint do próprio usuário para ler/alterar a preferência;
- endpoint de presença para assinantes retorna somente usuários:
  - online na janela operacional;
  - ativos;
  - que autorizaram a exibição;
- resposta mínima: nome, profissão/especialidade e horário aproximado; nunca e-mail;
- remover da tela social a lista de usuários offline;
- respeitar revogação imediatamente;
- manter telemetria administrativa separada e protegida para segurança/operabilidade, sem reutilizá-la como diretório social.

## Migrations previstas

- Evidências: resumo, URL original e DOI;
- Medicamentos: duração de ação e nota/fonte;
- Checklists: doença/procedimento;
- Diretrizes: datas oficiais, descoberta, fonte e fingerprint;
- Notificações de diretriz: controle idempotente por usuário/canal;
- Usuários: consentimento de visibilidade online;
- Round: arquivamento/exclusão lógica e metadados de auditoria.

Todas as migrations deverão ser aditivas, reversíveis e sem remoção destrutiva de coluna ou registro.

## Testes obrigatórios

### Backend

- apresentação com conteúdo estruturado e não estruturado;
- PDF com logos e identidade profissional;
- qualidade mínima de Evidências;
- filtros tipo/subtipo de Exames;
- dados individuais/comparativos de Medicamentos e CMED;
- busca e agrupamento de Checklists;
- cutoff de diretrizes em 10/08/2026, deduplicação e notificação idempotente;
- Mail360 configurado/não configurado e erros sanitizados;
- exclusão lógica no Round com isolamento por proprietário;
- Telediagnóstico bloqueado pela feature flag;
- presença online opt-in e ausência de e-mail na resposta.

### Frontend

- rota própria do Modo Apresentação;
- navegação para Documentos científicos;
- resumo/link original em Evidências;
- filtros de Exames;
- ações Visualizar/Comparar e gráficos;
- Checklist por grupo e busca;
- fluxograma responsivo sem corte;
- páginas Em breve;
- preferência de presença e lista somente de opt-ins online.

### Certificação integral

- migrations e idempotência;
- compilação Python;
- `pytest` integral;
- auditoria de dependências frontend;
- build e bundle/PWA;
- reconciliação de 4.936 registros científicos ou valor maior;
- smoke HTTP autenticado;
- backup e restauração PostgreSQL;
- validação visual dos PDFs;
- nenhum segredo no diff ou nos logs.

## Critérios de saída de rascunho

- todos os itens acima implementados ou explicitamente separados em PR posterior por decisão registrada;
- CI e reconciliação verdes no SHA final;
- nenhuma revisão pendente;
- credenciais Mail360 rotacionadas e instaladas fora do Git;
- plano de rollback aprovado;
- validação conjunta com o PR #46 concluída.
