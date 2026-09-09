---
kind: estudo
legacy_source: 'Documento novo, escrito em 08/09/2026. A pasta Calculadoras já cobria
  as três grandes famílias de risco cardiovascular em prevenção primária de origem
  americana e europeia — Framingham Risk Score (framingham-risk-score-frs), Pooled
  Cohort Equations e Equações PREVENT (pooled-cohort-equations-e-equacoes-prevent-risco-cardiovascular-em-prevencao-primaria)
  e SCORE2/SCORE2-OP, incluindo aplicabilidade brasileira e a variante SCORE2-Diabetes
  (score2-e-score2-op, score2-score2-op-aplicabilidade-e-limites-no-paciente-brasileiro,
  score2-diabetes-estimativa-de-risco-cardiovascular-em-10-anos-no-diabetes-tipo-2)
  — mas nenhum documento tratava do QRISK3, a ferramenta britânica (QResearch/NHS)
  que é hoje o modelo de risco cardiovascular com o maior número de variáveis clínicas
  incorporadas (doença renal crônica, variabilidade da pressão arterial, migrânea,
  corticosteroides, lúpus, antipsicóticos atípicos, doença mental grave e disfunção
  erétil), e que por isso levanta uma pergunta distinta das demais: o ganho de variáveis
  clínicas se traduz em ganho de discriminação, ou apenas em reclassificação de subgrupos
  específicos? Verificado via PubMed E-utilities nesta sessão (esearch por autor ''Hippisley-Cox
  QRISK3'' e por termo ''QRISK3 external validation''; efetch de abstract nos três
  PMIDs acima).'
published: true
review_status: revisado
slug: qrisk3-risco-cardiovascular-em-10-anos-derivacao-e-validacao-na-coorte-qresearch
source_refs:
- 'Hippisley-Cox J, Coupland C, Brindle P. Development and validation of QRISK3 risk
  prediction algorithms to estimate future risk of cardiovascular disease: prospective
  cohort study. BMJ. 2017;357:j2099. DOI: 10.1136/bmj.j2099. PMID: 28536104. PMCID:
  PMC5441081 — artigo de derivação e validação, conferido nesta sessão via PubMed
  E-utilities (esearch + efetch, registro/abstract lido diretamente)'
- 'Mortensen MB, Tybjærg-Hansen A, Nordestgaard BG. Statin Eligibility for Primary
  Prevention of Cardiovascular Disease According to 2021 European Prevention Guidelines
  Compared With Other International Guidelines. JAMA Cardiol. 2022;7(8):836-843. DOI:
  10.1001/jamacardio.2022.1876. PMID: 35793078. PMCID: PMC9260641 — usado aqui apenas
  como validação externa de desempenho do QRISK3 fora do Reino Unido (coorte dinamarquesa),
  não como fonte de coeficientes'
- 'Livingstone S, Morales DR, Fleuriot J, Donnan PT, Guthrie B. External validation
  of the QLifetime cardiovascular risk prediction tool: population cohort study. BMC
  Cardiovasc Disord. 2023;23(1):194. DOI: 10.1186/s12872-023-03209-8. PMID: 37061672.
  PMCID: PMC10105395 — usado aqui apenas para confirmar o uso do limiar QRISK3 ≥10%
  na prática clínica britânica (CPRD) e o número necessário a tratar associado'
theme: Calculadoras
title: 'QRISK3: Risco Cardiovascular em 10 Anos — Derivação e Validação na Coorte
  QResearch (Reino Unido)'
---

# QRISK3: Risco Cardiovascular em 10 Anos — Derivação e Validação na Coorte QResearch (Reino Unido)

## O que é e por que é diferente das ferramentas já cobertas nesta pasta

O **QRISK3** é o algoritmo de risco cardiovascular da linhagem **QResearch**, desenvolvido no Reino Unido e sucessor direto do QRISK2. Foi publicado por **Hippisley-Cox J, Coupland C, Brindle P** no **BMJ** em 2017 (*BMJ. 2017;357:j2099*, DOI 10.1136/bmj.j2099, **PMID: 28536104**), sob o título literal *"Development and validation of QRISK3 risk prediction algorithms to estimate future risk of cardiovascular disease: prospective cohort study"*.

