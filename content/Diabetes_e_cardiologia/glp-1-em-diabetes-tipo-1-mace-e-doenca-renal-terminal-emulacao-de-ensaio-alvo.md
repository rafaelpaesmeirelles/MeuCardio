---
title: "GLP-1 em Diabetes Tipo 1: MACE e Doença Renal Terminal em Emulação de Ensaio-Alvo (Xu et al., Nature Medicine 2026)"
slug: glp-1-em-diabetes-tipo-1-mace-e-doenca-renal-terminal-emulacao-de-ensaio-alvo
theme: "Diabetes e cardiologia"
kind: estudo
review_status: revisado
source_refs: ["Xu Y, Malek ND, Chang AR, Echouffo-Tcheugui JB, Selvin E, Grams ME, Fang M, Shin JI. Glucagon-like peptide-1 receptor agonists for major cardiovascular and kidney outcomes in type 1 diabetes. Nat Med. 2026;32(5):1682-1685. Epub 2026 Mar 19. DOI: 10.1038/s41591-026-04274-0. PMID: 41857198. PMCID: PMC13190255. Texto completo (Brief Communication, acesso aberto CC BY-NC-ND) conferido via PubMed E-utilities (efetch/esummary, db=pubmed e db=pmc) em 09/09/2026."]
legacy_source: "Documento novo, escrito em 09/09/2026. A pasta já cobre risco cardiovascular basal em diabetes tipo 1 (registro sueco por idade de início, calcificação coronariana em CACTI/DCCT-EDIC) e proteção cardiovascular de agonistas de GLP-1 em diabetes tipo 2 (LEADER, SUSTAIN-6, REWIND), mas nenhum documento tratava do efeito de uma terapia específica sobre desfecho cardiovascular ou renal DENTRO do diabetes tipo 1 — lacuna que os grandes CVOTs de GLP-1 nunca endereçaram porque excluíram diabetes tipo 1 de seus critérios de inclusão. Buscado no PubMed E-utilities nesta sessão por sobreposição com outras sessões ativas no mesmo repositório: nenhum documento existente (pasta e busca textual em todo o content/) menciona este PMID, este desenho de emulação de ensaio-alvo ou este achado."
---

# GLP-1 em Diabetes Tipo 1: MACE e Doença Renal Terminal em Emulação de Ensaio-Alvo

## Pergunta clínica
Agonistas do receptor de GLP-1 (GLP-1RA) reduzem risco cardiovascular e renal em diabetes tipo 2, achado já registrado nesta pasta (LEADER, SUSTAIN-6, REWIND — ver `agonistas-do-receptor-de-glp-1-e-protecao-cardiovascular-leader-sustain-6-rewind.md`). Mas **todos os grandes ensaios de desfecho cardiovascular (CVOT) de GLP-1RA excluíram diabetes tipo 1** de seus critérios de inclusão. Diabetes tipo 1 tem excesso de risco cardiovascular e renal bem documentado (ver `diabetes-tipo-1-e-risco-cardiovascular-idade-de-inicio-e-registro-sueco.md`), mas nunca houve um ensaio clínico randomizado de desfecho duro (MACE ou doença renal terminal) testando qualquer terapia farmacológica nessa população — os autores do estudo abaixo afirmam explicitamente que, até a data de publicação, **nenhum RCT avaliou terapias para prevenção de MACE ou doença renal terminal em diabetes tipo 1**, pela dificuldade prática de reunir eventos suficientes numa população jovem com baixa taxa de eventos, exigindo seguimento muito prolongado.

Diante dessa lacuna, os autores usaram **emulação de ensaio-alvo (target trial emulation)** — metodologia que aplica os princípios de desenho de um RCT a dados observacionais — para estimar o efeito do início de GLP-1RA sobre desfechos cardiovasculares e renais em diabetes tipo 1.

## Desenho
Xu Y et al. Nat Med. 2026;32(5):1682-1685 (PMID 41857198; PMCID PMC13190255; Brief Communication, acesso aberto).

