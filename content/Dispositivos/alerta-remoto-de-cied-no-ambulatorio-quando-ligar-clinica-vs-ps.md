---
title: "Alerta remoto de CIED no ambulatório: quando ligar a clínica e quando ir ao PS"
slug: alerta-remoto-de-cied-no-ambulatorio-quando-ligar-clinica-vs-ps
theme: "Dispositivos"
kind: protocolo
fonte_producao: grok
summary: "Pacote de consultório/telefone: diante de alerta de monitoramento remoto de marca-passo, CDI ou TRC, o que é PS agora, o que é contato com a clínica de dispositivos em horário útil, e o que o paciente não deve esperar do telemonitoramento — complementar ao ensaio IN-TIME e sem repetir pós-choque (#835) nem pré-RM (#870)."
review_status: pendente_revisao
review_note: "Lacuna além do PR #835 (eletrodo/choque) e #870 (pré-RM). Corpus já tem IN-TIME (evidência de desfecho) e HeartLogic/DOT-HF (algoritmos); falta o destino ambulatorial clínica vs PS. Fontes: HRS/EHRA/APHRS/LAHRS 2023 PMID 37208301; Slotwiner HRS 2015 PMID 25981148; IN-TIME PMID 25131977; TRUST PMID 20625110. Sem doses. Evitada infecção (densa + #711)."
source_refs:
  - "Ferrick AM, Raj SR, Deneke T, et al. 2023 HRS/EHRA/APHRS/LAHRS Expert Consensus Statement on Practical Management of the Remote Device Clinic. Europace. 2023;25(5):euad123. DOI: 10.1093/europace/euad123. PMID: 37208301"
  - "Slotwiner D, Varma N, Akar JG, et al. HRS Expert Consensus Statement on remote interrogation and monitoring for cardiovascular implantable electronic devices. Heart Rhythm. 2015;12(7):e69-e100. DOI: 10.1016/j.hrthm.2015.05.008. PMID: 25981148"
  - "Hindricks G, Taborsky M, Glikson M, et al; IN-TIME study group. Implant-based multiparameter telemonitoring of patients with heart failure (IN-TIME): a randomised controlled trial. Lancet. 2014;384(9943):583-590. DOI: 10.1016/S0140-6736(14)61176-4. PMID: 25131977"
  - "Varma N, Epstein AE, Irimpen A, Schweikert R, Love C; TRUST Investigators. Efficacy and safety of automatic remote monitoring for implantable cardioverter-defibrillator follow-up: the Lumos-T Safely Reduces Routine Office Device Follow-up (TRUST) trial. Circulation. 2010;122(4):325-332. DOI: 10.1161/CIRCULATIONAHA.110.937409. PMID: 20625110"
---

# Alerta remoto de CIED no ambulatório: quando ligar a clínica e quando ir ao PS

Complementa o ensaio já existente neste catálogo sobre telemonitoramento e desfecho ([`telemonitoramento-remoto-de-cdi-e-crt-d-e-desfecho-clinico-o-ensaio-in-time`](telemonitoramento-remoto-de-cdi-e-crt-d-e-desfecho-clinico-o-ensaio-in-time.md)). Este texto é o **ponto de entrada do ambulatório / plantão telefônico**: o alerta chegou — **para onde** o paciente e o clínico vão?

Não substitui:
- pós-choque de CDI ambulatorial — PR #835 / [`choque-do-cdi-no-ambulatorio-triagem-apropriado-versus-inapropriado-primeira-consulta`](choque-do-cdi-no-ambulatorio-triagem-apropriado-versus-inapropriado-primeira-consulta.md);
- disfunção de eletrodo — [`sinalizadores-ambulatoriais-de-disfuncao-de-eletrodo-quando-encaminhar`](sinalizadores-ambulatoriais-de-disfuncao-de-eletrodo-quando-encaminhar.md);
- pré-RM — PR #870;
- algoritmos de alerta de IC (HeartLogic vs OptiVol) — [`algoritmo-multissensor-heartlogic-multisense-e-o-contraste-com-optivol-dot-hf`](algoritmo-multissensor-heartlogic-multisense-e-o-contraste-com-optivol-dot-hf.md).

Árvore: [`fluxograma-alerta-remoto-cied-destino-ambulatorial`](fluxograma-alerta-remoto-cied-destino-ambulatorial.md). Premissa educativa: [`monitoramento-remoto-nao-e-servico-de-emergencia-24h`](monitoramento-remoto-nao-e-servico-de-emergencia-24h.md).

