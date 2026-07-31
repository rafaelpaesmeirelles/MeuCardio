---
title: "Monitoramento Remoto na Insuficiência Cardíaca: o Ensaio TIM-HF2"
slug: monitoramento-remoto-na-insuficiencia-cardiaca-o-ensaio-tim-hf2
theme: "Insuficiência cardíaca"
kind: estudo
review_status: revisado
source_refs: ["Koehler F, Koehler K, Deckwart O, Prescher S, Wegscheider K, Kirwan BA, et al; TIM-HF2 Investigators. Efficacy of telemedical interventional management in patients with heart failure (TIM-HF2): a randomised, controlled, parallel-group, unmasked trial. Lancet. 2018;392(10152):1047-1057. DOI: 10.1016/S0140-6736(18)31880-4. PMID: 30153985 — NCT01878630, 1.571 pacientes randomizados na Alemanha"]
legacy_source: "Documento novo, escrito em 31/07/2026. A biblioteca tinha a monitorização hemodinâmica IMPLANTÁVEL (CHAMPION e GUIDE-HF, em Dispositivos), que exige procedimento, mas nada sobre o monitoramento remoto não invasivo — que é o que a maioria dos serviços consegue montar, e que a Corvia, sendo plataforma digital, tem interesse direto em entender."
---

# Monitoramento Remoto na Insuficiência Cardíaca: o Ensaio TIM-HF2

## A ideia
Acompanhar à distância sinais de descompensação — peso, pressão, frequência, sintomas — permitiria **agir antes da manifestação completa** da piora, evitando internação. A ideia é antiga e os ensaios anteriores foram inconsistentes. O TIM-HF2 é o que melhor a testou, e o desenho explica por quê: **a população foi definida com cuidado**, o que ensaios anteriores não fizeram.

## Desenho
Koehler F et al., Lancet. 2018;392(10152):1047-1057 (PMID 30153985). Prospectivo, randomizado, controlado, grupos paralelos, **sem cegamento** (com ocultação da alocação), multicêntrico, na Alemanha:
- Elegíveis: insuficiência cardíaca em **classe NYHA II ou III**, **internação por IC nos 12 meses anteriores**, e **fração de ejeção de 45% ou menos** — ou acima de 45% desde que em uso de diurético oral
- **Pacientes com depressão maior foram excluídos**
- **Monitoramento remoto + cuidado habitual** vs. **cuidado habitual isolado**, com seguimento de até **393 dias**
- **1.571 randomizados** (796 e 775); análise completa com 765 e 773
- **Desfecho primário: percentual de dias perdidos por internação cardiovascular não planejada ou morte por qualquer causa**

**O desfecho primário merece atenção**: não é "número de internações", é **percentual de dias perdidos** — uma medida que combina frequência e duração dos eventos, e que penaliza tanto internar muito quanto internar por muito tempo.

## Resultados
- **Dias perdidos: 4,88% (IC95% 4,55-5,23) com monitoramento remoto vs. 6,64% (6,19-7,13) no cuidado habitual** — razão **0,80** (IC95% 0,65-1,00; **p=0,0460**)
- Em números do dia a dia: **17,8 dias perdidos por ano** (IC95% 16,6-19,1) com monitoramento vs. **24,2 dias por ano** (22,6-26,0) no cuidado habitual — **cerca de 6 dias a menos por ano**
- **Mortalidade por qualquer causa: 7,86 por 100 pessoas-ano** (IC95% 6,14-10,10) vs. **11,34** (9,21-13,95) — HR **0,70** (IC95% 0,50-0,96; **p=0,0280**)
- **Mortalidade cardiovascular: sem diferença significativa** — HR 0,671 (IC95% 0,45-1,01; p=0,0560)

**Interpretação dos autores:** uma intervenção **estruturada** de monitoramento remoto, **numa população de insuficiência cardíaca bem definida**, pode reduzir o percentual de dias perdidos por internação cardiovascular não planejada e a mortalidade por qualquer causa.

## Onde estao os limites, e eles importam
- **O p do desfecho primário é 0,0460 e o IC95% da razão vai até 1,00** — o resultado é positivo, mas por margem estreita
- **Ensaio sem cegamento**, com desfechos que envolvem decisão de internar — vulnerabilidade conhecida desse tipo de intervenção
- **A população foi cuidadosamente selecionada**: internação por IC no último ano (ou seja, risco alto e recente) e **exclusão de depressão maior**. Essa exclusão não é detalhe — depressão afeta adesão a automonitorização, e retirá-la seleciona quem consegue operar o sistema
- **A intervenção era estruturada**, com equipe dedicada respondendo aos alertas. **Não é o mesmo que fornecer um aparelho ao paciente**: o que foi testado é um serviço, não um dispositivo
- **Contexto alemão**, com estrutura de atenção e distâncias próprias

## Como isso conversa com o resto da biblioteca
A monitorização **hemodinâmica implantável** (sensor de pressão de artéria pulmonar) é outra abordagem para o mesmo problema, com evidência própria — ver `monitorizacao-hemodinamica-pulmonar-implantavel-champion-e-guide-hf.md`, em Dispositivos. A diferença prática: aquela exige procedimento invasivo e mede pressão; esta usa dados não invasivos e depende de uma equipe que responda.

## O que isso significa para um serviço que queira montar o modelo
- **O que reduziu desfecho foi um serviço estruturado**, com resposta clínica aos alertas — não a coleta de dados em si
- **A seleção do paciente é parte do resultado**: internação recente por IC define quem tem risco a reduzir
- **Medir o desfecho certo importa**: "dias perdidos" captura o que o paciente sente melhor que contagem de internações
- **O ganho de mortalidade total (HR 0,70) é maior que o de mortalidade cardiovascular**, que não atingiu significância — coerente com um efeito que passa por cuidado geral e não apenas por evitar descompensação

## Armadilhas clinicas
- **Prometer o resultado do TIM-HF2 entregando apenas um aparelho** — o que foi testado é um serviço com equipe respondendo
- **Aplicar a qualquer paciente com IC** — a população tinha internação por IC no último ano e NYHA II-III
- **Ignorar a exclusão de depressão maior** ao estimar quem se beneficia na prática real
- **Tratar o resultado como robusto** — p=0,0460 no primário, com IC até 1,00
- **Citar redução de mortalidade cardiovascular** — essa não atingiu significância (p=0,0560); o que caiu foi mortalidade total
- **Confundir com monitorização hemodinâmica implantável** — são abordagens diferentes, com evidência e custo diferentes
