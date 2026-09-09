---
title: "IA Generativa para Rascunho de Respostas a Mensagens do Portal do Paciente"
slug: ia-generativa-para-rascunho-de-respostas-a-mensagens-do-portal-do-paciente
theme: "Comunicação clínica"
kind: estudo
review_status: revisado
source_refs: ["Garcia P, Ma SP, Shah S, Smith M, Jeong Y, Devon-Sand A, Tai-Seale M, Takazawa K, Clutter D, Vogt K, Lugtu C, Rojo M, Lin S, Shanafelt T, Pfeffer MA, Sharp C. Artificial Intelligence-Generated Draft Replies to Patient Inbox Messages. JAMA Netw Open. 2024;7(3):e243201. DOI: 10.1001/jamanetworkopen.2024.3201. PMID: 38506805", "Crowley AP, Hanish A, Lubken J, Becker M, Rosen C, Moon J, Regli SH. Usage of and Satisfaction with Artificial Intelligence-Generated Draft Replies to Patient Portal Messages. Appl Clin Inform. 2026;17(3):510-517. DOI: 10.1055/a-2893-7363. PMID: 42361849", "Owens K, Jayaram A, Chowdhury A, Pollak KI, Klotman S, Griffen Z, Danielski M, Goldstein B, Maddocks J, Roman M, Poon EG, Bedoya A, Cavalier J. Patient Perspectives on AI-Drafted Electronic Portal Messages. JAMA Netw Open. 2026;9(7):e2622463. DOI: 10.1001/jamanetworkopen.2026.22463. PMID: 42412426"]
legacy_source: "Documento novo, escrito em 09/09/2026. Esta pasta já tem um documento sobre IA generativa aplicada a material educativo do paciente (legibilidade de texto gerado ou traduzido), mas nenhum cobria o uso de modelos de linguagem de grande porte (LLM) integrados ao prontuário eletrônico para RASCUNHAR a resposta do próprio médico/enfermagem às mensagens que o paciente envia pelo portal eletrônico — lacuna distinta (comunicação assíncrona bidirecional já em uso real em sistemas de saúde, não geração de material educativo unidirecional), coberta aqui com três estudos publicados entre 2024 e 2026, todos conferidos via PubMed nesta sessão."
---

# IA Generativa para Rascunho de Respostas a Mensagens do Portal do Paciente

## O problema que motivou a ferramenta
O volume de mensagens de paciente pelo portal eletrônico (dúvida sobre resultado de exame, ajuste de medicação, sintoma novo) cresceu de forma sustentada nos últimos anos e é apontado como contribuinte relevante para sobrecarga cognitiva e esgotamento profissional (*burnout*) de médicos e enfermagem. A resposta tecnológica que sistemas de saúde vêm implantando desde 2023 não é um chatbot que responde diretamente ao paciente, mas um LLM integrado ao prontuário eletrônico que gera um **rascunho** de resposta para o profissional revisar, editar ou descartar antes de enviar — o profissional permanece como autor final e responsável pelo conteúdo. Três estudos publicados entre 2024 e 2026, dois deles quantitativos sobre implementação real e um qualitativo sobre a perspectiva do paciente, permitem avaliar essa ferramenta com dado, não com expectativa.

## Estudo piloto fundador: Stanford (Garcia et al., JAMA Network Open 2024)
Garcia P et al., *JAMA Netw Open.* 2024;7(3):e243201 (PMID 38506805). Estudo de melhoria de qualidade, prospectivo, de braço único, conduzido por 5 semanas (10 de julho a 13 de agosto de 2023) no Stanford Health Care, nas divisões de Atenção Primária e Gastroenterologia/Hepatologia. Todos os médicos assistentes, profissionais de prática avançada, enfermagem de ambulatório e farmacêuticos clínicos dessas divisões foram matriculados no piloto; **197 profissionais matriculados, 162 incluídos na análise** (35 excluídos por serem usuários beta pré-piloto, estarem fora do serviço ou não vinculados a um ambulatório específico). A intervenção: rascunhos de resposta gerados por um LLM integrado ao prontuário eletrônico, compatível com HIPAA.

