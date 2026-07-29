# Corvia — contexto e instruções permanentes

## O que é
Plataforma de apoio à decisão clínica em Cardiologia ("Guia de Cardiologia"),
idealizada e desenvolvida por Dr. Rafael Paes Meirelles (CRM-SP 138266, RQE 134798).
Uso independente, sem vínculo institucional.

Inclui biblioteca científica, fluxogramas clínicos em árvore de decisão,
calculadoras/escores validados, comparador de medicamentos, galeria de imagens,
exames, evidências, estudos, round hospitalar, agenda, modelos de documento,
assistente de IA clínica, gestão de conta e assinatura, e o serviço de
telediagnóstico (laudo e consultoria à distância).

## Identidade do produto
A **Corvia** (https://corvia.med.br) é produto independente e próprio,
**sem vínculo institucional com nenhum hospital ou serviço**. A assinatura da
marca é "O caminho do coração".

O projeto já teve **duas marcas anteriores**, e nenhuma das duas pode voltar:

1. a primeira, ligada a um serviço hospitalar, removida integralmente do
   repositório, do banco e da interface;
2. a segunda, o nome usado até 28/07/2026, abandonado por **risco jurídico** —
   está registrado por outro titular. Por isso o domínio antigo foi
   **desligado, não redirecionado**: mantê-lo no ar, ainda que só redirecionando,
   prolongaria o uso do nome. Decisão do Rafael, registrada no `infra/Caddyfile`.
   Consequência assumida e conferida antes: link antigo, favorito e app já
   instalado deixam de resolver, e não havia assinante pagante nem usuário além
   do administrador.

Regras que decorrem disso:

- Nenhuma marca, nome ou referência anterior — institucional ou do próprio
  produto — pode voltar a aparecer em código, conteúdo, textos de interface,
  metadados ou configuração. Se precisar identificar os termos exatos para uma
  varredura, eles estão no histórico do git (`git log -S`), não neste arquivo —
  mantê-los escritos aqui recria justamente o resíduo que a regra proíbe.
- **Resíduos internos conhecidos do segundo nome, ainda no código** (invisíveis
  ao usuário, cada um com custo próprio para trocar, nenhum resolvido): a chave
  do token no `localStorage`, o valor de `kind` das assinaturas no banco e o
  nome do índice único que depende dele, o nome do logger de notificação e
  helpers internos do `billing.py`. Trocar a chave do token desloga todo mundo;
  trocar o `kind` é migração de dado. Não mexer sem decisão explícita.
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
  tratamento de 401, helpers get/post/patch/put/delete, `upload` para
  multipart e `blob` para arquivo protegido). **`FormData` não pode receber
  `Content-Type` manual** — o browser precisa gerar o boundary; e um
  `<a href="/api/...">` para arquivo protegido toma 401, porque a API
  autentica por header `Bearer`, não por cookie. Use `api.blob()`.
- Deploy: Docker Compose (`docker-compose.prod.yml`), serviços:
  `db` (pgvector/pgvector:pg16), `redis`, `backend`, `frontend-build`
  (container one-shot: builda e sai, não fica "rodando" — isso é normal),
  `caddy` (HTTPS automático). Volumes: `sitefiles` (build do frontend),
  `userfiles` (foto de perfil, servido pelo Caddy em `/fotos/*`) e
  `examefiles` (exames cifrados, **não** montado no Caddy).
- Domínio: https://corvia.med.br (o Caddy atende também `www.corvia.med.br`).
  É **domínio único**: o antigo foi desligado, e nada no sistema deve voltar a
  apontar para ele.

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
- Rebranding: "Serviço de Cardiologia" → "Guia de Cardiologia" em todo o
  frontend.
- **Paleta oficial aplicada** (navy `#0B2E45`, vermelho `#D5001D`, teal
  `#1C7293`, off-white, ink, muted, line). O `tokens.css` tem duas camadas:
  tokens de marca e, acima deles, papéis semânticos (`--primaria`, `--acao`,
  `--acento`, `--fundo`, `--texto`). **Componentes usam só os papéis** — trocar
  a cor de um papel é mudança de uma linha. Cabeçalho e títulos em navy, CTA em
  vermelho, link e estado ativo em teal. Verde de sucesso e vermelho escuro de
  erro ficam declaradamente fora da paleta, com o motivo escrito no arquivo:
  comunicam estado do sistema, não identidade. Contraste conferido em 13 pares,
  todos AA. O fio dourado foi removido do sistema — não recolocar.
  Três lugares fora do CSS que precisam acompanhar qualquer troca de paleta: o
  tema do mermaid em `Fluxograma.tsx`, o `theme_color` do PWA em
  `vite.config.ts` e a meta `theme-color` no `index.html`.
