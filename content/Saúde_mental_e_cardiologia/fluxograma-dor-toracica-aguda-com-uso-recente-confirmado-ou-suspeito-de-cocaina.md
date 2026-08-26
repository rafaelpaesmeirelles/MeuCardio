---
title: "Dor torácica aguda com uso recente confirmado ou suspeito de cocaína"
slug: fluxograma-dor-toracica-aguda-com-uso-recente-confirmado-ou-suspeito-de-cocaina
theme: "Saúde mental e cardiologia"
kind: fluxograma
summary: "Árvore de decisão para não confundir uso recente de cocaína com intoxicação aguda: investigar e tratar a síndrome coronariana pelo fluxo habitual, acrescentando benzodiazepínico e vasodilatador quando há euforia, taquicardia ou hipertensão e restringindo o betabloqueador somente nesse cenário agudo."
review_status: revisado
source_refs: ["Mittleman MA, Mintzer D, Maclure M, Tofler GH, Sherwood JB, Muller JE. Triggering of myocardial infarction by cocaine. Circulation. 1999;99(21):2737-2741. PMID: 10351966 — estudo caso-cruzado em 3.946 pacientes pós-IAM; risco de início do infarto 23,7 vezes maior na primeira hora após o uso", "McCord J, Jneid H, Hollander JE, et al. Management of cocaine-associated chest pain and myocardial infarction: a scientific statement from the American Heart Association. Circulation. 2008;117(14):1897-1907. DOI: 10.1161/CIRCULATIONAHA.107.188950. PMID: 18347214 — declaração científica dedicada à apresentação aguda", "Amsterdam EA, Wenger NK, Brindis RG, et al. 2014 AHA/ACC Guideline for the Management of Patients With Non-ST-Elevation Acute Coronary Syndromes. J Am Coll Cardiol. 2014;64(24):e139-e228. DOI: 10.1016/j.jacc.2014.09.017. PMID: 25260718 — recomenda tratar a SCA associada a uso recente como as demais; a exceção é a presença de sinais de intoxicação aguda e o uso de betabloqueador sem terapia vasodilatadora coronariana", "Lo KB, Virk HUH, Lakhter V, et al. Clinical Outcomes After Treatment of Cocaine-Induced Chest Pain with Beta-Blockers: A Systematic Review and Meta-Analysis. Am J Med. 2019;132(4):505-509. DOI: 10.1016/j.amjmed.2018.11.041. PMID: 30562494 — cinco estudos observacionais, 1.447 pacientes; sem diferença significativa de infarto ou mortalidade, evidência insuficiente para revogar a cautela durante intoxicação aguda"]
review_note: "Revisão de 26/08/2026: removido o marcador de verificação humana após confronto com a diretriz primária AHA/ACC 2014, a página educacional oficial do ACC que reproduz as recomendações específicas e a metanálise de Lo et al. A antiga proibição abrangente de betabloqueador foi corrigida: a recomendação Classe III (dano), nível C, refere-se a SCA com sinais de intoxicação aguda por cocaína/metanfetamina; uso recente sem intoxicação não deve retirar o paciente do tratamento habitual da SCA. O documento agora separa esse ponto do fluxograma farmacológico de vasoespasmo e não extrapola coortes de cardiomiopatia por metanfetamina para cocaína."
---

# Dor torácica aguda com uso recente confirmado ou suspeito de cocaína

A cocaína foi associada a risco **23,7 vezes maior de início de infarto na
primeira hora** após o uso no estudo caso-cruzado de Mittleman et al. (1999).
Esse dado aumenta a suspeita, mas não substitui ECG, troponina e estratificação
clínica. A decisão que realmente muda o fluxo é distinguir **história recente de
uso** de **intoxicação aguda em curso** — euforia, taquicardia e/ou hipertensão.

## Árvore de decisão