- **Fonte de dados**: Optum Labs Data Warehouse (OLDW), banco de prontuário eletrônico desidentificado de mais de 60 sistemas de saúde nos EUA, com aproximadamente 300 milhões de indivíduos.
- **Desenho**: emulação sequencial de 135 ensaios-alvo, construídos mês a mês entre janeiro de 2013 e março de 2024 — abordagem que elimina viés de tempo imortal (ao alinhar corretamente o início do tratamento com o início do seguimento) e maximiza poder estatístico (ao permitir que cada indivíduo contribua dados em múltiplos "ensaios" mensais).
- **Definição de exposição**: indivíduos que iniciaram qualquer GLP-1RA no mês de elegibilidade foram classificados como "iniciadores"; os demais, "não iniciadores". As moléculas incluídas na classe GLP-1RA foram: **albiglutida, dulaglutida, exenatida, liraglutida, lixisenatida, semaglutida e tirzepatida** — o estudo NÃO permite comparação entre moléculas individuais nem ajuste de dose, pela limitação de tamanho amostral por agente.
- **Critérios de elegibilidade**: diagnóstico de diabetes tipo 1 por algoritmo previamente validado (valor preditivo positivo de 88%), em uso de insulina, sem uso prévio de GLP-1RA, com IMC e HbA1c disponíveis na data-índice, e pelo menos 12 meses de vínculo prévio com o sistema de saúde. Foram excluídos pacientes com contraindicação a GLP-1RA (câncer de tireoide ou neoplasia endócrina múltipla tipo II), doença renal terminal ou gestação prévias à data-índice.
- **Ajuste**: ponderação por escore de propensão, com balanceamento adequado das características basais entre grupos após ponderação (todas as diferenças médias padronizadas <10%).
- **Desfechos primários**: MACE (composto de infarto agudo do miocárdio, AVC ou morte por qualquer causa) e doença renal terminal (diálise ou transplante renal).
- **Desfechos secundários**: hospitalização por insuficiência cardíaca, eventos hepáticos adversos maiores (composto de cirrose descompensada, carcinoma hepatocelular ou transplante hepático) e perda de peso (≥5%, ≥10%, ≥15%).
- **Desfechos de segurança**: hospitalização por cetoacidose diabética (CAD), hospitalização por hipoglicemia grave e eventos gastrointestinais (composto de doença biliar, pancreatite, obstrução intestinal ou gastroparesia).
- **Controle negativo**: acidente de trânsito, usado para avaliar confusão residual/não medida.

## População
- **174.678 indivíduos** com diabetes tipo 1, contribuindo **6.092.537 "ensaios-pessoa"** (person-trials) ao longo dos 135 ensaios-alvo mensais.
- Idade média **43 anos**; **47% mulheres**.
- **14.488 ensaios-pessoa** iniciaram GLP-1RA no mês de elegibilidade.
- Seguimento mediano **38 meses** (intervalo interquartil 18-64 meses).

## Resultados — desfechos primários
- **MACE**: risco em 5 anos **4,3%** com GLP-1RA versus **5,0%** sem GLP-1RA; diferença de risco **-0,7%** (IC95% -1,2% a -0,2%); **HR 0,85** (IC95% 0,77-0,95) — redução relativa de risco de **15%**. As curvas de Kaplan-Meier se separam após 1,5 ano e permanecem divergentes.
  - Componentes individuais: infarto agudo do miocárdio HR **0,79** (IC95% 0,66-0,95); AVC HR **0,93** (IC95% 0,78-1,10, não significativo); mortalidade por qualquer causa HR **0,84** (IC95% 0,71-1,00, no limite da significância).
- **Doença renal terminal**: risco em 5 anos **1,6%** versus **1,9%**; diferença de risco **-0,3%** (IC95% -0,6% a 0,0%); **HR 0,81** (IC95% 0,69-0,95) — redução relativa de risco de **19%**.

## Resultados — desfechos secundários e de segurança
- **Hospitalização por insuficiência cardíaca**: HR **0,82** (IC95% 0,71-0,94) — redução de **18%**.
- **Eventos hepáticos adversos maiores**: HR **0,72** (IC95% 0,60-0,85) — redução de **28%**.
- **Perda de peso**: pacientes que iniciaram GLP-1RA tiveram maior probabilidade de atingir perda de peso ≥5% (HR 1,25; IC95% 1,23-1,28), ≥10% (HR 1,22; IC95% 1,19-1,26) e ≥15% (HR 1,14; IC95% 1,09-1,18) — magnitude de efeito bem menor que a de peso observada nos grandes ensaios de agonistas de GLP-1/GIP em obesidade e diabetes tipo 2 já registrados nesta pasta.
- **Cetoacidose diabética (hospitalização)**: **sem aumento de risco** — HR **0,83** (IC95% 0,76-0,90), ou seja, risco *menor*, não maior, com GLP-1RA.
- **Hipoglicemia grave (hospitalização)**: **sem aumento de risco** — HR **0,82** (IC95% 0,72-0,94), também menor, não maior.
- **Eventos gastrointestinais**: mais frequentes numericamente com GLP-1RA, mas **sem diferença estatisticamente significativa** (HR 1,05; IC95% 0,99-1,13).

