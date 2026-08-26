---
title: "Fluxograma: ICFElr (FEVE 41-49%) — diagnóstico diferencial e escolha terapêutica farmacológica"
slug: fluxograma-icfelr-diagnostico-diferencial-e-tratamento-farmacologico
theme: "Insuficiência cardíaca"
kind: fluxograma
fonte_producao: chatgpt
review_status: revisado
review_note: "Corpus conferido antes de escrever (ls em content/Insuficiência_cardíaca/, 106 arquivos): o único fluxograma que toca a faixa 41-49% é fluxograma-insuficiencia-cardiaca-cronica-por-fracao-de-ejecao-esc-2023.md, e cobre só um ramo raso (FEVE 41-49% -> iSGLT2 Classe I), sem diagnóstico diferencial nem as demais classes farmacológicas da ICFEmr. O fluxograma-manejo-icfep-fenotipo-dirigido-acc-2026.md e o documento acc-2026-expert-consensus-icfep-diagnostico-fenotipos-e-tratamento.md tratam de ICFEp (FEVE >= 50%), fora deste recorte. Nenhum documento do corpus cobre a distinção diagnóstica central da ICFEmr -- FE 'melhorada' (HFimpEF, ICFEr prévia com recuperação, categoria formalizada pela Universal Definition of HF 2021/2021 ESC Guidelines) versus ICFEmr 'de novo' -- que muda a conduta terapêutica (manter os quatro pilares já otimizados vs. escalonamento com classes de recomendação IIb). Este fluxograma preenche essa lacuna. Quatro PMIDs conferidos nesta sessão via PubMed E-utilities (esearch/esummary), título/revista/ano batendo exatamente: McDonagh TA et al., 2021 ESC Guidelines for HF, Eur Heart J 2021;42(36):3599-3726, PMID 34447992; McDonagh TA et al., 2023 Focused Update, Eur Heart J 2023;44(37):3627-3639, PMID 37622666; Heidenreich PA et al., 2022 AHA/ACC/HFSA Guideline, Circulation 2022;145(18):e895-e1032, PMID 35363499; Halliday BP et al., TRED-HF, Lancet 2019;393(10166):61-73, PMID 30429050 (busca inicial por PMID de memória havia resolvido para artigo errado, corrigida por esearch pelo título exato antes de citar). As classes de recomendação IECA/BRA/ARNI/betabloqueador/antagonista mineralocorticoide = IIb, Nível C na ICFEmr, e iSGLT2 = Classe I, Nível A (atualização focada 2023), foram reaproveitadas de verificação já registrada em sessão anterior deste mesmo projeto em atualizacao-focada-2023-das-diretrizes-esc-2021-de-insuficiencia-cardiaca.md, conferidas ali contra o texto integral da diretriz-base ESC 2021 via mirror aberto (pascar.org) por não haver acesso direto ao Oxford Academic (403/Cloudflare, bloqueio catalogado no CLAUDE.md do projeto) -- não reconferidas página a página nesta sessão, mas com procedência registrada e auditável. EMPEROR-Preserved (PMID 34449189) e DELIVER (PMID 36027570), que sustentam a extensão do iSGLT2 à faixa 41-49%, também já verificados em documentos publicados desta mesma pasta (inibidores-de-sglt2-na-icfep-empagliflozina-emperor-preserved-e-dapagliflozina-deliver.md)."
source_refs: ["McDonagh TA, Metra M, Adamo M, et al. 2021 ESC Guidelines for the diagnosis and treatment of acute and chronic heart failure. Eur Heart J. 2021;42(36):3599-3726. DOI: 10.1093/eurheartj/ehab368. PMID: 34447992", "McDonagh TA, Metra M, Adamo M, et al. 2023 Focused Update of the 2021 ESC Guidelines for the diagnosis and treatment of acute and chronic heart failure. Eur Heart J. 2023;44(37):3627-3639. DOI: 10.1093/eurheartj/ehad195. PMID: 37622666", "Heidenreich PA, Bozkurt B, Aguilar D, et al. 2022 AHA/ACC/HFSA Guideline for the Management of Heart Failure. Circulation. 2022;145(18):e895-e1032. DOI: 10.1161/CIR.0000000000001063. PMID: 35363499", "Halliday BP, Wassall R, Lota AS, et al. Withdrawal of pharmacological treatment for heart failure in patients with recovered dilated cardiomyopathy (TRED-HF): an open-label, pilot, randomised trial. Lancet. 2019;393(10166):61-73. DOI: 10.1016/S0140-6736(18)32484-X. PMID: 30429050", "Anker SD, Butler J, Filippatos G, et al. Empagliflozin in Heart Failure with a Preserved Ejection Fraction (EMPEROR-Preserved). N Engl J Med. 2021;385(16):1451-1461. PMID: 34449189", "Solomon SD, McMurray JJV, Claggett B, et al. Dapagliflozin in Heart Failure with Mildly Reduced or Preserved Ejection Fraction (DELIVER). N Engl J Med. 2022;387(12):1089-1098. PMID: 36027570"]
---

# Fluxograma: ICFElr (FEVE 41-49%) — diagnóstico diferencial e escolha terapêutica farmacológica

