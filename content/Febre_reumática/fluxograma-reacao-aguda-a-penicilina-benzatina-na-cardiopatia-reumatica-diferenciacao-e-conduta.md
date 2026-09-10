---
title: 'Fluxograma: Reação Aguda à Penicilina Benzatina na Cardiopatia Reumática — Diferenciação e Conduta'
slug: fluxograma-reacao-aguda-a-penicilina-benzatina-na-cardiopatia-reumatica-diferenciacao-e-conduta
theme: Febre reumática
kind: fluxograma
summary: Reconhecimento imediato de reação após penicilina benzatina, com avaliação de parada, anafilaxia e recuperação
  vasovagal. Anafilaxia pode ocorrer sem sinais cutâneos; suspeita clínica exige adrenalina IM sem atraso, inclusive
  em valvopatia grave. Recuperação incompleta requer suporte de emergência.
review_status: revisado
source_refs:
- Sanyahumbi A et al. J Am Heart Assoc. 2022;11:e024517. DOI 10.1161/JAHA.121.024517. PMID 35049336. https://pmc.ncbi.nlm.nih.gov/articles/PMC9075066/
- Cardona V et al. World Allergy Organization anaphylaxis guidance 2020. World Allergy Organ J. 2020;13:100472.
  DOI 10.1016/j.waojou.2020.100472. https://pmc.ncbi.nlm.nih.gov/articles/PMC7607509/
review_note: 'Fluxo clínico refeito após conferência AHA/WAO integrais: parada avaliada primeiro, urticária isolada
  não fecha anafilaxia e hipotensão sem rash pode fechá-la. Recuperação incompleta não admite espera por critérios/pele;
  adrenalina IM imediata na suspeita, inclusive em valvopatia grave. Dose/concentração e repetição conferidas WAO,
  tabela 6; observação de 30 min não estendida como regra de alta após anafilaxia. Preservados vínculos temáticos.'
tags: []
source_tier: A
gaps: []
published: true
---

# Fluxograma: Reação Aguda à Penicilina Benzatina na Cardiopatia Reumática — Diferenciação e Conduta

A prioridade é reconhecer comprometimento de via aérea, respiração e circulação. **Ausência de urticária não exclui anafilaxia; urticária isolada não a confirma.** Os padrões vasovagais da AHA 2022 auxiliam a avaliação, mas não substituem os critérios clínicos e o tratamento precoce descritos pela WAO 2020.

## Árvore de decisão

```mermaid
flowchart TD
  R0["Sintoma agudo durante ou após BPG:<br/>interromper aplicação, chamar ajuda,<br/>avaliar consciência, respiração e circulação"] --> D0{"Parada cardiorrespiratória?"}
  D0 -->|"Sim"| C0(["Iniciar RCP e usar DEA/desfibrilador;<br/>acionar suporte avançado.<br/>Seguir protocolo de parada, incluindo<br/>adrenalina quando indicada em RCP."])
  D0 -->|"Não"| D1{"Suspeita de anafilaxia?<br/>Pele/mucosa + comprometimento respiratório,<br/>circulatório ou gastrointestinal grave;<br/>OU hipotensão, broncoespasmo ou alteração<br/>laríngea após alérgeno conhecido/provável,<br/>mesmo SEM manifestação cutânea"}
  D1 -->|"Sim ou reação sugestiva em evolução"| C1(["Adrenalina IM na face anterolateral da coxa,<br/>sem demora; acionar emergência.<br/>Monitorizar, ofertar O2 quando indicado<br/>e apoiar circulação com reavaliação frequente.<br/>Valvopatia grave não é motivo para reter<br/>adrenalina IM na suspeita de anafilaxia."])
  D1 -->|"Não há suspeita clínica neste momento"| D2{"Episódio típico vasovagal,<br/>com recuperação rápida e COMPLETA<br/>da consciência e da pressão ao deitar?"}
  D2 -->|"Não, recuperação incompleta ou piora"| C2(["Não classificar como vasovagal simples.<br/>Suporte de emergência, ECG/monitorização,<br/>avaliação de anafilaxia, arritmia e outras<br/>causas de choque. Se suspeita de anafilaxia<br/>surgir, adrenalina IM imediatamente.<br/>Não esperar rash ou exame confirmatório."])
  D2 -->|"Sim"| D3{"Alto risco: EM/EA/IA graves,<br/>FEVE menor que 50% ou NYHA III/IV?"}
  D3 -->|"Não"| C3(["Manter decúbito, elevar pernas se tolerado<br/>e observar por pelo menos 30 min.<br/>Contrapressão apenas se consciente e capaz.<br/>Não indicar adrenalina para vasovagal simples;<br/>reavaliar se sintomas voltarem ou mudarem."])
  D3 -->|"Sim"| C4(["Monitorização e avaliação médica;<br/>evitar contrapressão em IC/estenose crítica.<br/>Deterioração exige suporte de emergência.<br/>Após estabilização, discutir segurança<br/>da via IM e possibilidade de profilaxia oral."])
  classDef conduta fill:#eef6ef,stroke:#2f7a4f,color:#12301f;
  class C0,C1,C2,C3,C4 conduta;
```