- **Painel redesenhado**: contadores viraram barra compacta; o espaço principal
  é "Acesso rápido", com as funções do sistema em cartões que dizem o que cada
  uma resolve. Menu lateral continua — o painel é caminho adicional.
- Login (`Entrar.tsx`): logo aumentada (340px), botão de mostrar/ocultar
  senha, link "Assine já" apontando para `/assinatura`.
- Logo no cabeçalho de todas as páginas (`Shell.tsx`); rebuild confirmado.
- O selo de apoio da Biolab foi **removido** do sistema a pedido do Rafael —
  componente, imagem e usos. Não recolocar.
- Assinatura via Stripe (modo teste): produto + preço criados (R$20/mês),
  modelo `Subscription` (`backend/app/models/subscription.py`), router
  `backend/app/api/billing.py` (`/billing/checkout`, `/billing/status`,
  `/billing/webhook`), página `frontend/src/pages/Assinatura.tsx`. Webhook
  registrado no painel Stripe apontando para
  `https://corvia.med.br/api/billing/webhook`. Chaves no `.env`:
  `STRIPE_PUBLISHABLE_KEY`, `STRIPE_SECRET_KEY`, `STRIPE_WEBHOOK_SECRET`,
  `STRIPE_PRICE_ID` (valores reais só no `.env`, nunca commitados).
- Fluxogramas clínicos no ar: dependência `mermaid` no `package.json`,
  componente `frontend/src/components/Fluxograma.tsx`, `Documento.tsx`
  detectando `kind === "fluxograma"`, página de listagem `/fluxogramas` e item
  de menu no `Shell.tsx`. Rebuild confirmado em produção — o `mermaid` é
  servido como chunk separado e a rota responde. 16 fluxogramas publicados,
  todos no formato de árvore de decisão.
- **Minha Conta no ar e testado em produção**: `GET`/`PATCH /api/auth/me`,
  `POST /api/auth/alterar-senha`, upload e remoção de foto
  (`POST`/`DELETE /api/auth/me/foto`), `GET /api/billing/faturas` (lê do
  Stripe, sem espelhar no banco) e `POST /api/billing/portal`. Colunas `rqe` e
  `photo_url` em `users` (migração `a7f2c8d19e04`). A foto é validada por
  assinatura de arquivo (magic bytes), não por Content-Type nem extensão, com
  limite de 3 MB, e servida pelo Caddy em `/fotos/*` a partir do volume
  `userfiles`. Não implementei upgrade/downgrade de plano: com um plano só,
  seria tela morta.
- **Telediagnóstico completo, menos a assinatura digital.** Modelo
  `ServiceOrder` + `ServiceOrderPatient`, rotas em `app/api/service_orders.py`
  (`/api/pedidos`), páginas `/telediagnostico` (solicitante) e
  `/fila-telediagnostico` (só admin). Escopo fechado: ECG, MAPA, Holter e teste
  ergométrico. Preço calculado no servidor a partir de serviço × urgência —
  nunca recebido do cliente. O pedido só entra na fila quando o webhook do
  Stripe confirma o pagamento.
  - **Cofre** (`app/services/cofre.py`): exame cifrado em repouso com
    AES-256-GCM, chave em `STORAGE_ENCRYPTION_KEY` (só no `.env`; **se ela for
    perdida, os exames ficam ilegíveis para sempre** — precisa estar no backup
    de segredos, separado do backup do banco). Volume `examefiles`, **não
    montado no Caddy**: exame de paciente não pode ter URL alcançável de fora.
    O id do pedido entra como dado autenticado do GCM, então arquivo movido
    para outro pedido não decifra. Toda leitura vai para o `AuditLog`.
  - SLA: prazo conta a partir da confirmação do pagamento. Plantão das 7h às
    22h (America/Sao_Paulo); fora dessa janela, pedido urgente passa a valer
    como eletivo. Decisão do Rafael: o prazo pode ultrapassar o fim da janela.
- **Pagamento único via Stripe** (`mode: "payment"`, `price_data` inline em
  BRL): R$40/R$60 consultoria e R$70/R$100 laudo, eletivo/urgente. O webhook
  trata `checkout.session.completed` filtrando por `mode == "payment"` — sem
  esse filtro, uma assinatura nova cairia no caminho do pedido avulso. Existe
  `POST /api/pedidos/{id}/reconciliar` como rede de segurança para webhook
  perdido: consulta a sessão no Stripe, sem confiar no cliente.
