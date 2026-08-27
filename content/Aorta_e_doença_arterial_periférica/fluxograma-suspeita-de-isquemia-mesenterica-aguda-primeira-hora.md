---
title: "Fluxograma: Suspeita de isquemia mesentérica aguda — primeira hora"
slug: fluxograma-suspeita-de-isquemia-mesenterica-aguda-primeira-hora
theme: "Aorta e doença arterial periférica"
kind: fluxograma
review_status: revisado
fonte_producao: claude
review_note: "Lote auditável de 27/08/2026. Requer revisão clínica humana antes de publicação. Árvore de decisão estrita (raiz única, um pai por nó, conduta só em folha), validada mecanicamente (mermaid.parse + validador de estrutura da casa)."
source_refs: ["Bala M, Catena F, Kashuk J, De Simone B, Gomes CA, Weber D, et al. Acute mesenteric ischemia: updated guidelines of the World Society of Emergency Surgery. World Journal of Emergency Surgery. 2022;17(1):54. DOI: 10.1186/s13017-022-00443-x. PMID: 36261857.", "Koelemay MJ, Geelkerken RH, Kärkkäinen J, Leone N, et al. Editor's Choice – European Society for Vascular Surgery (ESVS) 2025 Clinical Practice Guidelines on the Management of Diseases of the Mesenteric and Renal Arteries and Veins. European Journal of Vascular and Endovascular Surgery. 2025;70(2):153-218. DOI: 10.1016/j.ejvs.2025.06.010. PMID: 40513642."]
---

# Fluxograma: Suspeita de isquemia mesentérica aguda — primeira hora

Árvore de reconhecimento, exame e primeira decisão terapêutica. Não substitui
a decisão da equipe cirúrgica/intervencionista nem o protocolo institucional.

## Árvore de decisão

```mermaid
flowchart TD
  R0["Dor abdominal aguda intensa,<br/>desproporcional ao exame físico,<br/>em paciente com fator de risco<br/>cardiovascular ou vascular"] --> D1{"Sinais de peritonite<br/>(irritação peritoneal, defesa,<br/>sepse abdominal)?"}

  D1 -->|"Sim"| C1(["Ressuscitação volêmica,<br/>antibiótico de amplo espectro<br/>e laparotomia ou laparoscopia<br/>sem aguardar angiotomografia"])

  D1 -->|"Não"| P1["Angiotomografia de abdome<br/>com contraste em fases arterial<br/>e venosa, sem atraso"]

  P1 --> D2{"Achado da angiotomografia"}

  D2 -->|"Sinais de infarto<br/>intestinal ou perfuração,<br/>qualquer etiologia"| C3(["Ressuscitação e laparotomia<br/>ou laparoscopia sem atraso"])

  D2 -->|"Oclusão arterial (êmbolo<br/>ou trombose), sem sinais<br/>de infarto"| D3{"Expertise em<br/>revascularização<br/>endovascular disponível?"}

  D2 -->|"Vasoconstrição difusa sem<br/>oclusão focal, em paciente<br/>crítico ou em vasopressor"| C4(["Corrigir a causa do baixo<br/>fluxo, revisar vasoconstritor<br/>evitável e considerar<br/>vasodilatador intra-arterial<br/>sob heparinização protetora"])

  D2 -->|"Trombose de veia<br/>mesentérica"| C5(["Anticoagulação plena com<br/>heparina não fracionada ou<br/>de baixo peso molecular,<br/>primeira linha"])

  D2 -->|"Normal ou outro<br/>achado"| C6(["Investigar diagnóstico<br/>alternativo; manter<br/>vigilância clínica"])

  D3 -->|"Sim"| C7(["Revascularização endovascular<br/>como primeira opção"])

  D3 -->|"Não"| C8(["Revascularização cirúrgica<br/>aberta; considerar<br/>transferência a centro<br/>com serviço 24/7"])

  classDef conduta fill:#eef6ef,stroke:#2f7a4f,color:#12301f;
  class C1,C3,C4,C5,C6,C7,C8 conduta;
```

## Notas de leitura da árvore

- O ramo de peritonite segue diretamente para cirurgia porque a WSES 2022
  recomenda laparotomia/laparoscopia pronta diante de peritonite franca
  (recomendação forte), sem esperar a angiotomografia.
- A angiotomografia é o próximo passo em qualquer suspeita mantida, sem
  distinção prévia por fator de risco: a ESVS 2025 recomenda o exame
  independentemente da função renal e recomenda que a suspeita clínica seja
  informada na requisição (Classe I).
- A escolha entre revascularização endovascular e cirurgia aberta segue a
  ESVS 2025 (Classe IIa/B para endovascular como primeira linha quando há
  expertise) e a recomendação de centro com serviço 24/7 multidisciplinar
  (Classe I/C) — daí o encaminhamento a transferência quando não há
  expertise local, em vez de uma conduta cirúrgica isolada como alternativa
  neutra.
- Fator de risco cardioembólico (fibrilação atrial, infarto recente,
  valvopatia, endocardite, embolia prévia) informa a probabilidade
  pré-teste e a comunicação com a cardiologia, mas não muda a ação
  imediata (angiotomografia sem atraso) — por isso não é um ramo da árvore;
  está descrito em prosa no documento de origem.

## Tudo com Tudo — vínculos clínicos diretos

- [Isquemia mesentérica aguda de origem cardioembólica: reconhecimento e a primeira hora](isquemia-mesenterica-aguda-origem-cardioembolica-reconhecimento-e-primeira-hora.md)
