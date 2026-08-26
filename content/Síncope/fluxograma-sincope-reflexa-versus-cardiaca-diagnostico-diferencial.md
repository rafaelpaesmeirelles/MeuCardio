---
title: "Fluxograma: Síncope reflexa versus cardíaca versus hipotensão ortostática — diagnóstico diferencial (ESC 2018)"
slug: fluxograma-sincope-reflexa-versus-cardiaca-diagnostico-diferencial
theme: "Síncope"
kind: fluxograma
fonte_producao: chatgpt
review_status: revisado
review_note: "Árvore construída a partir de três documentos já publicados e revisados nesta pasta, sem consulta a fonte nova: 'hipotensao-ortostatica-e-sindrome-de-taquicardia-postural-pots-diagnostico-diferencial.md' (critérios diagnósticos de OH da ESC 2018, PMID 29562304, e do consenso Freeman et al. 2011, PMID 21431947), 'sincope-classificacao-etiologica-em-tres-grandes-grupos.md' (definição dos três grandes grupos e os preditores do escore EGSYS, derivado por Del Rosso et al., Heart 2008, PMID 18519550) e 'sincope-situacional-miccional-defecatoria-tussigena-e-de-degluticao.md' (gatilhos reflexos). Os cortes pressóricos, os preditores do EGSYS e as definições de cada grupo foram conferidos contra o texto desses três documentos antes de montar a árvore."
source_refs: ["Brignole M, Moya A, de Lange FJ, et al.; ESC Scientific Document Group. 2018 ESC Guidelines for the diagnosis and management of syncope. Eur Heart J. 2018;39(21):1883-1948. DOI: 10.1093/eurheartj/ehy037. PMID: 29562304 — seção 4.2.2 (Orthostatic challenge) e critérios diagnósticos de hipotensão ortostática, já citados no documento 'hipotensao-ortostatica-e-sindrome-de-taquicardia-postural-pots-diagnostico-diferencial.md' desta pasta.", "Del Rosso A, Ungar A, Maggi R, et al. Clinical predictors of cardiac syncope at initial evaluation in patients referred urgently to a general hospital: the EGSYS score. Heart. 2008;94(12):1620-1626. DOI: 10.1136/hrt.2008.143123. PMID: 18519550 — preditores e desempenho do escore EGSYS, já citados no documento 'sincope-classificacao-etiologica-em-tres-grandes-grupos.md' desta pasta.", "Freeman R, Wieling W, Axelrod FB, et al. Consensus statement on the definition of orthostatic hypotension, neurally mediated syncope and the postural tachycardia syndrome. Clin Auton Res. 2011;21(2):69-72. DOI: 10.1007/s10286-011-0119-5. PMID: 21431947."]
---

# Fluxograma: Síncope reflexa versus cardíaca versus hipotensão ortostática — diagnóstico diferencial (ESC 2018)

Depois de confirmado que o episódio é síncope (e não crise epiléptica ou pseudossíncope
psicogênica — diferenciais já cobertos em documentos próprios desta pasta), a pergunta
seguinte é a que mais muda a conduta: qual dos três grandes grupos etiológicos está em
jogo. Este fluxograma organiza essa diferenciação a partir da história, do exame físico
com teste postural e dos preditores clínicos de causa cardíaca.

## Árvore de decisão

