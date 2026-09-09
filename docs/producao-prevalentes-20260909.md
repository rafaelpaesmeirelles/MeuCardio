# Produção cardiovascular prevalente — 09/09/2026

Base GitHub: `64796aa973316c94b47dcf8dc75a474415ecba34`. Produção original orientada a lacunas práticas; seis frentes autorais e revisão cruzada independente entre agentes, com consolidação pelo coordenador. Não houve revisão humana independente.

## Entrega

18 documentos novos, sete documentos existentes corrigidos, oito trilhas progressivas (49 etapas), 81 relações explícitas novas e complementos de documentos em 11 doenças. A validação local resolveu 359 links internos. Preservados os valores das 555 trilhas e 3.054 relações anteriores.

## Correções científicas consolidadas

- HAS: diagnóstico exige confirmação contextual, sem usar DCV isolada como prova; emergência definida por lesão aguda; resistência exige classes/doses/adesão e medida fora do consultório; segurança de ARM com K/função renal.
- IC: ESC 2026 conferida em fonte oficial, distinção entre nova nomenclatura e populações dos ensaios, seleção CDI, limites LVAD/ICFEp e manutenção da terapia após recuperação da FEVE.
- FA: diferenças ESC/AHA delimitadas; dose renal por fármaco e jurisdição; elegibilidade valvar e hepática antes da tabela de DOAC.
- Coronárias: individualização de teste, sem adiamento obrigatório; disfunção ventricular não encerra investigação etiológica de DAC.
- Lipídios: meta ESC abaixo de 40 não cria automaticamente nova categoria; inclisirana diferenciada de anticorpos com desfechos; conduta ALT e contexto ApoB refinados.
- Síncope: correção da direção da associação tilt/recorrência após MP e separação entre razão E/I e variação de FC em bpm.

## Percursos e integração

| Frente | Novos | Corrigidos | Foco |
|---|---:|---:|---|
| Hipertensão | 3 | 1 | Primeira consulta, edema/BCC, hipocalemia/renina |
| Insuficiência cardíaca | 3 | 2 | Diagnóstico, segurança, transição pós-alta |
| FA e arritmias | 3 | 1 | Consulta, anticoagulação, palpitações |
| Doença coronariana | 3 | 1 | Suspeita estável, discordância, retorno após SCA |
| Prevenção/lipídios e DM2 | 3 | 1 | Lipidograma, intensificação, consulta cardiometabólica |
| Valvopatias e síncope | 3 | 1 | EA/IM, recorrência pós-MP |

Links clínicos apontam para rotas reais do aplicativo: Biblioteca, doenças, exames, medicamentos, calculadoras, estudos, casos, materiais, checklists, galeria e trilhas. URLs de medicamentos usam `?slug=`, conforme o componente atual. Os vínculos não significam indicação automática de exame, fármaco ou intervenção.

## Validação e rastreabilidade

Frontmatter, slugs, destinos de links, estágios das trilhas e composição das doenças conferidos. Executado o carregador canônico `load_disease_records` com a correção nova sobre a base atual. Nenhum erro encontrado nessas validações. Detalhes quantitativos em [validação](producao-prevalentes-20260909-validacao.json).

Fontes, acessos que falharam e pareceres por frente estão na pasta [registros de revisão](producao-prevalentes-20260909/). Os registros autorais descrevem o estado antes da consolidação; correções solicitadas nas revisões cruzadas foram aplicadas nos arquivos finais. Não foram inventados PMIDs para fontes regulatórias/institucionais que não os possuem.

## Limites e sequência de trabalho

Este lote reforça a cobertura operacional e não certifica que todas as patologias prevalentes estejam completamente cobertas. Uma auditoria por domínio ainda deve conferir todos os critérios de diagnóstico, seguimento, populações especiais, urgências e materiais ao paciente de cada núcleo. A leitura integral de todas as fontes e do corpus histórico não foi realizada. Alguns textos completos SBC/OUP tiveram acesso indisponível; essas limitações foram preservadas nas notas, e recomendações novas não foram atribuídas a fontes não lidas.

Não foram executados importação em produção, promoção editorial no banco, reconciliação do grafo em produção ou deploy. A carga de registros novos no sistema não equivale automaticamente à publicação, conforme contrato existente. A navegação foi validada contra arquivos/rotas/IDs atuais; não foi certificada em sessão autenticada do site.

Próxima frente sugerida para continuidade autônoma: auditar os núcleos basais de cada doença em ordem de prevalência, corrigir contradições remanescentes e completar materiais/checklists/casos conforme lacunas confirmadas, com fontes primárias e sem duplicar os 18 novos protocolos.

## Arquivos científicos deste lote

