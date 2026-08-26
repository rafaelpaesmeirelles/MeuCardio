---
title: "Fluxograma: Hipercolesterolemia Familiar — Diagnóstico pelo Escore Dutch Lipid Clinic Network e Manejo (ESC/EAS 2025)"
slug: fluxograma-hipercolesterolemia-familiar-diagnostico-dlcn-e-manejo-esc-eas-2025
theme: "Prevenção e lipídios"
kind: fluxograma
fonte_producao: chatgpt
review_status: revisado
review_note: "Verificado por Claude em 26/08/2026: conteúdo derivado do protocolo já publicado no acervo (hipercolesterolemia-familiar-hf-diagnostico-e-manejo-atualizado-esceas-2025.md). As quatro citações primárias foram reconferidas nesta revisão por resolução de DOI (redirecionamento DOI→academic.oup.com com volume/fascículo/páginas conferidos) e, para a referência do DLCN, por leitura direta da página do PubMed (PMID 23956253); nenhum PMID/DOI foi criado nesta revisão, todos vêm do documento-fonte já revisado."
source_refs: ["Mach F, Koskinas KC, Roeters van Lennep JE, et al. 2025 Focused Update of the 2019 ESC/EAS Guidelines for the management of dyslipidaemias. Eur Heart J. 2025;46(42):4359-4378. DOI: 10.1093/eurheartj/ehaf190. PMID: 40878289 — metas de LDL-C por categoria de risco e recomendação de rastreamento de Lp(a) ao menos uma vez na vida, mantidas nesta árvore.", "Mach F, Baigent C, Catapano AL, et al. 2019 ESC/EAS Guidelines for the management of dyslipidaemias: lipid modification to reduce cardiovascular risk. Eur Heart J. 2020;41(1):111-188. DOI: 10.1093/eurheartj/ehz455. PMID: 31504418 — critérios de suspeita clínica de HF e recomendação de confirmação por análise de DNA, mantidos sem alteração pela atualização de 2025.", "Nordestgaard BG, Chapman MJ, Humphries SE, et al. Familial hypercholesterolaemia is underdiagnosed and undertreated in the general population: guidance for clinicians to prevent coronary heart disease: consensus statement of the European Atherosclerosis Society. Eur Heart J. 2013;34(45):3478-3490. DOI: 10.1093/eurheartj/eht273. PMID: 23956253 — origem do escore Dutch Lipid Clinic Network (DLCN) usado nesta árvore.", "Cuchel M, Raal FJ, Hegele RA, et al. 2023 Update on European Atherosclerosis Society Consensus Statement on Homozygous Familial Hypercholesterolaemia: new treatments and clinical guidance. Eur Heart J. 2023;44(25):2277-2291. DOI: 10.1093/eurheartj/ehad197. PMID: 37130090 — critérios de suspeita/confirmação de HoFH, metas de LDL-C e escalonamento terapêutico (evinacumabe, lomitapide) do ramo homozigoto desta árvore.", "Derivado de hipercolesterolemia-familiar-hf-diagnostico-e-manejo-atualizado-esceas-2025.md, já publicado no acervo (Prevenção e lipídios)."]
---

# Fluxograma: Hipercolesterolemia Familiar — Diagnóstico pelo Escore Dutch Lipid Clinic Network e Manejo (ESC/EAS 2025)

A hipercolesterolemia familiar (HF) é subdiagnosticada porque seu critério mais usado — o escore da **Dutch Lipid Clinic Network (DLCN)** — não é um corte único, e sim uma pontuação por categorias (história familiar, história clínica, exame físico, LDL-C e DNA) em que só a maior pontuação de cada grupo conta. Este fluxograma organiza duas decisões em sequência: primeiro, separar a forma **homozigota (HoFH)** — rara, com cortes e fármacos próprios — da investigação padrão por DLCN; depois, uma vez estabelecido o diagnóstico, levar à meta de LDL-C e à conduta certas conforme idade e categoria de risco.

**O que a árvore não resolve sozinha**: o diagnóstico definitivo de HF é clínico, não genético — a ausência de mutação identificada não afasta HF quando o quadro clínico é característico, e o inverso (variante encontrada sem fenótipo) também não basta isoladamente. Rastreamento em cascata dos familiares de 1º grau é parte do manejo, não um extra.

## Árvore de decisão