A insuficiência cardíaca com fração de ejeção levemente reduzida (ICFElr, HFmrEF, FEVE
41-49%) não é uma categoria homogênea. A Universal Definition of Heart Failure (2021) e as
Diretrizes ESC 2021 formalizaram uma distinção que muda diretamente a conduta: parte dos
pacientes com FEVE hoje entre 41 e 49% teve, no passado, ICFEr (FEVE ≤ 40%) e melhorou sob
tratamento — é a IC com fração de ejeção melhorada (ICFE melhorada, HFimpEF) —, enquanto
outra parte nunca teve FEVE ≤ 40% documentada, sendo ICFElr "de novo". O ensaio TRED-HF
mostrou que suspender a terapia médica otimizada em quem melhorou a FEVE não é seguro: a
recidiva foi próxima de 40% em 6 meses no grupo que teve a medicação retirada. Por isso, a
primeira pergunta antes de escalonar terapia numa FEVE de 41-49% é se esse paciente já foi
ICFEr — a resposta muda a base do tratamento antes mesmo de discutir qual classe adicionar.

## Árvore de decisão

```mermaid
flowchart TD
  R0["IC crônica sintomática com FEVE atual 41-49% na ecocardiografia (ICFElr/HFmrEF, ESC 2021/2023)<br/>NT-proBNP ou BNP elevado e evidência estrutural/funcional compatível"]
  D1{"FEVE ≤ 40% documentada em algum momento anterior, com aumento ≥ 10 pontos percentuais para a faixa atual (41-49%)?"}
  C1(["Classificar como ICFE melhorada (HFimpEF), não ICFElr 'de novo' (Universal Definition of HF, 2021 ESC Guidelines)<br/>MANTER os quatro pilares já otimizados da ICFEr: IECA/ARNI, betabloqueador, antagonista mineralocorticoide e iSGLT2<br/>NÃO suspender a terapia mesmo com FEVE normalizada — TRED-HF: suspensão associada a recidiva em cerca de 40% em 6 meses (Halliday et al., Lancet 2019)"])
  P1["Confirmar o diagnóstico de ICFElr 'de novo': excluir causa estrutural que explique melhor o quadro (valvopatia significativa não corrigida, doença pericárdica, estado de alto débito) e confirmar peptídeo natriurético elevado"]
  P2["Iniciar inibidor de SGLT2 (dapagliflozina ou empagliflozina) — Classe I, Nível A<br/>(2023 Focused Update ESC; base de evidência EMPEROR-Preserved e DELIVER, que incluíram a faixa de FEVE 41-49%)"]
  D2{"Fenótipo ou comorbidade que module a terapia farmacológica adicional ao iSGLT2?"}
  C2(["Considerar IECA/BRA ou sacubitril-valsartana (ARNI) associado ao iSGLT2 — Classe IIb, Nível C<br/>(ESC 2021, extrapolado de subgrupos do PARAGON-HF e da análise combinada PARADIGM-HF+PARAGON-HF; mantido pela atualização de 2023; AHA/ACC/HFSA 2022 concorda com a extrapolação de subgrupo)"])
  C3(["Considerar betabloqueador associado ao iSGLT2 — Classe IIb, Nível C<br/>(ESC 2021, mantido pela atualização de 2023 — indicação reforçada se houver fibrilação atrial permanente, isquemia ou outra indicação própria de betabloqueador)"])
  C4(["Considerar antagonista mineralocorticoide (espironolactona) associado ao iSGLT2 — Classe IIb, Nível C<br/>(ESC 2021, extrapolado de subgrupo do TOPCAT com FEVE < 55%; mantido pela atualização de 2023; monitorizar potássio e função renal)"])
  C5(["Manter iSGLT2 como pilar de eficácia comprovada + diurético de alça para controle de sintomas congestivos — Classe I, Nível C<br/>Reavaliar fenótipo, comorbidades e função ventricular na evolução"])
  R0 --> D1
  D1 -->|"Sim — trajetória de melhora documentada"| C1
  D1 -->|"Não — sem FEVE ≤ 40% prévia, ou aumento inferior a 10 pontos"| P1
  P1 --> P2
  P2 --> D2
  D2 -->|"Indicação de bloqueio do SRAA (hipertensão associada, proteinúria)"| C2
  D2 -->|"Fibrilação atrial permanente ou outra indicação de controle de frequência/isquemia"| C3
  D2 -->|"Potássio ≤ 5,0 mEq/L e TFGe ≥ 30 mL/min/1,73m², sem outra indicação específica acima"| C4
  D2 -->|"Nenhum fenótipo adicional específico além de congestão"| C5

  classDef conduta fill:#eef6ef,stroke:#2f7a4f,color:#12301f;
  class C1,C2,C3,C4,C5 conduta;
```

Duas armadilhas clínicas que este fluxograma resolve explicitamente. A primeira é tratar
toda FEVE de 41-49% como uma única entidade: um paciente que já foi ICFEr e melhorou não
deve ter a terapia desescalonada só porque a fração de ejeção normalizou — o TRED-HF mostrou
que a melhora depende da manutenção do tratamento, não é uma cura estrutural. A segunda é
esperar, na ICFElr "de novo", o mesmo nível de evidência da ICFEr: só o iSGLT2 tem ensaio
randomizado dedicado a essa faixa (recomendação Classe I); IECA/BRA, ARNI, betabloqueador e
antagonista mineralocorticoide seguem em Classe IIb, Nível C, apoiados em subgrupos de
ensaios desenhados para ICFEr ou ICFEp — a decisão de associá-los deve ser individualizada
pelo fenótipo do paciente, não automática.