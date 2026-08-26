---
title: "Fluxograma: SCA sem supra de ST — timing da estratégia invasiva (ESC 2023)"
slug: fluxograma-sca-sem-supra-timing-da-estrategia-invasiva-esc-2023
theme: "Doença coronariana"
kind: fluxograma
summary: "Na SCA sem supra de ST, a diretriz ESC 2023 separa três velocidades para a angiografia — imediata, precoce em menos de 24 h e seletiva — a partir de critérios de risco muito alto e de alto risco; o fluxograma organiza essa escolha e mostra o que fazer no ramo seletivo, em que o teste não invasivo decide se a angiografia acontece."
review_status: revisado
review_note: "Produção científica assistida (Claude, 26/08/2026); pendente de revisão independente e validação médica final. Conferido nesta sessão contra o texto integral da diretriz ESC 2023 de SCA (PDF do Eur Heart J 2023;44:3720-3826, seções 5.2.2 a 5.2.4, Figura 8, Recommendation Table 2 e Recommendation Table 4, além da tabela de recomendações revisadas em relação a 2020): critérios de risco muito alto e de alto risco, corte de GRACE maior que 140, classes e níveis de evidência (imediata I C, invasiva intra-hospitalar em alto risco I A, precoce em menos de 24 h IIa A, seletiva I A, angio-TC ou imagem de estresse na suspeita com troponina não elevada IIa A). Complementos lidos: 10 commandments da diretriz (Eur Heart J 2024), endosso da NVVC no Netherlands Heart Journal e metanálise de dados individuais de Jobs, Collet e Thiele (EHJ-ACVC 2023) — desta última só foi lida a síntese, não o texto integral. Derivado dos documentos já publicados sindrome-coronariana-aguda-timing-invasivo-e-dapt-esc-2023 e sindrome-coronariana-aguda-estratificacao-de-risco-grace-complemento-numerico; não repete os ramos de STEMI e de troponina do fluxograma-sindrome-coronariana-aguda-esc-2023. Verificação adversarial independente (Claude, 26/08/2026): texto do PDF da diretriz reextraído e conferido linha a linha (Tabela 3, Tabela 5 de recomendações revisadas, Figuras 4 e 8, Recommendation Tables 2 e 4, seções 5.2.2-5.2.4 e 5.4.1); DOI e PMID da diretriz, DOI do NVVC (texto integral via PMC11413259) e citações dos 10 commandments e de Jobs/Collet/Thiele conferidos no Crossref, PubMed e Europe PMC; corrigida a atribuição de origem do prazo de 2 h (diretriz ESC 2020 de NSTE-ACS, seção 6.1.2.1, confirmada no sumário do artigo) e a atribuição da nota sobre troponina não atrasar a triagem (nota da Figura 4, não Figura 8); acrescentados volume, páginas e PMID do endosso NVVC."
source_refs:
  - "Byrne RA, Rossello X, Coughlan JJ, et al. 2023 ESC Guidelines for the management of acute coronary syndromes. Eur Heart J. 2023;44(38):3720-3826. DOI: 10.1093/eurheartj/ehad191. PMID: 37622654. Texto integral lido no PDF espelhado em https://www.uniklinik-ulm.de/fileadmin/default/09_Sonstige/Klinische-Chemie/Downloads/ESC_Guideline_ACS_2023.pdf (seções 5.2.2-5.2.4, Figura 8, Recommendation Tables 2 e 4)."
  - "'10 commandments' for the 2023 ESC Guidelines for the management of acute coronary syndromes. Eur Heart J. 2024;45(14):1193-1195. https://academic.oup.com/eurheartj/article/45/14/1193/7516285"
  - "Jobs A, Collet JP, Thiele H. Timing of invasive coronary angiography in non-ST-elevation acute coronary syndrome: an updated individual patient data meta-analysis. Eur Heart J Acute Cardiovasc Care. 2023;12(6):374-375. https://academic.oup.com/ehjacc/article/12/6/374/7243212"
  - "2023 European Society of Cardiology guidelines for the management of acute coronary syndromes: statement of endorsement by the NVVC. Neth Heart J. 2024;32(10):338-345. DOI: 10.1007/s12471-024-01896-2. PMID: 39254829. PMC11413259. https://link.springer.com/article/10.1007/s12471-024-01896-2"
  - "Derivado de sindrome-coronariana-aguda-timing-invasivo-e-dapt-esc-2023.md e de sindrome-coronariana-aguda-estratificacao-de-risco-grace-complemento-numerico.md, já publicados no acervo (Doença coronariana)."
---

