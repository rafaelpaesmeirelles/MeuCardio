# CorVIA — pacote 100/100

## BARI 2D: revascularização imediata versus terapia médica intensiva no diabetes tipo 2 com DAC estável

**Tipo de pacote:** revisão adversarial independente / fechamento de gap de segurança interpretativa.  
**Escopo:** documento isolado em `docs/`; não altera conteúdo canônico, slugs, relações Tudo com Tudo, regras assistivas, schema ou runtime.

## Pergunta clínica

Em pacientes com diabetes mellitus tipo 2 e doença coronariana estável passível de revascularização, uma estratégia de revascularização coronariana imediata adicionada à terapia médica intensiva melhora sobrevida ou reduz eventos cardiovasculares maiores quando comparada à terapia médica intensiva inicialmente?

## Fonte primária verificada

- BARI 2D Study Group; Frye RL, August P, Brooks MM, et al. *A Randomized Trial of Therapies for Type 2 Diabetes and Coronary Artery Disease*. N Engl J Med. 2009;360:2503-2515.
- PMID: `19502645`.
- PMCID: `PMC2863990`.
- DOI: `10.1056/NEJMoa0805796`.
- ClinicalTrials.gov: `NCT00006305`.
- PubMed: https://pubmed.ncbi.nlm.nih.gov/19502645/
- DOI: https://doi.org/10.1056/NEJMoa0805796

## População e desenho

- Ensaio randomizado com **2.368 pacientes** com DM2 e cardiopatia isquêmica estável.
- Estratégia coronariana: **revascularização imediata + terapia médica intensiva** versus **terapia médica intensiva com revascularização diferida se clinicamente necessária**.
- Houve também randomização metabólica para estratégia de **sensibilização à insulina** versus **provisão de insulina**.
- Antes da randomização, o médico determinava se **PCI ou CABG** seria a modalidade de revascularização mais apropriada; a randomização coronariana foi estratificada por essa escolha.
- Desfechos primários: **mortalidade total** e **composto de morte, IAM ou AVC**.

## Resultados principais que podem ser afirmados

Em 5 anos:

- sobrevida: **88,3%** com revascularização imediata versus **87,8%** com terapia médica, `p=0,97`;
- ausência de eventos cardiovasculares maiores: **77,2%** versus **75,9%**, `p=0,70`;
- não houve diferença significativa global em morte ou MACE entre revascularização imediata e estratégia clínica inicial.

A randomização metabólica também não demonstrou diferença significativa de sobrevida entre sensibilização à insulina e provisão de insulina no ensaio principal.

## A nuance crítica do estrato de revascularização

O BARI 2D **não foi um ensaio head-to-head de PCI versus CABG**. A modalidade considerada apropriada foi definida **antes** da randomização e os pacientes dos estratos tinham anatomia e risco distintos.

No estrato em que **PCI** havia sido escolhida como modalidade apropriada, não houve diferença significativa dos endpoints primários entre revascularização imediata e terapia médica.

No estrato em que **CABG** havia sido escolhida como modalidade apropriada, houve redução de eventos cardiovasculares maiores com revascularização imediata, resultado impulsionado principalmente por menos IAM; no relatório principal, MACE ocorreu em aproximadamente **22,4% versus 30,5%** (`p=0,01`). Esse achado deve ser preservado, mas não transformado em comparação randomizada CABG-versus-PCI.

## Revisão adversarial: interpretações que o CorVIA deve bloquear

1. **“Revascularização nunca beneficia pacientes diabéticos com DAC estável.” — Incorreto.** O resultado global foi neutro, mas o estrato previamente selecionado para CABG apresentou sinal clínico relevante em MACE.
2. **“BARI 2D prova que CABG é superior à PCI.” — Incorreto.** CABG e PCI não foram randomizados entre si; a escolha do estrato ocorreu antes da randomização e refletia diferenças anatômicas e clínicas.
3. **“Todo diabético com DAC multiarterial deve ser operado com base no BARI 2D.” — Incorreto.** O achado do estrato CABG precisa ser integrado à anatomia, complexidade coronariana, risco cirúrgico, sintomas, função ventricular e evidência contemporânea.
4. **“Estratégia clínica inicial significa proibir revascularização posteriormente.” — Incorreto.** O braço clínico permitia revascularização diferida quando clinicamente indicada.
5. **“Os resultados metabólicos do BARI 2D definem a terapia antidiabética de 2026.” — Incorreto.** O ensaio antecede a evidência contemporânea de iSGLT2, agonistas de GLP-1 e outras estratégias cardiorrenais; sua randomização metabólica é historicamente importante, mas não deve substituir diretrizes atuais.
6. **“A tecnologia de PCI e CABG do período representa integralmente a prática contemporânea.” — Incorreto.** A validade externa deve considerar evolução de stents, técnicas cirúrgicas, fisiologia coronariana, imagem, prevenção secundária e terapias antidiabéticas.

## Integração com a evidência contemporânea

O BARI 2D permanece útil para três princípios:

- separar **estratégia inicial** de revascularização de uma proibição permanente de intervenção;
- não tratar diabetes como indicação automática de PCI;
- reconhecer que anatomia e modalidade de revascularização modificam a interpretação dos desfechos, sem promover análises estratificadas a uma comparação randomizada que não ocorreu.

Contexto normativo contemporâneo:

- **ESC 2024 Guidelines for the management of chronic coronary syndromes** — DOI `10.1093/eurheartj/ehae177`.
- **AHA/ACC/ACCP/ASPC/NLA/PCNA Chronic Coronary Disease Guideline 2023** — DOI `10.1161/CIR.0000000000001168`.
- **Diretriz de Síndrome Coronariana Crônica da SBC 2025** — PMID `41294178`; DOI `10.36660/abc.20250619`.

Nenhuma classe de recomendação ou nível de evidência é reproduzido neste pacote sem cotejo direto da tabela normativa específica.

## Limites de validade externa

- não aplicar mecanicamente a síndrome coronariana aguda, choque ou instabilidade;
- não usar o estudo como substituto para ensaios específicos de DAC multiarterial contemporânea ou para comparações randomizadas CABG-versus-PCI;
- não transportar a estratégia glicêmica do ensaio para a farmacoterapia atual do DM2;
- não ignorar a heterogeneidade anatômica entre os estratos PCI e CABG;
- não transformar neutralidade do resultado global em equivalência individual para qualquer anatomia coronariana.

## Conclusão operacional

**Guardrail CorVIA:** em DM2 com DAC estável, o BARI 2D não sustenta revascularização imediata universal para melhorar sobrevida ou MACE. Também não sustenta a afirmação oposta de que revascularização é prognosticamente irrelevante em todos os diabéticos. A anatomia, a modalidade considerada apropriada e a evidência contemporânea devem ser integradas, preservando a neutralidade global e a nuance do estrato CABG sem falsa comparação PCI-versus-CABG.

## Validação deste pacote

- PMID/PMCID/DOI/NCT verificados na fonte primária;
- população, desenho fatorial, estratificação, endpoints e resultados principais conferidos;
- distinção entre análise global e estrato CABG explicitada;
- nenhuma classe/nível de diretriz inventado;
- nenhum slug ou relação Tudo com Tudo criado;
- nenhuma dose ou prescrição automática criada;
- nenhum arquivo compartilhado/canônico alterado.
