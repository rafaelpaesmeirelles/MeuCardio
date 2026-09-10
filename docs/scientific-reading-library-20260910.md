# Leitura científica compartilhada — 10/09/2026

## Achado da auditoria

A biblioteca compartilhada não armazenava traduções integrais. Os botões “Traduzido” em Documento/Estudo apontavam ao corpo editorial ou aos resultados/implicações clínicas. O Intelligence produzia uma síntese original em português via busca web. A tradução integral existente era exclusiva da biblioteca privada de arquivos enviados pelo assinante, cifrada, com orçamento individual. Esses arquivos privados não foram consultados, migrados ou publicados.

## Implementação

A tabela `scientific_publication_assets` guarda a identidade DOI/URL e o estado dos artefatos de cada fonte. O original autorizado é adquirido pelo endpoint oficial Europe PMC, conservado como XML JATS cifrado em volume próprio e acompanhado por hash, licença e autoria. Não se apresenta XML como PDF. Nenhum endereço fornecido por usuário é buscado pelo servidor: host/API fixos, PMCID validado, sem redirecionamentos e limite de tamanho.

O parser exige DOI correspondente no artigo, licença CC BY ou CC0 explícita, corpo completo distinto de abstract, referências e texto de tabelas/legendas. Rejeita entidades XML, codificações não suportadas e fórmulas que não possa preservar. Tradução integral significa texto do artigo, incluindo legendas; figuras gráficas e suplementos permanecem no original e são explicitamente distinguidos na interface.

Cada execução paga traduz um bloco de até 2.000 caracteres, com segmentos identificados e conferência de sequência, números, sinais, comparadores e extensão. Os trechos são cifrados e retomáveis. A versão em português só fica disponível após todos os blocos corresponderem ao hash da fonte. A saída preserva atribuição, licença e indicação de tradução por IA. Essas verificações de software não constituem validação humana da fidelidade clínica de cada tradução.

O resumo editorial CorVIA já existente continua separado do resumo gerado a partir do artigo completo. Os controles de leitura informam disponibilidade real: original armazenado ou fonte externa, resumo em português e tradução integral pronta, na fila ou indisponível. Não há geração paga em requisições de leitura.

API: `GET /api/scientific-reading/{entity_type}/{slug}` e variantes autenticadas `/sources/{source_key}/original` e `/translation`. Tipos: documento, fluxograma, estudo, evidência, diretriz, doença, triagem, medicamento, exame, caso clínico, trilha, emergência, material ao paciente, imagem, checklist, calculadora e descoberta bibliográfica. A publicação do conteúdo é conferida antes de liberar artefatos. Descobertas exigem fonte confiável e DOI, sem tornar público conteúdo clínico ainda não publicado.

A fila cadastra fontes por anti-join persistido, em lotes de 200 novas identidades com `has_more`, até abranger os objetos pertinentes. Inclui descobertas confiáveis antes da antiga análise de IA. O worker prioriza finalizar uma tradução iniciada, em vez de alternar indefinidamente entre todas as fontes.

## Custos e retomada

O centro de custo institucional `editorial` é reutilizado; consultas ao material compartilhado pronto não exigem plano de IA e não consomem a carteira do assinante. O teto não foi elevado. Leitura financeira em produção, em transação somente leitura e rollback, constatou configuração de R$100/mês e nenhum período materializado para `institution:editorial` no mês corrente; nenhuma reserva ou cobrança foi criada pela auditoria.

Chave de operação determinística por fonte/bloco/pedido, reserva antes da chamada e bloqueio para reconciliação em resultados incertos impedem repetição automática de chamadas possivelmente cobradas. Um advisory lock em conexão dedicada protege a execução entre commits. Arquivos são append-only; rollback deixa arquivos órfãos sem referências, sem substituir versões anteriores.

O teto mensal e a elegibilidade das fontes limitam o ritmo da fila. Não se afirma que todo o acervo já esteja traduzido. A quantidade elegível só se confirma após verificar a licença e o texto integral de cada publicação.

## Evidências executadas

- Seis testes locais de identidade, licença, XML, estrutura textual, segmentos de tradução e URL fixa: passaram em 28,82 segundos.
- Três testes locais adicionais de sinais/comparadores, continuidade da fila, disponibilidade honesta, conteúdo não publicado e vínculo da fonte no download: passaram em 20,45 segundos.
- Dois testes adicionais de autenticação HTTP 401 e rejeição de truncamento silencioso na extração privada: passaram em 9,87 segundos. Total: 11 testes focais, sem repetição de suíte completa e sem CI backend.
- Migração real no banco exclusivo de QA: `c0aw20260909 → c1sp20260910`, concluída.
- Acesso gratuito real ao Europe PMC: DOI `10.1002/prca.70052`, PMCID `PMC13449635`, *Proteomic Remodeling in the Failing Left Ventricle Adapting to Dyssynchrony*. Licença CC BY 4.0 confirmada no XML; 99.476 bytes e 44.882 caracteres de texto integral, incluindo corpo e referências. Nenhuma chamada de IA, arquivo persistido ou alteração de produção nesse teste.
- Revisão independente de segurança/custos/integridade do software concluída sem bloqueio restante; não substitui revisão científica de saídas futuras.

Fontes de política consultadas: [CC BY 4.0](https://creativecommons.org/licenses/by/4.0/) e [PMC Open Access Subset](https://pmc.ncbi.nlm.nih.gov/tools/openftlist/). A disponibilidade gratuita de um artigo, por si só, não determina permissão para redistribuição e tradução.
