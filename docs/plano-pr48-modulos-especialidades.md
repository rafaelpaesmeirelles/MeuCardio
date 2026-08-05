# Plano técnico do PR #48 — módulos especializados e assistentes clínicos

Última atualização: 05/08/2026

Branch: `agent/pr48-modulos-especialidades`

Base: `main`, após a publicação dos PRs #46 e #47.

## Objetivo

Criar uma infraestrutura comum para quatro áreas de alta complexidade — cardiopediatria, cardiogeriatria, cardio-oncologia e cardiologia na gravidez — integrando conteúdo clínico original, busca, triagem por sintomas, assistentes por doença, calculadoras validadas, checklists, cronogramas, relatórios e materiais para pacientes.

O sistema deve apoiar a organização do raciocínio clínico e a documentação profissional. Nenhum módulo deve emitir diagnóstico definitivo, prescrição autônoma ou decisão terapêutica sem confirmação explícita do profissional.

## Arquitetura comum

### Guia de Doenças

Criar uma página principal `Guia de Doenças` com submenu `Assistentes por doença`.

Cada verbete terá:

- nome, sinônimos, siglas e termos de busca;
- área principal e áreas relacionadas;
- epidemiologia e relevância clínica;
- apresentação clínica;
- critérios diagnósticos descritos de forma original;
- diagnósticos diferenciais;
- exames iniciais, confirmatórios e de estratificação;
- red flags;
- fluxo ambulatorial;
- fluxo de emergência;
- tratamento e monitorização, sempre dependentes de confirmação médica;
- populações especiais;
- seguimento;
- material para paciente;
- fontes primárias e data da revisão;
- status editorial: rascunho, revisão especializada ou publicado.

O `Assistente por doença` transforma o verbete em formulário estruturado. O usuário informa os achados e recebe:

- síntese dos dados inseridos;
- elementos que apoiam ou enfraquecem a hipótese;
- informações ausentes;
- exames que podem ser considerados;
- sinais de alarme;
- sugestão de fluxo ambulatorial ou emergencial;
- checklist e relatório exportável.

### Triagem de sintomas

Criar uma central com duas frentes visíveis desde o início:

1. `Consultório / ambulatório`;
2. `Emergência`.

Cada fluxo deve:

- registrar idade, contexto clínico, comorbidades, duração, gatilhos e sinais associados;
- identificar red flags;
- classificar prioridade em níveis operacionais, sem substituir protocolos locais;
- listar diagnósticos diferenciais organizados por probabilidade contextual e gravidade potencial;
- sugerir exames iniciais e exames condicionais;
- explicar por que cada exame pode ser útil;
- gerar orientação de encaminhamento, observação ou atendimento imediato;
- produzir resumo para prontuário.

Sintomas iniciais:

- dor torácica;
- dispneia;
- palpitações;
- síncope e pré-síncope;
- cianose;
- edema;
- fadiga e intolerância ao esforço;
- sopro;
- hipertensão ou pressão muito baixa;
- bradicardia e taquicardia;
- febre com suspeita cardiovascular;
- dor em membro com suspeita vascular;
- déficit neurológico com suspeita embólica;
- sintomas cardiovasculares em gestante;
- sintomas cardiovasculares em criança;
- sintomas em paciente oncológico;
- queda, delirium ou deterioração funcional no idoso.

## Cardiopediatria

### Catálogo inicial de doenças e temas

#### Doenças prevalentes ou de apresentação frequente