# Fluxograma: SCA sem supra de ST — timing da estratégia invasiva (ESC 2023)

Na SCA sem supra de ST, o exame, o cateterismo e os fármacos são praticamente os mesmos
para todos os pacientes; o que a diretriz ESC 2023 decide, de fato, é **quando** levar cada
um à hemodinâmica. O fluxograma geral já publicado nesta pasta
(fluxograma-sindrome-coronariana-aguda-esc-2023) separa STEMI de NSTE-ACS e aplica o
algoritmo 0h/1h de troponina. Este aprofunda apenas o passo seguinte: com o diagnóstico de
trabalho de NSTE-ACS estabelecido, escolher entre estratégia invasiva **imediata**,
**precoce em menos de 24 h** e **seletiva** — e, no ramo seletivo, o que decide se a
angiografia acontece ou não.

A diretriz define as três estratégias na sua Tabela 3: invasiva imediata é angiografia de
emergência, "o mais rápido possível", com ICP ou cirurgia da artéria culpada se indicada;
invasiva precoce é angiografia em menos de 24 h do diagnóstico de SCA; invasiva seletiva é
angiografia decidida por avaliação clínica e/ou teste não invasivo.

## Árvore de decisão

```mermaid
flowchart TD
  R0["Diagnóstico de trabalho de SCA sem supra persistente de ST<br/>ECG feito, troponina ultrassensível colhida"]
  D1{"Algum critério de risco muito alto?<br/>instabilidade hemodinâmica ou choque, dor recorrente<br/>ou refratária, IC aguda por isquemia, arritmia com risco<br/>de vida ou parada cardíaca, complicação mecânica,<br/>alterações dinâmicas recorrentes de ST ou T"}
  D2{"Paciente já está em centro com ICP?"}
  C1(["Estratégia invasiva imediata<br/>angiografia de emergência e ICP ou CRM<br/>da artéria culpada se indicada"])
  C2(["Transferência imediata para centro com ICP<br/>angiografia de emergência na chegada"])
  D3{"Algum critério de alto risco?<br/>IAMSSST confirmado pelo algoritmo ESC de troponina,<br/>GRACE acima de 140, supra transitório de ST,<br/>alterações dinâmicas de ST ou T"}
  D4{"Paciente é candidato a<br/>angiografia invasiva?"}
  C3(["Abordagem seletiva por decisão clínica<br/>tratamento antitrombótico e anti-isquêmico<br/>otimizado, sem angiografia de rotina"])
  P1["Estratégia invasiva durante a internação<br/>iniciar antitrombóticos e monitorização"]
  D5{"Angiografia em menos de 24 h<br/>do diagnóstico é viável?"}
  C4(["Estratégia invasiva precoce<br/>angiografia em menos de 24 h, com transferência<br/>precoce se estiver em centro sem ICP"])
  C5(["Estratégia invasiva intra-hospitalar<br/>angiografia no menor prazo logístico possível,<br/>sem alta antes do cateterismo"])
  D6{"Índice de suspeita de angina instável<br/>ou de SCA sem supra?"}
  C6(["Estratégia invasiva durante a internação<br/>angiografia antes da alta"])
  P2["Estratégia invasiva seletiva<br/>teste não invasivo: imagem de estresse<br/>ou angiotomografia de coronárias"]
  D7{"Isquemia induzível ou doença<br/>coronariana obstrutiva na angio-TC?"}
  C7(["Angiografia invasiva eletiva<br/>e revascularização se indicada"])
  C8(["Sem angiografia<br/>manejo como síndrome coronariana crônica<br/>ou investigar diagnóstico alternativo"])

  R0 --> D1
  D1 -->|"Sim"| D2
  D2 -->|"Sim"| C1
  D2 -->|"Não"| C2
  D1 -->|"Não"| D3
  D3 -->|"Sim"| D4
  D4 -->|"Não"| C3
  D4 -->|"Sim"| P1
  P1 --> D5
  D5 -->|"Sim"| C4
  D5 -->|"Não"| C5
  D3 -->|"Não"| D6
  D6 -->|"Alto"| C6
  D6 -->|"Baixo"| P2
  P2 --> D7
  D7 -->|"Sim"| C7
  D7 -->|"Não"| C8

  classDef conduta fill:#eef6ef,stroke:#2f7a4f,color:#12301f;
  class C1,C2,C3,C4,C5,C6,C7,C8 conduta;
```

O que vale para todos os ramos e ficou fora do diagrama: terapia antitrombótica e anti-isquêmica desde o diagnóstico de trabalho, ecocardiograma de emergência em quem chega em choque ou com suspeita de complicação mecânica (Classe I, nível C) e reavaliação contínua — paciente do ramo seletivo que volta a ter dor ou muda o ECG sobe de ramo.

