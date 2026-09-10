# Frente fibrilação atrial e arritmias comuns — 09/09/2026

Base atual examinada: GitHub main `64796aa973316c94b47dcf8dc75a474415ecba34`. Conferidos diretamente os documentos centrais AF-CARE, dose de DOAC e cardioversão eletiva. Corpus anterior consultado somente para identificação preliminar; exames/doenças/trilhas conferidos nos metadados atuais disponibilizados em `base/`.

## Entregas

1. Novo protocolo `fibrilacao-atrial-primeira-consulta-plano-longitudinal-e-retorno`: execução da primeira consulta e retorno, objetivos verificáveis, controle de frequência versus ritmo com EAST-AFNET4/RACEII, caso didático.
2. Novo protocolo `anticoagulacao-na-fa-reconciliacao-de-dose-funcao-renal-e-interacoes`: reconciliação prática, cálculo CG, doses com jurisdição EMA explicitada, interações, exemplo calculado; não rotulado como bula brasileira.
3. Novo protocolo `palpitacoes-monitorizacao-e-correlacao-entre-sintoma-e-ritmo`: lacuna entre solicitar monitor e interpretar resultado, quatro situações de correlação, diário e caso fictício.
4. Correção pontual `fibrilacao-atrial-diagnostico-e-manejo-esc-2024-via-af-care`: VASc não considerado universalmente errado; janela 48h delimitada à ACC/AHA2023; fonte primária e links acrescentados. Restante preservado, sem alegação de revisão integral.

Status dos quatro arquivos: `pendente_revisao`, com nota explícita de produção assistida por IA e ausência de revisão humana. Sem commit, push ou deploy.

## Fontes efetivamente acessíveis e conferidas

- ACC/AHA/ACCP/HRS 2023: https://pmc.ncbi.nlm.nih.gov/articles/PMC11104284/ — texto integral, diagnóstico inicial, limiares VASc, recomendações de cardioversão e anticoagulação; seções 6.3.1 e 8.2.1.
- EAST-AFNET4: https://pubmed.ncbi.nlm.nih.gov/32865375/ — resumo primário; população e HR 0,79 IC96% 0,66–0,94.
- RACEII: https://pubmed.ncbi.nlm.nih.gov/20231232/ — resumo primário; alvo leniente <110 e não inferioridade no cenário de FA permanente.
- Raviele et al., EHRA 2011: https://academic.oup.com/europace/article/13/7/920/447426 — texto integral aberto. Fonte de consenso para palpitações; natureza da evidência explicitada, sem inventar classe de recomendação.
- RCMs EMA Eliquis/Xarelto/Lixiana/Pradaxa: PDFs oficiais abertos. Conferência de apixabana CrCl 15–29 e critérios de dose; rivaroxabana 15 mg CrCl 15–49; edoxabana 30 mg por um critério; dabigatrana 110/150 e restrição renal.

Síntese original, sem citações extensas. Casos e estruturas de prontuário são editoriais, identificados como didáticos/operacionais. Não foi atribuída classe de diretriz a sugestões editoriais de intervalo de retorno.

## Alertas do acervo atual

- Documento atual `cardioversao-eletiva-e-anticoagulacao-periprocedimento-esc-2024` afirma quatro semanas “sem exceção”. Exceção ESC de FA <24h sem fatores precisa confirmação no texto/figura primária antes de editar. OUP ESC2024 falhou reiteradamente; slide set oficial foi identificado, mas não baixado por restrição da rede. Por orientação do root, NÃO modifiquei este arquivo sem fonte primária acessível. A ACC/AHA2023 confirma sua própria incerteza em VASc 0–1 e duração <12h, que não deve ser transferida para a ESC.
- Fluxograma atual de DOAC mistura ramos regulatórios: em CrCl15–29 a figura diz apixabana “regra 2 de 3”, ao mesmo tempo que cita EMA; EMA tem redução própria nessa faixa. O novo protocolo explicita jurisdição e a diferença, mas o fluxograma antigo merece revisão regulatória brasileira integral antes de mudança. Evitar aplicar proibição americana de edoxabana CrCl>95 como regra europeia universal.

## Identificadores para integração central Tudo com Tudo

Doença atual: `fibrilacao-atrial`.

Calculadoras/documentos existentes: `cha2ds2-va`, `has-bled`, `clearance-de-creatinina-cockcroft-gault-ajuste-de-dose-em-cardiologia`.

Exames atuais confirmados em `base/exames/metadados.json`: `holter-24h`, `holter-ou-monitor-externo-prolongado-no-diagnostico-de-fa-paroxistica`, `monitor-de-eventos-implantavel-looper-em-palpitacoes-inexplicadas`. Demais slugs de ETE/CG/TSH localizados também no corpus anterior; conferir no base antes de promover relações.

Trilhas atuais confirmadas: `trilha-fibrilacao-atrial-reconhecimento-inicial`, `trilha-calculadoras-ajuste-renal-de-dose-e-escores-de-fibrilacao-atrial`.

Paciente e casos no corpus anterior: `fibrilacao-atrial-entendendo-o-plano-de-tratamento-af-care`, `has-bled-alto-e-motivo-para-nao-anticoagular`; root deverá conferir metadados atuais se usá-los na relação explícita.

Todos os links relativos dos novos documentos foram resolvidos contra a árvore atual e os novos arquivos: zero caminhos ausentes. Links JSON servem como âncora de fonte no repositório, com slug indicado; o root fará conversão para rotas funcionais do produto e relações explícitas.
