---
title: "Fluxograma: Lipoproteína(a) Elevada — Rastreamento e Estratificação de Risco Cardiovascular (Consenso EAS 2022 / ESC-EAS 2025)"
slug: fluxograma-lipoproteina-a-elevada-rastreamento-e-estratificacao-de-risco-eas-2022
theme: "Prevenção e lipídios"
kind: fluxograma
fonte_producao: chatgpt
review_status: revisado
review_note: "Verificado por Claude em 26/08/2026: conferido o corpus (content/Prevenção_e_lipídios/) antes de escrever para não duplicar — os dois fluxogramas de hipercolesterolemia familiar/DLCN e de hipertrigliceridemia grave/pancreatite já existem no acervo, então este documento cobre um terceiro ângulo ainda faltante (Lp(a) elevada), que só tinha cobertura em prosa, sem árvore de decisão. Os dois PMIDs citados foram reverificados nesta sessão via PubMed E-utilities (esummary.fcgi): PMID 36036785 (Kronenberg F et al., Eur Heart J. 2022;43(39):3925-3946, DOI 10.1093/eurheartj/ehac361) bate exatamente com título, revista, volume, fascículo, páginas e DOI já usados e verificados no documento em prosa já publicado no acervo (lipoproteina-a-rastreamento-populacional-ao-menos-uma-vez-na-vida-consenso-eas-2022.md); PMID 40878289 (2025 Focused Update of the 2019 ESC/EAS Guidelines for the management of dyslipidaemias, Eur Heart J. 2025;46(42):4359-4378, DOI 10.1093/eurheartj/ehaf190) também confere. Os cortes de mg/dL e nmol/L, as indicações de dosagem pediátrica e de cascata familiar, e a ausência de terapia específica aprovada vêm literalmente do consenso EAS 2022, mesma fonte já usada no documento em prosa correspondente; nenhum PMID/DOI foi criado nesta sessão."
source_refs: ["Kronenberg F, Mora S, Stroes ESG, Ference BA, Arsenault BJ, Berglund L, et al. Lipoprotein(a) in atherosclerotic cardiovascular disease and aortic stenosis: a European Atherosclerosis Society consensus statement. Eur Heart J. 2022;43(39):3925-3946. DOI: 10.1093/eurheartj/ehac361. PMID: 36036785. PMCID: PMC9639807 — fonte primária dos cortes de risco (menor que 30/entre 30-50/maior que 50 mg/dL, e os equivalentes em nmol/L), da recomendação de dosagem única na vida adulta com as exceções de repetição (doença renal, hepática, infecção aguda), das indicações pediátricas dirigidas, dos critérios de testagem em cascata e da ausência de terapia farmacológica específica aprovada, usados nesta árvore.", "Mach F, Koskinas KC, Roeters van Lennep JE, et al. 2025 Focused Update of the 2019 ESC/EAS Guidelines for the management of dyslipidaemias. Eur Heart J. 2025;46(42):4359-4378. DOI: 10.1093/eurheartj/ehaf190. PMID: 40878289 — recomendação de rastreamento de Lp(a) ao menos uma vez na vida, mantida nesta árvore como reforço da recomendação do consenso EAS 2022.", "Derivado, para os cortes de risco e as indicações de dosagem, do documento em prosa já publicado no acervo (lipoproteina-a-rastreamento-populacional-ao-menos-uma-vez-na-vida-consenso-eas-2022.md, Prevenção e lipídios), cuja fonte primária é a mesma citada acima."]
---

# Fluxograma: Lipoproteína(a) Elevada — Rastreamento e Estratificação de Risco Cardiovascular (Consenso EAS 2022 / ESC-EAS 2025)

A lipoproteína(a) — Lp(a) — é determinada em mais de 90% por variabilidade genética e se mantém estável ao longo da vida adulta, o que torna sua dosagem diferente de LDL-colesterol ou triglicerídeos: não é exame de seguimento seriado, é exame de uma vez na vida. Este fluxograma organiza duas decisões em sequência: primeiro, quando dosar (e quando não repetir uma dosagem já feita); depois, uma vez obtido o valor, como ele reclassifica o risco cardiovascular e calibra a intensidade do tratamento dos demais fatores modificáveis — já que não existe hoje terapia farmacológica específica para a própria Lp(a) com desfecho cardiovascular comprovado.

**O que a árvore não resolve sozinha**: os cortes de 30 e 50 mg/dL (75 e 125 nmol/L) são simplificação pragmática de uma relação de risco contínua — o próprio consenso descreve risco crescente por percentil populacional (75º, 90º, 95º), sem um único limiar biológico abrupto. A conversão entre mg/dL e nmol/L não é exata (varia com o tamanho da isoforma de apolipoproteína(a) de cada indivíduo).

## Árvore de decisão

