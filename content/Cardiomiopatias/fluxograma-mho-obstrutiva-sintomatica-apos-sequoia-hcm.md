---
kind: fluxograma
published: true
review_note: Revisão individual contra SEQUOIA, análise JACC/JAHA, MAPLE, EXPLORER
  e VALOR; resultados, denominadores, moléculas e respostas conferidos. Corrigido
  alívio versus prevalência de sintomas, limites de FEVE e interrupção na dose mínima
  pela FDA 2025, árvores e avaliação esportiva pela AHA/ACC 2024. Resumo didático
  de RC não afirma quatro componentes oficiais. Sem assumir registro brasileiro.
review_status: revisado
slug: fluxograma-mho-obstrutiva-sintomatica-apos-sequoia-hcm
source_refs:
- 'Maron MS, Masri A, Nassif ME, et al. Aficamten for Symptomatic Obstructive Hypertrophic
  Cardiomyopathy. N Engl J Med. 2024;390(20):1849-1861. DOI: 10.1056/NEJMoa2401424.
  PMID: 38739079. NCT05186818.'
- 'Maron MS, et al. Impact of Aficamten on Disease and Symptom Burden in Obstructive
  Hypertrophic Cardiomyopathy: Results From SEQUOIA-HCM. J Am Coll Cardiol. 2024;84(19):1821-1831.
  DOI: 10.1016/j.jacc.2024.09.003. PMID: 39352339.'
- FDA. MYQORZO (aficamten) prescribing information, 2025, sections 2 and 5. https://www.accessdata.fda.gov/drugsatfda_docs/label/2025/219083s000lbl.pdf
theme: Cardiomiopatias
title: 'Fluxograma: MHO obstrutiva sintomática após SEQUOIA-HCM'
---

# Fluxograma: MHO obstrutiva sintomática após SEQUOIA-HCM

Pergunta desta árvore: **neste paciente com miocardiopatia hipertrófica obstrutiva sintomática, o SEQUOIA-HCM informa o uso de aficamten?** Folhas verdes são condutas. O ensaio mediu **VO₂ pico em 24 semanas**, não mortalidade nem morte súbita. Redução septal continua existindo.

## Árvore de decisão

```mermaid
flowchart TD
    R0["MHO com sintomas limitantes"] --> D1{"Obstrução da via de saída<br/>documentada?"}

    D1 -->|"Não — não obstrutiva"| C1(["SEQUOIA-HCM não se aplica.<br/>Aficamten foi testado na forma obstrutiva.<br/>Não extrapolar."])
    D1 -->|"Sim"| D2{"Sintomas apesar da terapia de base?"}

    D2 -->|"Não — oligossintomático"| C2(["Reavaliar sintomas e fatores precipitantes;<br/>individualizar tratamento e contraindicações.<br/>SEQUOIA entrou com doença sintomática."])
    D2 -->|"Sim"| D3{"Candidato a inibidor de miosina<br/>com eco serial disponível?"}

    D3 -->|"Não — sem eco de titulação"| C4(["Não iniciar aficamten sem via de<br/>monitoramento da FEVE e do gradiente.<br/>Encaminhar a centro de MHO."])
    D3 -->|"Sim"| C5["SEQUOIA-HCM: n=282; 142 vs 140.<br/>VO2 pico +1,8 vs 0,0 mL/kg/min.<br/>Diferença 1,7; IC95% 1,0–2,4; P menor que 0,001.<br/>Dose 5–20 mg. Não é ensaio de mortalidade."]

    C5 --> D4{"Ainda elegível a redução septal?"}
    D4 -->|"Sim, sintomas persistentes"| C6(["Redução septal permanece opção.<br/>No SEQUOIA, 28/32 (88%) vs 15/29 (52%)<br/>deixaram de ser elegíveis a 24 semanas.<br/>Não prometer que o fármaco a substitui."])
    D4 -->|"Não"| C7(["Reavaliar resposta e segurança conforme bula específica;<br/>não manter automaticamente diante de queda da FEVE."])

    classDef conduta fill:#eef6ef,stroke:#2f7a4f,color:#12301f;
    class C1,C2,C4,C6,C7 conduta;
```

## Números que cabem na folha C5

282 randomizados (142 aficamten, 140 placebo). Idade média 59,1 anos; 59,2% homens; gradiente em repouso 55,1 mmHg; FEVE média 74,8%. 24 semanas. VO₂ pico: **+1,8** (1,2 a 2,3) vs **0,0** (−0,5 a 0,5); diferença de mínimos quadrados **1,7** mL/kg/min (1,0 a 2,4); P<0,001. Dose inicial 5 mg, máxima 20 mg, ajustada por eco.

Carga de doença (JACC, PMID 39352339): resposta hemodinâmica completa **68% vs 7%**; queda ≥50% do NT-proBNP **84% vs 8%**; os quatro critérios de resposta **23% vs 0**.

## O que a árvore não mostra

**Mavacamten.** SEQUOIA testou aficamten. Não é comparação de cabeça. Não inventar classe ESC/AHA para aficamten neste fluxograma.

**Morte súbita e CDI.** O ensaio não informa indicação de desfibrilador. Fatores de risco súbito seguem a diretriz de MHO, não esta árvore.

**Esporte.** Aporta na porta de Cardiologia do Esporte e do Exercício; o SEQUOIA não reescreve restrição esportiva.

## Tudo com Tudo

Cardiomiopatias · Farmacologia · Insuficiência cardíaca · Reabilitação cardíaca · Comunicação clínica · Cardiologia do Esporte e do Exercício.

Referência FDA 2025 (EUA): não iniciar/aumentar aficamten com FEVE <55%. FEVE 40 a <50%: reduzir 5 mg; se já em 5 mg, interromper. FEVE <40%: interromper. Reintrodução, quando cabível, somente após pelo menos sete dias e FEVE ≥55%, em 5 mg. Eco após início/ajuste e avaliação de interações são indispensáveis. Não transpor esses limites para mavacamten nem afirmar aprovação brasileira.
