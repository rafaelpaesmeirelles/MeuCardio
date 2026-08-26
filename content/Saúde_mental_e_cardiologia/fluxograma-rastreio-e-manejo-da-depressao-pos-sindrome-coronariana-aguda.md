---
title: "Fluxograma: Rastreio e Manejo da Depressão Após Síndrome Coronariana Aguda"
slug: fluxograma-rastreio-e-manejo-da-depressao-pos-sindrome-coronariana-aguda
theme: "Saúde mental e cardiologia"
kind: fluxograma
fonte_producao: chatgpt
review_status: revisado
review_note: "Verificado por Claude em 26/08/2026: fonte primaria conferida; conteudo derivado de documento(s) ja publicado(s) no acervo, listado(s) em source_refs."
source_refs:
  - "van Melle JP, de Jonge P, Spijkerman TA, et al. Prognostic association of depression following myocardial infarction with mortality and cardiovascular events: a meta-analysis. Psychosom Med. 2004;66(6):814-822. DOI: 10.1097/01.psy.0000146294.82810.9c. PMID: 15564344."
  - "Berkman LF, Blumenthal J, Burg M, et al; ENRICHD Investigators. Effects of treating depression and low perceived social support on clinical events after myocardial infarction: the Enhancing Recovery in Coronary Heart Disease (ENRICHD) Randomized Trial. JAMA. 2003;289(23):3106-3116. DOI: 10.1001/jama.289.23.3106. PMID: 12813116."
  - "Davidson KW, Rieckmann N, Clemow L, Schwartz JE, Shimbo D, Medina V, Albanese G, Kronish I, Hegel M, Burg MM. Enhanced depression care for patients with acute coronary syndrome and persistent depressive symptoms: coronary psychosocial evaluation studies randomized controlled trial. Arch Intern Med. 2010;170(7):600-608. DOI: 10.1001/archinternmed.2010.29. PMID: 20386003."
  - "Glassman AH, O'Connor CM, Califf RM, Swedberg K, Schwartz P, et al; SADHART Group. Sertraline treatment of major depression in patients with acute MI or unstable angina. JAMA. 2002;288(6):701-709. DOI: 10.1001/jama.288.6.701. PMID: 12169073."
  - "Lespérance F, Frasure-Smith N, Koszycki D, Laliberté MA, van Zyl LT, et al; CREATE Investigators. Effects of citalopram and interpersonal psychotherapy on depression in patients with coronary artery disease: the CREATE trial. JAMA. 2007;297(4):367-379. DOI: 10.1001/jama.297.4.367. PMID: 17244833."
  - "Angermann CE, Gelbrich G, Störk S, Gunold H, Edelmann F, et al; MOOD-HF Study Investigators. Effect of Escitalopram on All-Cause Mortality and Hospitalization in Patients With Heart Failure and Depression: The MOOD-HF Randomized Clinical Trial. JAMA. 2016;315(24):2683-2693. DOI: 10.1001/jama.2016.7635. PMID: 27367876."
  - "Derivado de depressao-pos-infarto-como-fator-de-risco-cardiovascular-van-melle-e-enrichd.md, ensaio-copes-cuidado-otimizado-de-depressao-apos-sindrome-coronariana-aguda.md e tratar-a-depressao-melhora-o-desfecho-cardiaco-sadhart-create-e-mood-hf.md, já publicados no acervo (Saúde mental e cardiologia)."
---

# Fluxograma: Rastreio e Manejo da Depressão Após Síndrome Coronariana Aguda

Depressão pós-infarto não tratada dobra o risco de morte e de novo evento cardiovascular. Mas os três ensaios que testaram tratá-la — ENRICHD, CREATE e MOOD-HF — mostram algo que não decorre automaticamente dessa associação: **melhorar o sintoma depressivo não reduziu, em nenhum deles, mortalidade ou reinfarto.** Este fluxograma une o rastreio (por que ele importa, mesmo sem prometer benefício cardíaco) ao modelo de cuidado (COPES) e à escolha farmacológica por contexto clínico (SADHART, CREATE, MOOD-HF), reunindo três documentos já publicados nesta pasta que, até aqui, tratavam cada pergunta em separado.

