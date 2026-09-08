---
title: "Alerta remoto de CIED no ambulatório: quando ligar a clínica e quando ir ao PS"
slug: alerta-remoto-de-cied-no-ambulatorio-quando-ligar-clinica-vs-ps
theme: "Dispositivos"
kind: protocolo
fonte_producao: grok
summary: "Pacote de consultório/telefone: diante de alerta de monitoramento remoto de marca-passo, CDI ou TRC, diferencia emergência, avaliação urgente por dependência/captura, choque isolado estável e alertas assintomáticos da clínica de dispositivos."
review_status: revisado
review_note: "Revisão clínica/editorial concluída em 08/09/2026. Corrigidos os achados do review: dependência de marca-passo com perda de captura/sensing passou a exigir avaliação monitorizada urgente; choque único em paciente estável foi separado de choques recorrentes/instabilidade; links para conteúdo ainda não integrado foram substituídos por fluxos canônicos já presentes; DOT-HF foi acrescentado à proveniência. Sem doses."
source_refs:
  - "Ferrick AM, Raj SR, Deneke T, et al. 2023 HRS/EHRA/APHRS/LAHRS Expert Consensus Statement on Practical Management of the Remote Device Clinic. Europace. 2023;25(5):euad123. DOI: 10.1093/europace/euad123. PMID: 37208301"
  - "Slotwiner D, Varma N, Akar JG, et al. HRS Expert Consensus Statement on remote interrogation and monitoring for cardiovascular implantable electronic devices. Heart Rhythm. 2015;12(7):e69-e100. DOI: 10.1016/j.hrthm.2015.05.008. PMID: 25981148"
  - "Hindricks G, Taborsky M, Glikson M, et al; IN-TIME study group. Implant-based multiparameter telemonitoring of patients with heart failure (IN-TIME): a randomised controlled trial. Lancet. 2014;384(9943):583-590. DOI: 10.1016/S0140-6736(14)61176-4. PMID: 25131977"
  - "Varma N, Epstein AE, Irimpen A, Schweikert R, Love C; TRUST Investigators. Efficacy and safety of automatic remote monitoring for implantable cardioverter-defibrillator follow-up: the Lumos-T Safely Reduces Routine Office Device Follow-up (TRUST) trial. Circulation. 2010;122(4):325-332. DOI: 10.1161/CIRCULATIONAHA.110.937409. PMID: 20625110"
  - "van Veldhuisen DJ, Braunschweig F, Conraads V, et al. Intrathoracic impedance monitoring, audible patient alerts, and outcome in patients with heart failure. Circulation. 2011;124(16):1719-1726. DOI: 10.1161/CIRCULATIONAHA.111.043042. PMID: 21931078"
---

# Alerta remoto de CIED no ambulatório: quando ligar a clínica e quando ir ao PS

Complementa o ensaio já existente neste catálogo sobre telemonitoramento e desfecho ([telemonitoramento-remoto-de-cdi-e-crt-d-e-desfecho-clinico-o-ensaio-in-time](/biblioteca/telemonitoramento-remoto-de-cdi-e-crt-d-e-desfecho-clinico-o-ensaio-in-time)). Este texto é o **ponto de entrada do ambulatório / plantão telefônico**: o alerta chegou — **para onde** o paciente e o clínico vão?

Não substitui:
- investigação de choque de CDI — [fluxograma-choque-inapropriado-de-cdi-investigacao-e-manejo](/biblioteca/fluxograma-choque-inapropriado-de-cdi-investigacao-e-manejo);
- disfunção de eletrodo — [fluxograma-disfuncao-de-eletrodo-fratura-e-falha-de-isolamento-conduta](/biblioteca/fluxograma-disfuncao-de-eletrodo-fratura-e-falha-de-isolamento-conduta);
- algoritmos de alerta de IC (HeartLogic vs OptiVol) — [algoritmo-multissensor-heartlogic-multisense-e-o-contraste-com-optivol-dot-hf](/biblioteca/algoritmo-multissensor-heartlogic-multisense-e-o-contraste-com-optivol-dot-hf).

Árvore: [fluxograma-alerta-remoto-cied-destino-ambulatorial](/biblioteca/fluxograma-alerta-remoto-cied-destino-ambulatorial). Premissa educativa: [monitoramento-remoto-nao-e-servico-de-emergencia-24h](/biblioteca/monitoramento-remoto-nao-e-servico-de-emergencia-24h).

## Princípio

**Monitoramento remoto (RM) é adjunto, não substituto de emergência.** O consenso HRS/EHRA/APHRS/LAHRS 2023 (PMID 37208301) enfatiza educação do paciente: RM não é serviço de emergência 24 h; muitas clínicas **não** revisam alertas fora do horário comercial. Se há sintoma de alarme, o caminho é atendimento presencial/PS — não “esperar o telefonema do centro”.

TRUST (PMID 20625110) mostrou detecção mais rápida de eventos acionáveis com RM automático; IN-TIME (PMID 25131977) associou telemonitoramento multiparâmetro a melhor escore clínico composto. DOT-HF (PMID 21931078) é um freio contra transformar alerta de impedância isolado em intervenção automática. Nenhum desses estudos autoriza tratar o canal remoto como pronto-socorro.

## Tabela de destino (primeira passagem)

