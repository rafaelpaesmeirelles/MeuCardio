# Auditoria transversal de ferramentas e jornadas — 2026-09-08

Base indicada pela coordenação: e7b7c35d. Escopo: origens calculadora, fluxograma, emergência, checklist, material paciente, caso, trilha e triagem. Inspeção de código e fontes canônicas locais; não equivale a fotografia do banco publicado. Não houve edição do grafo central, metadados compartilhados, UI, infraestrutura ou estados de revisão.

## Resultado acionável

O parser Markdown do grafo reconhecia somente Biblioteca e arquivos .md. Dez referências locais explícitas a quatro calculadoras, em nove documentos, eram descartadas antes da resolução de entidades. São referências por rota/slug; não inferência por palavras clínicas. A direção correta é **calculadora → mentioned_in → documento**. Nunca converter esses links automaticamente em monitor_with, diagnosed_by ou indicated_for.

Implementado auxiliar `backend/app/services/clinical_markdown_links.py`: `parse_clinical_markdown_target(destination) -> ((tipos permitidos,), slug) | None`. Aceita `/calculadoras/<slug>` e preserva Biblioteca/.md. Rejeita host externo, URLs de protocolo relativo, path com segmentos extras, travessia e slug vazio. Remoção de query/fragment e decodificação seguem o comportamento prévio. Integração do chamador em knowledge_graph.py pertence à coordenação.

Evidências canônicas (cada par ocorre uma vez):

| Origem calculadora | Documento que a menciona |
|---|---|
| acidose-metabolica-winter-anion-gap-uco | cetoacidose-euglicemica-associada-a-inibidores-de-sglt2 |
| acidose-metabolica-winter-anion-gap-uco | classificacao-scai-de-estagios-do-choque-cardiogenico |
| acidose-metabolica-winter-anion-gap-uco | acidose-latica-associada-a-metformina-mala-no-paciente-critico-cardiovascular |
| oxigenacao-pao2-fio2-sdra-uco | ventilacao-nao-invasiva-no-edema-agudo-de-pulmao-cardiogenico-cpap-versus-bipap |
| oxigenacao-pao2-fio2-sdra-uco | falencia-aguda-do-ventriculo-direito-cor-pulmonale-agudo-consenso-acvc-esc-2024 |
| lesao-renal-aguda-kdigo-uco | choque-cardiogenico-diagnostico-e-manejo-com-drogas-vasoativas |
| lesao-renal-aguda-kdigo-uco | acidose-metabolica-compensacao-respiratoria-e-anion-gap-na-uco |
| lesao-renal-aguda-kdigo-uco | lesao-renal-aguda-na-uco-criterios-kdigo-creatinina-e-diurese |
| lesao-renal-aguda-kdigo-uco | falencia-aguda-do-ventriculo-direito-cor-pulmonale-agudo-consenso-acvc-esc-2024 |
| hipercalemia-seguranca-uco | hipercalemia-na-uco-gravidade-ecg-e-gates-de-seguranca |

Fontes: arquivos com os slugs acima em content/; calculadoras em backend/app/services/intensive_care_calculators.py. O backfill deve continuar exigindo ambos os nós publicados e relatar referência não resolvida, nunca inventar nó.

## Matriz auditada

Contagens abaixo são dos metadados.json principais, todos com review_status revisado; fragmentos/correções não foram contados como registros adicionais.

| Origem | Quantidade | Estrutura disponível e decisão |
|---|---:|---|
| Calculadora | Registro Python | referência bibliográfica livre não determina estudo por título. Gap confirmado nos links Markdown acima; sem promoção de indication a partir de purpose/limitations. |
| Fluxograma | Document.kind | Links Biblioteca/.md já geram mentioned_in; nenhum link a calculadora encontrado nos arquivos cujo nome contém fluxograma. Não criar contains ou uses_flowchart pela semelhança temática. |
| Emergência | 77 | 77 documento_slug, 74 fluxograma_slug, 133 entradas relacionados. derived_from e uses_flowchart já cobertos. related é associated_with estrutural explícito. |
| Checklist | 473 | documento_origem já gera derived_from. itens/source_refs textuais não autorizam medicamento/exame usado. |
| Material paciente | 448 | documento_slug já gera derived_from. fontes livres não são slugs. Camada paciente-doença já certificada permanece fora desta auditoria. |
| Caso clínico | 915 | source_refs é bibliografia livre; campos enunciado/explicacao/opcoes não declaram identidade usada no caso. Não inferir used_in_case de opções incorretas ou citações narrativas. |
| Trilha | 555 | 3391 etapas explícitas: 2382 documento, 603 estudo, 240 medicamento, 80 checklist, 36 caso, 32 evidência, 18 calculadora. Todos os tipos efetivamente usados já são suportados por contains. |
| Triagem | 21 | áreas e diferenciais já importados. default_tests/emergency_flow são prosa e não slugs, inclusive instrução de acionar protocolo em sangramento. Não ligar automaticamente por nome parecido. |

## Correção de hipótese sobre emergência

