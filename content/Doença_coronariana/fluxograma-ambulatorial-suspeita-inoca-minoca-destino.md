---
title: "Fluxograma ambulatorial: suspeita de INOCA/MINOCA — PS vs. via especializada"
slug: fluxograma-ambulatorial-suspeita-inoca-minoca-destino
theme: "Doença coronariana"
kind: fluxograma
fonte_producao: grok
summary: "Árvore de consultório: SCA/MINOCA agudo → PS; sintoma estável após angiografia sem obstrução → RM ou teste funcional invasivo conforme a hipótese e o acesso ao exame escolhido."
review_status: revisado
review_note: "Revisão clínica final 08/09/2026. Corrigido tema canônico, gate de sintoma de repouso, links quebrados e checagem de acesso separada para RM versus CFT."
source_refs:
  - "Mills NL, Newby LK, Zaman S et al. Fifth Universal Definition of Myocardial Infarction 2026. DOI: 10.1016/j.jacc.2026.07.025. Seções 5 e 11."
  - "Vrints C, Andreotti F, Koskinas KC, et al. 2024 ESC Guidelines for the management of chronic coronary syndromes. Eur Heart J. 2024;45(36):3415-3537. DOI: 10.1093/eurheartj/ehae177. PMID: 39210710"
  - "Byrne RA, Rossello X, Coughlan JJ, et al. 2023 ESC Guidelines for the management of acute coronary syndromes. Eur Heart J. 2023;44(38):3720-3826. DOI: 10.1093/eurheartj/ehad191. PMID: 37622654"
  - "Tamis-Holland JE, Jneid H, Reynolds HR, et al. Contemporary Diagnosis and Management of Patients With Myocardial Infarction in the Absence of Obstructive Coronary Artery Disease. Circulation. 2019;139(18):e891-e908. DOI: 10.1161/CIR.0000000000000670. PMID: 30913893"
  - "Ford TJ, Stanley B, Good R, et al. Stratified Medical Therapy Using Invasive Coronary Function Testing in Angina: The CorMicA Trial. J Am Coll Cardiol. 2018;72(23 Pt A):2841-2855. DOI: 10.1016/j.jacc.2018.09.006. PMID: 30266608"
---

# Fluxograma ambulatorial: suspeita de INOCA/MINOCA — destino

Prosa: [suspeita-ambulatorial-inoca-minoca-quando-escalar](/biblioteca/suspeita-ambulatorial-inoca-minoca-quando-escalar). Pós-angiografia: [pos-angiografia-sem-obstrucao-ambulatorial-alarme-e-encaminhamento](/biblioteca/pos-angiografia-sem-obstrucao-ambulatorial-alarme-e-encaminhamento). Diagnóstico: [anoca-inoca-angina-e-isquemia-sem-obstrucao-coronariana-esc-2024](/biblioteca/anoca-inoca-angina-e-isquemia-sem-obstrucao-coronariana-esc-2024). MINOCA: [fluxograma-minoca-investigacao-diagnostica](/biblioteca/fluxograma-minoca-investigacao-diagnostica).

```mermaid
flowchart TD
  R0["Consulta: angina/isquemia + coronárias não obstrutivas<br/>ou alta suspeita de ANOCA/INOCA"] --> D1{"SCA/MINOCA agudo?<br/>sintoma atual novo/prolongado/crescente<br/>ECG isquêmico novo · troponina dinâmica · instabilidade"}

  D1 -->|"Sim ou dúvida fundamentada"| C1(["PS AGORA<br/>Não teste ergométrico ambulatorial<br/>Não aguardar RM eletiva"])

  D1 -->|"Não"| D3{"Episódio recente de lesão miocárdica/MINOCA<br/>com etiologia ainda aberta, mesmo sem sintomas?"}

  D3 -->|"Sim"| C3(["Priorizar RM cardíaca precoce<br/>+ retorno etiológico, sem fila indefinida"])
  C3 --> A3{"RM e retorno disponíveis?"}
  A3 -->|"Sim"| C6(["Manter via dirigida"])
  A3 -->|"Não"| C7(["Articular centro/rede alternativa<br/>PS se surgir alarme"])

  D3 -->|"Não"| D2{"Sintomas persistentes / QoL comprometida<br/>apesar de tratamento apropriado?"}
  D2 -->|"Não"| C2(["Seguimento clínico e alarmes"])
  D2 -->|"Sim"| C4(["Selecionar CFT / centro ANOCA-INOCA<br/>se mecanismo incerto e sintomas persistentes"])
  C4 --> A4{"CFT/centro especializado disponível?"}
  A4 -->|"Sim"| C6
  A4 -->|"Não"| C7

  classDef alerta fill:#fdecea,stroke:#b3261e,color:#3b0a0a;
  classDef conduta fill:#eef6ef,stroke:#2f7a4f,color:#12301f;
  class C1 alerta;
  class C2,C3,C4,C6,C7 conduta;
```

## Notas

- Dor crônica/cíclica em repouso sem piora e sem alarme atual não é automaticamente SCA; pode seguir via especializada de vasoespasmo.
- Acesso deve ser checado para o **exame escolhido**: RM e CFT são ramos distintos.

- Não redefine endótipos nem farmacoterapia.

MINOCA segue a nomenclatura de lesão miocárdica com coronárias não obstrutivas da Quinta Definição Universal 2026; ver [distinção de IAM e ANOCA/INOCA](/biblioteca/suspeita-ambulatorial-inoca-minoca-quando-escalar).

CFT não é automático após angiografia normal: selecionar conforme sintomas persistentes apesar de cuidado apropriado, hipótese, testes prévios e expertise. CorMicA apoia benefício sintomático/qualidade de vida, sem comprovar redução de mortalidade/MACE. Resposta a nitrato não confirma nem exclui SCA.
