# Revisão adversarial 020/100 — MASLD e risco cardiovascular

Data: 29/08/2026  
Base auditada: `main` `59566e1196e0fa7f465df93516790ef454e1f565`  
Objeto: `doencas/fragmentos/zzz-codex-20260829-doenca-hepatica-metabolica-masld-e-risco-cardiovascular.json`  
Slug auditado: `doenca-hepatica-metabolica-masld-e-risco-cardiovascular`

## Objetivo

Revisão adversarial independente do hub MASLD-cardiovascular para detectar extrapolações potencialmente danosas: tratar MASLD como equivalente automático de ASCVD estabelecida, usar transaminases normais para excluir doença/fibrose, suspender estatina apenas por esteatose estável, prescrever incretínicos ou terapias de MASH a todo paciente com MASLD, ou confundir redução de risco metabólico/hepático com benefício cardiovascular demonstrado para uma terapia hepatoespecífica.

## Fontes primárias/diretrizes verificadas

1. European Association for the Study of the Liver (EASL), European Association for the Study of Diabetes (EASD), European Association for the Study of Obesity (EASO). Clinical Practice Guidelines on the management of metabolic dysfunction-associated steatotic liver disease (MASLD). *J Hepatol*. 2024;81:492-542. DOI: `10.1016/j.jhep.2024.04.031`. PMID: `38851997`.
2. Duell PB, Welty FK, Miller M, et al. Nonalcoholic Fatty Liver Disease and Cardiovascular Risk: A Scientific Statement From the American Heart Association. *Arterioscler Thromb Vasc Biol*. 2022. DOI: `10.1161/ATV.0000000000000153`.
3. Ndumele CE, Rodriguez F, Dixon DL, et al. 2026 AHA/ACC/ADA/ASN Guideline for the Prevention, Detection, Evaluation, and Management of Cardiovascular-Kidney-Metabolic Syndrome. *Circulation*. 2026. DOI: `10.1161/CIR.0000000000001453`.

## Perguntas adversariais e resultado

### 1. MASLD é tratada como ASCVD estabelecida por definição?

**Não.** O hub reconhece risco cardiovascular aumentado e agrupamento cardiometabólico, mas explicita que MASLD isolada não significa doença aterosclerótica clínica estabelecida. Prevenção primária e secundária permanecem distintas.

### 2. Transaminases normais são usadas para excluir MASLD ou fibrose?

**Não.** O texto registra corretamente que aminotransferases normais não excluem MASLD nem fibrose clinicamente relevante. A estratégia EASL-EASD-EASO 2024 é baseada em case-finding e estratificação não invasiva de fibrose, não em ALT isolada.

### 3. A estratégia de fibrose está coerente com EASL-EASD-EASO 2024?

**Sim.** O hub prioriza FIB-4 como primeira camada quando aplicável e teste de segunda linha, como elastografia, quando o risco inicial ou contexto clínico justificar. A atenção é maior em diabetes tipo 2 e obesidade com fatores metabólicos adicionais.

### 4. O hub recomenda suspender estatina por MASLD estável?

**Não.** Pelo contrário, preserva tratamento hipolipemiante quando existe indicação cardiovascular e evita confundir esteatose estável/elevação discreta de enzimas com hepatotoxicidade clinicamente relevante.

### 5. Semaglutida, tirzepatida ou cirurgia são prescritas automaticamente por MASLD?

**Não.** O hub condiciona terapias para obesidade/diabetes às indicações próprias e ao fenótipo cardiometabólico. Não transforma a presença de MASLD em indicação automática de incretínico ou cirurgia metabólica.

### 6. Terapias dirigidas a MASH são apresentadas como prevenção cardiovascular comprovada?

**Não.** O texto ressalta que terapias hepatoespecíficas, inclusive resmetirom quando aplicável à indicação hepatológica/regulatória, não devem ser usadas com objetivo primário de prevenção cardiovascular sem evidência de desfecho correspondente.

## Achados de segurança

- Manter MASLD como marcador/manifestação do continuum cardiometabólico, sem equipará-la automaticamente a ASCVD clínica.
- Não usar transaminases normais como regra de exclusão de fibrose.
- Não retirar estatina indicada por prevenção cardiovascular apenas por esteatose estável.
- Não extrapolar benefício metabólico, ponderal ou histológico para redução comprovada de MACE sem ensaio de desfecho específico.
- Diferenciar MASLD de hepatopatia congestiva em insuficiência cardíaca direita/descompensada.

## Tudo com Tudo

`related_document_slugs` permanece vazio no hub atual. A revisão não adicionou conexões sem slug clínico central explicitamente verificado, preservando a política contra relações inferidas.

## Decisão editorial

**Aprovado na revisão adversarial quanto aos domínios críticos auditados, sem mudança de conteúdo clínico.** Nenhum erro bloqueante foi encontrado. O `review_status` original foi mantido, preservando a revisão editorial humana futura.

## Validações estruturais

- Arquivo isolado em `docs/`; alterações somente aditivas.
- Nenhum JSON clínico, schema, loader ou regra determinística modificado.
- Nenhum slug ou relação Tudo com Tudo criado.
- EASL-EASD-EASO 2024 confirmado: DOI `10.1016/j.jhep.2024.04.031`, PMID `38851997`.
- Diretriz CKM 2026 confirmada: DOI `10.1161/CIR.0000000000001453`.
- Sem necessidade de teste dependente de PostgreSQL.
