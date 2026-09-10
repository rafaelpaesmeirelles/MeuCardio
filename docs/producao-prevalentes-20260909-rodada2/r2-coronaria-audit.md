# Rodada 2 — Doença coronariana

Base indicada pelo coordenador: main `cb750689b94f7888b18133e68ff8293bff55d742`. Lidos os quatro documentos da primeira rodada e `production/notes/audit-coronaria.md`; pesquisados integralmente os catálogos atuais: 915 casos, 448 materiais e 473 checklists. Consultas por título/slug: coronária, angina, SCA, infarto, dor torácica, reconciliação, consulta, discordância, inconclusivo, ANOCA/INOCA.

## Gaps e entregas novas

- Caso básico `dor-toracica-estavel-teste-interrompido-por-gonalgia-proxima-decisao`: interpretação da conclusão completa de um teste interrompido, probabilidade clínica e próxima pergunta; complementa SCOT-HEART/Duke/ANOCA existentes sem repetir pergunta sobre efeito de ensaio.
- Caso avançado `primeiro-retorno-pos-sca-dois-p2y12-dispneia-e-receitas-conflitantes`: discrepância entre receita preliminar e definitiva, confirmação ativa com hemodinâmica, retirada médica de duplicação clopidogrel/ticagrelor e atribuição criteriosa de dispneia. Não repete prazo genérico DAPT/AUGUSTUS.
- Material `primeiro-retorno-apos-infarto-leve-remedios-receitas-e-duvidas`: preparação concreta da sacola/lista, acesso, compreensão e contato; distinto de doença coronariana, vida pós-infarto e explicação de DAPT já existentes.
- Checklist `primeiro-retorno-pos-sca-fechamento-de-divergencias-e-pendencias`: consulta após alta, erro ativo resolvido, pendências com pessoa/prazo, solicitação de exames condicionada. Não substitui checklist de alta ou de duração de DAPT.

Todos os dados de casos são fictícios. Quatro alternativas e resposta base zero. Explicação de cada alternativa. Schema replicado dos respectivos catálogos; novos registros sem `published: true`, com `review_status: pendente_revisao`. Sem atribuição de revisão humana.

## Duas correções legadas autorizadas durante a rodada

Arquivos separados com registro completo preservando slug e campo de ligação:

1. `casos-clinicos-corrections.json`: `angina-persistente-coronarias-normais-anoca-inoca-endotipo`. Correção do endótipo espástico: considerar bloqueador de canal de cálcio inicialmente, em vez de desviar automaticamente para IECA/ranolazina. Separado de disfunção microvascular por CFR/IMR alterados. Removida classe I/B genericamente atribuída a toda avaliação invasiva após teste inconclusivo, que não foi confirmada em fonte primária. Dados e explicações completados. Fonte primária de consenso EAPCI/COVADIS, não artigo de comentário.
2. `material-paciente-corrections.json`: `por-que-tomar-dois-remedios-para-o-sangue-depois-do-infarto-ou-stent`. Removidos proibição universal de qualquer redução nos primeiros 30 dias e declaração de única recomendação de maior grau. Explicitados cenário SCA sem alto risco hemorrágico e alternativa quando há anticoagulação concomitante. Retirados números de estudos não revalidados nesta rodada; simplificado texto para paciente e mantido documento_slug original. Não são instruções para suspensão autônoma.

## Fontes verificadas e limites

Consultadas em 09/09/2026:

- ESC SCC 2024, portal primário: https://www.escardio.org/guidelines/clinical-practice-guidelines/all-esc-practice-guidelines/chronic-coronary-syndromes/ — probabilidade ponderada por fatores de risco e ANOCA/INOCA. Acesso ao artigo EHJ retornou erro; não afirmada leitura integral.
- AHA/ACC 2021, slide set oficial: https://professional.heart.org/-/media/PHD-Files-2/Science-News/2/2021/2021-Chest-Pain-Guideline-Slide-Set-PDF-102821.pdf — página numerada 97, CCTA após teste inconclusivo no paciente estável de risco intermediário-alto (IIa B-NR). Classe limitada a essa recomendação/população.
- AHA/ACC SCA 2025, síntese oficial: https://professional.heart.org/en/science-news/2025-guideline-for-the-management-of-patients-with-acute-coronary-syndromes/top-things-to-know — combinação, alternativas para anticoagulação concomitante, retorno lipídico e reabilitação. Não transcrito quadro de classes.
- FDA ticagrelor, documento específico revisão 03/2024: https://www.accessdata.fda.gov/drugsatfda_docs/label/2024/022433s035lbl.pdf — 2.1 proíbe outro P2Y12 oral concomitante; 5.3 dispneia, tolerabilidade e alternativa se interrupção necessária. Não apresentado como última bula brasileira.
- EAPCI/COVADIS, consenso original em EuroIntervention: https://pmc.ncbi.nlm.nih.gov/articles/PMC9707543/ — seção Antianginal medication e Tabela 4 item 13: antagonista de cálcio inicialmente no espasmo microvascular; mecanismo de remodelamento é distinto. DOI 10.4244/EIJY20M07_01.
- Ministério da Saúde, SAMU: https://www.gov.br/saude/pt-br/composicao/saes/samu-192 — número, sinais de infarto/AVC e emergências cardiorrespiratórias.

