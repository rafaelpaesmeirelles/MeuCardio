---
title: "Fluxograma: suspeita de AVC agudo — reconhecimento e primeira hora"
slug: fluxograma-suspeita-de-avc-agudo-primeira-hora
theme: "Geral"
kind: fluxograma
review_status: revisado
fonte_producao: chatgpt
version: 2
review_note: "Revisão clínica concluída em 27/08/2026 contra AHA/American Red Cross 2024 e AHA/ASA 2026. O nó de imagem foi corrigido para excluir hemorragia e manter a hipótese clínica de AVC isquêmico, sem exigir confirmação radiológica precoce."
source_refs: ["Hewett Brumberg EK, Douma MJ, Alibertis K, et al. 2024 American Heart Association and American Red Cross Guidelines for First Aid. Circulation. 2024;150:e519-e579. DOI: 10.1161/CIR.0000000000001281.", "Prabhakaran S, Gonzalez NR, Zachrison KS, et al. 2026 Guideline for the Early Management of Patients With Acute Ischemic Stroke. Stroke. DOI: 10.1161/STR.0000000000000513; correção DOI: 10.1161/STR.0000000000000530."]
---

# Fluxograma: suspeita de AVC agudo — reconhecimento e primeira hora

```mermaid
flowchart TD
  A["Déficit neurológico súbito:<br/>face, braço, fala ou outro sinal focal"] --> B{"Adulto com suspeita de AVC?"}
  B -->|"Sim"| C["Acionar imediatamente o SAMU 192.<br/>Não dirigir e não esperar melhorar"]
  B -->|"Criança ou apresentação não típica"| C2["Acionar emergência; FAST isolado<br/>não foi validado para excluir AVC pediátrico"]
  C --> D["Registrar última vez bem,<br/>início testemunhado ou ao despertar"]
  C2 --> D
  D --> E{"Glicemia disponível sem atrasar o chamado?"}
  E -->|"Sim"| F["Medir; tratar hipoglicemia por protocolo.<br/>Se déficit persiste, manter alerta de AVC"]
  E -->|"Não"| G["Prosseguir sem atraso"]
  F --> H["Informar anticoagulante/última dose,<br/>sangramento, trauma, convulsão e cefaleia súbita"]
  G --> H
  H --> I["Serviço de emergência:<br/>ativar protocolo, ABC, sinais vitais,<br/>glicemia e neuroimagem urgente"]
  I --> J{"Hemorragia excluída e hipótese clínica<br/>de AVC isquêmico mantida?"}
  J -->|"Não/indefinido"| K["Tratar o diagnóstico identificado<br/>e manter avaliação especializada"]
  J -->|"Sim"| L["Equipe de AVC avalia déficit incapacitante,<br/>janela, imagem e contraindicações"]
  L --> M["Reperfusão e destino definidos<br/>pelo protocolo e pela capacidade local"]

  classDef action fill:#eef6ef,stroke:#2f7a4f,color:#12301f;
  class C,C2,D,F,G,H,I,K,L,M action;
```

## Limites do diagrama

O fluxo não reproduz critérios completos de trombólise, trombectomia ou metas
pressóricas. Esses critérios mudam com horário, imagem, subtipo, gravidade,
anticoagulação e capacidade local. A ação segura que o diagrama fixa é não
perder tempo nem iniciar antitrombótico antes de excluir hemorragia.
A TC sem contraste pode ser inicialmente normal no AVC isquêmico; excluir
hemorragia não equivale a exigir confirmação radiológica do infarto antes da
decisão de reperfusão.

## Tudo com Tudo

- [Protocolo de reconhecimento e primeira hora](deficit-neurologico-focal-subito-reconhecimento-e-primeira-hora-do-avc.md)
- [Alteplase](../Farmacologia/alteplase.md)
- [Tenecteplase](../Farmacologia/tenecteplase.md)

