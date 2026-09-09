---
kind: documento
published: true
review_note: 'VANISH2 PMID 39555820 e protocolo NCT02830360: resultados e critérios
  individuais conferidos; corrigida comparação de segurança com janelas diferentes
  e ordem indevida de implante antes de intervenção urgente. CDI/RC: ESC 2026; DANISH
  PMID incorreto 27557360 corrigido para 27571011, seguimento 41123523 incorporado.
  Critérios completos e limites primária/secundária explicitados. Mental ESC 2025
  conforme números confirmados, sem transformar associação em indicação de desativação.'
review_status: revisado
slug: vanish2-nao-dispensa-o-cdi
source_refs:
- Sapp JL, Tang ASL, Parkash R, Stevenson WG, Healey JS, et al.; VANISH2 Study Team.
  Catheter Ablation or Antiarrhythmic Drugs for Ventricular Tachycardia. N Engl J
  Med. 2025;392:737-747. DOI 10.1056/NEJMoa2409501. PMID 39555820. NCT02830360.
- Køber L, et al. Defibrillator Implantation in Patients with Nonischemic Systolic
  Heart Failure (DANISH). N Engl J Med. 2016. PMID 27571011.
- McDonagh TA, et al. 2026 ESC Guidelines for the diagnosis and treatment of acute
  and chronic heart failure. Eur Heart J. 2026. DOI 10.1093/eurheartj/ehag100. PMID
  42661420.
- VANISH2 protocol NCT02830360. https://clinicaltrials.gov/study/NCT02830360
theme: Dispositivos
title: VANISH2 não dispensa o CDI
---

# VANISH2 não dispensa o CDI

A frase que esta porta recusa: “fez ablação de TV, então o desfibrilador sobra.” O VANISH2 (Sapp, *N Engl J Med*. 2025;392:737-747; PMID **39555820**; NCT02830360) comparou **estratégia inicial** de ablação versus antiarrítmico (sotalol ou amiodarona) na TV isquêmica **clinicamente significativa**. **Todos** os **416** pacientes já tinham CDI. Ablação não foi testada como substituto do gerador. Números do composto e risco procedimental moram em `vanish2-ablacao-versus-antiarrhythmico-na-tv-pos-iam` (theme Arritmias). Aqui a pergunta é de **dispositivo**.

## O palco do ensaio já tinha gerador

Infarto prévio, cardiomiopatia isquêmica e TV definida como tempestade, choque apropriado ou ATP apropriada, ou TV sustentada interrompida por emergência. Ablação em até **14 dias** após a randomização (**203**) versus fármaco (**213**). Seguimento mediano **4,3** anos.

O primário é um **composto**: morte por qualquer causa **ou**, depois de 14 dias, tempestade de TV, choque apropriado de CDI ou TV sustentada tratada por intervenção médica.

- Ablação: **103/203 (50,7%)**
- Fármaco: **129/213 (60,6%)**
- HR **0,75**; IC95% **0,58–0,97**; P=**0,03**

Choque apropriado de CDI **entra** no composto. Sem desfibrilador no peito, esse componente não existe da forma que o ensaio mediu. Ganhar o conjunto **não** autoriza a frase “ablação reduz mortalidade” e **não** autoriza “então tira o CDI”. O abstract primário não entrega o componente morte como vencedor isolado. Sem NNT inventado.

## O que o VANISH2 não move na indicação de CDI

Esta ficha **não** inventa classe de CDI. A indicação de prevenção primária na IC contemporânea continua na porta `quando-nao-indicar-cdi-de-prevencao-primaria-na-ic-contemporanea`: na ESC 2026 de IC (PMID **42661420**) o CDI de prevenção primária permanece **I B1** no fenótipo isquêmico e **IIa B1** no não isquêmico. DANISH (PMID **27571011**) não apagou o gerador. Não houve rebaixamento para classe III. Não copie essas classes para a TV isquêmica do VANISH2 como se o ensaio as tivesse reescrito.

