---
title: 'Fluxograma: Profilaxia secundária da febre reumática — escolha do antibiótico e duração por gravidade'
slug: fluxograma-profilaxia-secundaria-febre-reumatica-duracao-e-esquema
theme: Febre reumática
kind: fluxograma
fonte_producao: chatgpt
review_status: revisado
review_note: Fluxos clínicos revistos integralmente. Separada escolha da via de duração, eliminando indicação automática
  de injeção em cardiopatia grave. Durações atualizadas pela tabela 10.3 australiana de agosto de 2025 e distinção
  entre ausência de envolvimento cardíaco e cardite prévia; dose/intervalo pela tabela 10.2, com protocolo brasileiro
  identificado. Retirada atribuição não sustentada à AHA de 21 dias para toda população de alta incidência, equivalência
  com dose de erradicação e minimização do episódio inicial. Incluída adrenalina intramuscular imediata na suspeita
  de anafilaxia. Vínculos clínicos conferidos dentro do suplemento.
source_refs:
- Menzies School of Health Research (ARF/RHD Writing Group). Australian guideline for the prevention, diagnosis
  and management of acute rheumatic fever and rheumatic heart disease. Edition 3.3, August 2025. Chapter 10, Tables
  10.2–10.3, pages 155–157 and 160. https://www.rhdaustralia.org.au/wp-content/uploads/2025/09/Australian-ARF-RHD-Guideline-2025_August_1.pdf
- World Health Organization. WHO guideline on the prevention and diagnosis of rheumatic fever and rheumatic heart
  disease. 2024. Section 4.7. https://www.ncbi.nlm.nih.gov/books/NBK609686/
- Sanyahumbi A et al. J Am Heart Assoc. 2022;11:e024517. DOI 10.1161/JAHA.121.024517. PMID 35049336. https://pmc.ncbi.nlm.nih.gov/articles/PMC9075066/
- Cardona V et al. World Allergy Organization anaphylaxis guidance 2020. World Allergy Organ J. 2020;13:100472.
  DOI 10.1016/j.waojou.2020.100472. https://pmc.ncbi.nlm.nih.gov/articles/PMC7607509/
- Sociedade Brasileira de Cardiologia et al. Diretrizes brasileiras para o diagnóstico, tratamento e prevenção da
  febre reumática. Arq Bras Cardiol. 2009;93(3 supl.4):1–18. Seção de profilaxia secundária. https://www.scielo.br/j/abc/a/BgMJ45rh8cKSsHpK7bTbjwM/?format=html
summary: Fluxo para escolher uma via segura e definir o marco de reavaliação da profilaxia secundária após febre
  reumática documentada, conforme referência australiana de 2025.
published: false
gaps: []
---

# Fluxograma: profilaxia secundária da febre reumática — esquema e duração

Organizar a profilaxia exige duas decisões: **qual esquema o paciente pode manter com segurança** e **por quanto tempo**. O fluxo utiliza a diretriz australiana de agosto de 2025, com a recomendação da OMS de 2024 sobre a alternativa oral. Conciliar a aplicação no Brasil com o protocolo assistencial local.

## 1. Escolher fármaco e via

```mermaid
flowchart TD
  R0["Confirmar indicação de profilaxia secundária"] --> D1{"Há alergia verdadeira à penicilina?"}
  D1 -->|"Sim ou história de reação grave a esclarecer"| A1["Avaliação especializada e alternativa não penicilínica apropriada; não fazer teste ou reexposição improvisados"]
  D1 -->|"Não"| D2{"A via intramuscular é adequada considerando risco cardiovascular, acesso, dor, adesão e preferência?"}
  D2 -->|"Sim"| A2["Penicilina G benzatina intramuscular em local preparado para reconhecer e tratar reações"]
  D2 -->|"Não ou risco elevado"| A3["Discutir penicilina V oral e planejar adesão diária; individualizar com o especialista"]
  A1 --> R1["Definir duração separadamente, conforme história e doença atual"]
  A2 --> R1
  A3 --> R1
```

Na referência australiana, a benzatina é aplicada em **1.200.000 UI para peso ≥20 kg** ou **600.000 UI para <20 kg**, por via intramuscular profunda, habitualmente a cada **28 dias**. A dose e a técnica em crianças muito pequenas precisam de planejamento pediátrico. O esquema pode ser de **21 dias** em recorrência apesar de adesão completa ao de 28 dias ou quando o impacto de uma recorrência seria especialmente grave. A diretriz brasileira de 2009 utiliza **21 dias**; documentar o protocolo adotado.

