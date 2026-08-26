---
title: "Fluxograma: Doença pericárdica induzida por radioterapia — da fase aguda à constrição tardia"
slug: fluxograma-doenca-pericardica-actinica-radioterapia
theme: "Pericárdio"
kind: fluxograma
fonte_producao: chatgpt
review_status: revisado
review_note: "Revisado contra a diretriz ESC 2022 de cardio-oncologia (PMID 36017568, DOI 10.1093/eurheartj/ehac244), além das revisões de doença cardíaca/pericárdica actínica já citadas. O rastreamento foi corrigido para ser estratificado pelo risco global de toxicidade cardiovascular — com preferência pela dose média cardíaca, quando disponível — e não por uma dicotomia não validada de 5 versus 10 anos. A constrição pós-radiação foi mantida sob os critérios diagnósticos gerais, mas a decisão cirúrgica agora exige avaliação especializada porque cardiomiopatia, coronariopatia e valvopatia concomitantes influenciam risco e benefício. Marcador residual de verificação humana removido após confronto com a diretriz. Revisão documental concluída; pendente revisão médica independente antes de uso assistencial."
source_refs: ["Lyon AR, López-Fernández T, Couch LS, et al. 2022 ESC Guidelines on cardio-oncology. European Heart Journal. 2022;43(41):4229-4361. DOI: 10.1093/eurheartj/ehac244. PMID: 36017568 — estratificação de risco, vigilância de sobreviventes e doença pericárdica pós-radioterapia.", "Quintero-Martinez JA, Cordova-Madera SN, Villarraga HR. Radiation-Induced Heart Disease. Journal of Clinical Medicine. 2021;11(1):146. DOI: 10.3390/jcm11010146. PMID: 35011887. PMCID: PMC8745750 — fases clínicas e manifestações da doença cardíaca actínica.", "von Kemp BA, Cosyns B. Radiation-Induced Pericardial Disease: Mechanisms, Diagnosis, and Treatment. Current Cardiology Reports. 2023;25(10):1113-1121. DOI: 10.1007/s11886-023-01933-3. PMID: 37584875 — classificação em fase aguda e fase crônica/tardia."]
---

# Fluxograma: Doença pericárdica induzida por radioterapia — da fase aguda à constrição tardia

A radioterapia torácica — usada em linfoma de Hodgkin, câncer de mama
(sobretudo do lado esquerdo), câncer de pulmão e outros tumores mediastinais
— pode lesar o pericárdio em duas janelas temporais bem separadas: **dias a
meses** depois (fase aguda) ou **anos a décadas** depois (fase
crônica/tardia), muitas vezes já fora do acompanhamento oncológico ativo. O
primeiro ramo desta árvore não é uma decisão clínica diante de sintoma, mas
sim **em que momento clínico o paciente está agora** — porque é isso que
decide se a via é vigilância assintomática, tratamento de pericardite aguda,
diferencial de derrame, ou investigação de constrição tardia.

## Árvore de decisão

