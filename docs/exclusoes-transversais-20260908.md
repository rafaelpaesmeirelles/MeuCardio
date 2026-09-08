# Exclusões e reclassificações transversais — 08/09/2026

Documento autocontido de decisões da auditoria Tudo com Tudo, sobre a base e7b7c35def95831f2745f5e5810f477de6a6da28 e o lote transversal integrado. Não altera conteúdos, status editoriais ou manifestação de autorização. As tabelas abaixo identificam os nós candidatos e a razão concreta de não publicar uma relação forte. Os arquivos de triagem externos foram consolidados aqui; sua consulta não é necessária para entender estas decisões.

## Síntese das decisões

- **37 candidatos medicamento→estudo excluídos**, incluindo colchicina→AIRTRIP da primeira rodada e os 36 da segunda rodada.
- **13 candidatos medicamento→evidência excluídos** por identidade incorreta, referência histórica, não participação no estudo ou exigência explícita de revisão da molécula.
- **4 registros de exclusão nos hubs críticos**: um par já existente e três grupos de candidatos semanticamente inadequados. Os grupos não são contagens de arestas individuais.
- **6 relações medicamento→estudo reclassificadas de studied_in para associated_with** após contrarrevisão independente. Os seis vínculos continuam presentes; não são exclusões de nós.
- Um registro estruturado de ausência de interação, rivaroxabana–digoxina, não pode produzir interacts_with nem alerta de interação.

Não somar grupos conceituais a relações individuais para criar uma contagem artificial. Nenhuma decisão depende de same_theme, similaridade lexical ou conveniência de densidade.

## Seis reclassificações confirmadas no manifesto integrado

A tabela descreve o estado verificado em `doencas/relacoes-transversais.json`. Todas as seis estão como associated_with com nota de contrarrevisão. Fontes de conteúdo: `estudos/metadados.json`, registro identificado pelo slug de destino, campo summary.

| Medicamento | Estudo canônico | Motivo do rebaixamento |
|---|---|---|
| carvedilol | overcome-enalapril-e-carvedilol-na-prevencao-de-disfuncao-sistolica-em-hemopatia-maligna | O braço experimental recebeu enalapril e carvedilol em conjunto versus controle; não houve contraste isolado de carvedilol. Vínculo contextual explícito; não afirma eficácia isolada, indicação ou recomendação. |
| espironolactona | realize-k-sodio-zirconio-ciclosilicato-na-otimizacao-da-espironolactona-na-icfer | Espironolactona foi titulada no run-in; a randomização posterior comparou continuação de sódio zircônio ciclosilicato versus placebo, preservando contexto de viabilização da terapia. Vínculo contextual explícito; não afirma eficácia isolada, indicação ou recomendação. |
| carvedilol | cardiac-care-bloqueio-neuro-hormonal-guiado-por-troponina-antraciclina | O braço experimental recebeu candesartana e carvedilol em conjunto versus cuidado usual; não houve contraste isolado de carvedilol. Vínculo contextual explícito; não afirma eficácia isolada, indicação ou recomendação. |
| sinvastatina | accord-lipid-fenofibrato-associado-a-sinvastatina-diabetes-tipo-2 | Sinvastatina aberta era tratamento de fundo em todos os pacientes; o contraste randomizado foi fenofibrato versus placebo. Vínculo contextual explícito; não afirma eficácia isolada, indicação ou recomendação. |
| furosemida | clorotic-trullas-2023-hctz-oral-add-on-furosemida-iv | Furosemida intravenosa era tratamento de fundo comum; o contraste randomizado foi hidroclorotiazida versus placebo. Vínculo contextual explícito; não afirma eficácia isolada, indicação ou recomendação. |
| ezetimiba | savesams-estatina-ezetimiba-idosos-seguranca-metabolica-estudo | Comparação de rosuvastatina em alta intensidade versus rosuvastatina em intensidade moderada associada a ezetimiba; duas mudanças simultâneas impedem afirmar contraste isolado de ezetimiba. Vínculo contextual explícito; não afirma eficácia isolada, indicação ou recomendação. |

O sublote original de 360 permanece com 360 relações, agora 309 studied_in e 51 associated_with. Uma relação studied_in deve respeitar o objeto realmente avaliado; adicionar ou alterar simultaneamente outro fármaco pode impedir afirmar contraste isolado. HNF/ULTIMA e sinvastatina/IMPROVE-IT foram preservados porque há comparador nominal isolado explicitamente documentado. Isso não autoriza exibir studied_in como eficácia isolada.

