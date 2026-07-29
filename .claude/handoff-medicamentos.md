# Contexto e instruções — sessão de Medicamentos (Corvia)

## O projeto
Corvia (https://corvia.med.br) — plataforma de apoio à decisão clínica em
Cardiologia, do Dr. Rafael Paes Meirelles. Repositório em `/opt/meucardio`.
**Leia o `CLAUDE.md` inteiro antes de qualquer coisa** — ele é a fonte de
verdade e tem regras que sobrescrevem comportamento padrão.

## Há mais de uma sessão trabalhando no mesmo repositório
Três frentes em paralelo. O `CLAUDE.md` tem uma tabela de posse por caminho e,
acima dela, a **divisão dos 27 temas de `content/`**. Você é a **sessão de
Medicamentos**. Não escreva fora da sua faixa.

**Sua faixa:**
- `medicamentos/metadados.json` e `medicamentos/interacoes.json`
- `backend/app/api/drugs.py`
- `frontend/src/pages/Interacoes.tsx`, `Condicoes.tsx`, `Medicamentos.tsx`
- `.claude/ferramentas/ler_pdf.py` e `decodifica_cid_offset.py`
- **13 temas de `content/`**: Farmacologia, Gravidez, Terapia intensiva,
  Tromboembolismo, Fibrilação atrial, Arritmias, Dispositivos, Prevenção e
  lipídios, Diabetes e cardiologia, Insuficiência cardíaca, Hipertensão,
  Hipertensão pulmonar, Calculadoras.

**Não toque:** `content/` dos outros 14 temas, `evidencias/`, `estudos/`,
`galeria/`, `exames/`, e tudo de `receituario*`/`controlados/` (Tarefa 27).

**Compartilhados** (`App.tsx`, `Shell.tsx`, `Painel.tsx`, `CLAUDE.md`,
`COBERTURA.md`): `git pull --rebase` antes, acrescente só a sua linha, commite
na sequência. **Nunca `git add -A`** — varre trabalho alheio pela metade.
Confira `ls .git/index.lock` antes de commitar.

## Estado atual (29/07/2026, fim da 2ª sessão)
- **88 fármacos** em `medicamentos/metadados.json`.
  **`pregnancy` em 88/88 e `lactation` em 88/88 — as duas frentes FECHARAM** em
  29/07/2026. **59 interações.**
  (Números no início desta sessão, para comparar: 42 e 30, com 32 interações.)

**Os únicos 3 campos de lactação sem conteúdo estão MARCADOS, não vazios** — adenosina,
dobutamina e indapamida. Nos três a fonte foi lida e é silente: Adenocard e Natrilix SR
não têm seção de lactação, e o rótulo do FDA da dobutamina não traz "Nursing Mothers".
Cada marcação diz qual documento foi lido e sugere o próximo, para não virar campo que
ninguém procurou. **Não rebaixe as mesmas fontes esperando resultado diferente.**


- **Login da API é form OAuth2, não JSON** — custou uma tentativa. Use
  `curl -X POST .../api/auth/login --data-urlencode "username=$EMAIL"
  --data-urlencode "password=$PASS"`. Mandar `{"email":...}` devolve 422.
- **O espelho `img.drogasil.com.br` devolveu 403 em tudo** nesta sessão,
  inclusive em nomes que funcionaram na anterior. Parece bloqueio geral do
  servidor, não nome de arquivo errado — não gaste tentativas ali antes de
  conferir se algum nome conhecido ainda passa.
- **Bulas obtidas e lidas nesta sessão** (todas em
  `saudedireta.com.br/catinc/drugs/bulas/<nome>.pdf`, extraídas com
  `pdftotext -layout`, nenhuma cifrada): `inderal`, `dilacoron`, `cardizem`,
  `adalat`, `crestor`, `rosucor`, `micardishct`, `atacand`, `benicar`,
  `zestril`, `natrilixsr`, `higroton`, `sotacor`, `eliquis`, `glifage`,
  `revatio`, `colchis`, `adenocard`, `monocordil`, `isordil`, `viagra`.
  Fora do espelho: a **bula profissional do Eliquis Rev0515** sai direto do
  site da BMS (URL está no `source_refs` de `content/Farmacologia/apixabana.md`)
  e é muito melhor que a do paciente — traz categoria de risco.
- **Bulas que existem mas NÃO servem, para não serem rebaixadas de novo:**
  `natrilix` (texto de compêndio antigo, sem seção de gravidez — use
  `natrilixsr`), `monocordil` (só texto ao paciente, nada sobre gravidez além
  do boilerplate), `micardis` (resumo de compêndio; o profissional só apareceu
  na associação `micardishct`), `revatio` (só o boilerplate genérico).
- **Ainda sem NENHUMA fonte, depois de tentar os três caminhos:** bula
  injetável da **atropina** e **Evkeeza** (evinacumabe) — os dois verbetes
  saíram do arquivo-fonte por não terem posologia, e voltam quando a bula
  aparecer. Todo o resto do acervo foi coberto.
  **Não repita estas buscas — elas já foram resolvidas por outro caminho:**
  Forxiga, Jardiance, Entresto, Lixiana, Ozempic, Tracleer, Verquvo, Vyndaqel,
  Camzyos, Leqvio, Nilemdo, Kengrexal, Angiox, Ranexa, Kerendia e Efient saíram
  pela **EMA**; flecainida, eplerenona, perindopril, sildenafila, nitroglicerina,
  mononitrato, nitroprussiato, heparina, protamina, vasopressina, dobutamina,
  adrenalina, noradrenalina e disopiramida saíram pelo **DailyMed**.
- **Atropina e evinacumabe despublicados** por não terem posologia — só voltam
  quando a dose entrar com fonte.
- 10 linhas órfãs no banco (duplicatas fundidas, despublicadas). O `DELETE`
  precisa do Rafael; o classificador bloqueia escrita destrutiva.
- **59 interações** em `interacoes.json`, todas com gravidade e fonte. **Elas são
  lidas do disco a cada chamada da rota** (`_interacoes_curadas()` em
  `backend/app/api/drugs.py`) — não há passo de carga, e editar o JSON já vale.
- Tarefas 8 (checador de interação), 9 (alerta de diretriz), 19 (alerta por
  condição especial) e 21 (Painel) no ar.

## Incidente de 29/07/2026 às 20h — leia antes de confiar no `git log`

**O commit `dbcf6d2`, cuja mensagem fala só de `COBERTURA.md`, contém também
seis arquivos meus** que nada têm a ver com cobertura. A outra sessão rodou
`git commit -a` com a minha árvore de trabalho suja e varreu tudo junto. O
conteúdo está íntegro — o que se perdeu foi a procedência, porque a mensagem
não descreve o que entrou.

**O que está dentro de `dbcf6d2` além do `COBERTURA.md`:**
- `medicamentos/metadados.json` — tenecteplase com o AVC isquêmico resolvido
  pelo rótulo do TNKase (FDA, 02/2025); alteplase com a premissa da marcação
  corrigida; milrinona reescrita pela bula do Primacor; colchicina marcada.
- `content/Farmacologia/`: `tenecteplase.md`, `alteplase.md`, `milrinona.md`,
  `colchicina.md`, `atropina.md` — as mesmas correções do lado da prosa, mais
  a remoção de **todas as 15 citações de `droracle.ai`** do repositório.

**Como não repetir — e o diagnóstico que eu tinha escrito aqui estava errado.**
Eu havia atribuído o caso a um `git commit -a`. A sessão da Biblioteca corrigiu
em `8fcd790`, e a correção dela é melhor: **o `-a` não foi usado, e evitá-lo não
teria impedido nada.** A causa real é que **o índice do git é compartilhado
entre as sessões** — `git add` de uma fica visível para a outra. Um
`git add <meu arquivo> && git commit -m "..."` leva junto tudo que a outra
sessão já tinha em *staging*, com a minha mensagem.

As duas defesas que funcionam, adotadas a partir de 29/07/2026:
1. **`git diff --cached --name-only` antes de commitar.** Se aparecer arquivo
   que não é seu, **pare** — a outra sessão está com trabalho staged.
2. **Commite por caminho: `git commit -m "..." -- <caminho>`.** Só aquele
   caminho entra, qualquer que seja o estado do índice.

E o corolário, que vale para mim: **não deixe arquivo staged e parado.**
`git add` e `git commit` andam na mesma chamada, sempre.

## Regras que não se flexibilizam
1. **Nada é publicado sem o aval do Rafael.** `published` fica `false`; o campo
   do JSON é ignorado pelos carregadores de propósito.
2. **Nada entra sem a fonte lida.** Resumo de resultado de busca **não é fonte**.
3. Onde a fonte não afirmar, o campo fica **vazio e marcado** com o texto
   literal `VERIFICAÇÃO HUMANA NECESSÁRIA`. Campo preenchido com texto vago é
   pior que vazio — faz o médico parar de procurar.
4. **Nomeie divergências, não as apague.** Quando a bula brasileira discorda do
   protocolo, do rótulo do FDA ou do que o documento já dizia, registre as duas
   versões atribuídas. Já apareceram: enoxaparina, varfarina, bisoprolol,
   nitroprussiato, hidralazina, metildopa.
5. Nunca invente dose, corte, DOI, PMID ou licença de imagem.

## Método que funciona para obter bula

### Primeiro: a EMA publica em PORTUGUÊS — comece por aqui nos fármacos modernos
Descoberto em 29/07/2026, e é o maior ganho de rendimento da sessão. Padrão:

```
https://www.ema.europa.eu/pt/documents/product-information/<nome>-epar-product-information_pt.pdf
```

Baixa com `curl -sL -A "<UA de browser>"`, abre com `pdftotext -layout` e **não
precisa do decodificador de CID**. A secção **4.6 é sempre "Fertilidade,
gravidez e aleitamento"**, e a **4.3 é "Contraindicações"** — as duas rendem
campo e interação de uma vez. Extraia com
`awk '/4\.6[ \t]+Fertilidade/{f=1} f{print} /^4\.7/{if(f)exit}'`.

**Funcionaram:** `verquvo`, `camzyos`, `leqvio`, `nilemdo`, `nustendi`,
`vyndaqel`, `lixiana`, `ozempic`, `tracleer`, `praxbind`, `multaq`, `entresto`,
`forxiga`, `jardiance`, `kengrexal`, `angiox`, `ranexa`, `kerendia`, `efient`.
**Não existem lá:** `inspra` (eplerenona) e, em geral, **nada anterior ao
procedimento centralizado europeu** — os hospitalares antigos não têm EPAR.

Isto resolve exatamente a lista que as duas sessões anteriores tinham dado por
perdida — Forxiga, Jardiance e Entresto estavam marcados como "não saíram em
espelho nenhum" e estão na EMA.

**Ressalva que precisa continuar aparecendo no campo:** é rotulagem europeia,
não bula da ANVISA. Escreva a origem dentro do próprio texto do campo, como
está feito nos dez que entraram, para o revisor saber o que está lendo.

### Para os hospitalares antigos: DailyMed (FDA)
Sem EPAR na EMA e sem espelho brasileiro, o caminho é o rótulo americano. Busca
por nome do princípio, depois o XML pelo `setid`:

```
https://dailymed.nlm.nih.gov/dailymed/services/v2/spls.json?drug_name=<nome>&pagesize=20
https://dailymed.nlm.nih.gov/dailymed/services/v2/spls/<setid>.xml
```

Tire as tags com regex e leia as secções **8.1 Pregnancy** e **8.2 Lactation**
no formato novo (PLLR), ou **Pregnancy Category** e **Nursing Mothers** nos
rótulos antigos. Dois cuidados que custaram retrabalho:
1. **Confira o título do resultado.** Buscar `protamine` devolve *insulina
   protamina*, que é outro fármaco. Filtre pelo título antes de baixar.
2. **Confira a forma farmacêutica.** `nitroglycerin` devolve a pomada; para
   cardiologia é preciso filtrar por `INJECTION`.

**O PLLR aboliu as categorias por letra.** Rótulo no formato novo **não tem**
categoria A/B/C/D/X — se um verbete atribui letra citando rótulo do FDA
recente, provavelmente é invenção. Foi assim que se achou o defeito da
noradrenalina em 29/07/2026.

### Depois: os espelhos brasileiros, pelo nome comercial
- `https://www.saudedireta.com.br/catinc/drugs/bulas/<marca>.pdf`
- `https://img.drogasil.com.br/raiadrogasil_bula/<Marca>.pdf`

**403 ou 404 num espelho = nome de arquivo errado, não documento ausente.**
Tente o outro antes de desistir — Selozok, Lasix e Marevan só apareceram assim.
Use `curl -sL -A "<user-agent de browser>"`; `WebFetch` toma 403 em site de
laboratório.

Extração: `python3 .claude/ferramentas/ler_pdf.py <arquivo.pdf>`.
- Saída **embaralhada** = fonte sem `/ToUnicode`. Use
  `decodifica_cid_offset.py <txt> <offset>`; teste 27 e 29 contra um texto
  conhecido antes de confiar.
- Saída **vazia** = PDF cifrado (`/Encrypt`) ou objetos em fluxo (`/ObjStm`).
  Diagnóstico: `grep -c '/Encrypt' arq.pdf ; grep -c '/ObjStm' arq.pdf`.
  Contorno: bulário em HTML (BulasMed republica o texto registrado).

## Como o conteúdo chega ao ar
Conteúdo **não precisa de rebuild**:
`POST /api/admin/conteudo/carregar?frente=medicamentos` (token de admin do
`.env`). **Sempre use `?frente=`** — sem ele recarrega todas as frentes,
inclusive trabalho pela metade das outras sessões.
Documentos de `content/` entram por `POST /api/admin/import`.
Só código exige `docker compose -f docker-compose.prod.yml up -d --build ...`,
e rebuild pede confirmação do Rafael antes.

## Padrão de documento novo em `content/`
Front matter igual ao dos existentes (`title`, `slug`, `theme`, `kind`,
`summary`, `review_status: revisado`, `source_refs` com citação completa).
O que funcionou: recorte estreito e **declarado no texto** — "o que a bula
registrada diz sobre X" —, com uma seção final dizendo **o que o documento não
cobre**. Fluxograma tem formato obrigatório de árvore de decisão: ver
`CLAUDE.md` e validar com os dois scripts de `.claude/ferramentas/`.

## Por onde continuar
0. ~~Correções de `content/Farmacologia` fora do ar~~ — **RESOLVIDO em
   29/07/2026.** As três subiram e estão publicadas: apixabana, lisinopril e
   ácido bempedoico. Conferido depois do import: documentos publicados
   seguiram em **246**, e os retidos foram de 22 para 24 — os dois que
   entraram são da sessão da Biblioteca e chegaram como `published = false`.
   Nada foi publicado indevidamente.
1. ~~Gestação e lactação~~ — **FRENTE ENCERRADA em 29/07/2026, 88/88 nos dois
   campos.** A ordem de fontes que resolveu, e que vale para qualquer campo novo:
   **(1) espelho brasileiro** pelo nome comercial; **(2) EMA em português**, que
   cobre tudo que é moderno; **(3) DailyMed**, que cobre os hospitalares antigos —
   dobutamina, vasopressina, protamina, nitroprussiato, heparina, adrenalina e
   noradrenalina não têm EPAR porque são anteriores ao procedimento centralizado
   europeu. Sempre declare a origem **dentro do texto do campo** quando não for a
   bula da ANVISA.
2. **Base de interações — 59, e a fonte mais produtiva agora é a secção 4.5 dos
   RCM da EMA.** Ela nomeia o fármaco com o número medido, que é o que a
   Tarefa 8 precisa. Priorize pares em que **os dois** lados estão no acervo:
   par a par serve ao checador, `classe_oposta` só serve para leitura.
   Vale registrar também a interação que **NÃO exige conduta** — edoxabana com
   verapamil e com amiodarona entraram como `leve` de propósito, para impedir
   a redução de dose por precaução que a bula dispensa.

   **Aguardando o aval do Rafael:** o documento
   `content/Terapia_intensiva/inotropicos-e-vasopressores-na-gestacao-e-lactacao-o-que-diz-a-rotulagem.md`
   está importado com `published = false`.
3. **Conteúdo novo nos seus 13 temas.** Os que precisam de diretriz nova
   (baixar e ler): Terapia intensiva, Insuficiência cardíaca, Diabetes e
   cardiologia, Fibrilação atrial, Dispositivos, Hipertensão pulmonar.
4. Varredura cruzada periódica entre `medicamentos/metadados.json` e
   `content/Farmacologia/<slug>.md` — já achou 1 contradição real em 90 pares.

## Primeira ação sugerida
Ler `CLAUDE.md`, rodar `git log --oneline -15` para ver o que as outras sessões
fizeram, e conferir o estado real com
`GET /api/admin/conteudo/pendentes` antes de escrever qualquer coisa.

---

# Anexo — estado detalhado ao encerrar a sessão de 29/07/2026

## Pendências que dependem do Rafael
1. **12 linhas mortas no banco `drugs`** — 10 duplicatas fundidas mais atropina e
   evinacumabe, todas despublicadas e invisíveis ao produto. Já saíram do
   arquivo-fonte, então não voltam num `carregar`. Falta só o `DELETE`, que o
   classificador de permissões bloqueia para a sessão:
   ```
   docker compose -f docker-compose.prod.yml exec -T db psql -U meucardio -d meucardio -c "DELETE FROM drugs WHERE published = false AND slug IN ('metoprolol-succinato','metoprolol-succinato-de-liberacao-prolongada','metoprolol-succinato-e-tartrato','nitratos-nitroglicerina-dinitratomononitrato-de-isossorbida','nitroglicerina-dinitrato-de-isossorbida','prasugrel-cloridrato','sotalol-cloridrato','trimetazidina-dicloridrato','verapamil-diltiazem','warfarina','atropina','evinacumabe')"
   ```
   Esperar `DELETE 12`. Depois: 88 registros, todos publicados.
2. **Nome do repositório no GitHub** ainda é a marca abandonada por risco
   jurídico. Renomear e depois `git remote set-url origin <nova URL>`.
3. **Bula injetável da atropina** e **bula do Evkeeza (evinacumabe)** — os dois
   verbetes foram removidos por não terem posologia. O conteúdo (mecanismo,
   indicações, contraindicações, efeitos adversos) está recuperável em
   `git show ff6c303~1:medicamentos/metadados.json`. Reinserir quando a bula
   aparecer. Evkeeza tem registro ANVISA 1.3964.0004 (Ultragenyx).

## Detalhe operacional que custou três tentativas
Nesta interface, comando de terminal colado como mensagem **não executa** — vai
como texto para o assistente. Para rodar no servidor é preciso **prefixar com
`!`**. Comandos do próprio Claude Code (`/clear`, `/compact`) vão sem prefixo.

## Bulas já obtidas — URLs que funcionaram
Os PDFs ficavam no scratchpad de `/tmp` e **se perdem ao limpar a sessão**.
Baixar de novo é barato com estas URLs, todas com `curl -sL -A "<UA de browser>"`.

`https://www.saudedireta.com.br/catinc/drugs/bulas/<nome>.pdf` — funcionou para:
`concor` (bisoprolol), `cozaar` (losartana), `renitec` (enalapril),
`aldactone` (espironolactona), `atenol` (atenolol), `norvasc` (anlodipino),
`lipitor` (atorvastatina), `coreg` (carvedilol), `aldomet` (metildopa),
`atensina` (clonidina), `apresolina` (hidralazina), `procoralan` (ivabradina),
`zetia` (ezetimiba), `selozok` e `seloken` (metoprolol), `lasix` (furosemida),
`marevan` (varfarina), `clexane` (enoxaparina), `iscover` e `plavix`
(clopidogrel — **modelo antigo, recusado**), `metalyse` (tenecteplase),
`actilyse` (alteplase), `vastarelmr` (trimetazidina), `eliquis` (apixabana),
`pradaxa` (dabigatrana), `atropina` (**é a OFTÁLMICA — não serve**).

Outras fontes que funcionaram:
- `img.drogasil.com.br/raiadrogasil_bula/<Marca>.pdf` — `Atlansil`,
  `Riscard-Biolab`, `Praluent`, `CaptoprilMedley`, `Aspirina`
- `far.fiocruz.br/.../Farmanguinhos-captopril_Bula_Prof-Saude.pdf` (captopril)
- `amgen.com.br/.../Repatha_Bula_Profissional.pdf` (evolocumabe)
- `abbottbrasil.com.br/.../BU-13-Ritmonorm-bula-profissional-FINAL.pdf`
- `cristalia.com.br/index.php/produto/138/bula-profissional` (nitroprussiato)
- `drogariaspacheco.vteximg.com.br/arquivos/firialta-10mg-...pdf` (finerenona)
- `azmed.com.br/.../Brilinta_Bula_Profissional.pdf` (ticagrelor)
- `bulas.med.br/p/detalhamento-das-bulas/1296088/...xarelto.htm` — **HTML**,
  contorna o PDF cifrado do Xarelto
- DailyMed (FDA): `dailymed.nlm.nih.gov/dailymed/services/v2/spls.json?drug_name=X`
  e depois `.../spls/<setid>.xml` — usado em flecainida e disopiramida
- EMA em português: `ema.europa.eu/pt/documents/product-information/<x>_pt.pdf`
  — usado no Multaq (dronedarona); precisa do decodificador com **offset 29**

**Não saíram em espelho nenhum:** digoxina, Forxiga (dapagliflozina),
Jardiance (empagliflozina), Entresto (sacubitril-valsartana), atropina
injetável, Evkeeza.

## Lacunas de conteúdo, medidas ao encerrar
- **88 fármacos**; `pregnancy` faltando em **46**, `lactation` em **58**.
- Sem gestação: ácido bempedoico, adenosina, apixabana, bivalirudina, bosentana,
  candesartana, cangrelor, clortalidona, colchicina, diltiazem, dinitrato de
  isossorbida, disopiramida, dobutamina, dronedarona, edoxabana, epinefrina,
  eplerenona, felodipino, flecainida, heparina não fracionada, idarucizumabe,
  inclisirana, indapamida, levosimendana, lisinopril, mavacamteno, metformina,
  milrinona, mononitrato de isossorbida, nifedipina, nitroglicerina,
  nitroprussiato, olmesartana, perindopril, propranolol, protamina, ranolazina,
  rosuvastatina, semaglutida, sildenafila, sotalol, tafamidis, telmisartana,
  vasopressina, verapamil, vericiguate.
- **Marcações `VERIFICAÇÃO HUMANA NECESSÁRIA` restantes (4 verbetes):**
  amiodarona (pediatria e gravidez), propafenona (EV, *pill in the pocket*,
  pediatria), alteplase (janela do AVC — a de 2012 diz 3 h, a prática usa 4,5),
  tenecteplase (uso no AVC isquêmico). As quatro dependem de **diretriz**, não
  de bula.

## Achados clínicos desta sessão que valem como precedente
Todos vieram de comparar a bula registrada com o que já estava escrito:
- **Nitroprussiato**: teto de adulto é **8** mcg/kg/min na bula brasileira; os
  10 que circulam são o teto **pediátrico**.
- **Varfarina**: FDA trata o aleitamento como compatível; **Marevan
  contraindica**. Divergência entre rotulagens, registrada nos dois lados.
- **Clopidogrel**: acima de 75 anos a dose de ataque **não é suprimida, é
  reduzida a 75 mg** (ESC 2023, Tabela S10).
- **Atenolol é categoria D e metoprolol é C** — betabloqueador não é classe
  homogênea na gestação.
- **Atorvastatina** restringe **mulher em idade fértil**, não só gestante.
- **Hidralazina oral** manda interromper na gravidez, enquanto a **parenteral**
  é usada na emergência hipertensiva — recorte precisa estar declarado.