## Princípio

**Monitoramento remoto (RM) é adjunto, não substituto de emergência.** O consenso HRS/EHRA/APHRS/LAHRS 2023 (PMID 37208301) enfatiza educação do paciente: RM não é serviço de emergência 24 h; muitas clínicas **não** revisam alertas fora do horário comercial. Se há sintoma de alarme, o caminho é atendimento presencial/PS — não “esperar o telefonema do centro”.

TRUST (PMID 20625110) mostrou detecção mais rápida de eventos acionáveis com RM automático; IN-TIME (PMID 25131977) associou telemonitoramento multiparâmetro a melhor escore clínico composto. Nenhum dos dois ensaios autoriza tratar o canal remoto como pronto-socorro.

## Tabela de destino (primeira passagem)

| Tipo de alerta / cenário | Destino sugerido | Por quê |
|---|---|---|
| Choque sentido, ATP em salva, síncope / pré-síncope, dor torácica, dispneia aguda, ICC descompensada | **PS / emergência agora** | Clínica remota não estabiliza; cruzar com pacote pós-choque (#835) |
| Alerta de integridade de eletrodo + sintoma (ou choque) | **PS / centro urgente** | Hardware + sintoma = risco imediato (#835) |
| Alerta de integridade / noise **assintomático**, horário comercial | **Clínica de dispositivos no mesmo dia / horas** | HRS 2023: alertas de alta prioridade em dia útil; não “próxima consulta de rotina” |
| Alerta de integridade **assintomático**, fora do horário, paciente estável | **Orientar: se sintoma → PS; se estável → clínica no próximo dia útil** | RM não é plantão 24 h (PMID 37208301) |
| FA nova / alta carga atrial, paciente estável, sem isquemia | **Clínica de dispositivos / cardiologia em dias curtos** | Decisão de anticoagulação/ritmo é ambulatorial dirigida — não PS automático |
| Índice de IC / impedância / “HF alert” assintomático | **Clínica / IC em dias úteis curtos** | Ver HeartLogic/DOT-HF: alerta ≠ emergência; DOT-HF mostrou risco de excesso de visitas se o paciente for ao PS por alerta audível isolado |
| Transmissão falhou / monitor offline, paciente estável | **Clínica em dias**; reforçar conectividade | Não é PS; HRS 2015 (PMID 25981148) trata adesão/conectividade como rotina de programa |
| Paciente assintomático ligando “porque o app apitou” sem saber o tipo | **Triagem telefônica**: tipo do alerta + sintomas → tabela acima | Sem tipo + sem sintoma → clínica no próximo dia útil, não PS |

## O que perguntar em 2 minutos (telefone ou consultório)

1. **Sintomas agora?** Síncope, choque sentido, dor, falta de ar, confusão.
2. **Qual alerta?** Choque/ATP, eletrodo/impedância/noise, arritmia (FA/TV), HF index, bateria/ERI, falha de transmissão.
3. **Quantos eventos / em quanto tempo?** Cascata vs aviso único.
4. **Dependência de marca-passo conhecida?**
5. **Horário:** a clínica de dispositivos deste paciente está aberta?

## Destinos em uma frase

- **PS agora** = sintoma de alarme **ou** terapia de CDI em cascata **ou** suspeita de eletrodo sintomática.
- **Clínica de dispositivos (horário útil / próximo dia útil)** = alerta de hardware ou clínico **assintomático**, FA estável, HF alert sem descompensação, falha de transmissão.
- **Não fazer** = mandar todo bip para o PS; nem dizer “o monitoramento cuida de você à noite”.

## O que o ambulatório geral não resolve sozinho

- Reprogramar discriminação / zonas de TV.
- Desligar terapias de choque.
- Decidir extração de eletrodo.
- Titular diurético só porque o índice de IC subiu, sem avaliação clínica (DOT-HF é o freio histórico).

## Mensagem ao paciente (linguagem simples)

O aparelho avisa a equipe **quando consegue**; isso **não** substitui o pronto-socorro se você se sentir mal. Se tiver choque, desmaio, dor no peito ou falta de ar forte — vá ao PS. Se só viu um aviso no monitor e está bem — ligue para a clínica de dispositivos no horário de funcionamento.

## Fontes

Consenso prático da clínica remota HRS/EHRA/APHRS/LAHRS 2023 (PMID 37208301); HRS 2015 sobre interrogação/monitoramento remoto (PMID 25981148); IN-TIME (PMID 25131977); TRUST (PMID 20625110).
