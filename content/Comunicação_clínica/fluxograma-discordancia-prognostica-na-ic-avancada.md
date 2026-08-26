---
title: "Fluxograma: Discordância Prognóstica na Insuficiência Cardíaca Avançada"
slug: fluxograma-discordancia-prognostica-na-ic-avancada
theme: "Comunicação clínica"
kind: fluxograma
fonte_producao: chatgpt
review_status: revisado
review_note: "Verificado por Claude em 26/08/2026: fonte primaria conferida; conteudo derivado de documento(s) ja publicado(s) no acervo, listado(s) em source_refs."
source_refs:
  - "Documento já publicado no acervo (tema Comunicação clínica): 'Comunicação de Incerteza Prognóstica na Insuficiência Cardíaca Avançada' (slug: comunicacao-de-incerteza-prognostica-na-insuficiencia-cardiaca-avancada), de onde vêm a técnica Ask-Tell-Ask, a formulação 'planejar para o pior enquanto se tem esperança no melhor', o uso de faixa em vez de ponto e a orientação de revisitar a cada exacerbação."
  - "Documento já publicado no acervo (tema Comunicação clínica): 'Otimismo Discordante sobre Prognóstico na Insuficiência Cardíaca' (slug: otimismo-discordante-sobre-prognostico-na-insuficiencia-cardiaca), de onde vem o critério de discordância e a recomendação de basear decisão de terapia avançada em avaliação objetiva, não no otimismo relatado."
  - "Allen LA, Stevenson LW, Grady KL, et al. Decision making in advanced heart failure: a scientific statement from the American Heart Association. Circulation. 2012;125(15):1928-1952. DOI: 10.1161/CIR.0b013e31824f2173. PMID: 22392529."
  - "Murray SA, Kendall M, Boyd K, Sheikh A. Illness trajectories and palliative care. BMJ. 2005;330(7498):1007-1011. DOI: 10.1136/bmj.330.7498.1007. PMID: 15860828."
  - "Allen LA, Yager JE, Funk MJ, et al. Discordance between patient-predicted and model-predicted life expectancy among ambulatory patients with heart failure. JAMA. 2008;299(21):2533-2542. DOI: 10.1001/jama.299.21.2533. PMID: 18523222."
  - "Cascino TM, Herron G, Richards B, et al. Understanding of Prognosis and Estimation of Mortality in Ambulatory Patients With Heart Failure. JAMA Netw Open. 2026;9(3):e260328. DOI: 10.1001/jamanetworkopen.2026.0328. PMID: 41774443."
---

# Fluxograma: Discordância Prognóstica na Insuficiência Cardíaca Avançada

Esta árvore parte do achado central dos dois documentos-fonte: perguntar a expectativa de sobrevida do próprio paciente (Ask) e compará-la à avaliação objetiva de risco é o passo que detecta o otimismo discordante — presente em 33,1% de uma coorte de alto risco (Cascino et al., 2026) e associado a quase o dobro de mortalidade em 2 anos (HR ajustado 1,98). A partir dessa comparação, a árvore segue dois caminhos: reforçar a informação com as técnicas que a AHA nomeia (quando a expectativa é compatível), ou tratar o otimismo discordante como dado clínico relevante para a decisão de terapia avançada.

## Árvore de decisão

```mermaid
flowchart TD
  R0["Paciente com IC avançada em consulta de acompanhamento ou alta hospitalar"] --> N1["Perguntar a expectativa do próprio paciente sobre sua sobrevida/prognóstico (Ask)"]
  N1 --> D1{"A expectativa do paciente é compatível com a avaliação objetiva de risco (modelo validado + julgamento clínico)?"}

  D1 -->|"Sim, compatível (concordante ou pessimista)"| N2["Reforçar a informação com faixa de prognóstico, nunca número único, nomeando os dois mecanismos possíveis de morte (súbita e por falência progressiva de bomba) — Tell"]
  N2 --> D2{"Paciente consegue repetir com as próprias palavras o que entendeu (Ask final)?"}
  D2 -->|"Sim, retenção confirmada"| C1(["Documentar a conversa e o plano; revisitar a expectativa a cada nova exacerbação, sem esperar a próxima consulta agendada"])
  D2 -->|"Não, entendimento incompleto ou distorcido"| C2(["Repetir a informação em linguagem mais simples, com pausas frequentes, e verificar novamente antes de encerrar a conversa"])

  D1 -->|"Não, otimismo discordante (paciente estima sobrevida muito acima do modelo/julgamento clínico)"| D3{"Há decisão de terapia avançada em jogo (transplante, dispositivo de assistência ventricular)?"}
  D3 -->|"Sim"| C3(["Basear a decisão de terapia avançada na avaliação objetiva de risco, não no otimismo relatado pelo paciente, e comunicar essa diferença antes de decidir"])
  D3 -->|"Não, decisão não é sobre terapia avançada no momento"| N3["Nomear a incerteza como fato clínico compartilhado ('nunca podemos saber com certeza...'), usando a formulação 'planejar para o pior enquanto se tem esperança no melhor'"]
  N3 --> C4(["Revisitar a conversa de prognóstico na próxima exacerbação, sem tratar a recuperação parcial como sinal de melhora da trajetória"])

  classDef conduta fill:#eef6ef,stroke:#2f7a4f,color:#12301f;
  class C1,C2,C3,C4 conduta;
```

## Sobre os critérios usados nesta árvore

O critério de discordância segue a definição operacional do estudo mais recente: índice de estimativa (expectativa do paciente dividida pela sobrevida estimada pelo modelo) igual ou acima de 1,5 caracteriza otimismo discordante, presente em 98 dos 296 pacientes da coorte REVIVAL — 33,1% (Cascino et al., JAMA Netw Open 2026, PMID 41774443). A recomendação de basear a decisão de terapia avançada em avaliação objetiva, não no relato otimista, é a conclusão textual dos próprios autores desse estudo, reforçada pelo achado de que a maior mortalidade associada ao otimismo discordante (HR 1,98) não foi explicada por menor acesso a transplante ou dispositivo de assistência ventricular.

A bifurcação sobre recuperação parcial pós-exacerbação segue diretamente a advertência de Murray et al. (BMJ 2005, PMID 15860828): na trajetória de falência de órgão, o paciente "geralmente sobrevive a muitos desses episódios", e cada "dia bom" que sucede uma descompensação não é evidência de mudança de trajetória — é o próprio formato esperado da doença. Tratar a recuperação parcial como sinal de bom prognóstico é listado como armadilha clínica no documento-fonte.

As técnicas Ask-Tell-Ask, a faixa de prognóstico em vez de número único e a formulação "planejar para o pior enquanto se tem esperança no melhor" são nomeadas textualmente na declaração científica da American Heart Association (Allen et al., Circulation 2012, PMID 22392529), que também documenta por que nem julgamento clínico nem modelo validado bastam sozinhos: o erro de previsão maior que o dobro ou menor que a metade da sobrevida real "permanece próximo de 50% sob premissas realistas".