- **Webhook de teste criado via API**, e depois migrado para o domínio novo.
  Hoje existe **um único endpoint**, em `https://corvia.med.br/api/billing/webhook`,
  com 6 eventos. Antes de criá-lo o webhook só existia em modo live, e **nenhum
  evento chegava em teste** — o que significa que o fluxo de assinatura nunca
  havia funcionado de ponta a ponta.
  **Ordem que a migração seguiu, e que vale para a próxima:** remover primeiro o
  webhook que aponta para o domínio a desligar, e só depois desligar o domínio.
  O inverso deixa endpoint cadastrado apontando para lugar nenhum, com evento
  falhando em silêncio — o padrão que já mordeu este projeto duas vezes.
- **Objeto do Stripe não é dict.** Na lib 15.3.1, `.get()` levanta
  `AttributeError` — só subscrito funciona. Existe o helper `_campo()` em
  `billing.py` para isso. Esse erro já causou um 500 no histórico de faturas e
  estava latente no webhook de assinatura, onde quebraria no primeiro
  assinante pagante.
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
- **Primeiro rebranding (saída da marca institucional) concluído e verificado a
  zero.** Varredura no repositório inteiro, nos arquivos binários rastreados e
  no banco (88 itens das quatro frentes, mais a busca full-text sobre o corpo
  dos documentos publicados): nenhuma ocorrência daquela marca. Foram
  corrigidos, entre outros, o `<title>` da página, o nome do PWA, o pacote do
  app Android (com `MainActivity.java` movido de diretório), a URL do Capacitor,
  `DEPLOY.md`, `COBERTURA.md`, `backend/README.md`, a chave do localStorage e um
  parágrafo de andaime que havia vazado para um documento publicado da
  biblioteca.
- **Segundo rebranding (para Corvia), feito em 28/07/2026 em fases.** Interface,
  logo e assinatura "O caminho do coração"; `DOMAIN` e `public_url` — e é o
  `public_url` que mais importa, porque dele saem as URLs de retorno do Stripe
  (checkout, portal, cursos, telediagnóstico) e os links dos e-mails; certificados
  emitidos para os dois domínios *antes* da virada, para não abrir janela sem
  TLS; app Android com nome exibido e `appId` (`br.med.corvia`) novos; e, por
  último, o desligamento do domínio antigo. **Não foi verificado a zero como o
  primeiro** — os resíduos internos conhecidos estão listados em "Identidade do
  produto".
- A chave do token no localStorage ainda é a do nome anterior. Houve uma migração
  automática a partir da chave antiga em `frontend/src/lib/api.ts`, removida
  depois que a varredura de resíduos foi concluída — quem não abria o site
  desde então precisou entrar de novo, o que é esperado.

### Conteúdo: as quatro frentes JSON foram carregadas e verificadas
- **As seções apareciam vazias porque nunca haviam sido carregadas no banco**,
  não por falta de conteúdo. Os carregadores `app/services/carregar_*.py`
  existiam só como scripts avulsos, sem rota que os chamasse. Hoje há
  `POST /api/admin/conteudo/carregar`, `GET /api/admin/conteudo/pendentes` e
  `POST /api/admin/conteudo/publicar` (que também **despublica**, com
  `publicar: false` + lista de slugs obrigatória).
- **Publicados: galeria 36, exames 17, evidências 19, estudos 15.**
- **`published` NUNCA vem do JSON.** Os carregadores copiavam esse campo do
  arquivo por cima do banco, e qualquer recarga despublicava tudo em silêncio —
  aconteceu de verdade com evidências e estudos. Corrigido nos quatro; o motivo
  está escrito no topo de cada carregador.
- **Fase B (verificação) concluída nas quatro frentes.** Nenhuma fabricação:
  15/15 DOIs resolvem no Crossref, todos os PMIDs existem, 36/36 licenças de
  imagem conferem e nenhuma é NC ou ND (importante: o produto é assinatura
  paga). Os defeitos encontrados foram de outra natureza — número errado
  (PEITHO), dado principal ausente (DAPA-HF, POST 2), fonte apontando para o
  artigo errado do mesmo ensaio (CLEAR SYNERGY), atribuição a diretriz errada
  (iSGLT2, colchicina na DAC), 7 fontes inaceitáveis (site de estudante,
  material de operadora, calculadoras, Medscape, site de respostas geradas por
  IA), imagem descrita como o que não é (ECG rotulado como parede anterior,
  sendo inferior) e **contradição entre telas** (ITB com 1,3 no verbete e 1,40
  no fluxograma). Esta última é a mais insidiosa: só aparece quando alguém
  compara duas páginas, que é o que um assinante faz.