## Exclusões de medicamento→estudo

Fonte canônica de cada linha: `estudos/metadados.json#<estudo>.summary`. A ausência de aresta não despublica o estudo ou medicamento. Todas as identidades foram conferidas nos catálogos revisados; exclusão abaixo é semântica, não falta de acesso ao conteúdo.

| Medicamento candidato | Estudo canônico | Decisão e razão |
|---|---|---|
| colchicina | airtrip-anakinra-na-pericardite-recorrente-colchicina-resistente | Excluído: resistência à colchicina define a população; o ensaio de retirada randomiza anakinra ou placebo. Não é estudo da colchicina. |
| valsartana | jhund-2015-paradigm-hf-sacubitril-valsartana-por-idade | Valsartana é componente de sacubitril/valsartana; não estudo do medicamento isolado. Usar nó da combinação. |
| valsartana | panorama-hf-sacubitril-valsartana-versus-enalapril-em-insuficiencia-cardiaca-pediatrica | Valsartana é componente de sacubitril/valsartana; não estudo do medicamento isolado. Usar nó da combinação. |
| valsartana | paradigm-hf-sacubitril-valsartana-icfer | Valsartana é componente de sacubitril/valsartana; não estudo do medicamento isolado. Usar nó da combinação. |
| clonidina | poise-2-aspirina-perioperatoria-em-cirurgia-nao-cardiaca | Artigo relata braço aspirina; clonidina é menção ao braço publicado separadamente. |
| ezetimiba | aim-high-niacina-hdl-baixo-estatina | Tratamento de fundo, não intervenção ou comparador estudado. |
| sinvastatina | aim-high-niacina-hdl-baixo-estatina | Tratamento de fundo, não intervenção ou comparador estudado. |
| ezetimiba | ocean-a-dose-olpasirana-reducao-lipoproteina-a | Tratamento de fundo, não intervenção ou comparador estudado. |
| heparina-nao-fracionada | timi-risk-score-derivacao-original-antman-2000 | Tratamento de fundo/coorte de origem; objeto do artigo é escore ou outro medicamento. |
| bosentana | phirst-tadalafila-na-hipertensao-arterial-pulmonar | Tratamento de fundo/coorte de origem; objeto do artigo é escore ou outro medicamento. |
| valsartana | transition-momento-de-inicio-de-sacubitril-valsartana-apos-ic-aguda | Componente valsartana não isolado; existe nó sacubitrilvalsartana. |
| bosentana | mclaughlin-2010-triumph-treprostinil-inalatorio-na-hipertensao-arterial-pulmonar | Tratamento de fundo/coorte de origem; objeto do artigo é escore ou outro medicamento. |
| ezetimiba | coralreef-hefh-enlicitide-hipercolesterolemia-familiar-heterozigotica | Tratamento de fundo, sem avaliação direta da droga no artigo. |
| digoxina | rales-espironolactona-ic-grave | Tratamento de fundo, sem avaliação direta da droga no artigo. |
| ezetimiba | broadway-obicetrapibe-inibidor-de-cetp-reducao-de-ldl | Tratamento de fundo, sem avaliação direta da droga no artigo. |
| digoxina | promise-milrinona-oral-mortalidade-insuficiencia-cardiaca-grave | Tratamento de fundo; artigo compara outra intervenção ou meta de tratamento. |
| valsartana | pioneer-hf-sacubitril-valsartana-internacao-icfer | Componente valsartana não isolado; usar nó sacubitrilvalsartana. |
| valsartana | paradise-mi-sacubitril-valsartana-pos-infarto | Componente valsartana não isolado; usar nó sacubitrilvalsartana. |
| ramipril | escape-controle-pressorico-intensivo-e-progressao-da-doenca-renal-em-criancas | Tratamento de fundo; artigo compara outra intervenção ou meta de tratamento. |
| felodipino | hot-alvo-de-pressao-diastolica-e-aspirina-em-baixa-dose-na-hipertensao | Tratamento de fundo; artigo compara outra intervenção ou meta de tratamento. |
| bosentana | step-iloprosta-inalatoria-associada-a-bosentana-hipertensao-arterial-pulmonar | Tratamento de fundo; artigo compara outra intervenção ou meta de tratamento. |
| colchicina | irap-anakinra-em-pericardite-corticoide-dependente-e-colchicina-resistente | Resistência/terapia de fundo ou braço relatado em outro artigo; não estudo da droga candidata. |
| acido-tranexamico | poise-3-manejo-pressorico-hipotensao-vs-hipertensao-em-cirurgia-nao-cardiaca | Resistência/terapia de fundo ou braço relatado em outro artigo; não estudo da droga candidata. |
| colchicina | cannabidiol-fase-2-na-pericardite-recorrente | Resistência/terapia de fundo ou braço relatado em outro artigo; não estudo da droga candidata. |
| valsartana | lcz-in-nhcm-sacubitril-valsartana-na-cardiomiopatia-hipertrofica-nao-obstrutiva | Componente valsartana não isolado; usar nó sacubitrilvalsartana. |
| espironolactona | charm-added-candesartana-sobre-ieca-na-icfer | Resistência/terapia de fundo ou braço relatado em outro artigo; não estudo da droga candidata. |
| indapamida | denerhtn-denervacao-renal-na-hipertensao-resistente | Resistência/terapia de fundo ou braço relatado em outro artigo; não estudo da droga candidata. |
| ezetimiba | descartes-evolocumabe-52-semanas-na-hiperlipidemia | Resistência/terapia de fundo ou braço relatado em outro artigo; não estudo da droga candidata. |
| valsartana | navigator-nateglinida-em-intolerancia-a-glicose | Resistência/terapia de fundo ou braço relatado em outro artigo; não estudo da droga candidata. |
| digoxina | vheft-ii-enalapril-versus-hidralazina-dinitrato-na-ic | Tratamento de fundo; objeto é outra droga, acesso vascular, adesão à polipílula ou ablação. |
| bivalirudina | safari-stemi-acesso-radial-versus-femoral-no-iamcsst | Tratamento de fundo; objeto é outra droga, acesso vascular, adesão à polipílula ou ablação. |
| sacubitrilvalsartana | poly-hf-polipilula-icfer-funcao-adesao | Tratamento de fundo; objeto é outra droga, acesso vascular, adesão à polipílula ou ablação. |
| valsartana | poly-hf-polipilula-icfer-funcao-adesao | Valsartana é componente de sacubitrilvalsartana, não droga isolada estudada. |
| edoxabana | stabled-ablacao-fa-apos-avc-prevencao-secundaria | Tratamento de fundo; objeto é outra droga, acesso vascular, adesão à polipílula ou ablação. |
| valsartana | sarah-sacubitril-valsartana-troponina-antraciclina-strain | Valsartana é componente de sacubitrilvalsartana, não droga isolada estudada. |
| valsartana | prada-ii-sacubitril-valsartana-cardiotoxicidade-cancer-mama | Valsartana é componente de sacubitrilvalsartana, não droga isolada estudada. |
| valsartana | sacubitril-valsartana-baixa-dose-prevencao-ctrcd-cancer-mama | Valsartana é componente de sacubitrilvalsartana, não droga isolada estudada. |

