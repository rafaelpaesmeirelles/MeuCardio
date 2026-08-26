---
title: "Fluxograma: recorrência de fibrilação atrial após ablação por cateter — blanking, cardioversão, antiarrítmico e reablação"
slug: fluxograma-recorrencia-fa-pos-ablacao-manejo-blanking-reablacao
theme: "Fibrilação atrial"
kind: fluxograma
fonte_producao: chatgpt
review_status: revisado
review_note: "Verificado por Claude em 26/08/2026: PMID 38587017 conferido via PubMed E-utilities (esearch/esummary/efetch) — título, autoria (Tzeis S et al.) e periódico (Europace 2024;26(4):euae043) batendo exatamente. Texto integral obtido via Europe PMC REST API (fullTextXML, PMCID PMC11000153) e lido diretamente nas seções 9.5.1 a 9.5.3 (Early recurrences after ablation — postablation blanking period), não resumido de memória nem de fonte secundária. Desta leitura vêm: a atualização do período de blanking de 3 meses para 8 semanas (decisão explícita do writing group, citada no texto), a orientação de cardioversão elétrica preferencialmente dentro de 30 dias da recorrência com pré-tratamento farmacológico antes de nova tentativa, a frase literal de que reablação dentro do blanking 'não é recomendada a menos que [as recorrências] sejam recorrentes, muito sintomáticas e refratárias a antiarrítmicos e cardioversão' (mesmo critério aplicado, por analogia textual do próprio documento em outra seção sobre flutter pós-ablação, ao ramo de recorrência tardia refratária desta árvore), e o dado de reconexão de veia pulmonar em mais de 80% dos casos de recorrência após crioablação de primeira geração (>50% com mais de uma veia), usado para justificar o alvo da reablação tardia."
source_refs:
  - "Tzeis S, Gerstenfeld EP, Kalman J, Saad EB, Sepehri Shamloo A, Andrade JG, et al. 2024 European Heart Rhythm Association/Heart Rhythm Society/Asia Pacific Heart Rhythm Society/Latin American Heart Rhythm Society Expert Consensus Statement on Catheter and Surgical Ablation of Atrial Fibrillation. Europace. 2024;26(4):euae043. DOI: 10.1093/europace/euae043. PMID: 38587017. PMCID: PMC11000153. Co-publicado em Heart Rhythm. 2024;21(9):e31-e149. DOI: 10.1016/j.hrthm.2024.03.017. PMID: 38597857."
  - "Texto integral consultado via Europe PMC REST API (fullTextXML), seções 9.5.1 (incidência e fisiopatologia da recorrência precoce), 9.5.2 (duração do período de blanking) e 9.5.3 (manejo da recorrência precoce — cardioversão elétrica e reablação precoce)."
---

# Fluxograma: recorrência de fibrilação atrial após ablação por cateter — blanking, cardioversão, antiarrítmico e reablação

O catálogo já tem seis fluxogramas de FA, mas nenhum cobre o recorte mais comum no
seguimento pós-ablação: o que fazer diante de uma recorrência documentada depois do
procedimento. Os fluxogramas existentes tratam da indicação da primeira ablação, da
FA de início recente no pronto-socorro, da cardioversão eletiva e da anticoagulação
periprocedimento — nenhum trata da decisão entre observar, cardioverter, ajustar
antiarrítmico ou reablacionar quando a arritmia volta.

O consenso EHRA/HRS/APHRS/LAHRS 2024 sobre ablação de FA (Tzeis et al., Europace
2024) atualizou um ponto central desse manejo: o período de blanking — a janela
inicial em que a recorrência não é contada como falha do procedimento — passou de
3 meses para **8 semanas**, decisão explícita do grupo redator para reduzir a
exposição desnecessária a reablação precoce em pacientes cuja recorrência é
transitória. A árvore abaixo segue essa atualização e a lógica de manejo descrita
nas seções 9.5.1 a 9.5.3 do documento: dentro do blanking, cardioversão é
priorizada sobre reablação; fora do blanking, a decisão passa por otimização de
antiarrítmico antes de indicar um novo procedimento, orientada pelo fato de que a
reconexão de veia pulmonar é o achado mais comum no reprocedimento.

## Árvore de decisão