Sem transcrição literal de tabelas/figuras. Perguntas, casos, sacola e fluxo de fechamento são construções didáticas próprias; não são instrumentos validados. Afirmações derivadas distribuídas entre fontes, sem reprodução extensa. Não foi necessário usar definição universal de IAM ou cortes de hs-cTn nesta rodada.

## Tudo com Tudo — integração solicitada ao coordenador

Vínculos centrais bidirecionais propostos:

- Caso básico ↔ documento `suspeita-de-doenca-coronariana-primeira-consulta-do-sintoma-a-decisao` ↔ documento `dor-toracica-exames-discordantes-reavaliacao-e-destino-seguro`; recurso exame `angiotomografia-de-coronarias`; doença `sindrome-coronariana-cronica`.
- Caso avançado, checklist e material novos ↔ documento `primeiro-retorno-pos-sca-conciliacao-antitrombotica-e-intercorrencias`; doença `sindrome-coronariana-aguda`; farmacologia AAS, ticagrelor e clopidogrel conforme os slugs canônicos conferidos na base.
- Os quatro novos recursos ↔ trilha `trilha-consulta-progressiva-doenca-coronariana`, progressão básico → decisões discordantes → primeiro retorno/intercorrências.
- Caso ANOCA corrigido ↔ primeira consulta; manter relações existentes do slug preservado. Material DAPT corrigido mantém `documento_slug: sindrome-coronariana-aguda-duracao-de-dapt-complemento-final`.

Links dentro dos casos usam rotas existentes `/biblioteca`, `/exames`, `/trilhas`, `/checklists`, `/material-paciente`; referências centrais de origem pertencem à primeira rodada. A atualização do grafo e das trilhas pertence ao coordenador; links Markdown isolados não demonstram grafo atualizado em produção.

Sem commit, push, merge, banco ou deploy nesta frente.

## Correção adicional do documento canônico DAPT

Por solicitação posterior do coordenador, arquivo atual obtido diretamente pelo conector GitHub na main fixada acima, blob `22676a955720beeaec19959635556b72d53f2964`. Original disponível para comparação em `round2-base/dapt-upstream-original.md`. Correção em `round2/content/Doença_coronariana/sindrome-coronariana-aguda-duracao-de-dapt-complemento-final.md`, preservando slug e origem legada.

Removidos: afirmação de única Classe I, limite máximo de um ano contradito no próprio texto, NNT/NNH genéricos reunindo DAPT/PEGASUS, faixa HBR 1–6 meses sem seleção e algoritmo que impunha monoterapia a todo risco duplo. Diferenciados cenário de anticoagulação prolongada, pós-ICP, ICP eletiva/SCC e outras estratégias de SCA. Reavaliação clínica não foi substituída por escore. Texto reconectado a material, caso e checklist da rodada.

Fontes primárias adicionais efetivamente consultadas: PRECISE-DAPT PMID 28290994 (componentes, derivação predominantemente AAS/clopidogrel sem ACO); MASTER DAPT PMID 34449185 (abstract obtido com `?dopt=Abstract`), mantendo 6,5% vs 9,4%, diferença e IC95%, distinguindo não inferioridade de ausência de todo risco isquêmico; OPT-BIRISK PMID 38630489, mantendo 2,5% vs 3,3% com seleção e horizonte. Encontrados e corrigidos **mais dois erros bibliográficos/estatísticos** no legado OPT-BIRISK: primeiro autor é **Li Y**, e o efeito 0,75 é **HR**, não RR. Acrescentados período sem eventos de pelo menos seis meses e nove meses de comparação após 9–12 de DAPT.

Resumos DAPT/PEGASUS tiveram acesso oscilante/vazio e não foram usados para novas magnitudes de benefício. FDA ticagrelor seção 2.2 confirma existência de regimes após um ano, explicitamente sem transformar bula em recomendação universal de prolongamento. Não se declara leitura integral da diretriz ACC/AHA 2025; síntese oficial sustenta referência e cenário ACO. Cada resumo de ensaio recebeu paráfrase curta própria, sem copiar tabelas. Registro `pendente_revisao`; encaminhado ao agente valvas/síncope para revisão independente.