## Exclusões de medicamento→evidência

Fonte canônica de cada linha: `evidencias/metadados.json#<evidência>.statement`. Nenhuma contraindicação ou causalidade foi inferida a partir destes registros.

| Medicamento candidato | Evidência canônica | Decisão e razão |
|---|---|---|
| valsartana | arni-preferencial-sobre-ieca-icfer | Valsartana somente como componente ARNI; nó sacubitrilvalsartana é o pertinente. |
| valsartana | betabloqueador-espironolactona-e-sacubitril-valsartana-na-disfuncao-sistolica-por-miocardite | Valsartana somente como componente ARNI; nó sacubitrilvalsartana é o pertinente. |
| valsartana | chagas-icfer-sacubitril-valsartana-em-substituicao-ao-ieca | Valsartana somente como componente ARNI; nó sacubitrilvalsartana é o pertinente. |
| valsartana | chagas-sacubitril-valsartana-para-reduzir-morte-subita | Valsartana somente como componente ARNI; nó sacubitrilvalsartana é o pertinente. |
| adenosina | hrs2015-sincope-marca-passo-em-sincope-adenosina-sensivel-no-idoso | Adenosina-sensível caracteriza mecanismo da síncope; recomendação é dispositivo, não medicamento. |
| adenosina | esc-2021-marca-passo-pode-ser-considerado-na-sincope-sensivel-a-adenosina | Adenosina endógena/sensibilidade é mecanismo, não indicação do fármaco. |
| valsartana | arni-substitui-ieca-na-insuficiencia-cardiaca-com-fracao-de-ejecao-reduzida-sintomatica | Valsartana é apenas componente ARNI. |
| ranolazina | lqts-mexiletina-terapia-genotipo-especifica-no-lqt3 | Ranolazina é comparação histórica; recomendação atual refere-se à mexiletina. |
| finerenona | esc-2026-mra-independente-de-feve | Fonte exige verificação humana da molécula; não inferir finerenona da classe. |
| ticagrelor | host-exam-populacao-coreana-e-desfecho-composto-misto | Ticagrelor não estudado no HOST-EXAM; citação é advertência contra extrapolação. |
| valsartana | sarah-sacubitril-valsartana-troponina-antraciclina-strain-achado-principal | Valsartana apenas componente ARNI; usar nó sacubitrilvalsartana. |
| valsartana | prada-ii-sacubitril-valsartana-cardiotoxicidade-cancer-mama-achado-principal | Valsartana apenas componente ARNI; usar nó sacubitrilvalsartana. |
| valsartana | sacubitril-valsartana-baixa-dose-prevencao-ctrcd-cancer-mama-achado-principal | Valsartana apenas componente ARNI; usar nó sacubitrilvalsartana. |

