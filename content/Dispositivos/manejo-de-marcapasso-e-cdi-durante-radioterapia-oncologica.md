---
title: "Manejo de Marca-passo e CDI durante Radioterapia Oncológica"
slug: manejo-de-marcapasso-e-cdi-durante-radioterapia-oncologica
theme: "Dispositivos"
kind: protocolo
review_status: revisado
source_refs: ["Chan MF, Young C, Gelblum D, et al. A Review and Analysis of Managing Commonly Seen Implanted Devices for Patients Undergoing Radiation Therapy. Adv Radiat Oncol. 2021;6(4):100732. DOI: 10.1016/j.adro.2021.100732. PMCID: PMC8361059. PMID: 34409216", "Miften M, Mihailidis D, Kry SF, et al. Management of radiotherapy patients with implanted cardiac pacemakers and defibrillators: A Report of the AAPM TG-203. Med Phys. 2019;46(12):e757-e788. DOI: 10.1002/mp.13838. PMID: 31571229", "Indik JH, Gimbel JR, Abe H, et al. 2017 HRS expert consensus statement on magnetic resonance imaging and radiation exposure in patients with cardiovascular implantable electronic devices. Heart Rhythm. 2017;14(7):e97-e153. DOI: 10.1016/j.hrthm.2017.04.025. PMID: 28502708", "Grant JD, Jensen GL, Tang C, et al. Radiotherapy-Induced Malfunction in Contemporary Cardiovascular Implantable Electronic Devices: Clinical Incidence and Predictors. JAMA Oncol. 2015;1(5):624-632. DOI: 10.1001/jamaoncol.2015.1787. PMID: 26181143", "Gomez DR, Poenisch F, Pinnix CC, et al. Malfunctions of implantable cardiac devices in patients receiving proton beam therapy: incidence and predictors. Int J Radiat Oncol Biol Phys. 2013;87(3):570-575. DOI: 10.1016/j.ijrobp.2013.07.010. PMCID: PMC3931127. PMID: 24074931", "Gelblum DY, Amols H. Implanted cardiac defibrillator care in radiation oncology patient population. Int J Radiat Oncol Biol Phys. 2009;73(5):1525-1531. DOI: 10.1016/j.ijrobp.2008.06.1903. PMID: 18977096"]
legacy_source: "Documento novo — lacuna real na pasta Dispositivos, conferida por grep antes de escrever: os 43 documentos existentes cobrem RM em portador de CIED (registro MAGNASAFE) e manejo perioperatório de cirurgia não cardíaca, mas nenhum cobre o problema fisicamente distinto de radioterapia oncológica (dano cumulativo por radiação ionizante e produção de nêutrons em feixes de alta energia, não campo magnético estático). Verificado nesta sessão via E-utilities do PubMed: a declaração de consenso primária da HRS (PMID 28502708) e o relatório técnico da AAPM TG-203 (PMID 31571229) não têm resumo estruturado com os limiares numéricos no PubMed — os valores de dose/energia deste documento vêm da revisão de acesso aberto de Chan MF et al. 2021 (PMC8361059, texto integral lido nesta sessão), que cita e resume ambos os documentos primários; e do estudo retrospectivo original de Grant JD et al. (JAMA Oncol 2015, PMID 26181143), cujo resumo estruturado foi lido na íntegra e confere com o que a revisão de Chan et al. relata sobre ele."
---

# Manejo de Marca-passo e CDI durante Radioterapia Oncológica

## Definicao

Documento novo na pasta — complementa, sem sobrepor, o já existente sobre ressonância magnética em portador de marca-passo/CDI (registro MAGNASAFE) e o de manejo perioperatório de dispositivo cardíaco em cirurgia não cardíaca. O risco da radioterapia oncológica a um dispositivo cardíaco implantável eletrônico (CIED — marca-passo, CDI, TRC) é **fisicamente distinto** dos dois: não é campo magnético estático nem bisturi elétrico intraoperatório, é **radiação ionizante cumulativa** incidindo sobre o circuito eletrônico do gerador ao longo de semanas de fracionamento, com um mecanismo de dano adicional específico de feixes de fóton de alta energia — a produção de nêutrons secundários.

**Por que isso é cada vez mais frequente na prática**: paciente com CIED e câncer que precisa de radioterapia não é situação rara — a mesma população que acumula dispositivo cardíaco (idade avançada, doença cardiovascular) tem incidência de câncer elevada, e a superposição só cresce.

