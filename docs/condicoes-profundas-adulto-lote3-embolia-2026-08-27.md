# Guia de Doenças — adulto, lote 3: embolia pulmonar aguda

Data da produção: 27/08/2026

Estado editorial: `pendente_revisao`

Publicação automática: bloqueada

## Escopo

O lote adiciona um único verbete adulto para `embolia-pulmonar-aguda`. Não há
duplicata em doenças: os registros existentes cobrem apenas câncer e
gestação. O protocolo `tromboembolismo-pulmonar` pertence à coleção de
emergência e é conexão do mesmo conceito, não duplicata.

O verbete estrutura reconhecimento, probabilidade pré-teste, diagnóstico,
gravidade, falência cardiopulmonar, segurança da anticoagulação, critérios de
alta, seguimento e populações especiais. O assistente não diagnostica, não
seleciona anticoagulante ou dose, não indica reperfusão automaticamente e não
autoriza alta.

## Segurança do assistente

- estado diagnóstico separa TEP confirmado, suspeita atual e ausência de
  suspeita;
- E2, E1, D1 e D2 possuem caminhos distintos, sem converter categoria em
  terapia automática;
- toda categoria C sintomática com escore clínico elevado leva à
  hospitalização, independentemente de VD ou biomarcadores;
- baixa gravidade só produz candidatura à avaliação de alta quando choque,
  falência respiratória, sangramento, contraindicação e barreiras foram
  negados;
- respostas obrigatórias ausentes geram HTTP 422 antes da execução;
- exames e fluxos educacionais do verbete não são rotulados automaticamente
  como sugestões do assessment.

## Relações clínicas diretas

- documentos AHA/ACC 2026 e SBPT 2025;
- material `embolia-pulmonar-o-que-aconteceu-com-meu-pulmao-e-o-que-esperar-da-recuperacao`;
- quatro triagens por diferencial nominal exato: dor torácica, dispneia,
  cianose e sintomas cardiovasculares na gravidez;
- emergência `tromboembolismo-pulmonar`;
- checklists de alta após TEV e seleção ambulatorial de TEP de baixo risco;
- trilha de TEP intermediário-alto e terapia guiada pelo risco.

As quatro arestas externas curadas ficam no manifesto genérico. O grafo exige
origem e destino publicados na mesma reconciliação; como a doença está
pendente, nenhuma nova aresta será exibida antes da revisão humana.

Exames, calculadoras, medicamentos, evidências, estudos e casos permanecem no
tópico `Tromboembolismo`. Apesar de vários registros serem diretamente
aplicáveis, não foram promovidos em massa a verbo clínico forte. Os metadados
farmacológicos ainda têm lacunas: alteplase usa indicação em formato
inconsistente e DOAC/HBPM têm campos de indicação vazios em alguns registros.

## Fontes primárias

- Creager et al. Diretriz multissocietária AHA/ACC 2026, DOI
  `10.1161/CIR.0000000000001415`, PMID `41712677`;
- correção oficial de 14/07/2026, DOI
  `10.1161/CIR.0000000000001462`, PMID `42441758`;
- Amado et al. Diretriz brasileira SBPT 2025, DOI
  `10.36416/1806-3756/e20240314`, PMID `40531728`, CC BY 4.0.

A correção AHA substitui a tabela de avaliação ecocardiográfica do VD; o
verbete não reproduz seus limiares numéricos. A SBPT foi parafraseada com
atribuição, link da licença e indicação de adaptação.

## Gates jurídicos

Conteúdo e fluxogramas derivados da ESC foram retirados deste verbete. A ESC
exige licença formal para conteúdo incluído, citado ou transformado em
software/algoritmos. A AHA usa copyright padrão; o lote cita e parafraseia a
diretriz sem copiar tabelas, figuras ou infográficos, mas o sistema A–E ainda
requer confirmação jurídica antes da publicação.

## Revisão necessária

Antes de mudar `review_status`, revisar clinicamente o comportamento combinado
das regras, critérios de alta, populações especiais, contraindicações à
reperfusão e o uso do sistema A–E. CI, reconciliação do banco, RC2 e QA visual
também devem estar verdes no head exato.
