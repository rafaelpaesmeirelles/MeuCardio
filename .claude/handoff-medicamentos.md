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

## Estado atual (29/07/2026)
- **90 fármacos** em `medicamentos/metadados.json`; 88 publicados.
  `pregnancy` em 38/90, `lactation` em 24/90.
- **Atropina e evinacumabe despublicados** por não terem posologia — só voltam
  quando a dose entrar com fonte.
- 10 linhas órfãs no banco (duplicatas fundidas, despublicadas). O `DELETE`
  precisa do Rafael; o classificador bloqueia escrita destrutiva.
- **27 interações par a par** em `interacoes.json`, todas com gravidade e fonte.
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
Buscar **pelo nome comercial**, em dois espelhos:
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
1. **Gestação e lactação** nos 52 fármacos que ainda não têm. Faltam com bula
   não obtida: digoxina, clopidogrel (só achei modelo antigo), Forxiga,
   Jardiance, Entresto, rivaroxabana (seção de gravidez).
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
