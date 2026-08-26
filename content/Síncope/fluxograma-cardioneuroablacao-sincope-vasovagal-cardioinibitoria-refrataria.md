---
title: "Fluxograma: Indicação de Cardioneuroablação na Síncope Vasovagal Cardioinibitória Refratária (EHRA/HRS/APHRS/LAHRS 2024)"
slug: fluxograma-cardioneuroablacao-sincope-vasovagal-cardioinibitoria-refrataria
theme: "Síncope"
kind: fluxograma
fonte_producao: chatgpt
review_status: revisado
review_note: "Árvore construída a partir do documento já publicado e revisado 'cardioneuroablacao-na-sincope-reflexa-posicao-conjunta-ehra-hrs-aphrs-lahrs-2024.md' desta mesma pasta (posição do comitê redator, critérios de pausa que definem o subgrupo com algum dado favorável, distinção entre disfunção sinusal/BAV vagal isolado versus síncope vasovagal cardioinibitória, e o estudo de marcadores procedimentais de 2026), com os dois PMID/DOI reconferidos nesta sessão via PubMed E-utilities (esummary), não aceitos por citação de segunda mão. Corpus de Síncope conferido antes de escrever para não duplicar: os 5 fluxogramas existentes cobrem avaliação inicial, critérios de alto risco na emergência, investigação diferenciada no idoso, monitor de eventos implantável na síncope inexplicada recorrente e diagnóstico diferencial reflexa versus cardíaca — nenhum trata da indicação específica de cardioneuroablação em árvore de decisão; os dois documentos existentes sobre cardioneuroablação (posição conjunta 2024 e marca-passo versus CNA) são narrativos, não fluxograma."
source_refs: ["Aksu T, Brignole M, Calo L, Debruyne P, et al. Cardioneuroablation for the treatment of reflex syncope and functional bradyarrhythmias: A Scientific Statement of the European Heart Rhythm Association (EHRA) of the ESC, the Heart Rhythm Society (HRS), the Asia Pacific Heart Rhythm Society (APHRS) and the Latin American Heart Rhythm Society (LAHRS). Europace. 2024;26(8):euae206. DOI: 10.1093/europace/euae206. PMID: 39082698 — registro (título, autoria, revista, volume, PMCID PMC11350289) conferido no PubMed via esummary em 26/08/2026; errata publicada em Europace. 2025;27(2):euaf023, PMID 39932921, não incorporada a este fluxograma por não alterar os critérios de seleção aqui descritos.", "Vojnika J, Patel D, Enriquiez A, Hyman MC, Dixit S, Santangeli P, Nazarian S, Callans DJ, Frankel DS, Marchlinski FE, Markman TM. Physiological Markers of Effective Autonomic Denervation Are Associated With Outcomes After Cardioneuroablation for Vasovagal Syncope. JACC Clin Electrophysiol. 2026 Jun 23. DOI: 10.1016/j.jacep.2026.05.021. PMID: 42360261 — registro conferido no PubMed via esummary em 26/08/2026."]
---

# Fluxograma: Indicação de Cardioneuroablação na Síncope Vasovagal Cardioinibitória Refratária (EHRA/HRS/APHRS/LAHRS 2024)

A posição conjunta EHRA/HRS/APHRS/LAHRS 2024 é deliberadamente cautelosa: não autoriza recomendação
forte para a cardioneuroablação (CNA), e restringe o único subgrupo com algum dado favorável de
redução de síncope a critérios objetivos de pausa cardioinibitória, sempre depois de falha
comprovada das medidas não farmacológicas. Fora desse subgrupo — componente vasodepressor
dominante, ou disfunção sinusal/BAV vagal isolado sem síncope vasovagal associada — a indicação
não tem racional ou permanece investigacional, restrita a ensaio clínico controlado. Um estudo
observacional de 2026 (57 pacientes, coorte unicêntrica) quantifica essa cautela com número real:
44% de recorrência em seguimento médio de 2,2 anos, o que torna a decisão compartilhada — e não
apenas o preenchimento dos critérios de pausa — parte obrigatória do caminho até a indicação.

## Árvore de decisão