- **Desfecho primário — taxa de utilização do rascunho de IA**: em média **20% das respostas** dos profissionais partiram de um rascunho gerado por IA.
- **Sem mudança mensurável no tempo** de ação, escrita ou leitura da mensagem entre os períodos pré-piloto e piloto — a ferramenta não acelerou objetivamente a tarefa neste estudo.
- **Redução estatisticamente significativa na carga de tarefa percebida** (escore derivado de 4 itens de carga de tarefa do médico: média 61,31 pré-piloto vs. 47,26 pós-piloto; diferença pareada -13,87; IC95% -17,38 a -9,50; p < 0,001).
- **Redução estatisticamente significativa no escore de exaustão no trabalho** (média 1,95 pré-piloto vs. 1,62 pós-piloto; diferença pareada -0,33; IC95% -0,50 a -0,17; p < 0,001), em subamostra de 73 profissionais (45,1% dos matriculados) que completaram as duas pesquisas.
- Conclusão dos próprios autores: houve adoção e usabilidade notáveis, com melhora na percepção de sobrecarga e esgotamento — **mas sem melhora de tempo**, e mais teste "do código à beira do leito" é necessário antes de estratégia organizacional definitiva.

## Replicação em outro sistema de saúde, com enfermagem incluída (Crowley et al., Applied Clinical Informatics 2026)
Crowley AP et al., *Appl Clin Inform.* 2026;17(3):510-517 (PMID 42361849). Estudo piloto em 7 clínicas de um sistema de saúde acadêmico da Pensilvânia (Penn Medicine), usando a ferramenta comercial de rascunho por IA integrada ao prontuário Epic (Augmented Response Technology, ART). **80 usuários voluntários**: 36 médicos, 25 enfermeiros(as), 10 enfermeiros(as) de prática avançada, 9 auxiliares médicos.

- **Taxa média de início de resposta a partir de rascunho de IA: 20,2%** — praticamente idêntica ao achado de Stanford, em sistema e ferramenta diferentes, o que reforça a robustez do número em torno de 1/5 das respostas.
- **40% das respostas enviadas tiveram pouca ou nenhuma edição** do rascunho gerado.
- Em pesquisa com 52 respondentes: **66% (n=33) concordaram que os rascunhos eram úteis**; **46% (n=23) concordaram que a ferramenta melhorou a qualidade** das respostas.
- **Enfermagem relatou opinião mais favorável que médicos** em praticamente todas as perguntas da pesquisa — assimetria por categoria profissional que o estudo de Stanford não estratificou da mesma forma.
- Nas respostas livres, os temas mais citados como positivos foram conteúdo útil da mensagem (28,3%, n=13) e redução de esforço/tempo percebido (23,9%, n=11); como negativos, conteúdo incorreto ou inapropriado no rascunho (34,9%, n=15) e sugestão excessiva de agendar consulta quando não necessário (27,9%, n=12).
- Conclusão dos autores: rascunhos de IA foram avaliados como geralmente aceitáveis e úteis, mas a expansão da ferramenta deve manter monitoramento contínuo de aceitabilidade, carga cognitiva **e segurança** — o achado de conteúdo incorreto em mais de 1 em cada 3 avaliações livres é o ponto que mais exige vigilância antes de qualquer expansão.

## O que o paciente pensa disso (Owens et al., JAMA Network Open 2026)
Garcia e Crowley respondem "o profissional usa e gosta?" — mas a pergunta seguinte, que só um estudo qualitativo recente responde, é "o paciente aceita ser respondido por um rascunho gerado por IA, mesmo revisado por humano?". Owens K et al., *JAMA Netw Open.* 2026;9(7):e2622463 (PMID 42412426). Estudo qualitativo por entrevista em vídeo, com **40 pacientes adultos** de um grande sistema de saúde acadêmico (Duke), recrutados com busca deliberada de maior representação de grupos raciais/étnicos minorizados, pacientes mais velhos e pacientes com menor satisfação prévia com mensagens geradas por IA (coleta entre abril e agosto de 2025). Amostra: 30 mulheres (75,0%), 9 homens (22,5%), 14 pretos ou afro-americanos (35,0%), 13 brancos (32,5%), 13 pacientes com 65 anos ou mais (32,5%).

- Pacientes descreveram a mensagem de portal como algo **transacional**, priorizando resolução rápida do problema acima de profundidade relacional.
- **Alto conforto com rascunhos gerados por IA**, condicional à supervisão do médico — o ponto central da aceitação não foi a origem (IA ou humana) do texto, e sim se o médico permanece revisando e responsável pelo conteúdo.
- Preferência de tom e expressão de empatia **variou entre indivíduos e contextos**, e foi determinada menos por a mensagem "parecer" gerada por IA ou por humano, e mais por o tom, a extensão e o nível de detalhe se ajustarem ao propósito e à gravidade daquela comunicação específica.
- **Divulgação (disclosure) do uso de IA foi amplamente endossada** pelos participantes como importante para a confiança — mas houve divergência sobre o momento e o formato preferido dessa divulgação (por exemplo, aviso fixo no portal versus rótulo em cada mensagem individual).
- Conclusão dos autores: pacientes apoiam o uso de IA quando ela melhora a eficiência da comunicação, desde que o médico revise e permaneça responsável pela mensagem — a implementação deveria priorizar supervisão clínica, padrões de comunicação sensíveis ao contexto, práticas padronizadas de divulgação e monitoramento de efeitos a jusante sobre qualidade, equidade e confiança/segurança do paciente.

