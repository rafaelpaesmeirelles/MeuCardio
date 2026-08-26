---
title: "Fluxograma: Síncope e queda no idoso — investigação diferenciada de causas ortostáticas, reflexas e cardíacas"
slug: fluxograma-sincope-idoso-investigacao-diferenciada
theme: "Síncope"
kind: fluxograma
fonte_producao: chatgpt
review_status: revisado
review_note: "Árvore construída a partir de três documentos já publicados e revisados nesta mesma pasta — 'sincope-no-idoso-armadilhas-diagnosticas-e-diferencial-com-queda-inexplicada.md' (obstáculos de amnésia retrógrada e ausência de testemunha no idoso, a recomendação da ESC 2018 de investigar queda inexplicada com o mesmo rigor de síncope inexplicada, a avaliação multifatorial de risco de queda e o papel crescente do monitor de eventos implantável nesta população), 'escore-romeo-quando-pedir-ecocardiograma-no-idoso-com-sincope-na-emergencia.md' (os 5 critérios do escore ROMEO e o desempenho da derivação de 2018 e da validação externa de 2026) e 'hipersensibilidade-do-seio-carotideo-no-idoso-e-restricoes-de-direcao-veicular.md' (técnica e subtipos de resposta da massagem do seio carotídeo, e as restrições de direção particular vs. comercial). Os cortes de hipotensão ortostática (queda ≥20 mmHg PAS ou ≥10 mmHg PAD em até 3 minutos) vêm da 2018 ESC Guidelines for the diagnosis and management of syncope (seção de teste postural), já usados com a mesma fonte no fluxograma 'fluxograma-sincope-reflexa-versus-cardiaca-diagnostico-diferencial.md' desta pasta. Nenhuma fonte nova foi consultada nesta sessão; os cortes, critérios e classes citados foram conferidos contra o corpo desses documentos antes de montar a árvore, sem acrescentar nem alterar nenhum dado clínico."
source_refs: ["Brignole M, Moya A, de Lange FJ, et al.; ESC Scientific Document Group. 2018 ESC Guidelines for the diagnosis and management of syncope. Eur Heart J. 2018;39(21):1883-1948. DOI: 10.1093/eurheartj/ehy037. PMID: 29562304 — recomendação de investigar queda inexplicada com o mesmo protocolo de síncope inexplicada e critérios diagnósticos de hipotensão ortostática (seção de teste postural), já citados e conferidos no documento 'sincope-no-idoso-armadilhas-diagnosticas-e-diferencial-com-queda-inexplicada.md' e no fluxograma 'fluxograma-sincope-reflexa-versus-cardiaca-diagnostico-diferencial.md' desta pasta.", "Rafanelli M, Mossello E, Testa GD, Ungar A. Unexplained falls in the elderly. Minerva Med. 2022;113(2):263-272. DOI: 10.23736/S0026-4806.21.07749-1. PMID: 34515457 — obstáculos da amnésia retrógrada e ausência de testemunha, avaliação multifatorial de risco de queda e papel do monitor de eventos implantável no idoso, abstract conferido via PubMed E-utilities e já citado no documento 'sincope-no-idoso-armadilhas-diagnosticas-e-diferencial-com-queda-inexplicada.md' desta pasta.", "Ungar A, Morrione A, Rafanelli M, Ruffolo E, Brunetti MA, Chisciotti VM, Masotti G, Del Rosso A, Marchionni N. The management of syncope in older adults. Minerva Med. 2009;100(4):247-258. PMID: 19749680 — causas mais prevalentes de síncope no idoso (hipotensão ortostática, hipersensibilidade do seio carotídeo, síncope neuromediada e arritmias), abstract conferido via PubMed E-utilities e já citado no mesmo documento desta pasta.", "Probst MA, Gibson TA, Weiss RE, et al. Predictors of Clinically Significant Echocardiography Findings in Older Adults with Syncope: A Secondary Analysis. J Hosp Med. 2018;13(12):823-828. DOI: 10.12788/jhm.3082. PMID: 30255862 — derivação do escore ROMEO (5 critérios, desempenho do ROMEO=0), texto integral conferido em PMC e já citado no documento 'escore-romeo-quando-pedir-ecocardiograma-no-idoso-com-sincope-na-emergencia.md' desta pasta.", "DeAngelis J, Vargas G, Weiss RE, et al. Predicting Echocardiography Findings in Adults Presenting to the Emergency Department With Syncope: An External Validation of the ROMEO Score. Acad Emerg Med. 2026;33(6):e70366. DOI: 10.1111/acem.70366. PMID: 42340085 — validação externa do escore ROMEO (sensibilidade 98,9%, VPN 98,6%, especificidade 20,2%, AUC 0,83), texto integral conferido na Wiley e já citado no mesmo documento desta pasta.", "Carotid Sinus Hypersensitivity. StatPearls (NCBI Bookshelf). https://www.ncbi.nlm.nih.gov/books/NBK559059/ — técnica e critérios da massagem do seio carotídeo, subtipos de resposta (cardioinibitório, vasodepressor, misto), já citados no documento 'hipersensibilidade-do-seio-carotideo-no-idoso-e-restricoes-de-direcao-veicular.md' desta pasta.", "Driving restrictions for patients with reflex syncope. PMC. https://pmc.ncbi.nlm.nih.gov/articles/PMC5728707/ — critério de restrição de direção particular versus comercial, já citado no mesmo documento desta pasta."]
---

