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
  `pregnancy` em **69/88**, `lactation` em **54/88**, **46 interações**.
  (Números da 1ª sessão, para comparar: 42 e 30, com 32 interações.)

**Sem `pregnancy` (19):** bivalirudina, cangrelor, disopiramida, dobutamina, epinefrina-adrenalina, eplerenona, felodipino, flecainida, heparina-nao-fracionada, levosimendana, milrinona, mononitrato-de-isossorbida, nitroglicerina-trinitrato-de-glicerila, nitroprussiato-de-sodio, perindopril-argininaerbumina, protamina, ranolazina, sildenafila-citrato, vasopressina

**Sem `lactation` (34):** adenosina, amiodarona-cloridrato, atenolol, benazepril-cloridrato, bivalirudina, cangrelor, carvedilol, clonidina, disopiramida, dobutamina, enalapril-maleato, epinefrina-adrenalina, eplerenona, felodipino, finerenona, flecainida, heparina-nao-fracionada, hidralazina, hidroclorotiazida, indapamida, ivabradina-cloridrato, levosimendana, milrinona, mononitrato-de-isossorbida, nitroglicerina-trinitrato-de-glicerila, nitroprussiato-de-sodio, noradrenalina-norepinefrina, perindopril-argininaerbumina, prasugrel, protamina, ramipril, sildenafila-citrato, tenecteplase, vasopressina
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
- **Bulas lidas cuja seção de lactação simplesmente não existe** — não vale
  rebaixá-las de novo pelo mesmo documento: **adenosina** (Adenocard) e
  **indapamida** (Natrilix SR). As duas têm gravidez preenchida.
- **Ainda sem fonte, depois de tentar espelho brasileiro E a EMA:** Coversyl
  (perindopril), Inspra (eplerenona) — a eplerenona **não tem EPAR na EMA** —,
  Tambocor (flecainida), Ranexa (ranolazina), Tridil (nitroglicerina),
  Monocordil retard (mononitrato), atropina injetável e Evkeeza (evinacumabe).
  Os que estavam nesta lista e **saíram pela EMA** (não tentar de novo pelo
  espelho brasileiro): Forxiga, Jardiance, Entresto, Lixiana, Ozempic,
  Tracleer, Verquvo, Vyndaqel, Camzyos, Leqvio, Nilemdo.
- **Atropina e evinacumabe despublicados** por não terem posologia — só voltam
  quando a dose entrar com fonte.
- 10 linhas órfãs no banco (duplicatas fundidas, despublicadas). O `DELETE`
  precisa do Rafael; o classificador bloqueia escrita destrutiva.
- **46 interações** em `interacoes.json`, todas com gravidade e fonte.
- Tarefas 8 (checador de interação), 9 (alerta de diretriz), 19 (alerta por
  condição especial) e 21 (Painel) no ar.

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
`forxiga`, `jardiance`. **Não existem lá:** `inspra` (eplerenona).

Isto resolve exatamente a lista que as duas sessões anteriores tinham dado por
perdida — Forxiga, Jardiance e Entresto estavam marcados como "não saíram em
espelho nenhum" e estão na EMA.

**Ressalva que precisa continuar aparecendo no campo:** é rotulagem europeia,
não bula da ANVISA. Escreva a origem dentro do próprio texto do campo, como
está feito nos dez que entraram, para o revisor saber o que está lendo.

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
0. **PENDENTE COM O RAFAEL, e é o item mais urgente:** duas correções em
   `content/Farmacologia/` estão **commitadas mas ainda não no ar**, porque a
   única rota que as sobe é `POST /api/admin/import`, que **reimporta
   `content/` inteiro** e por isso alcança a faixa da outra sessão. Enquanto
   não rodar, o documento publicado da **apixabana continua listando
   "Gravidez" e "Insuficiência hepática grave" como contraindicações** — o
   que a bula profissional Rev0515, citada no próprio arquivo, não faz
   (categoria B, "não recomendada"). Conferido no ar em 29/07/2026 pela
   `/api/library/documents/apixabana`.
1. **Gestação e lactação** nos fármacos que ainda não têm — as duas listas
   exatas estão na seção "Estado atual" acima. **Comece pela EMA**, e só depois
   pelos espelhos brasileiros: foi assim que 10 fármacos dados como perdidos
   entraram numa tarde. Os que sobraram são, na maioria, **fármacos de uso
   hospitalar antigos** (dobutamina, milrinona, vasopressina, protamina,
   heparina não fracionada, nitroglicerina) — esses não têm EPAR na EMA, porque
   são anteriores ao procedimento centralizado; o caminho para eles é bula de
   genérico brasileiro ou DailyMed.
2. **Base de interações** — cresce de graça: cada bula lida rende par com
   gravidade e fonte. Há 33 candidatos já sinalizados pelo texto do acervo.
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
