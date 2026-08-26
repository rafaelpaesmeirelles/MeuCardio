---
title: "Fluxograma: Critérios de alto risco na síncope da emergência — alta, observação ou internação (ESC 2018 / EUSEM 2024)"
slug: fluxograma-sincope-criterios-de-alto-risco-emergencia-esc-2018-eusem-2024
theme: "Síncope"
kind: fluxograma
fonte_producao: chatgpt
review_status: revisado
review_note: "Auditoria científica independente do lote Claude em 26/08/2026: o texto integral do consenso EUSEM 2024 (PMID 38874507; PMC11198953) e a diretriz ESC 2018 (PMID 29562304) foram reconferidos. Corrigidos a atribuição de FC <40/min à fibrilação atrial lenta, a lista de achados eletrocardiográficos maiores, o prazo de interpretação do ECG e os exames laboratoriais mínimos do processo EUSEM. Mantida pendência de revisão médica antes da publicação clínica."
source_refs: ["Brignole M, Moya A, de Lange FJ, et al.; ESC Scientific Document Group. 2018 ESC Guidelines for the diagnosis and management of syncope. Eur Heart J. 2018;39(21):1883-1948. DOI: 10.1093/eurheartj/ehy037. PMID: 29562304 — Tabelas 5, 6 e 7 (manejo no departamento de emergência e critérios de internação), texto integral já lido e citado no documento 'sincope-diagnostico-e-manejo-esc-2018.md' desta pasta.", "Möckel M, Janssens KA, Pudasaini S, Garcia-Castrillo Riesgo L, et al.; EUSEM syncope group. The syncope core management process in the emergency department: a consensus statement of the EUSEM syncope group. Eur J Emerg Med. 2024;31(4):250-259. DOI: 10.1097/MEJ.0000000000001146. PMID: 38874507 — características de alto risco maiores e menores do ECG, texto integral em acesso aberto (PMC11198953), já citado no documento 'sincope-na-emergencia-criterios-de-alto-risco-do-ecg-eusem-2024.md' desta pasta."]
---

# Fluxograma: Critérios de alto risco na síncope da emergência — alta, observação ou internação (ESC 2018 / EUSEM 2024)

O fluxograma de avaliação inicial já publicado nesta pasta resume a decisão em três
caixas — alto, intermediário e baixo risco. Este documento detalha o que entra em cada
caixa: as características maiores do ECG que o consenso EUSEM 2024 classifica como alto
risco por si só, os achados clínicos de alto risco da ESC 2018 que não dependem do ECG, e
o desdobramento seguinte — já dentro do grupo de alto risco — entre internar e apenas
observar em unidade de síncope, conforme a Tabela 7 da diretriz.

## Árvore de decisão

