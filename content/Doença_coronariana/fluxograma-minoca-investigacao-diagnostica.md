---
title: "Fluxograma: MINOCA — investigação diagnóstica do infarto sem doença coronariana obstrutiva"
slug: fluxograma-minoca-investigacao-diagnostica
theme: "Doença coronariana"
kind: fluxograma
fonte_producao: chatgpt
summary: "MINOCA é mais frequente em mulheres e sistematicamente subinvestigado quando a angiografia normal é lida como 'sem doença coronariana' em vez de como início de uma segunda investigação. O fluxograma organiza os passos do diagnóstico de trabalho até a etiologia específica, com a ressonância cardíaca como divisor entre causa isquêmica e não isquêmica."
review_status: revisado
review_note: "PMIDs conferidos nesta sessão via PubMed E-utilities (esearch/esummary): 30913893 (Tamis-Holland JE et al., AHA Scientific Statement sobre MINOCA, Circulation. 2019;139(18):e891-e908) e 30367850 (Nordenskjöld AM et al., Reinfarction in Patients with MINOCA, American Journal of Medicine. 2019;132(3):335-346) — título, revista, ano e volume/páginas batendo exatamente com o texto do documento. O recorte específico de acurácia diagnóstica por sexo já é tratado em documento próprio da biblioteca ('doença isquêmica na mulher'); este fluxograma cobre o algoritmo diagnóstico do MINOCA em si, sem duplicar aquele conteúdo."
source_refs: ["Tamis-Holland JE, Jneid H, Reynolds HR, et al. Contemporary Diagnosis and Management of Patients With Myocardial Infarction in the Absence of Obstructive Coronary Artery Disease · Circulation · 2019 · 139(18):e891-e908 · PMID: 30913893", "Nordenskjöld AM, Lagerqvist B, Baron T, et al. Reinfarction in Patients with Myocardial Infarction with Nonobstructive Coronary Arteries (MINOCA) · American Journal of Medicine · 2019 · 132(3):335-346 · PMID: 30367850"]
---

# Fluxograma: MINOCA — investigação diagnóstica

MINOCA (*myocardial infarction with non-obstructive coronary arteries*) é
diagnóstico de trabalho, não diagnóstico final — a diretriz da American
Heart Association é explícita quanto a isso, e a maior armadilha clínica é
parar a investigação no momento em que a angiografia mostra coronárias sem
obstrução significativa. É mais frequente em mulheres do que em homens, e o
documento **"Doença isquêmica na mulher"** desta biblioteca trata da acurácia
diferencial dos testes por sexo; este fluxograma cobre o algoritmo
diagnóstico do MINOCA propriamente dito, a partir do momento em que a
angiografia já foi feita.

## Árvore de decisão

```mermaid
flowchart TD
  R0["Diagnóstico de infarto do miocárdio confirmado<br/>(troponina com padrão dinâmico e critérios clínicos/ECG),<br/>angiografia coronária já realizada"] --> D1{"Angiografia mostra estenose coronária<br/>obstrutiva (≥50%) explicando o quadro?"}

  D1 -->|"Sim"| C1(["IAM com doença coronariana obstrutiva:<br/>seguir o fluxograma padrão de síndrome<br/>coronariana aguda"])

  D1 -->|"Não — coronárias normais<br/>ou estenose < 50%"| D2{"Critérios de MINOCA preenchidos, sem causa<br/>alternativa já evidente (miocardite, síndrome de<br/>Takotsubo, embolia pulmonar etc.)?"}

  D2 -->|"Não"| C2(["Investigar o diagnóstico alternativo específico<br/>sugerido pelo quadro clínico"])

  D2 -->|"Sim — MINOCA de trabalho"| D3{"Ressonância magnética cardíaca disponível<br/>e sem contraindicação?"}

  D3 -->|"Não"| C3(["Investigação limitada: ecocardiograma seriado<br/>e considerar reavaliação angiográfica com imagem<br/>intracoronária (OCT/IVUS) para afastar dissecção<br/>espontânea ou placa não obstrutiva rota"])

  D3 -->|"Sim"| P1["Ressonância magnética cardíaca com protocolo<br/>dedicado (mapeamento T1/T2, realce tardio) para<br/>diferenciar a etiologia"]

  P1 --> D4{"A RM identifica padrão isquêmico focal<br/>(subendocárdico ou transmural, compatível<br/>com infarto)?"}

  D4 -->|"Não — padrão sugere causa<br/>não isquêmica ou RM normal"| C4(["Reclassificar o diagnóstico (miocardite ou<br/>outra cardiomiopatia identificada pela RM):<br/>sair da via de MINOCA e tratar a etiologia confirmada"])

  D4 -->|"Sim"| D5{"Imagem intracoronária (OCT/IVUS) ou angiografia<br/>com múltiplas projeções sugere dissecção coronária<br/>espontânea (SCAD) ou ruptura/erosão de placa<br/>não obstrutiva?"}

  D5 -->|"Sim"| C5(["Tratar a causa coronariana específica<br/>identificada (conduta conservadora na SCAD estável;<br/>considerar antiagregação/estatina na placa rota)"])

  D5 -->|"Não"| C6(["Provável espasmo coronário ou<br/>tromboembolismo coronário sem substrato visível:<br/>testar vasoespasmo quando seguro e manter<br/>antiagregação/estatina empíricas"])

  classDef conduta fill:#eef6ef,stroke:#2f7a4f,color:#12301f;
  class C1,C2,C3,C4,C5,C6 conduta;
```

## O que a árvore não mostra

**A prevalência de MINOCA é maior em mulheres, e isso muda o limiar de
suspeita, não o algoritmo.** A diretriz cita prevalência de 5% a 6% dos
infartos, desproporcionalmente maior em mulheres jovens — mas uma vez que o
diagnóstico de trabalho é levantado, a investigação seguinte (RM, imagem
intracoronária) é a mesma para ambos os sexos. A diferença por sexo está na
acurácia de testes de estratificação de risco pré-angiografia, tema do
documento "Doença isquêmica na mulher" desta biblioteca.

**O prognóstico do MINOCA não é benigno**, apesar do nome sugerir isso. A
coorte sueca de Nordenskjöld et al. mostrou taxa relevante de reinfarto no
seguimento — a árvore termina na etiologia, mas o seguimento clínico e a
prevenção secundária continuam sendo necessários mesmo quando nenhuma
obstrução foi encontrada.

**Teste provocativo de vasoespasmo (ergonovina ou acetilcolina intracoronária)
não está detalhado.** É mencionado como opção em C6, mas a técnica exige
experiência do operador e tem contraindicações relativas (espasmo
multivascular grave, disfunção ventricular importante) que não cabem numa
árvore de decisão binária.

**Embolia pulmonar, sepse e crise hipertensiva grave** são exemplos de causa
alternativa que também elevam troponina sem obstrução coronariana — a árvore
as agrupa em C2 porque, uma vez identificadas, a investigação sai
completamente da via cardiológica de MINOCA.