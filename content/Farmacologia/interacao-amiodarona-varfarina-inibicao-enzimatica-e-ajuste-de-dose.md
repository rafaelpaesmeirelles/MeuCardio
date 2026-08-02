---
title: "Interação Amiodarona–Varfarina: Inibição Enzimática, Magnitude do Efeito e Ajuste de Dose"
slug: interacao-amiodarona-varfarina-inibicao-enzimatica-e-ajuste-de-dose
theme: "Farmacologia"
kind: farmacologia
review_status: revisado
source_refs: ["Sanoski CA, Bauman JL. Clinical observations with the amiodarone/warfarin interaction: dosing relationships with long-term therapy. Chest. 2002;121(1):19-23. PMID: 11796427 — estudo observacional prospectivo, 43 pacientes em varfarina estável iniciando amiodarona, seguidos por pelo menos 1 ano", "Naganuma M, Shiga T, Nishikata K, Tsuchiya T, Kasanuki H, Fujii E. Role of desethylamiodarone in the anticoagulant effect of concurrent amiodarone and warfarin therapy. J Cardiovasc Pharmacol Ther. 2001;6(4):363-367. PMID: 11907638 — 25 pacientes em varfarina estável recebendo amiodarona, dosagem plasmática de amiodarona e do metabólito desetilamiodarona no dia 7, correlacionada ao delta de INR/dose", "Bula do profissional de saúde do cloridrato de amiodarona (Fresenius Kabi Brasil Ltda., solução injetável) e Bula do ATLANSIL (cloridrato de amiodarona, Sanofi-Aventis Farmacêutica Ltda., comprimidos), itens de Interações Medicamentosas — mesma fonte já usada em 'amiodarona-associacoes-a-evitar-e-a-janela-apos-a-suspensao.md', citada aqui para a afirmação sobre persistência da interação após a suspensão"]
---

# Interação Amiodarona–Varfarina: Inibição Enzimática, Magnitude do Efeito e Ajuste de Dose

## Nota de sobreposição com o acervo existente
Esta interação **já está cadastrada como par estruturado** em
`medicamentos/interacoes.json` (slug `amiodarona-varfarina`, gravidade "grave") e
citada de passagem em `amiodarona-associacoes-a-evitar-e-a-janela-apos-a-suspensao.md`
(tema Arritmias) e em `varfarina-sodica.md` (linha de interações que aumentam o
INR). Nenhum dos três, porém, traz o **mecanismo farmacocinético detalhado por
enantiômero**, a **magnitude quantificada por estudo prospectivo** nem a relação
dose-resposta entre amiodarona e a redução necessária de varfarina — é essa
lacuna que este documento fecha, com fonte primária do PubMed em vez da bula.

## Por que a interação existe: dois mecanismos, dois enantiômeros
A varfarina comercial é uma mistura racêmica de dois enantiômeros com potência e
via de metabolização diferentes — distinção que importa porque a amiodarona não
afeta os dois da mesma forma:

- **S-varfarina**, o enantiômero **mais potente** (cerca de 2 a 5 vezes mais ativo
  que o R), é metabolizada principalmente pela **CYP2C9**.
- **R-varfarina**, menos potente, depende mais de **CYP1A2 e CYP3A4**.

Conforme Naganuma et al. (PMID 11907638), em pacientes que iniciaram amiodarona
mantendo varfarina estável, **não houve correlação entre a concentração
plasmática da amiodarona propriamente dita e a variação do INR por dose**, mas
**houve correlação com a concentração do metabólito ativo desetilamiodarona**.
A conclusão dos autores: é a **inibição da CYP2C9 pela desetilamiodarona** —
não pela amiodarona-mãe — que responde pela maior parte da potencialização do
efeito anticoagulante, por reduzir o clearance da **S-varfarina**, o enantiômero
mais potente. A amiodarona-mãe, por sua vez, inibe predominantemente **CYP1A2 e
CYP3A4**, o que contribui de forma adicional ao afetar a R-varfarina. O efeito
somado dos dois mecanismos — sobre os dois enantiômeros, por duas moléculas
diferentes (fármaco original e metabólito) — é o que torna esta uma das
interações farmacocinéticas mais consistentes e clinicamente relevantes de toda
a farmacologia cardiovascular.

## Magnitude do efeito: quanto reduzir, e conforme qual variável
O estudo de referência para a **quantificação** desta interação é Sanoski e
Bauman (PMID 11796427): 43 pacientes em uso estável de varfarina (dose basal
média de 5,2 ± 2,6 mg/dia) que iniciaram amiodarona, acompanhados por pelo menos
um ano.

Achados centrais:

- A interação **não é fixa** — ela se aprofunda ao longo do tempo e **atinge o
  pico de efeito em torno da 7ª semana** de amiodarona concomitante, com uma
  **redução média máxima de 44% na dose de varfarina** necessária para manter o
  mesmo INR-alvo.