A diferença estrutural para Framingham, Pooled Cohort Equations/PREVENT e SCORE2/SCORE2-OP — já cobertos nesta pasta — não é geográfica apenas: o QRISK3 é o modelo que testou e incorporou o maior número de variáveis clínicas específicas (doença renal crônica em estágios mais precoces, variabilidade da pressão arterial, migrânea, uso de corticosteroide, lúpus eritematoso sistêmico, antipsicóticos atípicos, doença mental grave e disfunção erétil), num desenho estatístico que permite dizer, variável a variável, quais delas realmente agregam poder preditivo independente numa coorte de quase 8 milhões de pessoas.

## Desenho e coorte de derivação/validação

Direto do abstract do registro (PMID 28536104):
- **Desenho**: estudo de coorte prospectivo, aberto (*prospective open cohort study*)
- **Fonte de dados**: base **QResearch**, agregando registros de clínicas gerais (*general practices*) da Inglaterra
- **1.309 clínicas gerais QResearch** no total, divididas em:
  - **981 clínicas** usadas para **derivar** os escores
  - **328 clínicas** (conjunto separado) usadas para **validar** os escores
- **Coorte de derivação**: **7,89 milhões de pacientes**, 25-84 anos
- **Coorte de validação**: **2,67 milhões de pacientes**
- **Critério de elegibilidade basal**: pacientes **livres de doença cardiovascular** e **não em uso de estatina** no início do seguimento
- **Método**: modelos de riscos proporcionais de Cox (Cox proportional hazards), com equações de risco **separadas para homens e mulheres**, avaliadas em **10 anos**
- **Desfecho primário**: doença cardiovascular incidente, registrada em qualquer uma de três fontes de dados vinculadas — **registro de clínica geral, registro de mortalidade ou registro de internação hospitalar**
- **Eventos na derivação**: **363.565 casos incidentes de doença cardiovascular**, ao longo de **50,8 milhões de pessoas-ano** de observação

## Variáveis do modelo

O artigo original separa explicitamente as variáveis **já presentes no QRISK2** das **variáveis novas testadas no QRISK3**, e diz quais delas efetivamente entraram no modelo final. Citação literal da fonte, traduzida:

**Já presentes no QRISK2** (mantidas no QRISK3): idade, etnia, índice de privação socioeconômica, pressão arterial sistólica, índice de massa corporal, razão colesterol total:HDL, tabagismo atual, história familiar de doença coronariana em parente de primeiro grau com menos de 60 anos, diabetes tipo 1, diabetes tipo 2, hipertensão tratada, artrite reumatoide, fibrilação atrial, doença renal crônica (estágio 4 ou 5).

**Variáveis novas testadas no QRISK3**: doença renal crônica em estágio **3, 4 ou 5** (ampliando o corte anterior, que só considerava estágio 4 ou 5), uma medida de **variabilidade da pressão arterial sistólica** (desvio-padrão de medidas repetidas), **migrânea**, uso de **corticosteroide**, **lúpus eritematoso sistêmico (LES)**, uso de **antipsicótico atípico**, **doença mental grave** e **HIV/AIDS**. Em homens, adicionalmente, **disfunção erétil** (diagnóstico ou tratamento).

**Resultado do teste de inclusão, citado literalmente**: *"todos os novos fatores de risco considerados atenderam aos critérios de inclusão do modelo, exceto o HIV/AIDS, que não foi estatisticamente significativo"*. Ou seja: **HIV/AIDS foi testado e excluído** — não é variável de entrada do QRISK3 final, ao contrário do que a lista de "novos fatores testados" poderia sugerir à primeira leitura. Todas as demais variáveis novas citadas acima (incluindo disfunção erétil em homens) atenderam ao critério e permanecem no modelo.

**Sobre os coeficientes numéricos**: o artigo do BMJ descreve as variáveis e reporta o desempenho, mas este documento não reproduz coeficientes nem permite reconstruir uma implementação clínica. O risco individual deve ser calculado com uma implementação mantida e validada para a versão pertinente; copiar coeficientes de uma calculadora de terceiros não assegura equivalência, atualização ou validação.

## Desempenho reportado na derivação/validação