## Ramo 1 — risco muito alto: invasiva imediata

Basta **um** critério. A Recommendation Table 4 lista: instabilidade hemodinâmica ou choque cardiogênico; dor torácica recorrente ou refratária apesar do tratamento clínico; arritmia intra-hospitalar com risco de vida; complicação mecânica do infarto; insuficiência cardíaca aguda presumidamente secundária a isquemia em curso; alterações dinâmicas recorrentes de ST ou onda T, particularmente com supra intermitente. O texto da seção 5.2.2 acrescenta parada cardíaca após a apresentação. A recomendação é **Classe I, nível C**.

O ponto que mais confunde: a diretriz 2023 não fixa número de horas para "imediata" — define-a como angiografia de emergência, "o mais rápido possível". O prazo de **menos de 2 horas**, que o documento derivado deste acervo mantém, não consta na Tabela 3 nem na Recommendation Table 4 de 2023 — o número vem da diretriz ESC 2020 de SCA sem supra de ST (Collet et al., Eur Heart J 2021;42(14):1289-1367), cuja seção 6.1.2.1 se intitula "Immediate invasive strategy (<2 h)", e o endosso da NVVC de 2024 ainda o usa como título de seção; a ESC 2023 substituiu o prazo por "de emergência, o mais rápido possível". Na Figura 8, quem está em centro sem ICP com critério de risco muito alto é **transferido imediatamente**; a nota da Figura 4 acrescenta que o resultado da troponina não é necessário para essa triagem inicial e não deve atrasá-la. O choque cardiogênico tem manejo próprio — ver choque-cardiogenico-na-sindrome-coronariana-aguda-culprit-shock-e-iabp-shock-ii.

## Ramo 2 — alto risco: invasiva na internação, precoce se possível

Também basta um critério. O que mudou em 2023 é a força da recomendação sobre o prazo:

| Recomendação | ESC 2020 | ESC 2023 |
|---|---|---|
| Estratégia invasiva durante a internação em alto risco ou alta suspeita de angina instável | — | Classe I, nível A |
| Estratégia invasiva precoce, em menos de 24 h, em alto risco | Classe I, nível A ("é recomendada") | Classe IIa, nível A ("deve ser considerada") |

Os quatro critérios de alto risco de 2023: diagnóstico confirmado de IAMSSST pelos algoritmos ESC de troponina ultrassensível; alterações dinâmicas de ST ou onda T; supra transitório de ST; **GRACE acima de 140**. A conduta obrigatória é a angiografia antes da alta; as 24 h são o alvo a perseguir, não o gatilho de uma conduta diferente. Por isso a árvore separa "viável em menos de 24 h" (ramo precoce, com transferência precoce a partir de centro sem ICP) de "não viável" (invasiva intra-hospitalar no menor prazo). O grupo de trabalho holandês que endossou a diretriz registra que, quando as 24 h não são possíveis por logística, angiografia em até 72 h é aceitável — posição da NVVC, não da ESC.

A diretriz explica a redução de classe: nas metanálises de ensaios que compararam angiografia precoce e tardia, nenhuma mostrou superioridade da estratégia precoce para morte ou infarto não fatal; o ganho consistente foi menos isquemia recorrente ou refratária e internação mais curta. Na metanálise de dados individuais houve benefício de sobrevida no subgrupo com **GRACE acima de 140** e no subgrupo com troponina positiva, com testes de interação inconclusivos. Jobs, Collet e Thiele, atualizando esses dados, resumem: GRACE acima de 140 continua sendo o único critério de estratégia precoce com evidência científica direta, e nenhum ensaio de timing usou o algoritmo 0h/1h para definir IAMSSST.

## Quem não é candidato à angiografia

A seção 5.2.3 admite abordagem seletiva também para paciente com IAMSSST ou angina instável que não seja bom candidato a angiografia. Esse é o ramo C3: tratamento clínico otimizado, com angiografia só se o quadro mudar. O detalhamento está no material suplementar da diretriz (seção 5.2.1), não lido nesta sessão.

## Ramo 3 — sem critério de risco: a suspeita clínica decide

Sem critério de risco muito alto nem de alto risco, o paciente é, em geral, alguém com troponina não elevada, ou elevada sem preencher critério de infarto. A diretriz divide esse grupo pelo **índice de suspeita**: alta suspeita de angina instável leva a estratégia invasiva durante a internação (Classe I, nível A); baixa suspeita de SCA sem supra leva a **estratégia invasiva seletiva** (Classe I, nível A), com angiografia condicionada a teste de isquemia apropriado ou à detecção de doença obstrutiva na angiotomografia.

