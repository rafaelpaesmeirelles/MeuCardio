---
title: "Oxigenação na UCO: PaO₂/FiO₂ e Critérios de SDRA"
slug: oxigenacao-pao2-fio2-e-criterios-de-sdra-na-uco
theme: "Terapia intensiva"
kind: protocolo
review_status: pendente_revisao
fonte_producao: chatgpt
summary: "Protocolo de conferência da razão PaO₂/FiO₂ e dos critérios globais de SDRA, com bloqueio explícito contra confundir edema cardiogênico ou sobrecarga volêmica com SDRA."
source_refs: ["Matthay MA, Arabi Y, Arroliga AC, Bernard G, Bersten AD, Brochard LJ, et al. A New Global Definition of Acute Respiratory Distress Syndrome. Am J Respir Crit Care Med. 2024;209(1):37-47. DOI: 10.1164/rccm.202303-0558WS. PMID: 37487152 — consenso global primário que inclui CNAF ≥30 L/min, razão PaO2/FiO2 ≤300 mmHg, ultrassom pulmonar e a categoria não intubada", "ARDS Definition Task Force; Ranieri VM, Rubenfeld GD, Thompson BT, et al. Acute respiratory distress syndrome: the Berlin Definition. JAMA. 2012;307(23):2526-2533. DOI: 10.1001/jama.2012.5669. PMID: 22797452 — definição original validada em 4.457 pacientes, fonte das faixas leve, moderada e grave", "Qadir N, Sahetya S, Munshi L, et al.; American Thoracic Society Assembly on Critical Care. An Update on Management of Adult Patients with Acute Respiratory Distress Syndrome: An Official American Thoracic Society Clinical Practice Guideline. Am J Respir Crit Care Med. 2024;209(1):24-36. DOI: 10.1164/rccm.202311-2011ST. PMID: 38032683 — diretriz oficial ATS usada apenas para conectar o reconhecimento às intervenções cuja indicação depende de avaliação clínica"]
review_note: "Lote técnico produzido em 27/08/2026 com fontes primárias. A calculadora implementa aritmética e gates da definição, mas não emite diagnóstico nem prescreve suporte; conteúdo permanece dependente de revisão clínica humana."
---

# Oxigenação na UCO: PaO₂/FiO₂ e Critérios de SDRA

## Função e limite

Este protocolo responde duas perguntas separadas:

1. qual é a razão entre a PaO₂ arterial e a FiO₂ realmente administrada no
   mesmo momento; e
2. o conjunto declarado preenche os **gates operacionais** da definição global
   de síndrome do desconforto respiratório agudo (SDRA)?

A razão P/F isolada não diagnostica SDRA. Na Unidade Coronariana, a cautela é
especialmente importante porque edema agudo cardiogênico, sobrecarga volêmica,
atelectasia e SDRA podem produzir hipoxemia e opacidades bilaterais. Também podem
coexistir. A ferramenta bloqueia a conclusão quando a origem não primariamente
cardiogênica não foi confirmada, mas não tenta substituir ecocardiografia,
hemodinâmica, imagem ou julgamento clínico.

## Dados simultâneos

Use PaO₂ e FiO₂ do **mesmo momento clínico**. Registre também:

- modalidade de suporte respiratório;
- PEEP/pressão expiratória, se ventilação invasiva, VNI ou CPAP;
- fluxo total, se cânula nasal de alto fluxo (CNAF);
- posição, mudanças recentes de PEEP/FiO₂ e qualidade da gasometria;
- fator predisponente, cronologia e imagem;
- avaliação de insuficiência cardíaca, sobrecarga e atelectasia.

FiO₂ estimada em cânula convencional ou máscara de baixo fluxo varia com fluxo,
volume-minuto, padrão respiratório, ajuste do dispositivo e vazamento. Por isso,
a calculadora exibe a razão, mas não considera oxigênio convencional como gate de
suporte para a categoria hospitalar com recursos.

## Cálculo

Converta FiO₂ percentual para fração antes da divisão:

**P/F (mmHg) = PaO₂ (mmHg) ÷ FiO₂ (fração).**

Exemplo: PaO₂ 80 mmHg em FiO₂ 40% corresponde a **80 ÷ 0,40 = 200
mmHg**. O formulário recebe **40**, e não 0,40, para reduzir erro de unidade.

## Critérios que se aplicam a todas as categorias globais

Todos os itens abaixo precisam ser sustentados pelo caso; a calculadora não os
infere a partir da P/F:

- fator predisponente agudo, como pneumonia, infecção extrapulmonar, aspiração,
  trauma, transfusão, queimadura ou choque;
- início ou piora da insuficiência respiratória hipoxêmica em até uma semana do
  fator predisponente ou de sintomas respiratórios novos/em piora;
- opacidades bilaterais em radiografia ou tomografia, ou perda bilateral de
  aeração em ultrassom realizado por operador treinado, não explicadas por
  derrame, atelectasia ou massa;