| Tipo de alerta / cenário | Destino sugerido | Por quê |
|---|---|---|
| Síncope/pré-síncope, dor torácica, dispneia aguda, instabilidade, IC descompensada ou choques/terapias de CDI repetidos em curto intervalo | **PS / emergência agora** | Sintoma ou terapia recorrente pode representar arritmia sustentada/instabilidade e não é resolvido pelo canal remoto |
| **Um choque isolado**, paciente agora assintomático e hemodinamicamente estável, sem nova terapia | **Contato urgente com clínica de dispositivos/EP no mesmo dia**; PS se houver novo choque, sintoma, instabilidade ou se não houver via segura de avaliação | Evita tratar choque único estável como equivalente a tempestade; precisa interrogação e classificação rápida |
| Alerta de integridade de eletrodo + sintoma, choque, perda de captura/sensing clinicamente efetiva | **Avaliação monitorizada urgente / PS ou centro de dispositivos** | Hardware + repercussão = risco imediato |
| **Dependente de marca-passo** + alerta compatível com perda de captura ou sensing efetivo, mesmo sem sintoma | **Avaliação monitorizada urgente no mesmo dia**; se o centro não puder avaliar imediatamente, **PS** | Dependência torna a falha de estimulação potencialmente crítica |
| Alerta de integridade/noise assintomático, sem perda de captura/sensing e sem dependência crítica | **Clínica de dispositivos no mesmo dia útil**; fora do horário, próximo dia útil com instrução explícita de PS se surgir sintoma | Alerta de hardware é prioritário, mas nem todo alerta assintomático exige PS |
| FA nova/alta carga atrial, paciente estável, sem isquemia/IC aguda | **Clínica de dispositivos/cardiologia em curto prazo** | Decisão de anticoagulação/ritmo é dirigida pelo contexto e não pelo bip isolado |
| Índice de IC/impedância/HF alert assintomático | **Clínica/IC em curto prazo** | Alerta isolado não é diagnóstico de descompensação; DOT-HF sustenta não automatizar ida ao PS/intervenção |
| Transmissão falhou/monitor offline, paciente estável | **Clínica em dias**; reforçar conectividade | Não é emergência por si só |
| Paciente assintomático ligando “porque o app apitou” sem saber o tipo | **Triagem telefônica**: identificar tipo + sintomas + dependência de marca-passo | Sem tipo e sem sintoma, esclarecer o alerta; não transformar todo aviso em PS |

## O que perguntar em 2 minutos

1. **Sintomas agora?** Síncope, pré-síncope, dor, falta de ar, confusão, hipotensão percebida.
2. **Foi terapia do CDI?** Quantos choques/ATPs e em quanto tempo?
3. **Qual alerta?** Eletrodo/impedância/noise, perda de captura/sensing, arritmia, HF index, bateria/ERI ou conectividade.
4. **Dependência de marca-passo conhecida?** Esta resposta muda a urgência quando há suspeita de falha de captura/sensing.
5. **A clínica consegue avaliar hoje?** Se a situação é potencialmente crítica e não há acesso imediato, o destino é atendimento monitorizado/PS.

## Destinos em uma frase

- **PS agora** = sintoma/instabilidade, terapias de CDI repetidas, ou falha de hardware com risco clínico imediato.
- **Avaliação monitorizada urgente** = dependência de marca-passo + suspeita de perda de captura/sensing, mesmo sem sintomas.
- **Clínica de dispositivos urgente** = choque isolado estável ou alerta de hardware prioritário sem critério de emergência.
- **Clínica em curto prazo** = FA/TVNS/HF alert assintomático ou conectividade, conforme o tipo e o contexto.

## O que o ambulatório geral não resolve sozinho

- Reprogramar discriminação/zonas de TV.
- Desligar terapias de choque.
- Decidir extração de eletrodo.
- Titular diurético só porque o índice de IC subiu, sem avaliação clínica.

## Mensagem ao paciente

O aparelho pode enviar alertas para a equipe, mas isso **não** significa vigilância humana contínua. Se houver desmaio, dor no peito, falta de ar importante, instabilidade ou choques repetidos, procure emergência. Se ocorreu **um único choque** e você está completamente bem, contate imediatamente sua clínica de dispositivos para orientação e interrogação; se houver novo choque ou qualquer sintoma, vá ao PS. Um aviso isolado no monitor, sem sintomas, deve ser classificado pela clínica conforme o tipo do alerta.

## Fontes

HRS/EHRA/APHRS/LAHRS 2023 (PMID 37208301); HRS 2015 (PMID 25981148); IN-TIME (PMID 25131977); TRUST (PMID 20625110); DOT-HF (PMID 21931078).

**TV sustentada já terminada espontaneamente ou por ATP isolada** exige contato urgente com dispositivos/EP no mesmo dia para revisar o episódio; arritmia em curso, recorrência ou sintomas mudam para emergência. **Bateria/ERI/EOL:** classificar pelo fabricante, tempo restante, dependência e eficácia das terapias. ERI isolada não é PS automático, mas EOL/depleção crítica com risco de perda de estimulação/terapia requer avaliação monitorizada imediata. Se a avaliação urgente não estiver disponível, usar PS. FA detectada exige confirmar eletrogramas/carga e avaliar risco antes de anticoagular; alerta de IC isolado não determina diurético.
