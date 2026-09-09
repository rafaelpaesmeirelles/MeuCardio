---
title: "Fluxograma ambulatorial: hipotensão ortostática no idoso — PS agora vs. retorno precoce"
slug: fluxograma-ambulatorial-hipotensao-ortostatica-idoso-destino
theme: "Cardiologia geriátrica"
kind: fluxograma
fonte_producao: grok
summary: "Árvore ambulatorial de destino na hipotensão ortostática do idoso: gate de alto risco ESC/ECG/trauma/isquemia para PS; braço HO sem alto risco com revisão de contexto e retorno precoce; braço HPP — sem doses."
review_status: pendente_revisao
review_note: "Irmão do protocolo sinalizadores-ambulatoriais-hipotensao-ortostatica-idoso-quando-encaminhar (07/09/2026). ESC 2018 PMID 29562304; Freeman 2011 PMID 21431947; ESC 2024 PMID 39210715. Anti-colisão com #851 e estratificação de emergência."
source_refs:
  - "Brignole M, Moya A, de Lange FJ, et al.; ESC Scientific Document Group. 2018 ESC Guidelines for the diagnosis and management of syncope. Eur Heart J. 2018;39(21):1883-1948. DOI: 10.1093/eurheartj/ehy037. PMID: 29562304"
  - "Freeman R, Wieling W, Axelrod FB, et al. Consensus statement on the definition of orthostatic hypotension, neurally mediated syncope and the postural tachycardia syndrome. Clin Auton Res. 2011;21(2):69-72. DOI: 10.1007/s10286-011-0119-5. PMID: 21431947"
  - "McEvoy JW, McCarthy CP, Bruno RM, et al. 2024 ESC Guidelines for the management of elevated blood pressure and hypertension. Eur Heart J. 2024;45(38):3912-4018. DOI: 10.1093/eurheartj/ehae178. PMID: 39210715"
---

# Fluxograma ambulatorial: hipotensão ortostática no idoso — destino

Prosa: [`sinalizadores-ambulatoriais-hipotensao-ortostatica-idoso-quando-encaminhar`](sinalizadores-ambulatoriais-hipotensao-ortostatica-idoso-quando-encaminhar.md). Quedas + fármacos: [`quedas-farmacos-cv-ortostatismo-idoso-quando-encaminhar-ambulatorial`](quedas-farmacos-cv-ortostatismo-idoso-quando-encaminhar-ambulatorial.md). Emergência: [`sincope-e-queda-no-idoso-estratificacao-de-risco-na-emergencia`](sincope-e-queda-no-idoso-estratificacao-de-risco-na-emergencia.md).

## Árvore de decisão

```mermaid
flowchart TD
  R0["Consulta ambulatorial\nidoso com tontura ao levantar /\npré-síncope / queda no ortostatismo\nou HO documentada"] --> D1{"Há alarme de PS?\nesforço ou supina / palpitações → evento\nECG de risco / BAV / pausas / isquemia\ntrauma / hipotensão persistente em decúbito\nquedas em cascata / equivalente isquêmico"}

  D1 -->|"Sim ou dúvida fundamentada"| C1(["Encaminhar AGORA ao PS\nUsar estratificação de emergência\njá publicada no tema"])

  D1 -->|"Não"| D2{"PA ortostática positiva\n(Freeman/ESC: PAS ≥20 e/ou PAD ≥10\nou PAS <90 em 3 min)?"}

  D2 -->|"Sim"| P1["Revisar volume, gatilhos e fármacos\nECG se ainda não feito\nOrientar alarmes por escrito"]
  P1 --> C2(["Retorno ambulatorial 24–72 h\n(ou ≤7 dias se isolada e suporte OK)"])

  D2 -->|"Não / equívoco"| D3{"Sintoma tipicamente\n30–90 min pós-refeição?"}

  D3 -->|"Sim"| C3(["Manter HPP no diferencial\nVer hub de hipotensão pós-prandial\nRetorno precoce; PS se surgir alarme"])
  D3 -->|"Não"| C4(["Repetir técnica de PA\nManter síncope/queda no diferencial\nNão rotular 'mecânica' só por idade"])

  C2 --> D4{"Acesso e suporte garantidos?"}
  D4 -->|"Não / fragilidade alta / nova queda"| C5(["Antecipar retorno 24 h ou PS\nse surgir alarme da tabela"])
  D4 -->|"Sim"| C6(["Manter retorno precoce\nNão protocolar doses neste fluxograma"])

  classDef conduta fill:#eef6ef,stroke:#2f7a4f,color:#12301f;
  classDef alerta fill:#fdecea,stroke:#b3261e,color:#3b0a0a;
  class C1,C5 alerta;
  class C2,C3,C4,C6 conduta;
```

## Notas

- **D1** = gate de segurança (alto risco ESC 2018 + trauma + cascata + equivalente isquêmico).
- **D2** = braço HO documentada sem alto risco → destino clínico precoce, não alta sem plano.
- **D3** = ponte para HPP (hub já em main); HO e HPP podem coexistir.
- Não decide indicação de marca-passo, Holter de longo prazo, doses nem estratégia invasiva.
