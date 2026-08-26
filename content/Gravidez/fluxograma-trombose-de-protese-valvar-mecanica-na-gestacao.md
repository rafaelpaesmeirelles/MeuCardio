---
title: "Fluxograma: Trombose de prótese valvar mecânica na gestação"
slug: fluxograma-trombose-de-protese-valvar-mecanica-na-gestacao
theme: "Gravidez"
kind: fluxograma
summary: "Árvore de emergência para gestante com prótese mecânica e suspeita de trombose, diferenciando apresentação subaguda não crítica de trombose aguda obstrutiva com necessidade de intervenção urgente."
review_status: revisado
review_note: "Revisão de 26/08/2026 contra a seção 12.5.3.2.2 da ESC 2025. Corrigida a seleção de trombólise: na paciente não crítica, ela pode ser considerada pelo Pregnancy Heart Team já como estratégia inicial e não exige falha prévia de HNF/AVK; na paciente crítica, permanece opção quando cirurgia não está imediatamente disponível, e também deve ser considerada na trombose de prótese direita. O manejo subagudo com HNF e restabelecimento do INR com AVK pode ser suficiente quando selecionado, sem extrapolá-lo à obstrução aguda grave. Mantida a decisão sobre cesárea antes da cirurgia conforme viabilidade fetal e capacidade local. Pendente revisão médica independente antes de uso assistencial."
source_refs: ["De Backer J, Haugaa KH, Hasselberg NE, et al.; ESC Scientific Document Group. 2025 ESC Guidelines for the management of cardiovascular disease and pregnancy. Eur Heart J. 2025;46(43):4462-4568. DOI: 10.1093/eurheartj/ehaf193. PMID: 40878294. Seção 12.5.3.2.2.", "van der Zande JA, Ramlakhan KP, Sliwa K, et al. Pregnancy with a prosthetic heart valve, thrombosis, and bleeding: the ESC EORP Registry of Pregnancy and Cardiac disease III. Eur Heart J. 2025. DOI: 10.1093/eurheartj/ehaf265. PMID: 40237423."]
---

# Trombose de prótese mecânica na gestação

```mermaid
flowchart TD
  R0["Gestante com prótese mecânica + dispneia nova,<br/>IC, síncope, embolia, novo sopro ou clique alterado"]
  P1["ABC + revisar anticoagulação/INR/anti-Xa +<br/>TTE urgente; acionar Pregnancy Heart Team"]
  D1{"TTE confirma ou mantém forte suspeita<br/>de disfunção/trombose protética?"}
  C1(["Não: ampliar diagnóstico diferencial e<br/>seguir investigação conforme risco"])
  P2["Sim: TEE e/ou fluoroscopia/CT conforme necessidade<br/>para mobilidade dos folhetos e gravidade"]
  D2{"Instabilidade, obstrução importante,<br/>regurgitação grave ou deterioração aguda?"}
  P3["Estratégia anticoagulante selecionada:<br/>otimizar HNF e restabelecer INR terapêutico com AVK;<br/>monitorização estreita e imagem seriada"]
  D3{"Função protética e quadro clínico melhoram?"}
  C2(["Sim: manter estratégia anticoagulante<br/>especializada e vigilância da prótese"])
  D5{"Cirurgia imediata disponível e apropriada<br/>ao quadro materno/gestacional?"}
  C3(["Cirurgia conforme a urgência; se o feto for viável,<br/>avaliar cesárea antes da circulação extracorpórea<br/>conforme condição materna e capacidade local"])
  C4(["Trombólise pode ser considerada pelo Heart Team:<br/>especialmente se não crítica, prótese direita<br/>ou cirurgia não imediatamente disponível no caso crítico;<br/>regime exige protocolo específico"])
  D6{"Paciente não crítica: estratégia selecionada<br/>pelo Pregnancy Heart Team conforme lado,<br/>risco hemorrágico, idade gestacional e recursos?<br/>Fibrinólise não exige falha prévia da anticoagulação"}
  C5(["Pós-estabilização: reavaliar anticoagulação,<br/>causa da trombose e plano obstétrico"])

  R0 --> P1
  P1 --> D1
  D1 -->|"Não"| C1
  D1 -->|"Sim"| P2
  P2 --> D2
  D2 -->|"Não"| D6
  D2 -->|"Sim"| D5
  P3 --> D3
  D3 -->|"Sim"| C2
  D3 -->|"Não"| D6
  D6 -->|"HNF + restabelecer INR"| P3
  D6 -->|"Cirurgia"| C3
  D6 -->|"Trombólise"| C4
  D5 -->|"Sim"| C3
  D5 -->|"Não/indisponível"| C4
  C2 --> C5
  C3 --> C5
  C4 --> C5

  classDef conduta fill:#eef6ef,stroke:#2f7a4f,color:#12301f;
  class C1,C2,C3,C4,C5 conduta;
```

## Segurança

Trombose de prótese mecânica na gestação tem alta mortalidade materna. **Eco urgente e definição rápida de obstrução/instabilidade vêm antes da escolha entre cirurgia e trombólise.**

Na apresentação subaguda, otimizar anticoagulação com HNF e restabelecer INR
terapêutico com AVK pode ser suficiente, conforme a ESC 2025. Isso não deve
atrasar intervenção na trombose aguda com obstrução ou regurgitação grave nem
ser transformado em teste obrigatório antes de fibrinólise na paciente não
crítica.

Trombólise não é um ramo automático nem está restrita ao colapso sem cirurgião:
a diretriz permite considerá-la sobretudo em paciente não crítica — sem exigir
falha prévia da anticoagulação —, em trombose de prótese direita e quando
cirurgia não está imediatamente disponível para a paciente crítica. Local da
prótese, estabilidade, idade gestacional, risco de
sangramento e experiência do centro definem a decisão. Dose e velocidade não
são reproduzidas aqui porque dependem de protocolo especializado.

Circulação extracorpórea impõe risco fetal elevado. Quando cirurgia cardíaca é
necessária e o feto é viável, cesárea antes do procedimento oferece benefício de
sobrevida fetal sem aumento demonstrado de mortalidade materna na metanálise
citada pela diretriz; a decisão depende da urgência materna e dos recursos.

## Tudo com Tudo

- [Doença cardiovascular e gravidez — ESC 2025](fluxograma-doenca-cardiovascular-e-gravidez-esc-2025.md)
- [ROPAC III: anticoagulação e risco na prótese mecânica](ropac-iii-anticoagulacao-em-protese-valvar-mecanica-na-gestacao-dados-atualizados-de-risco.md)
- [Trombose de prótese mecânica na gestação — revisão clínica](trombose-de-protese-valvar-mecanica-na-gestacao.md)
- [Trombose de prótese mecânica: fibrinólise ou cirurgia](../Valvopatias/trombose-de-protese-valvar-mecanica-diagnostico-e-decisao-entre-fibrinolise-e-cirurgia.md)
- [Sangramento maior em paciente anticoagulado](../Tromboembolismo/fluxograma-sangramento-maior-em-paciente-anticoagulado.md)