- Lição que vale para conteúdo novo: **DOI que resolve não prova nada sobre o
  conteúdo** — é preciso conferir se o artigo que ele abre é o que o registro
  descreve.

## O que falta fazer
Quase nada está pela metade, e as exceções estão nomeadas: a **Tarefa 9** tem
backend sem nenhuma tela que o consuma, e há conteúdo **carregado no banco e
ainda não publicado**, esperando o aval do Rafael — 6 fluxogramas e o registro
da colchicina. Todo o resto que foi construído está commitado, no ar e testado
em produção. As demais pendências são trabalho novo ou decisão do Rafael.

### Bloqueado, esperando o Rafael
1. **Colchicina na pericardite aguda — RESOLVIDO em 29/07/2026, aguardando só a
   publicação.** (`evidencias`, slug `colchicina-adjuvante-na-pericardite-aguda`.)
   O bloqueio era a classe: o registro vinha da diretriz brasileira de 2013 com
   IIa/B, e a extração da ESC 2015 devolvia resultado conflitante. A **ESC 2025
   de miocardite e pericardite** substitui a de 2015 e encerra a dúvida —
   Recommendation Table 10: *"Colchicine is recommended as first-line therapy in
   patients with pericarditis as an adjunct to aspirin/NSAID or corticosteroid
   therapy to reduce subsequent recurrences"*, **Classe I, nível A**. O registro
   está atualizado e `revisado`, com `published = false` esperando o aval.
   **Como a tabela foi lida, porque vale para as próximas diretrizes:** o PDF do
   Oxford Academic usa fonte subset **sem `/ToUnicode`**, e o `ler_pdf.py` avisa
   que o texto é ilegível — corretamente. O mapa glifo→caractere é um
   deslocamento constante de 27, e `.claude/ferramentas/decodifica_cid_offset.py`
   converte só os trechos cifrados. Confirmar o offset contra um texto conhecido
   antes de confiar na saída: offset errado produz texto plausível e errado.
2. **Credencial VIDAAS de homologação/API** — pedida, sem retorno até
   28/07/2026. Bloqueia a assinatura digital do telediagnóstico e a Tarefa 4
   inteira. Regra que não se flexibiliza: **nunca simular a assinatura.** A rota
   `POST /api/pedidos/{id}/responder` já devolve aviso explícito de que
   registrar resposta em pedido de laudo não emite laudo assinado.
3. **Chaves do Stripe de teste para produção** (`pk_live_`/`sk_live_`). A conta
   está com `details_submitted: true` e `charges_enabled: false` — ainda não
   cobra. É o último bloqueio para faturar de verdade. Ao trocar, lembrar que
   **portal e webhook são configurados por modo**: os de teste não valem em
   live, e vice-versa.

