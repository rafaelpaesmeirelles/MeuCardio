---
title: "Tamponamento cardíaco"
slug: fluxograma-tamponamento-cardiaco
theme: "Pericárdio"
kind: fluxograma
summary: "Protocolo de conduta imediata para tamponamento cardíaco: da tríade de Beck e confirmação por ecocardiograma point-of-care até a escolha entre pericardiocentese de emergência e drenagem cirúrgica conforme a causa, com rota própria para o paciente periparada."
review_status: revisado
source_refs: ["Pericardial tamponade: A comprehensive emergency medicine and echocardiography review · PubMed · 2022 · https://pubmed.ncbi.nlm.nih.gov/35696801/", "Pericardiocentesis: Overview, Indications, Contraindications · Medscape · https://emedicine.medscape.com/article/80602-overview", "2025 ESC Guidelines for the management of myocarditis and pericarditis. Eur Heart J. 2025;46(40):3952-4041. DOI: 10.1093/eurheartj/ehaf192. PMID: 40878297 — Tabela 8 (causas de tamponamento cardíaco), texto integral conferido em 30/07/2026.", "Cardiac Tamponade · StatPearls, NCBI Bookshelf · https://www.ncbi.nlm.nih.gov/books/NBK431090/", "Pericardiocentesis in cardiac tamponade: indications and practical aspects · E-Journal of Cardiology Practice, ESC · https://www.escardio.org/Journals/E-Journal-of-Cardiology-Practice/Volume-15/Pericardiocentesis-in-cardiac-tamponade-indications-and-practical-aspects", "Cardiac tamponade due to aortic dissection: clinical picture and treatment with focus on pericardiocentesis · E-Journal of Cardiology Practice, ESC · https://www.escardio.org/communities/councils/cardiology-practice/scientific-documents-and-publications/ejournal/volume-15/Cardiac-tamponade-due-to-aortic-dissection-clinical-picture-and-treatment-with-focus-on-pericardiocentesis/", "Procedure: Pericardiocentesis · Life in the Fast Lane (LITFL) · https://litfl.com/procedure-pericardiocentesis-instructions/", "Comparison of Pericardiocentesis in Post-Cardiac Surgery and Nonsurgical Patients with Pericardial Tamponade · PMC · https://pmc.ncbi.nlm.nih.gov/articles/PMC9423801/", "Adler Y, Charron P, Imazio M, et al. 2015 ESC Guidelines for the diagnosis and management of pericardial diseases · European Heart Journal · 2015;36(42):2921-2964 · DOI: 10.1093/eurheartj/ehv318 · PMID: 26320112 · https://pmc.ncbi.nlm.nih.gov/articles/PMC7539677/"]
---

# Tamponamento cardíaco

Protocolo de conduta imediata, não de investigação diagnóstica ampla. O
gatilho é a suspeita clínica — hipotensão com turgência jugular e bulhas
abafadas (tríade de Beck), pulso paradoxal — e o que decide o próximo passo é
se o paciente está periparada e se a causa por trás do tamponamento é uma
daquelas em que puncionar às cegas pode matar em vez de salvar.

## Árvore de decisão

```mermaid
flowchart TD
  R0["Suspeita clínica de tamponamento:<br/>hipotensão, turgência jugular e bulhas<br/>abafadas (tríade de Beck), pulso<br/>paradoxal, dispneia"] --> P1["Estabilização inicial: monitorização contínua,<br/>2 acessos venosos calibrosos, oxigênio<br/>suplementar, reposição volêmica cautelosa;<br/>evitar diurético, vasodilatador e ventilação<br/>com pressão positiva quando possível"]

  P1 --> D1{"Periparada: deterioração<br/>hemodinâmica iminente ou<br/>parada cardíaca?"}

  D1 -->|"Sim"| D2{"Causa sugere dissecção de aorta,<br/>ruptura de parede livre pós-IAM ou<br/>tamponamento pós-cirúrgico cardíaco?"}

  D2 -->|"Não — outra causa"| C1(["Pericardiocentese de emergência<br/>imediata, sem esperar imagem se não<br/>houver eco à mão — maior bolsão acessível"])

  D2 -->|"Sim"| C2(["Drenagem controlada em pequeno volume,<br/>só para ganhar tempo (ponte); acionar<br/>cirurgia de emergência de imediato,<br/>sem repetir punção ampla"])

  D1 -->|"Não — instável, sem<br/>deterioração iminente"| P2["Confirmar com ecocardiograma<br/>point-of-care: derrame pericárdico,<br/>colapso diastólico de VD, colapso<br/>sistólico de AD, VCI pletórica<br/>não colapsável"]

  P2 --> D3{"Ecocardiograma confirma<br/>tamponamento?"}

  D3 -->|"Não confirma"| C3(["Investigar diagnóstico alternativo;<br/>manter reavaliação clínica"])

  D3 -->|"Confirma"| D4{"Causa sugere dissecção de aorta,<br/>ruptura de parede livre pós-IAM ou<br/>tamponamento pós-cirúrgico cardíaco?"}

  D4 -->|"Sim"| C4(["Não puncionar às cegas: acionar<br/>cirurgia de emergência para drenagem/<br/>reabordagem — pericardiocentese só<br/>como ponte controlada se deteriorar<br/>antes da sala"])

  D4 -->|"Não — outra causa"| D5{"Instabilidade hemodinâmica, ou<br/>suspeita de etiologia específica<br/>(bacteriana, tuberculosa, neoplásica)?"}

  D5 -->|"Instabilidade hemodinâmica,<br/>independente do tamanho do derrame"| C5(["Pericardiocentese guiada por eco, no<br/>maior e mais superficial bolsão,<br/>sem estrutura vital interposta"])

  D5 -->|"Estável, com suspeita de<br/>etiologia específica"| C6(["Pericardiocentese diagnóstica<br/>guiada por eco, de forma eletiva"])

  D5 -->|"Estável, sem indicação<br/>de puncionar"| C7(["Conduta conservadora: tratar causa<br/>de base e reavaliação ecocardiográfica<br/>seriada"])

  classDef conduta fill:#eef6ef,stroke:#2f7a4f,color:#12301f;
  class C1,C2,C3,C4,C5,C6,C7 conduta;
```

