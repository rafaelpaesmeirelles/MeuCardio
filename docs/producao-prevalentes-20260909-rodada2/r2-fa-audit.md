# Rodada 2 — FA e arritmias comuns — 09/09/2026

## Base e gaps verificados

Base indicada pelo coordenador: main `cb750689b94f7888b18133e68ff8293bff55d742`. Consultados os três catálogos atuais em `round2-base/`, os quatro documentos de `production/content/{Arritmias,Fibrilação_atrial}` e `production/notes/audit-fa.md`.

1. **Correlação parcial**: o catálogo contém casos de extrassístoles e muitos ensaios de arritmias, porém não um exercício distinguindo duas queixas na mesma pessoa, com captura de apenas uma delas. Criado caso básico com falhas breves registradas e crises prolongadas não capturadas. Não repete literalmente o caso didático do protocolo, que descreve ausência total do sintoma-alvo.
2. **Adesão real antes de cardioversão**: existe checklist pré-cardioversão e casos de FA no pronto-socorro. Faltava caso decisório sobre revelar omissões do DOAC no dia de procedimento eletivo em paciente estável, sem imagem disponível. Não repete cálculo de apixabana renal nem o caso de doença coronariana crônica/AQUATIC já encontrado no catálogo.
3. **Participação do paciente no exame**: havia material sobre extrassístoles no Holter, sem roteiro específico de diário, diferenciação de queixas e consulta de retorno. Novo material não contém posologia.
4. **Retorno de monitorização**: já existe checklist de escolha do método diagnóstico JCS2022 e de extrassístoles frequentes. O novo checklist cobre interpretação do exame obtido, qualidade e conclusão limitada ao episódio registrado; são 10 itens.

## Entregas

- `round2/fa/casos-clinicos.json`: dois registros, com quatro alternativas cada, índice de resposta base zero e explicação de todas as opções.
- `round2/fa/material-paciente.json`: um registro, documento_slug canônico do protocolo de correlação.
- `round2/fa/checklists.json`: um registro, documento_origem do mesmo protocolo, dez IDs únicos prefixados `r2-palpit-` e seções de origem existentes.

Todos os quatro registros mantêm `review_status: pendente_revisao`, sem `published:true` e sem alegação de revisão humana. Novos slugs sem colisão com os catálogos. Chaves idênticas ao exemplar de cada catálogo; validação mecânica local passou. Detector de posologia do loader reproduzido: material sem correspondências.

## Fontes primárias consultadas e limites

- **ACC/AHA/ACCP/HRS 2023**, publicação JACC 2024, DOI 10.1016/j.jacc.2023.08.017: https://pmc.ncbi.nlm.nih.gov/articles/PMC11104284/ . O navegador de pesquisa retornou recaptcha; acesso HTTP direto autorizado retornou texto integral. Conferidas seções 8.2.1 e 6.3.1: requisito de anticoagulação ininterrupta ou imagem antes de cardioversão eletiva, anticoagulação pós-procedimento e risco embólico. A janela ≥48h é explicitamente AHA/ACC2023. O caso tem seis semanas de FA documentada; portanto não está próximo de qualquer divergência 24h/48h entre sociedades. O escore é explicitamente CHA₂DS₂-VASc, sem transplantar regra ESC de CHA₂DS₂-VA. Classes/níveis I B-R e I B-NR conferidos no texto primário.
- **ISHNE-HRS 2017**, DOI 10.1111/anec.12447: https://pmc.ncbi.nlm.nih.gov/articles/PMC6931745/ . Texto integral por HTTP direto; seções 3 e 4.2 consultadas para captura, diário, qualidade e monitorização compatível com frequência. Trata-se de consenso; não atribuído benefício de desfecho clínico ou probabilidade individual de diagnóstico. Caso e checklist são estruturas operacionais originais, sem copiar algoritmo/figura.
- **AHA — Holter Monitor**, revisado 25/02/2025: https://www.heart.org/en/health-topics/arrhythmia/symptoms-diagnosis--monitoring-of-arrhythmia/holter-monitor . Página aberta; base educativa para diário e devolução.
- **AHA — Cardiac Event Recorder**, revisado 10/10/2024: https://www.heart.org/en/health-topics/arrhythmia/symptoms-diagnosis--monitoring-of-arrhythmia/cardiac-event-recorder . Página aberta; base para registro mais longo e orientação específica do aparelho.
- **AHA — Symptoms, Diagnosis and Monitoring of Arrhythmia**, revisado 10/10/2024: https://www.heart.org/en/health-topics/arrhythmia/symptoms-diagnosis--monitoring-of-arrhythmia . Página aberta; sinais de alarme. Número de emergência adaptado ao Brasil: 192.