```mermaid
flowchart TD
  R0["Síncope reflexa vasovagal recorrente e grave, com investigação diagnóstica já concluída (ver documento de diagnóstico diferencial desta pasta)"] --> D1{"Medidas não farmacológicas de primeira linha (educação sobre gatilhos, hidratação e sal, manobras físicas de contrapressão) foram tentadas de forma adequada e falharam em prevenir a recorrência?"}
  D1 -->|"Não, ainda não otimizadas"| C1(["Otimizar primeiro as medidas não farmacológicas — ver documento de tratamento da síncope vasovagal recorrente desta pasta — antes de considerar qualquer terapia invasiva"])
  D1 -->|"Sim, falharam em prevenir recorrência"| D2{"Há documentação objetiva de componente cardioinibitório: pausa assistólica sintomática espontânea maior que 3 segundos (Holter/monitor de eventos implantável), OU pausa assintomática maior que 6 segundos por parada sinusal/BAV, OU síncope com assistolia maior que 3 segundos no tilt test?"}
  D2 -->|"Não, componente vasodepressor dominante ou pausa não documentada"| C2(["Cardioneuroablação sem racional fisiopatológico neste perfil — desnervar o vago não corrige a queda de resistência vascular periférica; manter tratamento conservador/farmacológico da síncope vasovagal e considerar monitor de eventos implantável se o diagnóstico permanecer incerto"])
  D2 -->|"Sim, critério cardioinibitório documentado"| D3{"Trata-se de disfunção do nó sinusal ou bloqueio atrioventricular de causa vagal extrínseca ISOLADO, sem síncope vasovagal cardioinibitória associada?"}
  D3 -->|"Sim, disfunção sinusal/BAV vagal isolado"| C3(["Indicação permanece investigacional — considerar cardioneuroablação apenas em contexto de ensaio clínico controlado, com decisão compartilhada, após falha comprovada da terapia conservadora"])
  D3 -->|"Não, é síncope vasovagal cardioinibitória propriamente dita"| D4{"Em decisão compartilhada, o paciente compreende que a evidência de eficácia é limitada (um único ensaio randomizado pequeno; coorte de 2026 mostrou 44% de recorrência em seguimento médio de 2,2 anos) e que faltam dados de segurança/eficácia de longo prazo?"}
  D4 -->|"Não aceita, ou decisão compartilhada não documentada"| C4(["Manter tratamento conservador da síncope reflexa; considerar marca-passo definitivo conforme critérios da ESC 2018 (Classe IIb, Nível B) — ver documento de marca-passo versus cardioneuroablação desta pasta"])
  D4 -->|"Sim, decisão compartilhada documentada"| C5(["Cardioneuroablação pode ser considerada, com seguimento estruturado (ECG, Holter, testes autonômicos; seguimento estendido de 3 a 5 anos) — informar ao paciente os marcadores procedimentais agudos associados a menor recorrência: resposta vagal na ablação do plexo ganglionar esquerdo, maior aumento da frequência sinusal intraprocedimento e resposta negativa ao teste da atropina ao final do procedimento"])

  classDef conduta fill:#eef6ef,stroke:#2f7a4f,color:#12301f;
  class C1,C2,C3,C4,C5 conduta;
```

## O que a árvore não mostra

- **A idade do paciente não entra como ramo binário.** A posição conjunta descreve que os dados
  favoráveis "se concentram" em pacientes jovens, mas isso é uma observação sobre a população
  estudada, não um critério de corte etário explícito para indicar ou excluir a CNA — por isso
  não virou nó de decisão. O contraste com a idade de 40 anos usada pela ESC 2021 de estimulação
  cardíaca para restringir marca-passo no fenótipo bradicárdico é contexto, tratado em prosa no
  documento de posição conjunta desta pasta, não critério de seleção da CNA em si.
- **O teste da atropina pré-procedimento não é um ramo de decisão.** Seu valor para selecionar
  quem se beneficia da CNA "ainda não está definido" segundo a posição de 2024 — historicamente
  foi usado para excluir doença intrínseca do nó sinusal/AV, não para prever benefício. O estudo
  de 2026 traz um dado novo, mas é sobre resposta ao teste **ao final** do procedimento associada
  a menor recorrência (achado prognóstico pós-procedimento), não critério de indicação prévia —
  por isso entra como informação a comunicar ao paciente na conduta final (C5), não como pergunta
  da árvore.
- **A técnica de guia da ablação (estimulação vagal extracardíaca versus outras) não está
  detalhada aqui.** O estudo de 2026 associa a estimulação vagal extracardíaca a maior incidência
  de taquicardia sinusal inapropriada sintomática (64% vs. 2%) — é dado de segurança do
  procedimento, relevante para a conversa de decisão compartilhada, mas não altera o caminho de
  indicação descrito nesta árvore.
- **Os riscos gerais do procedimento (acesso vascular, tamponamento, lesão de nó sinusal/AV,
  pericardite, entre outros) não estão listados como ramo** — são riscos de qualquer ablação por
  cateter atrial, tratados em prosa no documento de posição conjunta desta pasta, não critérios
  que mudam a indicação.
- **O algoritmo de escolha entre marca-passo e CNA quando ambos são tecnicamente elegíveis** (após
  a conduta C4) tem documento próprio nesta pasta — a árvore acima limita-se a apontar a
  alternativa estabelecida quando a CNA não é aceita ou a evidência não sustenta a indicação.
