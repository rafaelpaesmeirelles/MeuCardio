# Auditoria transversal: medicamentos e exames — 2026-09-08

Base informada pelo coordenador: e7b7c35def95831f2745f5e5810f477de6a6da28. Escopo: metadados canônicos, interações, mecanismos de importação e ligações medicamento–exame. Nenhuma publicação ou alteração editorial realizada por este agente.

## Inventário e validação

- 206 medicamentos e 423 exames; todos revisados; zero slugs duplicados em cada catálogo.
- Contagens coincidem com editorial-approvals/full-corpus-release-20260907.json. O campo `published:false` no JSON de exames não determina publicação: carregar_exames.py exclui esse campo e preserva a decisão no banco. Publicação efetiva deve ser confirmada na reconciliação/runtime pelo coordenador.
- 127 registros de interação, 49 pares nominais revisados, zero pares duplicados e zero medicamentos referenciados ausentes. Após classificar a ausência explícita abaixo, 48 pares positivos elegíveis.

## Falha clínica corrigida na fonte

`medicamentos/interacoes.json#rivaroxabana-digoxina` declara ausência de interação farmacocinética, mas o grafo importava qualquer par revisado como `interacts_with`. Adicionado somente `interaction_present:false`, preservando o texto e status.

A ausência também é documentada no estudo farmacológico original [PMID 23206451](https://pubmed.ncbi.nlm.nih.gov/23206451/) e na [rotulagem FDA do Xarelto](https://www.accessdata.fda.gov/drugsatfda_docs/label/2014/022406s010lbl.pdf). Não converter essa ausência em relação contextual artificial.

Consumidores que o coordenador precisa corrigir:

- `backend/app/services/knowledge_graph.py`: pular registro marcado `interaction_present is False`; a reconciliação deve rejeitar a aresta automática anterior, preservando auditoria.
- `backend/app/api/drugs.py`: não incluir o registro negativo no bloco `verificadas` como alerta leve. O gate de referências pode continuar verificando os dois slugs.
- Testar par negativo sem aresta/alerta, par positivo preservado e rejeição idempotente da aresta automática legada.

Não usar busca por negação no texto como implementação: digoxina–furosemida nega interação farmacocinética, mas afirma potencialização farmacodinâmica real da toxicidade. A marcação estruturada evita esse falso negativo.

## Lote curado entregue ao coordenador

`../candidatos-med-exames.json`: 15 arestas sem duplicatas, 14 `monitor_with` e uma `associated_with`. Ambos os extremos foram validados individualmente no catálogo revisado. Cada candidato inclui campo canônico de proveniência, trecho, referências e contexto clínico.

- Varfarina → INR.
- Digoxina → digoxinemia geral e digoxinemia no idoso com função renal reduzida (dois exames canônicos distintos, sem fundi-los).
- Amiodarona → provas tireoidianas específicas para disfunção por amiodarona.
- Espironolactona/eplerenona → potássio e creatinina no contexto explícito de uso concomitante de IECA/BRA.
- Apixabana/rivaroxabana/dabigatrana/edoxabana → clearance de Cockcroft–Gault no contexto de anticoagulação da FA.
- Apixabana/rivaroxabana/edoxabana → anti-Xa calibrado em situações excepcionais descritas na fonte; não monitorização rotineira.
- Heparina não fracionada → ACT periprocedural.
- Sacubitril/valsartana → conteúdo sobre interferência na interpretação BNP/NT-proBNP, por `associated_with`; não se afirmou interação farmacológica com um exame.

## Exclusões e limites

- Dabigatrana excluída do anti-Xa: o exame nomeia somente os três inibidores de Xa; dabigatrana inibe trombina.
- Não estender o exame de espironolactona/eplerenona a finerenona somente por classe: a fonte nomeia os dois primeiros no contexto estudado.
- Não criar relação para ECG pediátrico ou RX de tórax pediátrico a partir da monitorização genérica da amiodarona. Identidade do exame precisa respeitar população e contexto.
- Não transformar indicações/contraindicações livres em arestas fortes por palavras. Indicações, causalidade e contraindicações com exceções continuam no conteúdo canônico; lote atual não achata essas exceções.
- Alertas de classe, interações ternárias e menções textuais permanecem separados dos pares nominais.
- Diagnóstico doença→exame já certificado não foi repetido. Não se criaram arestas reversas redundantes: consulta do grafo deve percorrer entrada e saída.

Esta auditoria local valida o lote e revela falha concreta, mas não certifica publicação ou ausência global de todos os gaps clínicos. Importação transversal e execução runtime pertencem à integração coordenada.

## Segunda passagem e busca

Mais oito candidatos em `../candidatos-med-exames-adicional.json`, todos `exame → associated_with → medicamento`: eco de estresse/dobutamina; teste farmacológico de Brugada/flecainida e procainamida; teste diagnóstico-terapêutico de TSV/adenosina; RMC de estresse/adenosina; vasorreatividade pulmonar/epoprostenol; farmacogenética de estatinas/rosuvastatina e fluvastatina. São medicamentos nomeados explicitamente em `what_it_measures`. Não se afirmou que o medicamento trata a doença diagnosticada: isso seria particularmente perigoso no teste provocativo de Brugada.

Excluídos ajmalina, pilsicainida, iloprosta, óxido nítrico e regadenosona por ausência de nós medicamentosos canônicos. Não fabricar nós. Não estender automaticamente farmacogenética à associação fixa rosuvastatina/ezetimiba. Não criar `alternative_to` entre fármacos a partir de alternativas de um procedimento específico, pois perderia contexto e poderia afirmar intercambialidade geral.

`scripts/tests/test_transversal_search_sentinels.py`: quatro testes puros aprovados. Executam as funções reais extraídas da AST de catalog_search e o registro real de calculadoras, sem carregar banco. Cobrem as oito consultas humanas obrigatórias, CHA₂DS₂-VASc/CHA2DS2-VASc/HAS-BLED no registro, caracteres especiais de LIKE, unicidade/revisão do Holter e cláusula que inclui slug no FTS. Não simulam stemming PostgreSQL, ranking agregado, publicação efetiva ou HTTP público. Portanto esses quatro testes complementam, mas não substituem, as sentinelas runtime obrigatórias.

Escopo coberto: inventário completo das duas frentes; todos os 127 registros estruturados de interação e respectivos pares; campos de monitorização e exames farmacológicos nomeados; exclusões de população, mecanismo e classe; proveniência e direção dos 23 candidatos. A revisão não infere relações novas a partir da simples menção de classe terapêutica em todo texto livre: esses textos não constituem autorização estruturada para uma expansão cartesiana de centenas de arestas.

## Contrarrevisão independente do lote de estudos

Revisado o lote de 360 candidatos do outro agente: 315 `studied_in`, 45 `associated_with`, nenhuma duplicata. Conferência de pares e justificativas focada em tratamento de fundo, combinações e alvo real da randomização. Sem edição no arquivo do agente.

Recomendados seis rebaixamentos conservadores para `associated_with`, preservando vínculos, para manter a mesma regra já usada no lote em TRITON, SHARP e componentes de polipílulas:

| Medicamento | Estudo | Motivo documentado no resumo canônico |
|---|---|---|
| sinvastatina | ACCORD-LIPID | Sinvastatina aberta em todos; randomização fenofibrato/placebo. |
| furosemida | CLOROTIC | Furosemida como fundo comum; randomização HCTZ/placebo. |
| carvedilol | OVERCOME | Enalapril+carvedilol juntos versus controle, sem contraste isolado. |
| carvedilol | CARDIAC-CARE | Candesartana+carvedilol juntos versus cuidado usual. |
| espironolactona | REALIZE-K | Titulação/run-in com espironolactona; randomização posterior SZC/placebo. |
| ezetimiba | SaveSAMS idosos | Rosuvastatina alta versus dose moderada+ezetimiba; duas mudanças simultâneas. |

Não identificada exclusão integral obrigatória entre os 45 vínculos contextuais: as notas nomeiam o medicamento e preservam sua condição contextual. CONFIDENCE/AMBITION comportam `studied_in` porque incluem braços de monoterapia. HNF no ULTIMA e sinvastatina no IMPROVE-IT têm comparadores nominais isolados e são defensáveis com `studied_in`, desde que o verbo não seja exibido como eficácia isolada. A análise não revalidou externamente todos os 360 artigos nem certifica sua publicação runtime.

Após autorização do coordenador, os seis rebaixamentos foram aplicados em `doencas/relacoes-transversais.json`, com notas específicas e preservação dos trechos de prova. O sublote de 360 fica com 309 `studied_in` e 51 `associated_with`; nenhum vínculo foi eliminado. A alteração foi limitada às seis relações e respectivas notas; o inventário de conteúdo e seus status editoriais não foram alterados.
