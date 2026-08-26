---
title: "Fluxograma: Investigação da síncope inexplicada recorrente — do tilt test ao monitor de eventos implantável (ESC 2018)"
slug: fluxograma-sincope-inexplicada-recorrente-monitor-de-eventos-implantavel
theme: "Síncope"
kind: fluxograma
fonte_producao: chatgpt
review_status: revisado
review_note: "Árvore construída a partir do documento já publicado e revisado 'estratificacao-de-risco-tilt-test-e-monitor-de-eventos-implantavel-na-sincope.md' desta pasta (protocolo do tilt test, rendimento diagnóstico do monitor de eventos implantável e indicação de marca-passo pós-tilt-test positivo, todos com classe/nível ou número já conferidos contra a ESC 2018 e a American College of Cardiology em sessão anterior) e do documento 'sincope-diagnostico-e-manejo-esc-2018.md' (critério de investigação dedicada a assistolia em maiores de 40 anos com síncope grave, recorrente e sem pródromo). Nenhuma fonte nova foi consultada nesta sessão; os números e classes de recomendação foram conferidos contra o corpo desses dois documentos antes de montar a árvore."
source_refs: ["Brignole M, Moya A, de Lange FJ, et al.; ESC Scientific Document Group. 2018 ESC Guidelines for the diagnosis and management of syncope. Eur Heart J. 2018;39(21):1883-1948. DOI: 10.1093/eurheartj/ehy037. PMID: 29562304 — indicação de marca-passo pós-tilt-test positivo (Classe IIb, Nível B) e critério de investigação dedicada a assistolia em maiores de 40 anos, já citados nos documentos 'estratificacao-de-risco-tilt-test-e-monitor-de-eventos-implantavel-na-sincope.md' e 'sincope-diagnostico-e-manejo-esc-2018.md' desta pasta.", "Practical Instructions for the 2018 ESC Guidelines for the diagnosis and management of syncope. American College of Cardiology, 2018 — rendimento diagnóstico do monitor de eventos implantável (55%) contra testes convencionais (19%), já citado no documento 'estratificacao-de-risco-tilt-test-e-monitor-de-eventos-implantavel-na-sincope.md' desta pasta.", "Tilt testing evolves: faster and still accurate. European Heart Journal. 2023;44(27):2480. https://academic.oup.com/eurheartj/article/44/27/2480/7198277 — protocolo do tilt test, já citado no mesmo documento."]
---

# Fluxograma: Investigação da síncope inexplicada recorrente — do tilt test ao monitor de eventos implantável (ESC 2018)

Quando a avaliação inicial e a estratificação de risco não fecham o diagnóstico e a
síncope se repete, a diretriz ESC 2018 organiza um caminho específico: descartar primeiro
causa estrutural relevante, confirmar ou afastar síncope reflexa pelo tilt test quando
houver suspeita clínica, e reservar o monitor de eventos implantável para quem permanece
sem diagnóstico — inclusive como primeira linha em um subgrupo definido pela idade e pela
ausência de pródromo.

## Árvore de decisão

