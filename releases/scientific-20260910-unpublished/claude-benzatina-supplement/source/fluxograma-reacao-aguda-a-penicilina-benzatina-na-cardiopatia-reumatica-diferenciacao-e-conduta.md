---
title: "Fluxograma: Reação Aguda à Penicilina Benzatina na Cardiopatia Reumática — Diferenciação e Conduta"
slug: fluxograma-reacao-aguda-a-penicilina-benzatina-na-cardiopatia-reumatica-diferenciacao-e-conduta
theme: "Febre reumática"
kind: fluxograma
summary: 'Pergunta desta árvore: diante de um sintoma agudo minutos após a aplicação de penicilina benzatina em paciente com
  cardiopatia reumática, o quadro é anafilaxia, vasovagal de baixo risco, ou vasovagal em paciente sem reserva cardiovascular?
  A resposta muda a conduta, inclusive se administrar adrenalina. Folhas verdes são condutas. Um pai por nó. Sem ciclo. Folhas
  em estádio.'
review_status: pendente_revisao
source_refs:
- 'Sanyahumbi A, Ali S, Benjamin IJ, Karthikeyan G, Okello E, Sable CA, Taubert K, Wyber R, Zuhlke L, Carapetis JR, Beaton AZ;
  on behalf of the American Heart Association. Penicillin Reactions in Patients With Severe Rheumatic Heart Disease: A Presidential
  Advisory From the American Heart Association. J Am Heart Assoc. 2022 Mar 1;11(5):e024517. DOI: 10.1161/JAHA.121.024517. PMID:
  35049336. PMCID: PMC9075066 — tabela de diferenciação clínica vasovagal vs. anafilaxia e tabela de boas práticas de mitigação
  de risco, texto integral conferido.'
- 'Weldegerima AH, Yadeta D, Yemane M, Wehr G, Leuner C, Berhane S, Leul A, Dukessa T, Haileamlak A. Clinical and echocardiographic
  characteristics of patients who developed adverse events following Benzathine penicillin G injection for secondary prophylaxis
  of rheumatic heart disease: a cross-sectional study from three university hospitals in Ethiopia. Cardiovasc J Afr. 2025 Oct
  27;36(4):590-600. DOI: 10.5830/CVJA-2025-080. PMID: 41718701 — nenhum dos 5 casos revisados preencheu critério de anafilaxia
  nível 1 de Brighton, usado para a ressalva sobre reavaliar critérios de anafilaxia mesmo em padrão inicialmente atípico.'
review_note: 'Árvore nova, derivada da tabela de diferenciação clínica e da tabela de boas práticas do advisory da AHA (PMID
  35049336), lido em texto integral (JATS XML via PMC) nesta sessão, não apenas por resumo. Cada critério de decisão (sinal
  respiratório/cutâneo, força do pulso carotídeo, resposta à posição supina, contexto de risco valvar/funcional) corresponde
  a um critério explicitamente listado na tabela de diferenciação do documento-fonte — nenhum critério foi inventado ou extrapolado
  além do que a fonte descreve. A ressalva sobre não administrar adrenalina empiricamente fora de critério de anafilaxia em
  paciente de risco elevado reflete o próprio texto do advisory, que descreve esse risco específico (agravamento por taquicardia
  e redução do tempo de enchimento ventricular). Nó C2 (padrão atípico) foi acrescentado para não forçar todo paciente sem
  sinal respiratório/cutâneo em uma de duas caixas quando o próprio advisory reconhece resposta inconsistente ao tratamento
  padrão de anafilaxia em vários casos relatados. Pendente de revisão médica humana antes de publicação — não usar em decisão
  assistencial sem essa revisão. Vínculos conferidos por slug e pertinência clínica.'
tags: []
source_tier: A
gaps:
- 'Esta árvore não substitui protocolo local de emergência/RCP nem determina dose de adrenalina — orienta reconhecimento e
  primeira conduta, e pressupõe equipe treinada em suporte de vida. VERIFICAÇÃO HUMANA NECESSÁRIA quanto à adequação ao protocolo
  de cada serviço antes de uso assistencial.'
published: false
---

# Fluxograma: Reação Aguda à Penicilina Benzatina na Cardiopatia Reumática — Diferenciação e Conduta

Pergunta desta árvore: **diante de um sintoma agudo, em minutos, após a aplicação de penicilina benzatina intramuscular em paciente com cardiopatia reumática, o quadro é anafilaxia, resposta vasovagal em paciente de baixo risco, ou resposta vasovagal em paciente sem reserva cardiovascular — e a conduta muda entre esses três cenários, inclusive quanto a administrar adrenalina.** Este fluxograma cobre o momento da reação em si; a escolha prévia de fármaco/via e duração da profilaxia está no [fluxograma de esquema por gravidade](/biblioteca/fluxograma-profilaxia-secundaria-febre-reumatica-duracao-e-esquema), já publicado nesta pasta. Folhas verdes são condutas. Um pai por nó. Sem ciclo. Folhas em estádio.