- hipertensão arterial pediátrica;
- hipertensão do avental branco e hipertensão mascarada;
- obesidade e risco cardiovascular;
- dislipidemias familiares e adquiridas;
- dor torácica pediátrica;
- síncope e intolerância ortostática;
- palpitações e taquicardias supraventriculares;
- sopro inocente e sopro patológico;
- miocardite;
- pericardite;
- doença de Kawasaki;
- síndrome inflamatória multissistêmica pediátrica;
- endocardite infecciosa;
- febre reumática e cardiopatia reumática;
- insuficiência cardíaca pediátrica;
- cardiomiopatia dilatada;
- cardiomiopatia hipertrófica;
- cardiomiopatia restritiva;
- cardiomiopatia arritmogênica;
- miocárdio não compactado;
- canalopatias, incluindo QT longo, Brugada e taquicardia ventricular catecolaminérgica;
- morte súbita e investigação familiar;
- cardiotoxicidade por quimioterapia na infância;
- hipertensão pulmonar pediátrica;
- tromboembolismo venoso pediátrico;
- doença renal crônica e repercussão cardiovascular;
- cardiopatias associadas a síndromes genéticas.

### Calculadoras e ferramentas

- superfície corporal;
- IMC e escore-z;
- percentis de pressão arterial;
- interpretação estruturada de MAPA pediátrica;
- QTc por fórmulas selecionáveis;
- dose por peso ou superfície corporal, com dose máxima e aviso de conferência;
- escore-z coronariano para Kawasaki somente com fórmula licenciável ou de domínio adequado e validação formal;
- tendências de peso, pressão, FEVE, strain e biomarcadores;
- cronograma de retorno ao esporte após miocardite, condicionado à avaliação médica.

### Cardiopatias congênitas

Criar catálogo e assistente próprios dentro de Cardiopediatria.

Classificação principal:

- `Cianóticas`;
- `Acianóticas`.

Subcategorias sugeridas:

- hiperfluxo pulmonar;
- obstrução de via de saída esquerda;
- obstrução de via de saída direita;
- lesões dependentes do canal arterial;
- fisiologia univentricular;
- anomalias coronarianas;
- anomalias venosas;
- pós-operatório e lesões residuais;
- cardiopatia congênita no adulto.

Catálogo inicial:

#### Acianóticas

- comunicação interatrial;
- comunicação interventricular;
- persistência do canal arterial;
- defeito do septo atrioventricular;
- coarctação da aorta;
- estenose aórtica congênita;
- valva aórtica bicúspide;
- estenose pulmonar;
- anomalias de retorno venoso pulmonar parcial;
- janela aortopulmonar;
- anomalia de Ebstein com apresentação não cianótica;
- origem anômala de coronária;
- anéis vasculares;
- cor triatriatum.

#### Cianóticas

- tetralogia de Fallot;
- transposição das grandes artérias;
- truncus arteriosus;
- atresia pulmonar;
- atresia tricúspide;
- retorno venoso pulmonar anômalo total;
- ventrículo único;
- síndrome do coração esquerdo hipoplásico;
- dupla via de saída do ventrículo direito;
- anomalia de Ebstein com cianose;
- transposição corrigida das grandes artérias;
- interrupção do arco aórtico;
- dupla entrada ventricular.

Funcionalidades:

- pesquisa por nome, sigla, anatomia, fisiologia, sintoma e procedimento;
- filtros cianótica/acianótica e por grupo fisiopatológico;
- representação anatômica original ou licenciada;
- história natural;
- exames esperados;
- principais procedimentos e cirurgias;
- lesões residuais;
- indicação de profilaxia de endocardite conforme regra vigente;
- atividade física;
- seguimento;
- transição para cardiologia congênita do adulto;
- alerta de gravidez em cardiopatia congênita.

### Cardiologia fetal

Aplicar a mesma organização das cardiopatias congênitas:

- classificação por cianótica/acianótica quando aplicável ao fenótipo pós-natal;
- classificação fetal por dependência do canal, obstrução, fisiologia univentricular, arritmia e risco de instabilidade ao nascimento;
- pesquisa por diagnóstico, achado ultrassonográfico, arritmia ou risco perinatal.

Temas iniciais:

- indicações de ecocardiograma fetal;
- situs e conexões segmentares;
- comunicação interventricular;
- defeito do septo atrioventricular;
- tetralogia de Fallot;
- transposição das grandes artérias;
- truncus arteriosus;
- coarctação e interrupção do arco;
- síndrome do coração esquerdo hipoplásico;
- atresia pulmonar e tricúspide;
- retorno venoso pulmonar anômalo;
- anomalia de Ebstein;
- tumores cardíacos fetais;
- bloqueio atrioventricular fetal;
- taquicardia supraventricular fetal;
- flutter atrial fetal;
- extrassístoles;
- insuficiência cardíaca e hidropisia fetal;
- cardiomiopatias fetais;
- plano de parto e estabilização neonatal.

## Cardiogeriatria

### Funções

- avaliação multidimensional por domínios: o que importa, medicação, cognição, mobilidade, multimorbidade e suporte social;
- fragilidade, risco de quedas e velocidade de marcha;
- hipotensão ortostática;
- delirium e comprometimento cognitivo;
- nutrição e sarcopenia;
- polifarmácia e desprescrição supervisionada;
- revisão de função renal e ajuste de doses;
- avaliação pré-procedimento;
- plano de alta e transição de cuidado;
- insuficiência cardíaca no idoso;
- fibrilação atrial e anticoagulação;
- doença coronariana e síndrome coronariana no idoso;
- valvopatias, TAVI e cirurgia;
- cuidados paliativos cardiovasculares;
- objetivos terapêuticos e decisão compartilhada.

### Doenças e cenários iniciais

- insuficiência cardíaca com fração reduzida, levemente reduzida e preservada;
- fibrilação atrial;
- estenose aórtica;
- insuficiência mitral e tricúspide;
- doença arterial coronariana;
- hipertensão sistólica isolada;
- hipotensão ortostática;
- síncope e quedas;
- doença do nó sinusal e bloqueios;
- amiloidose cardíaca;
- doença renal crônica;
- doença vascular periférica;
- AVC e prevenção embólica;
- multimorbidade e polifarmácia;
- delirium em unidade cardiológica;
- fragilidade pré-intervenção;
- descondicionamento pós-internação.

## Cardio-oncologia

### Funções

- linha do tempo oncológica e cardiovascular;
- avaliação basal antes da terapia;
- fatores de risco e doença cardiovascular prévia;
- exposição cumulativa;
- cronograma de ECG, troponina, peptídeos natriuréticos, ecocardiograma, FEVE e GLS;
- comparação longitudinal;
- toxicidade por classe de tratamento;
- triagem de emergência;
- interações entre terapias oncológicas e cardiovasculares;
- plano de sobrevivência cardiovascular;
- relatório compartilhado com oncologia.

### Classes e cenários iniciais

- antraciclinas;
- anti-HER2;
- inibidores de VEGF;
- inibidores de tirosina-quinase;
- inibidores de BCR-ABL;
- inibidores de proteassoma;
- RAF/MEK;
- imunoterapia com inibidores de checkpoint;
- terapia hormonal;
- fluoropirimidinas;
- radioterapia torácica;
- transplante de células hematopoéticas;
- terapia CAR-T;
- miocardite por imunoterapia;
- disfunção ventricular relacionada ao tratamento;
- hipertensão relacionada ao tratamento;
- QT prolongado e arritmias;
- síndrome coronariana e vasoespasmo;
- trombose arterial e venosa;
- pericardite e derrame pericárdico;
- hipertensão pulmonar;
- doença valvar e pericárdica tardia por radioterapia.

Regra de propriedade intelectual: não reproduzir ferramentas ou tabelas da ESC/HFA-ICOS sem licença. Implementar dados originais, parâmetros de domínio público ou ferramentas com autorização explícita.

## Cardiologia na gravidez

### Funções

- consulta pré-concepcional;
- avaliação de risco materno e fetal;
- Pregnancy Heart Team;
- cronograma por trimestre e puerpério;
- banco de medicamentos na gravidez e lactação;
- planejamento de anticoagulação;
- plano formal de parto;
- emergências cardiovasculares obstétricas;
- seguimento de complicações obstétricas com impacto cardiovascular futuro;
- material para paciente.