```mermaid
flowchart TD
  N0["Adulto em avaliação de risco cardiovascular"] --> D1{"Já existe valor de Lp(a) medido em<br/>condição válida (fora de doença renal/hepática<br/>ou infecção aguda em curso)?"}

  D1 -->|"Sim"| N1["Usar o valor mais recente disponível;<br/>repetição da dosagem não é indicada<br/>rotineiramente (exceto doença renal/hepática<br/>ou infecção aguda no momento da coleta)"]
  N1 --> D2{"Valor de Lp(a)?"}

  D1 -->|"Não, ou o único valor disponível foi<br/>obtido em vigência de doença renal/<br/>hepática ou infecção aguda"| D3{"Critério para indicar a dosagem agora?"}

  D3 -->|"Adulto, sem critério especial<br/>(dosagem universal recomendada<br/>ao menos uma vez na vida)"| C1(["Solicitar Lp(a) agora; ao receber o<br/>resultado, interpretar pelos cortes de<br/>risco de mg/dL e nmol/L numa nova<br/>avaliação"])
  D3 -->|"Criança ou adolescente com AVC<br/>isquêmico prévio, ou pai/mãe com<br/>doença aterosclerótica prematura"| C2(["Solicitar Lp(a) (indicação pediátrica<br/>dirigida, não rastreamento universal<br/>infantil); interpretar pelo mesmo corte<br/>do adulto ao receber o resultado"])
  D3 -->|"Nenhum critério de indicação<br/>presente no momento"| C3(["Não indicar dosagem de rotina<br/>neste momento"])

  D2 -->|"Menor que 30 mg/dL<br/>(menor que 75 nmol/L)"| C4(["Baixa probabilidade de contribuição<br/>relevante da Lp(a) para o risco<br/>cardiovascular; manter a estratificação<br/>de risco padrão (SCORE2/Pooled Cohort<br/>Equations); repetir a dosagem não é<br/>indicado rotineiramente"])
  D2 -->|"De 30 a 50 mg/dL (75 a 125<br/>nmol/L) — zona intermediária"| C5(["Contribuição incerta para o risco;<br/>considerar a Lp(a) no conjunto dos<br/>demais fatores ao calibrar a<br/>intensidade do tratamento de LDL-C,<br/>pressão arterial e tabagismo"])
  D2 -->|"Maior que 50 mg/dL (maior que<br/>125 nmol/L) — fator de risco<br/>relevante"| D4{"Doença cardiovascular aterosclerótica<br/>progressiva apesar do manejo otimizado<br/>dos demais fatores de risco?"}

  D4 -->|"Sim"| C6(["Encaminhar a centro especializado em<br/>lipidologia; considerar aférese de<br/>lipoproteínas — não há hoje terapia<br/>farmacológica específica aprovada para<br/>reduzir a Lp(a) com desfecho<br/>cardiovascular comprovado; manter os<br/>fatores modificáveis no alvo mais<br/>agressivo"])
  D4 -->|"Não"| D5{"Familiar de 1º grau com<br/>hipercolesterolemia familiar, história<br/>familiar de Lp(a) muito elevada, ou<br/>história pessoal/familiar de doença<br/>aterosclerótica prematura?"}

  D5 -->|"Sim"| C7(["Intensificar controle de LDL-C, pressão<br/>arterial e tabagismo; indicar testagem<br/>em cascata dos familiares de 1º grau"])
  D5 -->|"Não"| C8(["Intensificar controle de LDL-C, pressão<br/>arterial e tabagismo; reclassificar o<br/>risco cardiovascular global<br/>considerando a Lp(a) elevada"])

  classDef conduta fill:#eef6ef,stroke:#2f7a4f,color:#12301f;
  class C1,C2,C3,C4,C5,C6,C7,C8 conduta;
```

## O que a árvore não mostra

**Os cortes de 30/50 mg/dL (75/125 nmol/L) são simplificação prática de uma relação contínua.** O consenso EAS 2022 descreve risco crescente por percentil populacional — acima do 75º percentil já há associação com estenose aórtica valvar e infarto do miocárdio; acima do 90º, com insuficiência cardíaca; acima do 95º, com mortalidade cardiovascular e AVC isquêmico. Não existe um único patamar biológico abrupto abaixo do qual não há risco algum.

**A mediana populacional de Lp(a) varia por ancestralidade** — o consenso cita dados do UK Biobank com mediana de 75 nmol/L em indivíduos de ascendência negra contra 19,7 nmol/L em ascendência branca. Aplicar o mesmo corte absoluto sem essa ressalva pode super ou subestimar quantas pessoas de cada grupo caem acima do corte de risco; a árvore usa os cortes pragmáticos do consenso, sem essa estratificação.

**Não existe hoje terapia farmacológica específica aprovada para reduzir a Lp(a) com desfecho cardiovascular comprovado** — por isso a conduta em risco aumentado não é "tratar a Lp(a)", é intensificar o tratamento dos fatores que já são modificáveis (LDL-C, pressão arterial, tabagismo), calibrado pelo risco cardiovascular global E pelo nível de Lp(a) juntos.

**A conversão entre mg/dL e nmol/L não é exata** — o tamanho da isoforma de apolipoproteína(a) varia entre indivíduos, então não existe fator de conversão fixo simples entre as duas unidades; os pares de corte desta árvore (30/75, 50/125) são os que o próprio consenso reporta lado a lado, não uma conversão calculada.

**Esta árvore não cobre gestantes, hipercolesterolemia familiar homozigota nem terapias experimentais em investigação** (siRNA como olpasirana e zerlasirana, antisense como pelacarsen, inibidor oral como muvalaplin) — nenhuma delas tem hoje aprovação regulatória nem desfecho cardiovascular comprovado; ver os documentos específicos desta pasta para o estágio de desenvolvimento de cada uma.
