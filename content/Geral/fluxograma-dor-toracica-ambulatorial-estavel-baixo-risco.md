---
title: "Fluxograma: Investigação Ambulatorial da Dor Torácica Estável de Baixo Risco"
slug: fluxograma-dor-toracica-ambulatorial-estavel-baixo-risco
theme: "Geral"
kind: fluxograma
fonte_producao: chatgpt
review_status: revisado
review_note: "Baseado na diretriz 2021 AHA/ACC/ASE/CHEST/SAEM/SCCT/SCMR para avaliação e diagnóstico de dor torácica, verificada via Europe PMC/PubMed em 26/08/2026 (título completo, autoria do comitê, DOI e PMID confirmados nas duas publicações-irmãs, JACC e Circulation; abstract estrutural — objetivo, método de busca de literatura, escopo de estratificação de risco e algoritmos diagnósticos — obtido diretamente da Europe PMC). O texto integral está pago (JACC e Circulation, isOpenAccess=N) e não foi acessado nesta sessão; por isso este fluxograma reproduz a estrutura algorítmica amplamente descrita da diretriz — triagem de sinais de alarme, caracterização da dor, probabilidade pré-teste de doença arterial coronariana obstrutiva e escolha entre teste anatômico (angiotomografia de coronárias) e teste funcional (ergométrico ou de imagem sob estresse) conforme capacidade de exercício, interpretabilidade do ECG basal e contraindicações técnicas à angiotomografia — sem citar classes de recomendação (COR/LOE) específicas por nó, já que essas graduações não puderam ser conferidas literalmente no texto integral nesta sessão. O escopo deste fluxograma é deliberadamente o paciente ambulatorial estável (não agudo/não emergencial): a via de dor torácica aguda com escore HEART já está coberta em outros documentos desta biblioteca (protocolo-de-dor-toracica-na-emergencia-escore-heart-e-tempo-porta-ecg-sbc-2025, escore-heart-dor-toracica-no-pronto-socorro), a dor torácica não cardíaca por ansiedade/pânico também (fluxograma-dor-toracica-nao-cardiaca-ansiedade-e-transtorno-de-panico), e a dor torácica por vasoespasmo induzido por cocaína também (fluxograma-dor-toracica-e-sca-por-vasoespasmo-coronariano-induzido-por-cocaina); nenhuma dessas sobreposições foi repetida aqui."
source_refs: ["Gulati M, Levy PD, Mukherjee D, et al. 2021 AHA/ACC/ASE/CHEST/SAEM/SCCT/SCMR Guideline for the Evaluation and Diagnosis of Chest Pain: A Report of the American College of Cardiology/American Heart Association Joint Committee on Clinical Practice Guidelines. J Am Coll Cardiol. 2021;78(22):e187-e285. DOI: 10.1016/j.jacc.2021.07.053. PMID: 34756653.", "Gulati M, Levy PD, Mukherjee D, et al. 2021 AHA/ACC/ASE/CHEST/SAEM/SCCT/SCMR Guideline for the Evaluation and Diagnosis of Chest Pain: A Report of the American College of Cardiology/American Heart Association Joint Committee on Clinical Practice Guidelines. Circulation. 2021;144(22):e368-e454. DOI: 10.1161/CIR.0000000000001029. PMID: 34709879.", "Gulati M, Levy PD, Mukherjee D, et al. 2021 AHA/ACC/ASE/CHEST/SAEM/SCCT/SCMR Guideline for the Evaluation and Diagnosis of Chest Pain: Executive Summary. J Am Coll Cardiol. 2021;78(22):2218-2261. DOI: 10.1016/j.jacc.2021.07.052. PMID: 34756652."]
---

# Fluxograma: Investigação Ambulatorial da Dor Torácica Estável de Baixo Risco

Este fluxograma cobre o paciente que chega ao consultório — não ao pronto-socorro — relatando dor ou desconforto torácico sem sinais de instabilidade no momento da consulta. A pergunta não é "isto é uma síndrome coronariana aguda agora?" (isso já está coberto pelos fluxos de emergência com escore HEART e pela via de vasoespasmo por cocaína desta biblioteca), mas sim: **este paciente estável precisa de teste para doença arterial coronariana obstrutiva e, se precisar, qual teste pedir primeiro?** A diretriz 2021 AHA/ACC organiza essa decisão em duas etapas que este fluxograma preserva: primeiro estimar a probabilidade pré-teste de doença coronariana obstrutiva a partir da caracterização da dor, idade, sexo e fatores de risco; depois, só para quem não é de baixo risco, escolher entre um teste anatômico (angiotomografia de coronárias) e um teste funcional (ergométrico ou de imagem sob estresse), com a escolha determinada por capacidade de exercício, interpretabilidade do ECG basal e contraindicações técnicas — não por preferência arbitrária.

## Árvore de decisão

