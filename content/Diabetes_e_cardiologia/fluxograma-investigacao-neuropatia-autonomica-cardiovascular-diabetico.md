---
title: "Fluxograma: Investigação da Neuropatia Autonômica Cardiovascular no Diabético"
slug: fluxograma-investigacao-neuropatia-autonomica-cardiovascular-diabetico
theme: "Diabetes e cardiologia"
kind: fluxograma
fonte_producao: chatgpt
review_status: revisado
review_note: "Árvore construída a partir de fonte nova consultada e verificada nesta produção — ADA Professional Practice Committee, 'Retinopathy, Neuropathy, and Foot Care: Standards of Care in Diabetes-2026', Diabetes Care 2026;49(Suppl 1):S261-S276, DOI 10.2337/dc26-S012, PMID 41358886 — texto integral conferido via PMC12690177 (europepmc.org), confirmando a Recomendação 12.19 (nível de evidência E): rastreio de sintomas e sinais de neuropatia autonômica a partir do diagnóstico de diabetes tipo 2 e 5 anos após o diagnóstico de diabetes tipo 1, repetido ao menos anualmente, com os cortes de hipotensão ortostática (queda de PAS > 20mmHg ou PAD > 10mmHg) e taquicardia de repouso (> 100bpm). Os cortes da bateria de testes de Ewing e a estratificação em NAC precoce/definida/grave pelo Consenso de Toronto foram conferidos contra Gogan A et al., J Clin Med. 2025;14(3):671, PMID 39941342, PMC11818907 (texto integral também conferido nesta produção), documento já citado em 'neuropatia-autonomica-cardiaca-diabetica-manifestacoes-testes-de-ewing-e-valor-prognostico.md' desta pasta. O ramo sobre não indicar rastreio sistemático de isquemia silenciosa apesar do risco aumentado por NAC reproduz a conclusão já documentada em 'rastreio-de-doenca-coronariana-assintomatica-no-diabetes-o-ensaio-diad.md' desta pasta (ensaio DIAD, PMID 19366774), sem busca de fonte nova para esse ramo específico. Nenhum PMID, DOI ou número foi inventado — todos os identificadores acima foram obtidos por busca e leitura do texto integral nesta produção."
source_refs: ["American Diabetes Association Professional Practice Committee for Diabetes. 12. Retinopathy, Neuropathy, and Foot Care: Standards of Care in Diabetes-2026. Diabetes Care. 2026;49(Suppl 1):S261-S276. DOI: 10.2337/dc26-S012. PMID: 41358886.", "Gogan A, Potre O, Avram V-F, Andor M, Caruntu F, Timar B. Cardiac Autonomic Neuropathy in Diabetes Mellitus: Pathogenesis, Epidemiology, Diagnosis and Clinical Implications: A Narrative Review. J Clin Med. 2025;14(3):671. DOI: 10.3390/jcm14030671. PMID: 39941342. PMC11818907 — já citado em 'neuropatia-autonomica-cardiaca-diabetica-manifestacoes-testes-de-ewing-e-valor-prognostico.md' desta pasta.", "Young LH, Wackers FJ, Chyun DA, Davey JA, Barrett EJ, Taillefer R, Heller GV, et al; DIAD Investigators. Cardiac outcomes after screening for asymptomatic coronary artery disease in patients with type 2 diabetes: the DIAD study: a randomized controlled trial. JAMA. 2009;301(15):1547-1555. DOI: 10.1001/jama.2009.476. PMID: 19366774 — já citado em 'rastreio-de-doenca-coronariana-assintomatica-no-diabetes-o-ensaio-diad.md' desta pasta."]
---

# Fluxograma: Investigação da Neuropatia Autonômica Cardiovascular no Diabético

Esta pasta já documenta os mecanismos da neuropatia autonômica cardíaca (NAC) —
manifestações, bateria de testes de Ewing e valor prognóstico — e o elo entre
hipoglicemia, prolongamento de QT e arritmia, mas faltava traduzir esse
conhecimento em um algoritmo de consultório: quem rastrear, quando suspeitar,
como confirmar e o que fazer depois de confirmada a NAC. Este fluxograma segue
a Recomendação 12.19 do Standards of Care in Diabetes—2026 da ADA para o
rastreio inicial e a estratificação do Consenso de Toronto para a bateria de
Ewing, e reforça — a partir do ensaio DIAD já documentado nesta pasta — que a
NAC não é, isoladamente, indicação para rastrear isquemia silenciosa de rotina.

## Árvore de decisão

