# Segunda rodada — HAS — 09/09/2026

Base informada pela coordenação: main cb750689b94f7888b18133e68ff8293bff55d742. Quatro documentos de production/content/Hipertensão lidos; nenhuma edição na rodada 1. Catálogos completos carregados (915 casos, 448 materiais; checklist integral carregado), com busca de títulos/temas e leitura das entradas próximas. Os artefatos são fragmentos de trabalho de projeto versionado e serão integrados pela coordenação; nenhum commit, push ou publicação executado nesta frente.

## Entregas

- has/casos-clinicos.json: 2 casos fictícios, 4 alternativas cada, índices base zero 2 e 3. Primeiro: descontrole sustentado com uso incompleto por intolerância. Segundo: hipocalemia prévia ao diurético e ARR negativa sob interferentes, sem declarar diagnóstico ou exclusão indevida.
- has/material-paciente.json: 1 material sobre transição de receitas, observação e preparação do retorno após troca.
- has/checklists.json: 1 checklist de fechamento da consulta após represcrição; 10 itens com IDs exclusivos.
- has/checklists-corrections.json: 1 entrada legada completa corrigida, preservando slug, para substituição focal pela coordenação. Alterações em resumo, 5 itens, fontes e nota.

Todos permanecem pendente_revisao, sem published:true e sem declaração de revisão humana. Esquemas de chaves das entradas novas comparados com a primeira entrada dos respectivos catálogos: exatos. Slugs novos confrontados com o catálogo integral: sem colisão. Não foi alegado diagnóstico real, uso de marca superior nem benefício causal de uma troca múltipla.

## Lacunas discriminadas

O caso existente cascata-de-prescricao-edema-por-bloqueador-de-canal-de-calcio-tratado-com-diuretico ensina reconhecer cascata geriátrica. O novo ensina separar PA externa elevada de comprovação de adesão e transformar a consulta em plano executável. O caso existente rastreio-de-aldosteronismo-em-hipertensao-resistente-sem-hipopotassemia ensina indicação de ARR; o novo interpreta resultado aparentemente negativo com interferentes e hipocalemia prévia. Não reproduzem o objetivo avaliativo.

Materiais existentes hipertensao-arterial, minha-pressao-nao-baixa-mesmo-com-os-remedios-certos e como-medir-minha-pressao-em-casa-corretamente cobrem conceitos/medição/resistência. A nova folha organiza a transição entre prescrição anterior e atual. Checklists existentes de primeira linha/diagnóstico/resistência não fecham especificamente a transição após intolerância, com teach-back, responsável por exames e acesso à nova receita.

A correção legada foi solicitada pela coordenação após alerta desta frente. O checklist confirmacao-de-hipertensao-resistente-verdadeira-antes-de-escalonar postergava investigação secundária até falha da quarta droga e afastava investigação diante de avental branco mesmo com pistas independentes. Também apresentava diurético de alça como regra para TFG genericamente reduzida. As frases foram substituídas por decisões condicionais e investigação paralela. O documento de origem pode repetir essas formulações: precisa da conferência da coordenação; não foi disponibilizado integralmente nesta frente, nem modificado.

## Fontes primárias verificadas

- AHA 2018, síntese oficial de Resistant Hypertension: https://professional.heart.org/en/science-news/resistant-hypertension-detection-evaluation-and-management/top-things-to-know — definição, adesão, aferição, avaliação; statement, sem atribuir uma classe própria ao checklist.
- AHA/ACC 2025, síntese oficial: https://professional.heart.org/en/science-news/2025-high-blood-pressure-guideline/top-things-to-know — acesso, cuidado em equipe, simplificação e medidas domiciliares. Não importada classificação norte-americana como brasileira.
- Endocrine Society 2025, recomendação 3 e observações: https://www.endocrine.org/clinical-practice-guidelines/primary-aldosteronism-2 — recomendação condicional/baixa certeza. Rastreio negativo sob interferência não tratado como exclusão definitiva. Nenhuma instrução universal de washout.
- AHA, Home Blood Pressure Monitoring: https://www.heart.org/en/health-topics/high-blood-pressure/understanding-blood-pressure-readings/monitoring-your-blood-pressure-at-home — seguimento e ausência de suspensão autônoma.
- NHS SPS, atualização 26/05/2026: https://sps.nhs.uk/articles/managing-peripheral-oedema-caused-by-calcium-channel-blockers/ — tolerabilidade e edema associado a BCC; serviço oficial de medicamentos, usado como suporte farmacológico, não RCT de superioridade.

Sem transcrição de trechos. Casos, cenários e organização operacional são originais. Não acrescentados DOI/PMID não conferidos. Acesso ao texto completo ESC via OUP falhou e busca adicional não trouxe fonte primária útil; nada foi atribuído à ESC por memória. WHO consultada, mas sem uso material nas entregas.

## Tudo com Tudo — mapa explícito para integração