Prevenção **secundária** (TV/FV recuperada, síncope arrítmica documentada) é **outra** porta — não sai do VANISH2 e não sai desta ficha. O VANISH2 entrou com gerador já implantado; não randomizou “ablação sem CDI” versus “CDI”. Quem ainda **não** tem CDI e tem TV isquêmica clinicamente significativa **não** herda a frase “o VANISH2 mostrou que ablação basta”. A árvore `fluxograma-tv-isquemica-estrategia-inicial-vanish2` já fecha esse nó: se o CDI não está implantado, não pular o desfibrilador se ele estiver indicado.

Não extrapolar para TV não isquêmica, canalopatia, extra-sístole ou “TV no Holter” sem o critério do ensaio. Não misturar com o VANISH de 2016 (ablação **após** falha de antiarrítmico).

## A conversa na clínica de dispositivo

Ablação, eventos em 30 dias: morte em **2 (1,0%)** e não fatais em **23 (11,3%)**. Braço fármaco: morte por toxicidade pulmonar em **1 (0,5%)** e não fatais em **46 (21,6%)**. Os dois caminhos têm dano. Nenhum dos dois substitui o gerador.

Na interrogação: o choque apropriado é evento do composto, não prova de que o CDI “falhou e sobra”. Encaminhar reabilitação na alta do implante continua na porta do hub. Desligar o CDI no fim de vida é conversa **separada** (`desligar-cdi-e-reabilitacao-duas-conversas-que-se-cruzam`) — não se abre com o HR 0,75.

## Tudo com Tudo

- **Dispositivos:** esta porta = ablação de TV isquêmica **não** dispensa o CDI. VANISH2 entrou com gerador em todos.
- **Arritmias:** números e o que o composto não é = `vanish2-ablacao-versus-antiarrhythmico-na-tv-pos-iam`. Árvore = `fluxograma-tv-isquemica-estrategia-inicial-vanish2`. Trilha = `trilha-tv-isquemica-vanish2-e-dispositivo`.
- **Insuficiência cardíaca:** prevenção primária de CDI (I B1 isquêmico; IIa B1 não isquêmico na ESC 2026) = `quando-nao-indicar-cdi-de-prevencao-primaria-na-ic-contemporanea`. Não reescrever essa tabela aqui.
- **Doença coronariana:** o recorte é IAM prévio.
- **Comunicação clínica:** “o ensaio comparou ablação com amiodarona/sotalol em quem **já** tinha CDI; não testou tirar o desfibrilador.” Ver `como-explicar-ablacao-de-tv-em-vez-de-so-amiodarona`.
- **Reabilitação cardíaca:** choque e tempestade atrasam a volta; ablação não dispensa o encaminhamento.

## Limite editorial

PMID **39555820**, NCT02830360, abstract PubMed/NEJM primário. Primário = composto. Vedado promover “ablação no lugar do CDI”. **Nenhuma classe de CDI inventada** a partir do VANISH2. Classes I B1 / IIa B1 saem da ESC 2026 de IC (PMID 42661420) na porta de prevenção primária — não desta.

## Seleção e leitura da segurança

O registro NCT02830360 especifica eventos nos seis meses anteriores sem antiarrítmico de classe I/III: TV monomórfica sustentada tratada, pelo menos um choque apropriado, três episódios em 24 horas, ou ATP em pelo menos três episódios com um sintomático ou cinco episódios independentemente de sintomas. Excluiu isquemia ativa/causa reversível, SCA recente, ablação prévia de TV e arritmia de apresentação polimórfica/FV. Instabilidade e tempestade ativa exigem estabilização imediata; o ensaio não define uma ordem obrigatória de implante antes de ablação urgente.

As taxas de segurança da ablação se referem aos 30 dias após o procedimento, enquanto as farmacológicas são eventos atribuídos ao antiarrítmico durante o acompanhamento. Não representam duas janelas temporais idênticas e não devem ser comparadas como se fossem.
