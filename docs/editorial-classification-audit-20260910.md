# Revisão editorial e regressões mobile — 10/09/2026

PR920. Base: `4c58de6fb7cd64bd8767f062d9ef0ee814870cda`.

## Pedido e sequência

A revisão começou depois do deploy bem-sucedido do PR919 (execução34430511881), conforme pedido do responsável. O deploy anterior publicou12.154 itens autorizados, preservou56 itens em quarentena e foi verificado nos módulos realmente instalados, sem sobreposição de código: sete consultas em transação somente leitura, rollback confirmado, contagens consistentes, duas fichas de fibrilação atrial e todos os18 campos de detalhe verificados presentes.

Durante esta revisão o responsável também relatou, com três capturas mobile, corte lateral na tela de escolha e desaparecimento do nome CorVIA no cabeçalho claro. Essas correções integram este PR. A instrução anterior “Sem novo ci backend” continua vigente e está vinculada especificamente a este PR e à sua integração exata, sem certificado de suíte aprovada.

## Cobertura editorial e causas confirmadas

O inventário de metadados cobre12.210 itens nas13 frentes canônicas, reconciliados ao manifesto:12.154 aprovados e56 em quarentena. Isso é um inventário e uma revisão de gênero editorial; não constitui nova revisão médica de todo o conteúdo.

Os3.027 documentos Markdown contêm1.226 estudos,585 protocolos,534 documentos genéricos,389 fluxogramas,143 itens de farmacologia,69 diretrizes,60 calculadoras,14 trilhas,3 consensos,3 revisões e1 módulo. O agrupamento anterior ignorava vários tipos explícitos e inferia a seção por palavras no título. Assim, um estudo podia cair em condutas e uma síntese temática podia virar diretriz por mencionar um consenso.

O importador de resumos de publicações monitoradas também criava todos os documentos como `kind=diretriz`, sem distinguir a natureza da publicação. Esse erro afeta conteúdo gerenciado em execução e exige inventário adicional, além dos arquivos canônicos.

Casos confirmados: EPIDAURUS (DOI10.1038/s41591-026-04629-7) é ensaio randomizado, não diretriz. O documento CorVIA sobre miopatia atrial reúne consensos e estudos e já tem `kind=documento`; a menção a consenso no título não transforma a síntese em consenso formal.

## Critérios da correção

O gênero do objeto editorial é distinto do gênero das fontes citadas. A classificação respeita o tipo explícito e sua proveniência; domínio do periódico, nível da fonte ou uma palavra isolada no título não são prova de diretriz. Documentos neutros permanecem neutros até haver evidência de uma classificação mais específica.

A identidade e a rota são preservadas: um estudo da Biblioteca continua sendo um documento acessível pela Biblioteca; não se transforma artificialmente em registro de ScientificStudy. As contagens e a paginação usam a mesma taxonomia. Consensos devem ser encontráveis na seção de diretrizes e consensos.

Reclassificações de metadados confirmadas estão registradas por identidade, estado anterior, estado corrigido e evidência. O texto clínico, as fontes originais e a autorização científica anterior não serão reescritos para acomodar uma classificação. A revisão não concede publicação aos itens em quarentena.

## Causas das regressões mobile

Uma regra responsiva específica do tema claro ocultava o wordmark no cabeçalho até900px, enquanto o tema escuro o mantinha. Na tela de escolha, larguras intrínsecas do conjunto marca/galáxia/conta e a coluna da grade expandiam o conteúdo além da tela, cortando cartões e texto.

A correção uniformiza a marca entre temas e permite que a grade encolha. Em telas estreitas a busca terá espaço próprio, preservando a identidade e a legibilidade. A verificação precisa medir os retângulos reais dos cartões, textos e marca; apenas verificar a largura do documento não detecta conteúdo cortado por um ancestral.

## Resultado da revisão

A revisão individual de 202 candidatos canônicos encontrou 43 correções confirmadas, 147 classificações a manter e 12 casos ambíguos preservados. Os 63 documentos publicados gerados pelo monitoramento científico foram conferidos por identidade, DOI e metadados bibliográficos primários: 62 exigem correção e um permanece diretriz. O registro contém 106 decisões verificáveis e 105 alterações de gênero editorial, sem mudar arquivos científicos, links, texto, versão, publicação ou quarentena.

Nos 63 documentos dinâmicos, os gêneros resultantes são: 23 estudos, 28 revisões, dois consensos, três posicionamentos, uma diretriz, quatro documentos neutros, um preprint e uma errata. O item vinculado ao DOI `10.1136/bmj-2026-100678` é uma errata da publicação ITACS; sua classificação foi corrigida, mas a correspondência do resumo clínico com a fonte continua exigindo revisão científica própria. Esta auditoria não certifica o conteúdo clínico desses resumos.

O importador deixa de presumir que toda publicação monitorada seja diretriz. Evidências editoriais ficam vinculadas à identidade e ao hash da fonte; objetos sem prova de gênero formal recebem classificação neutra. O reconciliador aplica os metadados confirmados em snapshot próprio, sem reescrever fontes nem reutilizar aprovação científica para conteúdo alterado.

## Validação e publicação

Concluídos: 14 testes locais do registro/importadores sem SQL; validação estática das 43 fontes canônicas e das 63 identidades dinâmicas; testes focais da taxonomia, filtros, paginação, rotas, concorrência das consultas e isolamento do radar; TypeScript integrado aprovado. A primeira bateria real do CLI passou cinco casos em banco QA exclusivo: simulação somente leitura, aplicação apenas de gênero, idempotência e rejeição atômica de evidências/snapshots adulterados. A reexecução reconhece uma classificação já concluída somente com auditoria vinculada exatamente à decisão, hashes, documento e gênero atual, e com a identidade da fonte preservada. A primeira aplicação continua exigindo o snapshot completo e a rechecagem no mesmo commit; a diretriz mantida também recebe comprovante único. A bateria final do CLI passou 11/11 testes em 86,13 segundos, incluindo atualização legítima após conclusão, fonte divergente, vínculo de auditoria incorreto e comprovante idempotente do item mantido.

A simulação do código candidato em produção executou apenas SELECT/SET em transação comprovadamente somente leitura: 63 identidades e snapshots válidos, 62 alterações planejadas, zero alterações realizadas, rollback confirmado e nenhuma tentativa de commit. Isso não equivale a código instalado ou a deploy concluído.

A matriz visual real de 32 combinações mobile e os gates de integração/publicação ainda precisam concluir. Nenhuma suíte completa de backend será repetida e nenhum novo CI backend será executado. Os gates independentes de corpus, frontend, navegação autenticada e publicação permanecem exigidos.