- edema pulmonar não exclusiva ou primariamente atribuível a edema cardiogênico
  ou sobrecarga volêmica;
- troca gasosa não primariamente atribuível a atelectasia.

A definição global permite diagnosticar SDRA na presença de insuficiência
cardíaca/sobrecarga se houver também fator predisponente e o edema cardiogênico
não for a explicação exclusiva ou principal. Isso é coexistência documentada,
não autorização para presumir vínculo.

## Gates de oxigenação e suporte

| Categoria | Oxigenação | Suporte mínimo |
|---|---:|---|
| Intubada | P/F ≤300 mmHg | Ventilação invasiva com PEEP ≥5 cmH₂O |
| Não intubada | P/F ≤300 mmHg | CNAF ≥30 L/min ou VNI/CPAP com pressão expiratória ≥5 cmH₂O |

Na categoria **intubada**, as faixas são:

- leve: 200 < P/F ≤300 mmHg;
- moderada: 100 < P/F ≤200 mmHg;
- grave: P/F ≤100 mmHg.

Essas faixas não devem ser aplicadas automaticamente ao paciente não intubado.
A nova definição cria uma categoria não intubada com limiar P/F ≤300, sem
transportar para ela a gradação da categoria intubada. O limite exato importa:
P/F igual a 300 preenche o critério; maior que 300, não.

## Sequência segura de uso

1. confirme que PaO₂, FiO₂ e suporte representam o mesmo momento;
2. calcule a P/F e registre a modalidade, a PEEP ou o fluxo;
3. confirme individualmente fator predisponente, tempo e imagem;
4. avalie objetivamente congestão, função cardíaca e sobrecarga quando a origem
   do edema não estiver clara;
5. documente se atelectasia explica predominantemente a hipoxemia;
6. só então descreva “conjunto compatível com critérios operacionais”, deixando
   o diagnóstico final ao médico responsável;
7. reavalie após mudança clínica ou de suporte — uma medida isolada não descreve
   a trajetória.

## O cálculo não escolhe tratamento

A diretriz ATS de 2024 sustenta ventilação com volume corrente 4–8 mL/kg de peso
predito e pressão de platô abaixo de 30 cmH₂O em SDRA, além de posição prona por
mais de 12 horas/dia em SDRA grave. Essas recomendações não autorizam a
calculadora de oxigenação a prescrever PEEP, prona, bloqueio neuromuscular ou
ECMO. Elegibilidade, contraindicações, hemodinâmica e protocolo local precisam
ser avaliados separadamente.

## Tudo com Tudo — conexões auditáveis

### Vínculo clínico direto

- A calculadora `oxigenacao-pao2-fio2-sdra-uco` executa a aritmética e os gates
  descritos aqui, sem inferir causa.
- A estação `ventilacao-protetora-uco` calcula peso predito, volume corrente por
  kg, platô e pressão de distensão; ela começa onde a avaliação diagnóstica deste
  protocolo termina, sem automatizar parâmetros.
- [Falência aguda do ventrículo direito (cor pulmonale agudo)](falencia-aguda-do-ventriculo-direito-cor-pulmonale-agudo-consenso-acvc-esc-2024.md):
  SDRA aumenta a pós-carga do VD e a ventilação pode agravar a interação
  cardiopulmonar; a relação é fisiopatológica e assistencial direta.

### Vínculo diferencial explícito

- [Ventilação não invasiva no edema agudo de pulmão cardiogênico](ventilacao-nao-invasiva-no-edema-agudo-de-pulmao-cardiogenico-cpap-versus-bipap.md):
  o documento trata de um fenótipo que pode produzir hipoxemia e opacidades
  bilaterais, mas não é SDRA por definição quando explica exclusiva ou
  primariamente o edema. O vínculo é de diagnóstico diferencial, não causal.

### Proximidade temática sem vínculo acrescentado

- Metas de oxigenação após parada cardíaca e estudos de ventilação em outros
  fenótipos tratam de oxigênio, porém não validam o diagnóstico de SDRA. Não foram
  adicionados como passos desta trilha.
- Não foram criadas relações com medicamento, antibiótico, caso clínico,
  emergência ou exame específico: a P/F não seleciona esses itens por si só.

## Armadilhas clínicas

- usar FiO₂ 40 como fração ou 0,40 como percentual, produzindo erro de cem vezes;
- combinar PaO₂ anterior com FiO₂ ou PEEP posterior;
- chamar P/F baixa de SDRA sem fator predisponente, tempo e imagem compatíveis;
- classificar edema cardiogênico como SDRA apenas porque há opacidades bilaterais;
- excluir SDRA apenas porque há insuficiência cardíaca — coexistência é possível,
  mas precisa ser defendida;
- aplicar a gradação intubada ao paciente em CNAF/VNI;
- estimar FiO₂ de baixo fluxo como se fosse concentração fixa;
- transformar o resultado em prescrição automática de FiO₂, PEEP ou prona.