```mermaid
flowchart TD
  R0["Síncope confirmada, diferencial de crise<br/>epiléptica e pseudossíncope já afastado —<br/>diferenciar entre os três grandes grupos etiológicos"] --> D1{"Queda documentada ao teste em pé ativo<br/>ou tilt test: PA sistólica caindo 20mmHg<br/>ou mais, ou diastólica 10mmHg ou mais,<br/>ou sistólica abaixo de 90mmHg,<br/>reproduzindo os sintomas espontâneos?"}

  D1 -->|"Sim"| C1(["Síncope por hipotensão ortostática —<br/>investigar causa (fármaco vasoativo,<br/>depleção de volume, disautonomia primária<br/>ou secundária) e orientar medidas<br/>posturais e de volume"])

  D1 -->|"Não, sem queda<br/>pressórica ortostática"| D2{"Há ECG anormal e/ou cardiopatia estrutural<br/>conhecida, OU palpitação súbita precedendo<br/>a síncope, OU síncope durante esforço físico<br/>ou em decúbito? perfil de síncope cardíaca<br/>do escore EGSYS"}

  D2 -->|"Sim"| D3{"Há também pródromo neurovegetativo<br/>típico (náusea, sudorese, palidez) e/ou<br/>fator desencadeante reflexo claro<br/>(dor, calor, ortostatismo prolongado, emoção)?"}

  D3 -->|"Não, quadro puro<br/>de perfil cardíaco"| C2(["Síncope provavelmente cardíaca —<br/>investigação cardiológica dirigida:<br/>ecocardiograma, monitorização de ritmo<br/>e avaliação de isquemia conforme o achado"])

  D3 -->|"Sim, achados mistos"| C3(["Quadro misto, não excluir causa cardíaca<br/>apenas pelo pródromo reflexo presente —<br/>investigar cardiopatia estrutural ou<br/>arrítmica antes de assumir etiologia reflexa<br/>EGSYS tem VPN alto, mas VPP moderado"])

  D2 -->|"Não, sem nenhum<br/>achado de perfil cardíaco"| D4{"Pródromo neurovegetativo presente<br/>(náusea, sudorese, palidez, visão turva)<br/>e/ou gatilho reflexo identificável? dor, emoção,<br/>calor, ortostatismo prolongado, micção,<br/>defecação, tosse, deglutição, rotação<br/>cervical ou colar apertado"}

  D4 -->|"Sim"| C4(["Síncope reflexa — vasovagal, situacional<br/>ou síndrome do seio carotídeo conforme<br/>o gatilho identificado. Reasseguramento,<br/>orientação sobre gatilhos e manobras<br/>de contrapressão"])

  D4 -->|"Não, nenhum<br/>padrão se encaixa com clareza"| C5(["Síncope inexplicada após a avaliação<br/>inicial — prosseguir investigação<br/>ver fluxograma de síncope inexplicada<br/>recorrente e monitor de eventos implantável"])

  classDef conduta fill:#eef6ef,stroke:#2f7a4f,color:#12301f;
  class C1,C2,C3,C4,C5 conduta;
```

## O que a árvore não mostra

- **O escore EGSYS tem valor preditivo negativo alto (99%) mas valor preditivo positivo
  moderado (33%)** — um escore baixo ajuda a excluir causa cardíaca com bastante segurança;
  um escore alto levanta a suspeita, mas não fecha o diagnóstico sozinho. É por isso que a
  árvore não trata "perfil EGSYS positivo" como diagnóstico definitivo de síncope cardíaca,
  e sim como gatilho para investigação dirigida.
- **Os três subtipos de hipotensão ortostática (inicial, clássica e tardia) têm janelas de
  tempo diferentes** — a inicial dura menos de 15 segundos e exige medida contínua
  batimento a batimento; a clássica e a tardia se distinguem pelo corte de 3 minutos em pé.
  A árvore trata "queda pressórica ortostática" como um único ramo porque a conduta inicial
  de investigação é a mesma nos três; a diferenciação entre eles é etapa posterior.
- **POTS não entra como ramo autônomo.** É definida por aumento de frequência cardíaca
  ortostática maior que 30 bpm (ou acima de 120 bpm) em até 10 minutos em pé, **na ausência**
  de hipotensão ortostática — reproduzindo os sintomas do paciente. Cabe dentro do mesmo
  ramo de investigação de intolerância ortostática, mas não é hipotensão ortostática.
- **Os três grupos não são estanques.** A própria diretriz descreve hipotensão ortostática,
  POTS e síncope vasovagal como pontos de um mesmo espectro fisiopatológico contínuo, não
  como categorias sempre mutuamente exclusivas — um mesmo paciente pode ter mecanismos
  sobrepostos ao longo do tempo.
- **A árvore não substitui a avaliação de risco da emergência.** Mesmo com perfil reflexo
  claro, características de alto risco (documentadas em fluxograma próprio desta pasta)
  continuam exigindo avaliação intensiva, independentemente da etiologia provável.
