---
title: "Fluxograma ambulatorial: hipertensão por VEGF/TKI — PS agora vs. pausa vs. retorno precoce"
slug: fluxograma-ambulatorial-hipertensao-por-vegf-tki-destino
theme: "Cardio-oncologia"
kind: fluxograma
fonte_producao: grok
summary: "Árvore ambulatorial sob anti-VEGF/VEGF-TKI: gate de alarme (lesão aguda/PRES), braço PA grave com pausa temporária da terapia oncológica, e braço de intensificação oral com retorno precoce — complemento ao fluxograma de crise hipertensiva por TKI."
review_status: pendente_revisao
review_note: "Irmão do protocolo sinalizadores-ambulatoriais-hipertensao-por-vegf-tki-quando-encaminhar (07/09/2026). ESC 2022 PMID 36017568; Maitland PMID 20351338; Steingart PMID 22305831; Hamnvik PMID 25236375. Sem doses; anti-colisão com #834/#869 e crise TKI."
source_refs:
  - "Lyon AR, López-Fernández T, Couch LS, et al. 2022 ESC Guidelines on cardio-oncology developed in collaboration with the European Hematology Association (EHA), the European Society for Therapeutic Radiology and Oncology (ESTRO) and the International Cardio-Oncology Society (IC-OS). Eur Heart J. 2022;43(41):4229-4361. DOI: 10.1093/eurheartj/ehac244. PMID: 36017568"
  - "Maitland ML, Bakris GL, Black HR, et al. Initial Assessment, Surveillance, and Management of Blood Pressure in Patients Receiving Vascular Endothelial Growth Factor Signaling Pathway Inhibitors. J Natl Cancer Inst. 2010;102(9):596-604. DOI: 10.1093/jnci/djq091. PMID: 20351338"
  - "Steingart RM, Bakris GL, Chen HX, et al. Management of cardiac toxicity in patients receiving vascular endothelial growth factor signaling pathway inhibitors. Am Heart J. 2012;163(2):156-163. DOI: 10.1016/j.ahj.2011.10.018. PMID: 22305831"
  - "Hamnvik OP, Choueiri TK, Turchin A, et al. Clinical risk factors for the development of hypertension in patients treated with inhibitors of the VEGF signaling pathway. Cancer. 2015;121(2):311-319. DOI: 10.1002/cncr.28972. PMID: 25236375"
---

# Fluxograma ambulatorial: hipertensão por VEGF/TKI — destino

Prosa: [`sinalizadores-ambulatoriais-hipertensao-por-vegf-tki-quando-encaminhar`](sinalizadores-ambulatoriais-hipertensao-por-vegf-tki-quando-encaminhar.md). Checklist: [`hipertensao-por-vegf-tki-checklist-ambulatorial-de-alarme`](hipertensao-por-vegf-tki-checklist-ambulatorial-de-alarme.md). Crise/TKI já revisado: [`fluxograma-hipertensao-grave-e-crise-hipertensiva-induzida-por-tki`](fluxograma-hipertensao-grave-e-crise-hipertensiva-induzida-por-tki.md).

## Árvore de decisão

```mermaid
flowchart TD
  R0["Consulta / contato ambulatorial<br/>sob bevacizumabe ou VEGF-TKI<br/>com PA elevada ou sintoma"] --> D1{"Há alarme de PS?<br/>déficit/cefaleia visual/convulsão PRES<br/>SCA, IC aguda, aórtica<br/>oligúria aguda / lesão de órgão-alvo"}

  D1 -->|"Sim ou dúvida fundamentada"| C1(["Encaminhar AGORA ao PS / emergência<br/>Pausar antiangiogênico causal<br/>Seguir crise TKI / PRES conforme quadro"])

  D1 -->|"Não"| D2{"PAS >180 ou PAD >110 mmHg?<br/>(ESC 2022: hipertensão grave sob terapia)"}

  D2 -->|"Sim"| P1["Confirmar técnica e causas transitórias<br/>Iniciar/intensificar anti-hipertensivo ORAL<br/>IECA/BRA ± DHP-CCB; evitar verapamil/diltiazem"]
  P1 --> C2(["Pausar TEMPORARIAMENTE o VEGF/TKI<br/>Retorno 24–72 h + discussão cardio-oncologia<br/>Orientação escrita de alarmes"])

  D2 -->|"Não"| D3{"PA ≥160/100 ou sintoma CV novo<br/>sem hipoperfusão?"}

  D3 -->|"Sim"| C3(["Intensificar oral (conceito ESC)<br/>MRPA/diário se disponível<br/>Retorno precoce ≤7 dias<br/>Antecipar se fragilidade"])
  D3 -->|"Não / PA controlável"| C4(["Manter vigilância (Maitland/Steingart)<br/>Meta tipicamente <140/90<br/>Reforçar adesão e alarmes"])

  C2 --> D4{"Acesso e suporte garantidos?"}
  D4 -->|"Não / piora / sintoma de alarme"| C5(["Antecipar retorno 24 h ou PS<br/>se surgir alarme da tabela"])
  D4 -->|"Sim"| C6(["Manter pausa + retorno 24–72 h<br/>Não reiniciar VEGF/TKI no corredor"])

  classDef conduta fill:#eef6ef,stroke:#2f7a4f,color:#12301f;
  classDef alerta fill:#fdecea,stroke:#b3261e,color:#3b0a0a;
  class C1,C5 alerta;
  class C2,C3,C4,C6 conduta;
```

## Notas

- **D1** = gate de segurança (lesão aguda / PRES — Steingart 2012; ESC 2022).
- **D2** = limiar operacional de **pausa** da terapia oncológica associada à hipertensão (ESC 2022).
- **D3** = elevação significativa controlável no ambulatório com retorno precoce (Maitland 2010).
- Não decide doses de anti-hipertensivo IV/oral nem redução percentual da dose oncológica.