# Fluxograma: Síncope e queda no idoso — investigação diferenciada de causas ortostáticas, reflexas e cardíacas

A síncope no idoso é um problema diagnóstico à parte, não apenas "a mesma
síncope, num paciente mais velho": amnésia retrógrada e ausência de
testemunha tornam a distinção entre queda mecânica e síncope verdadeira
frequentemente impossível de fazer só pela história. Este fluxograma organiza
a investigação a partir daí — quando tratar uma queda como síncope
inexplicada, como diferenciar as três causas mais prevalentes nesta faixa
etária (hipotensão ortostática, hipersensibilidade do seio carotídeo e causa
cardíaca) e quando pedir ecocardiograma pelo escore ROMEO, em vez de por
rotina.

## Árvore de decisão

```mermaid
flowchart TD

R["Idoso (≥60 anos) com episódio de perda de consciência ou queda sem explicação mecânica clara"]
D1{"Há explicação mecânica evidente e suficiente para a queda (tropeço, obstáculo, degrau)?"}
C1(["Queda mecânica explicada: não é necessário investigar como síncope inexplicada"])
X1["Investigar como síncope inexplicada, mesmo sem relato confiável de perda de consciência: anamnese completa (considerando amnésia retrógrada e ausência frequente de testemunha), exame físico, PA deitado e em pé, ECG, revisão completa de medicações"]
D2{"Queda ortostática da PA confirmada (≥20 mmHg PAS ou ≥10 mmHg PAD em até 3 min, ou PAS<90 mmHg)?"}
C2(["Hipotensão ortostática: revisar fármacos hipotensores em uso (anti-hipertensivo, diurético, tricíclico, antipsicótico), orientar medidas posturais e reavaliar a necessidade de cada medicação"])
X2["Avaliar suspeita clínica de hipersensibilidade do seio carotídeo (síncope/queda associada a giro cervical, barbear, colar apertado, idade avançada)"]
D3{"Suspeita clínica de hipersensibilidade do seio carotídeo presente?"}
X3["Massagem do seio carotídeo sob monitorização contínua batimento a batimento, em supino e ortostatismo"]
X4["Prosseguir com avaliação cardiovascular dirigida: aplicar o escore ROMEO para decidir a necessidade de ecocardiograma transtorácico"]
D4{"Resposta cardioinibitória, vasodepressora ou mista reproduzindo os sintomas (assistolia ≥3s e/ou queda de PAS ≥50 mmHg)?"}
C3(["Hipersensibilidade do seio carotídeo confirmada: considerar marca-passo se padrão cardioinibitório predominante; orientar restrição de direção conforme o perfil (particular vs. comercial) e o risco de recorrência"])
X5["Prosseguir com avaliação cardiovascular dirigida: aplicar o escore ROMEO para decidir a necessidade de ecocardiograma transtorácico"]
D5{"Algum critério ROMEO presente (IC congestiva, doença arterial coronariana, ECG anormal, troponina T de alta sensibilidade >14 pg/mL ou NT-proBNP >125 pg/mL)?"}
C4(["ROMEO=0: baixa probabilidade de achado ecocardiográfico significativo (VPN 98,6%) — não indicar ecocardiograma de rotina só pela síncope/queda, salvo outra indicação clínica independente. Se a etiologia permanecer indefinida, investigar como síncope inexplicada recorrente (tilt test e monitor de eventos implantável, com rendimento particularmente alto no idoso por amnésia retrógrada e ausência de testemunha) e complementar com avaliação multifatorial de risco de queda (marcha, força, visão, cognição, ambiente domiciliar)"])
C5(["ROMEO≥1: indicar ecocardiograma transtorácico; especificidade baixa (20%), então achado positivo exige correlação clínica antes de assumir causalidade. Se a etiologia permanecer indefinida mesmo após o ecocardiograma, investigar como síncope inexplicada recorrente (tilt test e monitor de eventos implantável) e complementar com avaliação multifatorial de risco de queda"])
D6{"Algum critério ROMEO presente (IC congestiva, doença arterial coronariana, ECG anormal, troponina T de alta sensibilidade >14 pg/mL ou NT-proBNP >125 pg/mL)?"}
C6(["ROMEO=0: baixa probabilidade de achado ecocardiográfico significativo (VPN 98,6%) — não indicar ecocardiograma de rotina só pela síncope/queda, salvo outra indicação clínica independente. Se a etiologia permanecer indefinida, investigar como síncope inexplicada recorrente (tilt test e monitor de eventos implantável, com rendimento particularmente alto no idoso por amnésia retrógrada e ausência de testemunha) e complementar com avaliação multifatorial de risco de queda (marcha, força, visão, cognição, ambiente domiciliar)"])
C7(["ROMEO≥1: indicar ecocardiograma transtorácico; especificidade baixa (20%), então achado positivo exige correlação clínica antes de assumir causalidade. Se a etiologia permanecer indefinida mesmo após o ecocardiograma, investigar como síncope inexplicada recorrente (tilt test e monitor de eventos implantável) e complementar com avaliação multifatorial de risco de queda"])

R --> D1
D1 -->|"Sim"| C1
D1 -->|"Não"| X1
X1 --> D2
D2 -->|"Sim"| C2
D2 -->|"Não"| X2
X2 --> D3
D3 -->|"Sim"| X3
D3 -->|"Não"| X4
X3 --> D4
D4 -->|"Sim"| C3
D4 -->|"Não"| X5
X4 --> D5
D5 -->|"Não"| C4
D5 -->|"Sim"| C5
X5 --> D6
D6 -->|"Não"| C6
D6 -->|"Sim"| C7

classDef conduta fill:#eef6ef,stroke:#2f7a4f,color:#12301f;
class C1,C2,C3,C4,C5,C6,C7 conduta;
```