## Árvore de decisão

```mermaid
flowchart TD
  R0["Paciente com síndrome coronariana aguda, em<br/>avaliação de sintomas depressivos após<br/>a fase aguda"] --> D1{"Sintomas depressivos persistentes confirmados<br/>por instrumento estruturado, além do<br/>período agudo inicial?"}

  D1 -->|"Não"| C1(["Sem depressão persistente identificada nesta<br/>avaliação; manter vigilância clínica de rotina —<br/>depressão pós-infarto é fator de risco<br/>independente de mortalidade e de novo evento<br/>cardiovascular (OR de 2 a 2,5, van Melle et al.,<br/>2004), mesmo quando ausente no<br/>rastreio inicial"])

  D1 -->|"Sim"| P1["Depressão confirmada é fator de risco<br/>cardiovascular independente (van Melle et al.:<br/>OR 2,38 para mortalidade por qualquer causa;<br/>OR 2,59 para mortalidade cardíaca). Tratar é<br/>indicado pela própria depressão, não pela<br/>expectativa de reduzir esse risco — no ENRICHD,<br/>a intervenção psicossocial melhorou os escores<br/>de depressão e de suporte social, mas não<br/>reduziu morte nem reinfarto"]
  P1 --> D2{"É possível oferecer ao paciente um modelo de<br/>cuidado escalonado, com escolha entre terapia<br/>de resolução de problemas e/ou farmacoterapia<br/>(stepped care)?"}
  D2 -->|"Sim"| C2(["Oferecer cuidado escalonado guiado pela<br/>preferência do paciente (modelo COPES): maior<br/>satisfação com o cuidado (54% vs. 19%) e<br/>maior redução de sintomas depressivos<br/>(-5,7 vs. -1,9 pontos no Beck Depression<br/>Inventory) do que o cuidado usual"])
  D2 -->|"Não, apenas terapia<br/>padrão disponível"| D3{"Contexto cardiovascular do paciente"}
  D3 -->|"Doença coronariana (aguda ou estável),<br/>sem insuficiência cardíaca"| C3(["Sertralina (SADHART) ou citalopram associado<br/>a manejo clínico estruturado (CREATE) são<br/>opções de primeira etapa, com segurança e<br/>eficácia antidepressiva estabelecidas nesse<br/>contexto; psicoterapia interpessoal isolada não<br/>acrescentou benefício sobre o manejo clínico<br/>estruturado no CREATE"])
  D3 -->|"Insuficiência cardíaca com fração<br/>de ejeção reduzida"| C4(["Tratar a depressão continua indicado pela<br/>própria depressão; no MOOD-HF, escitalopram<br/>não superou o placebo na melhora da depressão<br/>nem reduziu mortalidade ou internação nessa<br/>população — não prometer benefício<br/>cardíaco ao tratar"])

  classDef conduta fill:#eef6ef,stroke:#2f7a4f,color:#12301f;
  class C1,C2,C3,C4 conduta;
```

## O que a árvore não mostra

**A magnitude do risco associado à depressão não é fixa no tempo** — a própria metanálise de van Melle mostrou atenuação (embora não eliminação) do risco nos estudos mais recentes, possivelmente refletindo evolução do tratamento cardiológico padrão.

**O braço placebo do MOOD-HF também melhorou muito** (escala de depressão caindo de 21,4 para 12,5) — o que sugere que cuidado estruturado e contato regular têm efeito relevante por si só, independentemente do fármaco.

**Nenhum dos ensaios aqui citados testou terapia cognitivo-comportamental especificamente** — o braço psicoterápico do ENRICHD e do CREATE usou, respectivamente, terapia cognitivo-comportamental geral e psicoterapia interpessoal; os resultados não devem ser generalizados para todo formato de psicoterapia.

**Checar interação medicamentosa e QTc antes de escolher o antidepressivo** — a segurança estabelecida pelo SADHART é de fármacos específicos (sertralina, citalopram), não da classe inteira; ver o fluxograma de escolha de antidepressivo e antipsicótico no cardiopata, nesta mesma pasta.
