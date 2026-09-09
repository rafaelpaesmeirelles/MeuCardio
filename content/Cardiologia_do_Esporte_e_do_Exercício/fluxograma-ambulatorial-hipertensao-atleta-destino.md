---
title: "Fluxograma ambulatorial: hipertensão no atleta — PS vs restrição vs liberar com plano"
slug: fluxograma-ambulatorial-hipertensao-atleta-destino
theme: "Cardiologia do Esporte e do Exercício"
kind: fluxograma
fonte_producao: grok
summary: "Árvore ambulatorial de destino no atleta com PA elevada: gate de emergência hipertensiva para PS, braço de restrição competitiva até controle, e braço de liberação com educação de alarmes — sem duplicar #848 nem o estudo de elegibilidade."
review_status: pendente_revisao
review_note: "Irmão do protocolo sinalizadores-ambulatoriais-hipertensao-no-atleta-quando-restringir-e-escalar (07/09/2026). Além #848. Fontes: EAPC 2019 PMID 31122039; ESC sports 2020 PMID 32860412; AHA/ACC 2025 PMID 39973614. Sem doses."
source_refs:
  - "Niebauer J, Börjesson M, Carré F, et al. Brief recommendations for participation in competitive sports of athletes with arterial hypertension. Eur J Prev Cardiol. 2019;26(14):1549-1555. DOI: 10.1177/2047487319852807. PMID: 31122039"
  - "Pelliccia A, Sharma S, Gati S, et al. 2020 ESC Guidelines on sports cardiology and exercise in patients with cardiovascular disease. Eur Heart J. 2021;42(1):17-96. DOI: 10.1093/eurheartj/ehaa605. PMID: 32860412"
  - "Kim JH, Baggish AL, Levine BD, et al. Clinical Considerations for Competitive Sports Participation for Athletes With Cardiovascular Abnormalities: A Scientific Statement From the American Heart Association and American College of Cardiology. Circulation. 2025. DOI: 10.1161/CIR.0000000000001297. PMID: 39973614"
---

# Fluxograma ambulatorial: hipertensão no atleta — destino

Prosa: [`sinalizadores-ambulatoriais-hipertensao-no-atleta-quando-restringir-e-escalar`](sinalizadores-ambulatoriais-hipertensao-no-atleta-quando-restringir-e-escalar.md). Braço PA não controlada: [`pa-nao-controlada-no-atleta-ambulatorial-destino-esporte`](pa-nao-controlada-no-atleta-ambulatorial-destino-esporte.md). Fundo: [`hipertensao-arterial-no-atleta-diagnostico-manejo-e-elegibilidade-esportiva`](hipertensao-arterial-no-atleta-diagnostico-manejo-e-elegibilidade-esportiva.md).

Não duplica: [`fluxograma-ambulatorial-sinalizadores-atleta-destino`](fluxograma-ambulatorial-sinalizadores-atleta-destino.md) (#848).

## Árvore de decisão

```mermaid
flowchart TD
  R0["Consulta / pré-participação\natleta com PA elevada ou HAS conhecida"] --> D1{"Há lesão aguda de órgão-alvo\nou emergência hipertensiva?"}

  D1 -->|"Sim ou dúvida fundamentada"| C1(["Suspender exercício AGORA\nPS / urgência\nNão baixar PA agressivamente no consultório"])

  D1 -->|"Não"| D2{"PA de repouso não controlada\n(confirmada, técnica OK)?"}

  D2 -->|"Sim"| P1["Restringir competição / HIIT\nChecar adesão, estimulantes, manguito"]
  P1 --> C2(["Plano oral + retorno precoce\nMAPA/MRPA se decisão muda\nOrientação escrita de alarmes"])

  D2 -->|"Não / só pico no teste"| D3{"Jaleco branco documentado\nou PA controlada sem alarme?"}

  D3 -->|"Sim"| C3(["Liberar com plano escrito\nReavaliação periódica\nNão confundir com pico de esforço"])
  D3 -->|"Não / dúvida"| C4(["Restrição temporária prudente\nReavaliação precoce\nou cardiologia do esporte"])

  C2 --> D4{"Acesso a medicação e retorno OK?"}
  D4 -->|"Não / PA persiste muito elevada / fragilidade"| C5(["Antecipar retorno 24–72 h\nou PS se surgirem alarmes"])
  D4 -->|"Sim"| C6(["Manter restrição até controle documentado\nNão liberar por calendário de prova"])

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