A hipótese inicial de 133 relacionados invisíveis foi rejeitada após inspecionar `_publicavel` em knowledge_graph.py: há exceção específica para associated_with com campo EmergencyProtocol.relacionados pertencente ao backfill. Portanto são navegação já existente, não gap de publicação. Não é necessário liberar genericamente associated_with pendente, mudar review_status ou duplicar registros em novo manifesto. O arquivo externo solicitado `../candidatos-emergencia.json` contém lista vazia por esse motivo. A política só permite associated_with revisado com confiança explicit e proveniência editorial/imported; isso também impede promoção automática da configuração derived atual.

## Duplicatas e exclusões

Não há slug repetido dentro de nenhum dos seis metadados.json inspecionados. Nenhuma trilha repete a mesma identidade item_type + item_slug em suas etapas. Nenhuma emergência repete documento_slug ou fluxograma_slug dentro de relacionados. Isso não certifica ausência de duplicatas no banco, que não foi consultado.

Não adicionar arestas inversas: a API já consulta entrada e saída. Preservar identidade do nó fluxograma via Document.kind, fallback documento legado, upsert e exclusão de conteúdo despublicado. Links repetidos ao mesmo alvo devem gerar um único triplo. As 133 referências de emergência e 3391 etapas não são novas contribuições e não devem inflar o resultado da correção.

## Lacunas editoriais sem vínculo inventado

Para ampliar casos→ferramentas, triagem→exames/protocolos e calculadora→evidência, a fonte deve primeiro declarar destinos canônicos tipados, finalidade e condição/contexto. Exemplo de contrato futuro: target_type, target_slug, relation_type, fonte exata, revisão e nota de limite. Caso com calculadora realmente usada admite calculadora→used_in_case→caso; referência que apenas explica um caso admite caso→supported_by→estudo, desde que identificador exato e evidência suportem isso. A citação bibliográfica livre deve permanecer sem aresta forte quando não resolve univocamente DOI/PMID/slug.

Triagem default_tests não deve virar diagnosed_by automaticamente: um exame inicial ou condicional pode servir apenas para descartar risco e não diagnosticar o sintoma. Fluxo em emergency_flow também não prova treats. Não ampliar matriz só para preencher combinações vazias.

## Verificação

`scripts/tests/test_clinical_markdown_links.py`: três testes puros unittest com 16 entradas cobrindo links válidos, escapes, externos, ambiguidades e compatibilidade Biblioteca. Executados com sucesso. Teste integrado de backfill/publicação permanece responsabilidade da integração central; este relatório não declara dez arestas efetivamente persistidas.

Atualização de verificação: quatro testes passam após integração central. O quarto extrai via AST o loop real de documentos de `_registrar_referencias_explicitas`, executa-o com dublês das operações de banco e verifica calculadora→mentioned_in→fluxograma, proveniência do campo e exclusão de link externo. Não duplica o algoritmo de produção e não substitui teste de banco/publicação.

## Matriz de sentinelas para conferência de runtime

Gerado externamente `../sentinelas-canonicas.json`: 16 sentinelas × 16 frentes, com lista de slugs exatos, relações e fonte. Usa doença composta (326 registros), triagem composta (21), manifesto revisado e related_document_slugs/patient_material_slug. Não usa similaridade lexical. Contagens de vínculos declarados, deduplicadas por tipo/slug/verbo: FA 437; IC 437; SCA 132; embolia pulmonar 18; TEV 79; HAS 12; resistente 22; HCM 106; endocardite 116; choque 112; síncope 256; estenose aórtica 127; dilatada 54; pericardite 196; miocardite 178; BAV 54.

A matriz é expectativa parcial para comparação, não resultado runtime nem prova de completude clínica. Grupos com zero são rotulados explicitamente como ausência de declaração neste recorte. Em especial medicamentos são conectados também por mecanismos de indicação/contexto fora deste recorte; não inferir que inexistem ou estão desligados. As finalidades diagnóstico/seguimento e contraindicações devem ser aferidas por relação e evidência, nunca pela mera presença do grupo exame/medicamento. Não foram criados candidatos para preencher zeros artificialmente.

## Correção do inventário de calculadoras no auditor

O gate posterior à integração expôs falso broken para hipercalemia-seguranca-uco. A fonte é canônica: `intensive_care_hyperkalemia_safety.py` declara Calculator e `services/__init__.py` incorpora INTENSIVE_CARE_HYPERKALEMIA_SAFETY_REGISTRY ao REGISTRY. BRASH segue padrão equivalente. O glob anterior `*calculators*.py` ignorava ambos por nome de arquivo, apesar de o runtime possuir os nós.

Alterado apenas trecho calculator_source/slugs do auditor para ler o REGISTRY montado e filtrar status implementada, mesmo gate do grafo. O registro real possui 69 objetos no momento desta verificação; hipercalemia e BRASH estão implementadas. Não foi criado nó ou alterada calculadora. Cinco testes passam; o adicional executa via AST a atribuição real do auditor, inclui ferramentas de segurança e exclui registro de teste não implementado.