### Trabalho novo
4. **Medicamentos — 90 no ar, todos `pendente_revisao`, 17 com marcação de
   verificação.** Conferido item a item em 29/07/2026 contra o banco:
   `total 100 · publicados 90 · não publicados 10`, e o conjunto publicado é
   **exatamente** o dos 90 slugs do `medicamentos/metadados.json`. Ou seja, não
   há sobra da base antiga no ar — os órfãos são justamente os 10 que **não**
   estão publicados.
   - **`/api/drugs`, `/compare` e `/{slug}` filtram por `published`, não por
     `review_status`.** Por isso os 17 verbetes que carregam
     `VERIFICAÇÃO HUMANA NECESSÁRIA` estão visíveis a qualquer assinante hoje.
     Verificado buscando os slugs marcados pela rota pública — ela devolve 200
     para os 17. **Decisão pendente do Rafael:** despublicar só esses 17,
     despublicar os 90, ou manter e priorizar a verificação.
   - **Os carregadores fazem upsert por slug e nunca apagam.** Verbete removido
     do JSON continua no banco como linha órfã despublicada — é a origem exata
     dos 10: `metoprolol-succinato`, `metoprolol-succinato-de-liberacao-prolongada`,
     `metoprolol-succinato-e-tartrato`, `nitratos-nitroglicerina-dinitratomononitrato-de-isossorbida`,
     `nitroglicerina-dinitrato-de-isossorbida`, `prasugrel-cloridrato`,
     `sotalol-cloridrato`, `trimetazidina-dicloridrato`, `verapamil-diltiazem` e
     `warfarina`, todos duplicatas fundidas. **Risco latente:** qualquer rotina
     que publique "tudo" ressuscita esses fantasmas, com apresentações que não
     conferem. Falta uma varredura de órfãos, e ela não existe hoje.
   `extrair_drugs_de_markdown.py` reconstruiu os campos estruturados a
   partir dos 100 documentos de `content/Farmacologia`. O ZIP original
   (`knowledge/medicamentos/*.md`, que o `popular_drugs.py` lê) **não existe
   mais neste servidor** — procurado em todo o sistema de arquivos, dentro de
   todo zip/tar e no histórico completo do git. Não procurar de novo.
   Falta, antes de publicar: conferir contra fonte e resolver o
   **`drug_class` com 89 valores distintos para 99 fármacos**. A classe veio
   de cabeçalho em prosa ("Betabloqueador não seletivo com atividade alfa-1
   bloqueadora adicional"), então serve para ler mas é inútil como filtro —
   e é exatamente por ela que a API filtra. Precisa de um campo canônico ao
   lado do descritivo, não de substituição.
   Também vazios por decisão, nunca por esquecimento: `half_life_hours`,
   `sbp/dbp_reduction_mmhg` e `commercial_presentations` — os três exigem
   escolha de revisor ou bula/ANVISA, e um extrator que os adivinhasse
   produziria o dado sem procedência que a Fase B passou semanas removendo.
5. **Ampliar os fluxogramas.** **17 publicados** (SCA, FA, IC, HP, síncope, TEP,
   estenose aórtica, diabetes, gravidez, DAP, CDI, choque cardiogênico,
   endocardite, síndrome aórtica aguda, cardiomiopatia hipertrófica, hipertensão
   arterial, parada cardiorrespiratória), todos em árvore de decisão. Formato
   obrigatório: ver seção acima.
   **Mais 6 escritos, validados e carregados no banco em 29/07/2026, ainda
   `published = false` esperando o aval**: síndrome coronariana crônica (ESC
   2024), regurgitação mitral (ESC/EACTS 2025), bradiarritmia e marcapasso
   (ESC 2021), taquicardia de QRS largo (ESC 2019), pericardite aguda e
   miocardite aguda (ESC 2025).
   Ainda sem fluxograma: amiloidose cardíaca, cardiopatia congênita do adulto,
   cardio-oncologia, avaliação perioperatória, febre reumática, dislipidemia.
6. **Tarefa 4 do briefing — documentos com assinatura digital.** Existe base
   parcial (`prescriptions.py`, `documents.py`), mas **não há geração de PDF**
   nem assinatura. Receita de controle especial (Portaria 344/98) tem regra
   própria de numeração, via, validade e retenção — decidir o formato com o
   Rafael antes de implementar, como o próprio briefing pede.
7. **A busca não cobre as frentes novas.** `app/api/search.py` consulta só a
   tabela `documents`. Galeria, exames, evidências e estudos são invisíveis
   para a busca — 88 itens publicados que ninguém encontra pesquisando.

### Estado das tarefas 8 a 26 do briefing 2
Medido em 29/07/2026 direto sobre o código e o `git log`, não sobre o que este
arquivo dizia antes. **Concluída** aqui significa "existe rota + tela + conteúdo
e responde"; não significa auditada.

| # | Tarefa | Estado |
|---|---|---|
| 8 | Checador de interação medicamentosa | **Não começou.** Só o campo `interactions` em `models/drug.py` e a aba no comparador — não há cruzamento fármaco × fármaco. |
| 9 | Alerta de atualização de diretriz | **Backend pronto, sem tela.** `api/guidelines.py` tem entidade, `/impacto`, marcar substituída, `/meus-alertas` e envio. **Nada no frontend consome `/meus-alertas`** — o alerta existe e o médico não vê. |
| 10 | Indicadores pessoais | **Concluída.** `/api/indicadores/meus` + `Indicadores.tsx`. |
| 11a | Casos clínicos interativos | **Não começou.** |
| 11b | Trilhas de estudo | **Concluída.** 3 trilhas, `/api/trilhas` com progresso, `Trilhas.tsx`/`Trilha.tsx`. |
| 12 | Material educativo para o paciente | **Concluída.** 4 itens, `/api/material-paciente` com PDF. |
| 13 | Leitura assistida de ECG (v1) | **Não começou.** |
| 13b | Notificação ANVISA | **Não começou.** Sem dossiê, sem arquivo de gerenciamento de risco (ISO 14971), sem IFU/rotulagem. |
| 15 | Modo Emergência | **Concluída**, inclusive o offline: cache em `localStorage` com aviso "cópia de \<data\>". 10 protocolos. |
| 16 | Modo Apresentação/Ensino | **Concluída.** `ExportarApresentacao` + `/api/biblioteca/{slug}/apresentacao`, com anotação do médico. |
| 18 | Checklist de alta | **Concluída.** 3 checklists, aplicações com marcação item a item. |
| 19 | Contraindicação por condição especial | **Não começou.** |
| 20 | Roteiro de conversa difícil | **Concluída** como conteúdo, em `content/Comunicação_clínica/`. |
| 21 | Painel — segunda passada | **Não começou.** `Painel.tsx` ainda é lista plana de 16 funções, sem agrupamento por tema e sem Emergência, Apresentação, Checklist, Trilhas, Indicadores, Cursos e Material do paciente. |
| 22 | Verificação com mais autonomia | **Em andamento.** Restam **66 marcações**: 48 em `content/` e 18 em `medicamentos/` (17 registros). Zero nas quatro frentes JSON. |
| 23 | Procurar o arquivo antigo de Medicamentos | **Concluída, resultado negativo.** Não existe. Base reconstruída de `content/Farmacologia` — ver item 4. |
| 24 | Cursos parceiros | **Concluída no código.** `partner_course`, `/api/cursos` (assinar, material, admin, resumo financeiro), volume `cursofiles`. Sem parceiro real cadastrado. |
| 25 | — | **Não existe** em nenhum briefing nem em nota. |
| 26 | Destaque de curso no Painel | **Concluída.** `CursoDestaque` no Painel + `/api/cursos/destaque`. |

**Gargalo comum a 8 e 19:** as duas dependem da base de Medicamentos, que está
no ar mas não revisada (item 4). Construir o checador antes disso é cruzar dados
que ninguém conferiu.

### No fim da fila: preço, marca e relatório de prescrição
Três tarefas pedidas pelo Rafael em 28/07/2026, aprovadas para o **fim** da
fila — depois de tudo que já estava planejado. O levantamento abaixo já foi
feito sobre a lista real da CMED de 21/07/2026 (12,4 MB), não sobre suposição;
não refazer.

10. **Tarefa A — marcas, laboratório, apresentações e preço via CMED.**
    Fonte obrigatória, sem exceção: lista de preços da CMED em
    `gov.br/anvisa/pt-br/assuntos/medicamentos/cmed/precos`. Nenhum preço de
    outra origem.
    O que a planilha é: **25.702 linhas, 2.053 substâncias, 74 colunas**,
    header na linha 42, dados a partir da 43. Traz `LABORATÓRIO`, `PRODUTO`
    (marca), `APRESENTAÇÃO`, `EAN`, `REGISTRO`, `TARJA`, `TIPO DE PRODUTO`.
    Quatro achados que definem o desenho:
    - **Não existe coluna por UF.** São 13 alíquotas de ICMS, cada uma com
      variante "ALC" (Áreas de Livre Comércio). A nota (i) da própria lista diz
      que cabe ao adquirente checar a alíquota do estado de destino — o mapa
      UF→alíquota é responsabilidade nossa, é matéria tributária que muda por
      norma estadual e **não pode ser inventado**: vai como JSON versionado com
      fonte e data por UF, e onde não houver norma rastreável entra
      `VERIFICAÇÃO HUMANA NECESSÁRIA` com queda para média nacional rotulada.
    - **3.884 apresentações não têm PMC em nenhuma alíquota** — uso restrito
      hospitalar, proibidas de venda por PMC pela Resolução CMED nº 3/2009.
      Exibir "sem preço ao consumidor publicado", nunca em branco nem estimado.
    - **A URL tem timestamp** (`xls_conformidade_site_<AAAAMMDD>_<ms>.xlsx`),
      não é previsível por mês, e o servidor da ANVISA **devolve 403 sem
      User-Agent de browser** (medido: 403 no curl padrão, 200 com UA de
      Chrome). Automação exige raspar o link da página.
    - Parser em **stdlib pura** (`zipfile` + `ElementTree`), já validado no
      arquivo real: o servidor não tem `openpyxl` nem `pip`.
    Casamento com os 99 fármacos, medido: 62/99 por nome cru, **89/99** com
    normalizador que remove sal e parênteses ("Anlodipino (besilato)" ×
    "BESILATO DE ANLODIPINO"). Dos 10 restantes, 3 são grafia e resolvem por
    tabela de sinônimos — a CMED usa `VARFARINA SÓDICA`, `HEMITARTARATO DE
    NOREPINEFRINA`, e desmembra nitratos em `MONONITRATO DE ISOSSORBIDA` /
    `DINITRATO DE ISOSSORBIDA` / `NITROGLICERINA`. Os outros **7 estão
    genuinamente ausentes da CMED**: bivalirudina, cangrelor, disopiramida,
    dronedarona, flecainida, mavacamteno e vericiguate — isso é informação
    clínica válida ("sem preço regulado publicado no Brasil"), não uma falha.
    Rótulo obrigatório na interface: **"Preço máximo ao consumidor — teto
    regulado pela CMED, <UF>, ICMS <x>%, lista de <data>"**. Nunca "preço
    médio": PMC é teto, farmácia vende abaixo. UF padrão vem de
    `users.council_state`, com seletor ao lado — é a UF do conselho, que nem
    sempre é onde o paciente compra.
    Atualização mensal automática (preferência do Rafael): rota
    `POST /api/admin/cmed/atualizar` mais agendador diário, **um só caminho de
    código** para manual e automático; só baixa se o timestamp mudou; carga em
    transação única. Tabela `cmed_versions` com data de publicação, hash e nº
    de linhas — sem ela não dá para provar de qual lista veio um preço.
11. **Tarefa B — sugestão de marca durante a prescrição.** Depende da A.
    Ponto estrutural: `Prescription.items` hoje é `{"drug_name": <texto
    livre>}`. Precisa ganhar `drug_slug`, `brand_name`, `manufacturer`,
    `ggrem`, `pmc_snapshot`, `uf` e `cmed_version` — **snapshot do preço no
    momento da prescrição**, porque a lista muda todo mês e relatório de junho
    não pode ser recalculado com preço de agosto. Genérico continua sendo o
    padrão do campo; marca é escolha explícita, **nunca seleção automática**.
    Conferir antes de implementar o alcance da Lei 9.787/1999 (denominação
    genérica) fora do SUS — não afirmar de memória.
12. **Tarefa C — relatório de medicações prescritas, na Minha Conta.**
    Depende da B: agregar `drug_name` de texto livre por marca e laboratório
    dá contagem sem sentido. Prescrições anteriores à B entram por casamento
    aproximado e **rotuladas como tal**. Filtro por período, agregando por
    fármaco + marca + laboratório, sempre restrito a `created_by` — cada médico
    só vê o próprio. **Sem nome de paciente**: é contagem agregada, e manter
    dado de paciente fora do relatório é a escolha certa sob a LGPD.
    Exportação em PDF **não existe no sistema** — a escolha do renderizador
    deve ser feita aqui e reaproveitada nas tarefas 12 e 16 do briefing 2, em
    vez de decidida duas vezes.

13. **Tarefa 24 — área de cursos parceiros (revenda com repasse).** Definida
    pelo Rafael em 28/07/2026 como a tarefa seguinte à 23 do briefing 2, no
    **último lugar da fila**. Funcionalidade comercial: cursos de preparação
    para o Título de Especialista em Cardiologia, de parceiros externos
    (negociação em andamento), vendidos por assinatura dentro da Corvia.
    **O que o sistema faz e o que não faz:**
    - **Não hospeda vídeo.** Aula ao vivo e gravada continuam no ambiente do
      parceiro. A Corvia guarda, por curso, um link de acesso à aula ao vivo
      e um link para as gravadas, e redireciona o aluno.
    - **Guarda o material de apoio.** Apostila e documento enviados pelo curso
      ficam arquivados aqui, no mesmo padrão de armazenamento de arquivo já
      usado no resto do sistema.
    - **Vincula ao conteúdo existente.** Cada curso, módulo ou aula precisa
      poder apontar para trilha de estudo e/ou caso clínico da plataforma
      (Tarefa 11), para o aluno praticar sem sair da Corvia.
    **Cobrança — repasse com margem:**
    - Cada curso tem preço definido pelo parceiro (X). A Corvia cobra
      X + margem definida por nós e repassa X ao parceiro.
    - Via **Stripe Connect** (contas conectadas), com repasse automático na
      própria cobrança — nada de transferência manual.
    - **Preço e margem são por curso, configuráveis** — nunca fixados no código.
    - É **adicional** à assinatura de R$20/mês, não substitui: o médico pode
      assinar só a Corvia, ou a Corvia mais um ou mais cursos.
    - Nota fiscal dos dois lados está sendo tratada com o contador, não é
      decisão técnica — mas os registros internos precisam **separar receita
      própria de valor de repasse a terceiro**, senão o faturamento aparece
      inflado pelo dinheiro que só passa por aqui.
    - Ainda não há parceiro fechado: o primeiro curso é cadastrado à mão, sem
      interface de autocadastro para o parceiro.
    **Destaque no Painel principal** (acréscimo pedido no mesmo dia): banner ou
    cartão visualmente diferenciado **dentro do Painel**, não escondido em
    submenu, com nome do curso, frase de destaque (por exemplo índice de
    aprovação, *se o parceiro fornecer o dado*) e link direto para a página do
    curso **dentro da Corvia**. Trocar o curso em destaque tem de ser fácil,
    e o espaço deve **sumir por inteiro quando não houver curso ativo** — sem
    moldura vazia nem texto de exemplo no ar. Cadastrar `Corvia Curso` como
    exemplo.
    **Três bloqueios estruturais levantados antes de começar, já medidos:**
    1. `subscriptions.user_id` é **`unique=True`** — o banco impõe **uma
       assinatura por médico**. "Corvia + um ou mais cursos" é impossível sem
       migração que remova a restrição e acrescente discriminador de tipo e
       referência ao curso.
    2. O webhook separa os fluxos por `mode == "payment"`. Assinatura de curso
       também é `mode: "subscription"` e cairia no mesmo caminho da assinatura
       da Corvia, sobrescrevendo o estado dela. Precisa de discriminação por
       metadata, não por `mode`.
    3. **Metade da Tarefa 11 existe agora.** As trilhas de estudo (11b) foram
       construídas — 3 trilhas, `/api/trilhas`, com progresso. **Casos clínicos
       interativos (11a) continuam não existindo.** Então o vínculo curso →
       trilha já pode ser real; o vínculo curso → caso clínico segue como
       referência opcional, inerte até a 11a.
    Régua que vale aqui como no resto do produto: **índice de aprovação é
    afirmação de terceiro.** Ou o parceiro fornece por escrito e o número
    aparece atribuído a ele, ou não aparece. Não inventar, não arredondar, não
    exibir número sem origem declarada.

### Decisões pendentes de terceiros
14. **Revisão jurídica do TCLE** e definição de encarregado de dados (DPO). O
   próprio modelo diz que precisa disso antes do uso em produção.
15. **Prazo de retenção** de exame e laudo: segue regra de guarda de prontuário,
   sem exclusão automática (decisão do Rafael); o prazo exato ele confirma com
   o jurídico. **Pedido abandonado** — com exame e dados de paciente gravados
   antes do pagamento — por ora não é expurgado, por decisão dele.

## Notas importantes
- O usuário (Rafael) opera via terminal SSH em um app de celular — comandos
  longos ou builds demorados às vezes derrubam a conexão. Prefira comandos
  que não dependam de sessão interativa prolongada quando possível, e
  documente progresso incremental.

### Como o deploy funciona na prática
- **O Claude não tem senha de sudo, então não roda Docker.** Todo build,
  restart, migração e SQL no banco dependem do Rafael executar. Entregue o
  comando pronto, numa linha, e diga exatamente o que ele faz.
- **Conteúdo não precisa de deploy.** Escrever em `content/` ou nos JSON e
  acionar `POST /api/admin/import` ou `/api/admin/conteudo/carregar` publica
  sem rebuild. Só código exige build.
- **Migração vem antes do rebuild.** O startup do backend **não roda alembic** —
  o `init_db()` só faz `create_all`, que cria tabela nova mas **nunca adiciona
  coluna em tabela existente**. Subir código que espera coluna nova sem migrar
  quebra o backend. E como `migrations/versions` é bind mount, o container
  em execução já enxerga a migração nova: dá para migrar antes de rebuildar.
  Escreva migração **idempotente** (conferir a coluna no catálogo antes de
  criar) — este banco já teve `alembic_version` fora de sincronia.
- Quando o Caddyfile ou um volume mudar, o `caddy` também entra no rebuild.
- Dá para testar muita coisa sem Docker: a API responde em
  `https://corvia.med.br/api`, e o login de admin sai de
  `ADMIN_EMAIL`/`ADMIN_PASSWORD` do `.env`. Webhook do Stripe pode ser testado
  assinando o payload com o `STRIPE_WEBHOOK_SECRET` (HMAC-SHA256 de
  `timestamp.corpo`), que é exatamente o que o Stripe faz.
- Para validar mermaid e a estrutura de árvore dos fluxogramas existem dois
  scripts em `.claude/ferramentas/`. Precisam de `jsdom@24` (a versão nova não
  roda no Node 18 do servidor). Renderização completa não funciona headless —
  jsdom não implementa `getBBox`; `mermaid.parse()` é o que dá para validar.
- Nunca reproduzir o incidente do item "O que já foi feito" nº 1: sempre
  `alembic upgrade head` de verdade, nunca `stamp` sozinho, exceto quando o
  schema real já foi confirmado como equivalente.
- O domínio de produção é `corvia.med.br` — nunca usar variações como
  `corvia.br.br` ou domínios sem TLD completo (erro já cometido uma vez na
  configuração do webhook Stripe). E **nunca voltar a usar o domínio anterior**:
  ele foi desligado por risco jurídico, não por questão técnica, e qualquer
  chamada a ele hoje falha no TLS — não é redirecionamento, é porta fechada.
