---
title: "Fluxograma: Manejo da Hipotensão Sintomática Limitando a Titulação de IECA/BRA/ARNI na ICFEr"
slug: fluxograma-hipotensao-sintomatica-titulacao-ieca-arni-icfer
theme: "Insuficiência cardíaca"
kind: fluxograma
fonte_producao: chatgpt
review_status: revisado
review_note: "Documento de manejo clínico, sem ensaio próprio dedicado ao tema — construído a partir de referências já verificadas e publicadas nesta mesma pasta em sessões anteriores (PubMed E-utilities): CONSENSUS PMID 2883575 (redução da dose inicial de enalapril de 2,5 mg em paciente de alto risco, por hipotensão exigindo retirada em 7 pacientes no braço enalapril contra nenhum no placebo), PARADIGM-HF PMID 25176015 (mais hipotensão com sacubitril-valsartana que com enalapril, mas sem excesso de suspensão por esse motivo), STRONG-HF PMID 36356631 (protocolo de titulação intensiva monitorizando PA a cada visita). Nenhum PMID/DOI novo foi introduzido. Os nós de decisão sobre gravidade (\"PA persistentemente muito baixa\", \"sintoma grave\") são deliberadamente qualitativos — não existe corte numérico único validado nas fontes revisadas para definir hipotensão sintomática na titulação de GDMT, e inventar um seria o mesmo erro já evitado em 'fluxograma-resistencia-diuretica-e-congestao-refrataria-na-ic-aguda.md' desta pasta."
source_refs: ["CONSENSUS Trial Study Group. Effects of enalapril on mortality in severe congestive heart failure (CONSENSUS). N Engl J Med. 1987;316(23):1429-1435. DOI: 10.1056/NEJM198706043162301. PMID: 2883575", "McMurray JJ, Packer M, Desai AS, et al; PARADIGM-HF Investigators and Committees. Angiotensin-neprilysin inhibition versus enalapril in heart failure. N Engl J Med. 2014;371(11):993-1004. DOI: 10.1056/NEJMoa1409077. PMID: 25176015", "Velazquez EJ, Morrow DA, DeVore AD, et al; PIONEER-HF Investigators. Angiotensin-Neprilysin Inhibition in Acute Decompensated Heart Failure. N Engl J Med. 2019;380(6):539-548. DOI: 10.1056/NEJMoa1812851. PMID: 30415601", "Mebazaa A, Davison B, Chioncel O, et al. Safety, tolerability and efficacy of up-titration of guideline-directed medical therapies for acute heart failure (STRONG-HF): a multinational, open-label, randomised trial. Lancet. 2022;400(10367):1938-1952. DOI: 10.1016/S0140-6736(22)02076-1. PMID: 36356631", "2021 ESC Guidelines for the diagnosis and treatment of acute and chronic heart failure. Eur Heart J. 2021;42(36):3599-3726.", "2023 Focused Update of the 2021 ESC Guidelines for the diagnosis and treatment of acute and chronic heart failure. Eur Heart J. 2023;44(37):3627-3639. DOI: 10.1093/eurheartj/ehad195. PMID: 37622666"]
---

# Fluxograma: Manejo da Hipotensão Sintomática Limitando a Titulação de IECA/BRA/ARNI na ICFEr

Hipotensão é a razão mais comum de intolerância à titulação do bloqueio do
SRAA na ICFEr — mais frequente com sacubitril-valsartana que com enalapril no
PARADIGM-HF, sem que isso tenha exigido excesso de suspensão do fármaco. O
erro mais caro na prática não é a hipotensão em si: é **reduzir ou suspender
um pilar de sobrevida por um sintoma que, investigado, tinha outra causa**, ou
**reduzir o bloqueador do SRAA quando outro fármaco não essencial poderia ter
sido retirado primeiro**.

## Árvore de decisão

