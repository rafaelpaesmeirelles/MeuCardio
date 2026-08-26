---
title: "Fluxograma: Pericardite constritiva versus cardiomiopatia restritiva — diagnóstico diferencial por imagem"
slug: fluxograma-pericardite-constritiva-versus-cardiomiopatia-restritiva
theme: "Pericárdio"
kind: fluxograma
fonte_producao: chatgpt
review_status: revisado
review_note: "Construído a partir de três fontes já lidas e verificadas em documentos próprios desta mesma pasta, sem introduzir nenhum PMID, DOI ou número novo: (1) o gradiente numérico de e' medial que separa constrição de restrição — e′ > 8 cm/s constrição, e′ 6-8 cm/s com desvio septal fisiologia mista, e′ < 6 cm/s restrição — e os critérios de espessura pericárdica (> 3 mm) e annulus reversus, todos do posicionamento internacional Klein AL et al., JACC Cardiovasc Imaging 2024, PMID 39111992, já lido em texto integral (PMC12156183) e verificado em documento próprio desta pasta em 01/08/2026; (2) o critério ecocardiográfico combinado (desvio septal respirofásico associado a e' medial ≥9 cm/s OU razão de reversão diastólica expiratória da veia hepática ≥0,79, sensibilidade 87%/especificidade 91%, especificidade 97% com os três fatores juntos), da revisão em Circulation: Cardiovascular Imaging já citada no documento 'tamponamento-cardiaco-e-pericardite-constritiva-diagnostico-e-manejo' desta pasta; (3) a recomendação Classe I nível C da ESC 2025 (Schulz-Menger J et al., Eur Heart J 2025, PMID 40878297, Recommendation Table 24) sobre terapia anti-inflamatória na constrição transitória versus pericardiectomia na permanente, e o critério de reversibilidade por realce tardio ao gadolínio (espessura do realce ≥3 mm, sensibilidade 86%/especificidade 80%) de Feng D et al., Circulation 2011, PMID 21969014, ambos já verificados no mesmo documento desta pasta em 30/07/2026. Nenhum limiar foi alterado; a árvore só reorganiza esses três achados já publicados numa sequência de decisão."
source_refs: ["Klein AL, Wang TKM, Cremer PC, Abbate A, Adler Y, et al. Pericardial Diseases: International Position Statement on New Concepts and Advances in Multimodality Cardiac Imaging. Journal of the American College of Cardiology: Cardiovascular Imaging. 2024;17(8):937-988. DOI: 10.1016/j.jcmg.2024.04.010. PMID: 39111992. PMCID: PMC12156183 — critérios numéricos de e' medial, annulus reversus e espessura pericárdica que separam constrição de restrição.", "Echocardiographic Diagnosis of Constrictive Pericarditis. Circulation: Cardiovascular Imaging. DOI: 10.1161/circimaging.113.001613 — critério ecocardiográfico combinado (desvio septal + e' medial ≥9 cm/s ou reversão diastólica expiratória de veia hepática ≥0,79), sensibilidade e especificidade.", "Schulz-Menger J, Collini V, Gröschel J, Adler Y, et al. 2025 ESC Guidelines for the management of myocarditis and pericarditis. European Heart Journal. 2025;46(40):3952-4041. DOI: 10.1093/eurheartj/ehaf192. PMID: 40878297 — Recommendation Table 24, terapia anti-inflamatória na constrição transitória e pericardiectomia na constrição permanente, Classe I nível C.", "Feng D, Glockner J, Kim K, et al. Cardiac magnetic resonance imaging pericardial late gadolinium enhancement and elevated inflammatory markers can predict the reversibility of constrictive pericarditis after antiinflammatory medical therapy: a pilot study. Circulation. 2011;124(17):1830-1837. DOI: 10.1161/CIRCULATIONAHA.111.026070. PMID: 21969014 — corte de espessura do realce tardio ≥3 mm, sensibilidade 86%/especificidade 80% para reversibilidade."]
---

# Fluxograma: Pericardite constritiva versus cardiomiopatia restritiva — diagnóstico diferencial por imagem