## Mecanismo do dano

Dois mecanismos, com limiares diferentes (conferido no texto integral de Chan MF et al. 2021, PMC8361059, que resume o relatório técnico AAPM TG-203 — PMID 31571229 — e o consenso HRS 2017 — PMID 28502708):

- **Dano cumulativo por dose direta ao circuito (CMOS)**: os circuitos modernos toleram doses relativamente altas antes de dano permanente, mas um limite de dose total ao próprio gerador de **2 Gy** é o valor prático mais citado na literatura como referência de segurança.
- **Single-event upset (reset, perda de dados, alteração de parâmetro) por produção de nêutrons secundários**: ocorre especificamente com feixes de fóton de **alta energia (≥10 MV)** — a interação do feixe com estruturas do acelerador/paciente gera nêutrons que perturbam a memória do circuito, independentemente da dose absorvida pelo dispositivo. Feixes de baixa energia (6 MV), elétrons e Gamma Knife **não produzem nêutrons** relevantes nesse sentido.

## Estratificacao de risco — aapm tg-203

A AAPM TG-203 categoriza o paciente em **baixo, médio ou alto risco**, combinando três eixos (via Chan et al. 2021, que resume o relatório original — o texto integral do TG-203 não foi lido diretamente nesta sessão, e essa atribuição fica registrada):
1. **Dose cumulativa estimada ao CIED**: <2 Gy, 2-5 Gy, ou >5 Gy;
2. **Dependência de estimulação** (paciente pacing-dependente vs. não dependente);
3. **Presença ou não de feixe produtor de nêutrons** (≥10 MV).

Consequência prática de manejo por categoria de risco, também via a mesma revisão: paciente de **baixo e médio risco com CIED** — verificação semanal do dispositivo durante o curso de radioterapia; paciente de **alto risco** — avaliação do dispositivo em até 24 horas após cada fração. Todos os fabricantes recomendam realocar o gerador para fora do campo de radiação quando possível, mas essa realocação pode não ser necessária quando a dose cumulativa estimada for **<5 Gy**.

## Evidencia real de incidencia — o estudo de grant et al., jama oncol 2015

Grant JD et al. (JAMA Oncol. 2015;1(5):624-632, PMID 26181143), análise retrospectiva de **249 cursos de radioterapia com fóton/elétron em 215 pacientes** com CIED funcionante (123 marca-passos [57%], 92 CDI [43%]) num único centro acadêmico, agosto/2005 a janeiro/2014, com dados de interrogação do dispositivo pós-radioterapia:

- **Mau funcionamento do CIED atribuível à radioterapia: 7% dos cursos (18/249)** — 15 casos de single-event upset (perda de dado, reset de parâmetro, reset não recuperável) e 3 de interferência de sinal transitória.
- **Todos os single-event upsets ocorreram em cursos com produção substancial de nêutrons** (feixes de 15 ou 18 MV): taxa de **21% por curso produtor de nêutrons** para o conjunto de CIEDs, **10% especificamente para marca-passo** e **34% especificamente para CDI**.
- **Zero single-event upset entre os 178 cursos sem produção de nêutrons** (elétrons, Gamma Knife ou 6 MV) — diferença absoluta que sustenta diretamente a recomendação de preferir feixe de baixa energia sempre que clinicamente viável.
- **A dose incidente no CIED não se correlacionou com mau funcionamento**, em doses observadas até **5,4 Gy** — achado que, segundo os autores, permite reduzir procedimentos invasivos de realocação do dispositivo nesse cenário de dose.
- **Tratamento em região de abdome e pelve foi fator de risco independente** para single-event upset (HR 5,2; IC95% 1,2-22,6; p=0,03).
- **Seis pacientes com reset de parâmetro desenvolveram sintoma clínico**: 3 com hipotensão e/ou bradicardia, 2 com "tique" torácico anormal compatível com síndrome do marca-passo, 1 evoluiu com insuficiência cardíaca congestiva. As 3 interferências de sinal transitórias não tiveram repercussão clínica. Nenhum mau funcionamento tardio foi diretamente atribuído à radioterapia.

## Serie clinica anterior — gelblum e amols, 2009