```mermaid
flowchart TD
  R0["Síncope avaliada no departamento de emergência<br/>história, exame físico, sinais vitais, PA supina/em pé,<br/>glicemia, hemoglobina e ECG de 12 derivações"] --> D1{"ECG com característica MAIOR de alto risco<br/>do consenso EUSEM 2024?<br/>isquemia aguda; BAV Mobitz II ou 3º grau;<br/>FA lenta com FC menor que 40; bradicardia sinusal<br/>persistente menor que 40, bloqueio sinoatrial repetitivo<br/>ou pausa maior que 3 s em acordado não atleta;<br/>TV sustentada ou não sustentada; disfunção de dispositivo"}

  D1 -->|"Não neste grupo"| D1B{"Outro achado MAIOR do EUSEM?<br/>bloqueio de ramo ou distúrbio intraventricular;<br/>hipertrofia ou sinais de isquemia/cardiomiopatia;<br/>ondas T negativas direitas ou onda épsilon sugerindo<br/>cardiomiopatia arritmogênica; Brugada tipo 1;<br/>QTc maior que 460 ms repetido e sugestivo de QT longo"}

  D1 -->|"Sim"| D2{"Predominam fatores que favorecem<br/>internação hospitalar? Tabela 7 ESC 2018:<br/>lesão causada pela síncope, doença coexistente<br/>grave, necessidade de investigação ou tratamento<br/>só possível internado, mau funcionamento de dispositivo"}

  D1B -->|"Sim"| D2

  D2 -->|"Sim"| C1(["Internação hospitalar para<br/>investigação e tratamento<br/>Classe I, Nível B"])
  D2 -->|"Não, predominam fatores<br/>de observação"| C2(["Avaliação precoce e intensiva em<br/>unidade de síncope ou observação<br/>na emergência, sem internação<br/>Classe I, Nível B"])

  D1B -->|"Não, ECG sem<br/>característica maior"| D3{"Há característica clínica de alto risco<br/>independente do ECG? cardiopatia estrutural<br/>ou coronariana grave conhecida, síncope durante<br/>esforço físico ou em decúbito/sentado,<br/>palpitação súbita antes da síncope, história<br/>familiar de morte súbita em idade jovem"}

  D3 -->|"Sim"| D4{"Predominam fatores que favorecem<br/>internação hospitalar? Tabela 7 ESC 2018"}

  D4 -->|"Sim"| C3(["Internação hospitalar para<br/>investigação e tratamento<br/>Classe I, Nível B"])
  D4 -->|"Não, predominam fatores<br/>de observação"| C4(["Avaliação precoce e intensiva em<br/>unidade de síncope ou observação<br/>na emergência, sem internação<br/>Classe I, Nível B"])

  D3 -->|"Não, sem característica<br/>clínica de alto risco"| D5{"Características de baixo risco presentes?<br/>pródromo vasovagal típico, gatilho reflexo claro,<br/>síncope situacional ou ortostática documentada,<br/>ausência de doença cardíaca conhecida,<br/>exame físico e ECG normais"}

  D5 -->|"Sim"| C5(["Alta do departamento de emergência,<br/>manejo ambulatorial<br/>Classe I, Nível B"])

  D5 -->|"Não, sem perfil<br/>claro de alto nem de baixo risco"| C6(["Observação no departamento de emergência<br/>ou em unidade de síncope, sem internação<br/>Classe I, Nível B"])

  classDef conduta fill:#eef6ef,stroke:#2f7a4f,color:#12301f;
  class C1,C2,C3,C4,C5,C6 conduta;
```

## O que a árvore não mostra

- **Escore de estratificação de risco não substitui julgamento clínico.** A própria
  diretriz é explícita: escores (CSRS, EGSYS, OESIL) podem ser considerados como apoio
  (Classe IIb, Nível B), mas não têm desempenho comprovadamente melhor do que a avaliação
  clínica bem feita, e não devem decidir internação sozinhos.
- **O processo EUSEM prevê glicemia e hemoglobina como mínimo laboratorial.** Hemograma
  completo, eletrólitos, troponina seriada, D-dímero, radiografia e tomografia não formam
  um painel universal: devem ser solicitados de modo dirigido pela hipótese clínica, como
  hemorragia, síndrome coronariana, embolia pulmonar, dissecção ou causa neurológica.
- **Dispositivo cardíaco implantado exige interrogação, não espera.** Paciente com
  marca-passo ou CDI e síncope deve ter o dispositivo interrogado prontamente — é uma das
  medidas citadas pela diretriz para evitar internação desnecessária ou, ao contrário, para
  não deixar passar disfunção do dispositivo.
- **As características menores do ECG (EUSEM 2024) só contam se a história for compatível
  com síncope arritmogênica** — bloqueio Mobitz I, BAV de 1º grau com PR muito prolongado,
  bradicardia assintomática entre 40 e 50/min, taquicardia supraventricular paroxística,
  QRS pré-excitado, QTc curto, padrão atípico de Brugada e ondas T negativas/épsilon em
  precordiais direitas. Fora desse contexto clínico, esses achados isolados não classificam
  o paciente como alto risco — por isso não entraram como ramo autônomo na árvore.
- **O corte de QTc muda conforme o instrumento.** O EUSEM 2024 usa 460 ms como
  característica de alto risco do ECG; o Escore Canadense de Risco de Síncope (CSRS), citado
  em outro documento desta pasta, usa 480 ms como variável pontuada de um escore diferente.
  Não são o mesmo corte para o mesmo fim.
- **A avaliação inicial não pode ser abreviada.** O consenso EUSEM determina interpretação
  especializada e documentada do ECG em até 10 minutos **da chegada/registro na emergência**,
  não em até 10 minutos depois de o traçado ser obtido. A diretriz ESC exige história,
  exame físico, PA supina/em pé e ECG; o processo EUSEM acrescenta sinais vitais, glicemia
  e hemoglobina ao núcleo operacional mínimo.
