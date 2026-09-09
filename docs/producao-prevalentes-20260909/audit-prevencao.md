# Frente prevenção/lipídios e diabetes — 09/09/2026

## Entrega

3 documentos novos (3.022 palavras contando frontmatter) e correção pontual de 1 documento existente (816 palavras). Todos em `production/content/`. Nenhum commit, push ou deploy nesta frente.

- `Prevenção_e_lipídios/lipidograma-na-consulta-primeira-leitura-discordancia-e-decisao-clinica.md`: avaliação básica, amostra, método, não-HDL/ApoB/Lp(a), exemplos fictícios e passagem para HF/hiperTG.
- `Prevenção_e_lipídios/retorno-da-dislipidemia-resposta-insuficiente-seguranca-e-intensificacao.md`: adesão real, cálculos de resposta e distância da meta, segurança, intolerância e intensificação.
- `Diabetes_e_cardiologia/consulta-cardiometabolica-no-dm2-avaliacao-inicial-e-plano-longitudinal.md`: consulta inicial, TFGe/albuminúria, proteção CV independente do controle glicêmico, acesso, segurança e seguimento.
- `Prevenção_e_lipídios/dislipidemia-metas-ldl-estratificacao-risco-esc-eas-2025.md`: versão corrigida do arquivo main SHA 64796aa973316c94b47dcf8dc75a474415ecba34. Corrige falsa quinta categoria ESC “risco extremo”, explicita <40 mg/dL como opção IIb/B derivada de 2019, restringe idades SCORE2/SCORE2-OP e distingue inclisirana de anticorpos sem presumir equivalência de desfechos. Acrescenta links.

## Auditoria de lacunas

Inventário atual já contém extensa série de CVOTs, diretrizes 2019/2025/2026, fluxos de hiperTG, intolerância, HF, Lp(a), e dezenas de trilhas. Não duplicados esses títulos. A lacuna selecionada é operacional: transformar dados em consulta completa e fechar o ciclo até o retorno. Novos casos são explicitamente fictícios, não relatos reais.

Leituras GitHub de conteúdo atual: documento metas ESC 2025, ACC/AHA 2026 e ADA 2026. Leitura complementar do corpus local anterior só para descoberta/contexto (sem mutação). As referências internas foram conferidas contra inventário da main atual.

## Fontes e limites da verificação

Fontes primárias efetivamente acessíveis via web nesta frente:

- AHA, Top Things to Know, diretriz dislipidemia 2026 (13/03/2026): https://professional.heart.org/en/science-news/2026-guideline-on-the-management-of-dyslipidemia/top-things-to-know
- ESC, página oficial Focused Update 2025 (29/08/2025): https://www.escardio.org/guidelines/clinical-practice-guidelines/all-esc-practice-guidelines/dyslipidaemias/
- Tabelas oficiais ESC/EAS 2019 hospedadas pela EAS, incluindo pp. 124–129 de monitorização e metas: https://eas-society.org/wp-content/uploads/2022/11/2019_dyslipidaemias_guidelin.pdf
- KDIGO 2024, definição de cronicidade, monitorização, recomendação 3.7.1 (1A), ponto prático 3.7.2: https://kdigo.org/wp-content/uploads/2024/03/KDIGO-2024-CKD-Guideline.pdf

As rotas diretas dos originais SBC 2025, ADA 2026, NLA 2022, Sampson, DIAD e CLEAR Outcomes retornaram 403, páginas vazias ou erro de acesso. A identificação bibliográfica foi cruzada com documentos existentes do projeto; NÃO alegar nova leitura integral desses originais. Não foram introduzidas metas numéricas SBC com acesso não confirmado nem classes por analogia. Atualização AHA 2026 foi confirmada na síntese oficial; o corpo da fonte principal ADA 2026 já está no documento atual do projeto e foi mantido como suporte para síntese curta sem novos números de ensaio.

Textos são autorais, sem citação longa nem reprodução de tabela/figura alheia. Os blocos derivados das fontes web acessíveis foram limitados; exemplos, organização clínica e aritmética são originais. `review_status: revisado` é acompanhado de `review_note` declarando revisão técnica assistida por IA, sem alegar aprovação humana. Integrador deve aplicar a política editorial real sem remover essa distinção.

## Tudo com Tudo: recursos reais para integração central

IDs abaixo confirmados em `base/*/metadados.json` ATUAIS:

| Novo documento (slug) | Exames | Medicamentos | Trilhas |
|---|---|---|---|
| lipidograma-na-consulta-primeira-leitura-discordancia-e-decisao-clinica | perfil-lipidico-colesterol-total-ldl-hdl-e-triglicerideos; apolipoproteina-b-apob; lipoproteina-a-lp-a | atorvastatina-calcica; rosuvastatina-calcica; ezetimiba | trilha-prevencao-cardiovascular-e-dislipidemia |
| retorno-da-dislipidemia-resposta-insuficiente-seguranca-e-intensificacao | perfil-lipidico-colesterol-total-ldl-hdl-e-triglicerideos; apolipoproteina-b-apob | atorvastatina-calcica; rosuvastatina-calcica; ezetimiba | trilha-prevencao-cardiovascular-e-dislipidemia |
| consulta-cardiometabolica-no-dm2-avaliacao-inicial-e-plano-longitudinal | hemoglobina-glicada-hba1c; uacr-e-tfge-no-rastreio-de-doenca-renal-cronica-no-diabetes; perfil-lipidico-colesterol-total-ldl-hdl-e-triglicerideos | empagliflozina; atorvastatina-calcica | trilha-diabetes-e-protecao-cardiovascular |

Calculadoras já relacionadas por documentos reais: PCE/PREVENT e SCORE2-Diabetes. Não inventados IDs de ferramentas calculadoras nem slugs de doença adulta: catálogo de doenças especializadas não contém diretamente os hubs comuns buscados; integrador deve resolver pela origem real dos hubs.

Materiais de paciente localizados no corpus anterior (precisam confirmação na main/metadados atuais antes de criar aresta): `colesterol-alto-e-prevencao-cardiovascular`; `estatina-e-colesterol-por-que-o-remedio-continua-necessario-mesmo-comendo-bem`; `diabetes-e-o-coracao`; `por-que-meu-remedio-para-diabetes-tambem-protege-meu-coracao`.

Ordem sugerida em trilhas: leitura do lipidograma → diretriz de estratificação → tratamento → retorno; consulta cardiometabólica → diretriz DM2 → escolha iSGLT2/GLP-1 → segurança renal/metabólica. Inserção deve preservar etapas existentes, sem repetir CVOTs.

## Verificação

30 links Markdown relativos conferidos contra árvore atual + produção: zero destinos ausentes. Cálculos dos exemplos: 180→92 = 48,9%; 92→55 = 40,2%; 95→53 = 44,2%; não-HDL do primeiro exemplo = 134 mg/dL. Frontmatter presente nos quatro arquivos. Sem pacientes reais, sem novos efeitos quantitativos de estudos, sem afirmação de cobertura 100% ou publicação.
