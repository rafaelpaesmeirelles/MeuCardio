# MeuCardio — contexto e instruções permanentes

## O que é
Plataforma de apoio à decisão clínica em Cardiologia ("Guia de Cardiologia"),
idealizada e desenvolvida por Dr. Rafael Paes Meirelles (CRM-SP 138266, RQE 134798).
Uso independente, sem vínculo institucional.

Inclui biblioteca científica, calculadoras/escores validados, comparador de
medicamentos, galeria de imagens, exames, evidências, estudos, round hospitalar,
agenda, modelos de documento, assistente de IA clínica, e (em construção)
fluxogramas visuais de investigação/tratamento por patologia.

## Identidade do produto
O **MeuCardio** (https://meucardio.med.br) é produto independente e próprio,
**sem vínculo institucional com nenhum hospital ou serviço**. O projeto teve
uma marca anterior, ligada a um serviço hospitalar; ela foi integralmente
removida do repositório, do banco e da interface. Regras que decorrem disso:

- Nenhuma marca, nome ou referência institucional anterior pode voltar a
  aparecer em código, conteúdo, textos de interface, metadados ou
  configuração. Se precisar identificar os termos exatos para uma varredura,
  eles estão no histórico do git (`git log -S`), não neste arquivo — mantê-los
  escritos aqui recria justamente o resíduo que a regra proíbe.
- Nada de fluxo de revisão institucional: a responsabilidade clínica é do
  Rafael, cardiologista responsável pelo projeto.
- O público é o cardiologista brasileiro em geral, não uma equipe interna.
  Linguagem, navegação e conteúdo devem assumir esse leitor.

## Metas do projeto (norteiam prioridade de qualquer tarefa)
1. **Ser referência em Cardiologia no Brasil.** A régua de qualidade é a de
   uma fonte que um cardiologista citaria: sempre fundamentado em diretriz
   atual (ESC, AHA/ACC, SBC) ou estudo original, com referência completa e
   verificável. Nada de conteúdo raso, genérico ou preenchido de memória.
2. **Comercializar a assinatura mensal o quanto antes.** Tudo que destrava
   cobrança real e retenção de assinante tem prioridade sobre melhorias
   cosméticas: Stripe em produção, Minha Conta, portal de assinatura,
   cancelamento, troca de forma de pagamento, fluxo de entrada do novo
   assinante.
3. **Repertório de conteúdo o mais completo possível.** A biblioteca deve
   cobrir a Cardiologia inteira, não só os temas mais frequentes — amplitude
   (todas as patologias, todas as seis frentes abaixo) e profundidade
   (dose, corte de escore, valor de referência, número real do estudo).
   Lacuna de cobertura é dívida do produto, não detalhe.

## Regra permanente de autonomia
Quando eu pedir para "continuar expandindo a biblioteca" ou similar, você deve
trabalhar em QUALQUER uma das seis frentes abaixo (não só documentos de texto):

1. **content/<Tema>/*.md** — documentos da biblioteca científica (protocolo padrão já em uso).
2. **galeria/metadados.json** + arquivo de imagem em galeria/<pasta>/ — achados de imagem
   (ECG, eco, TC, RM, radiografia, cateterismo). Imagem só pode vir de fonte de acesso
   aberto com licença verificável (Wikimedia Commons, PMC Open Access) — nunca gerada por
   IA. Confira a licença de cada imagem antes de baixar, salve a atribuição completa.
3. **exames/metadados.json** — marcadores laboratoriais e exames cardiológicos
   (o que mede, valor de referência, indicação, interpretação, limitações).
   O campo `category` é taxonomia fixa, sempre um destes três valores —
   nunca inventar categoria nova: `laboratorial` (biomarcador de sangue/urina),
   `metodo_grafico` (gera traçado sem imagem — ECG, teste ergométrico, Holter,
   MAPA), `imagem` (gera imagem — eco, TC, RM, radiografia, cateterismo; o
   achado específico vai na Galeria, aqui é sobre o exame em si).
4. **evidencias/metadados.json** — registros de evidência: uma recomendação pontual
   por entrada, com classe (I/IIa/IIb/III), nível (A/B/C), sociedade, ano e referência
   completa — não é o documento inteiro, é a afirmação específica.
5. **estudos/metadados.json** — catálogo de ensaios clínicos, revisões sistemáticas
   e metanálises: resumo, principais achados (com números reais, não vagos) e
   implicação clínica, sempre em texto próprio — nunca copiar abstract original.
6. **Farmacologia** (dentro de content/) — preencher medicamentos que ainda faltam
   dose/apresentação/ajuste renal, ou cadastrar medicamento novo ainda ausente.

Para cada entrada em JSON (galeria/exames/evidências/estudos), o slug precisa ser
único dentro do arquivo — confira o JSON existente antes de adicionar, para não
duplicar. Consulte COBERTURA.md para decidir qual das seis frentes está mais fraca
e priorize por aí, mas sinta-se livre para alternar entre frentes na mesma sessão.

## Fluxogramas: formato obrigatório de árvore de decisão
Decisão do Rafael, válida para os fluxogramas já existentes e para todos os
próximos: o diagrama tem de ser uma **árvore de decisão estrita**, não um
fluxograma-grafo. Regras, todas verificáveis mecanicamente:

- `flowchart TD` (de cima para baixo), em bloco ```mermaid``` dentro do `.md`.
- **Uma única raiz**, e todo nó não-raiz com **exatamente um pai**. Caminho que
  converge ou que volta (ciclo) está proibido — é o que separa árvore de grafo.
  Quando dois ramos chegam à mesma conduta, **duplique o nó de conduta**; quando
  algo vale para todos os ramos (reavaliação periódica, tratar comorbidade),
  tire do diagrama e escreva em prosa logo abaixo dele.
- Formas com significado fixo: raiz e passos intermediários em retângulo
  `X["..."]`; decisão em losango `D{"...?"}`, com **rótulo em toda aresta** que
  sai dela e no mínimo dois ramos; **conduta em estádio `C(["..."])`, sempre
  folha** — toda folha da árvore é uma conduta, e nenhuma conduta tem filho.
- Fechar o bloco com `classDef conduta fill:#eef6ef,stroke:#2f7a4f,color:#12301f;`
  e `class C1,C2,... conduta;`. A forma de estádio já distingue conduta sem
  depender do CSS; a cor é reforço.
- Entradas de um mesmo cálculo (variáveis de um escore, parâmetros de uma
  probabilidade) **não são ramos** — vão para prosa ou tabela.
- Seção do diagrama intitulada `## Árvore de decisão` (ou
  `## Árvore de decisão: <recorte>` quando o documento tiver mais de uma).

Validação antes de commitar (os dois scripts ficam no scratchpad da sessão, e
podem ser recriados a partir desta descrição):
1. **sintaxe** — `mermaid.parse()` da própria lib, rodando em node com jsdom
   (`jsdom@24`; a versão nova não roda no node 18 do servidor). Renderização
   completa não funciona headless, jsdom não implementa `getBBox`.
2. **estrutura** — validador próprio que confere as regras de árvore acima
   (uma raiz, um pai por nó, sem ciclo, folha sempre conduta, decisão com
   rótulo em toda aresta).

Processo, igual para as seis:
1. Escolher o item mais fraco/ausente sozinho, sem perguntar.
2. Pesquisar (WebSearch/WebFetch) fonte real — diretriz mais atual (ESC, AHA/ACC,
   SBC) para conteúdo clínico; Wikimedia Commons/PMC Open Access para imagem;
   PubMed/journal original para estudo — cruzando pelo menos duas fontes quando
   possível.
3. Escrever seguindo exatamente o padrão de front matter/JSON dos itens já
   existentes na mesma pasta (review_status: revisado, source_refs/reference
   com citação completa e verificável).
4. Nunca inventar dose, valor numérico, licença de imagem, DOI, PMID, número de
   norma ou achado que não veio de uma fonte real consultada nesta sessão.
   **Onde não houver certeza, sinalizar explicitamente com o texto literal
   `VERIFICAÇÃO HUMANA NECESSÁRIA`** no campo correspondente, em vez de omitir
   ou de preencher com suposição.
   *(Esta regra foi invertida pelo `BRIEFING_CLAUDE_CODE.md`, decisão do Rafael
   em 28/07/2026. A regra anterior mandava omitir o dado em silêncio. Vence o
   briefing: um dado faltando sem marcação é indistinguível de um dado que
   ninguém procurou, e some da fila de revisão.)*
5. Fazer git add + git commit com mensagem descritiva.
6. Fazer git push.
7. **Entregar em lotes e apresentar cada lote ao Rafael antes de publicar.**
   Conteúdo clínico não vai a produção sem esse checkpoint — não marcar a
   tarefa como concluída sem ele. Escrever, commitar e importar pode seguir
   sem pausa; o que exige o aval é o passo de **publicar** (`published = true`).
   *(Também invertido pelo `BRIEFING_CLAUDE_CODE.md` em 28/07/2026. A regra
   anterior dizia para não pausar em nenhum momento.)*

## O que nunca fazer sem perguntar
- Nunca alterar código de backend/frontend na rotina de expansão de biblioteca
  (só content/ e os JSON das seis frentes).
- Nunca reescrever ou apagar documento já existente sem justificativa clara.

## Stack técnica
- Backend: FastAPI (Python), SQLAlchemy 2.0 (`Mapped[...]`/`mapped_column`), Alembic.
- Banco: PostgreSQL 16 com extensão `pgvector` (embeddings, índice hnsw),
  `pg_trgm` e `unaccent` (busca full-text/fuzzy).
- Frontend: React + TypeScript + Vite. Rotas em `frontend/src/App.tsx`.
  Chamadas de API centralizadas em `frontend/src/lib/api.ts` (token JWT,
  tratamento de 401, helpers get/post/patch/put/delete).
- Deploy: Docker Compose (`docker-compose.prod.yml`), serviços:
  `db` (pgvector/pgvector:pg16), `redis`, `backend`, `frontend-build`
  (container one-shot: builda e sai, não fica "rodando" — isso é normal),
  `caddy` (HTTPS automático).
- Domínio: https://meucardio.med.br

## O que já foi feito
- Deploy inicial resolvido: havia um bug grave no fluxo de migração — o script
  usava `alembic stamp_revision` (só marca "já aplicado", não roda o SQL de
  fato) em vez de `alembic upgrade head`. Isso deixava o banco vazio mesmo com
  o Alembic dizendo "tudo em dia". Corrigido com `DROP SCHEMA public CASCADE`
  + `CREATE EXTENSION vector` + `alembic stamp base` + `alembic upgrade head`.
  **Nunca rodar `stamp_revision`/`stamp` sem garantir que o schema real
  corresponde — é a causa raiz desse incidente.**
- Conteúdo científico importado (233 documentos) e publicado
  (`documents.published = true` via SQL direto, não pela rota
  `/api/admin/documents` — ciente de que isso pula o registro de auditoria).
- IA indexada: 233 documentos, 1328 chunks com embeddings.
- Login do admin corrigido (usuário criado pelo `bootstrap.py` no startup do
  backend, a partir de `ADMIN_EMAIL`/`ADMIN_PASSWORD` do `.env`).
- Rebranding: "Serviço de Cardiologia" → "Guia de Cardiologia" em todos os
  arquivos do frontend. Removida referência institucional antiga do
  `vite.config.ts` (verificar se restam outras menções).
- Login (`Entrar.tsx`): logo aumentada (340px), botão de mostrar/ocultar
  senha, link "Assine já" apontando para `/assinatura`.
- Logo adicionada no cabeçalho de todas as páginas (`Shell.tsx`) — **checar
  se o rebuild do frontend após essa mudança + a instalação do `mermaid`
  concluiu com sucesso, a conexão caiu no meio do processo antes de eu
  confirmar.**
- "Apoio" como rótulo ao lado do logo da Biolab (`ApoioBiolab.tsx`).
- Assinatura via Stripe (modo teste): produto + preço criados (R$20/mês),
  modelo `Subscription` (`backend/app/models/subscription.py`), router
  `backend/app/api/billing.py` (`/billing/checkout`, `/billing/status`,
  `/billing/webhook`), página `frontend/src/pages/Assinatura.tsx`. Webhook
  registrado no painel Stripe apontando para
  `https://meucardio.med.br/api/billing/webhook`. Chaves no `.env`:
  `STRIPE_PUBLISHABLE_KEY`, `STRIPE_SECRET_KEY`, `STRIPE_WEBHOOK_SECRET`,
  `STRIPE_PRICE_ID` (valores reais só no `.env`, nunca commitados).
- Fluxogramas clínicos no ar: dependência `mermaid` no `package.json`,
  componente `frontend/src/components/Fluxograma.tsx`, `Documento.tsx`
  detectando `kind === "fluxograma"`, página de listagem `/fluxogramas` e item
  de menu no `Shell.tsx`. Rebuild confirmado em produção — o `mermaid` é
  servido como chunk separado e a rota responde. 16 fluxogramas publicados,
  todos no formato de árvore de decisão.
- Minha Conta implementado (commit `d13c330`): `PATCH /api/auth/me`,
  `POST /api/auth/alterar-senha`, `POST /api/billing/portal` (Stripe Customer
  Portal) e a página `frontend/src/pages/MinhaConta.tsx` em `/minha-conta`.
  **Falta o deploy** — ver "O que falta fazer".
- **Customer Portal: funciona em modo de teste, confirmado na marra.** Criar
  uma sessão do portal (`POST /v1/billing_portal/sessions`) com a chave
  `sk_test_` do `.env` devolve uma URL válida — testado com um cliente
  descartável, depois apagado. É exatamente o que `POST /api/billing/portal`
  faz, então o botão "Gerenciar assinatura" está destravado do lado do Stripe.
- **Não use `GET /v1/billing_portal/configurations` para saber se o portal
  está configurado.** Esse endpoint lista só as configurações criadas
  explicitamente via API; a configuração padrão feita pelo painel **não
  aparece**, e o endpoint devolve `0` mesmo com o portal funcionando. Foi um
  diagnóstico errado já cometido aqui. O teste que vale é tentar criar a
  sessão de verdade.
- A conta Stripe está com `details_submitted: true` e `charges_enabled:
  false` — ainda não cobra de verdade, o que mantém o `.env` em `sk_test_`.
- **Rebranding concluído e verificado a zero.** Varredura no repositório
  inteiro, nos arquivos binários rastreados e no banco (88 itens das quatro
  frentes, mais a busca full-text sobre o corpo dos documentos publicados):
  nenhuma ocorrência da marca anterior. Foram corrigidos, entre outros, o
  `<title>` da página, o nome do PWA, o pacote do app Android (renomeado para
  `br.med.meucardio`, com `MainActivity.java` movido de diretório), a URL do
  Capacitor, `DEPLOY.md`, `COBERTURA.md`, `backend/README.md`, a chave do
  localStorage e um parágrafo de andaime que havia vazado para um documento
  publicado da biblioteca.
- A chave do token no localStorage é `meucardio.token`. Houve uma migração
  automática a partir da chave antiga em `frontend/src/lib/api.ts`, removida
  depois que a varredura de resíduos foi concluída — quem não abria o site
  desde então precisou entrar de novo, o que é esperado.

## O que falta fazer
Ordem de prioridade herdada das metas: primeiro o que destrava a cobrança da
assinatura (itens 1 e 3), depois amplitude de conteúdo (item 2).

1. **Subir o deploy do Minha Conta.** O código está commitado e no GitHub, mas
   o container em produção ainda roda a versão anterior — o Claude não tem
   senha de sudo para o Docker no servidor, então quem roda é o Rafael:
   `sudo docker compose -f docker-compose.prod.yml up -d --build backend frontend-build`.
   Enquanto isso não rodar, `/minha-conta` responde 404 em produção.
2. **Ampliar os fluxogramas clínicos.** Infraestrutura e formato prontos; 16
   documentos publicados (SCA, FA, IC, HP, síncope, TEP, estenose aórtica,
   diabetes, gravidez, DAP, CDI, choque cardiogênico, endocardite, síndrome
   aórtica aguda, cardiomiopatia hipertrófica, hipertensão arterial). Formato
   obrigatório de árvore de decisão: ver a seção própria acima. Patologias
   ainda sem fluxograma, em ordem sugerida: regurgitação mitral, miocardite,
   amiloidose cardíaca, bradiarritmia e indicação de marcapasso, taquicardia
   de QRS largo e TV, síndrome coronariana crônica, pericardite, cardiopatia
   congênita do adulto, cardio-oncologia, avaliação perioperatória, febre
   reumática, dislipidemia e prevenção primária.
3. **Trocar as chaves do Stripe de teste (`pk_test_`/`sk_test_`) para produção**
   (`pk_live_`/`sk_live_`) quando o Rafael decidir ativar cobranças reais —
   requer conta Stripe totalmente verificada. Conferido nesta sessão:
   `details_submitted: true`, mas `charges_enabled: false`, então a conta ainda
   não cobra. É o último bloqueio para faturar de verdade.

## Notas importantes
- O usuário (Rafael) opera via terminal SSH em um app de celular — comandos
  longos ou builds demorados às vezes derrubam a conexão. Prefira comandos
  que não dependam de sessão interativa prolongada quando possível, e
  documente progresso incremental.
- Nunca reproduzir o incidente do item "O que já foi feito" nº 1: sempre
  `alembic upgrade head` de verdade, nunca `stamp` sozinho, exceto quando o
  schema real já foi confirmado como equivalente.
- O domínio de produção é `meucardio.med.br` — nunca usar variações como
  `meucardio.br.br` ou domínios sem TLD completo (erro já cometido uma vez
  na configuração do webhook Stripe).