## Árvore de decisão

```mermaid
flowchart TD
    R0["Sintoma agudo, minutos após aplicação de<br/>penicilina G benzatina IM,<br/>em paciente com cardiopatia reumática"] --> D1{"Sinal respiratório (tosse, sibilo,<br/>rouquidão, estridor, desconforto<br/>respiratório) OU sinal cutâneo<br/>(urticária, angioedema, eritema<br/>generalizado, prurido)?"}

    D1 -->|"Sim, um ou ambos"| C1(["ANAFILAXIA até prova em contrário.<br/>Adrenalina intramuscular na coxa,<br/>dose ponderal, sem demora.<br/>Ativar suporte de emergência, O2,<br/>decúbito com pernas elevadas se tolerado,<br/>monitorização contínua.<br/>Administrar adrenalina independe<br/>da gravidade da valvopatia de base."])

    D1 -->|"Não — sem sinal<br/>respiratório nem cutâneo"| D2{"Pulso carotídeo e resposta<br/>à posição supina: pulso carotídeo<br/>PRESERVADO/forte, pele pálida-<br/>fria-úmida, e melhora ao deitar<br/>ou em Trendelenburg?"}

    D2 -->|"Não — hipotensão sustentada<br/>sem melhora ao deitar, ou pulso<br/>carotídeo fraco/ausente,<br/>ou taquicardia marcada"| C2(["Padrão atípico para vasovagal simples.<br/>Reavaliar critério de anafilaxia<br/>(pode faltar sinal respiratório/cutâneo<br/>evidente em fase inicial) e considerar<br/>outra causa de colapso.<br/>Tratar como emergência cardiovascular:<br/>suporte avançado, monitorização contínua,<br/>adrenalina SE critério de anafilaxia<br/>estiver presente."])

    D2 -->|"Sim — padrão vasovagal:<br/>melhora em decúbito, pulso<br/>carotídeo preservado"| D3{"Paciente tem valvopatia GRAVE<br/>(estenose mitral, estenose aórtica<br/>ou insuficiência aórtica graves)<br/>e/ou FE de VE &lt;50%<br/>e/ou sintomas NYHA III ou IV?"}

    D3 -->|"Não — sem nenhum<br/>desses critérios de risco elevado"| C3(["Síncope vasovagal de baixo risco.<br/>Decúbito imediato, elevar as pernas,<br/>manobra de contrapressão isométrica<br/>se tolerada (handgrip, cruzar pernas),<br/>compressa fria na face/pescoço.<br/>Observar no mínimo 30 minutos.<br/>Reserva cardiovascular preservada<br/>torna deterioração improvável."])

    D3 -->|"Sim — valvopatia grave<br/>e/ou FE&lt;50% e/ou NYHA III/IV"| C4(["Vasovagal em paciente de risco elevado<br/>para comprometimento cardiovascular.<br/>Decúbito imediato SEM manobra de<br/>contrapressão isométrica (relativamente<br/>contraindicada neste grupo).<br/>Monitorização cardíaca contínua,<br/>acesso venoso, equipe e material de<br/>RCP disponíveis.<br/>NÃO administrar adrenalina<br/>empiricamente sem critério de<br/>anafilaxia — pode agravar taquicardia<br/>e reduzir o enchimento ventricular.<br/>Após estabilizar, reavaliar via oral<br/>de profilaxia com a equipe."])

    classDef conduta fill:#eef6ef,stroke:#2f7a4f,color:#12301f;
    class C1,C2,C3,C4 conduta;
```

## Como ler cada folha

**C1 — anafilaxia até prova em contrário.** Sinal respiratório ou cutâneo, isolado ou combinado, é suficiente para tratar como anafilaxia e administrar adrenalina intramuscular sem demora. O advisório da AHA é explícito: a anafilaxia confirmada exige adrenalina **independentemente** da gravidade da valvopatia de base — o risco de não tratar anafilaxia supera o risco teórico do fármaco nesse cenário específico.

**C2 — padrão atípico, a folha que existe para não forçar uma resposta binária.** Hipotensão que não melhora em decúbito, ou pulso carotídeo fraco, ou taquicardia marcada, sem sinal respiratório/cutâneo evidente, não se encaixa perfeitamente nem no padrão vasovagal típico nem na apresentação clássica de anafilaxia. O próprio *advisory* descreve resposta inconsistente ao tratamento padrão de anafilaxia em vários casos graves relatados — por isso esta folha não descarta anafilaxia, reforça reavaliação e trata como emergência cardiovascular com adrenalina condicionada ao critério clínico, não automática.

