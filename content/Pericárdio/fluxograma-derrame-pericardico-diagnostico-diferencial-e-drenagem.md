---
title: "Fluxograma: Derrame pericárdico — diagnóstico diferencial e indicação de drenagem"
slug: fluxograma-derrame-pericardico-diagnostico-diferencial-e-drenagem
theme: "Pericárdio"
kind: fluxograma
fonte_producao: chatgpt
review_status: revisado
review_note: "Revisado contra a diretriz ESC 2025 para miocardite e pericardite (PMID 40878297, DOI 10.1093/eurheartj/ehaf192) e a revisão contemporânea de derrames crônicos grandes assintomáticos (PMID 38999452, DOI 10.3390/jcm13133887). A antiga recomendação de drenar rotineiramente todo derrame idiopático grande, crônico e assintomático — derivada de pequena coorte de 1999 — foi removida: a estratégia atual é vigilância especializada quando não há sintomas, inflamação, tamponamento nem suspeita bacteriana/neoplásica. Mantidas indicações de drenagem por tamponamento, suspeita bacteriana/neoplásica, sintomas persistentes e recorrência apesar do tratamento. Revisão documental concluída; pendente revisão médica independente antes de uso assistencial."
source_refs: ["Schulz-Menger J, Collini V, Gröschel J, et al. 2025 ESC Guidelines for the management of myocarditis and pericarditis. European Heart Journal. 2025;46(40):3952-4041. DOI: 10.1093/eurheartj/ehaf192. PMID: 40878297 — triagem etiológica e indicações atuais de drenagem e janela pleuropericárdica.", "Lazarou E, Vlachopoulos C, Antonopoulos A, et al. Asymptomatic Chronic Large Pericardial Effusions: To Drain or to Observe? Journal of Clinical Medicine. 2024;13(13):3887. DOI: 10.3390/jcm13133887. PMID: 38999452. PMCID: PMC11242720 — revisão da evidência contemporânea favorável a vigilância em derrame grande, crônico, idiopático, não inflamatório e assintomático.", "Adler Y, Charron P, Imazio M, et al. 2015 ESC Guidelines for the diagnosis and management of pericardial diseases. European Heart Journal. 2015;36(42):2921-2964. DOI: 10.1093/eurheartj/ehv318. PMID: 26320112 — classificação ecocardiográfica do tamanho do derrame.", "Sagristà-Sauleda J, Angel J, Permanyer-Miralda G, Soler-Soler J. Long-term follow-up of idiopathic chronic pericardial effusion. New England Journal of Medicine. 1999;341(27):2054-2059. DOI: 10.1056/NEJM199912303412704. PMID: 10615077 — coorte histórica pequena; não usada isoladamente para indicar drenagem rotineira."]
---

# Fluxograma: Derrame pericárdico — diagnóstico diferencial e indicação de drenagem

Este fluxograma parte do momento em que um derrame pericárdico já foi
identificado ao ecocardiograma, **sem** os sinais de tamponamento agudo que
exigem punção imediata — esse cenário de emergência já tem fluxograma próprio
nesta pasta. Aqui a pergunta é outra: **este derrame precisa ser drenado, e
se precisar, de que forma** — pericardiocentese diagnóstica eletiva,
pericardiocentese terapêutica, ou drenagem cirúrgica definitiva. O tamanho ao
ecocardiograma organiza a primeira triagem, mas não decide sozinho: um
derrame moderado com etiologia obscura pode precisar de punção diagnóstica
antes de um derrame grande de causa já conhecida e tratável.

## Árvore de decisão

