---
title: "Fluxograma ambulatorial: hipertensão no atleta — PS vs restrição vs liberar com plano"
slug: fluxograma-ambulatorial-hipertensao-atleta-destino
theme: "Cardiologia do Esporte e do Exercício"
kind: fluxograma
fonte_producao: grok
summary: "Árvore ambulatorial de destino no atleta com PA elevada: gate de emergência hipertensiva para PS, braço de restrição competitiva até controle, e braço de liberação com educação de alarmes — sem duplicar #848 nem o estudo de elegibilidade."
review_status: revisado
review_note: "Revisão científica/adversarial 08/09/2026: findings PR877 reconstruídos; urgência, bibliografia e limites revistos. Fonte grok preservada."
source_refs:
  - "Niebauer J, Börjesson M, Carré F, et al. Brief recommendations for participation in competitive sports of athletes with arterial hypertension. Eur J Prev Cardiol. 2019;26(14):1549-1555. DOI: 10.1177/2047487319852807. PMID: 31122039"
  - "Pelliccia A, Sharma S, Gati S, et al. 2020 ESC Guidelines on sports cardiology and exercise in patients with cardiovascular disease. Eur Heart J. 2021;42(1):17-96. DOI: 10.1093/eurheartj/ehaa605. PMID: 32860412"
  - "Kim JH, Baggish AL, Levine BD, et al. Clinical Considerations for Competitive Sports Participation for Athletes With Cardiovascular Abnormalities: A Scientific Statement From the American Heart Association and American College of Cardiology. Circulation. 2025. DOI: 10.1161/CIR.0000000000001297. PMID: 39973614"
---

# Fluxograma ambulatorial: hipertensão no atleta — destino

Prosa: [`sinalizadores-ambulatoriais-hipertensao-no-atleta-quando-restringir-e-escalar`](/biblioteca/sinalizadores-ambulatoriais-hipertensao-no-atleta-quando-restringir-e-escalar). Braço PA não controlada: [`pa-nao-controlada-no-atleta-ambulatorial-destino-esporte`](/biblioteca/pa-nao-controlada-no-atleta-ambulatorial-destino-esporte). Fundo: [`hipertensao-arterial-no-atleta-diagnostico-manejo-e-elegibilidade-esportiva`](/biblioteca/hipertensao-arterial-no-atleta-diagnostico-manejo-e-elegibilidade-esportiva).


## Árvore de decisão

```mermaid
flowchart TD
  R0["Adulto não gestante/não puérpera<br/>Consulta / pré-participação<br/>atleta com PA elevada ou HAS conhecida"] --> D1{"Há lesão aguda de órgão-alvo<br/>ou emergência hipertensiva?"}

  D1 -->|"Sim ou dúvida fundamentada"| C1(["Suspender exercício AGORA<br/>PS / urgência<br/>Não baixar PA agressivamente no consultório"])

  D1 -->|"Não"| D2{"PA de repouso não controlada<br/>(confirmada, técnica OK)?"}

  D2 -->|"Sim"| P1["Individualizar participação por PA confirmada,<br/>modalidade, LOA e risco<br/>Checar adesão, estimulantes, manguito"]
  P1 --> C2(["Confirmar HAS fora do consultório quando indicado<br/>Tratamento e retorno conforme risco<br/>MAPA/MRPA se decisão muda<br/>Orientação escrita de alarmes"])

  D2 -->|"Não / só pico no teste"| D3{"Jaleco branco documentado<br/>ou PA controlada sem alarme?"}

  D3 -->|"Sim"| C3(["Liberar com plano escrito<br/>Reavaliação periódica<br/>Não confundir com pico de esforço"])
  D3 -->|"Não / dúvida"| C4(["Avaliação de risco antes da decisão<br/>Reavaliação precoce<br/>ou cardiologia do esporte"])

  C2 --> D4{"Acesso a medicação e retorno OK?"}
  D4 -->|"Não / PA persiste muito elevada / fragilidade"| C5(["Via acessível de avaliação urgente/observação<br/>Não exigir retorno que não é viável"])
  D4 -->|"Sim"| C6(["Reavaliar participação por risco e resposta clínica<br/>Não liberar por calendário de prova"])

  classDef conduta fill:#eef6ef,stroke:#2f7a4f,color:#12301f;
  classDef alerta fill:#fdecea,stroke:#b3261e,color:#3b0a0a;
  class C1,C5 alerta;
  class C2,C3,C4,C6 conduta;
```

## Notas

- **D1** = gate de segurança (AHA/ACC 2025: emergência hipertensiva restringe até estabilização).
- **D2** = PA de repouso não controlada → restrição competitiva temporária (EAPC 2019 / ESC sports 2020).
- **D3** = liberação só com ausência convincente de red flags e controle/fenótipo claro.
- Pico isolado no esforço: não decidir elegibilidade só aqui — ver `resposta-pressorica-exagerada-exercicio-atleta`.
- Não decide doses, WADA, nem elegibilidade definitiva por doença estrutural.

## Escopo e participação

Aplicável a adultos não gestantes/não puérperas. Gestação/puerpério e atletas pediátricos seguem protocolos próprios. Excluir lesão aguda com história, exame e testes dirigidos, não apenas checklist negativo. Sem emergência, confirmar técnica/manguito e MAPA/MRPA antes de diagnosticar HAS por medida isolada; jaleco branco não exige medicação automaticamente. AHA/ACC 2025 permite participação individualizada em estágio 1/2 sem lesão aguda; considerar intensidade/componente estático, PA muito elevada confirmada, LOA e comorbidades. Exercício leve/moderado pode ter decisão diferente de competição intensa. Emergência exige parar e encaminhar; número isolado assintomático não é PS por definição.

Rever pré-treinos/estimulantes, AINE, descongestionantes, anabolizantes/SARMs sem atribuição causal automática. Resposta exagerada ao esforço não equivale a HAS de repouso. Conferir [lista antidoping vigente e TUE](https://www.wada-ama.org/en/prohibited-list) sem atrasar tratamento necessário.