## Armadilhas clínicas

- Descartar investigação cardiovascular porque o idoso "não perdeu a
  consciência", quando o relato vem de paciente sem testemunha do evento e
  sem confiabilidade de memória estabelecida — a amnésia retrógrada torna
  essa negativa pouco confiável nessa população, e a ESC 2018 recomenda
  investigar a queda inexplicada com o mesmo rigor da síncope inexplicada.
- Aplicar o escore ROMEO como se fosse regra de indicação de alto risco —
  ele é regra de **exclusão** de baixo risco (ROMEO=0, VPN alto); ROMEO≥1
  não significa achado positivo automático, só tira o paciente do grupo de
  exclusão segura, já que a especificidade fica em torno de 20%.
- Confundir a massagem do seio carotídeo negativa com ausência de causa
  cardiovascular — ela só investiga um mecanismo específico (hipersensibilidade
  do seio carotídeo); resultado negativo não dispensa a investigação cardíaca
  dirigida (ECG, ROMEO/ecocardiograma) nem a avaliação ortostática.
- Não revisar a lista completa de medicações em uso à procura de fármacos que
  reduzam o limiar para hipotensão ortostática ou bradicardia reflexa —
  anti-hipertensivos, diuréticos, tricíclicos e antipsicóticos são
  amplificadores comuns das duas causas mais prevalentes nessa faixa etária.
- Reservar o monitor de eventos implantável apenas para pacientes jovens com
  síncope recorrente — no idoso com queda/síncope inexplicada e sem
  diagnóstico após a avaliação inicial, é ferramenta com papel reconhecido
  justamente pela dificuldade de captar o evento por outros meios (sem
  testemunha, sem memória confiável).
- Investigar apenas a esfera cardiovascular e ignorar a avaliação
  multifatorial de risco de queda (marcha, força, visão, cognição, ambiente
  domiciliar) — as duas frentes são complementares, não substitutas uma da
  outra.
