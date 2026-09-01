# CorVIA 100 pacotes — 044/100 — Omecamtiv mecarbil: GALACTIC-HF e METEORIC-HF

Data: 29/08/2026  
Base auditada: `main` `59566e1196e0fa7f465df93516790ef454e1f565`

## Objetivo

Revisar adversarialmente a evidência do ativador de miosina omecamtiv mecarbil na ICFEr, separando o pequeno benefício no composto clínico do GALACTIC-HF de mortalidade, sintomas, qualidade de vida e capacidade de exercício.

## Evidência crítica verificada

- **GALACTIC-HF** — Teerlink JR et al. N Engl J Med. 2021;384:105-116. PMID `33185990`; DOI `10.1056/NEJMoa2025797`.
  - 8.256 pacientes com IC sintomática e FEVE ≤35%, hospitalizados ou ambulatoriais.
  - Omecamtiv mecarbil versus placebo, além do tratamento de IC.
  - Primeiro evento de IC ou morte CV: 37,0% vs 39,1%; HR 0,92 (IC95% 0,86-0,99; p=0,03).
  - Morte CV: 19,6% vs 19,4%; HR 1,01 (IC95% 0,92-1,11): sem benefício.
  - Não houve diferença significativa no KCCQ total symptom score.
  - Houve pequeno aumento mediano de troponina I, sem excesso aparente de eventos isquêmicos ou arritmia ventricular no RCT.
- **METEORIC-HF** — Lewis GD et al. JAMA. 2022;328:259-269. PMID `35852527`; DOI `10.1001/jama.2022.11016`.
  - 276 pacientes com ICFEr ≤35%, NYHA II-III e limitação objetiva de exercício.
  - Mudança de pico de VO2 em 20 semanas: diferença ajustada -0,45 mL/kg/min (IC95% -1,02 a 0,13; p=0,13).
  - O omecamtiv mecarbil **não melhorou significativamente a capacidade de exercício**.
- **ESC 2026 Heart Failure Guidelines** — Køber L et al. Eur Heart J. 2026; DOI `10.1093/eurheartj/ehag100`. Qualquer posição terapêutica, classe ou nível vigente deve ser verificada diretamente na diretriz; o RCT isolado não gera recomendação normativa.

## Revisão adversarial independente

1. **Composto positivo ≠ mortalidade positiva:** GALACTIC-HF demonstrou redução modesta do composto de primeiro evento de IC/morte CV, mas morte cardiovascular isolada foi neutra.
2. **Benefício clínico ≠ melhora de sintomas:** KCCQ não melhorou significativamente no GALACTIC-HF.
3. **Benefício clínico ≠ melhora de exercício:** METEORIC-HF foi negativo para pico de VO2.
4. **Mecanismo inovador não autoriza status de terapia fundacional:** qualquer colocação na sequência terapêutica depende de diretriz atual, disponibilidade e avaliação regulatória, não apenas do p=0,03.
5. **Subgrupos de FEVE muito baixa são geradores de hipótese:** sinais de heterogeneidade não devem ser promovidos a indicação categórica sem recomendação formal.
6. **Troponina deve ser contextualizada:** aumento biomarcador observado no estudo não deve ser automaticamente interpretado como IAM, mas também não deve ser omitido da discussão de segurança.

## Guardrails para CorVIA

- bloquear `omecamtiv reduz mortalidade cardiovascular`;
- bloquear `omecamtiv melhora capacidade funcional/exercício` com base no programa atual;
- separar `evento de IC` de `morte CV` ao descrever o primário do GALACTIC-HF;
- não transformar subgrupo por FEVE em indicação automática;
- não posicionar o medicamento como substituto das terapias fundacionais da ICFEr;
- classe/nível somente após leitura da diretriz vigente e nunca inferidos do ensaio.

## Resultado

Gap de interpretação fechado: **GALACTIC-HF mostrou benefício estatisticamente significativo, porém modesto, no composto de evento de IC/morte CV, sem redução de morte CV isolada; METEORIC-HF não mostrou melhora da capacidade de exercício**.

Nenhum arquivo clínico, slug, JSON, regra, schema ou loader foi alterado neste pacote.
