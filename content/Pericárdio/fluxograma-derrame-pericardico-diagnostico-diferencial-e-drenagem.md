---
title: "Fluxograma: Derrame pericárdico — diagnóstico diferencial e indicação de drenagem"
slug: fluxograma-derrame-pericardico-diagnostico-diferencial-e-drenagem
theme: "Pericárdio"
kind: fluxograma
fonte_producao: chatgpt
review_status: revisado
review_note: "Construído a partir de três documentos já publicados e verificados nesta mesma pasta: a classificação de tamanho do derrame por ecocardiograma (ESC 2015, Adler Y et al., Eur Heart J 2015;36(42):2921-2964, DOI 10.1093/eurheartj/ehv318, PMID 26320112, já usada no fluxograma de tamponamento cardíaco desta pasta); a história natural do derrame crônico idiopático de grande volume (Sagristà-Sauleda J et al., N Engl J Med 1999;341(27):2054-2059, PMID 10615077, já lida e verificada em documento próprio desta pasta em 07/08/2026); e o estudo comparativo entre pericardiocentese e janela pericárdica cirúrgica no derrame neoplásico, citado no documento de inibidores de IL-1 desta pasta — PMID confirmado nesta sessão via PubMed E-utilities (esummary): 37457544, título 'Best management of patients with malignant pericardial effusion: A comparative study between imaging-guided pericardiocentesis and surgical pericardial window' batendo a publicação. Nenhum número novo foi introduzido além dos já verificados nesses três documentos."
source_refs: ["Adler Y, Charron P, Imazio M, et al. 2015 ESC Guidelines for the diagnosis and management of pericardial diseases. European Heart Journal. 2015;36(42):2921-2964. DOI: 10.1093/eurheartj/ehv318. PMID: 26320112 — classificação do derrame pericárdico por tamanho ao ecocardiograma (pequeno, moderado, grande).", "Sagristà-Sauleda J, Angel J, Permanyer-Miralda G, Soler-Soler J. Long-term follow-up of idiopathic chronic pericardial effusion. New England Journal of Medicine. 1999;341(27):2054-2059. DOI: 10.1056/NEJM199912303412704. PMID: 10615077 — risco de tamponamento imprevisível e recorrência após pericardiocentese isolada no derrame crônico idiopático de grande volume.", "Best management of patients with malignant pericardial effusion: A comparative study between imaging-guided pericardiocentesis and surgical pericardial window. Journal of Clinical and Translational Research. 2023. PMID: 37457544 — comparação entre pericardiocentese isolada e janela pericárdica cirúrgica no derrame neoplásico recorrente."]
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

  D2 -->|"Moderado, de 10 a 20 mm"| D3{"A etiologia já está estabelecida pela<br/>investigação clínica de base — por<br/>exemplo pericardite viral já tratada,<br/>uremia em diálise, doença autoimune<br/>conhecida?"}

  D3 -->|"Sim, etiologia conhecida<br/>e tratável pela causa"| C3(["Tratar a causa de base; reavaliação<br/>ecocardiográfica seriada, sem<br/>pericardiocentese de rotina"])

  D3 -->|"Não — etiologia não esclarecida, ou<br/>suspeita de causa que exige<br/>confirmação (neoplasia, infecção<br/>bacteriana ou tuberculosa)"| C4(["Pericardiocentese diagnóstica, guiada<br/>por eco, de forma eletiva — análise<br/>bioquímica, citológica, cultura e,<br/>quando pertinente, pesquisa de<br/>micobactéria/ADA"])

  D2 -->|"Grande, acima de 20 mm"| D4{"O derrame é recorrente após<br/>pericardiocentese prévia, ou é crônico<br/>(mais de 3 meses) e permanece sem<br/>causa identificada apesar da<br/>investigação?"}

  D4 -->|"Não — primeira punção, com<br/>indicação diagnóstica e/ou<br/>sintomática"| C5(["Pericardiocentese guiada por eco —<br/>mesmo em paciente assintomático,<br/>derrame grande crônico tem risco de<br/>tamponamento súbito e imprevisível a<br/>qualquer momento"])

  D4 -->|"Sim — recorreu após punção<br/>prévia, ou é neoplásico com<br/>recidiva esperada"| C6(["Considerar drenagem definitiva: janela<br/>pericárdica cirúrgica (ou pericárdio-<br/>peritoneal) — recorrência após<br/>pericardiocentese isolada é comum, e<br/>não deve ser tratada como falha de<br/>técnica do primeiro procedimento"])

  classDef conduta fill:#eef6ef,stroke:#2f7a4f,color:#12301f;
  class C1,C2,C3,C4,C5,C6 conduta;
```

## O que a árvore não mostra

**"Bem tolerado por anos" não é sinônimo de "seguro".** A coorte de
Sagristà-Sauleda mostrou que, em 28 pacientes com derrame crônico idiopático
de grande volume (mediana de 3 anos de duração ao diagnóstico), **13 eram
assintomáticos na avaliação inicial** — e ainda assim **8 (29%) evoluíram
para tamponamento cardíaco franco**, de forma inesperada, a qualquer momento
do seguimento. É esse dado que sustenta o ramo "pericardiocentese mesmo
assintomático" para o derrame grande crônico, mesmo sem etiologia definida.

**Pericardiocentese isolada resolve uma minoria dos casos de forma
definitiva.** Na mesma coorte, o derrame desapareceu ou reduziu de forma
marcante em apenas 8 dos 24 pacientes puncionados — em 11, o derrame de
grande volume **recidivou**. A pericardiectomia deve ser considerada sempre
que a recorrência acontecer, não reservada como último recurso depois de
várias tentativas de punção repetida.

**No derrame neoplásico, a escolha entre pericardiocentese e janela cirúrgica
depende do que se espera adiante, não só do primeiro episódio.** A literatura
comparativa mostra taxas de recorrência elevadas (60-100%) com
pericardiocentese isolada no derrame maligno — muitas vezes seguida de
esclerose intrapericárdica com talco ou tetraciclina para tentar reduzir a
recidiva —, enquanto a janela pericárdica cirúrgica tende a oferecer melhor
resultado de longo prazo, com a vantagem adicional de fornecer espécime para
avaliação citohistológica. A via pericárdio-peritoneal é opção quando se
deseja drenagem contínua para a cavidade abdominal.

**Suspeita de pericardite purulenta bacteriana muda a lógica da punção.**
Nesse cenário, a pericardiocentese deixa de ser só diagnóstica — ela é
também o primeiro passo de um tratamento em que a drenagem mecânica é
obrigatória, associada a antibioticoterapia empírica imediata; adiar a
punção esperando confirmação por outro exame piora o desfecho. Este
fluxograma sinaliza a suspeita de causa bacteriana/tuberculosa como
indicação de punção diagnóstica, mas a conduta específica de cada etiologia
tem documento próprio nesta pasta.

**Loculação e localização do bolsão não aparecem na árvore.** Derrame
loculado ou de difícil acesso por pericardiocentese isolada — comum no
pós-operatório de cirurgia cardíaca e em processos infecciosos avançados —
pode exigir drenagem cirúrgica de propósito, independentemente do tamanho
medido pelo eco em um único plano.