Gelblum DY, Amols H (Int J Radiat Oncol Biol Phys. 2009;73(5):1525-1531, PMID 18977096), série de **33 pacientes com CDI** tratados com radioterapia num centro de câncer ao longo de 2,5 anos: **1 paciente** apresentou reset do dispositivo para configuração de fábrica, percebido pelo próprio paciente por sinal sonoro do gerador — tratado originalmente com feixe de **15 MV**. Após o evento, o serviço reprogramou a conduta institucional para tratar esses pacientes preferencialmente com **6 MV**, e não houve novo evento subsequente na série. É a mesma lógica que, seis anos depois, o estudo maior de Grant et al. confirmou com poder estatístico: energia do feixe, não dose, é o determinante principal do risco de reset.

## Radioterapia com proton — cautela adicional

O feixe de prótons acrescenta um mecanismo de risco que o de fóton convencional não tem: o sistema de varredura por *pencil beam* gera um **campo magnético relativamente forte ao redor do paciente**, que pode induzir mau funcionamento do CIED **independentemente da dose** de radiação propriamente dita (via Chan et al. 2021).

**Dado real de incidência** — Gomez DR et al. (Int J Radiat Oncol Biol Phys. 2013;87(3):570-575, PMID 24074931, PMCID PMC3931127): **42 pacientes com CIED** (28 marca-passos, 14 CDI) tratados com radioterapia de prótons entre março/2009 e julho/2012, sendo **23 (55%) por tumor torácico**. Seis eventos de mau funcionamento em 5 pacientes — 5 resets do dispositivo e 1 indicador de troca eletiva de gerador não relacionado à radiação. **Todos os resets ocorreram em pacientes tratados com radioterapia de prótons torácica**, com incidência de aproximadamente **20% entre os pacientes torácicos** — nenhum reset fora desse subgrupo. Todos os resets foram corrigidos sem intercorrência clínica. **Conclusão dos próprios autores, citada verbatim na tradução**: recomenda-se evitar radioterapia de prótons em paciente pacing-dependente, e acompanhar de perto qualquer paciente com CIED submetido a radioterapia de prótons torácica.

**Consequência prática**: em paciente **pacing-dependente**, a recomendação geral (via Chan et al. 2021, refletindo a cautela de múltiplas fontes) é **evitar** radioterapia de prótons quando houver alternativa — especialmente em centros com recursos limitados de suporte cardiológico durante o tratamento. Em paciente não pacing-dependente, o risco deve ser avaliado individualmente antes de iniciar.

## Manejo pratico, resumido

- **Antes de iniciar**: contato com o cardiologista/eletrofisiologista responsável para confirmar interrogação recente do dispositivo e o grau de dependência do paciente à estimulação; planejamento de campo que evite o gerador sempre que possível.
- **Escolha de energia**: preferir feixes que não produzam nêutrons (elétrons, Gamma Knife, fóton de 6 MV) sempre que a técnica permitir; reservar feixe ≥10 MV para quando for clinicamente indispensável, sabendo que é o principal determinante do risco de reset agudo.
- **Frequência de verificação do dispositivo durante o tratamento**: proporcional à categoria de risco (semanal em baixo/médio risco; até 24h após cada fração em alto risco), conforme a estratificação AAPM TG-203 resumida acima.
- **Disponibilidade de equipamento de emergência e magneto** durante as sessões em paciente de maior risco, e coordenação multidisciplinar entre radioterapeuta, físico médico e cardiologista.
- **Radioterapia de prótons**: tratar como cenário de cautela adicional, não como equivalente ao fóton convencional — mecanismo de risco (campo magnético do sistema de varredura) é diferente, e a evidência disponível é de séries pequenas com sinal consistente de risco em tratamento torácico.

## O que este documento nao cobre

- Ressonância magnética em portador de CIED — ver o documento já existente sobre o registro MAGNASAFE nesta mesma pasta; mecanismo de risco (campo magnético estático/gradiente) é diferente do de radiação ionizante.
- Interferência eletromagnética intraoperatória (bisturi elétrico) — ver o documento de manejo perioperatório de marca-passo/CDI em cirurgia não cardíaca.
- Exposição a exames de imagem diagnóstica (tomografia computadorizada, PET-CT) — a dose ao dispositivo nesse contexto é ordens de grandeza menor que a de um curso terapêutico fracionado, e não é o objeto deste documento.
- Detalhamento técnico de física médica (cálculo dosimétrico ao gerador, algoritmos de planejamento) — este documento resume a lógica clínica de manejo, não o procedimento de física médica em si.