```mermaid
flowchart TD
  N0["Paciente com suspeita clínica de HF: LDL-C sem<br/>tratamento muito elevado (adultos com 190 mg/dL<br/>ou mais; crianças com 150 mg/dL ou mais), DAC<br/>prematura (homens abaixo de 55 anos; mulheres<br/>abaixo de 60 anos), xantoma tendíneo, ou parente<br/>de 1º grau com DCV precoce ou LDL-C muito alto"] --> D1{"Critérios sugestivos de HoFH? (LDL-C sem<br/>tratamento acima de 400 mg/dL [acima de<br/>10 mmol/L], OU xantoma cutâneo/tendíneo<br/>antes dos 10 anos, OU LDL-C compatível com<br/>HF heterozigota em ambos os pais)"}

  D1 -->|"Sim"| N1["Investigar HoFH: buscar variantes patogênicas<br/>bialélicas (em loci diferentes) em LDLR, APOB,<br/>PCSK9 ou LDLRAP1, ou duas ou mais variantes<br/>distintas nesses genes — diagnóstico fenotípico<br/>tem prioridade sobre resultado genético<br/>discordante"]
  N1 --> D2{"Idade do paciente?"}
  D2 -->|"Criança ou adolescente<br/>(abaixo de 18 anos)"| C1(["HoFH pediátrica: meta de LDL-C abaixo de<br/>115 mg/dL (abaixo de 3 mmol/L) se sem DCV<br/>estabelecida. Iniciar estatina de alta intensidade<br/>+ ezetimiba desde o diagnóstico (não estatina<br/>isolada). Considerar evinacumabe 15 mg/kg IV<br/>a cada 4 semanas a partir dos 5 anos se meta<br/>não atingida com dose máxima tolerada, em<br/>centro especializado"])
  D2 -->|"Adulto (18 anos ou mais)"| D3{"Fator de risco aterosclerótico<br/>adicional?"}
  D3 -->|"Sim"| C2(["HoFH adulto de risco muito alto: meta de<br/>LDL-C abaixo de 55 mg/dL. Estatina de alta<br/>intensidade + ezetimiba desde o início; associar<br/>iPCSK9, ácido bempedoico, evinacumabe ou<br/>lomitapide conforme resposta, em centro<br/>especializado (monitorar esteatose hepática<br/>com lomitapide)"])
  D3 -->|"Não"| C3(["HoFH adulto: meta de LDL-C abaixo de<br/>70 mg/dL. Estatina de alta intensidade +<br/>ezetimiba desde o início; escalonar para<br/>iPCSK9, ácido bempedoico, evinacumabe ou<br/>lomitapide se meta não atingida, em centro<br/>especializado em lipidologia"])

  D1 -->|"Não"| N2["Calcular escore Dutch Lipid Clinic Network<br/>(DLCN) — maior pontuação por grupo, sem<br/>somar dentro do mesmo grupo: história familiar<br/>(até 2 pontos), história clínica (até 2), exame<br/>físico (até 6), LDL-C sem tratamento (até 8),<br/>análise de DNA (até 8)"]
  N2 --> D4{"Pontuação total do DLCN?"}
  D4 -->|"Mais de 6 pontos (HF definitiva:<br/>mais de 8; HF provável: 6 a 8)"| N3["Diagnóstico clínico de HF estabelecido.<br/>Confirmar por análise de DNA quando<br/>disponível (reforça, mas ausência não afasta<br/>o diagnóstico clínico); indicar rastreamento<br/>em cascata dos familiares de 1º grau"]
  D4 -->|"De 3 a 5 pontos (HF possível)"| C4(["HF possível: repetir perfil lipídico, investigar<br/>causas secundárias de LDL-C elevado<br/>(hipotireoidismo, síndrome nefrótica, colestase,<br/>fármacos) e considerar teste de DNA antes de<br/>fechar o diagnóstico"])
  D4 -->|"2 pontos ou menos<br/>(HF improvável)"| C5(["HF improvável: investigar causas secundárias<br/>de dislipidemia; não indicar rastreamento em<br/>cascata de familiares com base neste resultado"])

  N3 --> D5{"Idade do paciente?"}
  D5 -->|"Criança ou adolescente<br/>(5 a 17 anos)"| C6(["HF heterozigota pediátrica: testar a partir dos<br/>5 anos (ou antes se suspeita de HoFH); iniciar<br/>estatina entre 8 e 10 anos com orientação<br/>dietética; meta de LDL-C abaixo de 135 mg/dL<br/>(abaixo de 3,5 mmol/L) após os 10 anos; testar<br/>pais e irmãos"])
  D5 -->|"Adulto (18 anos ou mais)"| D6{"DCV aterosclerótica estabelecida OU<br/>outro fator de risco maior em<br/>prevenção primária?"}
  D6 -->|"Sim (risco muito alto)"| C7(["HF de risco muito alto: meta de LDL-C abaixo<br/>de 55 mg/dL e redução de pelo menos 50% do<br/>valor basal. Estatina de alta intensidade +<br/>ezetimiba; se meta não atingida, associar<br/>iPCSK9 ou ácido bempedoico"])
  D6 -->|"Não (alto risco)"| C8(["HF de alto risco: meta de LDL-C abaixo de<br/>70 mg/dL. Estatina de alta intensidade, com<br/>ou sem ezetimiba; escalonar com iPCSK9 ou<br/>ácido bempedoico se meta não atingida"])

  classDef conduta fill:#eef6ef,stroke:#2f7a4f,color:#12301f;
  class C1,C2,C3,C4,C5,C6,C7,C8 conduta;
```

## O que a árvore não mostra

**O DLCN não soma pontos dentro do mesmo grupo** — só a maior pontuação de cada uma das cinco categorias entra na soma final. Um paciente com xantoma tendíneo (6 pontos) e arco corneano antes dos 45 anos (4 pontos) pontua 6, não 10, porque os dois pertencem ao grupo de exame físico.

**Teste de DNA negativo não descarta HF.** A diretriz recomenda a confirmação genética quando disponível, mas o diagnóstico clínico por DLCN é suficiente para tratar — a ausência de mutação identificável não afasta HF clinicamente definida, porque nem toda causa genética de HF já foi mapeada.

**Em HoFH, o fenótipo tem prioridade sobre o genótipo quando os dois divergem** — um paciente com quadro clínico de HoFH (LDL-C muito alto desde a infância, xantomas precoces) é tratado como HoFH mesmo que o teste genético não confirme variantes bialélicas, e o inverso também vale: variantes bialélicas sem o fenótipo típico não bastam isoladamente.

**A conversão de Lp(a) entre mg/dL e nmol/L não é exata** (o tamanho da isoforma de apolipoproteína(a) varia entre indivíduos) — não é mostrada nesta árvore, mas deve entrar na avaliação de risco de todo paciente com HF, já que a diretriz recomenda medir Lp(a) ao menos uma vez na vida.

**Esta árvore não cobre suplementos ou vitaminas como alternativa a estatina** — a atualização ESC/EAS 2025 recomenda explicitamente contra essa estratégia (Classe III, Nível B) para reduzir risco de DCV aterosclerótica, independentemente da categoria de risco.