Quando escolhida a alternativa oral, a tabela australiana apresenta penicilina V **250 mg a cada 12 horas**; em alergia grave confirmada, apresenta eritromicina **250 mg a cada 12 horas**. Não misturar automaticamente alternativas de diferentes diretrizes: confirmar faixa etária, alergia, interações e protocolo local. A via oral não elimina a necessidade de adesão nem muda sozinha a duração.

## 2. Definir o marco de reavaliação

Este segundo fluxo se aplica a **episódio documentado de febre reumática**. A classificação considera ECG, ecocardiograma e evolução clínica, não apenas a descrição antiga da intensidade da cardite.

```mermaid
flowchart TD
  R0["Há episódio documentado de febre reumática?"] -->|"Não"| A0["Usar critérios específicos para cardiopatia diagnosticada sem episódio reconhecido ou para rastreamento; avaliação especializada"]
  R0 -->|"Sim"| D1{"Houve envolvimento cardíaco no episódio ou há cardiopatia reumática estabelecida?"}
  D1 -->|"Não; ECG e eco normais e seguimento apropriado"| A1["Pelo menos 5 anos após o último episódio ou até 21 anos, o que terminar mais tarde"]
  D1 -->|"Sim"| D2{"Qual é a doença atual?"}
  D2 -->|"Cardite prévia sem lesão persistente ou doença leve"| A2["Pelo menos 10 anos após o último episódio ou até 21 anos, o que terminar mais tarde"]
  D2 -->|"Doença moderada, sem complicações de estágio D"| A3["Pelo menos 10 anos após o último episódio ou até 35 anos, o que terminar mais tarde"]
  D2 -->|"Doença grave ou estágio D, incluindo complicações ou cirurgia valvar"| A4["Pelo menos 10 anos após o último episódio ou até 40 anos, o que terminar mais tarde; considerar prolongamento"]
  A1 --> R1["Antes de suspender: reavaliar clínica, ecocardiograma, recorrências, estabilidade valvar e exposição ao estreptococo"]
  A2 --> R1
  A3 --> R1
  A4 --> R1
```

Um episódio aos 25 anos, com ECG e ecocardiograma normais durante a doença e seguimento apropriado, não permite suspender imediatamente por já ter ultrapassado 21 anos: na referência utilizada, ainda é necessário cumprir o prazo mínimo de cinco anos. Havendo envolvimento cardíaco, essa regra muda. A data calculada nunca dispensa a reavaliação antes da suspensão.

## Pontos que mudam a decisão

**Doença grave não impõe a via intramuscular.** A AHA de 2022 e a OMS de 2024 orientam considerar a alternativa oral em pacientes selecionados com risco cardiovascular elevado. Essa escolha ocorre antes do ramo de duração; não é uma exceção escondida após a prescrição.

**Ausência de rash não exclui anafilaxia.** Se ocorrer reação com suspeita de anafilaxia, adrenalina intramuscular deve ser administrada prontamente, inclusive em valvopatia grave. A possibilidade de colapso vasovagal ou cardiovascular não justifica esperar por manifestações cutâneas.

**Erradicação aguda e profilaxia são indicações diferentes.** Não transportar automaticamente dose, faixa de peso ou duração de uma para a outra. O esquema preventivo é repetido pelo prazo definido; não se resume à dose usada durante o episódio agudo.

**Há situações fora desta árvore.** Diagnóstico possível/provável, alterações de rastreamento e cardiopatia sem história reconhecida de febre reumática têm critérios próprios. Cirurgia não elimina automaticamente a profilaxia; em doença avançada, a duração pode ser prolongada conforme risco e estabilidade.

## Tudo com Tudo

- [Profilaxia secundária: duração por categoria de risco](/biblioteca/profilaxia-secundaria-antibiotica-na-febre-reumatica-duracao-por-categoria-de-risco) — fundamentos e limites dos prazos.
- [Segurança da penicilina benzatina](/biblioteca/seguranca-da-penicilina-benzatina-na-cardiopatia-reumatica-grave-alergia-vasovagal-ou-comprometimento-cardiovascular) — seleção da via e avaliação do risco.
- [Reação aguda: diferenciação e conduta](/biblioteca/fluxograma-reacao-aguda-a-penicilina-benzatina-na-cardiopatia-reumatica-diferenciacao-e-conduta) — conduta diante de instabilidade após a aplicação.
