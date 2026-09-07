---
title: "Fluxograma ambulatorial: queda/síncope no idoso — PS agora vs. retorno precoce"
slug: fluxograma-ambulatorial-queda-sincope-idoso-destino
theme: "Cardiologia geriátrica"
kind: fluxograma
fonte_producao: grok
summary: "Árvore ambulatorial de destino: gate de alto risco ESC/ECG/trauma/isquemia para PS; braço ortostático e braço equívoco com retorno precoce — sem doses."
review_status: pendente_revisao
review_note: "Irmão do protocolo sinalizadores-ambulatoriais-queda-sincope-idoso-quando-encaminhar (07/09/2026). ESC 2018 PMID 29562304; AHA 2023 PMID 36503287. Anti-colisão com estratificação de emergência já em main."
source_refs:
  - "Brignole M, Moya A, de Lange FJ, et al. 2018 ESC Guidelines for the diagnosis and management of syncope. Eur Heart J. 2018;39(21):1883-1948. DOI: 10.1093/eurheartj/ehy037. PMID: 29562304"
  - "Damluji AA, Forman DE, Wang TY, et al. Management of Acute Coronary Syndrome in the Older Adult Population: A Scientific Statement From the American Heart Association. Circulation. 2023;147(3):e32-e62. DOI: 10.1161/CIR.0000000000001112. PMID: 36503287"
---

# Fluxograma ambulatorial: queda/síncope no idoso — destino

Prosa: [`sinalizadores-ambulatoriais-queda-sincope-idoso-quando-encaminhar`](sinalizadores-ambulatoriais-queda-sincope-idoso-quando-encaminhar.md). Emergência: [`sincope-e-queda-no-idoso-estratificacao-de-risco-na-emergencia`](sincope-e-queda-no-idoso-estratificacao-de-risco-na-emergencia.md).

## Árvore de decisão

```mermaid
flowchart TD
  R0["Consulta ambulatorial\nqueda inexplicada / pré-síncope / síncope\nno idoso"] --> D1{"Há alarme de PS?\nesforço ou supina / palpitações → evento\nECG de risco / BAV / pausas / isquemia\ntrauma importante / hipotensão persistente\nequivalente isquêmico (dispneia/dor/edema)"}

  D1 -->|"Sim ou dúvida fundamentada"| C1(["Encaminhar AGORA ao PS\nUsar estratificação de emergência\ne fluxograma já publicados no tema"])

  D1 -->|"Não"| D2{"PA ortostática positiva\nsem marcador de alto risco?"}

  D2 -->|"Sim"| P1["Revisar volume, gatilhos e fármacos\nECG se ainda não feito\nOrientar alarmes por escrito"]
  P1 --> C2(["Retorno ambulatorial 24–72 h\n(ou ≤7 dias se isolado e suporte OK)"])

  D2 -->|"Não / equívoco"| D3{"Episódio recente sem história clara\nou recorrência leve sem alto risco?"}

  D3 -->|"Sim"| C3(["ECG + exame focado\nManter síncope no diferencial\nRetorno 24–72 h; PS se surgir alarme"])
  D3 -->|"Não / estável baixo risco aparente"| C4(["Plano usual + educação de alarmes\nNão rotular queda mecânica só por idade"])

  C2 --> D4{"Acesso e suporte garantidos?"}
  D4 -->|"Não / fragilidade alta / novo episódio"| C5(["Antecipar retorno 24 h ou PS\nse surgir alarme da tabela"])
  D4 -->|"Sim"| C6(["Manter retorno precoce\nNão protocolar doses neste fluxograma"])

  classDef conduta fill:#eef6ef,stroke:#2f7a4f,color:#12301f;
  classDef alerta fill:#fdecea,stroke:#b3261e,color:#3b0a0a;
  class C1,C5 alerta;
  class C2,C3,C4,C6 conduta;
```

## Notas

- **D1** = gate de segurança (alto risco ESC 2018 + trauma + equivalente isquêmico AHA 2023).
- **D2** = braço ortostático sem alto risco → destino clínico precoce, não alta sem plano.
- **D3** = queda sem história clara permanece síncope no diferencial até prova em contrário.
- Não decide indicação de marca-passo, Holter de longo prazo, doses nem estratégia de SCA invasiva.