Direto do abstract do registro (PMID 28536104), medido na coorte de validação (2,67 milhões de pacientes), separado por sexo:

- **Mulheres**: o algoritmo explicou **59,6%** da variação no tempo até o diagnóstico de doença cardiovascular (R²); estatística D = **2,48**; **C-estatístico de Harrell = 0,88**
- **Homens**: R² = **54,8%**; estatística D = **2,26**; **C-estatístico de Harrell = 0,86**
- **Conclusão explícita da fonte sobre o ganho global**: *"o desempenho geral dos algoritmos QRISK3 atualizados foi semelhante ao dos algoritmos QRISK2"* — ou seja, a discriminação agregada **não mudou de forma marcante** em relação à versão anterior; o ganho do QRISK3 está em capturar risco adicional em subgrupos definidos pelas variáveis novas (DRC estágio 3, migrânea, LES, uso de corticosteroide, antipsicótico atípico, doença mental grave, disfunção erétil em homens), não em elevar a discriminação média da população geral.

### Desempenho fora do Reino Unido (validação externa indireta)

Mortensen MB et al., *JAMA Cardiol*. 2022;7(8):836-843 (PMID 35793078), compararam diretrizes internacionais de prevenção primária — incluindo o critério **UK-NICE, que usa o QRISK3** — numa coorte populacional dinamarquesa contemporânea (Copenhagen General Population Study, 66.909 indivíduos, 40-69 anos, livres de DCV/diabetes/DRC/estatina no início, seguimento médio de 9,2 anos). Achado direto do abstract: a razão evento previsto/observado do **UK-QRISK3 foi 1,3** (ou seja, **superestimação de risco de ~30%** nessa população não britânica), contra 0,8 para o SCORE2 europeu e 1,3 para as Pooled Cohort Equations americanas. Pelo critério UK-NICE (QRISK3), **26% da coorte** seria elegível para estatina em prevenção primária, com sensibilidade de **51%** para detectar eventos definidos pelo SCORE2.

Entre as fontes citadas neste registro, a validação dinamarquesa é o dado externo confirmado. Elas não estabelecem validação ou recalibração brasileira; portanto, este texto não sustenta tratar a saída do QRISK3 como calibrada para a população brasileira.

## O que muda na prática — quando usar em vez de Framingham, PCE/PREVENT ou SCORE2

- O QRISK3 é a ferramenta de referência no contexto britânico. A recomendação vigente do NICE NG238 oferece atorvastatina 20 mg para prevenção primária quando o risco QRISK3 em 10 anos é de pelo menos 10% e admite considerar tratamento abaixo desse limiar quando a preferência informada o favorece ou o risco possa estar subestimado. O percentual integra a decisão clínica compartilhada e não deve ser usado de forma isolada. Livingstone S et al. (PMID 37061672) também empregam o limiar de 10% na população britânica do CPRD.
- Fora do Reino Unido — e em particular para uso em paciente brasileiro — o QRISK3 **não tem equivalente de recalibração publicado e confirmado nesta pesquisa** (diferente do que já existe para Framingham, PCE e SCORE2, com estudos brasileiros específicos como Fontenelle LF et al., PMID 40736124, citado no documento de PCE/PREVENT desta pasta). O único dado de comportamento fora do Reino Unido aqui confirmado é a superestimação de ~30% na coorte dinamarquesa (PMID 35793078) — não intercambiável com calibração brasileira.
- A vantagem clínica real do QRISK3 sobre as demais famílias é capturar **risco adicional em pacientes com comorbidades específicas** que os outros escores ignoram por completo: doença renal crônica estágio 3 (não só 4-5), lúpus, uso crônico de corticosteroide, antipsicótico atípico, doença mental grave, migrânea e disfunção erétil (homens). Nesses subgrupos, Framingham, PCE/PREVENT e SCORE2 tendem a **subestimar** risco por não terem essas variáveis como entrada.
- **Fibrilação atrial entra como variável de entrada do QRISK3** — mas para uma pergunta clínica diferente da dos escores de FA já cobertos nesta pasta: o QRISK3 usa a FA como um fator de risco a mais dentro do cálculo de risco cardiovascular **geral e de primeira ocorrência**; não substitui, e não deve ser confundido com, o **CHA2DS2-VA** (cha2ds2-va) ou os escores ATRIA (escores-atria-risco-de-avc-e-de-sangramento-na-fibrilacao-atrial), que estimam risco de **AVC especificamente em quem já tem FA diagnosticada**, para orientar anticoagulação.