Base dos ensaios de rotina versus seletiva, segundo a diretriz: a estratégia invasiva de rotina não reduziu mortalidade total no conjunto dos pacientes com NSTE-ACS, mas reduziu desfechos isquêmicos compostos, sobretudo nos de alto risco, ao custo de mais complicação periprocedimento e sangramento — e a maior parte desses ensaios é anterior ao acesso radial, aos stents farmacológicos atuais e à troponina ultrassensível.

## O teste não invasivo no ramo seletivo

| Situação | Conduta ESC 2023 | Classe, nível |
|---|---|---|
| Suspeita de SCA, troponina ultrassensível não elevada ou incerta, ECG sem alteração, sem recorrência de dor | Incorporar angio-TC de coronárias ou imagem de estresse não invasiva ao workup inicial | IIa, A |
| Angio-TC precoce de rotina em toda suspeita de SCA | Não recomendada | III, B |
| Escores de risco estabelecidos, como o GRACE, para estimativa de prognóstico | Devem ser considerados | IIa, B |

A angio-TC como primeira linha para todos não melhorou desfecho em 1 ano no RAPID-CTCA e prolongou a internação — daí a Classe III para o uso rotineiro. Quem sai do ramo seletivo sem isquemia e sem doença obstrutiva passa a ser manejado como síndrome coronariana crônica (ver fluxograma-sindrome-coronariana-cronica-esc-2024) ou recebe investigação de diagnóstico alternativo.

## Entradas do GRACE

GRACE acima de 140 é um dos quatro critérios de alto risco, mas as variáveis do escore não são ramos da árvore. As oito entradas — idade, frequência cardíaca, pressão sistólica, creatinina, classe Killip, parada cardíaca na admissão, desvio de ST e elevação de marcador de necrose —, seus pesos e as faixas de mortalidade intra-hospitalar estão em sindrome-coronariana-aguda-estratificacao-de-risco-grace-complemento-numerico. A própria diretriz observa que faltam estudos do valor do corte de 140 na era da troponina ultrassensível.

## Limitações e o que confirmar

- O prazo de "menos de 2 horas" para a estratégia imediata não está na tabela de recomendação de 2023, que diz apenas "de emergência, o mais rápido possível"; ele vem da diretriz ESC 2020 de SCA sem supra (seção 6.1.2.1) e o documento derivado deste acervo (sindrome-coronariana-aguda-timing-invasivo-e-dapt-esc-2023) mantém o número sem indicar essa origem — VERIFICAÇÃO HUMANA NECESSÁRIA para harmonizar os dois textos.
- A diretriz não define operacionalmente "alto" e "baixo índice de suspeita" de angina instável; o ramo D6 é julgamento clínico, sem escore.
- O ramo "não candidato à angiografia" segue o texto principal; o detalhe está no material suplementar, não lido nesta sessão.
- A janela de 72 h no ramo de alto risco sem viabilidade de 24 h é posição do endosso holandês (NVVC), não recomendação da ESC.
- Da metanálise de Jobs, Collet e Thiele foi lida apenas a síntese; nenhum hazard ratio foi reproduzido aqui por isso.

## Tudo com Tudo

- [Fluxograma: Síndrome Coronariana Aguda — do primeiro contato à reperfusão (ESC 2023)](/biblioteca/fluxograma-sindrome-coronariana-aguda-esc-2023)
- [Síndrome Coronariana Aguda — Timing da Estratégia Invasiva e Duração de DAPT (ESC 2023)](/biblioteca/sindrome-coronariana-aguda-timing-invasivo-e-dapt-esc-2023)
- [Síndrome Coronariana Aguda: Estratificação de Risco GRACE (Complemento Numérico)](/biblioteca/sindrome-coronariana-aguda-estratificacao-de-risco-grace-complemento-numerico)
- [Síndrome Coronariana Aguda: Diagnóstico e Manejo (ESC 2023)](/biblioteca/sindrome-coronariana-aguda-diagnostico-e-manejo-esc-2023)
- [Choque Cardiogênico na Síndrome Coronariana Aguda: CULPRIT-SHOCK e IABP-SHOCK II](/biblioteca/choque-cardiogenico-na-sindrome-coronariana-aguda-culprit-shock-e-iabp-shock-ii)
- [Fluxograma: Síndrome coronariana crônica — investigação da dor torácica (ESC 2024)](/biblioteca/fluxograma-sindrome-coronariana-cronica-esc-2024)
