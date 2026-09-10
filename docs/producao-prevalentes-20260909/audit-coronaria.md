# Auditoria da frente coronariana — 09/09/2026

Base: GitHub `rafaelpaesmeirelles/MeuCardio`, SHA `64796aa973316c94b47dcf8dc75a474415ecba34`. Leitura de paths completos e leitura remota de protocolo de dor torácica SBC 2025, prevenção secundária integrada, diretriz ACC/AHA 2025 e fluxograma SCC ESC 2024. Um caminho presumido `sindrome-coronariana-cronica-esc-2024.md` retornou 404; não foi usado como referência nem link.

## Entregas

Três documentos novos complementares, de aproximadamente 800–900 palavras contando frontmatter/links:

- suspeita-de-doenca-coronariana-primeira-consulta-do-sintoma-a-decisao: entrevista estruturada, pergunta clínica, seleção individualizada de teste, diagnósticos concorrentes e continuidade ANOCA/INOCA.
- dor-toracica-exames-discordantes-reavaliacao-e-destino-seguro: incerteza diagnóstica, rastreabilidade do ensaio/timing, reavaliação, exercícios e registro do destino; sem cortes universais de troponina.
- primeiro-retorno-pos-sca-conciliacao-antitrombotica-e-intercorrencias: reconstrução das receitas, DAPT versus anticoagulação, intercorrências e barreiras de acesso, complementando documento de alta existente.

Uma correção pontual no arquivo existente `fluxograma-sindrome-coronariana-cronica-esc-2024.md`, autorizada pelo agente principal: removida afirmação de escolha obrigatoriamente única fora da faixa moderada e ajustado ramo de probabilidade baixa para decisão individualizada. A página primária ESC 2024 explicita que pacientes em faixas muito baixa e baixa podem não precisar de teste adicional; a síntese institucional ACC confirma seleção por características, desempenho, recursos e experiência. Não constitui revalidação integral de todas as afirmações antigas do documento.

## Fontes e limites

Portais oficiais ESC 2024 SCC e ESC 2023 SCA e sínteses oficiais AHA/ACC 2021, 2023 e 2025 foram acessados. Material oficial AHA de dor torácica em PDF disponível. Artigos integrais EHJ da ESC retornaram erro de redirecionamento; slides PPTX ESC foram identificados, mas tentativa de acesso/download retornou bloqueio/403. Não se declarou leitura integral desses documentos nem se inventaram classes/níveis. Síntese institucional ACC sobre ESC 2024 é identificada como tal, distinguida da fonte primária ESC.

Também consultados resumos originais RAPID-TnT, PMID 31478763, e AUGUSTUS, PMID 30883055. Sem transcrição literal de recomendações, figuras ou tabelas originais. Perguntas de consulta, quadros de rastreabilidade, modelos de prontuário e cenários são construções didáticas originais, expressamente não validadas como escore/algoritmo. Ensaios sustentam somente afirmações circunscritas às populações estudadas.

Atualização temporal relevante: a quinta definição universal IAM, 28/08/2026, está no portal primário ESC; o resumo confirma categorias primário/secundário/relacionado a procedimento e limiares de troponina por sexo. O texto novo informa esse nível de mudança, remete ao documento específico existente e não reconstrói critérios de infarto periprocedimento a partir de resumo.

Documentos novos marcados `revisao_tecnica_ia`; não são revisão humana. Não existe promessa de completude de todo o tema, comparação com banco de produção ou testes da aplicação nesta frente.

## Tudo com Tudo e verificação

28 links internos nos quatro documentos, conferidos por resolução de caminho contra `current-paths.txt` mais os três arquivos novos: zero destinos inexistentes. Os links cobrem diretrizes/protocolos, exames, calculadoras, farmacologia, ensaios, prevenção, reabilitação e comunicação.

IDs atuais lidos de `base/*/metadados.json` estão em `coronaria-integration-ids.json`; todos validados por pertencimento. O agente principal integra relações bidirecionais e trilhas, incluindo casos/materiais ao paciente se aplicáveis. Este arquivo não afirma que links Markdown por si só tenham atualizado o grafo em produção.

Integração sugerida:

- SCC → primeira consulta → algoritmo SCC, angioTC, cálcio, provas funcionais, ANOCA/INOCA → trilha DAC crônica.
- SCA → exames discordantes → troponina, HEART, GRACE, definição IAM → trilha SCA.
- SCA → primeiro retorno → AAS/clopidogrel/ticagrelor, FA+ICP, prevenção/reabilitação → trilha antitrombótico.

Sem commit, push, PR, merge, banco ou deploy nesta frente.
