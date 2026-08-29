# Revisão adversarial 021/100 — doença tireoidiana e risco cardiovascular

Data: 29/08/2026  
Base auditada: `main` `59566e1196e0fa7f465df93516790ef454e1f565`  
Objeto: `doencas/fragmentos/zzz-codex-20260829-doenca-tireoidiana-e-risco-cardiovascular.json`  
Slug auditado: `doenca-tireoidiana-e-risco-cardiovascular`

## Objetivo

Revisão adversarial independente das interações tireoide-coração, priorizando risco de iatrogenia: atribuir arritmia à tireoide sem confirmação hormonal, tratar todo hipotireoidismo subclínico do idoso com levotiroxina, ignorar risco de fibrilação atrial no hipertireoidismo subclínico com TSH persistentemente suprimido, converter associação tireoidiana em regra própria de anticoagulação e atribuir classes/níveis de recomendação não conferidos.

## Fontes primárias/diretrizes verificadas

1. Van Gelder IC, Rienstra M, Bunting KV, et al. 2024 ESC Guidelines for the management of atrial fibrillation. *Eur Heart J*. 2024;45:3314-3414.
2. Ross DS, Burch HB, Cooper DS, et al. 2016 American Thyroid Association Guidelines for Diagnosis and Management of Hyperthyroidism and Other Causes of Thyrotoxicosis. *Thyroid*. 2016;26:1343-1421. DOI: `10.1089/thy.2016.0229`.
3. Jonklaas J, Bianco AC, Bauer AJ, et al. Guidelines for the Treatment of Hypothyroidism. *Thyroid*. 2014;24:1670-1751. DOI: `10.1089/thy.2014.0028`.
4. Biondi B, Bartalena L, Cooper DS, et al. 2015 European Thyroid Association Guidelines on Diagnosis and Treatment of Endogenous Subclinical Hyperthyroidism. *Eur Thyroid J*. 2015;4:149-163.
5. Stott DJ, Rodondi N, Kearney PM, et al. Thyroid Hormone Therapy for Older Adults with Subclinical Hypothyroidism (TRUST). *N Engl J Med*. 2017;376:2534-2544. DOI: `10.1056/NEJMoa1603825`. PMID: `28402245`.

## Perguntas adversariais e resultado

### 1. O hub atribui fibrilação atrial ou insuficiência cardíaca à tireoide sem confirmação laboratorial?

**Não.** TSH e T4 livre são tratados como base da confirmação, e o hub reconhece que doença aguda, fármacos e síndrome do eutireoidiano doente podem alterar testes. A manifestação cardiovascular deve ser tratada em paralelo e não aguardar explicação endócrina definitiva.

### 2. Todo idoso com hipotireoidismo subclínico é tratado com levotiroxina?

**Não.** O hub usa o TRUST de forma adequada: em adultos ≥65 anos com hipotireoidismo subclínico persistente, levotiroxina não demonstrou benefício aparente nos desfechos sintomáticos principais. O resultado não é extrapolado para hipotireoidismo manifesto nem para todos os subgrupos clínicos.

### 3. O hipertireoidismo subclínico é tratado como condição inócua?

**Não.** O texto preserva a recomendação da ETA 2015 de tratar pacientes >65 anos com TSH persistentemente <0,1 mUI/L e considerar tratamento quando TSH está entre 0,1 e 0,39 mUI/L, particularmente pelo risco de fibrilação atrial. A revisão não converte essa recomendação específica em uma classe ESC cardiovascular inexistente.

### 4. A presença de tireotoxicose cria uma regra de anticoagulação própria?

**Não.** O hub orienta que anticoagulação em fibrilação atrial seja decidida pelo risco tromboembólico/hemorrágico e pelas diretrizes de FA, em vez de usar a tireotoxicose isoladamente como indicação ou contraindicação automática.

### 5. Emergências endócrinas e cardiovasculares são separadas corretamente?

**Sim.** Tempestade tireotóxica e coma mixedematoso são tratados como emergências específicas; FA instável, SCA, edema agudo de pulmão, tamponamento ou bradicardia/bloqueio avançado seguem manejo cardiovascular urgente em paralelo.

### 6. O texto inventa classe/nível da ESC para doença tireoidiana?

**Não.** Não foi encontrada atribuição de classe/nível ESC não confirmada. As recomendações endocrinológicas são identificadas pela sociedade/documento de origem.

## Achados de segurança

- Confirmar disfunção tireoidiana antes de atribuir causalidade a arritmia, IC ou dislipidemia.
- Não extrapolar TRUST para hipotireoidismo manifesto ou para todo adulto mais jovem.
- Evitar excesso de levotiroxina e supressão iatrogênica de TSH em idosos pelo risco de FA e outros efeitos adversos.
- No uso de amiodarona, distinguir hipotireoidismo de tireotoxicose tipo 1, tipo 2 ou mista antes de escolher tratamento.
- Não deixar tratamento da tireoide atrasar cardioversão ou manejo de uma síndrome cardiovascular instável.

## Limitação explicitada

As diretrizes tireoidianas específicas citadas são anteriores à ESC AF 2024; nesta revisão foi confirmada a coerência das recomendações reproduzidas e do RCT TRUST, mas **não se afirma que cada documento endocrinológico citado seja a publicação mais recente de sua sociedade** sem uma atualização formal específica confirmada. Esta limitação impede atualização artificial de classe/nível.

## Decisão editorial

**Aprovado na revisão adversarial dos pontos críticos, sem alteração do conteúdo clínico.** Nenhum erro bloqueante foi identificado. O `review_status` foi preservado e nenhuma decisão humana de publicação foi substituída.

## Validações estruturais

- Revisão documental isolada e aditiva.
- Nenhum JSON clínico ou schema alterado.
- Nenhum novo slug ou relação Tudo com Tudo criado.
- TRUST confirmado: DOI `10.1056/NEJMoa1603825`, PMID `28402245`.
- Nenhuma classe cardiovascular nova inferida de diretriz endocrinológica.
- Sem necessidade de suíte dependente de PostgreSQL.