```mermaid
flowchart TD
  R["Paciente com recorrência documentada de arritmia atrial (FA, flutter atrial ou taquicardia atrial) após ablação por cateter índice de FA"] --> D1{"A recorrência ocorre dentro das primeiras 8 semanas após o procedimento (período de blanking, consenso EHRA/HRS/APHRS/LAHRS 2024)?"}
  D1 -->|"Sim, dentro do blanking (≤ 8 semanas)"| B1["Recorrência dentro do blanking não é considerada falha do procedimento<br/>Reablação não é indicada rotineiramente nesta fase"]
  D1 -->|"Não, recorrência tardia (> 8 semanas)"| D5{"Na reavaliação pós-blanking (ECG de 12 derivações e/ou monitorização de ritmo dirigida por sintomas), a recorrência é sintomática e compromete a qualidade de vida do paciente?"}
  B1 --> D2{"O episódio é sintomático e sustentado (FA ou flutter persistente, sem reversão espontânea)?"}
  D2 -->|"Não, assintomático ou autolimitado"| C1(["Conduta expectante: manter controle de frequência e anticoagulação já estabelecidos<br/>Seguimento clínico de rotina em 2-3 meses; recorrência dentro do blanking não altera a interpretação de sucesso do procedimento"])
  D2 -->|"Sim, sintomático e sustentado"| B2["Considerar cardioversão elétrica, preferencialmente dentro de 30 dias do início da recorrência<br/>Se recidivar, pré-tratamento farmacológico e aguardar algumas semanas antes de nova cardioversão"]
  B2 --> D3{"Mesmo após a cardioversão (com pré-tratamento farmacológico se indicado), a arritmia permanece recorrente, muito sintomática e refratária tanto ao antiarrítmico quanto à cardioversão?"}
  D3 -->|"Não, controlada com cardioversão e/ou antiarrítmico"| C2(["Manter seguimento clínico dentro do período de blanking<br/>Reavaliar formalmente ao final da 8ª semana antes de qualquer decisão sobre reablação"])
  D3 -->|"Sim, refratária a antiarrítmico e a cardioversão"| C3(["Reablação precoce pode ser considerada mesmo ainda dentro do blanking, reservada a casos recorrentes, muito sintomáticos e refratários a antiarrítmico e a cardioversão"])
  D5 -->|"Não, assintomática ou pouco sintomática"| C4(["Manter seguimento clínico anual com ECG de 12 derivações<br/>Ajustar apenas controle de frequência e anticoagulação conforme risco tromboembólico; reablação não indicada neste momento"])
  D5 -->|"Sim, sintomática e/ou compromete qualidade de vida"| D6{"A recorrência permanece recorrente, muito sintomática e refratária ao antiarrítmico otimizado, ou o paciente não é candidato/recusa antiarrítmico?"}
  D6 -->|"Não, ainda não tentou (ou pode otimizar) terapia farmacológica"| C5(["Iniciar ou otimizar antiarrítmico em decisão compartilhada com o paciente<br/>Reavaliar resposta clínica antes de indicar novo procedimento"])
  D6 -->|"Sim, refratária ao antiarrítmico otimizado ou não é candidato/recusa"| D7{"O paciente é candidato clínico a novo procedimento (sem contraindicação proibitiva) e aceita repetir a ablação?"}
  D7 -->|"Não, contraindicação clínica ou recusa do paciente"| C6(["Manter/otimizar terapia farmacológica de controle de ritmo ou de frequência<br/>Reavaliação periódica dentro da via de decisão compartilhada"])
  D7 -->|"Sim, candidato e aceita repetir o procedimento"| C7(["Indicar reablação (redo) por cateter<br/>Reconexão de veia(s) pulmonar(es) é o achado mais comum no reprocedimento — descrita em mais de 80% dos casos de recorrência após crioablação de primeira geração, com reconexão de mais de uma veia em mais da metade — e deve ser buscada e tratada como alvo primário"])

  classDef conduta fill:#eef6ef,stroke:#2f7a4f,color:#12301f;
  class C1,C2,C3,C4,C5,C6,C7 conduta;
```

## O que a árvore não mostra

**O corte de 8 semanas substitui o de 3 meses usado até 2017/2021, e é decisão
explícita do grupo redator, não achado isolado de um único estudo.** O documento
cita a razão diretamente: ausência de recorrência nas primeiras 3 meses já
predizia ~90% de chance de permanecer livre de arritmia em 12 meses (dado de
Calkins et al., citado no próprio consenso), mas o objetivo do corte mais curto é
reduzir a "má classificação" de pacientes com recorrência precoce transitória —
e a exposição desnecessária deles a reablação. Serviço que ainda usa a janela de
3 meses não está seguindo uma prática abandonada por acaso; é uma atualização
recente (2024) que pode não ter chegado a toda a prática clínica ainda.

**A cardioversão dentro do blanking tem evidência conflitante entre os estudos
citados no próprio consenso**, e a recomendação de fazê-la preferencialmente
dentro de 30 dias da recorrência é uma leitura de conjunto do writing group, não
um resultado único e forte. Estudos observacionais retrospectivos mostram
resultado favorável e neutro lado a lado — o documento é transparente sobre essa
inconsistência antes de fazer a recomendação prática.

**O dado de reconexão de veia pulmonar (>80%, >1 veia em mais da metade) vem
especificamente da experiência com o balão de crioablação de primeira geração**,
citado no consenso ao descrever a evolução da tecnologia — não é necessariamente
a mesma proporção com radiofrequência de ponta de contato ou ablação por campo
pulsado (PFA), tecnologias mais recentes com taxas de durabilidade de isolamento
diferentes. A árvore usa o dado como justificativa geral de que a veia pulmonar
continua sendo o alvo mais produtivo na reablação, não como número que se aplica
igualmente a qualquer técnica usada no procedimento índice.

**Esta árvore não decide qual antiarrítmico usar, nem cobre a escolha entre
manter ou suspender a anticoagulação após reablação bem-sucedida** — esse segundo
tema já está coberto pelo documento publicado
`alone-af-suspensao-da-anticoagulacao-apos-ablacao-bem-sucedida-de-fibrilacao-atrial.md`
neste mesmo acervo. Também não substitui os fluxogramas já existentes de
indicação da primeira ablação (`fluxograma-indicacao-ablacao-cateter-fa-esc-2024`)
nem de cardioversão eletiva com anticoagulação periprocedimento
(`fluxograma-cardioversao-eletiva-anticoagulacao-periprocedimento`) — esta árvore
começa depois que o procedimento índice já foi feito e a arritmia recorreu.