## Adrenalina e reconhecimento clínico

Na suspeita de anafilaxia, a dose profissional é **0,01 mg/kg IM, máximo 0,5 mg por dose**, usando solução de **1 mg/mL**, na face anterolateral da coxa. Repetir em **5–15 min** se necessário, com monitorização e suporte. A via intravenosa em bolus não é o tratamento inicial da anafilaxia e traz risco de arritmia; infusão para anafilaxia refratária exige equipe experiente e ambiente monitorizado. Na parada cardíaca, segue-se o protocolo próprio de RCP.

Os critérios auxiliam o diagnóstico, sem exigir espera por todos os sinais. Comprometimento circulatório após alérgeno altamente provável pode ser anafilaxia mesmo sem urticária ou broncoespasmo. Não aguardar confirmação de Brighton, triptase ou resposta a medidas posturais para iniciar adrenalina quando a suspeita já existe.

Urticária isolada, com respiração e circulação preservadas, requer avaliação e observação de possível evolução, mas não é automaticamente anafilaxia. Pulso carotídeo palpável e melhora parcial ao deitar também não a excluem.

## Cuidados com a posição e a observação

Manter posição segura, ajustada à respiração e ao nível de consciência; não permitir levantar ou caminhar durante instabilidade. Decúbito costuma ser adequado, mas dispneia intensa ou inconsciência exigem posicionamento e proteção de via aérea apropriados. Reposição de volume deve ser individualizada, sobretudo na cardiopatia com congestão.

Os **30 min** correspondem à observação de rotina após BPG e não a uma regra de alta após anafilaxia, choque ou reação prolongada. Esses quadros exigem observação e atendimento conforme gravidade, resposta e risco de recorrência.

A estratificação cardíaca deve ocorrer antes da aplicação. O alto risco muda a prevenção e o nível de suporte necessário; não altera a indicação de adrenalina IM quando há suspeita de anafilaxia.

## Tudo com Tudo

- [Segurança da Penicilina Benzatina na Cardiopatia Reumática Grave: Diferenciando Reação Alérgica, Resposta Vasovagal e Comprometimento Cardiovascular](/biblioteca/seguranca-da-penicilina-benzatina-na-cardiopatia-reumatica-grave-alergia-vasovagal-ou-comprometimento-cardiovascular) — Síntese clínica completa da qual esta árvore deriva, com a tabela de diferenciação e a estratificação de risco na íntegra.
- [Fluxograma: Profilaxia secundária da febre reumática — escolha do antibiótico e duração por gravidade](/biblioteca/fluxograma-profilaxia-secundaria-febre-reumatica-duracao-e-esquema) — Decisão pré-injeção entre via intramuscular e oral, que D3 nesta árvore pressupõe já ter sido considerada.
- [Fluxograma: síncope reflexa versus cardíaca — diagnóstico diferencial](/biblioteca/fluxograma-sincope-reflexa-versus-cardiaca-diagnostico-diferencial) — Amplia a avaliação de síncope fora do contexto de injeção; não substitui os critérios de anafilaxia.
- [Síndrome de Kounis: síndrome coronariana aguda alérgica](/biblioteca/sindrome-de-kounis-sindrome-coronariana-aguda-alergica) — Diagnóstico diferencial a considerar na folha C2, quando o padrão não se encaixa integralmente em vasovagal nem em anafilaxia clássica.
- [Epinefrina (adrenalina)](/biblioteca/epinefrina-adrenalina) — Tratamento de primeira linha quando há suspeita de anafilaxia, inclusive com doença valvar grave.
