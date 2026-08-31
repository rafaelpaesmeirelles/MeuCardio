# Revisão adversarial 017/100 — DPOC e risco cardiovascular

Data: 29/08/2026  
Base auditada: `main` `59566e1196e0fa7f465df93516790ef454e1f565`  
Objeto: `doencas/fragmentos/zzz-codex-20260829-dpoc-e-risco-cardiovascular.json`  
Slug auditado: `dpoc-e-risco-cardiovascular`

## Objetivo

Revisão científica independente do hub de DPOC sob a ótica cardiovascular, procurando especificamente erros com potencial de dano: atribuir toda dispneia à doença pulmonar, retirar betabloqueador indicado por doença cardiovascular, extrapolar o BLOCK-COPD para pacientes com indicação cardiovascular de betabloqueio, transformar associação epidemiológica em causalidade ou criar recomendações não presentes nas diretrizes.

## Fontes primárias/diretrizes verificadas

1. Global Initiative for Chronic Obstructive Lung Disease (GOLD). *Global Strategy for Prevention, Diagnosis and Management of COPD — 2026 Report*. Documento oficial GOLD 2026. URL oficial: https://goldcopd.org/2026-gold-report-and-pocket-guide/
2. Visseren FLJ, Mach F, Smulders YM, et al. 2021 ESC Guidelines on cardiovascular disease prevention in clinical practice. *Eur Heart J*. 2021;42:3227-3337. DOI: `10.1093/eurheartj/ehab484`. PMID: `34458905`.
3. Dransfield MT, Voelker H, Bhatt SP, et al. Metoprolol for the Prevention of Acute Exacerbations of COPD. *N Engl J Med*. 2019;381:2304-2314. DOI: `10.1056/NEJMoa1908142`. PMID: `31633896`.

## Perguntas adversariais e resultado

### 1. O hub usa BLOCK-COPD para proibir betabloqueador em qualquer paciente com DPOC?

**Não.** O texto preserva a população real do ensaio: pessoas com DPOC e risco aumentado de exacerbação **sem indicação estabelecida para betabloqueador**. O estudo não testou a retirada de betabloqueador de pacientes com insuficiência cardíaca, doença coronariana ou outra indicação cardiovascular formal.

A formulação do hub — não iniciar metoprolol apenas para prevenir exacerbações de DPOC, mas não retirar terapia cardiovascular comprovada apenas pelo rótulo de DPOC — é coerente com o GOLD 2026 e com o desenho do BLOCK-COPD.

### 2. O desfecho do BLOCK-COPD foi vendido como benefício ou como contraindicação absoluta?

**Não.** O ensaio não mostrou prolongamento do tempo até a primeira exacerbação e observou mais exacerbações que levaram à hospitalização no grupo metoprolol. O hub usa esse achado para a situação estudada, sem converter o resultado em contraindicação universal ao betabloqueio.

### 3. A dispneia aguda é atribuída automaticamente à DPOC?

**Não.** O hub exige investigação paralela de insuficiência cardíaca, síndrome coronariana aguda, arritmia, pneumonia e tromboembolismo pulmonar. Isso fecha um gap de segurança importante porque sibilância e DPOC conhecida não excluem edema pulmonar ou outras causas cardiovasculares.

### 4. O hub cria classe/nível de recomendação não confirmado?

**Não.** Não foi identificada classe ESC/GOLD inventada. As recomendações operacionais são descritas como condutas clínicas, e o ensaio BLOCK-COPD é citado com população e finalidade compatíveis.

### 5. Há vínculo Tudo com Tudo potencialmente órfão ou não verificado?

**Não.** `related_document_slugs` permanece vazio no hub atual. A revisão adversarial não adiciona relações por inferência. Isso é deliberadamente conservador e evita criar conexão apenas por proximidade temática.

## Achados de segurança

- Manter explícita a diferença entre **não usar betabloqueador para prevenir exacerbação de DPOC sem indicação cardiovascular** e **não negar betabloqueador quando existe indicação cardiovascular independente**.
- Manter investigação cardiovascular na piora aguda da dispneia, especialmente IC, SCA, arritmia e TEP.
- Não extrapolar o BLOCK-COPD para outras moléculas, para pacientes com indicação cardiovascular formal ou para desfechos de mortalidade que o ensaio não demonstrou.
- A afirmação de que DPOC aumenta carga de doença cardiovascular é epidemiologicamente plausível e coerente com diretrizes, mas não deve ser usada isoladamente para diagnosticar ASCVD/IC/FA em um indivíduo.

## Decisão editorial

**Aprovado na revisão adversarial quanto à coerência científica, sem alteração do conteúdo clínico.** Nenhum erro bloqueante foi encontrado. O `review_status` original não foi modificado, preservando a decisão editorial humana. Nenhum slug, schema, loader, regra determinística ou monólito foi alterado.

## Validações estruturais

- Arquivo de revisão isolado e aditivo.
- Nenhuma mudança em JSON clínico.
- Nenhum novo slug criado.
- Nenhuma relação Tudo com Tudo adicionada sem resolução explícita.
- DOI/PMID do BLOCK-COPD conferidos: `10.1056/NEJMoa1908142` / `31633896`.
- Sem necessidade de suíte dependente de PostgreSQL para este pacote documental de revisão.
