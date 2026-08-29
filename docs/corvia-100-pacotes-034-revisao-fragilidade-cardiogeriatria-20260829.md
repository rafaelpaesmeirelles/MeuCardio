# CorVIA 100 pacotes — 034/100 — Fragilidade e decisão cardiovascular

Data: 29/08/2026  
Base: `main` `59566e1196e0fa7f465df93516790ef454e1f565`

## Objetivo

Revisão adversarial do uso de fragilidade na cardiogeriatria, especialmente antes de TAVI, cirurgia valvar, revascularização e outras intervenções cardiovasculares invasivas.

## Evidência crítica

- **FRAILTY-AVR** — Afilalo et al. J Am Coll Cardiol. 2017;70:689-700; PMID `28693934`; DOI `10.1016/j.jacc.2017.06.024`. Comparou instrumentos de fragilidade em idosos submetidos a TAVI ou troca valvar cirúrgica e demonstrou forte valor prognóstico do Essential Frailty Toolset.
- A evidência de fragilidade é predominantemente prognóstica/observacional. Um instrumento capaz de predizer mortalidade ou incapacidade não é, por isso, um ensaio que demonstre benefício de negar ou oferecer determinada intervenção.

## Revisão adversarial

1. **Fragilidade ≠ idade cronológica:** idade isolada não substitui avaliação funcional, cognitiva, nutricional e de mobilidade.
2. **Risco prognóstico ≠ futilidade:** um escore de fragilidade elevado não deve ser convertido automaticamente em `não intervir`.
3. **Predição ≠ efeito terapêutico:** FRAILTY-AVR não randomizou pacientes para TAVI/cirurgia versus tratamento conservador com base no escore; portanto não prova que um limiar específico de fragilidade deva excluir intervenção.
4. **Fragilidade é potencialmente dinâmica:** descondicionamento agudo, hospitalização, anemia, congestão e doença intercurrente podem alterar desempenho funcional.
5. **Decisão deve incorporar objetivos:** sobrevida, independência, sintomas, cognição, suporte social, carga de tratamento e preferência do paciente são dimensões separadas.
6. **Evitar soma informal de escalas:** Clinical Frailty Scale, Essential Frailty Toolset e outras ferramentas têm propriedades e contextos de validação distintos.

## Guardrails para CorVIA

- nunca gerar `fragilidade alta = contraindicação`;
- nunca gerar `idade avançada = futilidade`;
- apresentar fragilidade como modificador de prognóstico e de decisão compartilhada;
- evitar pontos de corte automáticos para negar TAVI, cirurgia ou revascularização quando a fonte não os validou como regra decisória;
- distinguir limitação reversível/descondicionamento de fragilidade persistente quando houver dados clínicos suficientes;
- recomendar Heart Team/decisão multidisciplinar nos cenários de alta complexidade, sem substituir julgamento médico.

## Resultado

A integração de fragilidade ao CorVIA é clinicamente valiosa, mas o principal risco é transformar **associação prognóstica em regra de exclusão terapêutica**. Esse erro deve ser bloqueado na camada de IA e nos futuros fluxos determinísticos.

Nenhum arquivo clínico foi alterado neste pacote; revisão documental apenas.
