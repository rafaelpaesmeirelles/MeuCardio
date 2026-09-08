# Auditoria transversal — evidências, estudos, documentos e galeria

Data: 08/09/2026. Base inspecionada: e7b7c35def95831f2745f5e5810f477de6a6da28. Auditoria complementar à camada doença→conteúdo certificada, sem alterações de conteúdo/editorial, UI, infraestrutura ou merges.

## Resultado entregue ao coordenador

Arquivo de integração: `work/candidatos-estudos.json` no diretório pai deste repositório. São 360 relações revisadas: **315 studied_in** e **45 associated_with**. Frentes de origem: 358 medicamento e 2 galeria; destinos: 358 estudo e 2 exame. Abrangem 76 medicamentos e 303 estudos. Todos os nós foram resolvidos unicamente nos manifestos canônicos e estão revisados; zero duplicatas na chave tipada de relação. A publicação real deve ser confirmada pelo importador e reconcile runtime do coordenador, não inferida apenas do JSON fonte.

As 360 relações têm fonte com caminho e fragmento e trecho editorial integral no review_note. O campo `studied_in` significa que o medicamento foi intervenção, comparador ou exposição efetivamente avaliada; não significa benefício, indicação, tratamento ou recomendação. Ensaios neutros ou prejudiciais, como GALILEO, INVICTUS e APPRAISE-2, permanecem classificados dessa maneira. Estudos observacionais e metanálises mantêm sua natureza explícita na prova.

## Cobertura e validação

- 2.061 estudos, 3.363 evidências e 281 imagens: todos revisados; nenhum slug duplicado dentro de cada frente.
- 1.215 evidências declaram document_slug; 174 declaram study_slug. Todos os 174 estudos-alvo existem; todas as respectivas referências textuais contêm o DOI do estudo-alvo.
- Nenhum DOI não vazio repetido no manifesto de estudos. Nenhum file_path repetido no manifesto de galeria.
- O published:false dos arquivos não foi modificado: a autorização de publicação vem dos manifestos editoriais e reconcile, não de alteração artificial desses campos. O manifesto full-corpus-release-20260907 autoriza o corpus revisado de 11.581 itens.
- Triagem percorreu todos os 2.061 resumos contra a identidade nominal completa do generic_name do catálogo de medicamentos, seguida de leitura contextual de todos os 383 pares adicionais encontrados. Além destes, o primeiro lote validou 12 relações nominais de ensaios centrais e 2 relações de galeria.
- Dos 383 pares adicionais: 303 studied_in, 43 associated_with e 37 excluídos. Os 353 da segunda rodada têm decisão individual em `work/decisoes-estudos.json`; a primeira rodada aprovou 29 e excluiu colchicina→AIRTRIP.
- O mecanismo atual não produz studied_in automaticamente; o manifesto legado exige origem doença. Assim, as relações medicamento→estudo não duplicam essas relações existentes. A deduplicação final contra o banco cabe ao importador por chave source/target/verbo.

## Semântica dos mecanismos existentes

`knowledge_graph.py`, `_registrar_referencias_explicitas`, já orienta documento→evidência como supported_by, usando EvidenceRecord.document_slug. Orienta evidência→estudo como supported_by usando EvidenceRecord.study_slug e exige evidência revisada e estudo publicado/revisado. Não inverter essas direções nem fabricar evidência→medicamento supported_by.

O artigo de revisão ou orientação contextual não equivale a evidência que sustenta toda indicação do medicamento. Por isso não foi acrescentada nenhuma relação supported_by neste lote; toda nova relação forte é studied_in com intervenção/comparador/exposição explícita em resumo revisado. Medicamentos apenas citados em guias, componentes de polipílula, exposição cujo antídoto foi estudado e fármacos usados como parte de teste foram associados conservadoramente quando pertinentes.

A galeria não possui campos de referência clínica no modelo, e hoje recebe ligação temática e vínculos originados em outras frentes. Foram revisadas duas associações explícitas:

1. galeria `holter-bloqueio-atrioventricular-alto-grau-sarcoidose-cardiaca` → exame `holter-24h`: findings declara trecho de Holter, sem extrapolar a reversibilidade do caso para BAV degenerativo.
2. galeria `eco-endocardite-vegetacao-aortica` → exame `ecocardiograma-transesofagico-na-endocardite-infecciosa`: teaching_points discute expressamente a maior sensibilidade do ETE para vegetações pequenas e abscessos. Vínculo educacional associated_with; não declara que a própria imagem foi obtida por ETE.

## Exclusões deliberadas

37 pares rejeitados, documentados na triagem. Categorias principais:

- Valsartana citada somente como componente de sacubitril/valsartana: conectar o nó canônico da combinação, não duplicar o estudo no fármaco isolado. PARADIGM-HF, PIONEER-HF, PARADISE-MI, PANORAMA-HF, TRANSITION, SARAH e PRADA-II são exemplos. PARAGON-HF/PARAGLIDE-HF mantêm valsartana porque ela é comparador isolado explícito.
- Colchicina em AIRTRIP e IRAP: resistência/intolerância define população; a intervenção é anakinra.
- Tratamento de fundo: digoxina em RALES/PROMISE/V-HeFT-II; ezetimiba em OCEAN(a), CORALreef-HeFH, BROADWAY/DESCARTES; bosentana em PHIRST/TRIUMPH/STEP; espironolactona em CHARM-Added; entre outros.
- Braço de ensaio publicado separadamente: clonidina no artigo POISE-2 de aspirina; ácido tranexâmico no artigo POISE-3 de metas pressóricas; valsartana no artigo NAVIGATOR de nateglinida.
- Bivalirudina em SAFARI-STEMI: cointervenção basal; o objeto é acesso radial/femoral.
- Nenhuma relação por same_theme foi promovida. Nenhuma contraindicação, interação ou causalidade foi gerada.

