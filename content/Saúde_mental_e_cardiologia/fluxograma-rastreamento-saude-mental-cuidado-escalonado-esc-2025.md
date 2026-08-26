---
title: "Fluxograma: saúde mental no cuidado cardiovascular — rastreamento e cuidado escalonado (ESC 2025)"
slug: fluxograma-rastreamento-saude-mental-cuidado-escalonado-esc-2025
theme: "Saúde mental e cardiologia"
kind: fluxograma
summary: "Aplicação dos princípios ACTIVE do consenso ESC 2025: checar sistematicamente sintomas com instrumento validado, avaliar gravidade e segurança, integrar o time Psycho-Cardio e escalar ou reduzir o cuidado conforme resposta e preferência."
review_status: revisado
review_note: "Fluxograma auditado em 26/08/2026 contra a publicação primária (PMID 40878270; DOI 10.1093/eurheartj/ehaf191) e a página oficial ESC. A árvore organiza declarações de consenso produzidas por Delphi modificado; não atribui classe/nível de evidência, não impõe um instrumento único e não cria intervalo fixo de rastreamento ou ponto de corte diagnóstico. Cinco vínculos internos conferidos contra slugs existentes."
source_refs: ["Bueno H, Deaton C, Farrero M, et al. 2025 ESC Clinical Consensus Statement on mental health and cardiovascular disease: developed under the auspices of the ESC Clinical Practice Guidelines Committee. Eur Heart J. 2025;46(41):4156-4225. DOI: 10.1093/eurheartj/ehaf191. PMID: 40878270.", "European Society of Cardiology. 2025 ESC Clinical Consensus Statement on mental health and cardiovascular disease — página oficial, 29/08/2025. https://www.escardio.org/guidelines/clinical-practice-guidelines/all-esc-practice-guidelines/mental-health-and-cvd/"]
---

# Fluxograma: saúde mental no cuidado cardiovascular (ESC 2025)

O consenso ESC 2025 propõe integrar saúde mental ao cuidado cardiovascular com os princípios **ACTIVE**: reconhecer a relação bidirecional, checar sintomas, usar ferramentas validadas, implementar cuidado centrado na pessoa, criar colaboração e avaliar a evolução. A árvore abaixo organiza esse processo; ela **não é um algoritmo validado nem uma recomendação graduada**.

## Entrada pelo cuidado cardiovascular

```mermaid
flowchart TD
  A["Pessoa em risco cardiovascular<br/>ou vivendo com doença cardiovascular"] --> B["Acknowledge + Check:<br/>perguntar ativamente sobre sofrimento,<br/>humor, ansiedade, estresse e impacto funcional"]
  B --> C["Usar instrumento validado apropriado ao domínio<br/>por exemplo PHQ, HADS, IES ou CDI-SF<br/>sem tratar o escore isolado como diagnóstico"]
  C --> D{"Há sintomas, prejuízo funcional<br/>ou preocupação clínica?"}

  D -->|Não| E(["Reforçar prevenção e suporte<br/>Reavaliar em contatos regulares,<br/>após evento cardíaco ou mudança clínica"])
  D -->|Sim| F{"Há preocupação de segurança<br/>ou necessidade de avaliação urgente?"}
  F -->|Sim| G(["Acionar via local de avaliação urgente<br/>de saúde mental, preservando em paralelo<br/>a segurança e o tratamento cardiovascular"])
  F -->|Não| H["Avaliar gravidade, contexto, preferências,<br/>adesão, suporte social, comorbidades<br/>e possíveis efeitos/interações de medicamentos"]

  H --> I["Implement + Venture:<br/>definir cuidado escalonado e centrado na pessoa<br/>com atenção primária, saúde mental e cardiologia"]
  I --> J{"Resposta clínica e funcional<br/>na reavaliação?"}
  J -->|Adequada| K(["Manter a intervenção eficaz<br/>e reduzir intensidade quando apropriado,<br/>com seguimento planejado"])
  J -->|Insuficiente ou piora| L(["Escalar intensidade, revisar diagnóstico,<br/>barreiras, medicações e necessidade<br/>de time Psycho-Cardio especializado"])
  L --> J

  classDef action fill:#eef5f8,stroke:#1c7293,color:#0b2e45;
  class E,G,K,L action;
```