## Robustez e limitações reconhecidas pelos próprios autores
- Achados **consistentes em subgrupos exploratórios** por idade (<45 vs ≥45 anos) e por HbA1c basal (<8% vs ≥8%).
- Análise por protocolo (censurando desvio da estratégia de tratamento, seguimento mediano de 7 meses) foi menos precisa, mas consistente com a análise por intenção de tratar.
- Análises de sensibilidade (exclusões adicionais, definição alternativa de desfecho, censura diferente para peso, definição laboratorial mais estrita de diabetes tipo 1, imputação de covariáveis ausentes) produziram resultados semelhantes.
- **Controle negativo** (acidente de trânsito): sem diferença significativa entre grupos — HR **0,96** (IC95% 0,77-1,20) — argumento contra confusão residual forte.
- **E-values**: **1,63** para MACE e **1,77** para doença renal terminal — um confundidor não medido precisaria ter associação de magnitude pelo menos moderada com exposição e desfecho para anular o achado.
- Limitações declaradas pelos próprios autores: (1) estudo observacional, com possibilidade de confusão residual/não medida apesar da ponderação; (2) possível má classificação do diagnóstico de diabetes tipo 1, mitigada por algoritmo validado (VPP 88%) e por análise de sensibilidade restrita a casos confirmados por critério laboratorial, com resultado semelhante; (3) CAD e hipoglicemia grave identificadas apenas por registro de **hospitalização**, capturando provavelmente só os casos mais graves — mas esse viés de captação deveria afetar igualmente os dois grupos; (4) parte da perda de peso, sobretudo a de 5%, pode ser não intencional (por exemplo, por doença intercorrente), sem forma de distinguir isso nos dados de prontuário eletrônico; (5) sem dado de dose de insulina, o que limita avaliar ajustes de dose; (6) tamanho amostral insuficiente para analisar agentes individuais separadamente ou fazer comparação frente a frente entre eles.

## Interpretação
Este é o maior estudo já conduzido especificamente sobre efeito de uma classe terapêutica em desfechos cardiovasculares e renais duros em diabetes tipo 1 — população sistematicamente excluída dos CVOTs de GLP-1RA que estabeleceram benefício em diabetes tipo 2. A magnitude de redução de risco (15% para MACE, 19% para doença renal terminal) é **comparável** à observada nos ensaios randomizados de diabetes tipo 2 já registrados nesta pasta (ordem de 13-14% para MACE e 16% para desfecho renal nos grandes CVOTs), apesar de o efeito sobre perda de peso ter sido proporcionalmente menor que o observado em diabetes tipo 2/obesidade — sugerindo que parte do benefício cardiorrenal possa ocorrer por vias independentes de perda de peso (efeito anti-inflamatório, melhora de sensibilidade à insulina, função endotelial, agregação plaquetária), hipótese discutida pelos próprios autores mas não testada diretamente neste desenho.

O achado de segurança é o ponto mais relevante para a prática: ensaios pequenos e antigos com liraglutida (ADJUNCT ONE e TWO, citados no artigo mas não verificados diretamente nesta redação) haviam sugerido aumento de hipoglicemia sintomática e hiperglicemia com cetose. Este estudo, maior e mais recente, **não encontrou esse sinal** — os autores atribuem a discrepância a avanços no cuidado (monitorização contínua de glicose, sistemas de infusão automatizada de insulina) que teriam tornado o uso de GLP-1RA mais seguro na prática atual em relação aos ensaios mais antigos.

Ainda assim, **é um estudo observacional, não um RCT** — os próprios autores concluem pedindo ensaios randomizados de grande porte para confirmar os achados, e não afirmam que a evidência já sustenta o mesmo grau de certeza que os CVOTs de diabetes tipo 2.