```mermaid
flowchart TD
  R0["Pessoa com diabetes<br/>em consulta de rotina"] --> D1{"Atingiu o marco de início do<br/>rastreio de neuropatia autonômica?<br/>DM2: qualquer momento após o<br/>diagnóstico. DM1: 5 anos ou mais<br/>de diagnóstico (ADA 2026)"}

  D1 -->|"Ainda não atingiu o marco"| C1(["Sem indicação de rastreio<br/>sistemático agora; reavaliar no<br/>próximo marco (diagnóstico de<br/>DM2 ou 5 anos de DM1)"])

  D1 -->|"Atingiu o marco"| X1["Rastreio anual: perguntar sobre<br/>tontura postural, síncope, saciedade<br/>precoce, disfunção erétil, alteração<br/>da sudorese e pele seca ou<br/>rachada em extremidades; medir<br/>PA deitado e em pé e FC de repouso"]

  X1 --> D2{"Sintoma sugestivo relatado OU<br/>sinal anormal ao exame (hipotensão<br/>ortostática: queda de PAS ><br/>20mmHg ou PAD > 10mmHg; ou FC<br/>de repouso > 100bpm; ou pele<br/>seca/rachada)?"}

  D2 -->|"Não"| C2(["Rastreio negativo: repetir a<br/>avaliação clínica anualmente;<br/>nenhum teste adicional<br/>indicado agora"])

  D2 -->|"Sim"| X2["Suspeita clínica de neuropatia<br/>autonômica cardiovascular (NAC):<br/>solicitar a bateria de testes de Ewing"]

  X2 --> D3{"Resultado da bateria de Ewing<br/>(Consenso de Toronto): variação da<br/>FC ao respirar fundo (E/I), razão de<br/>Valsalva, razão 30:15 e queda<br/>ortostática de PA"}

  D3 -->|"Nenhum teste cardiovagal alterado"| C3(["NAC não confirmada agora; manter<br/>rastreio anual e otimizar controle<br/>glicêmico e fatores de risco<br/>cardiovascular"])

  D3 -->|"1 teste cardiovagal alterado<br/>(E/I < 10bpm OU Valsalva < 1,2<br/>OU razão 30:15 < 1,03)"| C4(["NAC precoce/potencial: repetir a<br/>bateria em 1 ano; reforçar o controle<br/>glicêmico e de fatores de risco<br/>cardiovascular"])

  D3 -->|"2 ou mais testes cardiovagais<br/>alterados, sem hipotensão<br/>ortostática"| X3["NAC definida confirmada"]

  D3 -->|"2 ou mais testes cardiovagais<br/>alterados COM hipotensão<br/>ortostática associada"| X4["NAC grave confirmada"]

  X3 --> D4{"Paciente vai iniciar programa de<br/>exercício estruturado ou cirurgia de<br/>médio/alto risco cardiovascular?"}

  D4 -->|"Sim"| C5(["Solicitar teste de estresse cardíaco<br/>antes de liberar o exercício ou a<br/>cirurgia; monitorar a resposta<br/>cronotrópica e pressórica; reforçar o<br/>risco perioperatório (maior<br/>necessidade de vasopressor, maior<br/>instabilidade hemodinâmica e térmica)"])

  D4 -->|"Não"| C6(["Sem indicação de teste de estresse<br/>agora; orientar sobre o risco de<br/>isquemia silenciosa e sobre sinais<br/>atípicos de síndrome coronariana<br/>aguda — rastreio sistemático de<br/>isquemia não reduziu eventos no<br/>diabético assintomático (DIAD)"])

  X4 --> D5{"Em uso de insulina ou<br/>sulfonilureia, OU antecedente de<br/>hipoglicemia grave?"}

  D5 -->|"Sim"| C7(["Risco arrítmico somado: hipoglicemia<br/>prolonga o QTc e a NAC grave já<br/>compromete a resposta autonômica;<br/>individualizar meta glicêmica menos<br/>rígida, priorizar fármacos com baixo<br/>risco de hipoglicemia e considerar<br/>monitorização contínua de glicose"])

  D5 -->|"Não"| C8(["Orientar sobre hipotensão ortostática<br/>(medidas posturais, hidratação,<br/>revisão de anti-hipertensivos), vigiar<br/>sinais de arritmia e encaminhar para<br/>avaliação cardiológica dirigida"])

  classDef conduta fill:#eef6ef,stroke:#2f7a4f,color:#12301f;
  class C1,C2,C3,C4,C5,C6,C7,C8 conduta;
```

A árvore separa dois momentos distintos. Primeiro, o **rastreio sistemático**
baseado em tempo de doença (Recomendação 12.19 da ADA 2026, nível de evidência
E), que não depende de sintomas e deve ser repetido ao menos uma vez por ano.
Segundo, a **confirmação diagnóstica** pela bateria de Ewing só quando o
rastreio for positivo — e a estratificação em NAC precoce, definida ou grave
determina condutas diferentes: da simples repetição anual até a indicação de
teste de estresse antes de liberar exercício ou cirurgia de risco, e o cuidado
redobrado com hipoglicemia em quem já tem NAC grave, pelo efeito somado sobre o
QTc. O fluxograma deixa explícito que NAC não é, isoladamente, gatilho para
rastrear isquemia silenciosa de rotina — o ensaio DIAD, já documentado nesta
pasta, mostrou que essa estratégia não reduz eventos cardíacos no diabético
assintomático.