As duas condições convergem para o mesmo quadro clínico — insuficiência cardíaca
direita com fração de ejeção preservada, sinais de restrição diastólica — e exigem
condutas radicalmente diferentes: pericardiectomia numa, investigação de doença
miocárdica infiltrativa na outra. A pasta já tem os números que separam as duas
(posicionamento internacional de imagem multimodal de 2024) e a conduta da
constrição confirmada (ESC 2025), mas nenhum documento os organizava como sequência
de decisão diagnóstica. Este fluxograma parte do ponto em que a suspeita clínica já
existe e o ecocardiograma inicial está indicado.

## Árvore de decisão

```mermaid
flowchart TD
  R0["Insuficiência cardíaca direita com FE preservada e sinais de restrição<br/>diastólica (dispneia, edema, ascite, turgência jugular, sinal de Kussmaul) —<br/>suspeita de pericardite constritiva versus cardiomiopatia restritiva"] --> P1["Ecocardiograma transtorácico com Doppler tecidual do anel mitral<br/>medial (e') e avaliação de interdependência ventricular<br/>(desvio septal respirofásico) — Classe I"]

  P1 --> D1{"Velocidade e' medial ao Doppler tecidual do anel mitral"}

  D1 -->|"e' > 8 cm/s (normal ou supranormal)"| D2{"Desvio septal respirofásico presente<br/>(interdependência ventricular)?"}
  D1 -->|"e' entre 6 e 8 cm/s"| D3{"Desvio septal respirofásico presente<br/>(interdependência ventricular)?"}
  D1 -->|"e' < 6 cm/s"| C1(["Padrão sugestivo de cardiomiopatia restritiva: e' medial baixa é o<br/>inverso do esperado na constrição — investigar etiologia infiltrativa/<br/>miocárdica (amiloidose, RM cardíaca com mapeamento T1, considerar<br/>biópsia); pericardite constritiva é diagnóstico improvável"])

  D2 -->|"Sim"| D4{"Desvio septal associado a e' medial ≥ 9 cm/s OU<br/>reversão diastólica expiratória de veia hepática ≥ 0,79?"}
  D2 -->|"Não"| C2(["Padrão indeterminado ao Doppler: complementar com TC/RM cardíaca<br/>multimodal (espessura pericárdica, calcificação, realce tardio ao<br/>gadolínio) e cateterismo cardíaco antes de definir a etiologia"])

  D3 -->|"Sim"| C3(["Fisiologia mista constrição-restrição (e' 6-8 cm/s com desvio<br/>septal): RM/TC multimodal obrigatória para espessamento, calcificação<br/>e inflamação ativa do pericárdio antes de qualquer decisão terapêutica"])
  D3 -->|"Não"| C6(["Zona borderline (e' 6-8 cm/s sem desvio septal): padrão mais<br/>compatível com cardiomiopatia restritiva pela ausência de<br/>interdependência ventricular — mesma investigação etiológica<br/>infiltrativa/miocárdica do ramo com e' < 6 cm/s, correlacionando<br/>com RM/TC multimodal e cateterismo se a dúvida persistir"])

  D4 -->|"Presente — sensibilidade 87%, especificidade 91%;<br/>com os três critérios juntos, especificidade 97%"| P2["TC ou RM cardíaca multimodal para espessura pericárdica<br/>(> 3 mm), calcificação e sinais de inflamação ativa<br/>(realce tardio ao gadolínio) — Classe I, nível C, ESC 2025"]
  D4 -->|"Ausente"| C2b(["Padrão indeterminado mesmo com desvio septal presente:<br/>complementar com TC/RM cardíaca multimodal e cateterismo<br/>cardíaco antes de definir a etiologia"])

  P2 --> D5{"Realce tardio pericárdico ao gadolínio (inflamação ativa),<br/>com espessura do realce ≥ 3 mm e PCR/VHS elevados?"}

  D5 -->|"Presente — sugere constrição transitória/reversível"| C4(["Constrição provavelmente transitória: terapia anti-inflamatória<br/>(AINE/colchicina, associados a corticoide se necessário) por 3 a<br/>6 meses antes de considerar cirurgia — Classe I, nível C, ESC 2025"])
  D5 -->|"Ausente, OU falha da terapia anti-inflamatória após 3-6 meses"| C5(["Constrição permanente: pericardiectomia — Classe I, nível C,<br/>ESC 2025 (sem inflamação ativa, ou sem sucesso da terapia<br/>anti-inflamatória em 3 a 6 meses de tentativa)"])

  classDef conduta fill:#eef6ef,stroke:#2f7a4f,color:#12301f;
  class C1,C2,C2b,C3,C4,C5,C6 conduta;
```

