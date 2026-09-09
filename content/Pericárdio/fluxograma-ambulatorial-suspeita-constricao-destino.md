---
title: "Fluxograma ambulatorial: suspeita de constrição pericárdica — destino"
slug: fluxograma-ambulatorial-suspeita-constricao-destino
theme: "Pericárdio"
kind: fluxograma
fonte_producao: grok
summary: "Árvore ambulatorial: alarme hemodinâmico → PS; sem alarme → eco com Doppler tecidual + referência para DD constrição×restrição — sem doses nem indicação de pericardiectomia."
review_status: pendente_revisao
review_note: "Irmão de sinalizadores-ambulatoriais-suspeita-constricao-pericardica-quando-encaminhar (07/09/2026). ESC 2025 PMID 40878297; Klein 2024 PMID 39111992; Feng 2011 PMID 21969014. Anti-colisão #846/#857 e fluxograma de DD imagem. Sem doses."
source_refs:
  - "Schulz-Menger J, Collini V, Gröschel J, Adler Y, et al. 2025 ESC Guidelines for the management of myocarditis and pericarditis. Eur Heart J. 2025;46(40):3952-4041. DOI: 10.1093/eurheartj/ehaf192. PMID: 40878297"
  - "Klein AL, Wang TKM, Cremer PC, Abbate A, Adler Y, et al. Pericardial Diseases: International Position Statement on New Concepts and Advances in Multimodality Cardiac Imaging. JACC Cardiovasc Imaging. 2024;17(8):937-988. DOI: 10.1016/j.jcmg.2024.04.010. PMID: 39111992"
  - "Feng D, Glockner J, Kim K, et al. Cardiac magnetic resonance imaging pericardial late gadolinium enhancement and elevated inflammatory markers can predict the reversibility of constrictive pericarditis after antiinflammatory medical therapy: a pilot study. Circulation. 2011;124(17):1830-1837. DOI: 10.1161/CIRCULATIONAHA.111.026070. PMID: 21969014"
---

# Fluxograma ambulatorial: suspeita de constrição — destino

Prosa: [`sinalizadores-ambulatoriais-suspeita-constricao-pericardica-quando-encaminhar`](sinalizadores-ambulatoriais-suspeita-constricao-pericardica-quando-encaminhar.md). Checklist: [`constricao-pericardica-checklist-ambulatorial-de-alarme`](constricao-pericardica-checklist-ambulatorial-de-alarme.md). DD imagem: [`fluxograma-pericardite-constritiva-versus-cardiomiopatia-restritiva`](fluxograma-pericardite-constritiva-versus-cardiomiopatia-restritiva.md).

## Árvore de decisão

```mermaid
flowchart TD
  R0["Consulta ambulatorial<br/>edema / ascite / dispneia<br/>FE preservada ou desconhecida"] --> D0{"Há pista de constrição?<br/>IC direita dominante ± Kussmaul<br/>± pericardite/TB/cirurgia/RT"}

  D0 -->|"Não"| C0(["Investigar outras causas de IC / edema<br/>Não forçar rótulo de constrição"])

  D0 -->|"Sim ou dúvida fundamentada"| D1{"Alarme de PS?<br/>hipotensão / hipoperfusão<br/>tríade de Beck / síncope<br/>dispneia em repouso / TV"}

  D1 -->|"Sim"| C1(["Encaminhar AGORA ao PS / urgência<br/>Se tamponamento: fluxograma-tamponamento-cardiaco"])

  D1 -->|"Não"| P1["Exame focado + solicitar eco<br/>com Doppler tecidual (e' medial)<br/>e desvio septal respirofásico"]
  P1 --> C2(["Retorno 24–72 h se congestão em evolução<br/>≤7 dias se estável com eco agendado<br/>Alarmes escritos"])

  C2 --> D2{"Eco sugere constrição<br/>ou padrão indeterminado?"}
  D2 -->|"Sim / dúvida"| C3(["Referência especializada<br/>Seguir fluxograma constrição×restrição<br/>RM/TC / decisão transitória vs permanente<br/>— sem doses neste fluxograma"])
  D2 -->|"Padrão de restrição miocárdica"| C4(["Investigar infiltrativa / miocárdica<br/>Não indicar pericardiectomia aqui"])
  D2 -->|"Ainda sem eco"| C5(["Manter retorno curto<br/>Antecipar PS se surgir alarme"])

  classDef conduta fill:#eef6ef,stroke:#2f7a4f,color:#12301f;
  classDef alerta fill:#fdecea,stroke:#b3261e,color:#3b0a0a;
  class C1 alerta;
  class C0,C2,C3,C4,C5 conduta;
```

## Notas

- **D0** = filtro de suspeita clínica (pré-teste), não diagnóstico.
- **D1** = gate de segurança (tamponamento / choque / síncope).
- **D2** = ponte para o pacote de DD imagem já existente (e', interdependência, RM com LGE — Klein 2024 / Feng 2011 / ESC 2025).
- Não decide doses de AINE, colchicina, corticoide nem timing de pericardiectomia.
