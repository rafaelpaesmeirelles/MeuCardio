# Referências sem destino público nesta versão

Esta correção de apresentação preserva os bytes científicos e as autorizações existentes. Não publica os documentos retidos, não cria registros científicos nem declara revisão clínica humana.

O auditor identificou 32 ocorrências de links sem destino navegável autorizado: 20 apontavam para slugs ausentes; outras 12 apontavam para dez documentos existentes, porém explicitamente em quarentena. A simples presença de um slug no inventário não comprova disponibilidade pública.

Sete destinos históricos têm correspondência bibliográfica e de entidade inequívoca com cinco doenças e dois estudos aprovados. Seus dez links usam resolução tipada compartilhada pelo Markdown, API, grafo e auditor. O levantamento está em `docs/tct-missing-link-destination-review-20260910.json`.

Os outros 17 destinos abrangem 22 ocorrências. Dez ocorrências usam sete slugs sem equivalente integral aprovado; isso inclui CA-125, cuja ficha de exame tem escopo parcial e não pode substituir a revisão histórica inteira. Doze ocorrências usam dez slugs explicitamente retidos. O registro exato encontra-se em `backend/app/services/clinical_link_availability.json`.

Para esses destinos, a resposta pública preserva o rótulo e acrescenta **(conteúdo indisponível nesta versão)**, sem hyperlink. O parser compartilhado não cria arestas para eles. O auditor registra `unavailable_references`, os motivos, os caminhos de origem e as provas. Essa classificação não representa conexão disponível nem deve ser somada às referências resolvidas.

Cada exceção tem um caminho de prova e seu SHA-256. O auditor primeiro valida o snapshot integral, a partição e a proveniência; depois verifica a prova da exceção, o caminho da fonte e se o destino continua ausente ou retido. Destinos desconhecidos continuam bloqueantes. Se um destino retido for aprovado posteriormente, ou se um destino ausente passar a existir, a disposição fica obsoleta e a auditoria falha até sua reconciliação explícita. A camada pública nunca decide publicar conteúdo por este registro.

Validação local em 10/09/2026: 40 testes e 21 subtestes focais passaram; o auditor reportou zero bloqueios e 22 referências indisponíveis (10 sem equivalente integral; 12 retidas). Foram verificadas também as funções dos quatro manifestos editoriais incrementais e do último manifesto estrito por data presente no workflow, `science-release-20260901.json`, com 727 itens e zero pendências. Não houve novo disparo de CI backend.

O corpus permanece com 12.210 identidades: 12.154 aprovadas e 56 em quarentena. Essas medidas descrevem consistência e apresentação das referências; não certificam integralidade clínica, disponibilidade de todas as relações úteis nem revisão científica humana independente.
