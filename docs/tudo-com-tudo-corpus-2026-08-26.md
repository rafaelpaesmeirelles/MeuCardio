# Tudo com Tudo — auditoria integral do corpus (2026-08-26)

## Escopo

O script `scripts/audit_tudo_com_tudo.py` percorre os 9.452 itens versionados:
1.887 documentos Markdown e 7.565 registros em 12 manifestos JSON. A execução
não lê dados de paciente, não altera banco e falha de forma visível quando uma
referência por slug deixa de resolver.

## Resultado do snapshot

- 9.452/9.452 itens com `review_status=revisado`;
- zero slug duplicado no inventário canônico;
- zero referência explícita quebrada após a correção de oito
  `checklists.documento_origem` inválidos;
- 568 links Markdown internos válidos (links externos e exemplos dentro de
  blocos/código inline são excluídos);
- 3.067 etapas de trilha válidas;
- 776 vínculos evidência→documento;
- 355 checklists com documento de origem válido; oito permanecem sem origem
  porque não existe documento canônico correspondente e um link aproximado
  seria incorreto;
- 386 materiais ao paciente com documento técnico;
- 259 referências estruturadas no Modo Emergência;
- 101 vínculos doença→documento/material;
- 49 pares medicamento–medicamento revisados e nominalmente explícitos;
- três diferenciais de triagem com casamento exato e não ambíguo.

## Mudança de arquitetura

O backfill anterior cadastrava todos os nós, mas criava `same_theme` apenas para
os cinco primeiros itens de cada tipo/tema. A seleção nem sequer tinha ordenação
estável. A correção substitui essa malha parcial por:

```text
item -[belongs_to_topic]-> tema canônico <-[belongs_to_topic]- item
```

Cada item com tema recebe uma associação linear. A API resolve o segundo salto,
prioriza relações explícitas e oculta o nó taxonômico. Arestas `same_theme`
antigas ficam preservadas para rollback e deixam de contaminar a resposta nova.

## Cobertura segura

9.452/9.452 itens possuem tema explícito. Os 61 que não tinham `theme`/`tema`
passam a ser cobertos pelos campos estruturados `area`/`areas`: 49 doenças
geram uma aresta cada e 12 triagens geram 40 arestas. No corpus completo, as
87 doenças e 14 triagens mantêm 129 associações de área, usando somente a tabela fechada
Geral, Cardiologia pediátrica, Cardiologia geriátrica, Cardio-oncologia e
Gravidez. Relações clínicas adicionais continuam na fila de curadoria; nenhum
vínculo será criado por similaridade textual, embedding, URL compartilhada ou
LLM.

## Relações importadas

- `supported_by`: documento→evidência ligada;
- `derived_from`: material/checklist/protocolo→documento de origem;
- `uses_flowchart`: protocolo de emergência→fluxograma;
- `associated_with`: relacionados declarados de emergência;
- `contains`: trilha→etapa, preservando ordem e justificativa em `extra`;
- `mentioned_in`: links internos de Markdown;
- `interacts_with`: somente pares curados com exatamente dois slugs;
- relações especializadas de doença/triagem já existentes.

Toda derivação mecânica permanece `pendente_revisao`; os 49 pares de interação
já têm fonte e revisão no próprio registro e entram como `explicit/revisado`.

O reconciliador marca cada aresta automática com produtor e fingerprint. Se o
metadado muda, a aresta é atualizada; se some, ela vira `rejeitado` com motivo
auditável, sem `DELETE`. Relações manuais têm precedência. Uma trava transacional
impede dois backfills PostgreSQL simultâneos, e o log administrativo é gravado
na mesma transação do backfill.

A primeira execução adota arestas automáticas legadas somente por uma assinatura
fechada do campo de origem. Rejeições humanas continuam terminais para o gerador;
somente uma rejeição marcada como `source_removed` pode ser reativada quando a
fonte reaparece. O lock é não bloqueante e a API responde `409` quando outra
reconciliação já está em andamento.

O workflow `Corpus inventory` fixa os pisos em 9.452 registros/2.185 arquivos e
executa este auditor em todo PR que altera o corpus ou seus validadores.

## Interface

Trilhas, modelos/aplicações de checklist, materiais ao paciente e protocolos de
emergência passam a expor o ecossistema relacionado. O Modo Emergência também
renderiza seus `relacionados` diretamente do pacote offline.
