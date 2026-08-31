# Revisão adversarial 018/100 — anemia, deficiência de ferro e risco cardiovascular

Data: 29/08/2026  
Base auditada: `main` `59566e1196e0fa7f465df93516790ef454e1f565`  
Objeto: `doencas/fragmentos/zzz-codex-20260829-anemia-deficiencia-de-ferro-e-risco-cardiovascular.json`  
Slug auditado: `anemia-deficiencia-de-ferro-e-risco-cardiovascular`

## Objetivo

Revisão adversarial independente focada nos pontos de maior risco de extrapolação: confundir anemia com deficiência de ferro, transformar ferro intravenoso em tratamento indiscriminado de anemia, usar agente estimulador de eritropoiese para melhorar prognóstico da insuficiência cardíaca, aplicar limiar transfusional de paciente estável ao infarto agudo do miocárdio e vender resultado não significativo do MINT como superioridade.

## Fontes primárias/diretrizes verificadas

1. Heidenreich PA, Bozkurt B, Aguilar D, et al. 2022 AHA/ACC/HFSA Guideline for the Management of Heart Failure. *Circulation*. 2022;145:e895-e1032. DOI: `10.1161/CIR.0000000000001063`.
2. McDonagh TA, Metra M, Adamo M, et al. 2023 Focused Update of the 2021 ESC Guidelines for the diagnosis and treatment of acute and chronic heart failure. *Eur Heart J*. 2023;44:3627-3639. DOI: `10.1093/eurheartj/ehad195`.
3. Carson JL, Brooks MM, Hébert PC, et al. Restrictive or Liberal Transfusion Strategy in Myocardial Infarction and Anemia (MINT). *N Engl J Med*. 2023;389:2446-2456. DOI: `10.1056/NEJMoa2307983`. PMID: `37952133`.
4. Carson JL, et al. Restrictive versus Liberal Transfusion in Myocardial Infarction — A Patient-Level Meta-Analysis. *NEJM Evidence*. 2025. PMID: `39714935`.

## Perguntas adversariais e resultado

### 1. O hub confunde deficiência de ferro com anemia?

**Não.** O texto reconhece que deficiência de ferro pode existir com ou sem anemia e exige avaliação com ferritina e saturação de transferrina no fenótipo apropriado. Também diferencia reposição de ferro de transfusão de hemácias.

### 2. A recomendação AHA/ACC/HFSA para ferro intravenoso foi reproduzida corretamente?

**Sim.** A diretriz de 2022 considera, em pacientes com HFrEF e deficiência de ferro com ou sem anemia, ferro intravenoso razoável para melhorar estado funcional e qualidade de vida: **Classe IIa, nível B-R**. O hub não transforma essa recomendação em tratamento para qualquer anemia nem em prova de redução de mortalidade.

### 3. O hub sugere eritropoetina/ESA para melhorar morbimortalidade da IC?

**Não.** Ele registra corretamente que agentes estimuladores de eritropoiese **não devem** ser usados na insuficiência cardíaca com o objetivo de melhorar morbidade/mortalidade, reproduzindo **Classe III: dano, nível B-R** da AHA/ACC/HFSA 2022.

### 4. O MINT foi apresentado como prova de superioridade da estratégia liberal?

**Não.** A população e o resultado foram preservados: pacientes com IAM e hemoglobina <10 g/dL, estratégia restritiva versus liberal; a diferença no desfecho primário de morte ou IAM em 30 dias não atingiu significância estatística convencional. O hub registra que possível dano da estratégia restritiva não pôde ser excluído, sem declarar vitória estatística da estratégia liberal.

### 5. O texto importa limiar transfusional de pacientes estáveis para IAM?

**Não.** Pelo contrário, alerta que IAM com anemia é um cenário diferente e que a decisão transfusional deve integrar isquemia, sintomas, estabilidade, sangramento e comorbidades.

### 6. Há risco de vínculo documental inventado?

**Não.** `related_document_slugs` permanece vazio. Nenhum vínculo foi criado sem confirmação de um documento central com slug estável.

## Achados de segurança

- Preservar a separação conceitual entre anemia, deficiência de ferro, ferro IV e transfusão.
- Não extrapolar benefício funcional/qualidade de vida do ferro IV em HFrEF para redução comprovada de mortalidade.
- Não usar ESA para melhorar desfechos de IC.
- No IAM, evitar aplicar automaticamente limiar transfusional restritivo derivado de populações clínicas estáveis.
- A queda inexplicada de hemoglobina em paciente em anticoagulação/antiagregação deve manter busca ativa de sangramento.

## Decisão editorial

**Aprovado na revisão adversarial quanto aos pontos críticos auditados, sem alteração do conteúdo clínico.** Nenhum erro bloqueante foi identificado. O `review_status` original foi preservado, bem como schema, regras e decisões editoriais humanas.

## Validações estruturais

- Revisão exclusivamente aditiva em `docs/`.
- Nenhum JSON clínico modificado.
- Nenhum slug criado ou alterado.
- Nenhuma relação Tudo com Tudo adicionada por inferência.
- MINT confirmado: DOI `10.1056/NEJMoa2307983`, PMID `37952133`.
- Metanálise individual confirmada pelo PMID `39714935`.
- Sem necessidade de teste dependente de banco para este pacote documental.