## Síntese prática
Os três estudos, lidos em conjunto, convergem para um retrato consistente, ainda que preliminar, desta tecnologia já em uso real (não hipotético) em pelo menos dois sistemas de saúde acadêmicos dos EUA:

1. **A taxa de adoção real gira em torno de 20%** das respostas em ambos os pilotos de implementação (Stanford e Penn Medicine, ferramentas diferentes) — não é adoção majoritária, e cerca de 4 em cada 5 respostas continuam sendo escritas do zero pelo profissional.
2. **O benefício mensurado até agora é sobre carga percebida e esgotamento, não sobre tempo cronometrado** — no único estudo que mediu tempo de forma objetiva (Stanford), não houve redução detectável, apesar de o profissional relatar sentir menos sobrecarga.
3. **A taxa de erro no rascunho não é desprezível** — no estudo de Penn Medicine, mais de 1 em 3 comentários livres mencionou conteúdo incorreto ou inadequado no texto gerado, o que reforça que a revisão humana antes do envio não é uma formalidade opcional, e sim a etapa que evita que erro de IA chegue ao paciente.
4. **O paciente, de modo geral, aceita bem o uso de IA nesse canal — mas condiciona essa aceitação à permanência da supervisão médica e à transparência sobre o uso da ferramenta**, sem exigir necessariamente que a mensagem "pareça" ter sido escrita por humano.

Para a prática em cardiologia, onde mensagens de portal frequentemente envolvem ajuste de anticoagulante, resultado de exame com sigla técnica (fração de ejeção, INR, biomarcador) ou dúvida sobre sintoma que pode ser urgente, a leitura honesta dos três estudos é: a ferramenta pode reduzir a sensação de sobrecarga do profissional, mas não substitui a revisão clínica de cada rascunho antes do envio, e a decisão de adotá-la deveria vir acompanhada de divulgação clara ao paciente de que IA participou da elaboração da resposta.

## Armadilhas clínicas
- **Presumir que "rascunho revisado por humano" elimina o risco de erro clínico** — no estudo de Penn Medicine, mais de um terço das avaliações livres mencionou conteúdo incorreto ou inapropriado no rascunho; a revisão evita que esse erro chegue ao paciente apenas se for feita de fato, com atenção, e não como aprovação automática do texto pronto.
- **Confundir redução de carga percebida com redução de tempo de trabalho** — no estudo de Stanford, o escore de exaustão e de carga de tarefa melhorou, mas o tempo cronometrado de resposta não mudou; prometer à equipe ou à gestão "ganho de tempo" com base nesses dados não é sustentado pelo próprio estudo fundador.
- **Implantar a ferramenta sem divulgar ao paciente que uma resposta pode ter sido gerada com apoio de IA** — o estudo de Owens et al. mostra que pacientes endossam amplamente a divulgação como condição de confiança, mesmo aceitando bem o uso da tecnologia em si.
- **Extrapolar taxa de adoção de ~20% (dois sistemas americanos, dois pilotos voluntários) como piso ou teto universal** — o número é notavelmente consistente entre os dois estudos, mas ambos são pilotos voluntários em sistemas acadêmicos dos EUA; adoção compulsória, outra especialidade ou outro país podem se comportar de forma diferente, ponto que nenhum dos três estudos testa diretamente.

## Tudo com Tudo

- [Inteligência artificial generativa na comunicação com o paciente cardiológico](inteligencia-artificial-generativa-na-comunicacao-com-o-paciente-cardiologico.md)
- [Adesão ao tratamento cardiovascular com aplicativos e portal do paciente (mHealth)](adesao-ao-tratamento-cardiovascular-com-aplicativos-e-portal-do-paciente-mhealth.md)
- [OpenNotes: acesso do paciente às notas médicas e comunicação em cardiologia](opennotes-acesso-do-paciente-as-notas-medicas-e-comunicacao-em-cardiologia.md)
- [Letramento em saúde (health literacy) e desfechos cardiovasculares](letramento-em-saude-e-desfechos-cardiovasculares.md)
- [Documentação de decisão compartilhada e consentimento informado no prontuário e litígio em cardiologia](documentacao-de-decisao-compartilhada-e-consentimento-informado-no-prontuario-e-litigio-em-cardiologia.md)
- [Teleconsulta em cardiologia: limites do exame físico a distância e evidência de não inferioridade](teleconsulta-em-cardiologia-limites-do-exame-fisico-a-distancia-e-evidencia-de-nao-inferioridade.md)
