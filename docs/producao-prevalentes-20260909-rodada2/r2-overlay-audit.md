# Auditoria técnica de overlays — cinco correções legadas

Data: 09/09/2026. Escopo: arquivos `*corrections.json` das frentes HAS, coronária e valvas/síncope. Nenhum catálogo global foi modificado, nenhum loader conectado ao banco foi executado.

**Conclusão:** nenhuma colisão de conteúdo com overlays versionados nos cinco registros. Os dois materiais permanecem integralmente iguais após simulação da correção editorial real do loader. Existe uma possibilidade distinta de sobrescrita das **notas de revisão dos dois checklists** pelo CorVIA Intelligence após publicação, dependendo de vínculos confirmados presentes no banco; o código atual preserva os itens e o resumo clínico desses checklists.

## Base imutável e código verificado

- Ref: `cb750689b94f7888b18133e68ff8293bff55d742`.
- Árvore recursiva em `round2-current-tree.json`: `b93dbae0e794992e9a36b02c434fe183d0dd1581`, `truncated: false`.
- Hashes Git dos quatro serviços locais calculados e comparados com a árvore: todos idênticos.

| Arquivo | Blob SHA |
|---|---|
| `backend/app/services/carregar_material_paciente.py` | `eca8639ae8fda67198ee8932592c2d16d576ec3a` |
| `backend/app/services/carregar_checklists.py` | `aff1b8c41521fce804b6de6ec1710e20f849aff8` |
| `backend/app/services/carregar_casos_clinicos.py` | `c4521666a413b84c7367a8aad75c1c1b1443700d` |
| `backend/app/services/scientific_loader_safety.py` | `11d9398eb085ae9dac0d7c7853742365be1005e8` |
| `material-paciente/correcoes/release-all-three-20260829-sem-posologia.json` | `a3bb53342847e3c0bcf9131e3f9c060dc0008c6c` |
| `backend/app/services/guideline_clinical_update.py` | `c400d8fde19263a43e5ddbfe4e80dadc610969d7` |
| `backend/app/services/guideline_clinical_update_runtime.py` | `e5230baf03cd0d932133cda0053c6fd127f602f5` |
| `backend/app/commands/reconcile_content.py` | `7446ba0fd742d631f7f5a3dc826083ae8da2ff16` |
| `backend/app/commands/publish_preserved_content.py` | `6e97f039f8b9323e75237a5ca79a7b837f2f8dc1` |

Overlays e serviços adicionais lidos pelo conector GitHub na ref acima. As cópias locais estão em `round2/overlay-cache/` apenas como evidência temporária, não para inclusão no commit final.

## Resultado por registro

| Tipo e slug | Overlay versionado | Outro caminho de carga/pós-carga |
|---|---|---|
| Material `estenose-aortica-e-troca-de-valva` | Nenhuma colisão; igualdade completa preservada após `_aplicar_correcoes`; sem posologia detectável | Não é alvo suportado do CorVIA Intelligence neste código |
| Material `por-que-tomar-dois-remedios-para-o-sangue-depois-do-infarto-ou-stent` | Nenhuma colisão; igualdade completa preservada após `_aplicar_correcoes`; sem posologia detectável | Não é alvo suportado do CorVIA Intelligence neste código |
| Caso `angina-persistente-coronarias-normais-anoca-inoca-endotipo` | Não existe diretório `casos-clinicos/correcoes` na árvore e seu loader não aplica overlays | Carga por slug a partir de `metadados.json`; não é alvo suportado do Intelligence |
| Checklist `confirmacao-de-hipertensao-resistente-verdadeira-antes-de-escalonar` | Não existe diretório `checklists/correcoes`; loader não aplica overlays | Itens e resumo preservados pelo Intelligence; `revisao` pode ser substituída e `source_refs` acrescida se houver vínculo confirmado |
| Checklist `estenose-aortica-de-baixo-fluxo-e-baixo-gradiente-avaliacao` | Não existe diretório `checklists/correcoes`; loader não aplica overlays | Mesma possibilidade de alteração de metadados acima; nenhuma reescrita de itens/resumo no ramo atual |

Os três slugs de caso/checklists ocorrem exatamente uma vez nos catálogos atuais. As substituições não introduzem chaves fora dos contratos existentes.

## Simulação de materiais

Extraídos via AST, sem importar banco ou aplicação, os métodos reais `_aplicar_correcoes`, `_regex_replace_recursive` e `_texto_do_registro` do serviço verificado. Simulação sobre os 448 registros atuais, substituindo somente os dois materiais desta rodada:

- Um arquivo de overlay encontrado; ele opera por slug, não globalmente.
- Quatro slugs efetivamente modificados pelo overlay: `icfep-e-obesidade-semaglutida-e-tirzepatida-o-que-esperar`, `semaglutida-protege-o-coracao-mesmo-sem-diabetes-o-select`, `segundo-diuretico-na-internacao-por-insuficiencia-cardiaca-o-que-esperar`, `meu-exame-de-lpa-veio-alto-o-que-muda-agora`.
- Interseção desses slugs com os dois materiais corrigidos: vazia.
- Os quatro padrões existentes ainda encontram suas ocorrências na simulação, sem provocar ValueError global.
- Os dois materiais corrigidos ficam idênticos ao fragmento de correção, e ambos passam a expressão regular de posologia do loader.
- Resultado reproduzível registrado em `round2/overlay-cache/overlay-result.json`.

## Ordem de carga e o que ainda importa na integração

`reconcile_content.FRONTS` encaminha cada frente ao seu loader nativo: casos → `carregar_casos_clinicos`, checklists → `carregar_checklists`, materiais → `carregar_material_paciente`. O importador Markdown escreve `Document`, não esses modelos. Overlays de doenças/triagem pertencem às respectivas frentes e não recebem esses cinco slugs por esse caminho.

Os nomes de trabalho `*-corrections.json` da rodada **não são descobertos automaticamente pelos loaders**. A integração precisa substituir o registro correspondente no `metadados.json` canônico. Apenas adicionar esses arquivos de trabalho ao repositório não aplicaria a correção. Depois da substituição, uma carga futura do mesmo manifesto reaplica os campos corrigidos.

`scientific_loader_safety` não restaura conteúdo antigo; gerencia status/publicação e notas/proveniência. Se a fonte permanecer `pendente_revisao`, o registro será despublicado pela carga, mesmo quando anteriormente público. Isso é contrato editorial, não colisão de overlay; o coordenador deve manter status e autorização coerentes com a revisão realmente realizada.

## Limite específico: notas dos checklists no Intelligence

`publish_preserved_content.main`, depois da sincronização, invoca `guideline_clinical_update_runtime.reapply_confirmed_updates`. O núcleo consulta `GuidelineLink` de origem Intelligence, confirmado, com diretriz não substituída. O ramo `item_type == "checklist"` atual acrescenta referência e define `revisao = "CorVIA Intelligence: ..."`; não altera `itens`, `resumo`, `condicao` ou `documento_origem`.

Portanto: **sem colisão de conteúdo clínico identificada; preservação integral da nota editorial do checklist não é garantida quando existir vínculo confirmado no banco**. Não houve acesso ao banco nesta auditoria; a existência de vínculos para esses dois registros continua desconhecida. Não é correto afirmar nem que a nota será certamente sobrescrita nem que ela está protegida em todos os ambientes.