## O que vale para todo ramo, e por isso não está na árvore

**Reposição volêmica é ponte, não tratamento.** Em paciente hipotenso (PA
sistólica abaixo de 100 mmHg), um volume baixo — 250 a 500 mL de soro
fisiológico — costuma melhorar a hemodinâmica; volume maior arrisca aumentar
ainda mais a pressão intrapericárdica e piorar o débito cardíaco.

**Diurético intravenoso é contraindicado e pode ser fatal** no tamponamento —
não é um problema de sobrecarga de volume, é compressão mecânica, e reduzir
a pré-carga piora a fisiologia. Vasodilatador (incluindo nitrato) tem o mesmo
efeito de redução de pré-carga e deve ser evitado pelo mesmo motivo.

**Ventilação com pressão positiva reduz débito cardíaco em até 25%** no
tamponamento, por elevar a pressão intratorácica e a pressão de enchimento do
VD — evitar intubação/ventilação mecânica sempre que o paciente sustentar
respiração espontânea.

**Reavaliação contínua** do estado hemodinâmico e do ecocardiograma acompanha
qualquer ramo escolhido, inclusive depois da drenagem — reacúmulo de líquido
exige repetir a decisão.

## Técnica da pericardiocentese, e por que a via às cegas fica reservada à parada

O local de punção ideal é definido pelo ecocardiograma — o ponto em que o
espaço pericárdico está mais próximo da pele e o acúmulo de líquido é maior —
e não, por padrão, o subxifoide. A abordagem apical (1 cm lateral ao ictus,
5º a 7º espaço intercostal) é considerada a mais segura quando o eco aponta
esse trajeto.

A pericardiocentese **às cegas** (sem ecocardiograma nem fluoroscopia) tem
complicação de 15 a 20% (subxifoide, 1 cm inferior à borda xifoidal esquerda,
ângulo de 30°), contra cerca de 2% guiada por imagem — por isso ela só se
justifica em parada cardíaca ou quando não há ultrassom disponível.

## Por que dissecção de aorta e tamponamento pós-cirúrgico não vão para a punção às cegas

**Dissecção de aorta e ruptura de parede livre pós-infarto** são
contraindicação à pericardiocentese com agulha: a descompressão rápida do
pericárdio pode restaurar a pressão arterial o suficiente para reabrir a
comunicação e agravar o sangramento — mortalidade descrita em série de casos
de até 3 de 4 pacientes puncionados, contra sobrevida nos que foram direto
para cirurgia. A exceção é a drenagem controlada em pequenos volumes (5 a
10 mL por vez, mirando pressão sistólica em torno de 90 mmHg) como ponte para
o paciente que não sobrevive até a sala — estratégia temporizadora com
recomendação Classe IIa na diretriz europeia de 2015.

**Tamponamento pós-cirúrgico cardíaco** costuma ter derrame loculado,
frequentemente póstero-lateral, com coágulo ou hematoma intrapericárdico —
achados bem mais comuns nesse contexto do que no tamponamento não cirúrgico e
que tornam a punção subxifoide às cegas pouco confiável; a via é a
reabordagem cirúrgica, com drenagem guiada por imagem reservada a casos
selecionados e sem esses achados.

## Principais causas de tamponamento, em ordem de frequência

Mais comuns: neoplasia/malignidade, causa iatrogênica ou traumática,
pericardite, tuberculose (a mais comum em países em desenvolvimento). Menos
comuns: doença vascular do colágeno (lúpus, artrite reumatoide,
esclerodermia), síndrome de lesão pericárdica, infarto agudo do miocárdio,
dissecção de aorta, uremia, infecção bacteriana, pneumopericárdio. É essa
suspeita etiológica — junto da instabilidade hemodinâmica — que orienta tanto
a via cirúrgica das causas de risco quanto a indicação diagnóstica da punção
nas causas infecciosas ou neoplásicas.
