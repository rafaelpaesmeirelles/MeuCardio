# Revisão adversarial 019/100 — doença carotídea aterosclerótica e CREST-2

Data: 29/08/2026  
Base auditada: `main` `59566e1196e0fa7f465df93516790ef454e1f565`  
Objeto: `doencas/fragmentos/zzz-codex-20260829-doenca-carotidea-aterosclerotica.json`  
Slug auditado: `doenca-carotidea-aterosclerotica`

## Objetivo

Revisão adversarial de alto risco para evitar quatro erros frequentes: chamar estenose carotídea de sintomática por sintomas não focais, converter percentuais por métodos diferentes sem explicitar NASCET, transformar resultado pós-diretriz do CREST-2 em nova classe formal de recomendação e vender benefício de um dos braços do CREST-2 como evidência equivalente para endarterectomia e stent.

## Fontes primárias/diretrizes verificadas

1. 2024 ESC Guidelines for the management of peripheral arterial and aortic diseases. *Eur Heart J*. 2024. Documento oficial ESC; recomendações de doença carotídea sintomática e assintomática usadas no hub.
2. Kleindorfer DO, Towfighi A, Chaturvedi S, et al. 2021 Guideline for the Prevention of Stroke in Patients With Stroke and Transient Ischemic Attack. *Stroke*. 2021. Documento AHA/ASA.
3. CREST-2 Investigators. Medical Management and Revascularization for Asymptomatic Carotid Stenosis. *N Engl J Med*. 2026;394:219-231. DOI: `10.1056/NEJMoa2508800`. PMID: `41269206`.

## Perguntas adversariais e resultado

### 1. O hub chama tontura, vertigem ou síncope isoladas de doença carotídea sintomática?

**Não.** A definição exige evento isquêmico focal cerebral ou retinal ipsilateral atribuível ao território carotídeo. Sintomas não focais isolados não transformam automaticamente uma estenose em sintomática.

### 2. O método de quantificação da estenose é tratado como intercambiável?

**Não.** O hub orienta quantificação por método validado compatível com NASCET e adverte contra misturar percentuais obtidos por técnicas distintas sem explicitar o método.

### 3. Os resultados do CREST-2 foram reproduzidos corretamente?

**Sim.** O estudo foi composto por dois ensaios paralelos em pacientes com estenose carotídea assintomática de alto grau (≥70%). No ensaio de stent, o desfecho primário cumulativo em 4 anos foi 2,8% com stent + tratamento médico intensivo versus 6,0% com tratamento médico intensivo isolado (`p=0,02`). No ensaio de endarterectomia, foi 3,7% versus 5,3% (`p=0,24`). O hub preserva a diferença estatística entre os dois ensaios e não declara benefício demonstrado da endarterectomia nesse estudo.

### 4. O desfecho primário do CREST-2 foi reduzido a AVC perioperatório isolado?

**Não.** A interpretação mantém o composto que inclui AVC ou morte peri-procedimento e AVC isquêmico ipsilateral no seguimento. Não é correto reduzir o resultado a apenas uma janela procedural.

### 5. O hub cria uma nova classe ESC a partir do CREST-2?

**Não.** Este é o principal guardrail. O CREST-2 foi publicado depois da diretriz ESC 2024. O hub o incorpora como atualização de evidência e declara explicitamente que seus achados **não devem ser convertidos automaticamente em uma nova classe de recomendação**.

### 6. A doença sintomática continua priorizando tempo e risco procedural?

**Sim.** O hub preserva a lógica de benefício mais robusto da endarterectomia em estenose sintomática de alto grau, a importância de intervenção precoce em pacientes apropriados e a necessidade de incorporar risco procedural do centro, tamanho do infarto, estabilidade neurológica e risco hemorrágico.

## Achados de segurança

- Não revascularizar doença assintomática apenas pelo percentual anatômico.
- Não transformar um resultado positivo do ensaio de stent do CREST-2 em prova de benefício de toda estratégia de revascularização.
- Não atribuir causalidade carotídea a AVC/AIT sem considerar FA e outras fontes cardioembólicas.
- Não atrasar trombólise/trombectomia no AVC agudo por investigação carotídea eletiva.
- Manter explícito que CREST-2 é evidência posterior às recomendações formais ESC 2024.

## Tudo com Tudo

Os dois `related_document_slugs` já existentes no hub — reconhecimento de déficit neurológico focal súbito e fluxograma da primeira hora do AVC — têm vínculo clínico direto com a apresentação sintomática. Esta revisão não adicionou relações novas.

## Decisão editorial

**Revisão adversarial aprovada.** Nenhum erro bloqueante foi encontrado nos pontos auditados. O hub já estava marcado como `revisado`; esta auditoria independente não altera esse estado nem cria nova recomendação formal.

## Validações estruturais

- Pacote exclusivamente documental e aditivo.
- Nenhuma alteração no JSON do hub.
- Nenhum novo slug ou relação criada.
- CREST-2 confirmado: DOI `10.1056/NEJMoa2508800`, PMID `41269206`.
- População e dois ensaios paralelos mantidos distintos.
- Sem teste de PostgreSQL necessário para revisão sem mudança de runtime.