```mermaid
flowchart TD
  R0["Paciente com história de radioterapia<br/>torácica prévia — linfoma, câncer de<br/>mama, câncer de pulmão ou tumor<br/>mediastinal"] --> D1{"Qual o momento clínico atual?"}

  D1 -->|"Assintomático, dentro do<br/>seguimento oncológico estruturado,<br/>sem sinal cardíaco novo"| D2{"Qual o risco de toxicidade cardiovascular<br/>após o tratamento, considerando dose<br/>média cardíaca da radioterapia,<br/>antraciclina, eventos durante o tratamento,<br/>doença e fatores de risco cardiovasculares?"}

  D2 -->|"Muito alto ou alto precoce"| C1(["Avaliação cardiovascular anual;<br/>considerar ecocardiograma nos anos 1, 3<br/>e 5 após o tratamento e, depois, a cada<br/>5 anos, conforme a diretriz de<br/>cardio-oncologia"])

  D2 -->|"Alto tardio"| C2(["Avaliação cardiovascular anual a partir<br/>de 5 anos; considerar ecocardiograma e<br/>rastreamento não invasivo de coronariopatia<br/>a cada 5 anos conforme protocolo local"])

  D2 -->|"Moderado"| C7(["Considerar avaliação clínica, ECG,<br/>peptídeo natriurético e ecocardiograma<br/>a cada 5 anos se a avaliação ao fim do<br/>tratamento foi normal"])

  D2 -->|"Baixo ou risco não definido"| C8(["Não inventar calendário apenas pela<br/>história de radioterapia: completar a<br/>estratificação de cardio-oncologia e<br/>individualizar o seguimento"])

  D1 -->|"Sintomas agudos — dor torácica<br/>pleurítica, atrito pericárdico —,<br/>dias a meses após a radioterapia"| C3(["Investigar e tratar como pericardite<br/>aguda, seguindo o fluxograma de<br/>pericardite aguda desta biblioteca — a<br/>etiologia actínica não muda a<br/>abordagem inicial"])

  D1 -->|"Derrame pericárdico assintomático,<br/>achado em exame de imagem de<br/>seguimento oncológico"| C4(["Seguir a árvore de derrame pericárdico<br/>desta biblioteca para diagnóstico<br/>diferencial e decisão de drenagem,<br/>registrando a radioterapia prévia como<br/>etiologia possível"])

  D1 -->|"Sinais insidiosos de insuficiência<br/>cardíaca direita, anos a décadas<br/>após a radioterapia"| D3{"Ecocardiograma, tomografia contrastada<br/>ou ressonância com realce tardio<br/>mostram espessamento pericárdico e<br/>critérios hemodinâmicos de constrição?"}

  D3 -->|"Sim"| C5(["Pericardite constritiva actínica<br/>confirmada: encaminhar a centro<br/>experiente para avaliar pericardiectomia<br/>e doença miocárdica, coronária e valvar<br/>concomitante; a etiologia influencia<br/>risco e prognóstico cirúrgicos"])

  D3 -->|"Não confirma constrição"| C6(["Investigar diagnóstico alternativo para a<br/>insuficiência cardíaca direita — a<br/>história de radioterapia não confirma,<br/>por si só, a constrição"])

  classDef conduta fill:#eef6ef,stroke:#2f7a4f,color:#12301f;
  class C1,C2,C3,C4,C5,C6,C7,C8 conduta;
```

## O que a árvore não mostra

**O risco atual não pode ser inferido por séries históricas.** Técnicas
modernas reduziram a exposição cardíaca, mas doença pericárdica ainda pode
surgir meses a décadas depois da radioterapia. A incidência depende do campo,
da dose recebida pelas estruturas cardíacas, de terapias concomitantes e da
população; por isso, percentuais antigos não devem ser apresentados como
risco contemporâneo individual.

**A dose média cardíaca é preferível à dose prescrita.** A diretriz ESC 2022
classifica o risco tardio combinando a dose média cardíaca, a dose cumulativa
de antraciclina, eventos ocorridos durante o tratamento, doença cardiovascular
prévia e fatores de risco. Lado irradiado ou dose total prescrita, isolados,
não substituem a dosimetria cardíaca e não fornecem um corte específico para
pericardite.

**Perguntar sobre radioterapia torácica prévia é o passo mais fácil de
pular.** Em paciente com derrame pericárdico de causa não imediatamente
óbvia — sobretudo se anos ou décadas se passaram desde o tratamento
oncológico — a exposição pode nem ser mencionada espontaneamente, e o próprio
paciente pode não relacionar sintomas cardíacos atuais a um tratamento
distante. Constrição de início insidioso em ex-paciente oncológico deve
levantar a hipótese actínica mesmo sem outro fator de risco clássico para
constrição, como tuberculose ou cirurgia cardíaca prévia.

**Os critérios hemodinâmicos específicos de constrição não são repetidos
aqui.** Variação respiratória de fluxo mitral/tricúspide, septal bounce e
acoplamento ventricular seguem os mesmos critérios já publicados nos
documentos desta pasta sobre pericardite efusivo-constritiva e critérios
numéricos de constrição por imagem — não há, na literatura consultada,
particularidade validada que justifique um critério diagnóstico à parte. Isso
não torna a etiologia irrelevante: fibrose miocárdica, coronariopatia e
valvopatia actínicas podem coexistir e devem ser avaliadas antes de decidir
pericardiectomia.