Resumo científico original e curto, sem transcrição literal das fontes. Números demográficos, resultados clínicos e situações dos dois casos são inteiramente fictícios. Não há escolha nova de dose, mistura EMA/Anvisa nem generalização de ETE negativo para ausência de necessidade de anticoagulação.

O caso avançado inclui estabilidade, FEVE, ausência de prótese mecânica/estenose mitral relevante, função renal/peso, hemograma, ausência de sangramento/hepatopatia com coagulopatia e interações. O foco é adesão prévia; não autoriza dose extra improvisada, não elimina controle de ritmo, não troca anticoagulante por aspirina. Anticoagulação de longo prazo indicada pelo risco do cenário mesmo após quatro semanas.

## Integração Tudo com Tudo — identificadores reais

### Núcleo novo palpitações

- Documento existente da produção 1: `palpitacoes-monitorizacao-e-correlacao-entre-sintoma-e-ritmo`.
- Caso novo: `palpitacoes-dois-tipos-de-sintoma-e-correlacao-parcial-no-holter`.
- Material novo: `diario-de-palpitacoes-e-retorno-do-holter-como-participar`.
- Checklist novo: `retorno-das-palpitacoes-auditoria-da-correlacao-sintoma-ritmo`.
- Exame existente: `holter-24h`.
- Trilha da produção 1: `trilha-consulta-progressiva-fibrilacao-atrial`.

Relações solicitadas para consolidação: documento ↔ caso, documento ↔ material, documento ↔ checklist, caso ↔ exame; inserir o caso e material na sequência inicial da trilha, antes das decisões terapêuticas de FA. Não atrelar anticoagulante ao diagnóstico genérico de palpitação.

### Núcleo novo reconciliação antes de cardioversão

- Caso novo: `fa-cardioversao-eletiva-omissoes-doac-reveladas-na-reconciliacao`.
- Documentos produção 1: `anticoagulacao-na-fa-reconciliacao-de-dose-funcao-renal-e-interacoes` e `fibrilacao-atrial-primeira-consulta-plano-longitudinal-e-retorno`.
- Checklist já existente e conferido no catálogo atual: `pre-cardioversao-eletiva-de-fibrilacao-atrial`.
- Doença canônica utilizada nos documentos produção 1: `fibrilacao-atrial`.
- Calculadora canônica utilizada nos documentos produção 1: `cha2ds2-vasc`.
- Medicamento canônico utilizado nos documentos produção 1: `apixabana`.

Relações solicitadas para consolidação: caso ↔ dois documentos, caso ↔ checklist, caso ↔ doença/calculadora/apixabana. Inserir na etapa avançada da trilha, depois de reconciliação e prevenção de AVC. Os links inline dos casos usam destinos existentes; material/checklist têm relação documental explícita no schema. As relações inversas e atualização da trilha dependem da consolidação do coordenador; não foram alegadas como executadas por este agente.

## Escopo preservado

Não houve mudança em production1, commit, push ou publicação. Não foram alterados os fluxogramas legados sinalizados em audit-fa.md. Arquivos `round2/aha-source.txt` e `round2/consensus-source.txt` são cache temporário de pesquisa, não integrar ao commit/artifact final.
