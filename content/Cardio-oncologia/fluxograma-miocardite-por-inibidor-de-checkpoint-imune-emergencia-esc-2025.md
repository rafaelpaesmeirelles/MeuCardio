---
title: "Fluxograma: miocardite por inibidor de checkpoint imune — emergência (ESC 2025)"
slug: fluxograma-miocardite-por-inibidor-de-checkpoint-imune-emergencia-esc-2025
theme: "Cardio-oncologia"
kind: fluxograma
summary: "Árvore de decisão para suspeita de miocardite por ICI com estratificação de gravidade, suspensão da imunoterapia, corticoterapia e escalada em 24–48 horas se refratária."
review_status: revisado
review_note: "Revisado em 26/08/2026 contra a tabela terapêutica de miocardite induzida por ICI da diretriz ESC 2025 de miocardite/pericardite (PMID 40878297) e a seção 6.1.3 da diretriz ESC 2022 de cardio-oncologia (PMID 36017568). Preservadas as doses distintas para apresentação grave e não grave; a resposta em 24-48 horas passou a exigir melhora clínica/hemodinâmica e de bloqueio/arritmia, além de queda de troponina. A transição após pulso grave foi explicitada como prednisona oral 1 mg/kg/dia; a segunda linha foi limitada às opções enumeradas pela ESC 2025. Pendente revisão médica independente antes de uso assistencial."
source_refs: ["Schulz-Menger J, Collini V, Gröschel J, et al. 2025 ESC Guidelines for the management of myocarditis and pericarditis. Eur Heart J. 2025;46(40):3952-4041. DOI: 10.1093/eurheartj/ehaf192. PMID: 40878297 — tabela de tratamento da miocardite induzida por ICI, doses para quadro grave/não grave e escalada em 24-48 horas.", "Lyon AR, López-Fernández T, Couch LS, et al. 2022 ESC Guidelines on cardio-oncology. Eur Heart J. 2022;43(41):4229-4361. DOI: 10.1093/eurheartj/ehac244. PMID: 36017568 — seção 6.1.3, início precoce de corticoide, critérios de resposta e vigilância clínica/ECG/troponina."]
---

# Miocardite por inibidor de checkpoint imune

```mermaid
flowchart TD
  R0["Paciente em uso recente/atual de ICI<br/>com troponina elevada, alteração nova no ECG,<br/>dispneia, síncope, arritmia ou insuficiência cardíaca"]
  P1["Suspender ICI; ECG + telemetria;<br/>troponina seriada; ecocardiograma;<br/>investigar SCA/TEP/sepse e outras causas"]
  D1{"Há apresentação grave?<br/>choque/baixo débito, edema pulmonar,<br/>TV/FV, BAV avançado ou instabilidade"}
  C1(["UTI/unidade monitorizada;<br/>tratar choque/arritmia em paralelo;<br/>metilprednisolona IV 7–14 mg/kg/dia x3 dias;<br/>não atrasar por CMR/biópsia"])
  C2(["Metilprednisolona IV 500–1000 mg/dia x3 dias;<br/>monitorização clínica, ECG e troponina;<br/>CMR quando viável"])
  D2{"Em 24–48 h há melhora clínica/hemodinâmica,<br/>resolução ou melhora de disfunção ventricular,<br/>BAV e arritmias, além de queda de troponina?"}
  C3(["Resposta ao pulso: no quadro grave, seguir<br/>com prednisona oral 1 mg/kg/dia; no não grave,<br/>transicionar para prednisona oral e iniciar taper.<br/>Manter vigilância clínica, ECG e troponina"])
  C4(["Miocardite refratária: escalar imunossupressão<br/>em centro experiente — considerar micofenolato,<br/>ATG, abatacepte ou alemtuzumabe; tratar choque,<br/>BAV e arritmias em paralelo"])

  R0 --> P1
  P1 --> D1
  D1 -->|"Sim"| C1
  D1 -->|"Não"| C2
  C1 --> D2
  C2 --> D2
  D2 -->|"Sim"| C3
  D2 -->|"Não"| C4

  classDef conduta fill:#eef6ef,stroke:#2f7a4f,color:#12301f;
  class C1,C2,C3,C4 conduta;
```

## Segurança

FEVE preservada não exclui o diagnóstico. Em miocardite por ICI, bloqueio de condução e arritmia ventricular podem ser a manifestação predominante e justificam monitorização intensiva mesmo antes de disfunção ventricular evidente.

O tratamento não deve aguardar ressonância ou biópsia quando a miocardite é
clinicamente provável. Em contrapartida, troponina isoladamente elevada, sem
sintomas, alteração nova no ECG, disfunção ventricular ou outro dado compatível,
exige investigação de causas alternativas e não confirma por si só miocardite.

A diretriz ESC 2025 enumera opções de segunda linha, mas não estabelece que uma
seja superior às demais. A escolha depende do fenótipo, das toxicidades imunes
concomitantes, de infecção, citopenias e experiência do centro; por isso o fluxo
não atribui uma ordem universal entre micofenolato, ATG, abatacepte e
alemtuzumabe.