```mermaid
flowchart TD
  R0["Dor torácica aguda e uso recente<br/>confirmado ou suspeito de cocaína"]
  P1["ECG precoce, troponina seriada,<br/>monitorização e avaliação clínica<br/>como em qualquer suspeita de SCA"]
  D1{"Há sinais de intoxicação aguda?<br/>Euforia, taquicardia e/ou hipertensão"}
  P2["Tratar hiperatividade simpática:<br/>benzodiazepínico, isolado ou associado<br/>a nitroglicerina, conforme pressão e sintomas"]
  C1["Não iniciar betabloqueador nessa fase<br/>sem terapia vasodilatadora coronariana;<br/>discutir qualquer exceção com especialista"]
  P3["Uso recente sem intoxicação aguda:<br/>não suspender o cuidado padrão de SCA<br/>apenas por causa da exposição"]
  D2{"ECG, troponina e evolução<br/>sustentam SCA ou isquemia persistente?"}
  C2(["Sim: seguir estratégia de reperfusão ou<br/>invasiva e antitrombótica do protocolo de SCA,<br/>de acordo com ECG, risco e estabilidade"])
  C3(["Não: manter observação e reavaliação seriada<br/>conforme risco; investigar vasoespasmo,<br/>aorta, embolia pulmonar, miocardite,<br/>Takotsubo e causas não cardíacas"])

  R0 --> P1 --> D1
  D1 -->|"Sim"| P2 --> C1 --> D2
  D1 -->|"Não"| P3 --> D2
  D2 -->|"Sim"| C2
  D2 -->|"Não"| C3

  classDef conduta fill:#eef6ef,stroke:#2f7a4f,color:#12301f;
  class C1,C2,C3 conduta;
```

## A regra do betabloqueador, sem generalização indevida

A diretriz AHA/ACC 2014 recomenda que o paciente com SCA e história recente de
cocaína ou metanfetamina seja tratado da mesma forma que o paciente sem essa
exposição. A exceção é a presença de **sinais de intoxicação aguda**: nesse
contexto, betabloqueador não deve ser administrado sem terapia vasodilatadora
coronariana, pelo risco de potencializar espasmo (Classe III: dano, nível C).
Benzodiazepínico, isolado ou com nitroglicerina, é opção razoável para controlar
hipertensão e taquicardia nessa fase (Classe IIa, nível C).

Isso não equivale a proibição permanente. A metanálise de Lo et al. reuniu cinco
estudos observacionais e 1.447 pacientes com dor torácica associada a cocaína e
não encontrou diferença significativa de infarto (RR 1,08; IC 95% 0,61–1,91)
ou mortalidade (RR 0,75; IC 95% 0,46–1,24) entre quem recebeu e quem não recebeu
betabloqueador. A ausência de ensaios randomizados e a mistura de pacientes com
e sem intoxicação ativa impedem usar esse resultado para revogar a cautela no
ramo agudo; ele serve para impedir a extrapolação da contraindicação para todo
uso passado, insuficiência cardíaca crônica ou alta hospitalar.

## Limites e segurança

- Troponina positiva não obriga cateterismo em todos os casos; o tempo e a via
  invasiva dependem do ECG, da estabilidade, da probabilidade de SCA e dos
  diagnósticos alternativos, como nos protocolos gerais.
- Dados de recuperação ventricular após abstinência de **metanfetamina** não
  demonstram, por si, reversibilidade de uma disfunção atribuída à cocaína.
- A janela de maior risco na primeira hora não autoriza alta imediata após ela;
  observação e exames seriados são definidos pelo risco clínico e pelo protocolo
  institucional.

## Tudo com Tudo

- [Fluxograma geral de síndrome coronariana aguda (ESC 2023)](../Doença_coronariana/fluxograma-sindrome-coronariana-aguda-esc-2023.md)
- [Diretriz de síndrome coronariana aguda (ACC/AHA 2025)](../Doença_coronariana/acc-aha-2025-diretriz-sindrome-coronariana-aguda.md)
- [Protocolo de dor torácica na emergência (SBC 2025)](../Doença_coronariana/protocolo-de-dor-toracica-na-emergencia-escore-heart-e-tempo-porta-ecg-sbc-2025.md)
- [Fluxograma farmacológico do vasoespasmo por cocaína](../Geral/fluxograma-dor-toracica-e-sca-por-vasoespasmo-coronariano-induzido-por-cocaina.md)
- [Cardiotoxicidade aguda por cocaína e arritmia por bloqueio de sódio](../Terapia_intensiva/cardiotoxicidade-aguda-por-cocaina-vasoespasmo-bloqueio-de-canal-de-sodio-e-por-que-nao-usar-betabloqueador-isolado.md)
- [Cocaína, metanfetamina, infarto e cardiomiopatia: limites de extrapolação](cocaina-e-metanfetamina-infarto-desencadeado-na-primeira-hora-e-cardiomiopatia-reversivel.md)