- Novo: [palpitacoes-monitorizacao-e-correlacao-entre-sintoma-e-ritmo](../content/Arritmias/palpitacoes-monitorizacao-e-correlacao-entre-sintoma-e-ritmo.md)
- Novo: [consulta-cardiometabolica-no-dm2-avaliacao-inicial-e-plano-longitudinal](../content/Diabetes_e_cardiologia/consulta-cardiometabolica-no-dm2-avaliacao-inicial-e-plano-longitudinal.md)
- Novo: [dor-toracica-exames-discordantes-reavaliacao-e-destino-seguro](../content/Doença_coronariana/dor-toracica-exames-discordantes-reavaliacao-e-destino-seguro.md)
- Corrigido: [fluxograma-sindrome-coronariana-cronica-esc-2024](../content/Doença_coronariana/fluxograma-sindrome-coronariana-cronica-esc-2024.md)
- Novo: [primeiro-retorno-pos-sca-conciliacao-antitrombotica-e-intercorrencias](../content/Doença_coronariana/primeiro-retorno-pos-sca-conciliacao-antitrombotica-e-intercorrencias.md)
- Novo: [suspeita-de-doenca-coronariana-primeira-consulta-do-sintoma-a-decisao](../content/Doença_coronariana/suspeita-de-doenca-coronariana-primeira-consulta-do-sintoma-a-decisao.md)
- Novo: [anticoagulacao-na-fa-reconciliacao-de-dose-funcao-renal-e-interacoes](../content/Fibrilação_atrial/anticoagulacao-na-fa-reconciliacao-de-dose-funcao-renal-e-interacoes.md)
- Corrigido: [fibrilacao-atrial-diagnostico-e-manejo-esc-2024-via-af-care](../content/Fibrilação_atrial/fibrilacao-atrial-diagnostico-e-manejo-esc-2024-via-af-care.md)
- Novo: [fibrilacao-atrial-primeira-consulta-plano-longitudinal-e-retorno](../content/Fibrilação_atrial/fibrilacao-atrial-primeira-consulta-plano-longitudinal-e-retorno.md)
- Novo: [edema-no-hipertenso-em-uso-de-bcc-avaliacao-e-represcricao](../content/Hipertensão/edema-no-hipertenso-em-uso-de-bcc-avaliacao-e-represcricao.md)
- Corrigido: [hipertensao-arterial-classificacao-diagnostico-metas](../content/Hipertensão/hipertensao-arterial-classificacao-diagnostico-metas.md)
- Novo: [hipertensao-hipocalemia-e-renina-alta-interpretacao-sem-atalhos](../content/Hipertensão/hipertensao-hipocalemia-e-renina-alta-interpretacao-sem-atalhos.md)
- Novo: [hipertensao-primeira-consulta-plano-longitudinal-e-retorno-seguro](../content/Hipertensão/hipertensao-primeira-consulta-plano-longitudinal-e-retorno-seguro.md)
- Novo: [ic-primeira-consulta-dispneia-confirmacao-e-etiologia](../content/Insuficiência_cardíaca/ic-primeira-consulta-dispneia-confirmacao-e-etiologia.md)
- Novo: [ic-terapia-fundacional-seguranca-renal-potassio-e-hipotensao](../content/Insuficiência_cardíaca/ic-terapia-fundacional-seguranca-renal-potassio-e-hipotensao.md)
- Novo: [ic-transicao-pos-alta-plano-primeiras-seis-semanas](../content/Insuficiência_cardíaca/ic-transicao-pos-alta-plano-primeiras-seis-semanas.md)
- Corrigido: [icfep-diagnostico-e-terapias-avancadas-lvad-e-transplante](../content/Insuficiência_cardíaca/icfep-diagnostico-e-terapias-avancadas-lvad-e-transplante.md)
- Corrigido: [icfer-classificacao-diagnostico-quatro-pilares](../content/Insuficiência_cardíaca/icfer-classificacao-diagnostico-quatro-pilares.md)
- Corrigido: [dislipidemia-metas-ldl-estratificacao-risco-esc-eas-2025](../content/Prevenção_e_lipídios/dislipidemia-metas-ldl-estratificacao-risco-esc-eas-2025.md)
- Novo: [lipidograma-na-consulta-primeira-leitura-discordancia-e-decisao-clinica](../content/Prevenção_e_lipídios/lipidograma-na-consulta-primeira-leitura-discordancia-e-decisao-clinica.md)
- Novo: [retorno-da-dislipidemia-resposta-insuficiente-seguranca-e-intensificacao](../content/Prevenção_e_lipídios/retorno-da-dislipidemia-resposta-insuficiente-seguranca-e-intensificacao.md)
- Corrigido: [sincope-diagnostico-e-manejo-esc-2018](../content/Síncope/sincope-diagnostico-e-manejo-esc-2018.md)
- Novo: [sincope-recorrente-apos-marca-passo-interpretacao-do-tilt-e-reavaliacao](../content/Síncope/sincope-recorrente-apos-marca-passo-interpretacao-do-tilt-e-reavaliacao.md)
- Novo: [estenose-aortica-do-laudo-discordante-a-consulta-longitudinal](../content/Valvopatias/estenose-aortica-do-laudo-discordante-a-consulta-longitudinal.md)
- Novo: [insuficiencia-mitral-leitura-critica-do-laudo-e-preparo-da-decisao](../content/Valvopatias/insuficiencia-mitral-leitura-critica-do-laudo-e-preparo-da-decisao.md)