## Documentos e gaps de mecanismo

Links Markdown da Biblioteca são processados como alvo→mentioned_in→documento. Contudo `_slug_de_link_markdown` reconhece apenas `/biblioteca/` e arquivos .md. Há **10 links explícitos /calculadoras/** em documentos canônicos da UCO ignorados por esse caminho: acidose metabólica, cetoacidose euglicêmica, classificação SCAI, falência de VD, choque cardiogênico, ventilação não invasiva no EAP, LRA, hipercalemia e acidose láctica por metformina. A correção apropriada é resolução de rotas tipadas existentes, exigindo alvo canônico ativo, mantendo mentioned_in; não inferir diagnóstico/monitorização a partir do link.

## Duplicatas de mídia e limites

Seis URLs de origem de galeria são compartilhadas por duas entradas cada. Três são arquivos Wikimedia idênticos (FA de duas derivações; peça de vegetação; ventriculografia de Takotsubo); três são artigos PMC com figuras/modalidades distintas. Isto não é slug duplicado nem foi motivo para apagar conteúdo. Não criar relação clínica entre imagens só porque usam a mesma fonte.

Esta auditoria fecha todos os candidatos da triagem nominal declarada; não prova ausência universal de relações clínicas no texto livre. O generic_name completo não cobre automaticamente todos os nomes sem sal, traduções, marcas e abreviações. O coordenador deve preservar esse limite no relatório global, completar os gates e comparar a produção real. Não foram realizados deploy, runtime sentinels ou alteração de knowledge_graph.py por este agente.

## Complemento — evidência como destino de medicamentos e exames

Arquivo final separado: `work/candidatos-evidencias-transversais.json` (fora do repositório). **312 relações revisadas**, sendo **181 recommended_by** e **131 associated_with**; 298 origens medicamento e 14 exame. Zero nós ausentes/não revisados e zero duplicatas internas. O lote inicial de 46 também não duplicava o manifesto transversal integrado; o coordenador deverá repetir deduplicação no momento da integração final.

A triagem integral dos 3.363 enunciados pelo generic_name completo encontrou 296 pares. Dezessete estavam no lote inicial e os 279 restantes foram TODOS lidos e decididos: 138 recommended_by, 128 associated_with e 13 excluídos. Não resta fila de revisão desses candidatos. `work/decisoes-evidencias.json` contém as 279 decisões individuais; `work/triagem-evidencias-pendente.json` conserva o nome do arquivo de entrada, mas TODOS os seus itens já têm decisão no arquivo de decisões. Os outros 29 itens do lote inicial são medicamentos identificados por nome sem sal ou exames, fora daquela varredura nominal.

Recomendação positiva explicitamente nominal usa medicamento/exame→recommended_by→evidência. O review_note preserva o enunciado e a referência completos, inclusive população, condições, dose, grau e limitações. Nenhuma relação doença→tratamento, contraindicação ou causalidade foi criada. Evidência negativa, monitorização, ajuste/suspensão, resultado de ensaio, recomendação histórica ou contexto de alternativa usa associated_with quando clinicamente pertinente. Não converter ausência de benefício em indicação positiva.

Os hubs abrangidos por recomendações diretas incluem FA, ICFEr/ICFEp, HAS resistente, pericardite, miocardite, endocardite, síncope/Holter, SCA, TVP/TEP e contexto de choque/arrítmias. Para amiodarona, as restrições de cardioversão e preferência por alternativas permanecem explícitas; para espironolactona, cortes de função renal/potássio e terapia prévia permanecem no texto; recomendações específicas de Chagas não foram generalizadas a outras etiologias.

Dez das evidências do lote inicial já declaravam document_slug. Isso produz documento→supported_by→evidência, mas não substitui medicamento/exame→evidência, pois a origem e a navegação são diferentes. As referências existentes foram preservadas.

Treze exclusões da triagem adicional:

- Oito pares de valsartana apenas como componente de sacubitrilvalsartana: não representar o ARNI por valsartana isolada.
- Dois pares de adenosina em síncope adenosina-sensível: o enunciado recomenda dispositivo; adenosina é mecanismo/sensibilidade, não medicamento indicado.
- Ranolazina no enunciado LQT3: comparação histórica; recomendação atual citada é mexiletina.
- Ticagrelor no HOST-EXAM: advertência contra extrapolar a droga não estudada.
- Finerenona em `esc-2026-mra-independente-de-feve`: o próprio enunciado exige VERIFICAÇÃO HUMANA NECESSÁRIA para mapear molécula à faixa de FE. A aresta foi excluída, sem alterar fonte, status ou inventar recomendação.

Exclusões adicionais de métodos: Holter de eventos de dispositivo, gravador de alça de sete dias e looper implantável não foram equiparados a Holter externo de 24h. ETE em cirurgia congênita, dissecção ou ablação não foi ligado ao exame específico de endocardite. Recomendações históricas ESC2015 de colchicina recebem somente associação contextual, não nova recomendação atual. Nome genérico de classe não gerou arestas para todos os integrantes.

Limite: revisão completa dos candidatos encontrados pelo método nominal declarado não equivale a provar que todo sinônimo, marca, tradução ou nome sem sal foi exaurido em texto livre. Gates e runtime continuam sob responsabilidade do coordenador; nenhum conteúdo foi alterado por este agente.
