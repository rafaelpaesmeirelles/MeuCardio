---
title: "Fluxograma: Síndrome Coronariana Aguda — do primeiro contato à reperfusão (ESC 2023)"
slug: fluxograma-sindrome-coronariana-aguda-esc-2023
theme: "Doença coronariana"
kind: fluxograma
summary: "Caminho decisório da dor torácica suspeita de SCA: ECG em 10 minutos, separação STEMI × NSTE-ACS, algoritmo 0h/1h de troponina ultrassensível e definição do tempo da estratégia invasiva."
review_status: revisado
review_note: "Revisão adversarial Codex em 08/09/2026: fibrinólise condicionada à janela e contraindicações, NSTEMI confirmado como alto risco, rule-in não confirma etiologia e rule-out não exclui angina instável. ESC 2023, Recommendation Table 4 e seções 5.1–5.3."
source_refs: ["2023 ESC Guidelines for the management of acute coronary syndromes · European Heart Journal · 2023 · 44(38):3720-3826 · 10.1093/eurheartj/ehad191", "2023 ESC Guidelines for Acute Coronary Syndromes: Key Points · American College of Cardiology · 2023 · https://www.acc.org/Latest-in-Cardiology/ten-points-to-remember/2023/08/29/14/01/2023-esc-guidelines-acs-esc-2023", "'10 commandments' for the 2023 ESC Guidelines for the management of acute coronary syndromes · European Heart Journal · 2024 · 45(14):1193-1195 · https://academic.oup.com/eurheartj/article/45/14/1193/7516285"]
---

# Fluxograma: Síndrome Coronariana Aguda (ESC 2023)

A apresentação clínica, o ECG, o tempo de sintomas, a estabilidade e as contraindicações definem a estratégia. **Angiografia imediata não significa fibrinólise para toda SCA.** Troponina elevada identifica injúria miocárdica; confirmar IAM exige integração com evidência de isquemia e avaliação da causa. As expressões STEMI/NSTEMI abaixo descrevem as vias operacionais da diretriz de SCA de 2023.

## Árvore de decisão

```mermaid
flowchart TD
  A["Suspeita de SCA: avaliar estabilidade e causas alternativas graves<br/>ECG em até 10 min do primeiro contato"] --> B{"Supra persistente de ST ou equivalente<br/>compatível com oclusão coronariana aguda?"}
  B -->|Sim| C{"ICP primária pode proporcionar reperfusão<br/>em até 120 min do diagnóstico?"}
  C -->|Sim| PCI["Ativar ICP primária e transferência imediata<br/>sem esperar troponina"]
  C -->|Não| L{"STEMI com sintomas até 12 h<br/>e sem contraindicação à fibrinólise?"}
  L -->|Sim| LY["Fibrinólise conforme protocolo por equipe habilitada<br/>e transferência imediata para centro com ICP"]
  L -->|Não| TRANS["Não administrar fibrinolítico automaticamente<br/>Transferir para estratégia invasiva; urgência conforme<br/>isquemia em curso, instabilidade e tempo de apresentação"]
  LY --> RES{"Falha de reperfusão, dor persistente,<br/>piora isquêmica ou instabilidade?"}
  RES -->|Sim| RESC["ICP de resgate"]
  RES -->|Não| ANG["Angiografia após lise bem-sucedida<br/>em 2 a 24 h, conforme protocolo"]
  B -->|Não| V{"Suspeita de NSTE-ACS com<br/>algum critério de risco muito alto?"}
  V -->|Sim| IMM["Angiografia imediata e tratamento de suporte<br/>Não administrar fibrinólise pela via NSTE-ACS"]
  V -->|Não| T["Troponina ultrassensível em algoritmo validado<br/>0 h/1 h ou 0 h/2 h, integrado à clínica e ECG"]
  T --> R{"Resultado e reavaliação clínica"}
  R -->|Rule-in| CONF["Confirmar etiologia: IAM requer isquemia<br/>Considerar injúria não isquêmica e outros mecanismos"]
  CONF --> HIGH{"NSTEMI confirmado ou outro alto risco:<br/>GRACE maior que 140, alterações dinâmicas de ST/T<br/>ou supra transitório?"}
  HIGH -->|Sim| EARLY["Estratégia invasiva durante internação<br/>Considerar precoce em menos de 24 h"]
  HIGH -->|Não| CAUSE["Definir investigação e tratamento da causa<br/>Não presumir SCA por troponina isolada"]
  R -->|Observação| OBS["Repetir troponina conforme ensaio/protocolo,<br/>reavaliar clínica e ECG; não dar alta automática"]
  R -->|Rule-out| OUT["IAM menos provável; avaliar angina instável,<br/>sintomas persistentes e outros diagnósticos graves<br/>Alta somente após avaliação clínica completa"]
  OUT -->|Forte suspeita de angina instável| UA["Avaliar estratégia invasiva durante internação<br/>Reavaliar imediatamente se surgir risco muito alto"]
```

## Como interpretar os caminhos

No STEMI, o limite de 120 minutos é a previsão do diagnóstico até a reperfusão por ICP, não uma autorização para esperar. A fibrinólise depende de início dos sintomas em até 12 horas e ausência de contraindicações; sangramento e diagnósticos alternativos, incluindo dissecção de aorta, precisam ser considerados pelo protocolo. Após 12 horas, ou quando a lise é contraindicada, priorizar a estratégia invasiva conforme apresentação. Isquemia persistente, instabilidade ou arritmia ameaçadora à vida exige resposta imediata. A via farmacoinvasiva inclui transferência sem esperar provar sucesso da lise; falha de reperfusão ou deterioração indica resgate.

Na NSTE-ACS, risco muito alto inclui choque/instabilidade, dor persistente ou recorrente refratária, insuficiência cardíaca aguda atribuível a isquemia em curso, arritmia ameaçadora à vida, complicação mecânica e alterações recorrentes dinâmicas de ST/T, especialmente supra intermitente. Esses achados justificam angiografia imediata. **Não autorizam fibrinólise.** Parada recuperada sem supra não gera, isoladamente, angiografia imediata universal em paciente estável.

**NSTEMI confirmado já é critério de alto risco**, sem exigir GRACE >140 adicional. A diretriz recomenda estratégia invasiva durante a internação em alto risco e orienta considerar a realização em menos de 24 horas; a via imediata fica reservada ao risco muito alto. Angina instável com forte suspeita clínica também exige avaliação da estratégia invasiva, mesmo com troponina negativa.

Os limiares dos algoritmos rápidos dependem do ensaio laboratorial e não são intercambiáveis. *Rule-in* não prova infarto por trombose coronariana e *rule-out* não exclui angina instável, TEP, doença aórtica ou outras emergências. Sintomas persistentes, apresentação muito precoce, mudanças no ECG ou incoerência clínica exigem reavaliação; não usar o resultado isolado para alta.

Fonte primária: [ESC 2023 — SCA, texto integral, Recommendation Table 4 e seções 5.1–5.3](https://repisalud.isciii.es/bitstream/20.500.12105/16578/1/2023%20ESC%20Guidelines_Eur%20Heart%20J_2023.pdf). O repositório institucional hospeda o artigo original; as decisões acima não transformam a classificação bioquímica em indicação automática de reperfusão.