- Houve **forte correlação inversa entre a dose de manutenção da amiodarona e a
  dose de varfarina necessária** (r² = 0,94; p < 0,005) — quanto maior a dose de
  amiodarona, maior a redução de varfarina exigida. Os autores propõem uma
  relação prática, por faixa de dose de manutenção da amiodarona:

  | Dose de manutenção de amiodarona | Redução aproximada de dose de varfarina |
  |---|---|
  | 100 mg/dia | ~25% |
  | 200 mg/dia | ~30% |
  | 300 mg/dia | ~35% |
  | 400 mg/dia | ~40% |

  Os autores descrevem a **redução média máxima observada no estudo (44%)**
  como o efeito de pico, e a tabela acima como uma estimativa prática de ajuste
  gradual conforme a dose de manutenção — as duas cifras não são contraditórias,
  são o "efeito máximo observado" e "estimativa de ajuste por faixa de dose".
- **Sangramento menor ocorreu em 5 dos 43 pacientes (12%)** durante o período de
  ajuste, reforçando que a interação tem consequência clínica real, não é só um
  achado laboratorial.

Este intervalo (25% a 44%, dependendo da dose e do momento) é compatível com o
que o verbete de varfarina desta biblioteca já registra ("espera-se reduzir a
dose de varfarina em 25 a 50%, com interação lenta ao longo de 6 a 8 semanas") —
a fonte primária agora confirma e refina esse número, com a relação por dose de
amiodarona que a bula, por si só, não detalha.

## Tempo de instalação: por que o efeito não aparece de imediato
A amiodarona tem meia-vida de eliminação extremamente longa — rotineiramente
descrita na ordem de semanas — e sua ação farmacológica plena, incluindo a
inibição enzimática, se acumula ao longo de várias semanas de uso contínuo, não
em dias. É por isso que Sanoski e Bauman (PMID 11796427) encontraram o **pico do
efeito de potencialização em torno da 7ª semana** após o início da amiodarona,
não na primeira ou segunda semana. Um INR estável nos primeiros 7 a 10 dias após
iniciar amiodarona **não garante** que o paciente esteja fora de risco — o efeito
ainda está se instalando.

## A parte que mais se esquece: a interação persiste depois de suspender
Pela mesma meia-vida longa que explica o início lento, a amiodarona (e seu
metabólito ativo) permanece no organismo por tempo prolongado após a
descontinuação. A bula do profissional de saúde do cloridrato de amiodarona
registra que **as interações medicamentosas podem ser observadas por vários
meses após a suspensão do fármaco** — a mesma fonte já usada no documento de
associações a evitar desta biblioteca (tema Arritmias).

Consequência prática direta: **suspender a amiodarona não autoriza suspender a
vigilância do INR**. Um paciente que interrompeu amiodarona há 4 ou 8 semanas
continua sob risco de potencialização do efeito da varfarina, e a dose de
varfarina eventualmente precisará ser **reaumentada** conforme o efeito
inibitório se dissipa — de forma igualmente lenta e imprevisível, não em um
único ajuste.

## Manejo prático de monitorização e ajuste

- **Antes de iniciar amiodarona** em paciente já anticoagulado com varfarina,
  antecipar a necessidade de redução de dose — não esperar o INR subir para
  agir.
- **Monitorizar o INR com maior frequência** ao iniciar amiodarona (por
  exemplo, semanalmente nas primeiras semanas, em vez do intervalo habitual de
  4 semanas de um paciente estável), estendendo essa vigilância por **pelo
  menos 2 meses**, já que o efeito de pico só aparece por volta da 7ª semana
  (PMID 11796427).
- **Ajustar a dose de varfarina de forma gradual e guiada pelo INR**, usando a
  faixa de redução aproximada por dose de manutenção de amiodarona como ponto
  de partida (tabela acima), nunca como valor fixo — a resposta individual
  varia, e o próprio estudo de referência descreve relação estatística, não
  regra determinística.
- **Ao suspender a amiodarona**, manter a vigilância de INR por semanas a
  meses, com expectativa de necessidade de **reaumento gradual** da dose de
  varfarina conforme o efeito inibitório se dissipa.
- **Não relaxar a vigilância pelo tempo decorrido desde a suspensão** — a bula
  não define um prazo fixo de "segurança", apenas "vários meses", o que exige
  julgamento clínico caso a caso. `VERIFICAÇÃO HUMANA NECESSÁRIA`: nenhuma das
  fontes consultadas nesta sessão define um número exato de semanas ou meses
  em que a vigilância pode ser considerada encerrada com segurança após a
  suspensão da amiodarona.

## O que este documento não cobre
Substituição por outro antiarrítmico, manejo de sangramento agudo por
supra-anticoagulação e a lista completa das demais interações da amiodarona (por
glicoproteína P, CYP2D6 e prolongamento de QT) estão fora do escopo — ver
`amiodarona-associacoes-a-evitar-e-a-janela-apos-a-suspensao.md`, no tema
Arritmias, para o panorama completo das oito interações verificadas contra
bula.
