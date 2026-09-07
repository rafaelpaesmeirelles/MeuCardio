---
title: "Sinalizadores ambulatoriais de bradicardia e bloqueio AV: quando escalar"
slug: sinalizadores-ambulatoriais-de-bradicardia-e-bloqueio-av-quando-escalar
theme: "Arritmias"
kind: protocolo
fonte_producao: grok
summary: "Bradicardia ou bloqueio AV no consultório: quais sinais pedem PS agora, quais permitem via eletiva de marca-passo definitivo e como não confundir com bradicardia fisiológica do atleta ou efeito farmacológico reversível."
review_status: pendente_revisao
review_note: "Lacuna ambulatorial além de TVNS (#839) e SVT/WPW (#864); além do fluxograma agudo ACLS já revisado. Anti-colisão: evita #835 (eletrodo/choque CDI), #859 (síncope pós-avaliação), #838/#860 farmacologia. Fontes: ESC 2021 pacing PMID 34455430; ACC/AHA/HRS 2018 bradycardia PMID 30586772. Sem doses."
source_refs:
  - "Glikson M, Nielsen JC, Kronborg MB, et al. 2021 ESC Guidelines on cardiac pacing and cardiac resynchronization therapy. Eur Heart J. 2021;42(35):3427-3520. DOI: 10.1093/eurheartj/ehab364. PMID: 34455430"
  - "Kusumoto FM, Schoenfeld MH, Barrett C, et al. 2018 ACC/AHA/HRS Guideline on the Evaluation and Management of Patients With Bradycardia and Cardiac Conduction Delay. Circulation. 2019;140(8):e382-e482. DOI: 10.1161/CIR.0000000000000628. PMID: 30586772"
---

# Sinalizadores ambulatoriais de bradicardia e bloqueio AV: quando escalar

Pergunta de **consultório**: diante de bradicardia sinusal, pausas, doença do nó sinusal ou bloqueio atrioventricular no ECG/Holter, **quando mandar ao PS agora** e quando completar avaliação **eletiva** para marca-passo definitivo?

Não substitui:
- manejo agudo da bradicardia instável — [`fluxograma-bradicardia-sintomatica-manejo-agudo`](fluxograma-bradicardia-sintomatica-manejo-agudo.md);
- indicação operacional de marca-passo (ESC 2021) — [`fluxograma-bradiarritmia-indicacao-de-marcapasso-esc-2021`](../Dispositivos/fluxograma-bradiarritmia-indicacao-de-marcapasso-esc-2021.md);
- bifascicular no consultório — [`bloqueio-bifascicular-no-consultorio-sinais-vermelhos-quando-escalar`](bloqueio-bifascicular-no-consultorio-sinais-vermelhos-quando-escalar.md);
- árvore irmã — [`fluxograma-sinalizadores-ambulatoriais-bradicardia-e-bloqueio-av`](fluxograma-sinalizadores-ambulatoriais-bradicardia-e-bloqueio-av.md);
- disfunção de eletrodo / choque CDI — PR #835 (tema Dispositivos).

## Princípio

**Frequência isolada não decide destino.** O que decide é **sintoma atribuível**, **nível do bloqueio**, **evidência de escape precário** e **reversibilidade** (fármaco, eletrólito, isquemia, hipertonia vagal).

- ESC 2021 (PMID 34455430): marca-passo permanente quando bradicardia/bloqueio é **sintomático e persistente**, ou quando há bloqueio AV de alto grau / 3º grau com risco de progressão — mesmo em alguns assintomáticos selecionados.
- ACC/AHA/HRS 2018 (PMID 30586772): correlacionar sintoma com bradiarritmia documentada; tratar causas reversíveis; não implantar por bradicardia fisiológica (sono, atleta treinado) sem sintoma.

## Sinalizadores → PS agora

| Domínio | Sinalizador |
|---|---|
| Hemodinâmico / neurológico | Síncope, pré-síncope grave, confusão nova, hipotensão sintomática, choque, dor torácica isquêmica, edema agudo |
| Elétrico de alto risco | BAV 2º grau Mobitz II, BAV 2:1 com QRS largo / suspeita infra-His, BAV 3º grau, pausas longas com escape lento ou ausente |
| Escape precário | Escape ventricular amplo e lento, escapes instáveis, pausas com recuperação ruim |
| Isquemia / tóxico | SCA suspeita + bradiarritmia; hipercalemia clínica; intoxicação (betabloqueador, BCC, digoxina) com repercussão |
| Pós-evento | Parada recuperada, necessidade recente de estimulação temporária, síncope recorrente nas últimas horas |

**Conduta no consultório:** não “esperar o Holter de retorno” se há linha da tabela. Documentar ECG de 12 derivações, monitorizar se seguro até o transporte, encaminhar ao PS. Manejo medicamentoso/estimulação aguda = fluxo ACLS — **sem doses neste protocolo**.

## Sem sinalizador de alarme → via eletiva

1. **Confirmar o mecanismo** (sinusal vs. nó vs. AV; pausas vs. BAV) com ECG e, se pontual, Holter/monitor de eventos.
2. **Correlacionar sintoma ↔ bradiarritmia** (diário de sintomas + traçado) — ESC 2021 / ACC/AHA/HRS 2018.
3. **Reversíveis óbvios:** revisar betabloqueador/BCC/digoxina/ivabradina/antiarrítmicos; eletrólitos; tireoide se contexto; isquemia conforme perfil — sem atrasar o PS se já há alarme.
4. **Ecocardiograma** se cardiopatia estrutural suspeita, IC ou dúvida de FEVE (afeta estratégia de dispositivo).
5. Encaminhar à **eletrofisiologia / dispositivos eletiva** se: bradicardia sintomática documentada persistente, doença do nó sinusal sintomática, BAV avançado intermitente sem instabilidade atual, ou dúvida de indicação Classe I/IIa.
6. Atleta / sono / vagotonia: ver [`bradicardia-sinusal-do-atleta-versus-doenca-do-no-sinusal-criterios-de-diferenciacao`](bradicardia-sinusal-do-atleta-versus-doenca-do-no-sinusal-criterios-de-diferenciacao.md) — não rotular como “indicação de MP” só pela FC de repouso.

## Checklist de 90 segundos

1. Síncope, instabilidade ou BAV avançado / escape precário? → **PS agora**.
2. Sintoma leve + bradicardia documentada sem alarme elétrico? → **via eletiva** (correlacionar + causa reversível + EP/dispositivos).
3. Assintomático + FC baixa no sono/atleta + ECG sem BAV avançado? → **não escalar**; educar alarmes.
4. Bifascicular + síncope? → protocolo irmão de bifascicular (não “só observar”).

## Armadilhas

- Liberar Mobitz II / BAV total “porque o paciente está falando agora”.
- Implantar mentalmente marca-passo por FC <50 sem sintoma nem documentação.
- Ignorar fármacos/eletrólitos e chamar tudo de “degenerativo”.
- Confundir com disfunção de eletrodo já implantado (#835).
- Inventar doses de atropina/cronotrópicos neste documento ambulatorial.

## Limite da evidência

ESC 2021 e ACC/AHA/HRS 2018 definem **indicação e correlação sintoma-traçado**, não um limiar único de “batimentos por minuto no consultório” que separe sempre PS de eletivo. A decisão combina sintoma, morfologia do bloqueio e reversibilidade.
