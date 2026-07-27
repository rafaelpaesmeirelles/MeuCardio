# MeuCardio — contexto e instruções permanentes

## O que é
Plataforma de apoio à decisão clínica em Cardiologia ("Guia de Cardiologia"),
idealizada e desenvolvida por Dr. Rafael Paes Meirelles (CRM-SP 138266, RQE 134798).
Uso independente, sem vínculo institucional.

Inclui biblioteca científica, calculadoras/escores validados, comparador de
medicamentos, galeria de imagens, exames, evidências, estudos, round hospitalar,
agenda, modelos de documento, assistente de IA clínica, e (em construção)
fluxogramas visuais de investigação/tratamento por patologia.

## Mudança de foco: de CardioBenê para MeuCardio
O projeto nasceu como **CardioBenê**, ferramenta interna ligada a um serviço
hospitalar. Ele **deixou de ser isso**. Hoje é o **MeuCardio**
(https://meucardio.med.br): produto independente, próprio, sem vínculo
institucional com nenhum hospital ou serviço.

Consequências práticas dessa mudança, válidas para qualquer trabalho no repo:
- Nenhuma marca, nome ou referência institucional antiga deve sobreviver em
  código, conteúdo, textos de interface, metadados ou configuração. Ao
  encontrar qualquer resíduo (inclusive "Beneficência Portuguesa de Ribeirão
  Preto", "CardioBenê", "cardiobene", caminhos `/opt/cardiobene`), remover.
- Nada de fluxo de revisão institucional: a responsabilidade clínica é do
  Rafael, cardiologista responsável pelo projeto.
- O público não é mais uma equipe interna, é o cardiologista brasileiro em
  geral. Linguagem, navegação e conteúdo devem assumir esse leitor.

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
4. Nunca inventar dose, valor numérico, licença de imagem ou achado que não veio
   de uma fonte real consultada nesta sessão. Se não conseguir confirmar um dado
   específico, simplesmente não incluir esse dado — não escrever nota de aviso,
   não pedir verificação humana no texto, só omitir.
5. Fazer git add + git commit com mensagem descritiva.
6. Fazer git push.
7. Sem pausar para perguntar "posso continuar?" — seguir direto para o
   próximo item mais fraco, repetindo o ciclo, até eu mandar parar.

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
- **Pegadinha do Customer Portal: a configuração do portal é por modo.** O
  Rafael ativou o portal no painel, mas em modo *live* — o link gerado foi
  `https://billing.stripe.com/p/login/fZu9AS6n3bKD30JgGy2sM00`, e link de
  teste teria o prefixo `test_`. Conferido via API com a chave do `.env`
  (`GET /v1/billing_portal/configurations` devolveu **0 configurações**),
  porque o `.env` usa `sk_test_`. Enquanto o portal não for salvo também em
  modo de teste, `POST /api/billing/portal` cai no `InvalidRequestError` e
  devolve 503. A conta ainda está com `charges_enabled: false`, então trocar
  para chave live não é alternativa disponível hoje.
- Rebranding concluído e conferido por varredura no repositório inteiro: além
  do frontend, foram corrigidos o `<title>` da página, o nome do PWA, o app
  Android (pacote renomeado de `br.org.beneficenciaportuguesa.cardiobene` para
  `br.med.meucardio`, com `MainActivity.java` movido de diretório), a URL do
  Capacitor, `DEPLOY.md`, `COBERTURA.md`, `backend/README.md` e a chave do
  localStorage. As duas únicas ocorrências que sobraram são deliberadas: a
  regra neste arquivo, que precisa citar o termo para poder proibi-lo, e o
  nome literal do ZIP legado no histórico do `COBERTURA.md`, que é registro
  de proveniência.
- Chave do token no localStorage passou de `cardiobene.token` para
  `meucardio.token`, com **migração automática** em `frontend/src/lib/api.ts`:
  o `token.get()` lê a chave antiga, copia para a nova e apaga a antiga. Sem
  isso, a troca deslogaria todos os usuários de uma vez. A constante
  `TOKEN_KEY_ANTIGA` existe só para essa migração — pode ser removida quando
  já não houver sessões antigas em circulação.

## O que falta fazer
Ordem de prioridade herdada das metas: primeiro o que destrava a cobrança da
assinatura (itens 1, 3 e 4), depois amplitude de conteúdo (item 2).

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
3. **Salvar a configuração do Customer Portal também em modo de teste**, no
   painel do Stripe: alternar para *Test mode* → Settings → Billing → Customer
   portal → salvar as configurações padrão. Sem isso o botão "Gerenciar
   assinatura" da página Minha Conta devolve 503 enquanto o `.env` usar
   `sk_test_` (ver a pegadinha registrada acima).
4. **Trocar as chaves do Stripe de teste (`pk_test_`/`sk_test_`) para produção**
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