## O parâmetro que abre a árvore, e por quê

A **velocidade e' medial** ao Doppler tecidual do anel mitral é o achado mais
contraintuitivo do diagnóstico diferencial, e por isso está na raiz da decisão: ela
se comporta como um **gradiente contínuo e invertido** em relação ao que a maioria
espera. Na constrição pericárdica, o miocárdio está preservado e o relaxamento
diastólico é normal ou até acelerado pela pressão intrapericárdica elevada — daí
e' **alta** (> 8 cm/s). Na cardiomiopatia restritiva, o miocárdio em si está doente
(infiltrado, fibrosado), e o relaxamento é lento — daí e' **baixa** (< 6 cm/s). O
**annulus reversus** (e' medial maior que e' lateral) é o achado correlato que mais
desconcerta quem não o espera, porque inverte a relação habitual entre as duas
paredes.

## O critério ecocardiográfico combinado, e o que ele acrescenta ao e' isolado

Nenhum achado isolado fecha diagnóstico — é a mesma advertência já registrada no
documento de critérios numéricos desta pasta. Por isso a árvore não para no e'
medial: quando ele é compatível com constrição (> 8 cm/s) e há desvio septal
respirofásico, o passo seguinte é checar se esse desvio vem acompanhado de e'
medial ≥ 9 cm/s **ou** razão de reversão diastólica expiratória da veia hepática
≥ 0,79 — combinação com sensibilidade de 87% e especificidade de 91%, que sobe a
97% de especificidade quando os três fatores (desvio septal + e' ≥ 9 + reversão
hepática ≥ 0,79) coexistem no mesmo paciente.

## Por que a árvore não termina na imagem multimodal

Confirmar constrição pericárdica por TC/RM (espessura > 3 mm, calcificação, realce
tardio) não encerra a decisão terapêutica — só a diagnóstica. A ESC 2025 separa a
constrição em **transitória** (com inflamação pericárdica ativa concomitante, que
pode regredir com terapia anti-inflamatória) e **permanente** (sem inflamação
ativa, ou refratária após 3 a 6 meses de tratamento clínico otimizado), e as duas
têm recomendação própria Classe I nível C. Tratar toda constrição como cirúrgica
de saída expõe ao risco de uma pericardiectomia evitável; tratar toda constrição
como reversível sem prazo definido posterga uma cirurgia necessária.

## Armadilhas clínicas

- **Ler e' baixa como constrição grave.** É o contrário: e' **alta** (> 8 cm/s) é
  da constrição pericárdica; e' **baixa** (< 6 cm/s) aponta para cardiomiopatia
  restritiva. Inverter essa leitura troca o diagnóstico.
- **Exigir pericárdio espessado para considerar constrição.** O posicionamento
  internacional de 2024 já registrado nesta pasta mostra espessura pericárdica
  normal em até 18% dos casos com constrição comprovada em cirurgia — a ausência
  de espessamento não sai desta árvore como critério de exclusão.
- **Fechar diagnóstico por um achado isolado.** Nem o e' medial sozinho, nem o
  desvio septal sozinho: é a combinação, com os cortes numéricos específicos, que
  sustenta sensibilidade e especificidade relatadas.
- **Indicar pericardiectomia antes de avaliar inflamação ativa.** A distinção
  entre constrição transitória e permanente decide entre tratamento clínico por
  3 a 6 meses e cirurgia — pular essa etapa expõe a uma pericardiectomia evitável.
- **Aplicar os cortes de interdependência ventricular do tamponamento a este
  contexto.** São valores diferentes (30% e 60% no tamponamento, 25% e 40% na
  constrição, conforme já registrado no documento de critérios numéricos desta
  pasta) — não são intercambiáveis.
