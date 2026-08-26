---
title: "Fluxograma: Qual Escore de Sangramento Usar na Fibrilação Atrial Anticoagulada — HAS-BLED, ORBIT ou ABC"
slug: fluxograma-escolha-escore-sangramento-fibrilacao-atrial
theme: "Calculadoras"
kind: fluxograma
fonte_producao: chatgpt
review_status: revisado
review_note: "Verificado por Claude Sonnet 5 em 26/08/2026: os 3 PMIDs conferidos via PubMed E-utilities (esearch por título exato + esummary + efetch de abstract, e texto completo aberto no PMC para o ORBIT, PMC4670965). Os c-índices de comparação direta entre os três escores (ABC vs. ORBIT vs. HAS-BLED na coorte RE-LY; ORBIT vs. HAS-BLED vs. ATRIA na coorte ORBIT-AF) foram extraídos das Tabelas dos próprios artigos originais, não de fonte secundária. Corpus (content/Calculadoras/) conferido antes de escrever: já existem os documentos individuais de cada escore (has-bled.md, escore-orbit-risco-de-sangramento-em-fibrilacao-atrial-anticoagulada.md, escores-abc-na-fibrilacao-atrial-risco-de-avc-e-de-sangramento-por-biomarcadores.md) e um fluxograma de decisão de anticoagulação por CHA2DS2-VA, mas nenhum fluxograma de escolha ENTRE os três escores de sangramento — confirmado por listagem de content/Calculadoras/fluxograma-*.md antes de iniciar. Nenhum corte numérico foi inventado; a diretriz ESC 2024 de FA (PMID 39210723) é citada apenas como referência de contexto de prática clínica, sem atribuição de Classe/Nível específico não verificado nesta sessão (texto completo da diretriz não está em acesso aberto no PMC — confirmado por elink)."
source_refs:
  - "Pisters R, Lane DA, Nieuwlaat R, de Vos CB, Crijns HJ, Lip GY. A novel user-friendly score (HAS-BLED) to assess 1-year risk of major bleeding in patients with atrial fibrillation: the Euro Heart Survey. Chest. 2010;138(5):1093-1100. PMID: 20299623 — derivação e validação em 3.978 pacientes do Euro Heart Survey on Atrial Fibrillation (coorte mista, incluindo pacientes sem anticoagulação); c-estatística 0,72 na população geral"
  - "O'Brien EC, Simon DN, Thomas LE, et al. The ORBIT bleeding score: a simple bedside score to assess bleeding risk in atrial fibrillation. Eur Heart J. 2015;36(46):3258-3264. PMID: 26424865, PMCID: PMC4670965 (texto completo em acesso aberto) — derivado e validado no registro ORBIT-AF, 7.411 pacientes já em anticoagulação oral; escore de 5 variáveis com c-índice 0,67 (IC95% 0,64-0,69), superior ao HAS-BLED 0,64 (IC95% 0,62-0,67) e comparável ao ATRIA 0,66 (IC95% 0,63-0,68) na mesma coorte (Tabela 4 do artigo)"
  - "Hijazi Z, Oldgren J, Lindbäck J, Alexander JH, Connolly SJ, Eikelboom JW, Ezekowitz MD, Held C, Hylek EM, Lopes RD, Siegbahn A, Yusuf S, Granger CB, Wallentin L; ARISTOTLE and RE-LY Investigators. The novel biomarker-based ABC (age, biomarkers, clinical history)-bleeding risk score for patients with atrial fibrillation: a derivation and validation study. Lancet. 2016;387(10035):2302-2311. PMID: 27056738 — derivação em 14.537 pacientes do ARISTOTLE, validação externa em 8.468 pacientes do RE-LY; c-índice na validação externa: ABC 0,71 (IC95% 0,68-0,73) vs. ORBIT 0,68 (IC95% 0,65-0,70) vs. HAS-BLED 0,62 (IC95% 0,59-0,64), p<0,001 para as duas comparações"
  - "Van Gelder IC, Rienstra M, Bunting KV, et al. 2024 ESC Guidelines for the management of atrial fibrillation developed in collaboration with the European Association for Cardio-Thoracic Surgery (EACTS). Eur Heart J. 2024;45(36):3314-3414. PMID: 39210723 — citada apenas como referência de contexto de prática clínica sobre o uso do HAS-BLED para identificar fatores de risco modificáveis; texto completo não verificado nesta sessão (sem acesso aberto no PMC)"
---

# Fluxograma: Qual Escore de Sangramento Usar na Fibrilação Atrial Anticoagulada — HAS-BLED, ORBIT ou ABC

A pasta Calculadoras já tem um documento dedicado a cada um dos três escores de sangramento validados para fibrilação atrial (HAS-BLED, ORBIT e ABC de sangramento), mas nenhum fluxograma respondia à pergunta que antecede o cálculo: **diante deste paciente, qual dos três é o escore certo a aplicar?** Os três escores não competem pela mesma pergunta clínica — foram derivados em populações e com propósitos diferentes, e usar o escore fora do contexto para o qual foi validado é o erro mais comum, não a escolha entre ferramentas equivalentes.

## Árvore de decisão

