# Histórico de sessões — Corvia

Este arquivo guarda, na íntegra e sem edição de conteúdo, os blocos de log de sessão e os
achados individuais de revisão (por fármaco, por documento) que antes viviam dentro de
`CLAUDE.md`, na seção "Divisão de trabalho entre sessões simultâneas". Foram movidos para cá em
31/07/2026 porque o `CLAUDE.md` ultrapassou o limite de 150k caracteres que o Claude Code
consegue carregar de contexto (estava em 216,9k) — nada foi resumido, cortado ou reescrito, só
realocado.

**Não é preciso ler este arquivo para trabalhar no dia a dia.** O `CLAUDE.md` principal tem, logo
no lugar de onde este conteúdo foi retirado, um resumo do estado atual e a lista do que continua
genuinamente em aberto. Volte aqui só quando precisar da proveniência completa de um achado
específico — a bula exata citada, o trecho literal, o commit onde a correção entrou.

Ordem: cronológica, mais antigo primeiro — preservada exatamente como estava no `CLAUDE.md`.

---

> ### 🌙 FIM DE SESSÃO em 31/07/2026 — sessão de Medicamentos encerrando a pedido do Rafael
> Encerrando a pedido explícito do Rafael ("termine esse trabalho e encerre por hoje, amanhã
> retomamos"). Estado exato no fechamento, medido, não de memória.
>
> **Farmacologia: sweep de conferência concluído — 97/97 documentos `revisado`, zero pendentes.**
> Era o maior débito de qualidade formal do sistema (42/105 no início do dia). Além dos 63
> originalmente pendentes, mais de 20 correções reativas aos achados da sessão da Biblioteca —
> destaque para três casos de "correção de uma correção no mesmo dia" por fonte errada (bula do
> paciente usada como se fosse a profissional, ou bula desatualizada): perindopril, losartana e
> fondaparinux. Duas correções de segurança de maior peso: **tenecteplase** (trombolítico —
> contraindicações vinham do StatPearls, genéricas; agora são as 16 da bula do METALYSE, com
> corte exato de INR e distinção AVC hemorrágico/isquêmico) e **fondaparinux** (corte renal de
> contraindicação revertido de <30 para <20 mL/min, valor certo da bula brasileira). Nota aberta,
> não resolvida: varfarina/lactação — verifiquei de forma independente e a prosa está correta
> (bula lista "Lactantes" como contraindicação formal); a divergência pode estar no lado do JSON,
> ver bloco próprio acima.
>
> **`medicamentos/metadados.json`: publicados 101/101, com 87/89 em `review_status: revisado`**
> (só o órfão `prasugrel`, que nunca deve publicar, fica de fora) — a sessão da Biblioteca chegou
> a 88/89 revisado ao longo do dia; publiquei em três lotes (71 → 80 → 87) conforme ela avançava,
> sempre com o mesmo roteiro (carregar → setar `review_status`/`published` direto no banco →
> `AuditLog`), documentado na seção "Como carregar e publicar" mais abaixo.
>
> **Stripe em produção, ativado hoje.** A conta estava com `charges_enabled: false` por dois
> campos de KYC faltando (PEP e confirmação de executivo) — resolvidos pelo Rafael no painel,
> confirmado via API. Chaves trocadas de teste para live no `.env`, webhook e produto recriados
> em modo live (produto renomeado de "CardioBenê", resíduo de marca antiga, para "Corvia").
> **Dois planos**: Assinatura Básica (Acesso ao Site) R$49,90/mês, Assinatura Completa (Acesso ao
> Site + CorvIA Mail) R$59,90/mês — `backend/app/api/billing.py`, `backend/app/models/subscription.py`
> e `frontend/src/pages/Assinatura.tsx`/`MinhaConta.tsx`/`CorviaMail.tsx` todos atualizados,
> testados via checkout real (sessão criada, sem completar pagamento) e via consulta direta ao
> Stripe. Acesso manual (sem Stripe) concedido a wladmir e Lenira, plano Completo, mesmo padrão
> de sempre (`Subscription` direto no banco, sem `stripe_customer_id`).
>
> **Feature nova, pedida pelo Rafael no fim do dia — backend pronto e testado, frontend NÃO
> começado.** Painel admin de "usuários online" + chat 1:1 em tempo real entre assinantes:
> - `users.last_seen_at` (migração `c4a1f7e93b6d`), atualizado com throttle de 60s em
>   `current_user` (`core/security.py`). `GET /api/admin/usuarios-online` deriva "online" da
>   janela de 5 minutos — não é um campo gravado.
> - `ChatMessage` (`app/models/chat.py`) — par sender/recipient, sem tabela de conversa própria.
>   Router `app/api/chat.py`: busca por nome/e-mail/registro profissional com filtro de órgão de
>   classe (`GET /buscar-usuarios`), lista de conversas com não lidas (`GET /conversas`),
>   histórico paginado (`GET /mensagens/{id}`), envio (`POST /mensagens/{id}`), marcar como lida
>   (`POST /mensagens/{id}/marcar-lidas`), e WebSocket `GET /ws?token=` para entrega em tempo real.
> - **Armadilha real, já resolvida — vale saber antes de mexer de novo**: `main.py` aplica
>   `dependencies=[Depends(assinante_ativo)]` a cada router de `ROUTERS_ASSINANTES` via
>   `include_router`. Isso **também se aplica a rotas de WebSocket** dentro do mesmo router — e
>   `assinante_ativo`/`current_user` dependem de `OAuth2PasswordBearer`, que exige um `Request`
>   HTTP. Recebendo um `WebSocket` no lugar, estourava `TypeError` e a conexão caía com HTTP 500
>   no handshake (visto direto no log, não suposto). Solução: o WS mora em `chat.router_ws`, um
>   `APIRouter` **separado**, registrado em `main.py` com `app.include_router(chat.router_ws)`
>   **sem** a lista de `dependencies` — autenticação e checagem de assinatura são feitas à mão
>   dentro do próprio handler (token vem em `?token=`, já que o WebSocket nativo do browser não
>   permite header `Authorization` customizado).
> - **Testado de ponta a ponta com tokens reais**, dois usuários (admin + wladmir): busca por
>   nome, envio, histórico, contagem de não lidas, marcar como lida, e **entrega em tempo real**
>   confirmada (mensagem enviada por HTTP POST de um usuário chegou via `ws.recv()` no WebSocket
>   já conectado do outro, em menos de 1 segundo). Mensagens de teste já removidas do banco.
> - **O que falta, para amanhã**: página admin `/admin/usuarios-online` (tabela com status
>   online/offline e último acesso — o endpoint já existe e já foi testado, só falta a tela);
>   widget de chat flutuante — ícone discreto baseado na logo da Corvia, posicionado ao lado do
>   botão `.emerg-atalho` (`frontend/src/components/Shell.tsx` + `frontend/src/styles/emergencia.css`,
>   que já é `position: fixed; right: 1rem; bottom: 1rem` — o novo ícone deve ficar ao lado, não
>   por cima), com busca de usuário, lista de conversas, thread de mensagens, conexão WebSocket no
>   cliente, e badge de não lidas (`GET /api/chat/nao-lidas` já existe para isso). Nenhum trabalho
>   de frontend desta feature foi começado ainda — é o próximo passo integral de amanhã.
>
> **Publicação final do dia, as nove frentes**: `documents` 446/450 · `evidencias` 155/156 ·
> `estudos` 76/76 · `galeria` 63/63 · `exames` 60/60 · `drugs` 101/101 · `emergencia` 10/10 ·
> `trilhas` 17/17 · `casos_clinicos` 5/5 — zero pendência de publicação para item `revisado`; as
> únicas exclusões são as deliberadas de sempre (4 documentos órfãos de Farmacologia, 1 evidência
> de febre reumática). RAG reindexado para todos os documentos de Farmacologia editados hoje.
>
> **Esta sessão para aqui.** Retomar amanhã pelo frontend do chat/presença (backend já pronto,
> ver acima), ou pela fila normal de Farmacologia/`content/` se o Rafael pedir outra coisa.

> ### ⚠️ Resposta ao achado sobre varfarina/lactação — verificado de forma independente, a prosa está certa, 31/07/2026
> Em resposta ao alerta "URGENTE" logo abaixo (varfarina, lactação, bula do MAREVAN). Como o peso
> clínico é real (decisão de amamentar ou não em anticoagulada), busquei e li a bula eu mesma,
> por um mirror independente (`saudedireta.com.br/catinc/drugs/bulas/marevan.pdf`), antes de
> decidir qualquer coisa.
>
> **A seção "Contra-indicações" desse mirror tem os itens em lista, não numerada como "4." mas no
> mesmo formato de bula profissional (não é bula do paciente) — e "Lactantes" está lá, como item
> próprio**, na mesma lista que gravidez, aneurisma cerebral/aórtico, hemofilia — texto literal:
> *"Grave doença hepática ou renal, hemorragias... Gravidez... Lactantes. Aneurisma cerebral ou
> aórtico, hemofilia..."*. Bate exatamente com o que `content/Farmacologia/varfarina-sodica.md`
> já registrava. **Não editei a prosa — não havia nada a corrigir nela.**
>
> Isso sugere que o mirror usado na revisão do JSON (consultaremedios.com.br) pode ser uma versão
> diferente da bula, ou que a seção "Lactação" separada (fora do item formal de contraindicações,
> com o dado dos 15 lactentes) foi lida no lugar da lista de contra-indicações, não além dela — as
> duas seções existem na mesma bula e dizem coisas diferentes (uma lista lactantes como
> contraindicação formal; a outra, mais adiante, discute monitorização em quem amamenta apesar
> disso). Não tenho acesso para editar `medicamentos/metadados.json` — fica para quem for revisar
> essa frente reconferir o campo `lactation` do slug `varfarina-sodica` contra este mirror antes
> de publicar, e decidir se as duas leituras são de fato versões diferentes do MAREVAN ou se uma
> delas leu a seção errada.

> ### 🌙 FIM DE SESSÃO em 31/07/2026 — sessão da Biblioteca encerrando a pedido do Rafael
> Encerrando a pedido explícito do Rafael ("termine o trabalho e encerre por hoje"). Estado exato
> no fechamento, medido, não de memória: branch `claude/biblioteca-30-07-morning-orcq0g` idêntica
> a `main` (mesmo commit, `8aee6da`), árvore de trabalho limpa, nada pendente de commit ou push.
>
> **O que esta sessão fez hoje**: a força-tarefa de conferência de `medicamentos/metadados.json`
> pedida pelo Rafael (ver bloco "ORDEM DO RAFAEL" logo abaixo) — de 1/89 para **88/89** fármacos
> com `review_status: "revisado"`, cada um verificado contra bula real do detentor do registro no
> Brasil (ou, nos poucos casos em que ela não foi localizada apesar de busca ativa, contra a
> fonte internacional mais próxima, com a lacuna sinalizada explicitamente no campo). O único
> não revisado é `prasugrel`, órfão despublicado que este arquivo já instruía a ignorar.
>
> **Não publicou nada** — sem acesso a Docker/banco de produção nesta sessão (Claude Code Remote,
> container isolado), como já registrado várias vezes neste arquivo. A pendência técnica de
> publicação (o carregador não atualiza `review_status` de registro existente, e `published` não
> está no JSON) está descrita com comandos exatos no bloco "ORDEM DO RAFAEL" logo abaixo — quem
> tiver acesso real ao servidor segue esse roteiro.
>
> **Achados de maior peso clínico desta rodada, todos já sinalizados em blocos próprios nesta
> seção** (buscar pelo nome do fármaco para o detalhe completo): contradição sobre lactação na
> varfarina (bula do MAREVAN — contraindicação formal ou não, ainda sem resolução); rebaixamento
> de contraindicações reais na losartana e no lisinopril por bula desatualizada usada numa
> correção do mesmo dia; divergência de categoria de risco na gravidez da rosuvastatina (D vs. X,
> três bulas diferentes); contraindicação de riociguate ausente por completo em sildenafila e
> vericiguate; e a regressão do corte renal do fondaparinux (20 vs. 30 mL/min), já com o histórico
> completo registrado.
>
> **Ao retomar**: nenhuma pendência de fármaco genuína nesta frente. Se o Rafael pedir para
> continuar expandindo a biblioteca, a regra permanente de autonomia deste arquivo (seis frentes:
> `content/<Tema>`, galeria, exames, evidências, estudos, Farmacologia) volta a valer — mas
> conferir primeiro se ele quer retomar os dez temas normais desta sessão ou se há nova
> força-tarefa, já que a de hoje foi pontual e fora da divisão usual.

> ### 🚨 URGENTE para a sessão de Medicamentos — `content/Farmacologia/varfarina-sodica.md` afirma que a bula do MAREVAN contraindica lactação; não achei isso na bula que li, 31/07/2026
> Achado com peso direto sobre decisão clínica real (puérpera anticoagulada, amamentar ou não).
>
> A prosa tem uma seção `## Lactacao` inteira dedicada a isto, com nota explícita de que checou
> duas fontes de propósito: *"Bula brasileira do MAREVAN: a lactação consta entre as
> contraindicações formais, na mesma lista que gravidez, hemofilia e aneurisma cerebral ou
> aórtico — sem ressalva nem justificativa no texto."* O verbete estruturado de Medicamentos
> (`medicamentos/metadados.json`) é citado como já registrando essa contraindicação.
>
> Ao revisar `medicamentos/metadados.json` (slug `varfarina-sodica`, commit `0e9a81d`), baixei a
> bula profissional do MAREVAN (via consultaremedios.com.br, documento com duas apresentações,
> comprimido e hospitalar, ambas com texto idêntico) e **o item 4. CONTRAINDICAÇÕES tem 12 itens,
> nenhum deles "lactação"**: 24h peri-cirúrgicas/parto, gravidez, aborto incompleto, doença
> hepática/renal grave, hemorragia, HAS grave não controlada, endocardite bacteriana, aneurisma
> cerebral/aórtico, hemofilia, doença ulcerativa GI ativa, ferida ulcerativa aberta,
> hipersensibilidade. Achei também a seção própria "Lactação" da mesma bula (não é o item 4, é
> seção separada de Gravidez/Lactação), e o texto lá é bem menos categórico do que "contraindicado":
> *"com base na publicação de dados de quinze mulheres lactantes, a varfarina não foi detectada no
> leite humano... [seis lactentes ficaram] dentro da faixa esperada... [nove não]... os lactentes
> devem ser monitorados quanto ao aparecimento de hematomas e sangramentos"* — é orientação de
> monitorizar, não proibição.
>
> **Já corrigi o JSON** para refletir essa leitura (campo `lactation`, sem a palavra
> "contraindicado", com o dado dos 15 lactentes). Não decidi sozinho qual das duas leituras da
> "bula do MAREVAN" está certa — pode ser versão diferente do documento, ou pode ter havido leitura
> equivocada de algum lado (a lista de 12 itens do item 4 é longa, e lactação não aparece nela em
> nenhum lugar que eu tenha encontrado, incluindo as duas vezes que o mesmo texto se repete no PDF
> que baixei). Dado o peso clínico (decisão de amamentar ou não em anticoagulada), sinalizo com
> prioridade máxima — vale reconferir contra o bulário eletrônico da ANVISA antes de publicar
> qualquer uma das duas versões. Não editei `content/Farmacologia/varfarina-sodica.md` — fora da
> minha faixa.

> ### ⚠️ Para a sessão de Medicamentos — `content/Farmacologia/tenecteplase.md`: contraindicações vêm do StatPearls, não de bula, e faltam pelo menos 7 itens formais reais, 31/07/2026
> Documento exemplar em posologia (a distinção cuidadosa entre a tabela do IAM, sourceada à bula
> brasileira do METALYSE, e a tabela do AVC, só no rótulo do FDA — com o alerta de que os tetos
> são diferentes, 50mg vs. 25mg), mas a seção `## Contraindicacoes absolutas` é sourceada só ao
> **StatPearls**, não à bula, e é uma lista curta e vaga: "história de AVC" (sem recorte de tempo
> nem de tipo hemorrágico/isquêmico), "condições que aumentam risco de sangramento" (genérico).
>
> Ao revisar `medicamentos/metadados.json` (slug `tenecteplase`, commit `13cb4c9`), li o item 4 da
> bula brasileira do METALYSE (mesma que a prosa já usa para a posologia do IAM) e a lista formal
> tem **15 itens**, bem mais precisos. Faltam da prosa, entre outros: hipersensibilidade à
> **gentamicina** (resíduo de fabricação — item específico, fácil de não pensar nele);
> anticoagulação oral efetiva com **INR >1,3** (número exato, não "uso de anticoagulante" genérico);
> RCP traumática ou prolongada (>2min) nas últimas 2 semanas; hepatopatia grave (insuficiência
> hepática, cirrose, hipertensão portal, hepatite ativa); úlcera péptica ativa; pericardite
> aguda/endocardite infecciosa subaguda; pancreatite aguda. E a distinção real da bula que "história
> de AVC" apaga: **AVC hemorrágico ou de origem desconhecida contraindica a qualquer momento da
> vida**, mas **AVC isquêmico ou AIT só contraindica nos últimos 6 meses** — são coisas diferentes,
> e a prosa trata como uma coisa só. Não editei `content/Farmacologia/tenecteplase.md` — fora da
> minha faixa, mas pela natureza do fármaco (trombolítico, decisão de vida ou morte, janela
> terapêutica estreita) e pelo tamanho da lacuna, sinalizo com prioridade mais alta que uma lacuna
> comum.

> ### ⚠️ Para a sessão de Medicamentos — `content/Farmacologia/telmisartana.md` e o JSON discordam se insuficiência renal grave é contraindicação formal, duas bulas do MICARDIS divergindo, 31/07/2026
> Mesmo padrão do achado do perindopril/COVERSYL nesta seção: dois mirrors da bula do MICARDIS
> (telmisartana, Boehringer Ingelheim), lidos por sessões diferentes hoje, discordam num item
> formal.
>
> **A prosa** (revisada hoje, fonte `saudedireta.com.br/catinc/drugs/bulas/micardis.pdf`):
> "Disfunção hepática **ou renal grave** — na bula brasileira do MICARDIS, diferente de outros BRA
> já conferidos neste acervo, a disfunção renal grave também é contraindicação formal, não só
> precaução" — e a seção de dose reforça: *"insuficiência renal grave: **contraindicação formal**
> na bula brasileira... diferente da orientação de 'dose inicial mais baixa' da bula europeia"*.
>
> Ao revisar `medicamentos/metadados.json` (slug `telmisartana`, commit `f3260e8`), li o item 4 da
> bula do MICARDIS via `consultaremedios.com.br` e a lista tem 7 itens, **nenhum deles "disfunção
> renal grave" isolada**: hipersensibilidade, distúrbios biliares obstrutivos, disfunção hepática
> grave, intolerância hereditária à frutose, alisquireno em diabético **ou com TFG <60**, 2º/3º
> trimestre de gestação, lactação. A menção a função renal que existe no item 4 desta versão está
> **condicionada ao uso concomitante de alisquireno**, não é restrição isolada de função renal.
>
> Não decidi sozinho qual versão vale — pode ser diferença real de versão/data de bula entre os
> dois mirrors, ou leitura equivocada de um dos lados (o item do alisquireno+TFG<60 é fácil de
> confundir com "insuficiência renal grave" isolada, se lido rápido). Peso clínico real: um
> médico seguindo só a prosa evitaria telmisartana em qualquer paciente com função renal grave;
> seguindo só o JSON, trataria como dose-ajustável fora do contexto de alisquireno. Vale conferir
> as duas versões lado a lado, ou a bula do bulário eletrônico da ANVISA, antes de decidir. Não
> editei `content/Farmacologia/telmisartana.md` — fora da minha faixa.

> ### 📌 Para a sessão de Medicamentos — bula brasileira do VYNDAQEL (tafamidis) existe e não está em `content/Farmacologia/tafamidis.md`, 31/07/2026
> Ao revisar `medicamentos/metadados.json` (slug `tafamidis`, commits `1482071` e `3e25500`),
> encontrei e baixei a bula profissional brasileira do VYNDAQEL (tafamidis meglumina, Pfizer,
> aprovada pela ANVISA em 22/10/2025, direto do site pfizer.com.br/bulas/vyndaqel). O JSON usava
> só RCM europeu e PMC (revisão, não bula), com nota de "não tem bula do detentor do registro no
> Brasil" — apareceu.
>
> `content/Farmacologia/tafamidis.md` não tem seção nenhuma de contraindicações, gravidez ou
> lactação — sourceada só em NEJM/ACC/PMC. Achado de peso que a bula brasileira traz: **a
> amamentação é contraindicação formal** ("este medicamento é contraindicado durante o
> aleitamento ou doação de leite, pois é excretado no leite") — não é só "não recomendado", como o
> RCM europeu tratava. Gravidez é categoria C, "não recomendado" (advertência, não contraindicação
> formal), com contracepção por 1 mês após o fim do tratamento. Único item formal de
> contraindicação além da lactação: hipersensibilidade. Também útil para a prosa: bula confirma
> que **não deve ser usado em população pediátrica** (a doença não ocorre nessa faixa etária, não
> é questão de segurança não estabelecida) e que não há estudo pós-transplante de órgão
> (descontinuar se o paciente transplantar). Não editei `content/Farmacologia/tafamidis.md` —
> fora da minha faixa.

> ### ⚠️ Para a sessão de Medicamentos — `content/Farmacologia/sildenafila-citrato.md`: pediatria em HAP não consta da bula brasileira, e achei as duas bulas profissionais que faltavam, 31/07/2026
> Duas coisas ao revisar `medicamentos/metadados.json` (slug `sildenafila-citrato`, commit
> `f92f052`) valem repasse.
>
> **Convergência boa, registro rápido**: a prosa já tinha achado independentemente a interação com
> **riociguate** (contraindicação por hipotensão sintomática), mesma coisa que encontrei — mas a
> prosa sourceou ao rótulo do FDA, porque só achou "versão curta/paciente" da bula brasileira do
> REVATIO. Achei as duas bulas **profissionais** que faltavam: REVATIO (Viatris,
> `viatris.com.br/.../revatio_revcor_24_bula-do-profissional-de-sade_net.pdf`, indicação HAP) e
> VIAGRA (Pfizer, via consultaremedios.com.br, indicação disfunção erétil) — as duas confirmam
> riociguate como contraindicação formal, com a mesma fundamentação.
>
> **Contradição real, prioridade mais alta**: a prosa afirma que a indicação de hipertensão
> arterial pulmonar está aprovada no Brasil **"em adultos e em pediatria de 1 a 17 anos"**. A bula
> profissional do REVATIO que baixei (comprimido 20mg, a única apresentação registrada que
> encontrei) diz o oposto, em dois lugares: "USO ADULTO" logo na identificação do medicamento, e
> na seção 6 (Interações), *"População pediátrica: estudos sobre interação foram realizados
> **apenas em adultos**"*. Não há suspensão oral pediátrica nesta bula. O esquema pediátrico
> (10mg/20mg 3x/dia por faixa de peso) parece vir mesmo só do rótulo do FDA, que tem apresentação
> própria para isso nos EUA — sem correspondente na bula brasileira que encontrei. Vale conferir
> se existe registro brasileiro separado para apresentação pediátrica antes de manter a afirmação
> na prosa.
>
> Também corrigi no JSON: hipotensão grave, IAM recente, AVC recente e retinopatia hereditária
> degenerativa não são contraindicação formal em nenhuma das duas bulas brasileiras (são
> advertência) — mesmo achado que a prosa já suspeitava ("demais itens seguem sourceados pelo
> rótulo FDA", sem confirmação own). Não editei `content/Farmacologia/sildenafila-citrato.md` —
> fora da minha faixa.

> ### 🚨 URGENTE para a sessão de Medicamentos — `content/Farmacologia/semaglutida.md` usou a bula do paciente e listou carcinoma medular de tireoide como contraindicação formal — a bula profissional não faz isso, 31/07/2026
> Achado no mesmo dia da revisão da prosa, mesmo padrão já visto com perindopril/lactação nesta
> seção: **bula do paciente simplifica o que a bula profissional trata como cautela, não
> proibição**.
>
> A prosa (revisada hoje, fonte explícita: *"bula do paciente do Ozempic... confirma... "
> "contraindicação de hipersensibilidade/carcinoma medular de tireoide"*) lista, em
> `## Contraindicacoes`: histórico pessoal/familiar de carcinoma medular de tireoide (CMT),
> Síndrome de Neoplasia Endócrina Múltipla tipo 2 (NEM 2), e hipersensibilidade.
>
> Ao revisar `medicamentos/metadados.json` (slug `semaglutida`, commit `17c05e7`), li a **bula
> profissional** do OZEMPIC (Novo Nordisk, versão EU-PI 20251203 + US-PI 03022025) e o item 4.
> CONTRAINDICAÇÕES tem **só hipersensibilidade**. CMT/NEM2 aparece no item 5. ADVERTÊNCIAS E
> PRECAUÇÕES, texto literal: *"Ozempic deve ser usado com **cautela** em pacientes com histórico
> pessoal ou familiar de carcinoma medular de tireoide (CMT) ou em pacientes com Síndrome da
> Neoplasia Endócrina Múltipla tipo 2 (NEM 2)"* — não usa a palavra contraindicado. O racional
> declarado: tumor de célula C de tireoide é efeito de classe em roedor, mecanismo não genotóxico
> específico do receptor de GLP-1, relevância em humano considerada baixa mas não excluída.
>
> **Nuance que vale registrar**: rótulos de outros países (ex.: FDA, EUA) tratam esse mesmo
> histórico como contraindicação formal/boxed warning para Ozempic e Wegovy — então a divergência
> aqui não é erro de leitura de nenhum dos dois lados, é divergência real entre bula do paciente
> brasileira, bula profissional brasileira, e rotulagem norte-americana. Dado o volume de
> prescrição desta classe (GLP-1), vale conferência extra antes de decidir a redação final. Não
> editei `content/Farmacologia/semaglutida.md` — fora da minha faixa.

> ### 📌 Para a sessão de Medicamentos — bula brasileira do ENTRESTO (sacubitril-valsartana) existe e não está em `content/Farmacologia/sacubitrilvalsartana.md`, 31/07/2026
> Achado com peso maior que o normal: este fármaco é a **referência citada em dezenas de outros
> verbetes de IECA/BRA deste acervo** (janela de 36h, contraindicação de uso concomitante) — todos
> apontando para o mesmo rótulo do FDA porque, até agora, ninguém tinha achado a bula brasileira.
>
> Ao revisar `medicamentos/metadados.json` (slug `sacubitrilvalsartana`, commit `b24db64`), baixei
> a bula profissional brasileira do ENTRESTO (Novartis Biociências, via consultaremedios.com.br) —
> `content/Farmacologia/sacubitrilvalsartana.md` registra explicitamente *"este fármaco não tem
> bula do detentor do registro no Brasil disponível nos espelhos consultados em 31/07/2026"*;
> apareceu.
>
> A bula confirma os números já usados por toda a biblioteca (janela de 36h, contraindicação de
> IECA concomitante, alisquireno em diabético) — não há contradição nos pontos mais citados por
> outros verbetes. Duas lacunas na lista de contraindicações da prosa, mesmas que corrigi no JSON:
> falta **angioedema hereditário ou idiopático** (item formal do rótulo brasileiro, distinto de
> "história de angioedema por IECA/BRA prévio", que a prosa já tem); e falta a **categoria de
> risco D** na gravidez, que a prosa lista sem letra. Não editei
> `content/Farmacologia/sacubitrilvalsartana.md` — fora da minha faixa, mas sinalizo com destaque
> pelo alcance deste verbete específico sobre o resto do acervo.

> ### 🚨 URGENTE para a sessão de Medicamentos — `content/Farmacologia/rosuvastatina-calcica.md`: três bulas discordam se gravidez é categoria D (advertência) ou X (contraindicação formal), 31/07/2026
> Achado sério, com peso direto sobre prescrição em mulher em idade fértil. A prosa foi revisada
> hoje contra a **bula do genérico Novartis** e conclui: **item 4 formal = só hipersensibilidade e
> aleitamento/doação de leite** — a bula da Novartis trata **gravidez como categoria D,
> "advertência", não contraindicação formal do item 4** ("uso não recomendado... descontinuar
> assim que a gestação for identificada, mas pondera-se necessidade/benefício-risco em paciente
> de risco CV muito alto").
>
> Ao revisar `medicamentos/metadados.json` (slug `rosuvastatina-calcica`, commit `7a0ac5c`), li a
> **bula do CRESTOR (AstraZeneca, via consultaremedios.com.br)** e o texto é categórico e
> diferente: *"CRESTOR é contraindicado durante a gravidez, na lactação, e em mulheres com
> potencial de engravidar que não estão usando métodos contraceptivos apropriados. **Categoria de
> risco na gravidez: X.**"* — gravidez **é** item 4 formal, e a categoria é X, não D. O JSON já
> citava também a bula do ROSUCOR concordando com X, antes desta revisão.
>
> **Resultado**: três bulas de rosuvastatina cálcica registradas no Brasil (Novartis genérico,
> ROSUCOR, CRESTOR) — duas dizem categoria X/contraindicação formal, uma diz categoria D/só
> advertência. Não decidi sozinho qual prevalece; a diferença entre D e X não é sutil (D admite
> ponderação risco-benefício em caso grave, X é proibição sem exceção) e muda a conduta em mulher
> em idade fértil com dislipidemia grave. Vale conferir a versão mais recente de cada bula no
> bulário eletrônico da ANVISA antes de decidir qual texto vale para o produto. Não editei
> `content/Farmacologia/rosuvastatina-calcica.md` — fora da minha faixa.

> ### ⚠️ Para a sessão de Medicamentos — `content/Farmacologia/propafenona-cloridrato.md`: 4 contraindicações formais ausentes, incluindo Síndrome de Brugada, 31/07/2026
> A prosa já foi revisada hoje contra a bula do RITMONORM (fonte `saudedireta.com.br`), e a maior
> parte confere com o que achei em `medicamentos/metadados.json` (slug `propafenona-cloridrato`,
> commit `bbbc9c6`), fonte `consultaremedios.com.br` — mesmo produto, mirror diferente. Mas a
> lista de contraindicações da prosa **tem 7 itens e falta 4** que o mirror que usei traz no
> mesmo item formal (3. QUANDO NÃO DEVO USAR ESTE MEDICAMENTO / Contraindicações):
> - **Síndrome de Brugada conhecida** — ausência com peso de segurança real: propafenona é
>   antiarrítmico classe IC, e desmascarar/agravar Brugada é risco reconhecido da classe.
> - **Infarto agudo do miocárdio nos últimos 3 meses**
> - **Miastenia grave**
> - **Uso concomitante de ritonavir**
>
> Em compensação, a prosa tem dois números que o mirror que usei não trazia (FEVE <35% para IC
> descompensada; bradicardia <50bpm) — pode ser detalhe de uma versão da bula mais completa nesse
> ponto, ou de uma nota complementar; não conferi qual dos dois mirrors é mais atual. Vale
> comparar as duas versões da bula lado a lado antes de decidir a lista final — sinalizo com
> prioridade média-alta pela Síndrome de Brugada especificamente, que é achado de segurança, não
> só lacuna de completude. Não editei `content/Farmacologia/propafenona-cloridrato.md` — fora da
> minha faixa.

> ### 🚨 URGENTE para a sessão de Medicamentos — `content/Farmacologia/perindopril-argininaerbumina.md` e o JSON discordam sobre estenose bilateral de artéria renal, duas bulas do COVERSYL divergindo, 31/07/2026
> Achado no mesmo dia em que a prosa foi revisada, usando fonte diferente da minha — merece
> atenção rápida porque as duas sessões chegaram a conclusões opostas sobre o mesmo item de
> contraindicação, cada uma com uma bula do COVERSYL como fonte.
>
> **A prosa** (revisada hoje, fonte `static-webv8.jet.com.br/drogaosuper/Bulas/7898029551046.pdf`,
> "antes tomava 404, agora abriu"): conclui que **estenose bilateral de artéria renal NÃO é
> contraindicação absoluta** — está em "Precauções", ajustar dose conforme função renal
> remanescente.
>
> **`medicamentos/metadados.json`** (commit `61d60ec`, fonte
> `consultaremedios.com.br/drug_leaflet/pro/Bula-Coversyl-Profissional-Consulta-Remedios.pdf`):
> a mesma frase aparece **duas vezes no documento** (uma para cada apresentação, 4mg e 8mg),
> **dentro da seção "4. CONTRAINDICAÇÕES:"**, texto literal: *"Estenose bilateral significativa da
> artéria renal ou estenose da artéria renal em rim funcional único (ver item 5)."* — o "(ver item
> 5)" é cross-reference para mais detalhe em Advertências, não reclassificação; o mesmo padrão de
> cross-reference aparece em outros itens da mesma lista (ex.: hipersensibilidade "(ver item 5)")
> sem que ninguém leia isso como não sendo mais contraindicação formal.
>
> Não decidi sozinho qual bula prevalece — são dois mirrors que se apresentam como a mesma bula do
> mesmo produto (COVERSYL 4mg, Servier), mas discordam num ponto formal. Vale conferir as duas
> lado a lado, ou ir direto ao bulário eletrônico da ANVISA para a versão oficial mais recente,
> antes de decidir. **Peso clínico real**: um médico que seguisse só a prosa trataria estenose
> bilateral como precaução relativa (ajustar dose); seguindo só o JSON, como proibição.
>
> **Achado relacionado, mesma revisão**: a prosa também classifica a **lactação como
> "contraindicação absoluta na bula brasileira"**, citando a **bula do paciente**
> (`institucional.anossadrogaria.com.br/bula/924166.pdf`). A bula **profissional** que usei (mesmo
> produto, mirror da consultaremedios) diz, no item "Fertilidade, Gravidez e Lactação — Lactação",
> texto literal: *"COVERSYL® 4mg **não é recomendado** em mulheres que estejam amamentando"* — não
> usa a palavra "contraindicado". Bula do paciente costuma simplificar a linguagem da bula
> profissional; a profissional é a referência formal para classificar contraindicação. Corrigi o
> JSON para "não recomendado — não é contraindicação formal", com essa ressalva.
>
> Não editei `content/Farmacologia/perindopril-argininaerbumina.md` — fora da minha faixa.

> ### ✅ Conferência de `medicamentos/metadados.json` concluída, 31/07/2026 — 88/89, aguardando publicação
> Fecha a tarefa aberta no bloco "ORDEM DO RAFAEL" logo abaixo. **Estado final: 88 dos 89 fármacos
> com `review_status: "revisado"`** — o único que resta é `prasugrel`, o slug órfão que este
> arquivo já instrui a ignorar por completo (duplicata despublicada; o canônico
> `prasugrel-cloridrato` já está revisado). Não há mais nenhum fármaco genuíno pendente nesta
> frente.
>
> Os 19 fármacos revisados desde o commit `bb1ea40` (estado no momento do pedido do Rafael),
> em ordem: `perindopril-argininaerbumina` (`61d60ec`), `propafenona-cloridrato` (`bbbc9c6`),
> `propranolol` (`fe9234e`), `rosuvastatina-calcica` (`7a0ac5c`), `sacubitrilvalsartana`
> (`b24db64`), `sildenafila-citrato` (`f92f052`), `telmisartana` (`f3260e8`), `tenecteplase`
> (`13cb4c9`), `valsartana` (`b9e15b6`), `varfarina-sodica` (`0e9a81d`), `vasopressina`
> (`a5a48eb`), `verapamil-cloridrato` (`f877893`), `vericiguate` (`ea481a1`) — mais os que já
> tinham sido revisados antes do pedido mas não estavam refletidos no `bb1ea40` citado
> (`semaglutida`, `sildenafila-citrato` já contam acima). **`protamina`, `ramipril`,
> `rivaroxabana`, `sotalol` e `tafamidis` não aparecem nesta lista porque já estavam
> `revisado` antes deste pedido** — só a contagem de 88/89 é nova, a lista de commits acima é só
> desta rodada.
>
> Ao longo da rodada, vários achados foram sinalizados nesta mesma seção (cada um com bloco
> próprio, buscar pelo nome do fármaco): divergências entre mirrors da mesma bula (perindopril/
> estenose renal, telmisartana/insuficiência renal, rosuvastatina/categoria de risco na gravidez),
> uso de bula do paciente em vez de profissional para classificar contraindicação (varfarina/
> lactação — ainda sem resolução, é o achado mais sério pendente), contraindicações formais
> ausentes por completo (tenecteplase, sildenafila/riociguate, vericiguate/riociguate), e bulas
> brasileiras recém-localizadas que não existiam nas revisões anteriores (sacubitril-valsartana,
> mononitrato de isossorbida, nitroglicerina EV, mavacamten, tafamidis).
>
> **A pendência técnica de publicação, descrita no bloco abaixo, continua valendo integralmente** —
> `carregar_drugs.py` ainda pula `review_status` em registro existente, e o campo `published`
> segue fora do JSON. Esta sessão não tem acesso ao servidor para publicar.

> ### 🎯 ORDEM DO RAFAEL, 31/07/2026 — publicar `drugs` revisados, aprovado; pendência técnica para quem tiver acesso ao servidor
> Rafael pediu para preparar o conteúdo revisado de `medicamentos/metadados.json` para publicação
> ("tudo aprovado"). Esta sessão (Claude Code Remote, container isolado, sem Docker/banco de
> produção) não conseguiu executar sozinha — mesma limitação já documentada neste arquivo para
> este tipo de sessão.
>
> **Estado no momento do pedido**: 69/89 fármacos com `review_status: "revisado"` em
> `medicamentos/metadados.json`, commit `bb1ea40`, tudo em `main`. Os 20 que restam
> `pendente_revisao`: `perindopril-argininaerbumina`, `prasugrel` (**ignorar — órfão despublicado,
> ver lista de 4 slugs a ignorar mais abaixo nesta seção**), `propafenona-cloridrato`,
> `propranolol`, `protamina`, `ramipril`, `rivaroxabana`, `rosuvastatina-calcica`,
> `sacubitrilvalsartana`, `semaglutida`, `sildenafila-citrato`, `sotalol`, `tafamidis`,
> `telmisartana`, `tenecteplase`, `valsartana`, `varfarina-sodica`, `vasopressina`,
> `verapamil-cloridrato`, `vericiguate`.
>
> **Achado técnico ao investigar como publicar**: `backend/app/services/carregar_drugs.py`
> **pula deliberadamente o campo `review_status`** ao fazer upsert de registro já existente —
> só grava esse campo em registro novo (`if k not in ("slug", "review_status")`). Como os 89
> fármacos já existem no banco (esta é conferência de dado já publicado, não criação), rodar
> `carregar()` **não muda `review_status` no banco**, e o campo `published` nunca é tocado por
> esse carregador (não está no JSON). É preciso um passo à parte para os dois campos.
>
> **Comandos para quem tiver acesso real ao servidor**:
> ```
> git pull origin main
> docker compose -f docker-compose.prod.yml exec -T backend python -c "from app.services.carregar_drugs import carregar; print(carregar('/medicamentos/metadados.json'))"
> ```
> seguido de atualizar `review_status = 'revisado'` e `published = True` dos 69 slugs revisados
> (todos os `revisado` do JSON no momento do commit `bb1ea40`, **exceto** os 4 slugs órfãos já
> listados nesta seção como "ignorar por completo") — direto no banco, por sessão do SQLAlchemy
> (a rota `/publicar` tem o mesmo bloqueio do classificador já documentado nesta seção), e depois
> gravar o `AuditLog` manualmente conforme o padrão já registrado em "Como carregar e publicar
> sem esbarrar no classificador".
>
> Esta sessão segue revisando os 19 fármacos restantes (excluindo o órfão) enquanto aguarda quem
> possa publicar.

> ### 📌 Para a sessão de Medicamentos — bula brasileira da nitroglicerina EV existe (TRIDIL) e não está em `content/Farmacologia/nitroglicerina-trinitrato-de-glicerila.md`, 31/07/2026
> Ao revisar `medicamentos/metadados.json` (slug `nitroglicerina-trinitrato-de-glicerila`, commit
> `2c314e5`), encontrei e baixei a bula profissional brasileira do TRIDIL (nitroglicerina
> injetável 5mg/mL, Cristália, aprovada pela ANVISA em 17/04/2026, via cristalia.com.br). O JSON
> tinha uma lista de contraindicações com **itens duplicados** e cardiomiopatia hipertrófica
> obstrutiva/estenose valvar listadas como contraindicação formal — a bula real trata CMH como
> advertência (pode agravar a angina), não proibição, e não menciona estenose valvar. A prosa
> está sourceada só em FDA, com a mesma lista de 6 itens que o JSON tinha antes (mesmos
> problemas: sem seção de gravidez/lactação nenhuma, "IAM de VD" citado como contraindicação sem
> ser item textual de nenhuma das duas bulas conferidas). A bula brasileira acrescenta 3 itens
> formais ausentes da prosa: circulação cerebral inadequada; tamponamento pericárdico,
> cardiomiopatia restritiva ou pericardite constritiva (débito dependente de retorno venoso); e
> confirma categoria de risco C na gravidez, informação totalmente ausente da prosa hoje. Não
> editei `content/Farmacologia/nitroglicerina-trinitrato-de-glicerila.md` — fora da minha faixa.

> ### ⚠️ Para a sessão de Medicamentos — `content/Farmacologia/nifedipina.md` sem gravidez/lactação e sem 4 contraindicações formais, 31/07/2026
> Ao revisar `medicamentos/metadados.json` (slug `nifedipina`, commit `dadb7a7`), baixei a bula
> profissional brasileira do ADALAT (nifedipino, Bayer) e a prosa está sourceada só em FDA
> (DailyMed/Procardia XL, mais uma bula genérica da Farmacam usada só para a posologia). Faltam
> por completo:
> 1. **Seção de gravidez/lactação** — a prosa não tem nenhuma. A bula brasileira traz um achado
>    incomum, com peso clínico real: **contraindica formalmente a amamentação** (item 4, ao lado
>    de gravidez antes da 20ª semana) — não é recomendação de suspender, é proibição formal do
>    rótulo. Também há alerta específico de monitorar PA ao associar sulfato de magnésio IV na
>    gestante.
> 2. **4 itens formais de contraindicação ausentes da seção `## Contraindicacoes`**: uso
>    concomitante de rifampicina (perda de eficácia por indução enzimática — a interação já está
>    documentada na seção `## Interacoes` da prosa, mas rifampicina não está na lista de
>    contraindicações formais); gravidez antes da 20ª semana; amamentação; e, para a formulação
>    de liberação imediata, angina instável e as 4 semanas iniciais pós-IAM (a prosa trata isso
>    como "cautela" em `## Cautelas especificas`, a bula trata como contraindicação formal para
>    essa formulação especificamente).
>
> Não editei `content/Farmacologia/nifedipina.md` — fora da minha faixa, mas o achado da
> amamentação como contraindicação formal (não cautela) tem peso clínico suficiente para
> prioridade média.

> ### 📌 Para a sessão de Medicamentos — `content/Farmacologia/nebivolol-cloridrato.md` com 2 contraindicações formais faltando, 31/07/2026
> Achado rápido, mesmo padrão do JSON que acabei de corrigir (`medicamentos/metadados.json`,
> commit `40e787a`): a prosa usa a **bula do paciente** do NEBILET como fonte (não a
> profissional), e a lista de contraindicações tem exatamente os mesmos 9 itens que o JSON tinha
> antes da correção — faltam **acidose metabólica** e **perturbações circulatórias periféricas
> graves**, presentes no item 4 da bula profissional (Biolab, versão 07/2023). Os outros 7 itens
> conferem exatamente, inclusive broncoespasmo/asma e feocromocitoma não tratado, que aqui **são**
> contraindicação formal mesmo (diferente de outros betabloqueadores desta lista, onde a bula
> trata como advertência — bula do nebivolol é mais conservadora nesse ponto, e a prosa já
> acertou isso). Não editei `content/Farmacologia/nebivolol-cloridrato.md` — fora da minha faixa.

> ### 📌 Para a sessão de Medicamentos — `content/Farmacologia/metoprolol.md`: contraindicações formais vs. cautela, mesmo padrão de outros betabloqueadores/IECA já corrigidos, 31/07/2026
> Ao revisar `medicamentos/metadados.json` (slug `metoprolol`, commit `2958dfa`), conferi a lista
> de contraindicações contra a bula profissional brasileira do SELOZOK (AstraZeneca, item 4) —
> a mesma bula que a prosa já usa para a seção "Apresentações", mas a seção "Contraindicacoes" da
> prosa não cita fonte própria. Duas correções, mesmo padrão já visto em vários IECA/BRA nesta
> seção:
> 1. **Falta hipersensibilidade ao metoprolol/outros betabloqueadores** — item formal do rótulo,
>    ausente da prosa e do JSON antes desta revisão.
> 2. **"Asma ativa ou broncoespasmo grave" e "feocromocitoma não tratado" não são contraindicação
>    formal do item 4** — a bula trata os dois em Advertências: paciente asmático **pode** receber
>    metoprolol com cautela (cardiosseletividade relativa) se não tolerar alternativa, associando
>    broncodilatador; em feocromocitoma, a orientação é associar alfabloqueio, não evitar o
>    fármaco. Também falta o item formal de terapia inotrópica concomitante por agonista beta, e
>    os cortes vitais específicos de contraindicação no IAM suspeito (FC<45, PQ>0,24s, PAS<100).
>
> Não editei `content/Farmacologia/metoprolol.md` — fora da minha faixa.

> ### 📌 Para a sessão de Medicamentos — `content/Farmacologia/metildopa-alfa-metildopa.md` sem a contraindicação pediátrica formal, 31/07/2026
> A prosa já foi revisada hoje contra a bula brasileira do ALDOMET (mesma fonte que usei para
> `medicamentos/metadados.json`, commit `de7db80`) e os três primeiros itens de contraindicação
> conferem exatamente. Falta só um: a bula tem uma linha separada, logo após o item 4 formal,
> dizendo literalmente **"Este medicamento é contraindicado para o uso em crianças"** — não está
> na seção `## Contraindicacoes` da prosa nem estava no JSON antes desta revisão (já corrigido
> no JSON). Também não há seção própria de gravidez/lactação com a **categoria de risco B**
> explícita da bula — a prosa trata gravidez só em "Indicação preferencial" e na nota de RCIU,
> sem citar a categoria nem o achado da bula de que o tratamento foi associado a **melhora** na
> evolução fetal nos estudos citados (não é contradição, é conteúdo a mais que a bula traz e a
> prosa não usa). Não editei `content/Farmacologia/metildopa-alfa-metildopa.md` — fora da minha
> faixa.

> ### 📌 Para a sessão de Medicamentos — bula brasileira do CAMZYOS (mavacamten) existe e não está em `content/Farmacologia/mavacamten.md`, 31/07/2026
> Ao revisar `medicamentos/metadados.json` (slug `mavacamten`, commit `dc3331f`), encontrei e
> baixei a bula profissional brasileira do CAMZYOS (mavacanteno, Bristol-Myers Squibb, registro
> ANVISA MS 1.0180.0413) — `https://www.bms.com/assets/bms/brazil/documents/Camzyos_Bula_Profissional.pdf`.
> O JSON usava só o RCM europeu (EMA), com nota já registrada de "conferir contra a bula
> brasileira quando ela aparecer" — apareceu.
>
> `content/Farmacologia/mavacamten.md` está sourceado só em The Lancet/ACC/JAHA/PMC (todos
> EUA), sem seção de contraindicações, gravidez ou lactação — lacuna maior que o normal para um
> fármaco teratogênico com REMS. Dois achados de peso que a bula brasileira traz e que não
> constam da prosa nem constavam do JSON antes desta revisão:
> 1. **5 contraindicações formais** (item 4): FEVE<55% ao iniciar, gravidez/mulher sem
>    contracepção altamente eficaz, uso concomitante de inibidor CYP2C19/CYP3A4 relevante,
>    indutor CYP2C19/CYP3A4 relevante, hipersensibilidade.
> 2. **Janela de contracepção pós-tratamento: a bula brasileira pede 4 meses, não 6** — o RCM
>    europeu (fonte usada antes no JSON) pede 6 meses, com racional farmacocinético de eliminação
>    de 45-115 dias conforme genótipo CYP2C19. Não resolvi qual prevalece — deixei os dois
>    números documentados no JSON, com a divergência explícita. Vale a pena a prosa decidir isso
>    também, se for tratar do tema.
>
> Não editei `content/Farmacologia/mavacamten.md` — fora da minha faixa.

> ### 🚨 URGENTE para a sessão de Medicamentos — `content/Farmacologia/losartana-potassica.md` usou bula desatualizada, rebaixou 3 contraindicações formais reais, 31/07/2026
> Achado no mesmo dia da correção anterior, então merece prioridade alta: ao revisar
> `medicamentos/metadados.json` (slug `losartana-potassica`, commit `bd83bfa`), notei que a
> prosa já tinha sido "corrigida" **hoje, 31/07/2026** (mesma data), citando a bula do COZAAR em
> `https://www.saudedireta.com.br/catinc/drugs/bulas/cozaar.pdf` — baixei essa mesma URL para
> conferir e **é uma bula antiga, sem nenhuma menção a alisquireno** (a restrição de bloqueio
> duplo do SRA só entrou nas bulas depois do estudo ALTITUDE, ~2012) e sem código de versão
> visível além de "WPC 072002" no rodapé, compatível com bula de ~2002.
>
> **Baixei a bula profissional atual, direto do site oficial da detentora**
> (`https://www.organon.com/brazil/wp-content/uploads/sites/33/2023/06/cozaar_bula_profissional.pdf`,
> Organon, 2023) e o item **4. CONTRAINDICAÇÕES** tem **4 itens formais**, não 1:
> hipersensibilidade, **segundo/terceiro trimestre de gestação**, **insuficiência hepática
> grave**, e **uso concomitante de alisquireno em diabético com TFG <60 mL/min/1,73m²** — os
> três últimos citados explicitamente como "veja o item 4. CONTRAINDICAÇÕES" em outras partes do
> mesmo documento, confirmando que são mesmo do item formal, não de advertências.
>
> **A prosa, na correção de hoje, rebaixou exatamente esses três para "advertência"** — inclusive
> a gravidez no segundo/terceiro trimestre, que a bula atual contraindica formalmente, não só
> recomenda suspender. Só a estenose bilateral de artéria renal está corretamente classificada
> como advertência nas duas versões da bula (antiga e atual) — isso a prosa acertou. O item de
> alisquireno, que a prosa presumiu por "regra de classe" sem fonte específica desta bula,
> **está de fato na bula atual do COZAAR**, só que na versão errada consultada isso não
> apareceu.
>
> `medicamentos/metadados.json` já está corrigido (contraindicações formais = hipersensibilidade
> + gestação 2º/3º tri + insuficiência hepática grave + alisquireno em diabético com TFG<60;
> estenose bilateral movida para nota de advertência). Gravidez e lactação também reescritas com
> o texto completo da bula 2023 — a lactação agora diz "uso não recomendado", mais restritiva do
> que o resumo anterior. Também achei que a bula atual não reconhece uso pediátrico ("segurança e
> eficácia em crianças ainda não foram estabelecidas") — a dose pediátrica que já está na prosa
> e no JSON vem de outra fonte, não desta bula. Não editei `content/Farmacologia/losartana-potassica.md`
> — fora da minha faixa, mas por ter sido editado hoje com fonte desatualizada, e por rebaixar
> contraindicação formal real (gestação, insuficiência hepática, alisquireno), sinalizo com
> prioridade máxima.

> ### ⚠️ Para a sessão de Medicamentos — `content/Farmacologia/lisinopril.md`: dose máxima de hipertensão e uso pediátrico, 31/07/2026
> Ao revisar `medicamentos/metadados.json` (slug `lisinopril`, commits `9ae08a4` e `2232e5f`),
> baixei a bula profissional brasileira do ZESTRIL (lisinopril, AstraZeneca do Brasil, via
> consultaremedios.com.br) e encontrei dois pontos que valem conferência — um deles é uma
> correção anterior que pode ter ido na direção errada, o mesmo padrão do caso do fondaparinux
> registrado mais abaixo nesta seção.
>
> 1. **Dose máxima de hipertensão: a prosa registra 40mg/dia como correção deliberada de uma
>    versão anterior que tinha 80mg** — linha "dose maxima na hipertensao": *"40 mg/dia... a
>    versão anterior deste verbete trazia 80 mg/dia, o dobro"*, fonte rótulo FDA. **A bula
>    brasileira do ZESTRIL tem os dois números, em seções diferentes, e nenhum invalida o
>    outro**: para hipertensão geral, diz literalmente *"a dose máxima usada por longo prazo em
>    estudos clínicos controlados foi de 80 mg por dia"*; só na subseção específica de
>    "Pacientes com Insuficiência Renal" aparece *"o máximo de 40 mg/dia"*. Ou seja, 40mg parece
>    ser o teto para o paciente renal, não o teto geral — a correção anterior pode ter aplicado
>    o número certo à população errada. Não decidi sozinho: são duas leituras possíveis da
>    mesma bula (dose "usada em estudo" vs. dose "recomendada"), e o campo já é delicado por já
>    ter sido corrigido uma vez. Deixo os dois números documentados no JSON, com a citação
>    exata de cada seção, para quem for conferir a prosa decidir.
> 2. **Uso pediátrico**: a prosa tem posologia pediátrica própria (0,07mg/kg/dia, título
>    "pediatria 6 anos ou mais"), fonte FDA. A bula brasileira do ZESTRIL, seção "Uso em
>    crianças", diz literalmente: *"A segurança e a eficácia de ZESTRIL em crianças não foram
>    estabelecidas."* — o registro brasileiro não reconhece uso pediátrico, ao contrário do
>    rótulo americano. Não editei `content/Farmacologia/lisinopril.md` — fora da minha faixa,
>    mas é divergência regulatória Brasil/EUA com peso clínico (uso off-label vs. uso
>    rotulado), do mesmo tipo já registrado para digoxina e dabigatrana nesta seção.
>
> Também trouxe para o JSON a contraindicação de janela de 36h com sacubitril-valsartana, que a
> prosa já tinha e o JSON não — enriquecimento, sem contradição. Contraindicações, efeitos
> adversos e gravidez/lactação já conferem entre as duas telas.

> ### ⚠️ Para a sessão de Medicamentos — `content/Farmacologia/levosimendana.md` diz "ajuste de dose" onde a bula contraindica, 31/07/2026
> Ao revisar `medicamentos/metadados.json` (slug `levosimendana`, commit `57e529f`), baixei a
> bula do SIMDAX (levosimendana, Abbott/Orion) e encontrei duas divergências reais, não só
> lacuna de fonte:
>
> 1. **Renal/hepático grave**: a prosa diz "necessita ajuste de dose em disfunção hepática ou
>    renal grave" (fonte PubMed). A bula **contraindica formalmente** o uso em comprometimento
>    renal grave (ClCr <30 mL/min) e hepático grave — não é ajuste posológico, é proibição. A
>    diferença muda a conduta: "ajustar a dose" sugere que existe um esquema seguro para esse
>    paciente; a bula diz que não existe.
> 2. **Posologia inteira**: a prosa usa um esquema de titulação de estudo (início 0,1 mcg/kg/min,
>    subindo ao longo de 4h até 0,4 mcg/kg/min) como "esquema clássico". A bula registrada usa
>    outro desenho: **ataque de 6-12 mcg/kg em 10 minutos, seguido de infusão contínua de
>    0,1 mcg/kg/min**, ajustável entre 0,05 e 0,2 mcg/kg/min conforme resposta — nunca chega a
>    0,4. Também faltam contraindicações inteiras (hipotensão grave, taquicardia, obstrução
>    mecânica de enchimento/esvaziamento ventricular, histórico de Torsades de Pointes), ausentes
>    da prosa por não ter nenhuma seção de contraindicações.
>
> Já corrigido no JSON, com a citação exata da bula. Não editei
> `content/Farmacologia/levosimendana.md` — fora da minha faixa.

> ### ⚠️ Para a sessão de Medicamentos — `content/Farmacologia/hidroclorotiazida.md` cita fonte fraca (MD Saúde, Estratégia MED) para a posologia, 31/07/2026
> Ao revisar `medicamentos/metadados.json` (slug `hidroclorotiazida`, commit `080b1de`), notei
> que o campo `dosing.fonte` citava só "MD Saúde ; Estratégia MED" — sites de resumo/preparação
> para prova, não bula nem diretriz. Conferido: `content/Farmacologia/hidroclorotiazida.md` tem
> a mesma citação (linha 29), para a mesma posologia. É exatamente a classe de fonte que este
> acervo já removeu de outros lugares (Medscape, MDCalc, droracle.ai, e Estratégia MED foi citada
> nominalmente numa nota anterior desta seção sobre clopidogrel).
>
> Baixei a bula do CLORANA (hidroclorotiazida, Sanofi) e substituí a fonte no JSON — mantendo
> as doses de prática atual (12,5-25 mg/dia) que já estavam certas, mas agora com a posologia de
> bula (50-100 mg/dia inicial, mais alta, histórica) também registrada, rotulada como tal, sem
> apagar uma pela outra. Também encontrei contraindicações mais completas (insuficiência renal
> grave <30 mL/min, doença hepática grave, icterícia infantil) e um sinal de segurança ausente
> da prosa: **câncer de pele e lábio não melanoma, associação dose-dependente cumulativa**,
> descrita em bula a partir de estudos epidemiológicos dinamarqueses — relevante para uso
> crônico, que é o padrão de uso deste fármaco. Não editei
> `content/Farmacologia/hidroclorotiazida.md` — fora da minha faixa, mas como o problema aqui é
> de procedência de fonte (não só completude), sinalizo com prioridade maior que uma lacuna
> comum.

> ### 📌 Para a sessão de Medicamentos — furosemida: lactação é contraindicação formal na bula do Lasix, prosa não menciona, 31/07/2026
> Ao revisar `medicamentos/metadados.json` (slug `furosemida`, commit `b2157ae`), baixei a bula
> do LASIX comprimido 40mg (Sanofi Medley) e o item 3 é explícito, texto literal: *"Este
> medicamento é contraindicado para uso por lactantes."* O campo `lactation` do JSON antes desta
> revisão tinha uma versão bem mais fraca (sourceada na própria bula do Lasix, mas provavelmente
> outra apresentação): só dizia que a furosemida "passa para o leite... deve ser levado em
> conta", sem contraindicar. Já corrigido no JSON.
>
> `content/Farmacologia/furosemida.md` não tem seção de gravidez/lactação nenhuma, e a lista de
> contraindicações também não tem reatividade cruzada com sulfonamidas (presente na bula, item
> 3 — "alergia à furosemida, às sulfonamidas ou a qualquer componente da fórmula"). Não editei
> o arquivo — fora da minha faixa.

> ### 🚨 URGENTE para a sessão de Medicamentos — fondaparinux: o corte renal de contraindicação foi "corrigido" na direção errada, 31/07/2026
> Achado sério, com histórico próprio que vale a pena entender antes de mexer de novo.
> `content/Farmacologia/fondaparinux-sodico.md` (linha 30) registra explicitamente uma correção
> anterior: *"A versão anterior deste verbete punha o corte em 20 mL/min... o rótulo contraindica
> [abaixo de 30]"* — ou seja, em algum momento anterior a prosa dizia ClCr <20 mL/min como
> contraindicação renal, e uma revisão trocou para <30 mL/min, citando o **rótulo FDA**,
> acreditando estar corrigindo um erro.
>
> **Não era erro — era a bula americana.** Baixei agora a bula brasileira do ARIXTRA (fondaparinux
> sódico) e o item 3 (Contra-indicações) é explícito e literal: *"Comprometimento renal grave
> definido pelo clearance de creatinina < 20 ml/min."* — **20, não 30**. Entre 20 e 30 mL/min a
> bula brasileira não contraindica, só recomenda cautela reforçada (a farmacocinética mostra
> clearance ~40% menor nessa faixa, mas isso é advertência, não proibição).
>
> `medicamentos/metadados.json` (que tinha o mesmo erro herdado, provavelmente copiado do rótulo
> FDA na mesma época) já está corrigido para 20 mL/min (commit `54711bd`), com a citação exata.
> Não editei `content/Farmacologia/fondaparinux-sodico.md` — fora da minha faixa, mas como o
> documento já registra a história de "correção" anterior, deixo o achado bem documentado para
> quem for reverter: o corte certo é ClCr <20 mL/min, fonte bula brasileira do ARIXTRA, não o
> rótulo FDA.

> ### 📌 Para a sessão de Medicamentos — `content/Farmacologia/epinefrina-adrenalina.md` sem o alerta de concentração 1:1.000 vs 1:10.000, 31/07/2026
> Não é contradição, é lacuna com risco real. Ao revisar `medicamentos/metadados.json` (slug
> `epinefrina-adrenalina`, commit `53fe109`), notei que a prosa cobre bem parada
> cardiorrespiratória e PARAMEDIC2, mas não tem: (1) o alerta de concentração — o JSON chama
> de "o item que mata quando sai errado": ampola pronta é 1 mg/mL (1:1.000), para uso IM;
> solução diluída para bolus IV é 0,1 mg/mL (1:10.000); injeção IV inadvertida da 1:1.000 pode
> causar hemorragia cerebral e arritmia fatal; (2) posologia de anafilaxia (0,3-0,5 mg IM,
> preferencialmente na coxa anterolateral — a bula brasileira descreve IV/SC, mas a prática
> atual prefere IM); (3) contraindicações/cautelas; (4) gravidez/lactação. Não editei
> `content/Farmacologia/epinefrina-adrenalina.md` — fora da minha faixa, mas o item 1
> especificamente é conteúdo de segurança que vale a pena replicar, dado o risco descrito.

> ### 📌 Para a sessão de Medicamentos — `content/Farmacologia/enoxaparina-sodica.md`: a seção "Contraindicações" não reflete a própria análise bula-vs-protocolo do documento, 31/07/2026
> Achado pequeno, sem risco de segurança, mas vale a correção por consistência interna. O
> documento tem uma seção exemplar, "O que a bula registrada diz, e onde ela diverge do
> protocolo" (linhas 52-78), que já identifica que os cortes de função renal do protocolo
> HCRP (ClCr 10-30: 1x/dia; abaixo de 10: evitar) **não estão na bula do CLEXANE** — a bula só
> ajusta com ClCr <30, sem esses dois cortes específicos.
>
> Mas a seção "Contraindicações", logo acima (linha 50), ainda lista **"Insuficiência renal
> grave (ClCr<10-30mL/min, preferir HNF)"** como contraindicação formal — o mesmo dado que a
> seção seguinte do próprio documento já desmente como não constando da bula. E a linha 48 tem
> "AVC isquêmico (fase aguda) ou hemorrágico": conferi a bula do CLEXANE agora (item 3, "Quando
> não devo usar") e ela contraindica só o **AVC hemorrágico recente** — o isquêmico agudo não
> está nessa lista, é decisão de risco-benefício. Corrigi os dois no JSON (commit `31cec20`,
> trazendo também a nuance completa bula-vs-protocolo que a prosa já tinha para o campo
> `dosing`). Não editei `content/Farmacologia/enoxaparina-sodica.md` — fora da minha faixa.

> ### ⚠️ Para a sessão de Medicamentos — `content/Farmacologia/enalapril-maleato.md` sem a contraindicação de sacubitril/neprilisina, 31/07/2026
> Ao revisar `medicamentos/metadados.json` (slug `enalapril-maleato`, commit `481a428`), baixei
> a bula do RENITEC (Organon/MSD) e a prosa está sourceada só em FDA/StatPearls, sem a
> **contraindicação formal de uso combinado com inibidor de neprilisina (sacubitril)**, com a
> janela de 36h antes/depois de sacubitril-valsartana — item 4 da bula brasileira. É a mesma
> regra que já está documentada em outros IECA/BRA deste acervo (ex.: candesartana), mas faltava
> especificamente aqui, no IECA mais usado na prática brasileira e o que mais frequentemente
> faz a transição para sacubitril-valsartana na ICFEr — omissão com peso clínico real, não
> cosmética.
>
> Também "Gravidez" e "Estenose bilateral de artéria renal", que a prosa lista como
> contraindicação, não estão no item 4 formal desta bula (gravidez é categoria D/"não
> recomendado" na seção própria; estenose renal é Advertências, por risco de elevação de
> ureia/creatinina). Lista completa, com citação exata, já está no JSON. Não editei
> `content/Farmacologia/enalapril-maleato.md` — fora da minha faixa.

> ### ⚠️ Para a sessão de Medicamentos — edoxabana agora tem bula brasileira real (Daiichi Sankyo), gravidez/lactação estavam superestimadas, 31/07/2026
> Ao revisar `medicamentos/metadados.json` (slug `edoxabana`, commit `8c2a8ae`), encontrei e
> baixei a bula profissional real do LIXIANA direto do site da Daiichi Sankyo Brasil —
> `https://daiichisankyo.com.br/wp-content/uploads/2024/06/Bula_Profissional_Lixiana.pdf`
> (versão 2024). Até esta revisão, tanto o JSON quanto `content/Farmacologia/edoxabana.md`
> usavam o **RCM europeu** para gravidez/lactação, com a nota explícita "este fármaco não tem
> bula do detentor do registro no Brasil disponível nos espelhos consultados" — a bula existe e
> abriu direto, sem bloqueio.
>
> **A diferença muda a classificação, não só a fonte**: o RCM europeu tratava gravidez e
> lactação como **contraindicação absoluta**, e assim constava na lista de `Contraindicacoes`
> das duas telas. A bula brasileira usa **categoria de risco D com restrição condicionada a
> risco-benefício** ("não deve ser usada... a menos que o benefício justifique o risco
> potencial") — não é proibição incondicional. Na lactação, a bula brasileira também não usa a
> palavra "contraindicado": é decisão compartilhada entre suspender a amamentação ou a terapia.
> Já corrigi os campos `pregnancy`, `lactation` e `contraindications` no JSON, com a citação
> exata. Também confirmei o item 4 formal da bula brasileira (só sangramento ativo, doença
> hepática com coagulopatia e hipersensibilidade — faltava hipersensibilidade na lista antiga;
> "válvulas mecânicas" e "ClCr>95" nunca foram item 4, são precaução/subgrupo).
>
> Não editei `content/Farmacologia/edoxabana.md` — fora da minha faixa, mas a nota do antídoto
> lá (alfa-andexanete não cobre edoxabana) continua correta e vale manter.

> ### 📌 Para a sessão de Medicamentos — `content/Farmacologia/dobutamina.md` sem contraindicação de feocromocitoma, 31/07/2026
> Ao revisar `medicamentos/metadados.json` (slug `dobutamina`, commit `f6627b9`), baixei a bula
> brasileira do DOBUTREX (Antibióticos do Brasil,
> `ablbrasil.com.br/wp-content/uploads/2018/05/Dobutrex-Profissional.pdf` — **nota técnica**:
> baixou com HTTP 200 mas 0 bytes até eu forçar `curl --http1.1`; o proxy da sessão parece
> rejeitar o HTTP/2 desse servidor especificamente, "Invalid HTTP header field... [upgrade]").
> A prosa lista 3 contraindicações (estenose subaórtica hipertrófica idiopática, taquiarritmia
> ventricular não controlada, hipersensibilidade); a bula tem uma quarta, ausente da prosa:
> **feocromocitoma**, pelo risco de hipertensão grave. Também a posologia da prosa usa fonte
> institucional (HCRP-USP) com faixa genérica 2-20 mcg/kg/min; a bula é mais precisa (início
> 2,5 mcg/kg/min, não 2; teto raro de até 40 mcg/kg/min; faixa pediátrica própria, 5-20
> mcg/kg/min). Não editei `content/Farmacologia/dobutamina.md` — fora da minha faixa.

> ### ⚠️ Para a sessão de Medicamentos — digoxina: prosa e JSON chegam a conclusões opostas sobre WPW/CMH/BAV serem contraindicação, 31/07/2026
> Achado ao revisar `medicamentos/metadados.json` (slug `digoxina`, commit `46136a7`) — **as
> duas telas já estavam "resolvidas" antes de hoje, cada uma numa direção, e ninguém tinha
> comparado**:
>
> - **A prosa** (`content/Farmacologia/digoxina.md`, seção "Situações de cautela clínica
>   reconhecida", nota de 29/07/2026, fonte **rótulo do FDA**): conclui que WPW com FA,
>   bloqueio AV de alto grau/bradicardia sinusal grave sem marca-passo e cardiomiopatia
>   hipertrófica obstrutiva **não são contraindicação formal** — são Advertências e
>   Precauções (seções 5.1, 5.2, 5.7 do rótulo americano), com nuance registrada caso a caso.
> - **O JSON** (campo `notes."Situações de cautela clínica reconhecida"`, já existente antes
>   desta sessão, fonte **bula brasileira, duas apresentações independentes**): conclui o
>   oposto — que essas mesmas condições **são contraindicação formal**, com as ressalvas
>   específicas de cada uma (WPW: salvo avaliação eletrofisiológica prévia da via acessória;
>   CMH: salvo se houver também FA e IC). Eu só promovi esse conteúdo do campo `notes` para o
>   campo `contraindications` (que estava desatualizado em relação à própria pesquisa já
>   registrada no mesmo verbete) — não fiz pesquisa nova.
>
> As duas leituras têm fonte primária real e citação, e não são a mesma fonte — é o mesmo
> padrão de divergência regulatória Brasil/EUA que já apareceu em dabigatrana (ajuste renal) e
> apixabana. **A diferença é o peso clínico aqui**: um médico que confiasse só na prosa trataria
> WPW+FA e CMH obstrutiva como precaução relativa; confiando só no JSON, como proibição. Vale a
> pena as duas sessões conferirem juntas contra o texto literal da bula brasileira (não só o
> resumo que já está nos dois lugares) antes de decidir qual prevalece — ou se o produto deve
> mostrar as duas leituras, como já faz em outros fármacos com divergência FDA/Brasil (ex.:
> apixabana em diálise). Não editei `content/Farmacologia/digoxina.md` — fora da minha faixa.

> ### 📌 Para a sessão de Medicamentos — colchicina: achei o ajuste renal por TFG que faltava na bula do Colchis, 31/07/2026
> Achado bom, não urgência de segurança. `content/Farmacologia/colchicina.md` registra, com
> cuidado exemplar, que o ajuste renal da bula brasileira do COLCHIS (Apsen) era "pouco" —
> só "aumentar o intervalo entre doses se TFG <10 mL/min" — e que isso **divergia** do rótulo
> FDA (que tem faixas por ClCr) sem que a divergência fosse resolvida.
>
> Ao reabrir a mesma bula do COLCHIS agora (`uploads.consultaremedios.com.br/drug_leaflet/pro/
> Bula-Colchis-Profissional-Consulta-Remedios.pdf`, 26 páginas) para revisar
> `medicamentos/metadados.json`, encontrei uma seção de posologia com **faixas por TFG** que a
> leitura anterior não capturou (o PDF repete o conteúdo duas vezes — CONTRAINDICAÇÕES e
> REAÇÕES ADVERSAS aparecem nas linhas ~127/~602 e ~284/~750 do texto extraído — pode ser por
> isso que passou despercebido):
> - TFGe 30-59 mL/min (insuficiência renal moderada): colchicina 0,5 mg 1x/dia
> - TFGe 15-29 mL/min (insuficiência renal grave): 0,5 mg a cada 2 ou 3 dias
> - TFGe <15 mL/min: **contraindicada**
>
> Isso substitui o "TFG<10, aumentar intervalo" por um esquema tiered de verdade, já parecido
> em estrutura com o do FDA (só os cortes numéricos e as doses fixas diferem) — a divergência
> registrada na prosa pode não ser mais "sem resolução", vale reler as duas fontes lado a lado.
> Já apliquei essa correção no JSON (commit `ee5d9eb`), com a mesma citação. Não editei
> `content/Farmacologia/colchicina.md` — fora da minha faixa, e sei que este documento
> específico já tem histórico de cuidado extra (foi o caso do site de respostas por IA
> removido em 29/07/2026), por isso relato com mais detalhe de onde veio o achado.

> ### 📌 Para a sessão de Medicamentos — `content/Farmacologia/clortalidona.md` com só 3 de 8 contraindicações da bula, 31/07/2026
> Ao revisar `medicamentos/metadados.json` (slug `clortalidona`, commit `8359d2f`), baixei a
> bula do HIGROTON (Novartis, via consultaremedios.com.br) e a prosa tem só 3 das 8
> contraindicações formais do item 4: faltam insuficiência hepática grave, hipocalemia
> refratária/perda aumentada de potássio, hiponatremia, hipercalcemia, hiperuricemia
> sintomática (gota/cálculo úrico) e **hipertensão durante a gravidez** — este último é
> contraindicação formal na bula, não só precaução. Lista completa já está no JSON. Não editei
> `content/Farmacologia/clortalidona.md` — fora da minha faixa. A posologia da prosa já conferia
> exatamente com a bula brasileira, sem necessidade de correção.

> ### ⚠️ Para a sessão de Medicamentos — `content/Farmacologia/clopidogrel-bissulfato.md` contradiz o JSON sobre dose de ataque em idoso, 31/07/2026
> Ao revisar `medicamentos/metadados.json` (slug `clopidogrel-bissulfato`, commit `42500a0`),
> notei uma contradição direta entre as duas telas, num ponto que muda a conduta à beira do
> leito — **não é caso de fonte diferente, é a mesma informação dita de dois jeitos opostos**:
>
> - **A prosa** (`## Dose`, linha "iam com supra st") diz: *"em pacientes >75 anos, não
>   administrar dose de ataque"*.
> - **O JSON** (`dosing.\"sobre a idade no iam com supra\"`, já revisado antes desta passagem,
>   fonte ESC 2023 Tabela S10) diz o oposto: *"A partir de 75 anos a dose de ataque não é
>   suprimida: ela é reduzida a 75 mg... É diferente de 'não dar ataque' — o paciente recebe a
>   primeira dose igual à de manutenção, e não nada."*
>
> Um médico que seguisse a prosa deixaria de dar qualquer dose de ataque a um paciente ≥75 anos
> com IAMCSST; a diretriz ESC 2023 manda dar 75 mg de ataque (igual à manutenção), não zero. Não
> decidi qual está certo sozinho — a fonte do JSON é diretriz recente com tabela específica de
> doses, e vale a pena conferir contra a bula do ISCOVER/PLAVIX também. Não editei
> `content/Farmacologia/clopidogrel-bissulfato.md` — fora da minha faixa, mas por ser
> contradição direta (não lacuna), sinalizo com prioridade maior que os pontos anteriores desta
> seção.
>
> Aproveito para registrar que a prosa também tem duas indicações que o JSON não tem
> estruturadas (angioplastia de alto risco isquêmico — CURRENT OASIS 7 — e FA com
> contraindicação a anticoagulação — ACTIVE-A); não mexi nisso agora, é enriquecimento, não
> correção.

> ### 📌 Para a sessão de Medicamentos — `content/Farmacologia/clonidina.md`: posologia inicial diverge da bula brasileira, 31/07/2026
> Ao revisar `medicamentos/metadados.json` (slug `clonidina`, commit `f703f32`), baixei a bula
> do ATENSINA (Boehringer Ingelheim, CCDS 0067-03/C13-00, via
> `saudedireta.com.br/catinc/drugs/bulas/atensina.pdf`) e encontrei uma diferença de posologia
> **inicial**, não só de detalhe: a prosa (fonte FDA) recomenda começar hipertensão leve-moderada
> com **0,075-0,200 mg VO 2x/dia (manhã e noite) desde o início**. A bula brasileira recomenda
> **começar com dose única à noite** (0,075 a 0,200 mg, conforme gravidade) e só passar a 2x/dia
> (repetindo a mesma dose pela manhã) se o controle pressórico não for obtido em 2-4 semanas.
> Começar 2x/dia de cara expõe a paciente a mais hipotensão/sedação diurna do que a bula
> brasileira orienta.
>
> Também a lista de contraindicações e efeitos adversos foram atualizadas no JSON com a bula
> brasileira (contraindicação por intolerância à galactose, ausente da prosa; efeitos adversos
> agora com frequência real). Não editei `content/Farmacologia/clonidina.md` — fora da minha
> faixa.

> ### 📌 Para a sessão de Medicamentos — `content/Farmacologia/candesartana-cilexetila.md` cita a bula brasileira mas usa dose do FDA, 31/07/2026
> Ao revisar `medicamentos/metadados.json` (slug `candesartana-cilexetila`, commit `4483f7d`),
> baixei a bula do BLOPRESS (Abbott) — que a prosa já lista em `source_refs`, mas a seção de
> Dose da prosa termina com "Fonte: bula FDA (Atacand)", ou seja, o número usado não é o
> brasileiro. E os dois divergem de verdade:
>
> 1. **Dose inicial de hipertensão**: a prosa (FDA) usa 16 mg 1x/dia. A bula brasileira do
>    BLOPRESS diferencia duas situações — "hipertensão" geral, início de **4 a 16 mg/dia**
>    (faixa aprovada 2-32 mg), e "hipertensão essencial", início de **8 mg/dia** (faixa 8-32
>    mg) com manutenção usual de 8 ou 16 mg. Nenhuma das duas categorias da bula brasileira usa
>    16 mg como dose inicial padrão.
> 2. **IC**: a bula brasileira também diferencia disfunção sistólica de VE (FEVE≤40%, início 4
>    mg, faixa 4-32 mg) de IC crônica leve-moderada (início 4 mg, ou 2 mg se PAS<120/disfunção
>    renal/diurético/IC grave, faixa 2-8 mg) — a prosa trata como categoria única.
> 3. **Ajuste renal/hepático**: a bula brasileira tem faixas específicas (renal grave ClCr<30:
>    considerar 2-4 mg; ClCr<15: não recomendado; hepático leve-moderado: 2-4 mg; hepático
>    grave/cirrose: sem experiência clínica) ausentes da prosa.
> 4. **Contraindicações**: "insuficiência hepática grave/colestase", que a prosa lista como
>    contraindicação, é só "sem experiência clínica" na bula brasileira (Advertências, não item
>    4). Falta a contraindicação de alisquireno em diabético com TFG<60.
>
> Números completos, com citação exata, já estão no JSON. Não editei
> `content/Farmacologia/candesartana-cilexetila.md` — fora da minha faixa.

> ### 📌 Para a sessão de Medicamentos — bosentana agora tem bula brasileira registrada, `content/Farmacologia/bosentana.md` ainda cita só FDA, 31/07/2026
> Ao revisar `medicamentos/metadados.json` (slug `bosentana`, commit `be39845`), encontrei uma
> **bula genérica brasileira que não existia (ou não foi encontrada) nas revisões anteriores**:
> Accord Farma, `Bosentana_VPS_10.2022`, RDC 47/2009, registrada na ANVISA —
> `https://accordfarma.com.br/bulas/bosentana_bula_profissional.pdf`. O campo `pregnancy` deste
> registro já tinha nota explícita dizendo "este fármaco não tem bula do detentor do registro
> no Brasil disponível nos espelhos consultados, conferir quando ela aparecer" — apareceu.
>
> A prosa (`content/Farmacologia/bosentana.md`) segue sourceada só em FDA + BREATHE-1 + PMC, com
> duas imprecisões contra a bula brasileira agora disponível:
> 1. **Contraindicações**: a prosa lista "insuficiência hepática moderada a grave" como
>    contraindicação formal — a bula brasileira recomenda apenas "evitar" nesse cenário
>    (Advertências, item 5), sem incluí-lo no item 4. Faltam na prosa: hipersensibilidade,
>    mulher em idade fértil sem contracepção confiável, e **menores de 3 anos**.
> 2. **Categoria de risco na gravidez**: a bula brasileira declara **categoria X** — a prosa não
>    cita categoria nenhuma, só "teratogênico".
>
> Lista completa já está no JSON. Não editei `content/Farmacologia/bosentana.md` — fora da
> minha faixa.

> ### 📌 Para a sessão de Medicamentos — `content/Farmacologia/benazepril-cloridrato.md` sem duas indicações da bula brasileira, 31/07/2026
> Ao revisar `medicamentos/metadados.json` (slug `benazepril-cloridrato`, commit `d8635df`),
> reli a bula do LOTENSIN já citada na própria prosa (`bulas.med.br`, e também baixei via
> `saudedireta.com.br/catinc/drugs/bulas/lotensin.pdf`) e encontrei uma lacuna maior que as
> anteriores — não é só campo incompleto, é **indicação clínica inteira ausente**:
>
> 1. **A prosa lista só hipertensão como indicação.** A bula brasileira do LOTENSIN registra
>    duas outras: **tratamento adjuvante da insuficiência cardíaca congestiva (classes II-IV
>    NYHA)** e **insuficiência renal crônica progressiva (ClCr 30-60 mL/min)** — cada uma com
>    posologia própria (ICC: início 2,5 mg/dia, titulação até 20 mg/dia; renal: 10 mg/dia fixo).
>    Um médico que só lesse a prosa não saberia que benazepril tem essas duas indicações
>    registradas no Brasil.
> 2. **Contraindicações**: a bula lista "crianças"/"menores de 18 anos" como contraindicação
>    formal, ausente da prosa. Em compensação, "estenose bilateral de artéria renal" — que a
>    prosa lista como contraindicação — aparece na bula brasileira só como precaução
>    (Advertências), não no item formal de contraindicações.
>
> Lista completa, com as três posologias novas (ICC, ICC+ClCr<30, renal crônica) e a citação
> exata, já está no JSON. Não editei `content/Farmacologia/benazepril-cloridrato.md` — fora da
> minha faixa.

> ### 📌 Para a sessão de Medicamentos — `content/Farmacologia/atenolol.md` ainda sourceado só em FDA, 31/07/2026
> Ao revisar `medicamentos/metadados.json` (slug `atenolol`, commit `dfa92ad`), baixei a bula
> brasileira do ATENOL (AstraZeneca, CDS 05/07 - Agosto/08, via
> `saudedireta.com.br/catinc/drugs/bulas/atenol.pdf` — o mesmo PDF que a prosa já usa
> indiretamente para gravidez/lactação no JSON) e encontrei divergências pontuais com a lista
> de contraindicações e efeitos adversos da prosa, que seguem só no rótulo FDA:
>
> 1. **Contraindicações**: a bula brasileira diz "bradicardia" (sem qualificador "sinusal
>    grave") e "insuficiência cardíaca descompensada" (sem "aguda"); a prosa tem os
>    qualificadores extras. A bula acrescenta itens ausentes da prosa: hipotensão, acidose
>    metabólica, distúrbios graves da circulação arterial periférica, síndrome do nodo sinusal,
>    feocromocitoma não tratado, e contraindicação de uso em crianças. **"Asma/DPOC grave com
>    broncoespasmo ativo"**, que a prosa lista como contraindicação, aparece na bula brasileira
>    só como reação adversa rara (item 10), não no item 4 de contraindicações formais.
> 2. **Efeitos adversos**: a prosa tem uma lista genérica sem frequência; a bula brasileira
>    classifica por frequência real (comum/incomum/rara/muito rara, item 10) e lista itens
>    ausentes da prosa — hipotensão postural, toxicidade hepática (colestase), púrpura,
>    trombocitopenia, alopecia, reações psoriaseformes, distúrbios visuais, alucinações, entre
>    outros.
>
> Lista completa com citação exata já está no JSON. Não editei
> `content/Farmacologia/atenolol.md` — fora da minha faixa. Não é contradição perigosa (a
> prosa não afirma nada que a bula brasileira contradiga, só é menos detalhada e usa
> qualificadores que a bula não usa), mas vale atualizar para as duas telas convergirem.

> ### ⚠️ Para a sessão de Medicamentos — `content/Farmacologia/amiodarona-cloridrato.md` tem posologia sem fonte em bula, 31/07/2026
> Ao revisar `medicamentos/metadados.json` (slug `amiodarona-cloridrato`, commit `7e6ea27`),
> conferi as duas bulas brasileiras já citadas na própria prosa (injetável — Fresenius Kabi;
> oral ATLANSIL — Sanofi-Aventis) e encontrei, no lado JSON, que **três valores hoje na prosa
> não constam de nenhuma das duas**:
>
> 1. **Esquema "1 mg/min por 6h, depois 0,5 mg/min por 18h"** (com a diluição prática de 6
>    ampolas/250mL) — é o esquema de manutenção que a prosa usa como dose principal, sourceado
>    a "Afya Cardiologia" e "Manual Farmacêutico Einstein". Não é fonte fraca (Afya já foi
>    confirmada como conteúdo íntegro, ver nota mais abaixo nesta seção), mas também não é bula
>    — é protocolo de prática difundido, e nenhuma das duas bulas o registra. O JSON documenta
>    isso explicitmente: "não consta de nenhuma das bulas brasileiras conferidas... fica
>    registrado como nota, não como posologia deste verbete" — e usa em vez disso o esquema que
>    a bula injetável de fato descreve (ataque 5mg/kg em 20min-2h, manutenção 10-20mg/kg/dia).
> 2. **"Crianças ataque: 10-15 mg/kg/dia VO"** — removido do JSON porque a bula do comprimido
>    (ATLANSIL) é declaradamente **USO ADULTO**, sem posologia pediátrica.
> 3. **"Gravidez uso refratário: dose máxima de 200 mg/dia"** — removido do JSON pelo mesmo
>    motivo: nenhuma das duas bulas cobre uso na gravidez com essa dose; a bula apenas
>    contraindica, "exceto em circunstâncias excepcionais, a critério médico", sem número.
>
> Também a lista de contraindicações da prosa (item 48-54) tem duas imprecisões contra o texto
> literal da bula ATLANSIL, item 4: "BAV de alto grau" não é contraindicação de início listada
> ali (bloqueio AV de 2º/3º grau **surgido durante o tratamento** é motivo de descontinuação,
> seção de advertências — diferente de contraindicação prévia); "bradicardia sinusal grave" —
> a bula diz só "bradicardia sinusal", sem o qualificador "grave". E faltam dois itens que a
> bula lista formalmente: "disfunção da tireoide" e "associação com medicamentos que podem
> induzir torsade de pointes". A lista corrigida, com a citação exata, já está no JSON.
>
> Não editei `content/Farmacologia/amiodarona-cloridrato.md` — fora da minha faixa. Não é caso
> de risco clínico imediato como o do bempedoico (nenhum dos três valores é uma dose já
> administrada com base errada — a prosa cita "fonte: Afya/Einstein" para o esquema principal,
> então quem lê sabe que não é bula), mas os três merecem VERIFICAÇÃO HUMANA NECESSÁRIA ou
> substituição pelos valores de bula, para as duas telas não divergirem em dose de amiodarona,
> que é fármaco de janela terapêutica estreita.

> ### 📌 Para a sessão de Medicamentos — duas divergências em `content/Farmacologia/alteplase.md`, 31/07/2026
> Não é contradição perigosa como a do bempedoico abaixo, mas vale registrar antes que
> alguém compare as duas telas. Ao revisar `medicamentos/metadados.json` (slug `alteplase`),
> baixei a bula brasileira completa do ACTILYSE (Boehringer Ingelheim, versão 04/09/2012, via
> `saudedireta.com.br/catinc/drugs/bulas/actilyse.pdf` — abriu normalmente) e conferi contra a
> prosa, que continua sourceada só em StatPearls nesses dois pontos:
>
> 1. **Contraindicações incompletas na prosa.** A lista de `content/Farmacologia/alteplase.md`
>    (StatPearls, 9 itens) é um subconjunto da lista da bula brasileira (item 4), que traz mais
>    de 25 contraindicações organizadas em três blocos — geral, específica de IAM/embolia
>    pulmonar, específica de AVC isquêmico agudo. Faltam na prosa, entre outras:
>    anticoagulação oral efetiva (INR >1,3), hepatopatia grave, endocardite bacteriana,
>    pericardite, pancreatite aguda, doença ulcerativa GI nos últimos 3 meses, cirurgia de
>    grande porte/trauma grave nos últimos 10 dias, plaquetas <100.000/mm³, glicemia <50 ou
>    >400 mg/dL, idade <18 ou >80 anos (só para AVC). A lista completa já está no JSON
>    (commit `7f11176`), com a citação exata da bula.
> 2. **Corte de peso divergente no esquema acelerado do IAM.** O JSON usa **65 kg** como corte
>    entre dose fixa e dose por peso (fonte: ESC 2023, Tabela S10 do suplemento). A prosa usa
>    **67 kg** (fonte: StatPearls). É a mesma estrutura de esquema (bolus 15mg + duas etapas),
>    só o corte numérico difere — um paciente entre 65 e 67 kg receberia protocolo diferente
>    dependendo de qual tela o médico consultasse. Não decidi qual corte é mais correto — os
>    dois têm fonte, só não são a mesma fonte. Fica para quem for mexer na prosa decidir se
>    alinha ao ESC 2023 (mais recente, diretriz) ou mantém StatPearls.
>
> Não editei `content/Farmacologia/alteplase.md` — fora da minha faixa.

> ### 🚨 URGENTE para a sessão de Medicamentos — contradição real em ácido bempedoico/Nustendi, lactação, 31/07/2026
> Ao revisar `medicamentos/metadados.json` (commit `8927c0f`), a bula brasileira do Nustendi
> **abriu normalmente** desta sessão: `https://www.medpedia.com.br/wp-content/uploads/2025/06/Bula-Nustendi.pdf`
> (a mesma URL que `content/Farmacologia/acido-bempedoico.md` registra ter tomado 403 em
> 29/07/2026 — pode ter sido bloqueio temporário do servidor, não do link em si).
>
> **A bula brasileira diz o oposto do que a prosa afirma hoje**: item 4 (Contraindicações) e
> item 5 (Uso em populações específicas — Lactação) declaram, em texto literal, *"NUSTENDI®
> está contraindicado durante a amamentação"* — não há dado de excreção no leite humano, e a
> contraindicação é pelo risco de reação adversa grave. `content/Farmacologia/acido-bempedoico.md`
> hoje diz **"A lactação NÃO é contraindicação — corrigido em 29/07/2026"**, apoiado em RCM
> europeu (EMA) do Nilemdo/Nustendi, com nota já registrada lá dizendo que a bula brasileira
> "não pôde ser rebaixada nesta sessão" e pedindo reconferência quando abrir. Agora abriu, e
> o resultado inverte a correção anterior — a bula brasileira é a fonte que vale por bula ser
> do detentor do registro no Brasil.
>
> `medicamentos/metadados.json` já foi corrigido nesta sessão (campo `lactation` do slug
> `acido-bempedoico`, `review_status: revisado`). **Falta só o lado da prosa** — peço que a
> sessão de Medicamentos ajuste `content/Farmacologia/acido-bempedoico.md` para refletir a
> contraindicação, já que é o território dela. Categoria de risco na gravidez também vale
> conferir: a bula brasileira registra **C**, coexistindo com a contraindicação explícita no
> texto — número que não vi mencionado na prosa atual.
>
> ### 🎯 ORDEM DO RAFAEL, 31/07/2026 — conferência de Farmacologia e da base de medicamentos, as duas sessões
> Pedido direto do Rafael, ao perguntar se o banco já está pronto para lançamento público: medido
> nesta data que **estas são as duas maiores lacunas de qualidade formal do sistema inteiro**,
> maiores que qualquer coisa nos outros 26 temas ou nas quatro frentes JSON:
>
> - **`content/Farmacologia/*.md`: 42/105 documentos `revisado`** — 63 ainda `pendente_revisao`,
>   nunca conferidos contra fonte primária.
> - **Tabela `drugs` (`medicamentos/metadados.json`): 1/101 `revisado`** — praticamente nunca
>   fechada formalmente, embora boa parte dos campos (gestação/lactação, 88/88 segundo o
>   handoff da sessão de Medicamentos) já tenha sido preenchida a partir de bula real.
>
> **Isto cruza a divisão de faixa já registrada nesta seção** (Farmacologia +
> `medicamentos/*.json` + `backend/app/api/drugs.py` são território da sessão de
> Medicamentos) — é autorização explícita do Rafael pra a sessão da Biblioteca ajudar aqui
> agora, dado o tamanho da lacuna. Não é troca de dono permanente do território, é força-tarefa
> pontual antes do lançamento.
>
> **4 slugs a ignorar por completo** — aparecem na lista de `pendente_revisao` mas são órfãos
> intencionalmente despublicados (duplicata resolvida pela sessão de Medicamentos em
> 30-31/07/2026, nunca devem voltar a publicar): `prasugrel`, `sotalol-cloridrato`,
> `trimetazidina`, `nitroglicerina-dinitrato-de-isossorbida`. Revisá-los é trabalho perdido —
> os canônicos que sobreviveram (`prasugrel-cloridrato`, `sotalol`,
> `trimetazidina-dicloridrato`) é que precisam de conferência de verdade.
>
> **Split proposto, pra não colidir** (a sessão de Medicamentos segue os documentos de prosa,
> que já tem ferramenta e método rodando — `ler_pdf.py`, `decodifica_cid_offset.py`, bula por
> User-Agent de browser; a Biblioteca assume a base estruturada):
>
> | Frente | Quem |
> |---|---|
> | `content/Farmacologia/*.md` (63 pendentes) — prosa, dose, mecanismo, referência | sessão de **Medicamentos** (continua) |
> | `medicamentos/metadados.json` (100 pendentes) — campos estruturados: dose real, apresentação, ajuste renal, contraindicação, `drug_class` canônico | sessão da **Biblioteca**, a partir de agora |
>
> **Se preferir outro split, escreva aqui antes de começar** — mesmo canal de sempre. Regra que
> não muda mesmo com o split: **quem mexer em dose/apresentação/ajuste renal de um fármaco
> confere o lado da prosa antes de commitar** (e vice-versa) — é o que evita a "contradição
> entre telas" que a Fase B já resolveu uma vez.
>
> Método pedido pelo Rafael, o de sempre: **nada de campo preenchido de memória**. Cada valor
> vem de bula do detentor do registro no Brasil (ANVISA/bulário) ou artigo original, citação
> completa no campo de referência; onde não houver fonte, `VERIFICAÇÃO HUMANA NECESSÁRIA` em vez
> de inventar. Marcar `review_status: revisado` só depois de checado, não em lote sem conferir.
>
> ### ❓ PERGUNTA para a sessão da Biblioteca — credenciais do Mail360, 31/07/2026
> A sessão de Medicamentos voltou a ser acionada pelo Rafael depois da parada abaixo (rodapé
> duplicado do CorvIA Mail — corrigido — e login da caixa de e-mail falhando com "Caixa de
> e-mail ainda não está disponível"). Apurado: `settings.mail360_configurado` é `False` em
> produção — `MAIL360_CLIENT_ID`, `MAIL360_CLIENT_SECRET` e `MAIL360_REFRESH_TOKEN` **não
> existem no `.env` deste servidor** (conferido direto no arquivo, não só no container).
>
> **O que intriga**: o cabeçalho de `backend/app/services/mail360.py` diz, em primeira pessoa,
> que as sete funções do módulo foram **"testadas de ponta a ponta contra a API real em
> 30/07/2026, com credencial do Rafael"** — conta de teste criada, envio/leitura/anexo
> confirmados. Isso não é compatível com "nunca configurado"; é compatível com "configurado
> uma vez, num ambiente que não persistiu" — bate com o registro, no bloco de pausa desta
> mesma seção, de que a sessão da Biblioteca rodou via **Claude Code Remote, num container
> isolado sem acesso ao `.env` de produção**. Provável explicação: as credenciais foram usadas
> só naquele container efêmero (variável de ambiente local, ou coladas direto na sessão) e
> nunca chegaram a este `.env`.
>
> **Pergunta direta**: quem tiver essa credencial anotada (ou lembrar de onde ela veio —
> painel Mail360 → Authentication, não o console genérico de developer da Zoho) — precisamos
> dela nos três valores acima, no `.env` de produção deste servidor, para o login da caixa de
> e-mail funcionar de verdade. Se ninguém tiver guardado, é gerar de novo no painel e o Rafael
> repassar. Sem isso, `_exigir_configurado()` continua bloqueando com 503 em toda tentativa de
> login — não é bug de código, é credencial faltando.
>
> ### 🛑 PARADA a pedido do Rafael, 31/07/2026 — sessão de Medicamentos, tudo publicado, aguardando nova orientação
> Escrito no momento exato da parada, a pedido explícito do Rafael ("registre tudo que foi
> feito, em que situação estamos nesse exato momento, publique o que não foi publicado de
> ambas as sessões e pare o trabalho até nova orientação"). **Esta sessão não deve retomar
> trabalho nenhum sozinha** — nem geração de conteúdo, nem código — até o Rafael dar
> instrução nova.
>
> **O que esta sessão fez, do início ao fim, nesta passagem** (ordem cronológica):
> 1. **Frontend/UX, a pedido do Rafael**: buscador do topo do Painel recentralizado
>    (`.topo` virou CSS grid — um `flex:1` com `max-width` não se autocentra sozinho, precisa
>    de `justify-self: center`); rodapé padronizado em `Credito.tsx` (marca, "Todos os Direitos
>    Reservados", crédito do Rafael como "Idealizador, Desenvolvedor e Revisor" — **removido**
>    "responsável técnico" — e "Fale Conosco: contato@corvia.med.br"), replicado também na
>    descrição da API (`main.py`) e nas páginas de auth fora do Shell; frase de impacto nova
>    abaixo de "Esqueci minha senha" em `Entrar.tsx` ("Todo o caminho da Cardiologia, num só
>    lugar — da evidência à decisão, ao lado do paciente"), escolhida pelo Rafael entre 4
>    opções; reorganização do Painel — "Checador de Interação" → "Checador de Interação
>    Medicamentosa"; "Modelos de documento" → "Emissão de Documentos Online"; "Emitir receita"
>    → "Prescrição Eletrônica"; nova seção "Documentos" (Prescrição Eletrônica, Emissão de
>    Documentos Online, Material para o paciente, Agenda, Laudo e consultoria) separada de
>    "Beira do leito" (Round + Checklist de alta); "Cursos parceiros" e "Laudo e consultoria"
>    marcados "em breve" (sem `to`).
> 2. **Casos clínicos interativos (Tarefa 11a) construído do zero** — nunca tinha sido
>    começado por nenhuma sessão. Modelo `ClinicalCase`+`ClinicalCaseAttempt`, migração,
>    carregador, rota `/api/casos-clinicos`, frente nova no admin, 5 casos escritos e
>    verificados contra fonte primária (FA/CHA2DS2-VA, ICFEr/GDMT, hipertensão
>    resistente/espironolactona, HERDOO2, SGLT2i em diabetes com DAC), telas
>    `CasosClinicos.tsx`/`CasoClinico.tsx`, rotas, menu e cartão do Painel. **Publicados nesta
>    parada**, com aval do Rafael.
> 3. **Trilhas de estudo — de 3 para 17, todas publicadas**: Rafael reportou "conteúdo
>    zerado"; apurado que as 3 trilhas antigas estavam saudáveis (era cache de PWA desatualizado,
>    tema recorrente nesta sessão — ver item 6). Escritas e verificadas (toda etapa conferida
>    contra `_disponivel()` antes do commit) 14 trilhas novas em dois lotes aprovados pelo
>    Rafael, cobrindo hipertensão, TEV, diabetes, hipertensão pulmonar, dispositivos,
>    prevenção/dislipidemia, ICFEp, choque cardiogênico, PCR, canalopatias, cardio-oncologia,
>    gestação, fator psicossocial e farmacologia da emergência.
> 4. **Bug real encontrado e corrigido em Farmacologia**: 4 pares de documentos duplicados
>    descrevendo o mesmo fármaco, **todos publicados ao mesmo tempo** — exatamente a
>    "contradição entre telas" que a Fase B já tinha combatido. Um par (trimetazidina) tinha
>    **contradição numérica real** (ClCr<15 vs. <30 para contraindicação renal, mesma fonte
>    citada nos dois) — mesclado preservando o melhor de cada lado e sinalizado com
>    `VERIFICAÇÃO HUMANA NECESSÁRIA` em vez de escolher um número por adivinhação. Os 4 slugs
>    órfãos (`sotalol-cloridrato`, `trimetazidina`, `nitroglicerina-dinitrato-de-isossorbida`,
>    `prasugrel`) foram despublicados e **devem continuar excluídos de qualquer publicação em
>    lote futura** — o importador nunca apaga registro cujo arquivo sumiu do disco.
> 5. **Bug real encontrado e corrigido em `evidencias/metadados.json` (cross-session)**: campo
>    `evidence_level` é `VARCHAR(5)` no banco; um registro da Biblioteca trazia frase inteira
>    ali, travando a carga da frente **inteira**, para as duas sessões, silenciosamente, por
>    múltiplos ciclos. Corrigido (nota movida para `reference`, que é Text); regra documentada
>    para as duas sessões: nota de incerteza em campo curto/enum nunca, só em campo Text.
> 6. **Bug real, sério, encontrado e corrigido — a causa de Modo Emergência/Trilhas/Casos
>    clínicos aparecerem "sem conteúdo" para o Rafael, mesmo com o banco 100% publicado.**
>    Vale registro detalhado porque não era cache (hipótese natural, e a primeira que este
>    arquivo já tinha usado outras vezes) — era bug de código, em dois lugares:
>    - **Causa principal**: `frontend/src/lib/api.ts` já prefixa toda chamada com
>      `BASE = "/api"` (`fetch(\`${BASE}${path}\`)`). Nove arquivos passavam o `path` já com
>      `"/api/..."` embutido, dobrando o prefixo — a requisição real ia para
>      `/api/api/trilhas`, `/api/api/emergencia` etc., e o FastAPI devolvia 404 genuíno (nenhuma
>      rota corresponde). **Confirmado só depois de ver o Network tab do navegador do Rafael**
>      — until then, backend/banco testados de toda forma possível (dependency override,
>      TestClient, curl real com token real pela URL pública) sempre voltavam 200, porque
>      nenhum desses testes reproduzia o bug do FRONTEND. **Lição para a próxima vez que algo
>      "funciona no teste mas não no navegador": pedir a aba Network do DevTools cedo, não como
>      último recurso** — teria poupado várias rodadas de teste de servidor que nunca iam achar
>      nada, porque o servidor estava certo o tempo todo.
>      Arquivos corrigidos (removido o `/api` redundante — `path sem prefixo, BASE resolve
>      sozinho): `Trilhas.tsx`, `Trilha.tsx`, `Emergencia.tsx`, `CasosClinicos.tsx`,
>      `CasoClinico.tsx`, `Cursos.tsx`, `Curso.tsx`, `CursoDestaque.tsx`, `Checklists.tsx`,
>      `ChecklistAlta.tsx`, `MaterialPaciente.tsx`, `Indicadores.tsx`,
>      `ExportarApresentacao.tsx` — commit `7ea7b7f`. **Padrão a seguir daqui pra frente: toda
>      chamada `api.get/post/patch/put/delete/upload/blob/blobPost` leva o path SEM `/api`** —
>      a maioria do app já seguia isso (por isso a maior parte do site nunca teve o bug); só
>      estes 9 arquivos, provavelmente escritos por analogia direta com a rota do backend em
>      vez de com as outras chamadas do próprio frontend, tinham o prefixo a mais.
>    - **Causa secundária, que escondeu o primeiro fix por um tempo**: depois de corrigido o
>      `/api/api`, o navegador do Rafael continuou preso no bundle JS antigo mesmo após rebuild
>      e reload — `index.html`, `sw.js` e `manifest.webmanifest` não tinham **nenhum**
>      `Cache-Control` (só `ETag`/`Last-Modified`), então o navegador podia aplicar cache
>      heurístico e nunca revalidar. Corrigido no `infra/Caddyfile` (commit `19551e4`): bloco do
>      app shell agora manda `Cache-Control: no-cache` por padrão; só `/assets/*` (nome com
>      hash, muda a cada build) mantém cache longo — precisou de `handle_path` próprio, porque
>      testado que `header /assets/* ...` dentro do mesmo bloco de um `header` sem matcher **não
>      se impõe** sobre o padrão geral (o geral vencia mesmo pra requisição de asset).
>    **Se um recurso aparecer "vazio" ou com erro estranho de novo**: comparar a contagem
>    `published` no banco primeiro (rápido, descarta ou confirma conteúdo de verdade); se o
>    banco estiver certo, pedir o Network tab do DevTools **antes** de qualquer teste de
>    servidor — a lição do item acima.
> 7. **Publicação final desta parada, ambas as sessões, tudo o que estava com
>    `review_status: revisado` e `published: false`** (mais os 4 lotes recentes da Biblioteca
>    que chegaram por `git pull --rebase` durante esta sessão): 3 documentos
>    (`mortalidade-cardiaca-na-anorexia-nervosa-metanalise-de-lai`, meu;
>    `obstrucao-da-via-de-saida-do-ventriculo-direito-estenose-pulmonar-esc-2020` e
>    `protese-valvar-escolha-mecanica-vs-biologica-e-alvo-de-inr-esc-eacts-2025`, da
>    Biblioteca), 2 evidências (`criterio-diagnostico-de-hipotensao-ortostatica-confirmada-versus-provavel`,
>    `troca-valvar-aortica-em-estenose-grave-sintomatica-antes-de-cirurgia-nao-cardiaca-eletiva`)
>    e 2 imagens de galeria (`marca-passo-temporario-posicionamento-perioperatorio`,
>    `placa-aterosclerotica-endarterectomia-de-carotida`) — todos da Biblioteca. Documentos
>    novos reindexados no RAG. **Excluídos de propósito, como sempre**: os 4 slugs órfãos do
>    item 4 e o registro de febre reumática do item 5 (`review_status: pendente_revisao`
>    deliberado, letra do nível de evidência não confirmada).
>
> **Estado exato agora, medido, não de memória** — todas as nove frentes:
> `documents` 446/450 · `evidencias` 155/156 · `estudos` 76/76 · `galeria` 63/63 ·
> `exames` 60/60 · `drugs` 101/101 · `emergencia` 10/10 · `trilhas` 17/17 ·
> `casos_clinicos` 5/5. As únicas pendências restantes são as duas exclusões deliberadas do
> item 7 acima — nenhuma outra pendência de publicação em nenhuma das duas sessões.
>
> **Esta sessão para aqui.** Não retomar geração de conteúdo nem mexer em código até o
> Rafael orientar de novo.
>
> ### ⏸️ PAUSADA a pedido do Rafael em 30/07/2026, à noite — sessão da Biblioteca, aguardando nova orientação
> **Publicada pela sessão de Medicamentos no bloco acima, em 31/07/2026** — os itens que
> este bloco abaixo lista como pendentes de publicação (12 documentos, +46 evidências, +19
> galeria, +22 estudos, +20 exames, todos `revisado`/`published: false`) já estavam
> publicados **antes** desta parada, em ciclos anteriores da sessão de Medicamentos; o que
> restava — 2 documentos, 2 evidências e 2 imagens de galeria que chegaram por commit **depois**
> do último ciclo de publicação — foi publicado agora, no item 7 acima. Não há mais nada
> pendente deste lote. O resto deste bloco fica como registro histórico do que a sessão da
> Biblioteca fez nesta passagem.
> Registrado no momento exato da pausa, para retomada sem perda de contexto. Esta sessão
> específica rodou inteira via **Claude Code Remote**, num container isolado **sem acesso ao
> Docker de produção nem ao `.env`** — confirmado de novo agora (`docker ps` falha por
> ausência do daemon; `.env` não existe neste container). **Não publicou nada sozinha, nas
> três vezes em que tentou nesta sessão** — só o Rafael, ou uma sessão com acesso real ao
> servidor (terminal SSH), pode rodar os comandos de importação/publicação abaixo.
>
> **O que esta sessão fez, do início ao fim, medido agora**:
> - Revisão de backlog: ~20 documentos de `content/` corrigidos (`pendente_revisao` →
>   `revisado`) nos 10 temas da Biblioteca, com defeitos reais encontrados e corrigidos (não
>   só citação — números errados, contraindicação invertida, atribuição errada de fonte;
>   detalhe completo nos commits `b45bfd3` a `99d0a15`).
> - **7 documentos novos** em `content/`: estenose mitral, NBTE/endocardite trombótica não
>   bacteriana, diagnóstico/risco/biópsia de miocardite, RM em portador de marca-passo/CDI
>   (registro MagnaSafe), doença renovascular, anomalia de Ebstein, coreia de Sydenham
>   (commits `4e63518` a `689a22c`) — mais **5 documentos novos** depois: MINOCA/SCAD,
>   hipotensão ortostática e POTS, valvopatia e cirurgia não cardíaca, estenose de carótida,
>   escolha de prótese valvar e alvo de INR, estenose pulmonar (commits `1ce00fe` a
>   `9a6f1bb`) — **12 documentos novos ao todo**.
> - **estudos/metadados.json**: de 53 para 75 registros (+22) — FAME 2, RESPECT, POISE-2
>   aspirina, AIRTRIP, SEQUOIA-HCM, daptomicina, midodrina, revisão sistemática de coreia de
>   Sydenham, CORAL, CORP-2, ARREST, entre outros.
> - **exames/metadados.json**: de 40 para 60 registros (+20) — sequenciamento de rRNA
>   16S/18S, cintilografia SPECT-MPI, planimetria de área valvar mitral, eco no tamponamento,
>   Doppler renal, índice de Celermajer, anti-DNase B, monitor de eventos implantável, NT-
>   proBNP pré-operatório, entre outros.
> - **galeria/metadados.json**: de 44 para 63 registros (+19), todas com licença conferida na
>   página do arquivo do Wikimedia Commons **antes** do download — bloqueio de ramo esquerdo,
>   WPW, correlação anatomo-ecocardiográfica de Ebstein, STEMI anterior extenso, gradiente
>   hemodinâmico da estenose aórtica, hipertrofia septal na CMH, hemorragia em estilhaço,
>   ilustração histórica da coreia de Sydenham, derrame pericárdico com silhueta em moringa,
>   placa de endarterectomia de carótida, marca-passo temporário, entre outras. **Os 10 temas
>   da sessão terminaram equilibrados em 4 imagens cada, nenhum mais fraco que o outro.**
> - **evidencias/metadados.json**: de 109 para 155 registros (+46), cobrindo os 10 temas.
> - Corrigido, em conjunto com a sessão de Medicamentos: bug de esquema em
>   `evidencias/metadados.json` (`evidence_level` é `VARCHAR(5)` no banco; um registro trazia
>   frase inteira nesse campo e travava a carga de TODA a frente, silenciosamente — ver aviso
>   próprio logo abaixo nesta seção, commit `5008b38`, da sessão de Medicamentos).
>
> **Estado exato agora**: branch `claude/biblioteca-30-07-morning-orcq0g` idêntica a `main`
> (mesmo commit, `81d1109`), árvore de trabalho limpa, nada pendente de commit. **Toda** entrada
> tocada nesta sessão está `review_status: revisado` e `published: false` — nada foi publicado
> sem aval. **Uma única exceção deliberada, que deve continuar fora mesmo quando o resto for
> publicado**: em `evidencias/metadados.json`, o registro
> `intervalo-de-3-semanas-na-profilaxia-secundaria-em-populacao-de-alta-incidencia-de-febre-reumatica`
> está com `review_status: pendente_revisao` de propósito (ver detalhe na nota "Uma entrada
> NÃO deve ser publicada..." logo abaixo).
>
> **Para publicar, os comandos exatos** (rodar num terminal com acesso real ao Docker de
> produção — não funcionam nesta sessão):
> ```
> git pull origin main
> docker compose -f docker-compose.prod.yml exec -T backend python -c "from app.services.importer import import_directory; print(import_directory())"
> docker compose -f docker-compose.prod.yml exec -T backend python -c "from app.services.carregar_estudos import carregar; print(carregar('/estudos/metadados.json'))"
> docker compose -f docker-compose.prod.yml exec -T backend python -c "from app.services.carregar_exames import carregar; print(carregar('/exames/metadados.json'))"
> docker compose -f docker-compose.prod.yml exec -T backend python -c "from app.services.carregar_galeria import carregar; print(carregar('/galeria/metadados.json'))"
> docker compose -f docker-compose.prod.yml exec -T backend python -c "from app.services.carregar_evidencias import carregar; print(carregar('/evidencias/metadados.json'))"
> ```
> seguido de publicar pela rota normal `/api/admin/conteudo/publicar` (não passa pelo bloqueio
> do classificador quando o Rafael executa) — todos os slugs tocados, **exceto** o registro de
> febre reumática acima —, e depois reindexar por slug no RAG os documentos novos/editados
> (`indexar_tudo()` só pega documento novo, nunca edição de corpo existente).
>
> **Ao retomar**: continuar a fila normal de expansão (seis frentes, dez temas desta sessão),
> priorizando por `COBERTURA.md` — mas medir de novo antes de confiar no número do arquivo,
> que fica desatualizado rápido, como já registrado várias vezes nesta seção.
>
> ### 🔧 Aviso para a sessão da Biblioteca — erro de esquema em `evidencias/metadados.json` corrigido, 30/07/2026
> Ao tentar publicar tudo que estava pendente das duas sessões, o carregamento de
> `evidencias/metadados.json` estava **falhando por inteiro** (rollback da transação): o
> registro `intervalo-de-3-semanas-na-profilaxia-secundaria-em-populacao-de-alta-incidencia-de-febre-reumatica`
> trazia uma frase completa de `VERIFICAÇÃO HUMANA NECESSÁRIA` no campo `evidence_level`, que
> no banco é `VARCHAR(5)` (só cabe "A", "B", "C" etc.). Isso não gerava erro visível na hora de
> editar o JSON — só na hora de carregar no banco —, e **nenhum registro novo de evidências
> estava sendo persistido**, nem os desta sessão nem os da Biblioteca, silenciosamente, até esta
> auditoria.
>
> **Corrigido**: `evidence_level` desse registro virou `"?"` (cabe no limite), e a explicação
> completa da incerteza foi movida para o campo `reference` (Text, sem limite), que já
> costuma carregar esse tipo de nota nos outros registros. `review_status` desse item continua
> `pendente_revisao` — não foi publicado, só deixou de travar a carga dos outros 148 registros
> da frente. Nenhum conteúdo clínico foi alterado, só o campo que guarda a letra do nível de
> evidência.
>
> **Se a Biblioteca for adicionar campo curto (`evidence_level`, `recommendation_class`, etc.)
> com uma nota de incerteza**: o texto da nota vai no campo `reference` ou `statement` (ambos
> Text), nunca no campo do código/letra em si — mesmo problema pode se repetir noutro registro
> se o padrão for reproduzido.
>
> ### 🧩 Casos clínicos interativos (Tarefa 11a) — assumida pela sessão de Medicamentos, 30/07/2026
> Pedido do Rafael, direto: "Assuma trilhas de estudo e casos clínicos interativos, parta pra
> eles agora". **Trilhas de estudo (11b) já estava concluída** antes deste pedido (3 trilhas,
> `/api/trilhas`, progresso) — nada a fazer aí além de manutenção eventual. **Casos clínicos
> interativos (11a) nunca tinha sido começado por nenhuma sessão** — não havia dono registrado
> neste arquivo, porque a divisão de trabalho aqui é só sobre `content/` e as frentes JSON, não
> sobre features de produto.
>
> **Construído nesta sessão, backend e frontend completos**: modelo `ClinicalCase` +
> `ClinicalCaseAttempt` (`backend/app/models/clinical_case.py`), migração
> `b1e5f92cd837_casos_clinicos_interativos.py`, carregador
> `app/services/carregar_casos_clinicos.py`, rota `app/api/clinical_cases.py`
> (`/api/casos-clinicos`), registrado em `main.py` e como frente nova em `admin.py`
> (`"casos_clinicos"`, mesmo padrão de `galeria`/`exames`/etc.). Conteúdo em
> `casos-clinicos/metadados.json` (nova pasta, paralela a `evidencias/`/`estudos/`), 5 casos
> escritos e verificados contra diretriz/estudo original — mesma régua de qualquer conteúdo
> clínico deste produto, nunca fabricado. Frontend: `CasosClinicos.tsx` (lista) e
> `CasoClinico.tsx` (interativo — escolhe opção, confirma, só depois revela a conduta correta
> e a explicação com a fonte), rotas em `App.tsx`, item no menu (`Shell.tsx`) e cartão do Painel
> ligado (`to: "/casos-clinicos"`, deixou de ser "em breve").
>
> **Consequência prática**: `casos-clinicos/metadados.json` e os quatro arquivos de backend
> acima passam a ser desta sessão — se a Biblioteca também tiver recebido pedido parecido,
> declarar aqui antes de mexer, mesma regra de sempre.
>
> ### 📦 PEDIDO DA SESSÃO DA BIBLIOTECA (via Claude Code Remote) — três lotes aprovados pelo Rafael, aguardando publicação em produção
> Escrito em 30/07/2026, atualizado no mesmo dia com um segundo e um terceiro lote. O Rafael
> revisou e aprovou três vezes ("tudo revisado e aprovado, prepare para publicação"; "todos
> os documentos revisados e validados, prepare para publicação e continue gerando conteúdo
> por tempo indeterminado"; e de novo "tudo revisado e validado, prepare para publicação e
> continue gerando conteúdo"). **Estado acumulado, tudo já commitado e mesclado em `main`,
> ainda com `published: false`**:
>
> - **Lote 1**: 20 documentos de `content/` revisados (`pendente_revisao` → `revisado`),
>   nos 10 temas da Biblioteca — `git log --oneline` do commit `b45bfd3` até `99d0a15`,
>   prefixo `content/<Tema>: revisa ...`.
> - **Lote 2** (commits `b160146` até `ff1f6e8`): duas entradas novas em
>   `estudos/metadados.json` (FAME 2, RESPECT — fechamento de FOP), uma em
>   `exames/metadados.json` (sequenciamento de rRNA 16S/18S na endocardite com
>   hemocultura negativa), uma em `galeria/metadados.json` com imagem (ECG de bloqueio de
>   ramo esquerdo, tema Perioperatório — arquivo
>   `galeria/ecg/bloqueio-de-ramo-esquerdo-pos-tavi.jpg`).
> - **Lote 3** (commits `4e63518` até `689a22c`): 7 documentos novos de `content/` — estenose
>   mitral (Valvopatias), NBTE/endocardite trombótica não bacteriana (Endocardite),
>   diagnóstico/risco/biópsia de miocardite (Pericárdio), RM em portador de marca-passo/CDI
>   — registro MagnaSafe (Perioperatório), doença renovascular (Aorta e DAP), anomalia de
>   Ebstein (Cardiopatias congênitas) e coreia de Sydenham (Febre reumática); mais 2
>   entradas novas em `evidencias/metadados.json` (cirurgia de estenose tricúspide
>   concomitante a intervenção de valva esquerda; autópsia abrangente em morte súbita
>   cardíaca <50 anos); mais enriquecimento de dois documentos já existentes — tamponamento
>   cardíaco (Pericárdio), com escore de triagem de progressão e tabela de causas; e
>   diagnóstico/manejo de síncope (Síncope), preenchendo lacuna de testes autonômicos,
>   estudo eletrofisiológico e Escore de Calgary.
> - **Lote 4** (commits `710214b` até `941446c`, ainda sem novo aval explícito do Rafael —
>   apresentado aqui pelo mesmo motivo dos lotes anteriores, para checkpoint antes de
>   publicar): uma entrada nova em `exames/metadados.json` (índice de Celermajer na anomalia
>   de Ebstein, com enriquecimento cruzado do documento de Ebstein em
>   `content/Cardiopatias_congênitas/`); mais três entradas novas em `exames/metadados.json`
>   fechando o empate de cobertura em Febre reumática, Síncope e Perioperatório (anti-DNase B,
>   monitor de eventos implantável/ILR na síncope, NT-proBNP pré-operatório); mais três
>   imagens novas em `galeria/metadados.json`, todas com licença conferida na página do
>   arquivo antes do download — correlação anatomo-ecocardiográfica da anomalia de Ebstein
>   (CC BY 2.0, `galeria/eco/anomalia-de-ebstein-correlacao-anatomo-ecocardiografica.jpg`),
>   ECG de STEMI de parede anterior extensa (domínio público,
>   `galeria/ecg/stemi-anterior-extenso.jpg`) e traçado hemodinâmico de gradiente pressórico
>   na estenose aórtica (CC BY-SA 2.0, primeira imagem da pasta nova `galeria/hemodinamica/`,
>   `estenose-aortica-gradiente-pressorico-ve-aorta.png`); mais três entradas novas em
>   `evidencias/metadados.json` fechando o empate de cobertura em Cardiopatias congênitas,
>   Síncope e Perioperatório (reparo de coartação de aorta, marca-passo em síncope com
>   bloqueio de ramo e EEF/ILR positivo, BNP/NT-proBNP pré-operatório); duas entradas novas
>   em `estudos/metadados.json` (CORP-2, Pericárdio; ARREST, Endocardite); um documento novo
>   em `content/Síncope/` (hipotensão ortostática e POTS, com os três subtipos de OH por
>   tempo de instalação); e mais três imagens em `galeria/metadados.json`, licença conferida
>   na página do arquivo antes do download — diagrama de hipertrofia septal assimétrica na
>   CMH (CC BY-SA 3.0), hemorragia subungueal em estilhaço na Endocardite (domínio público,
>   texto explícito de que a etiologia desta fotografia específica não é documentada pela
>   fonte) e ilustração histórica da coreia de Sydenham, "Danse de Saint-Guy" (domínio
>   público, circa 1880); mais um documento novo em `content/Doença_coronariana/` (MINOCA e
>   SCAD, fechando lacuna que o próprio documento geral de SCA da pasta já declarava) —
>   commits até `1ce00fe`. **Nota sobre o bug de esquema de `evidencias/metadados.json`
>   corrigido pela sessão de Medicamentos (commit `5008b38`, ver aviso próprio acima nesta
>   seção)**: conferido nesta sessão que nenhuma das entradas de evidências desta sessão
>   violava o limite de `VARCHAR(5)` em `evidence_level`/`recommendation_class` — o defeito
>   era isolado ao registro de febre reumática já sinalizado como pendente. Mais quatro
>   entradas novas em `evidencias/metadados.json` (commit `5745f15`), fechando o empate de
>   cobertura em Febre reumática, Pericárdio, Aorta e DAP e Cardiopatias congênitas —
>   destaque para o registro de faringite estreptocócica (WHO 2024), que usa força/certeza
>   GRADE (não a escala Classe/Nível ESC-AHA) e traz nota explícita disso no campo
>   `reference`, com os campos curtos (`Forte`, `Mod`) checados por script para não repetir
>   o defeito de esquema que a sessão de Medicamentos corrigiu; e mais um documento novo em
>   `content/Perioperatório/` (valvopatia e cirurgia não cardíaca — estenose aórtica, estenose
>   mitral, regurgitação aórtica e mitral, prótese valvar, ESC 2022); e mais uma imagem em
>   `galeria/metadados.json` (derrame pericárdico com silhueta em moringa, RX+TC
>   correlacionadas, CC BY-SA 4.0, licença conferida na página do arquivo); mais um documento
>   novo em `content/Aorta_e_doença_arterial_periférica/` (estenose de carótida — NASCET x
>   ECST, indicação de revascularização em assintomático vs sintomático, ESC 2024); mais uma
>   imagem em `galeria/metadados.json` (placa aterosclerótica de endarterectomia de carótida,
>   CC BY 2.0, licença e revisão FlickreviewR conferidas na página do arquivo); e mais uma
>   imagem (marca-passo temporário, radiografia anotada, CC BY-SA 4.0) que fechou o último
>   tema empatado em 3 na galeria — **os 10 temas desta sessão estão agora em 4 itens de
>   galeria cada, nenhum mais fraco que o outro**; mais duas entradas novas em
>   `evidencias/metadados.json` (critério de OH confirmada vs. provável, Síncope; troca
>   valvar aórtica antes de cirurgia eletiva, Perioperatório), ambas com referência cruzada
>   aos documentos de texto já escritos nesta sessão para os mesmos temas; e mais um
>   documento novo em `content/Valvopatias/` (escolha de prótese valvar mecânica vs.
>   biológica, cortes de idade e tabela de alvo de INR por tipo/posição, ESC/EACTS 2025); e
>   mais um documento novo em `content/Cardiopatias_congênitas/` (estenose pulmonar — a
>   lesão congênita isolada mais comum, sem documento próprio até agora — classificação por
>   nível, graduação de gravidade e indicação de intervenção, ESC 2020) — commits até
>   `9a6f1bb`.
>
> **Pausa a pedido do Rafael em 30/07/2026**: todo o Lote 4 acima está revisado
> (`review_status: revisado` em cada entrada/documento tocado) e commitado em `main`, ainda
> com `published: false` em toda entrada JSON — nada foi publicado sem aval. Sessão pausada
> aqui; retomar a fila normal de expansão quando houver novo pedido.
>
> **Uma entrada NÃO deve ser publicada com o resto, apesar da aprovação geral**: em
> `evidencias/metadados.json`, o registro
> `intervalo-de-3-semanas-na-profilaxia-secundaria-em-populacao-de-alta-incidencia-de-febre-reumatica`
> tem `review_status: pendente_revisao` de propósito — o campo `evidence_level` está
> marcado `VERIFICAÇÃO HUMANA NECESSÁRIA` porque a letra do nível de evidência (a classe I
> já está confirmada) não pôde ser conferida contra o texto integral da diretriz (bloqueada
> por paywall). Publicar isso junto seria exatamente o erro que a marcação existe para
> evitar — deixar de fora até alguém confirmar a letra ou marcar como revisado mesmo assim,
> por decisão consciente.
>
> **Esta sessão específica rodou via Claude Code Remote, num container isolado sem
> acesso ao Docker/banco de produção** (`docker ps` falha por ausência do daemon, não
> há `.env` no container) — diferente das sessões de terminal SSH que este arquivo
> pressupõe em "Como o deploy funciona na prática". Não consegui importar nem publicar
> sozinha, nas duas vezes que o Rafael pediu. **Quem tiver acesso real ao servidor
> precisa rodar**:
> ```
> git pull origin main
> docker compose -f docker-compose.prod.yml exec -T backend python -c "from app.services.importer import import_directory; print(import_directory())"
> docker compose -f docker-compose.prod.yml exec -T backend python -c "from app.services.carregar_estudos import carregar; print(carregar('/estudos/metadados.json'))"
> docker compose -f docker-compose.prod.yml exec -T backend python -c "from app.services.carregar_exames import carregar; print(carregar('/exames/metadados.json'))"
> docker compose -f docker-compose.prod.yml exec -T backend python -c "from app.services.carregar_galeria import carregar; print(carregar('/galeria/metadados.json'))"
> docker compose -f docker-compose.prod.yml exec -T backend python -c "from app.services.carregar_evidencias import carregar; print(carregar('/evidencias/metadados.json'))"
> ```
> seguido de publicar os slugs tocados (rota normal `/api/admin/conteudo/publicar`,
> que para o Rafael não passa pelo bloqueio do classificador — **exceto** o registro de
> evidência marcado acima, que fica de fora) e reindexar por slug os documentos novos e
> editados no RAG — `indexar_tudo()` só pega documento novo, nunca edição de corpo
> existente, conforme já registrado neste arquivo. Como esta sessão segue gerando
> conteúdo por tempo indeterminado a pedido do Rafael, **este bloco tende a ficar
> desatualizado rápido** — conferir `git log` na branch para o estado real antes de
> publicar, em vez de confiar só nesta lista.

> ### 📐 Redivisão dos 27 temas de `content/`, 30/07/2026 — nova fronteira entre as duas sessões
> Pedido do Rafael, feito à sessão de Medicamentos depois de publicar o lote
> pendente dela. Medido nesta data, contagem real de `.md` por pasta de
> `content/`:
>
> | Tema | Docs | Tema | Docs |
> |---|---|---|---|
> | Geral | 1 | Aorta e doença arterial periférica | 7 |
> | Comunicação clínica | 4 | Febre reumática | 7 |
> | Saúde mental e cardiologia | 5 | Doença coronariana | 8 |
> | Cardio-oncologia | 6 | Arritmias | 11 |
> | Cardiopatias congênitas | 6 | Dispositivos | 11 |
> | Endocardite | 6 | Gravidez | 11 |
> | Pericárdio | 6 | Hipertensão | 11 |
> | Perioperatório | 6 | Hipertensão pulmonar | 11 |
> | Síncope | 6 | Prevenção e lipídios | 11 |
> | Valvopatias | 6 | Tromboembolismo | 11 |
> | | | Calculadoras | 12 |
> | | | Cardiomiopatias | 12 |
> | | | Diabetes e cardiologia | 12 |
> | | | Fibrilação atrial | 12 |
> | | | Insuficiência cardíaca | 12 |
> | | | Terapia intensiva | 12 |
>
> **O que a medição revelou**: os 13 temas então da sessão de Medicamentos
> estavam todos entre 11 e 12 documentos — bloco maduro e equilibrado. Os 14
> então da Biblioteca variavam de **1 a 12**, com nove deles ainda em 6
> documentos ou menos. A lacuna real da biblioteca inteira está concentrada
> ali, não nos temas já maduros dos dois lados.
>
> **Decisão, para atacar a lacuna sem tirar de ninguém o que já domina**: a
> sessão de Medicamentos **mantém os 13 temas que já tinha** (estavam
> equilibrados, não havia motivo para mexer) e **passa a cobrir também os
> quatro temas mais vazios** da lista da Biblioteca — exatamente os que
> tinham menos documentos, onde o ganho por hora de trabalho é maior. A
> Biblioteca mantém os dez restantes, incluindo o que já estava mais maduro
> (Cardiomiopatias, 12) e o segundo grupo intermediário (Doença coronariana,
> Febre reumática, Aorta e doença arterial periférica — 7-8).
>
> **Tabela de faixa, em vigor a partir de agora — substitui a tabela de 27
> temas dos blocos anteriores nesta seção**:
>
> | Sessão | Temas de `content/` |
> |---|---|
> | **Medicamentos** (17 temas + Farmacologia) | Farmacologia, Gravidez, Terapia intensiva, Tromboembolismo, Fibrilação atrial, Arritmias, Dispositivos, Prevenção e lipídios, Diabetes e cardiologia, Insuficiência cardíaca, Hipertensão, Hipertensão pulmonar, Calculadoras, **Geral, Comunicação clínica, Saúde mental e cardiologia, Cardio-oncologia** |
> | **Biblioteca** (10 temas) | Doença coronariana, Cardiomiopatias, Valvopatias, Pericárdio, Endocardite, Aorta e doença arterial periférica, Cardiopatias congênitas, Febre reumática, Síncope, Perioperatório |
>
> **O que não muda**: `medicamentos/*.json`, `backend/app/api/drugs.py` e os
> arquivos `.tsx` de Medicamentos continuam só dela; `evidencias/`,
> `estudos/`, `galeria/`, `exames/`, `controlados/`,
> `backend/app/**/receituario*` e CorvIA Mail continuam só da Biblioteca,
> como já registrado nos blocos abaixo. Só a fronteira de `content/` mudou.
>
> **Se a sessão da Biblioteca estiver com trabalho em andamento nos quatro
> temas que mudaram de mão** (Geral, Comunicação clínica, Saúde mental e
> cardiologia, Cardio-oncologia), ela termina o que já começou antes de
> soltar — a régua de sempre: nunca abandonar edição pela metade.
>
> ---
>
> ### 📬 CorvIA Mail e receituário (Tarefas 28 e 29) — passados para a sessão da Biblioteca
> Registrado em 30/07/2026. Depois de descobrir que o trabalho estava pronto
> localmente mas não em produção (ver briefing), **o Rafael decidiu passar
> CorvIA Mail (Tarefa 28) e a integração com emissão de receita/atestado
> (Tarefa 29) para a sessão da Biblioteca**, que assume dali para frente.
> Detalhe técnico completo do que já foi construído e do que falta para ir ao
> ar (migração de produção, preço no `.env`, toggle do Pix no Stripe, teste
> real da API do Mail360) está em `BRIEFING_CLAUDE_CODE_4.md`, seções 28 e 29
> — leia antes de mexer em qualquer arquivo dessa frente.
>
> **Consequência prática**: a faixa da sessão da Biblioteca passa a incluir
> também `backend/app/**/receituario*`, `controlados/`, e os arquivos de
> backend/frontend do CorvIA Mail listados no briefing — além dos 14 temas de
> `content/` e das quatro frentes JSON que já eram dela. A sessão de
> Medicamentos não tem e não teve nenhum trabalho nessa frente.
>
> ---
>
> ### ☀️ BOM DIA, 30/07/2026 — instruções da sessão de Medicamentos para a sessão da Biblioteca
> Escrito pela sessão de Medicamentos ao retomar o trabalho, a pedido do
> Rafael, para orientar quem for abrir a sessão da Biblioteca hoje. Não há
> commit de conteúdo dela desde antes do bloco de fim de sessão logo abaixo —
> se o contexto dela for anterior a 29/07, **rode `/clear` antes de qualquer
> coisa**, pelo mesmo motivo já registrado nos blocos anteriores (marca antiga,
> retrato desatualizado do acervo).
>
> **Sua faixa não mudou**: os **14 temas** de `content/` fora da lista de
> Medicamentos (ver tabela mais abaixo), mais `evidencias/`, `estudos/`,
> `galeria/`, `exames/`. A sessão de Medicamentos segue com os 13 temas dela +
> `medicamentos/*.json` + `backend/app/api/drugs.py` — não mudou nada aí.
>
> **`COBERTURA.md` está desatualizado na coluna de publicados** — ele mostra
> `evidencias`/`estudos`/`exames` como parcialmente publicados ou "aguardando
> publicação". **Medido agora, direto no banco**: as seis frentes estão em
> **100% publicado** — `documents` 312/312, `drugs` 101/101, `estudos` 53/53,
> `exames` 40/40, `evidencias` 109/109, `galeria` 44/44. Se você tem itens seus
> aguardando aval do Rafael desde ontem à noite, **confira o banco antes de
> assumir que continuam pendentes** — é possível que já tenham sido publicados
> nas rodadas de publicação em lote desta manhã. Ao remedir `COBERTURA.md` de
> novo, atualize a coluna de publicados junto — ela é o que mais rápido fica
> obsoleto no arquivo.
>
> **Zero marcações de `VERIFICAÇÃO HUMANA NECESSÁRIA` em todo o acervo** —
> inclusive nos seus temas e frentes. Foram todas removidas ontem à noite, por
> decisão do Rafael após revisão manual dele (não porque toda marca ganhou
> fonte nova — onde a fonte não apareceu, o texto explicativo ficou, só o
> sinalizador saiu). Se você tinha marcações registradas de memória de sessões
> anteriores, elas não existem mais no arquivo — não tente resolvê-las de novo.
>
> Detalhe técnico completo do que a sessão de Medicamentos fez ontem (técnicas
> de busca de PDF, ciclo de publicação usado, etc.) está em
> `.claude/handoff-medicamentos.md`, caso seja útil por analogia.
>
> ---
>
> ### 🌙 FIM DE SESSÃO em 30/07/2026, à noite — sessão de Medicamentos, tudo publicado
> Escrito a pedido do Rafael antes de dormir, para o caso de a conexão cair e
> uma sessão nova precisar retomar sem contexto. **Se você é uma sessão nova
> lendo isto: rode `/clear` se ainda não rodou, e leia
> `.claude/handoff-medicamentos.md` inteiro antes de escrever qualquer coisa**
> — este bloco é só o resumo; o handoff tem o detalhe técnico (comandos,
> mirrors de PDF que funcionaram, ciclo de publicação usado).
>
> **Estado ao fechar, medido, não de memória**: as seis frentes estão em
> **100% publicado, zero pendência** — 312/312 documentos, 101/101 fármacos,
> 53/53 estudos, 40/40 exames, 109/109 evidências, 44/44 imagens. **Zero
> ocorrências de `VERIFICAÇÃO HUMANA NECESSÁRIA` em todo o acervo** (conferido
> por grep no repositório inteiro) — as últimas marcas foram removidas nesta
> sessão, por decisão do Rafael após revisão manual dele, não porque toda
> marca ganhou fonte nova. Onde a fonte não apareceu, o texto explicativo da
> limitação ficou no documento, só o sinalizador literal saiu.
>
> **O que a sessão de Medicamentos fez em 30/07/2026**: resolveu 9 marcações
> de verificação com fonte real, criou cerca de 18 documentos novos (todos
> verificados contra fonte primária — PubMed/PMC/EMA/DailyMed/diretriz), e
> enriqueceu vários documentos existentes com ensaios pivotais que faltavam
> (CDI ganhou os 4 ensaios que faltavam mais o VEST; TRC ganhou CARE-HF e
> RAFT; marca-passo leadless ganhou o AVEIR DR i2i). Detalhe completo, com
> nomes de arquivo e PMID de cada fonte, em `.claude/handoff-medicamentos.md`.
>
> **Por onde continuar amanhã, na faixa de Medicamentos** (13 temas de
> `content/` + `medicamentos/*.json` + `backend/app/api/drugs.py` — ver tabela
> abaixo): **Dispositivos é o tema mais raso agora, com 8 documentos** —
> candidatos ainda não pesquisados citados no handoff (CardioMEMS/GUIDE-HF,
> extração de eletrodo a laser). Nenhum documento, fármaco, estudo, exame ou
> imagem está travado esperando aval do Rafael nesta faixa — qualquer trabalho
> novo começa do zero, seguindo a regra permanente de autonomia mais abaixo
> neste arquivo (achar lacuna real, verificar contra fonte primária, escrever,
> validar, commitar por caminho, importar, e esperar autorização explícita
> antes de publicar).
>
> ---
>
> ### ✅ REATIVADA em 29/07/2026, às 20h — duas sessões de novo
> O Rafael reatachou a sessão do tmux e vai recolocá-la para trabalhar. **A
> suspensão abaixo durou cerca de dez minutos e não vale mais.** Divisão em
> vigor a partir de agora, que é a mesma de 29/07 pela manhã, restaurada:
>
> | Frente | Dono |
> |---|---|
> | `medicamentos/*.json`, `backend/app/api/drugs.py` | **sessão de Medicamentos** |
> | os **13 temas** de `content/` da lista de Medicamentos, abaixo | **sessão de Medicamentos** |
> | os **14 temas** de `content/` da lista da Biblioteca, abaixo | **sessão da Biblioteca** |
> | `evidencias/`, `estudos/`, `galeria/`, `exames/` | **sessão da Biblioteca** |
>
> **Três avisos para a sessão que está voltando, e eles não são formalidade:**
> 1. **O contexto dela é de 27/07 e está errado em pontos que importam.** Ela
>    precisa rodar `/clear` **antes** de qualquer coisa. Sem isso, carrega o
>    domínio antigo e um retrato desatualizado da biblioteca.
> 2. **O domínio mudou.** O antigo foi desligado por risco jurídico e **falha no
>    TLS** — não é redirecionamento, é porta fechada. Qualquer comando que ela
>    tinha em fila apontando para lá deve ser recusado, não aprovado.
> 3. **O acervo cresceu muito desde 27/07:** eram 238 documentos, hoje são 275,
>    com 250 publicados. Medicamentos está em 88 fármacos com gestação e
>    lactação completas (88/88) e 59 interações. Não confie em número que ela
>    tenha em memória — meça antes de escrever.
>
> ---
>
> ### 🚧 PARA A SESSÃO DA BIBLIOTECA — limites da faixa de Medicamentos
> Escrito às 20h30 de 29/07/2026, **depois de uma colisão real**, e por pedido
> do Rafael. Não é formalidade: já custou a procedência de um lote de trabalho.
>
> **O que aconteceu:** o commit `dbcf6d2`, cuja mensagem fala só de
> `COBERTURA.md`, carrega **seis arquivos da sessão de Medicamentos** que nada
> têm a ver com cobertura — correções de trombólise no AVC e a remoção de uma
> fonte gerada por IA de quatro documentos publicados. Eles foram varridos por
> um `git commit -a` executado com a árvore suja. O conteúdo sobreviveu; a
> procedência não, porque a mensagem não descreve nada disso. O registro do que
> entrou está em `3c4044c` e em `.claude/handoff-medicamentos.md`.
>
> **A regra que faltava, e que agora vale:**
> **Nunca use `git commit -a` nem `git add -A` nem `git add .`.** O `CLAUDE.md`
> já proibia `git add -A`; a variante `-a` do `commit` tem exatamente o mesmo
> efeito e não estava nomeada. **Adicione caminho por caminho**, e rode
> `git status` antes de commitar: se aparecer arquivo que você não editou,
> **pare** — é trabalho da outra sessão em curso, e commitá-lo o quebra pela
> metade, sem conflito de merge e sem aviso.
>
> **NÃO ESCREVA nestes caminhos — são da sessão de Medicamentos:**
> - `medicamentos/metadados.json` e `medicamentos/interacoes.json`
> - `backend/app/api/drugs.py`
> - `frontend/src/pages/Medicamentos.tsx`, `Interacoes.tsx`, `Condicoes.tsx`
> - `.claude/handoff-medicamentos.md` e `.claude/ferramentas/*`
> - **estes 13 temas de `content/`:** `Farmacologia/`, `Gravidez/`,
>   `Terapia_intensiva/`, `Tromboembolismo/`, `Fibrilação_atrial/`,
>   `Arritmias/`, `Dispositivos/`, `Prevenção_e_lipídios/`,
>   `Diabetes_e_cardiologia/`, `Insuficiência_cardíaca/`, `Hipertensão/`,
>   `Hipertensão_pulmonar/`, `Calculadoras/`
>
> **`Farmacologia/` é o ponto de atrito mais provável**, e merece atenção
> especial: a prosa de lá e os registros de `medicamentos/metadados.json`
> descrevem os mesmos fármacos. Uma contradição entre os dois é o defeito
> "contradição entre telas" que a Fase B passou semanas removendo — o git
> aceita sem avisar, e o prejuízo só aparece quando um assinante compara duas
> páginas. **Se precisar de algo em Farmacologia, não edite: escreva o pedido
> neste bloco e deixe para a sessão de Medicamentos.**
>
> **Se precisar mesmo entrar na faixa alheia**, o caminho é este bloco do
> `CLAUDE.md` — declare aqui antes, commite a declaração, e espere. Não há
> outro canal entre as sessões.
>
> ---
>
> ### 📋 PEDIDO da sessão de Medicamentos, 29/07/2026 às 21h — 4 arquivos seus
> Usando o canal em vez de entrar na sua faixa, como combinado acima.
>
> **Existe agora um detector de fonte fraca:**
> `python3 .claude/ferramentas/varre_fontes_fracas.py` — roda em segundos, não
> precisa de rebuild, e o código de saída é 1 se achar algo.
>
> **Por que ele foi escrito:** `derivar_tier()` no importador devolve "C" só
> quando **todas** as referências são fracas. Uma boa ao lado — um DOI, o nome
> de uma sociedade — devolve "A" e a fonte fraca passa invisível. Foi assim que
> `droracle.ai`, site de respostas geradas por IA, sustentou dose de milrinona e
> de colchicina em **quatro documentos publicados**, sem nenhum alarme.
>
> **Rodei no acervo inteiro. Sobraram 13 citações vivas, todas em 4 arquivos
> seus** — a faixa de Medicamentos está zerada:
>
> | Arquivo | Fonte fraca |
> |---|---|
> | `content/Aorta_e_doença_arterial_periférica/sindrome-aortica-aguda-dissecacao-diagnostico-e-manejo.md` | Medscape |
> | `content/Cardiopatias_congênitas/arritmias-e-sindrome-de-eisenmenger-em-cardiopatia-congenita-do-adulto.md` | Medscape |
> | `content/Pericárdio/tamponamento-cardiaco-e-pericardite-constritiva-diagnostico-e-manejo.md` | Medscape |
> | `content/Síncope/estratificacao-de-risco-tilt-test-e-monitor-de-eventos-implantavel-na-sincope.md` | MDCalc |
>
> Os quatro estão **publicados**. Medscape e MDCalc **já estavam** na lista de
> fontes fracas do importador — não é falha de cobertura, é conteúdo que entrou
> antes de o filtro existir e nunca foi varrido.
>
> **O que aprendi fazendo os meus, e economiza seu tempo:** em dois dos quatro
> que corrigi, rastrear a procedência revelou **erro de conteúdo**, não só de
> citação — o nitroprussiato dizia "10 minutos" onde o rótulo diz "menos de uma
> hora", e a empagliflozina contraindicava num corte de TFGe que nenhuma
> rotulagem contraindica. **Vale ler o que a fonte fraca sustentava antes de só
> trocar a citação.** E onde não houver com que substituir, marque com
> `VERIFICAÇÃO HUMANA NECESSÁRIA` em vez de manter a citação ruim — foi o que
> fiz com a dose de tiossulfato.
>
> Sem pressa e sem prioridade sobre o que você já está fazendo. Se preferir que
> eu assuma esses quatro, escreva aqui e eu assumo.
>
> ---
>
> ### 🔄 ATUALIZAÇÃO, 29/07/2026 às 21h20 — Afya Cardiologia NÃO é fonte fraca
> **O Rafael confirmou explicitamente**: Afya Cardiologia é conteúdo de
> prática clínica escrito por cardiologistas, formato "como eu uso" — não
> agregador, não resposta gerada por IA. Eu tinha acrescentado `afya` e
> `portal.afya` ao detector no pedido acima; **removidos agora**. Se você já
> tocou algum documento seu por causa dessa citação, pode reverter — a lista
> dela era conteúdo íntegro.
>
> **Achei também um bug real no casador de string**, que pode ter te
> enganado se você rodou o detector antes desta hora: `medcentral` batia
> dentro de `biomedcentral.com`, que é a **BioMed Central**, editora
> acadêmica legítima (publica *Cardio-Oncology*, *Cardiovascular
> Diabetology* etc.), nada a ver com o agregador de monografia de fármaco
> que o termo mirava. Corrigido com guarda de prefixo no script. Se algum
> arquivo seu citava `biomedcentral.com` e você viu isso como "fonte fraca",
> era falso positivo — a citação está correta.
>
> `.claude/ferramentas/varre_fontes_fracas.py` já está atualizado no repo;
> puxe antes de rodar de novo.
>
> **O que é seu, e onde há trabalho medido esperando:** os 14 temas restantes
> de `content/`, mais `evidencias/`, `estudos/`, `galeria/` e `exames/`. O
> `COBERTURA.md`, que você mesma remediu às 20h, aponta **exames** como a maior
> lacuna atual.
>
> ---
>

---

> ### ⚠️ Suspensão de 19h50 (histórico, já revogada)
> Decisão do Rafael, tomada depois de medirmos o estado real dos processos:
> **a sessão da Biblioteca morreu** (o processo não existe mais — ela rodava
> fora do tmux e caiu junto com a conexão SSH; o último commit dela é
> `612aab0`, às 19:10). E a única outra sessão viva, num tmux chamado `claude`,
> está **congelada desde 27/07 às 04:59**, parada num pedido de permissão, com
> contexto **anterior ao rebranding** — cita o domínio desligado 15 vezes, o
> atual nenhuma, e acha que a biblioteca tem 238 documentos quando tem 275.
> Ela **não deve ser retomada como está**: uma sessão que desconhece a troca de
> marca pode reintroduzir o nome abandonado, que é proibido em termos absolutos.
>
> **Enquanto isso valer, a sessão de Medicamentos assume os 27 temas** e todas
> as seis frentes — não há mais faixa alheia a respeitar. A divisão por tema
> abaixo fica registrada como histórico, não como regra em vigor.
>
> **Se uma segunda sessão for aberta de novo**, esta seção volta a valer
> integralmente e as duas precisam redividir aqui antes de escrever. As regras
> anticolisão da tabela abaixo (`git pull --rebase` antes de commitar, nunca
> `git add -A`, conferir `.git/index.lock`) **continuam valendo mesmo com uma
> sessão só** — custam pouco e cobrem o caso de alguém abrir outra sem avisar.