O caso finerenona→esc-2026-mra-independente-de-feve permanece uma exclusão deliberada de expansão: o próprio enunciado exige VERIFICAÇÃO HUMANA NECESSÁRIA sobre qual molécula corresponde à faixa de fração de ejeção. Esta auditoria não alterou a fonte e não resolveu essa ambiguidade por associação de classe.

## Exclusões de hubs críticos

| Hub | Candidato ou grupo | Razão |
|---|---|---|
| embolia-pulmonar-aguda | tep-hemodinamicamente-estavel-rivaroxabana-isolada-einstein-pe | O par já existe no manifesto explícito; não criar segunda relação para o mesmo alvo apenas mudando o verbo. |
| embolia-pulmonar-aguda | CTEPH isolada / hipertensao arterial pulmonar | Doença crônica ou mecanismo diferente; não expandir por palavra pulmonar. |
| hipertensao-arterial-sistemica | HOPE / HOPE-3 | Coorte de risco cardiovascular sem HAS obrigatória; não promover identidade de doença. |
| hipertensao-arterial-sistemica | Galeria HVE inespecifica | Hipertrofia pode ter etiologias diversas; não preencher artificialmente categoria galeria por inferência. |

## Interações, exames e população

- `medicamentos/interacoes.json#rivaroxabana-digoxina`: a fonte declara ausência de interação farmacocinética. O registro recebeu interaction_present:false. Não produzir interacts_with, alerta leve ou associação artificial para substituir a interação inexistente.
- Digoxina–furosemida não deve ser excluída por uma negação parcial: a ausência de interação farmacocinética não elimina a potencialização farmacodinâmica da toxicidade descrita. A decisão usa marcação estruturada, não detector lexical de negação.
- Dabigatrana não entra no exame anti-Xa calibrado: ela inibe trombina; a fonte nomeia apenas os inibidores de Xa.
- Não estender exame de potássio/creatinina de espironolactona/eplerenona à finerenona apenas por classe.
- Não associar monitorização genérica de amiodarona a ECG ou radiografia pediátrica: população e identidade do exame precisam coincidir.
- Ajmalina, pilsicainida, iloprosta, óxido nítrico e regadenosona foram excluídos do lote exame→medicamento por ausência de nó medicamentoso canônico; não criar nós runtime-only.
- Farmacogenética de rosuvastatina não foi estendida à associação fixa rosuvastatina/ezetimiba. Alternativas dentro de um teste não viram alternative_to geral entre medicamentos.
- Holter de eventos do dispositivo implantado, gravador de alça de sete dias e looper implantável não equivalem a Holter externo de 24h.
- ETE em cardiopatia congênita, dissecção ou ablação não sustenta automaticamente vínculo com o exame específico ETE-endocardite.

## Relações contextuais preservadas, sem promoção indevida