```mermaid
flowchart TD
    A{"Momento da avaliação: decisão INICIAL sobre iniciar anticoagulação oral (paciente ainda sem terapia definida) ou REAVALIAÇÃO de risco em paciente JÁ em uso de anticoagulante oral?"}
    A -->|"Avaliação inicial, antes de decidir/iniciar a anticoagulação — foco em identificar fator de risco modificável"| C1(["Usar o HAS-BLED (Pisters et al., Chest 2010) — validado em coorte mista do Euro Heart Survey (n=3.978), incluindo pacientes sem anticoagulação; pontuação alta NUNCA contraindica a anticoagulação isoladamente — reavaliar e corrigir os fatores modificáveis (hipertensão não controlada, INR lábil, uso concomitante de AINE/antiplaquetário/álcool) antes de decidir"])
    A -->|"Reavaliação em paciente JÁ em anticoagulação oral"| D2{"Biomarcadores laboratoriais (GDF-15, troponina T ultrassensível, hemoglobina) estão disponíveis para o cálculo?"}
    D2 -->|"Sim, biomarcadores disponíveis"| C2(["Usar o escore ABC de sangramento (Hijazi et al., Lancet 2016) — melhor discriminação dos três nesta validação (c-índice 0,71 na coorte externa RE-LY, contra 0,68 do ORBIT e 0,62 do HAS-BLED na mesma coorte, p<0,001); exige coleta de GDF-15 e troponina T ultrassensível, não disponível na rotina da maioria dos serviços"])
    D2 -->|"Não, biomarcadores indisponíveis (cenário mais frequente)"| C3(["Usar o ORBIT (O'Brien et al., Eur Heart J 2015) — 5 variáveis simples à beira do leito, derivado e validado no registro ORBIT-AF (n=7.411) só com pacientes já em anticoagulação oral; discriminação superior ao HAS-BLED nesta mesma coorte (c-índice 0,67 vs. 0,64)"])

    classDef conduta fill:#eef6ef,stroke:#2f7a4f,color:#12301f;
    class C1,C2,C3 conduta;
```

## Variáveis de cada escore (fora da árvore, para consulta)

**HAS-BLED (0-9 pontos, 1 ponto por item, exceto onde indicado):** Hipertensão não controlada (PAS >160 mmHg), função renal e/ou hepática alterada (1 ponto cada, até 2), AVC prévio, sangramento prévio ou predisposição, INR lábil, idade >65 anos, drogas (antiplaquetário/AINE) e/ou álcool (1 ponto cada, até 2).

**ORBIT (0-7 pontos):** idade ≥75 anos (1), hemoglobina/hematócrito reduzidos ou história de anemia (2), sangramento prévio (2), função renal insuficiente/TFGe <60 (1), uso concomitante de antiplaquetário (1). Categorias: baixo risco 0-2 (2,4 sangramentos/100 pacientes-ano), médio 3 (4,7/100 pacientes-ano), alto ≥4 (8,1/100 pacientes-ano).

**ABC de sangramento:** não é soma de pontos inteiros — é um modelo de risco contínuo calculado a partir de idade, GDF-15, troponina T ultrassensível, hemoglobina e história de sangramento prévio, exigindo calculadora/software (não há tabela de pontos manual).

## Por que a bifurcação inicial é "decisão inicial vs. reavaliação em uso", e não "qual escore discrimina melhor"

Os três escores foram derivados em populações diferentes, e a diferença de desenho importa mais que o c-índice isolado:

- **HAS-BLED** (Pisters R et al., Chest 2010, PMID 20299623) foi derivado numa coorte **mista** do Euro Heart Survey — pacientes com e sem anticoagulação. É o único dos três desenhado explicitamente para apontar **fatores de risco modificáveis** (hipertensão não controlada, INR lábil, uso concomitante de AINE/antiplaquetário/álcool), o que o torna a ferramenta natural no momento de decidir se e como iniciar a anticoagulação — nunca para excluir o paciente da terapia por pontuação alta isolada.
- **ORBIT** (O'Brien EC et al., Eur Heart J 2015, PMID 26424865) foi derivado e validado **só em pacientes já em anticoagulação oral** (registro ORBIT-AF, n=7.411) — é a ferramenta mais alinhada ao cenário de reavaliação de risco durante o seguimento, com 5 variáveis simples e discriminação superior ao HAS-BLED nessa mesma coorte (c-índice 0,67 vs. 0,64 — Tabela 4 do artigo original).
- **ABC de sangramento** (Hijazi Z et al., Lancet 2016, PMID 27056738) teve a melhor discriminação das três, tanto na derivação (ARISTOTLE, n=14.537) quanto na validação externa (RE-LY, n=8.468: c-índice ABC 0,71 vs. ORBIT 0,68 vs. HAS-BLED 0,62, p<0,001) — mas exige biomarcadores (GDF-15 e troponina T ultrassensível) que não fazem parte da rotina da maioria dos serviços, o que limita seu uso prático fora de centros com acesso a esses exames.

## Armadilhas clínicas

- Usar a pontuação alta de qualquer um dos três escores para **negar ou suspender a anticoagulação** — nenhum foi desenhado para essa finalidade; o risco de AVC isquêmico da FA não tratada costuma superar o risco hemorrágico, e a resposta correta a um escore alto é reavaliar/corrigir fatores modificáveis, não negar terapia.
- Comparar diretamente a pontuação do HAS-BLED (0-9) com a do ORBIT (0-7) como se fossem a mesma escala — são sistemas de pontos com variáveis e pesos diferentes, sem equivalência numérica direta.
- Calcular o ABC de sangramento sem os biomarcadores reais (GDF-15 e troponina T-hs) — ao contrário do HAS-BLED e do ORBIT, ele não tem versão simplificada por soma manual de pontos; sem os exames laboratoriais, não há como estimá-lo.
- Aplicar o ORBIT num paciente que ainda não iniciou anticoagulação — foi derivado e validado exclusivamente em pacientes já em terapia (ORBIT-AF), diferente do HAS-BLED, que também cobre a decisão inicial.
- Presumir que o escore mais recente ou de melhor c-índice (ABC) é sempre a melhor escolha — na ausência dos biomarcadores, uma estimativa validada e simples (ORBIT ou HAS-BLED, conforme o momento da avaliação) vale mais do que tentar calcular o ABC com dados incompletos ou estimados.
