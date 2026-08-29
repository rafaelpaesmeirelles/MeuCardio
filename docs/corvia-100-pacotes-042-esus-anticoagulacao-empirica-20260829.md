# CorVIA 100 pacotes — 042/100 — ESUS e anticoagulação empírica

Data: 29/08/2026  
Base auditada: `main` `59566e1196e0fa7f465df93516790ef454e1f565`

## Objetivo

Revisar adversarialmente a estratégia de anticoagulação empírica após AVC embólico de fonte indeterminada (ESUS) e após AVC criptogênico com cardiopatia atrial sem fibrilação atrial documentada, evitando que suspeita de mecanismo embólico seja convertida automaticamente em indicação de DOAC.

## Evidência crítica verificada

- **NAVIGATE ESUS** — Hart RG et al. N Engl J Med. 2018;378:2191-2201. PMID `29766772`; DOI `10.1056/NEJMoa1802686`.
  - 7.213 pacientes com ESUS recente.
  - Rivaroxabana 15 mg/dia versus AAS 100 mg/dia.
  - Primário de eficácia: HR 1,07 (IC95% 0,87-1,33; p=0,52): sem superioridade.
  - Sangramento maior: HR 2,72 (IC95% 1,68-4,39; p<0,001), maior com rivaroxabana.
  - O ensaio foi interrompido precocemente por ausência de benefício e sangramento.
- **RE-SPECT ESUS** — Diener HC et al. N Engl J Med. 2019;380:1906-1917. PMID `31091372`; DOI `10.1056/NEJMoa1813959`.
  - 5.390 pacientes.
  - Dabigatrana 150 ou 110 mg 2x/dia versus AAS 100 mg/dia.
  - AVC recorrente: HR 0,85 (IC95% 0,69-1,03; p=0,10): sem superioridade.
  - Sangramento maior: HR 1,19 (IC95% 0,85-1,66); houve mais sangramento clinicamente relevante não maior com dabigatrana.
- **ARCADIA** — Kamel H et al. JAMA. 2024;331:573-581. PMID `38324415`; DOI `10.1001/jama.2023.27188`.
  - AVC criptogênico + marcadores de cardiopatia atrial, sem FA documentada.
  - Apixabana não reduziu recorrência de AVC versus AAS; o estudo foi interrompido por futilidade.
- Análise de segurança do ARCADIA publicada em 2026: PMID `41741942`; DOI `10.1002/ana.78186`. Achados hemorrágicos favoráveis à apixabana em alguns endpoints **não revertem a neutralidade do desfecho de eficácia do RCT principal**.

## Revisão adversarial independente

1. **ESUS não é sinônimo de FA oculta:** o fenótipo é heterogêneo; ateroma aórtico, PFO, câncer, doença atrial, fontes arteriais não estenosantes e outras etiologias precisam ser procuradas.
2. **Três RCTs não sustentam DOAC empírico de rotina:** NAVIGATE ESUS e RE-SPECT ESUS foram neutros para superioridade; ARCADIA também foi neutro mesmo enriquecendo cardiopatia atrial.
3. **Subgrupo não deve anular o primário:** análises posteriores podem gerar hipóteses, mas não substituem o resultado randomizado principal.
4. **Segurança não é eficácia:** menor hemorragia intracraniana em uma análise secundária não significa prevenção superior de AVC recorrente.
5. **Se FA for documentada, a pergunta clínica muda:** o paciente deixa de estar no cenário de anticoagulação empírica por ESUS e passa a ser avaliado segundo evidência própria de FA e prevenção cardioembólica.
6. **PFO, trombo ventricular, prótese, estenose mitral e outras fontes definidas são cenários distintos:** não transportar os resultados de ESUS para indicações estabelecidas de anticoagulação.

## Guardrails para CorVIA

- bloquear `AVC criptogênico/ESUS = anticoagular empiricamente`;
- bloquear `cardiopatia atrial sem FA = indicação comprovada de apixabana`;
- não promover subgrupos de NAVIGATE ESUS/RE-SPECT ESUS a recomendação clínica geral;
- separar investigação etiológica prolongada de decisão antitrombótica;
- quando houver FA ou outra fonte cardioembólica definida, redirecionar para o protocolo específico;
- não inventar classe/nível AHA/ASA, ESC ou SBC a partir do p-valor dos ensaios.

## Verificação no corpus

A `main` já referencia explicitamente o documento clínico `anticoagulacao-empirica-no-avc-criptogenico-sem-fa-documentada-navigate-esus-re-spect-esus-e-arcadia` no hub de AVC agudo. Este pacote é uma revisão adversarial independente do eixo científico; **nenhum slug, JSON clínico ou regra foi alterado**.

## Resultado

Gap de segurança fechado documentalmente: **não há suporte para anticoagulação oral empírica de rotina em ESUS ou cardiopatia atrial sem FA documentada com base em NAVIGATE ESUS, RE-SPECT ESUS ou ARCADIA**.