O instrumento é escolhido pela pergunta clínica e pelo contexto. O consenso nomeia ferramentas validadas, mas não elege uma única escala obrigatória nem autoriza diagnosticar depressão, ansiedade ou estresse pós-traumático apenas pelo resultado de rastreamento.

## Entrada pelo cuidado em saúde mental

```mermaid
flowchart TD
  A["Pessoa tratada por condição de saúde mental<br/>especialmente transtorno mental grave"] --> B["Avaliar regularmente risco cardiovascular,<br/>sintomas físicos, fatores de risco e efeitos<br/>cardiometabólicos/eletrofisiológicos do tratamento"]
  B --> C{"Há sintoma cardiovascular,<br/>risco elevado ou alteração relevante?"}
  C -->|Não| D(["Prevenção cardiovascular longitudinal<br/>e coordenação com atenção primária"])
  C -->|Sim| E["Investigar e tratar com o mesmo esforço clínico<br/>oferecido a pessoas sem transtorno mental"]
  E --> F(["Integrar saúde mental e cardiologia;<br/>evitar estigma, viés e atribuição automática<br/>do sintoma físico à condição psiquiátrica"])

  classDef action fill:#eef5f8,stroke:#1c7293,color:#0b2e45;
  class D,F action;
```

Essa segunda entrada combate o **diagnostic overshadowing**: sintomas cardiovasculares não devem ser descartados como “ansiedade” ou consequência inevitável do transtorno mental sem avaliação clínica adequada.

## Time Psycho-Cardio e cuidado escalonado

O time Psycho-Cardio não precisa ter composição idêntica em todos os serviços. O princípio é garantir comunicação entre cardiologia, atenção primária e profissionais de saúde mental, envolvendo enfermagem, assistência social, reabilitação e cuidadores conforme a necessidade e os recursos locais.

Cuidado escalonado significa começar pela intervenção menos intensiva que seja adequada à gravidade, segurança e preferência; reavaliar; e aumentar, manter ou reduzir a intensidade conforme a resposta. Não significa oferecer intervenção mínima a toda pessoa nem atrasar avaliação urgente.

## Conteúdo CorVIA conectado

- [Consenso clínico ESC 2025: saúde mental e doença cardiovascular](/biblioteca/saude-mental-e-doenca-cardiovascular-consenso-clinico-esc-2025)
- [Depressão pós-infarto e prognóstico cardiovascular](/biblioteca/depressao-pos-infarto-como-fator-de-risco-cardiovascular-van-melle-e-enrichd)
- [Segurança cardiovascular de antidepressivos](/biblioteca/seguranca-cardiovascular-de-psicofarmacos-antidepressivos-e-doenca-cardiaca)
- [Antipsicóticos, QT e morte súbita](/biblioteca/antipsicoticos-e-prolongamento-de-qt-risco-de-morte-subita-cardiaca)
- [Disparidade cardiovascular no transtorno mental grave](/biblioteca/disparidade-no-cuidado-cardiovascular-do-transtorno-mental-grave)

## Limites

- O consenso usa Delphi modificado, não classes tradicionais de recomendação e níveis de evidência.
- Rastreamento não substitui entrevista clínica nem avaliação diagnóstica.
- O documento não fixa escala, ponto de corte ou periodicidade universal.
- A base de evidência para melhorar desfechos cardiovasculares duros por meio do rastreamento e tratamento de saúde mental ainda tem lacunas.
- Situações urgentes seguem o protocolo local de segurança e emergência; este fluxo não o substitui.