```mermaid
flowchart TD
  R0["Derrame pericárdico identificado ao<br/>ecocardiograma, sem sinais de<br/>tamponamento hemodinâmico agudo"] --> D1{"Há sinais clínicos ou<br/>ecocardiográficos de tamponamento<br/>(deterioração hemodinâmica, colapso de<br/>VD/AD, veia cava inferior pletórica não<br/>colapsável)?"}

  D1 -->|"Sim"| C1(["Não seguir esta árvore: aplicar o<br/>fluxograma de tamponamento cardíaco<br/>desta biblioteca, que define a via de<br/>drenagem de emergência"])

  D1 -->|"Não — paciente<br/>hemodinamicamente estável"| D2{"Qual o tamanho do derrame<br/>ao ecocardiograma (espaço livre<br/>de eco em diástole)?"}

  D2 -->|"Pequeno, abaixo de 10 mm"| C2(["Observação clínica e tratar a causa de<br/>base; pericardiocentese raramente<br/>indicada só pelo tamanho"])

  D2 -->|"Moderado ou grande,<br/>10 mm ou mais"| D3{"Há suspeita de etiologia bacteriana<br/>(inclusive tuberculose) ou neoplásica?"}

  D3 -->|"Sim"| C3(["Pericardiocentese diagnóstica e<br/>terapêutica guiada por imagem; enviar<br/>material para citologia, microbiologia<br/>e testes dirigidos. Suspeita purulenta<br/>exige drenagem e antibiótico imediatos"])

  D3 -->|"Não"| D4{"Há pericardite inflamatória ou causa<br/>sistêmica identificada e tratável?"}

  D4 -->|"Sim"| C4(["Tratar a pericardite ou a causa de<br/>base e monitorar clínica, PCR e<br/>ecocardiograma; não drenar apenas<br/>pelo tamanho se o paciente permanece<br/>estável e assintomático"])

  D4 -->|"Não"| D5{"Há sintomas atribuíveis ao derrame,<br/>crescimento, comprometimento<br/>hemodinâmico ou falha do tratamento<br/>da causa/inflamação?"}

  D5 -->|"Sim"| C5(["Considerar pericardiocentese guiada<br/>por imagem, com drenagem prolongada<br/>quando indicada; drenagem cirúrgica se<br/>punção inviável ou em derrame purulento"])

  D5 -->|"Não — inclusive derrame grande,<br/>crônico, idiopático, não inflamatório<br/>e assintomático"| C6(["Vigilância ambulatorial em centro com<br/>experiência, educação sobre sintomas e<br/>reavaliação clínica/ecocardiográfica<br/>individualizada — em geral, cerca de<br/>cada 6 meses para derrame moderado ou<br/>grande estável"])

  C5 --> D6{"O derrame recidivou apesar do<br/>tratamento e da drenagem apropriados?"}
  D6 -->|"Sim"| C7(["Considerar janela pleuropericárdica;<br/>discutir a via com equipe especializada<br/>conforme etiologia, loculação e risco<br/>cirúrgico"])
  D6 -->|"Não"| C8(["Seguimento dirigido à etiologia e à<br/>evolução clínica/ecocardiográfica"])

  classDef conduta fill:#eef6ef,stroke:#2f7a4f,color:#12301f;
  class C1,C2,C3,C4,C5,C6,C7,C8 conduta;
```

## O que a árvore não mostra

**O dado histórico não autoriza drenagem rotineira.** Uma pequena coorte de
1999 encontrou tamponamento inesperado em 8 de 28 pacientes com derrame
idiopático crônico grande. Evidência observacional mais recente, resumida em
revisão de 2024, mostrou que vigilância é uma opção segura para o fenótipo
estritamente assintomático, crônico, idiopático e sem inflamação. A decisão
deve integrar sintomas, hemodinâmica, evolução, inflamação e etiologia — não
o diâmetro isolado.

**Recorrência não significa pericardiectomia automática.** A diretriz ESC
2025 recomenda considerar janela pleuropericárdica quando o derrame recidiva
apesar de tratamento apropriado. A escolha entre nova punção, drenagem
prolongada, janela ou outra abordagem depende de etiologia, loculação,
prognóstico, risco operatório e necessidade de tecido diagnóstico.

**Suspeita de pericardite purulenta bacteriana muda a lógica da punção.**
Nesse cenário, a pericardiocentese deixa de ser só diagnóstica — ela é
também o primeiro passo de um tratamento em que a drenagem mecânica é
obrigatória, associada a antibioticoterapia empírica imediata; adiar a
drenagem esperando confirmação por outro exame é inadequado. Este
fluxograma sinaliza a suspeita bacteriana/tuberculosa como indicação de
drenagem e coleta diagnóstica, mas a escolha da via e a antibioticoterapia
exigem avaliação especializada imediata.

**Loculação e localização do bolsão não aparecem na árvore.** Derrame
loculado ou de difícil acesso por pericardiocentese isolada — comum no
pós-operatório de cirurgia cardíaca e em processos infecciosos avançados —
pode exigir drenagem cirúrgica de propósito, independentemente do tamanho
medido pelo eco em um único plano.