```mermaid
flowchart TD
  R0["Síncope recorrente sem diagnóstico definido<br/>após avaliação inicial completa e<br/>avaliação cardiológica básica"] --> D1{"Há suspeita de cardiopatia estrutural<br/>ou isquêmica significativa, ou o ECG mostra<br/>característica de alto risco?"}

  D1 -->|"Sim"| C1(["Investigação cardíaca dirigida primeiro:<br/>ecocardiograma, teste de esforço ou<br/>estudo eletrofisiológico conforme o achado,<br/>antes de considerar o monitor de<br/>eventos implantável"])

  D1 -->|"Não, sem suspeita<br/>estrutural relevante"| D2{"O quadro clínico sugere fortemente<br/>síncope reflexa (pródromo típico, gatilho claro)<br/>e a suspeita justifica confirmação por tilt test?"}

  D2 -->|"Sim"| D3{"O tilt test reproduz os sintomas<br/>com o padrão hemodinâmico esperado?"}

  D3 -->|"Sim"| D4{"A resposta é predominantemente<br/>cardioinibitória, em paciente com 40 anos ou mais,<br/>com síncope recorrente, frequente e imprevisível,<br/>após falha de terapias alternativas?"}

  D4 -->|"Sim"| C2(["Considerar marca-passo definitivo<br/>Classe IIb, Nível B, ESC 2018 —<br/>mesma indicação tratada em detalhe no<br/>documento de marca-passo versus<br/>cardioneuroablação desta pasta"])

  D4 -->|"Não, resposta<br/>vasodepressora predominante<br/>ou critérios acima não preenchidos"| C3(["Síncope reflexa confirmada —<br/>reasseguramento, orientação sobre gatilhos<br/>e medidas não farmacológicas<br/>ver documento de tratamento da<br/>síncope vasovagal recorrente"])

  D3 -->|"Não, tilt test<br/>negativo ou inconclusivo"| C4(["Síncope permanece inexplicada apesar<br/>do tilt test — monitor de eventos implantável<br/>indicado na sequência"])

  D2 -->|"Não, perfil não sugere<br/>reflexa com clareza"| D5{"Paciente com 40 anos ou mais, síncope grave,<br/>recorrente e imprevisível, sem pródromo<br/>reconhecível? perfil de investigação<br/>dedicada a assistolia, ESC 2018"}

  D5 -->|"Sim"| C5(["Monitor de eventos implantável como<br/>primeira linha de investigação prolongada,<br/>priorizando detecção de assistolia<br/>ou bradiarritmia"])

  D5 -->|"Não, mas síncope<br/>permanece inexplicada e recorrente"| C6(["Monitor de eventos implantável indicado —<br/>rendimento diagnóstico de 55%,<br/>predominantemente bradiarritmia,<br/>contra 19% dos testes convencionais<br/>tilt test e estudo eletrofisiológico"])

  classDef conduta fill:#eef6ef,stroke:#2f7a4f,color:#12301f;
  class C1,C2,C3,C4,C5,C6 conduta;
```

## O que a árvore não mostra

- **O protocolo do tilt test em si não está detalhado aqui.** Jejum de 2 a 4 horas, fase
  supina de pelo menos 5 minutos (ou 20 minutos com canulação venosa), fase de inclinação
  passiva de 20 a 45 minutos e, se negativa, provocação farmacológica com nitroglicerina
  sublingual ou isoproterenol intravenoso — está descrito no documento próprio desta pasta.
- **O tilt test é teste confirmatório, não teste de rastreio geral.** A diretriz ESC 2018
  reposicionou seu uso: só deve ser solicitado quando a suspeita clínica já aponta para
  síncope reflexa ou tendência a hipotensão — não para investigar qualquer síncope
  inexplicada indiscriminadamente, o que a árvore reflete ao condicionar esse ramo à
  suspeita clínica prévia.
- **Vídeo gravado por smartphone durante um episódio espontâneo** passa a ser aceito pela
  diretriz como ferramenta diagnóstica auxiliar, e pode encurtar a investigação quando
  disponível — não é um ramo separado porque depende de oportunidade, não de indicação
  programável.
- **A escolha entre marca-passo e cardioneuroablação, no cenário de resposta
  cardioinibitória confirmada, tem algoritmo próprio** (posição conjunta EHRA/HRS/APHRS/LAHRS
  2024), tratado em documento dedicado desta pasta — a árvore acima limita-se à indicação
  Classe IIb de marca-passo já estabelecida pela ESC 2018.
- **Estudo eletrofisiológico não é indicado de rotina** quando o paciente tem ECG normal,
  ausência de cardiopatia estrutural e ausência de palpitação — geralmente não acrescenta
  informação nesse perfil, mesmo dentro do ramo de "suspeita estrutural" da árvore.