Usar os nós abaixo com relações contextuais e recíprocas na camada suportada pelo projeto. Campos extras não foram inventados nos schemas. Este mapa não afirma que links já estejam publicados ou que o grafo em produção tenha sido testado.

| Tipo | Slug verificado | Aplicação |
|---|---|---|
| Doença | hipertensao-arterial-sistemica | Ambos os casos, material e checklist |
| Documento | hipertensao-primeira-consulta-plano-longitudinal-e-retorno-seguro | Caso 1; documento_slug material; documento_origem checklist |
| Documento | edema-no-hipertenso-em-uso-de-bcc-avaliacao-e-represcricao | Caso 1 e material |
| Documento | hipertensao-hipocalemia-e-renina-alta-interpretacao-sem-atalhos | Caso 2; item condicional de hipocalemia do checklist |
| Documento | hipertensao-resistente-verdadeira-versus-pseudorresistente-tecnica-adesao-avental-branco | Caso 1, diagnóstico diferencial; checklist legado |
| Documento | hipertensao-arterial-classificacao-diagnostico-metas | Base longitudinal |
| Calculadora | ckd-epi-2021 | Segurança renal no caso 2 e monitoramento indicado; não calcula ARR nem confirma resistência |
| Exame | mapa-monitorizacao-ambulatorial-pressao-arterial | Ambos os casos e checklist |
| Exame | mrpa-monitorizacao-residencial-da-pressao-arterial | Material/checklist e monitoramento após ajuste |
| Exame | potassio-serico-risco-arritmico-e-monitorizacao | Caso 2 e segurança após ajuste |
| Trilha | trilha-consulta-progressiva-hipertensao | Inserir caso 1 após consulta/edema, caso 2 após hipocalemia; folha e checklist como aplicações práticas |
| Medicamento | olmesartana-medoxomila | Caso 2, interpretação de exposição farmacológica |
| Medicamento | anlodipino-besilato | Caso 1, tolerabilidade |
| Material existente | hipertensao-arterial | Introdução do paciente antes da nova folha de transição |

Verificação dos nós: documentos da rodada 1 e round2-paths.txt; doença/exames em base/*/metadados.json; calculadora em base/backend/app/services/calculators.py; trilha em production/trilhas/metadados.json. Revalidação final de nós contra SHA atual cabe à integração, pois parte dos catálogos auxiliares é da base anterior. Não há necessidade de ligar todos os nós indiscriminadamente: o vínculo deve conservar a pergunta clínica.

## Limites e revisão cruzada

Solicitar revisão cruzada de suficiência clínica dos dois casos, foco no ECG normal não excluir risco eletrolítico, índices base zero e ausência de equivalência entre descontrole e resistência. Hipocalemia exige conduta clínica paralela: a questão não substitui protocolo de reposição. Nenhuma dose de reposição foi inventada. A correção focal legada preserva fontes históricas não relidas integralmente; a nota explicita seu alcance. Nenhuma alegação de cobertura integral da HAS ou de revisão humana.

## Complemento autorizado — documento de origem

Arquivo upstream obtido pelo plugin GitHub no commit cb750689b94f7888b18133e68ff8293bff55d742: content/Hipertensão/hipertensao-resistente-verdadeira-versus-pseudorresistente-tecnica-adesao-avental-branco.md; blob SHA 6b1641e64bf7373150ac7be4dab90d7957c38f05. Cópia temporária de comparação: round2-base/has-pseudorresistencia-upstream.md. O documento repetia e ampliava o erro conhecido do checklist.

Versão corrigida: round2/content/Hipertensão/hipertensao-resistente-verdadeira-versus-pseudorresistente-tecnica-adesao-avental-branco.md. Diff auditável: round2/notes/r2-has-upstream.diff.

Correção focal tornou explícita a investigação secundária paralela quando indicada; retirou espera por falha da quarta droga; retirou a classificação automática de dados não verificados como pseudorresistência; condicionou estratégia diurética à função renal e ao volume, sem a regra indiscriminada de alça para qualquer TFG reduzida. Ajustados introdução, títulos e armadilhas que contradiziam essas correções. O marcador genérico de verificação humana foi convertido em limitação metodológica explícita: não somar percentuais de coortes distintas; não se inventou estimativa combinada nem se alegou revisão humana. Recomendação de rastreio atribuída à Endocrine Society 2025; referência AHA2018 adicionada com URL oficial. Status pendente_revisao.

Mantidos os parágrafos quantitativos dos estudos históricos, sem certificar revisão integral deles. Em particular, a redação sobre Jung apresenta 108 elegíveis e 40 (53%) detectados; requer conferência do denominador efetivamente submetido à triagem antes de uma futura revisão quantitativa integral. Este complemento não reescreve o documento inteiro nem converte fontes históricas não verificadas em referências certificadas. Requer revisão cruzada da coordenação antes de mudar status.