**C3 — vasovagal de baixo risco.** Melhora em decúbito e pulso carotídeo preservado, em paciente sem valvopatia grave, disfunção sistólica relevante ou sintomas avançados de insuficiência cardíaca. Neste grupo, as manobras de contrapressão isométrica são apropriadas e têm respaldo em estudos de síncope vasovagal em outros contextos (doação de sangue, vacinação).

**C4 — vasovagal em paciente sem reserva cardiovascular, a folha mais delicada da árvore.** O padrão clínico inicial ainda é vasovagal (pulso carotídeo preservado, melhora relativa em decúbito), mas o paciente pertence ao grupo de risco elevado da estratificação do *advisory* — por isso a resposta correta não é reflexa: **evitar contrapressão isométrica** (pode ser contraindicada em estenose valvar crítica e insuficiência cardíaca) e **não administrar adrenalina empiricamente** fora de critério de anafilaxia, porque a taquicardia induzida pela adrenalina reduz o tempo de enchimento ventricular exatamente no paciente que mais depende dele (estenose mitral grave, em particular). A conduta é monitorização, suporte e, depois de estabilizado, reavaliação da via de profilaxia.

## O que a árvore não mostra

**Dose e protocolo de RCP/adrenalina não estão especificados aqui.** Esta árvore orienta reconhecimento e primeira conduta; a execução técnica (dose ponderal de adrenalina, protocolo de suporte avançado) segue o protocolo de emergência do próprio serviço, com equipe treinada — **VERIFICAÇÃO HUMANA NECESSÁRIA** quanto à adequação a cada contexto assistencial.

**A estratificação de risco (D3) deveria, idealmente, já ter acontecido antes da aplicação**, não apenas ser descoberta durante uma reação aguda — ver o [documento de segurança da profilaxia](/biblioteca/seguranca-da-penicilina-benzatina-na-cardiopatia-reumatica-grave-alergia-vasovagal-ou-comprometimento-cardiovascular) e o [fluxograma de escolha de esquema por gravidade](/biblioteca/fluxograma-profilaxia-secundaria-febre-reumatica-duracao-e-esquema), que tratam da decisão pré-injeção entre via intramuscular e oral.

**Sintomas gastrointestinais isolados (náusea, vômito) não discriminam entre os dois quadros** e, por isso, não formam um ramo próprio nesta árvore — a fonte é explícita quanto a essa limitação.

**Diagnósticos alternativos raros** (por exemplo, síndrome de Kounis — vasoespasmo coronariano mediado por reação de hipersensibilidade) podem se sobrepor ao quadro de C2 e não têm ramo dedicado nesta árvore, que se limita à diferenciação proposta pelo advisório da AHA.

## Tudo com Tudo

- [Segurança da Penicilina Benzatina na Cardiopatia Reumática Grave: Diferenciando Reação Alérgica, Resposta Vasovagal e Comprometimento Cardiovascular](/biblioteca/seguranca-da-penicilina-benzatina-na-cardiopatia-reumatica-grave-alergia-vasovagal-ou-comprometimento-cardiovascular) — Síntese clínica completa da qual esta árvore deriva, com a tabela de diferenciação e a estratificação de risco na íntegra.
- [Fluxograma: Profilaxia secundária da febre reumática — escolha do antibiótico e duração por gravidade](/biblioteca/fluxograma-profilaxia-secundaria-febre-reumatica-duracao-e-esquema) — Decisão pré-injeção entre via intramuscular e oral, que D3 nesta árvore pressupõe já ter sido considerada.
- [Fluxograma: síncope reflexa versus cardíaca — diagnóstico diferencial](/biblioteca/fluxograma-sincope-reflexa-versus-cardiaca-diagnostico-diferencial) — Mesma lógica de diferenciação por pulso e resposta postural, aplicada a síncope fora do contexto de injeção.
- [Síndrome de Kounis: síndrome coronariana aguda alérgica](/biblioteca/sindrome-de-kounis-sindrome-coronariana-aguda-alergica) — Diagnóstico diferencial a considerar na folha C2, quando o padrão não se encaixa integralmente em vasovagal nem em anafilaxia clássica.
- [Epinefrina (adrenalina)](/biblioteca/epinefrina-adrenalina) — Fármaco de C1; a folha C4 explica por que a mesma conduta pode ser prejudicial fora do critério de anafilaxia.