A revisão dos estudos manteve contexto por associated_with para componentes de polipílulas, estratégias combinadas sem contraste isolado, fármaco usado em teste e exposição cujo antídoto foi avaliado. As seis contrarrevisões da primeira tabela seguem essa mesma regra.

A revisão das evidências manteve associated_with para segurança, ajuste de dose, suspensão perioperatória, monitorização, falha/alternativa, resultados de ensaio e recomendações históricas. Em especial, APPRAISE-2, GALILEO, ausência de benefício e evidência insuficiente nunca viraram recommended_by. A prova integral de cada relação aceita está no review_note do manifesto integrado. A referência negativa não foi convertida em contraindicated_in ou may_cause.

As referências históricas ESC2015 de colchicina foram ligadas apenas como contexto quando pertinentes, preservando distinção da fonte editorial ESC2025. Nomes genéricos de classes não geraram expansão para todos os integrantes. Documento→supported_by→evidência e evidência→supported_by→estudo mantêm a direção verbal correta; não inverter essas arestas.

## Jornadas, documentos e navegação

- 133 entradas EmergencyProtocol.relacionados já são cobertas pelo mecanismo público apropriado. Não duplicá-las nem liberar genericamente associated_with pendente.
- 3.391 etapas de trilhas já representam contains. Não tratá-las como novas relações para inflar o lote.
- Opções incorretas, explicações e menções narrativas de casos clínicos não comprovam medicamento/calculadora used_in_case. Não criar relações fortes para alternativas de resposta.
- default_tests e emergency_flow de triagem são prosa: não converter automaticamente em diagnosed_by ou treats. Primeiro é necessária declaração canônica tipada e contextual quando não houver identificação inequívoca.
- Links explícitos de documentos para calculadoras geram mentioned_in. Não geram monitor_with, diagnosed_by ou indicated_for por si só.
- URLs externas, caminhos com travessia, segmentos extras e slugs vazios são rejeitados pelo resolvedor de links clínicos. Referência quebrada deve ser relatada, não resolvida inventando nó.
- Não gerar arestas inversas redundantes; o grafo consulta entrada e saída.

## Galeria e duplicidade

Não há slug nem file_path duplicado na galeria inspecionada. Seis URLs de origem são compartilhadas por pares: três apontam ao mesmo arquivo Wikimedia (FA de duas derivações, peça de vegetação, ventriculografia de Takotsubo) e três a artigos PMC com figuras/modalidades distintas. Compartilhar fonte não comprova duplicação de nó nem relação clínica entre imagens. Nada foi apagado para reduzir artificialmente contagens.

## Exclusões anteriores que permanecem válidas

Os dois falsos positivos de CIV certificados continuam fora de expansão por identidade lexical: CIV adquirida pós-IAM e atresia pulmonar/TOF com CIV anatômica. Os sete candidatos corvia-intelligence-* runtime-only anteriormente rejeitados permanecem fora do grafo clínico persistente; este documento não inventa os sete slugs não enumerados no pedido de retomada. Conteúdo pendente do Grok e PRs em revisão separada não integram esta autorização.

## Limites e fontes no repositório

A triagem nominal percorreu os 2.061 resumos de estudos e 3.363 enunciados de evidências contra generic_name completo e todos os candidatos encontrados tiveram decisão contextual. A cobertura declarada não é prova de exaustão universal de marcas, abreviações, traduções, nomes sem sal ou toda prosa clínica. As exclusões não mudam contagens ou status editoriais e não certificam produção.

A publicação, retirada de arestas automáticas antigas, deduplicação persistida, gates integrais e reprodução pública dependem do reconcile e dos testes runtime documentados pela coordenação. Não interpretar tabela de decisões locais como confirmação de deploy.

Fontes de apoio presentes neste repositório:

- `doencas/relacoes-transversais.json`: relações aceitas, verbos finais e provas completas.
- `doencas/relacoes-explicitas.json`: vínculos dos hubs e camada doença→conteúdo preservada.
- `estudos/metadados.json`, `evidencias/metadados.json`, `medicamentos/metadados.json`, `medicamentos/interacoes.json`, `exames/metadados.json` e `galeria/metadados.json`: identidades e afirmações canônicas.
- `docs/auditoria-transversal-evidencias-estudos-20260908.md`, `docs/auditoria-transversal-medicamentos-exames-20260908.md` e `docs/auditoria-transversal-ferramentas-jornadas-20260908.md`: escopos, decisões dos agentes e limitações específicas.