## Armadilhas clínicas
- **Tratar este estudo como equivalente a um CVOT randomizado** — é emulação de ensaio-alvo sobre dados observacionais de prontuário eletrônico; a robustez metodológica (ponderação por propensão, controle negativo nulo, E-values moderados, sensibilidade consistente) reduz mas não elimina a possibilidade de confusão residual, e os próprios autores pedem RCTs para confirmação.
- **Extrapolar o achado para uma molécula específica de GLP-1RA** — o estudo agrupa sete moléculas diferentes (albiglutida, dulaglutida, exenatida, liraglutida, lixisenatida, semaglutida, tirzepatida) e explicitamente não teve poder estatístico para analisá-las separadamente ou compará-las entre si.
- **Ler "sem aumento de risco de cetoacidose/hipoglicemia grave" como "risco zero" ou "dispensa monitorização"** — a ascertainment dependeu de registros de **hospitalização**, capturando provavelmente só os casos mais graves; eventos leves a moderados não hospitalizados não foram capturados em nenhum dos dois grupos.
- **Ignorar que a mortalidade por qualquer causa teve IC95% no limite da significância** (HR 0,84; IC95% 0,71-1,00) — resultado direcionalmente favorável, mas menos robusto que o de MACE composto, IAM isolado ou doença renal terminal; o AVC isolado nem chegou a ser significativo (HR 0,93; IC95% 0,78-1,10).
- **Superestimar o efeito sobre perda de peso** — a magnitude aqui (HR 1,14-1,25 para atingir diferentes limiares de perda de peso) é claramente menor que a observada nos grandes ensaios de agonistas de GLP-1/GIP em obesidade e diabetes tipo 2 já registrados nesta pasta; parte da perda de peso relatada pode ainda ser não intencional, conforme reconhecido pelos próprios autores.
- **Assumir aprovação regulatória de GLP-1RA para esta indicação em diabetes tipo 1** — o estudo não trata de bula ou registro regulatório; `VERIFICAÇÃO HUMANA NECESSÁRIA` quanto ao status de uso on-label versus off-label de GLP-1RA em diabetes tipo 1 no Brasil (Anvisa) e nos EUA (FDA), e quanto a eventual atualização de diretrizes (ADA, SBD) incorporando este achado.

## Tudo com Tudo

- [Diabetes Tipo 1 e Risco Cardiovascular: Idade de Início e o Registro Sueco](/biblioteca/diabetes-tipo-1-e-risco-cardiovascular-idade-de-inicio-e-registro-sueco)
- [Diabetes Tipo 1 de Longa Duração e Calcificação Coronariana: os Estudos CACTI e DCCT/EDIC](/biblioteca/diabetes-tipo-1-de-longa-duracao-e-calcificacao-coronariana-cacti-e-dcct-edic)
- [Agonistas do Receptor de GLP-1 e Proteção Cardiovascular no Diabetes: LEADER, SUSTAIN-6 e REWIND](/biblioteca/agonistas-do-receptor-de-glp-1-e-protecao-cardiovascular-leader-sustain-6-rewind)
- [Semaglutida e Desfecho Renal no Diabetes Tipo 2: o Ensaio FLOW](/biblioteca/semaglutida-e-desfecho-renal-no-diabetes-tipo-2-o-ensaio-flow)
- [Cetoacidose diabética euglicêmica associada a inibidores de SGLT2](/biblioteca/cetoacidose-euglicemica-associada-a-inibidores-de-sglt2)
- [Doença Cardiovascular em Pacientes com Diabetes: Estratificação de Risco e Manejo (ESC 2023)](/biblioteca/doenca-cardiovascular-em-pacientes-com-diabetes-estratificacao-de-risco-e-manejo-esc-2023)

## Revisão editorial CorVIA

Revisado em 09/09/2026 com fontes públicas rastreáveis (PubMed E-utilities — esearch/esummary/efetch em db=pubmed e db=pmc). Todos os números centrais deste documento (n, HRs, ICs95%, diferenças de risco, E-values) foram conferidos diretamente no texto completo indexado no PubMed Central (PMCID PMC13190255), não apenas no resumo. As referências de estudos de terceiros citadas dentro do artigo-fonte (ensaios ADJUNCT ONE/TWO com liraglutide, CVOTs de GLP-1RA em diabetes tipo 2) foram reproduzidas apenas como o próprio artigo as descreve, e NÃO foram verificadas de forma independente nesta redação — não usar os números desses estudos citados indiretamente sem conferência própria em fonte primária. `VERIFICAÇÃO HUMANA NECESSÁRIA`: status regulatório (FDA/Anvisa) do uso de GLP-1RA em diabetes tipo 1 e eventual posicionamento de diretrizes (ADA Standards of Care, SBD) sobre este achado específico após a data desta redação.