### Doenças e cenários iniciais

- hipertensão crônica;
- hipertensão gestacional;
- pré-eclâmpsia e eclâmpsia;
- cardiomiopatia periparto;
- cardiomiopatia dilatada e hipertrófica;
- cardiopatias congênitas;
- estenose mitral e aórtica;
- prótese valvar mecânica;
- insuficiências valvares;
- aortopatias, Marfan, Loeys-Dietz e valva bicúspide;
- hipertensão pulmonar;
- arritmias supraventriculares e ventriculares;
- fibrilação atrial;
- síndrome coronariana espontânea e aterosclerótica;
- tromboembolismo venoso;
- dissecção de aorta;
- síndrome de Takotsubo;
- miocardite;
- cardiopatia chagásica;
- doença renal e diabetes com risco cardiovascular;
- pós-parto de alto risco.

A mWHO 2.0 e outras ferramentas somente serão incorporadas após análise formal de licença, fórmula, validação e rastreabilidade.

## Conteúdo e fontes

Priorizar fontes primárias e oficiais:

- diretrizes e declarações científicas da SBC, AHA/ACC, ESC, EACVI, ASE, PACES e sociedades pediátricas/obstétricas;
- publicações originais quando não houver diretriz;
- diretrizes brasileiras de cardiologia fetal e cardiopatias congênitas;
- bulas regulatórias e fontes oficiais para medicamentos.

Todo conteúdo publicado deve ter:

- referência original;
- URL ou DOI;
- data de publicação;
- data de revisão Corvia;
- nome ou identificação do revisor;
- aviso quando a evidência for limitada.

## Segurança clínica

- resultados sempre descritos como apoio, não diagnóstico definitivo;
- red flags devem ter destaque visual e linguagem acionável;
- fluxo de emergência deve recomendar protocolo local e avaliação presencial;
- nenhuma dose deve ser aplicada sem peso, idade, função renal e confirmação do profissional;
- nenhum escore protegido será reproduzido sem licença;
- toda fórmula terá testes unitários com casos de referência;
- cada regra clínica será versionada;
- o relatório deve registrar dados de entrada, versão da regra e fontes.

## Implementação por fases

### Fase 1 — infraestrutura comum

- modelos de área, doença, sintoma, assistente, regra, fonte e versão editorial;
- APIs de catálogo, busca e detalhe;
- página Guia de Doenças e submenu Assistentes;
- página Triagem de Sintomas com duas frentes;
- filtros, favoritos, histórico e relatórios;
- migração aditiva e reversível.

### Fase 2 — cardiopediatria

- hipertensão/MAPA;
- Kawasaki;
- miocardite;
- síncope, dor torácica e sopro;
- cardiopatias congênitas;
- cardiologia fetal;
- doses pediátricas com validação.

### Fase 3 — cardiologia na gravidez

- pré-concepção;
- risco;
- medicamentos;
- anticoagulação;
- plano de parto;
- puerpério.

### Fase 4 — cardio-oncologia

- linha do tempo;
- avaliação basal;
- monitorização;
- toxicidades;
- sobrevivência.

### Fase 5 — cardiogeriatria

- avaliação multidimensional;
- polifarmácia;
- fragilidade;
- procedimentos;
- alta e seguimento.

## Critérios de aceite

- busca por nome, sinônimo, sigla, sintoma e categoria;
- navegação acessível em desktop e celular;
- nenhuma recomendação sem fonte e versão;
- triagem separada em ambulatório e emergência;
- cardiopatias congênitas e fetais pesquisáveis e classificadas;
- testes de isolamento entre usuários para históricos e relatórios;
- migrations, build, pytest, smoke HTTP, backup/restauração e corpus verdes;
- revisão clínica antes de publicar conteúdo terapêutico;
- nenhum deploy antes de certificação integral do PR.