```mermaid
flowchart TD
  R0["Hipotensão sintomática (tontura,<br/>pré-síncope, síncope, fadiga com PA<br/>baixa) durante titulação de IECA, BRA<br/>ou ARNI na ICFEr"]
  D1{"PA baixa confirmada no momento do<br/>sintoma, com outras causas afastadas<br/>(hipoglicemia, arritmia, anemia,<br/>desidratação aguda)?"}
  C1(["Investigar e tratar a causa<br/>identificada (arritmia, anemia,<br/>hipoglicemia etc.); manter a dose atual<br/>do bloqueador do SRAA até a<br/>reavaliação"])
  D2{"Há sinal de hipovolemia associada<br/>(diurético em dose alta sem congestão<br/>ativa, sinais de depleção de volume)?"}
  C2(["Reduzir a dose do diurético primeiro,<br/>se não houver congestão ativa; manter a<br/>dose do bloqueador do SRAA e reavaliar<br/>a PA em poucos dias"])
  D3{"Outro fármaco não essencial para a<br/>terapia quádrupla está contribuindo<br/>(nitrato, bloqueador de canal de<br/>cálcio, alfabloqueador)?"}
  C3(["Suspender ou reduzir o fármaco não<br/>essencial primeiro; manter a titulação<br/>planejada do bloqueador do SRAA"])
  D4{"PA sistólica persistentemente muito<br/>baixa ou sintoma grave (síncope,<br/>hipoperfusão)?"}
  C4(["Reduzir a dose do bloqueador do SRAA<br/>para o último nível tolerado; não<br/>escalar nesta consulta; priorizar a<br/>titulação de iSGLT2 e antagonista<br/>mineralocorticoide, que têm menor<br/>efeito hipotensor imediato"])
  D5{"Já está em ARNI (sacubitril-<br/>valsartana) ou ainda em IECA/BRA<br/>isolado?"}
  C5(["Manter a dose atual do ARNI —<br/>hipotensão é mais frequente que com<br/>enalapril, mas raramente exige<br/>suspensão (PARADIGM-HF); espaçar a<br/>titulação das demais classes e<br/>reavaliar PA em 1 a 2 semanas"])
  C6(["Manter a dose atual de IECA/BRA sem<br/>escalar nesta consulta; priorizar a<br/>titulação de iSGLT2 e antagonista<br/>mineralocorticoide enquanto a PA se<br/>estabiliza"])

  R0 --> D1
  D1 -->|"Não — outra causa identificada"| C1
  D1 -->|"Sim — hipotensão confirmada, sem<br/>outra causa"| D2
  D2 -->|"Sim"| C2
  D2 -->|"Não"| D3
  D3 -->|"Sim"| C3
  D3 -->|"Não"| D4
  D4 -->|"Sim — grave ou persistente"| C4
  D4 -->|"Não — leve/assintomática entre<br/>doses"| D5
  D5 -->|"Já em ARNI"| C5
  D5 -->|"Ainda em IECA/BRA isolado"| C6

  classDef conduta fill:#eef6ef,stroke:#2f7a4f,color:#12301f;
  class C1,C2,C3,C4,C5,C6 conduta;
```

## O que a árvore não mostra

**Não há corte numérico único e validado** de PA sistólica que defina
"persistentemente muito baixa" na titulação de GDMT — as fontes revisadas não
oferecem esse número, e a decisão em D4 é clínica (sintoma, tolerância
funcional, tendência), não um limiar fixo.

**Início da terapia após iniciação recente na internação** (PIONEER-HF) tem
perfil de segurança próprio, sem diferença significativa de hipotensão
sintomática frente ao enalapril nesse cenário específico — cenário distinto do
paciente ambulatorial em titulação crônica, que é o foco desta árvore. Ver
`sacubitril-valsartana-iniciada-na-internacao-o-ensaio-pioneer-hf.md` para a
hipotensão na iniciação hospitalar.

**Manejo de hipercalemia concomitante** não é o objeto deste fluxograma — ver
`hipercalemia-como-barreira-ao-bloqueio-do-sraa-o-ensaio-diamond-com-patiromer.md`
nesta pasta.

**Medida não farmacológica** (elevação da cabeceira, meias de compressão,
hidratação oral quando não há congestão) é parte do cuidado geral do paciente
com hipotensão ortostática e não aparece como ramo próprio — é conduta
complementar em qualquer ponto da árvore, não uma decisão que altera o
próximo passo farmacológico.