## Armadilhas clínicas

- **Aplicar o QRISK3 fora da faixa etária de derivação (25-84 anos)** ou em quem já tem doença cardiovascular estabelecida ou já usa estatina — a coorte de derivação excluiu explicitamente ambos os grupos.
- **Assumir que HIV/AIDS é variável de entrada do QRISK3** porque aparece na lista de "novos fatores testados" — não é: o próprio artigo de derivação relata que HIV/AIDS **não atingiu significância estatística** e foi excluído do modelo final. Só a disfunção erétil (em homens) entre as variáveis "testadas fora do QRISK2" foi de fato incorporada, junto com DRC estágio 3, variabilidade da PAS, migrânea, corticosteroide, LES, antipsicótico atípico e doença mental grave.
- **Usar o percentual de saída do QRISK3 sem ajuste em população fora do Reino Unido** e tratá-lo como calibrado — o único dado de validação externa aqui confirmado (coorte dinamarquesa, PMID 35793078) mostra superestimação de ~30%; não há confirmação nesta pesquisa de comportamento em população brasileira.
- **Buscar a tabela de coeficientes numéricos em calculadora online e tratá-la como fonte primária confirmada** — o artigo de derivação no BMJ não publica a tabela de coeficientes no corpo do texto; qualquer reprodução de coeficientes vinda de implementação de terceiros é fonte secundária e não foi usada neste documento.
- **Confundir com o CHA2DS2-VA ou com os escores ATRIA/ABC de fibrilação atrial** — aqueles estimam risco de AVC (e de sangramento) em quem **já tem** FA diagnosticada, para decidir anticoagulação; o QRISK3 usa a FA apenas como uma das variáveis de entrada para estimar risco de **primeiro evento cardiovascular** na população geral. São perguntas clínicas diferentes, não escores concorrentes.
- **Comparar diretamente o percentual do QRISK3 com o do Framingham, da PCE/PREVENT ou do SCORE2 no mesmo paciente** e tratar a diferença como erro de cálculo — são coortes, desfechos e listas de variáveis diferentes; divergência é esperada, não indica que um dos escores está "errado".
- **Tratar "desempenho geral semelhante ao QRISK2"** como ausência de utilidade clínica do QRISK3 — a fonte é explícita de que a discriminação agregada não mudou muito, mas o ganho real está na reclassificação de subgrupos específicos definidos pelas variáveis novas, não na população geral.

## Escopo deste registro

Este é o registro **técnico**, centrado na derivação, validação e desempenho. O uso prático na atenção primária britânica, com entradas e limites de interpretação, está em [QRISK3 — risco cardiovascular total na atenção primária britânica](/biblioteca/qrisk3-risco-cardiovascular-total-na-atencao-primaria-britanica). Ambos permanecem não publicados até a validação editorial conjunta de sua complementaridade; nenhum implementa a equação.

## Tudo com Tudo

- [Framingham Risk Score (FRS)](/biblioteca/framingham-risk-score-frs)
- [Pooled Cohort Equations (ASCVD Risk Estimator) e as Equações PREVENT: Risco Cardiovascular em Prevenção Primária](/biblioteca/pooled-cohort-equations-e-equacoes-prevent-risco-cardiovascular-em-prevencao-primaria)
- [SCORE2 e SCORE2-OP](/biblioteca/score2-e-score2-op)
- [SCORE2 e SCORE2-OP — aplicabilidade e limites no paciente brasileiro](/biblioteca/score2-score2-op-aplicabilidade-e-limites-no-paciente-brasileiro)
- [SCORE2-Diabetes: Estimativa de Risco Cardiovascular em 10 Anos no Diabetes Tipo 2](/biblioteca/score2-diabetes-estimativa-de-risco-cardiovascular-em-10-anos-no-diabetes-tipo-2)
- [CHA2DS2-VA](/biblioteca/cha2ds2-va)