```mermaid
flowchart TD
  R["Paciente ambulatorial relata dor ou desconforto torácico, sem instabilidade clínica no momento da consulta"] --> D1{"Há sinal de alarme para síndrome coronariana aguda em curso? dor em repouso iniciada há menos de 24 horas, dor típica prolongada por mais de 20 minutos, dispneia intensa, síncope ou instabilidade hemodinâmica"}

  D1 -->|"Sim"| C1(["Encaminhar imediatamente para serviço de emergência para avaliação de síndrome coronariana aguda; não prosseguir pela via ambulatorial"])

  D1 -->|"Não"| P2["Realizar anamnese dirigida, exame físico e ECG de repouso de 12 derivações"]
  P2 --> D2{"O ECG de repouso mostra alteração isquêmica aguda ou arritmia significativa?"}

  D2 -->|"Sim"| C2(["Encaminhar para avaliação cardiológica urgente antes de qualquer investigação ambulatorial eletiva"])

  D2 -->|"Não"| P3["Classificar a dor como anginosa típica, atípica ou não anginosa, e estimar a probabilidade pré-teste de doença arterial coronariana obstrutiva a partir de idade, sexo, fatores de risco cardiovascular e características da dor"]
  P3 --> D3{"A probabilidade pré-teste é baixa, inferior a 5 por cento, e não há fator de risco cardiovascular relevante associado?"}

  D3 -->|"Sim"| P4["Investigar e conduzir causas não cardíacas da dor torácica, como musculoesquelética, gastrointestinal ou psicogênica"]
  P4 --> C3(["Não há indicação de teste cardíaco adicional para doença arterial coronariana neste momento; orientar sinais de alarme e reavaliar se os sintomas mudarem de padrão"])

  D3 -->|"Não"| D4{"O paciente já tem diagnóstico conhecido de doença arterial coronariana obstrutiva?"}

  D4 -->|"Sim"| C4(["Conduzir como possível isquemia em doença arterial coronariana já conhecida, com avaliação direcionada a essa condição, fora do escopo deste fluxograma"])

  D4 -->|"Não"| D5{"Há contraindicação ou limitação técnica para angiotomografia de coronárias? taxa de filtração glomerular abaixo de 30 mL/min, alergia a contraste sem preparo possível, arritmia que impeça sincronização cardíaca do exame, ou obesidade que inviabilize a aquisição"}

  D5 -->|"Não"| C5(["Solicitar angiotomografia de coronárias como teste inicial, pelo alto valor preditivo negativo para excluir doença arterial coronariana obstrutiva"])

  D5 -->|"Sim"| D6{"O paciente consegue exercitar-se de forma adequada e o ECG basal é interpretável, sem bloqueio de ramo esquerdo, marca-passo, pré-excitação ou depressão do segmento ST basal maior ou igual a 1 mm?"}

  D6 -->|"Sim"| C6(["Solicitar teste ergométrico com ECG de esforço como teste funcional inicial"])

  D6 -->|"Não"| C7(["Solicitar teste de estresse com imagem — ecocardiograma de estresse farmacológico, cintilografia miocárdica de perfusão ou ressonância cardíaca sob estresse — conforme disponibilidade local"])

  classDef conduta fill:#eef6ef,stroke:#2f7a4f,color:#12301f;
  class C1,C2,C3,C4,C5,C6,C7 conduta;
```

## Lógica por trás dos nós

**Triagem de sinais de alarme primeiro (D1/D2).** A diretriz distingue explicitamente a avaliação de dor torácica aguda (predominantemente em ambiente de emergência) da avaliação de dor torácica estável (predominantemente ambulatorial). Antes de qualquer estratificação de probabilidade pré-teste, este fluxograma garante que o paciente não está, na verdade, cursando uma síndrome coronariana aguda que exige via de emergência — e não interpretação de risco em consultório.

**Probabilidade pré-teste como bifurcação central (D3).** A diretriz recomenda o uso rotineiro de estimativas de probabilidade pré-teste de doença arterial coronariana obstrutiva — a partir de idade, sexo, características da dor e fatores de risco — para orientar se e qual teste é indicado, em vez de testar todo paciente com dor torácica de forma indiscriminada. Pacientes de baixa probabilidade pré-teste e sem fatores de risco relevantes tipicamente não se beneficiam de teste adicional para doença coronariana, e a atenção deve se voltar para causas não cardíacas.

**Escolha entre teste anatômico e funcional (D4-D6).** Para quem não é de baixo risco e não tem diagnóstico prévio de doença coronariana, a diretriz posiciona a angiotomografia de coronárias como opção de primeira linha eficaz, com alto valor preditivo negativo, especialmente quando não há contraindicação técnica. Quando a angiotomografia é tecnicamente limitada — função renal reduzida, alergia a contraste, arritmia que atrapalha a sincronização do exame, ou aquisição inviável por biotipo — a escolha recai sobre teste funcional, e dentro dele, o ECG de esforço convencional é preferido quando o paciente consegue exercitar-se e o ECG basal é interpretável; caso contrário, um teste de estresse com imagem farmacológica é a alternativa.

## O que este fluxograma deliberadamente não faz

- não avalia dor torácica aguda com necessidade de decisão em minutos a horas — para isso, ver os fluxos de escore HEART desta biblioteca;
- não repete a via de dor torácica não cardíaca por ansiedade/transtorno de pânico, já coberta em outro documento;
- não repete a via de vasoespasmo coronariano induzido por cocaína, já coberta em outro documento;
- não define conduta terapêutica para doença arterial coronariana confirmada — apenas até a indicação do teste diagnóstico inicial;
- não atribui classe de recomendação (COR/LOE) a nenhum nó específico, por não ter sido possível conferir esse dado no texto integral da diretriz nesta sessão;
- não cria cutoff numérico próprio de probabilidade pré-teste além do "baixo risco, inferior a 5%" já descrito na diretriz.

## Conexões no CorVIA

- Via de emergência com escore HEART: `protocolo-de-dor-toracica-na-emergencia-escore-heart-e-tempo-porta-ecg-sbc-2025` e `escore-heart-dor-toracica-no-pronto-socorro`;
- Dor torácica não cardíaca por ansiedade/pânico: `fluxograma-dor-toracica-nao-cardiaca-ansiedade-e-transtorno-de-panico`;
- Dor torácica por vasoespasmo induzido por cocaína: `fluxograma-dor-toracica-e-sca-por-vasoespasmo-coronariano-induzido-por-cocaina`;
- Valor prognóstico do teste ergométrico: `escore-de-duke-do-teste-ergometrico-valor-prognostico-em-dor-toracica`.
