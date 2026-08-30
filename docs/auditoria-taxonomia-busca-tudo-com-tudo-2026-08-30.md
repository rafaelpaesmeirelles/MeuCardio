# Auditoria de taxonomia, busca e “Tudo com Tudo” — 30/08/2026

## Escopo e regra de segurança

Auditoria somente sobre conteúdo científico versionado e superfícies públicas do
produto. Nenhum dado de paciente foi lido. O lote não autoriza deploy e não
reescreve as categorias editoriais originais: cria uma camada canônica,
reversível e auditável para navegação.

## Inventário confirmado

- 10.905 itens científicos revisados no corpus versionado.
- 2.341 documentos Markdown.
- 3.189 registros de evidência e 1.899 estudos.
- 889 casos, 534 trilhas, 445 checklists, 431 materiais para pacientes, 423
  exames, 281 itens de galeria, 206 medicamentos, 172 doenças, 77 protocolos
  de emergência e 18 fluxos de triagem.
- 1.357 vínculos `doença → documento`; 8 das 172 doenças ainda não têm nenhum
  documento relacionado.
- As 1.357 referências existentes resolvem para slugs válidos. O problema
  principal é cobertura e pertinência, não link quebrado.

## Achados

### 1. “Área clínica” misturava dimensões diferentes

O Guia de Doenças expunha diretamente 52 categorias editoriais. Vinte e seis
delas tinham apenas um verbete. Entre os rótulos havia áreas clínicas,
populações, tratamentos, etapas assistenciais e tipos de evento. Isso produzia
uma lista longa, esparsa e pouco previsível.

A dimensão `area` já representa população/contexto (`geral`, pediatria,
geriatria, cardio-oncologia e gravidez). A nova dimensão `clinical_domain`
representa o domínio cardiovascular. As duas passam a ser independentes.

### 2. O corpus tinha 58 grafias de tema para 30 coleções reais

Foram encontrados 131 itens publicados sob aliases ou grafias técnicas como
`hipertensao`, `sindrome_coronariana_aguda`, `insuficiencia-cardiaca`,
`valvopatia` e `avc_agudo`. A camada de relações conhecia apenas dois aliases.
Com isso, conteúdo válido podia ficar isolado ou aparecer como coleção nova.

O catálogo de aliases passa a reconciliar todas as 58 grafias em 30 temas
canônicos, sem alterar a fonte científica original.

### 3. “Tudo com Tudo” chamava formato de conteúdo de área clínica

Na busca, “Condutas”, “Diretrizes”, “Fluxogramas”, “Estudos”, “Evidências”,
“Exames” e “Galeria” eram apresentados como áreas clínicas. São frentes de
conhecimento. O rótulo e a descrição foram corrigidos para refletir essa
semântica.

### 4. A complementação por tema podia gerar relações falsas

Quando a busca coincidia com um tema, o frontend solicitava até cinco itens de
cada frente usando apenas o tema amplo. Não enviava o assunto específico para
o filtro contextual já existente no backend. Assim, itens recentes da mesma
coleção podiam aparecer sem relação com a pergunta inicial.

A busca agora envia `assunto`, obrigando sobreposição específica de
título/slug/tag antes de completar os resultados. No grafo exibido nas páginas,
a expansão em dois saltos por “mesmo tema” fica desativada por padrão; vínculos
editoriais e estruturados continuam disponíveis.

## Taxonomia aplicada ao Guia de Doenças

Os 52 rótulos internos foram agregados em 16 domínios acionáveis, todos com ao
menos dois verbetes:

| Domínio | Verbetes |
|---|---:|
| Arritmias, eletrofisiologia e dispositivos | 15 |
| Doença coronariana e intervenção | 6 |
| Insuficiência cardíaca, miocárdio e cardiomiopatias | 20 |
| Valvopatias e cardiologia estrutural | 15 |
| Hipertensão, prevenção e risco cardiovascular | 12 |
| Aorta e medicina vascular | 8 |
| Circulação pulmonar e tromboembolismo | 8 |
| Doenças inflamatórias, infecciosas e do pericárdio | 7 |
| Cardiopatias congênitas | 18 |
| Cardiologia pediátrica adquirida | 5 |
| Cardiologia fetal | 13 |
| Cardio-oncologia | 14 |
| Cardiogeriatria e cuidado centrado na pessoa | 8 |
| Emergências cardiovasculares e cuidado crítico | 5 |
| Condições cardiometabólicas e comorbidades | 8 |
| Síndromes e avaliação cardiovascular | 10 |

Os nomes foram comparados com as coleções oficiais de tópicos da
[European Society of Cardiology](https://www.escardio.org/topics/) e do
[American College of Cardiology](https://www.acc.org/clinical-topics). O
agrupamento final, porém, foi calibrado pelo conteúdo real do CorVIA para não
criar filtros vazios.

## Validação executada

- Auditoria reprodutível de todas as referências: zero slugs quebrados.
- Cobertura da nova taxonomia: 172/172 doenças; nenhuma categoria sem mapa.
- Build de produção do frontend: aprovado.
- Compilação dos módulos Python alterados: aprovada.
- Testes completos com PostgreSQL ficam a cargo do CI isolado do PR; a
  execução local sem o serviço de banco foi interrompida por conexão recusada,
  e não por falha de código.

## Próximo lote antes do deploy

1. Revisar as oito doenças sem documentos relacionados.
2. Amostrar relações por domínio e calcular precisão editorial, não apenas
   resolução de slug.
3. Introduzir pontuação explicável por tipo de relação e limiar mínimo.
4. Medir busca por casos sentinela (FA, hipertensão pulmonar, pericardite,
   insuficiência cardíaca, doença coronariana e condições raras).
5. Só então liberar a revisão para merge/deploy.

