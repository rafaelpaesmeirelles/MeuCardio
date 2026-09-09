# Passagem para deploy — produção prevalente do CorVIA

## Pedido do usuário e ponto de parada

O usuário determinou: **“Interrompa a produção, salve tudo que foi feito e prepare para outro chat fazer deploy.”** A produção foi encerrada. Não iniciar novos lotes a partir desta passagem. Nenhum merge, importação, promoção editorial ou deploy foi executado por esta frente.

Repositório: `rafaelpaesmeirelles/MeuCardio`.
PR: https://github.com/rafaelpaesmeirelles/MeuCardio/pull/915
Branch: `codex/corvia-prevalentes-progressao-20260909`.
Primeira rodada já salva no commit `4796d8d54e7557e2400737a4d46361ace8543b8b`; a continuação está preservada no patch `handoff/corvia-prevalentes-rodada2.patch.xz`, acrescentado à mesma branch. O patch precisa ser aplicado e commitado antes do deploy; o commit de salvamento do pacote não altera sozinho os catálogos.

## Conteúdo consolidado

- 18 documentos científicos novos e nove documentos existentes corrigidos.
- 12 casos fictícios, seis materiais ao paciente e seis checklists novos.
- Cinco registros estruturados existentes corrigidos: um caso, dois materiais e dois checklists.
- Oito trilhas progressivas, agora com 67 etapas; 105 relações explícitas novas entre as duas rodadas.
- Complementação dos documentos relacionados em 11 doenças na primeira rodada.
- 24 novos recursos da segunda rodada com vínculo de volta ao documento e 14 documentos com links de ida. Nenhum órfão identificado na validação estática.

As revisões científicas e cruzadas foram realizadas por agentes de IA, com transparência nos metadados. Não representam revisão humana nem certificação de completude do corpus histórico.

## Arquivos de referência

- `docs/producao-prevalentes-20260909.md` e `docs/producao-prevalentes-20260909-validacao.json`: primeira rodada.
- `docs/producao-prevalentes-20260909/`: auditorias autorais e revisões da primeira rodada.
- `docs/producao-prevalentes-20260909-rodada2.md`: relatório consolidado da continuação.
- `docs/producao-prevalentes-20260909-rodada2-validacao.json`: contratos e links, sem erros.
- `docs/producao-prevalentes-20260909-rodada2-mapa.json`: mapeamento dos 24 recursos para documentos, doenças e trilhas.
- `docs/producao-prevalentes-20260909-rodada2/`: fontes, pareceres, auditoria de overlays, revisão final de pacientes e grafo.

Os arquivos finais estão nos diretórios canônicos `content/`, `casos-clinicos/`, `checklists/`, `material-paciente/`, `trilhas/` e `doencas/`. Os fragmentos de autoria chamados `*-corrections.json` foram consolidados nos catálogos; não é necessário importá-los separadamente.

## Preservação de trabalho paralelo

A autoria da segunda rodada partiu da main `cb750689b94f7888b18133e68ff8293bff55d742`. O salvamento foi confrontado com a main `1c8454d132bfc6ecedec802c731dbb26b4d1e6da`, sem colisões nos arquivos da entrega. O patch foi construído sobre os arquivos exatos da primeira rodada. A main mais recente não foi incorporada automaticamente à branch; preservá-la durante a integração.

Como outras frentes trabalham no repositório, conferir novamente HEAD, mergeabilidade e alterações concorrentes antes de integrar. Não substituir os catálogos atuais por snapshots antigos. Não restaurar versões de interface, infraestrutura ou corpus que antecedam a release escolhida pelo responsável pelo deploy.

## Validações concluídas

- 431 links internos do conjunto conferidos contra destinos existentes.
- Slugs, frontmatter, JSON, referências, índices de respostas e IDs de checklists válidos.
- Detector de posologia do carregador real executado nos oito materiais novos/corrigidos; nenhum recusado.
- Simulação do overlay de materiais preservou as correções.
- 914 casos, 471 checklists e 446 materiais fora das correções preservados em seus valores.
- Relações e tipos de etapa conferidos; materiais ao paciente não foram inseridos como tipo de etapa não suportado.
- Revisão cruzada e consolidação de correções clínicas registradas nos pareceres.

Catálogos deste lote: 927 casos, 479 checklists, 454 materiais. Esses números são do snapshot entregue, não uma contagem atual do banco de produção.

## Pendência concreta antes da liberação

Na primeira rodada, o CI apresentou 117 testes de scripts aprovados e uma falha no teste histórico de autorização do corpus. O manifesto `editorial-approvals/full-corpus-release-20260907.json` autoriza 11.581 itens, enquanto a base já havia avançado. O arquivo e o teste continuam preservados. **Não considerar a nova produção como aprovação retroativa de todo o corpus; não desativar o teste nem fabricar uma autorização.** O responsável pela release deve tratar a autorização aplicável ao snapshot realmente escolhido, conforme o fluxo existente, e conferir os checks do novo HEAD.

Nenhum registro recebeu `published: true`. Os carregadores não publicam novos registros automaticamente. Portanto, merge e carga de arquivos não bastam para mostrar todo este conteúdo no site: é necessário executar o fluxo editorial de promoção já existente com a autorização pertinente.

## Continuação operacional para o outro chat

1. Ler este documento, o PR e as instruções operacionais atuais do repositório. Em checkout da branch com a primeira rodada, descompactar `handoff/corvia-prevalentes-rodada2.patch.xz` para um arquivo temporário, executar `git apply --check` e depois `git apply --index` no patch; registrar o commit das alterações. O patch inclui este documento e todo o resultado da segunda rodada. Confirmar o SHA que será incorporado e coordenar com qualquer outra release em andamento.
2. Integrar o conteúdo preservando a main e resolver somente conflitos efetivos. Conferir a autorização do corpus e o resultado do CI sem disparar repetidamente suítes longas.
3. Usar o procedimento existente de release/importação para os tipos alterados, incluindo documentos, casos, checklists, materiais, trilhas e relações/correções de doenças. Não criar importação paralela que ignore os contratos dos carregadores.
4. Aplicar a promoção editorial autorizada; reconciliar grafo e índices/busca conforme os mecanismos atuais do CorVIA.
5. Após o deploy, verificar prontidão/versão e amostras das oito trilhas. Conferir documento → recurso → documento, busca dos novos slugs, materiais/PDFs e relações úteis entre tipos. A navegação autenticada e o estado do banco não foram verificados por esta frente.

Limite conhecido: o CorVIA Intelligence pode substituir notas `revisao` dos checklists conforme vínculos confirmados no banco; os itens clínicos e resumos são preservados pelo código auditado. Conferir proveniência final se esse fluxo for executado.

O objetivo desta passagem é concluir a publicação do trabalho já salvo. A produção científica permanece interrompida até nova instrução do usuário.
