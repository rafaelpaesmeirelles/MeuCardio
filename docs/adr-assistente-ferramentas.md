# ADR — Ferramentas do assistente de IA sobre Agenda e CorvIA Mail

**Status:** implementado em código nesta branch (`agent/claude-continuacao-corvia`),
**não validado em produção real** — depende de `AI_ASSISTANT_TOOLS_ENABLED=true`
no servidor e de consentimento individual de cada médico. Ver seção "O que
ainda falta" antes de anunciar como funcional.

## Contexto

O assistente clínico (`app/services/rag.py`, `app/services/ia/provedor.py`)
até aqui só produzia texto — respondia com base no corpus institucional,
PubMed e busca na internet, sem agir sobre dado real do médico. Pedido do
proprietário: o assistente deve poder consultar e operar a Agenda Integrada
do próprio médico (ver e criar/reagendar/cancelar compromisso, saber o
próximo local de trabalho e o trânsito até lá) e ler a caixa do CorvIA Mail
do próprio médico — sempre a própria conta autenticada, nunca a de outra
pessoa.

## Decisão

- **Function-calling nativo da Anthropic** (`tool_use`/`tool_result`), não um
  parser de intenção à parte. `ProvedorAnthropic.responder`/`responder_stream`
  ganharam os parâmetros `ferramentas` (schemas) e `executor_ferramenta`
  (callback síncrono `(nome, argumentos) -> dict`), com um teto de
  `_MAX_RODADAS_TOOL_USE = 6` rodadas por resposta — nunca encadeamento
  indefinido. `ProvedorOpenAI` aceita os mesmos parâmetros por paridade de
  interface e os ignora (mesmo padrão já usado para `usar_internet`).
- **Duas travas independentes, as duas precisam estar de acordo** antes de
  uma pergunta sequer *oferecer* as tools ao modelo
  (`rag._ferramentas_para`):
  1. `settings.ai_assistant_tools_enabled` — decisão de instalação/administrador,
     desligada por padrão;
  2. `users.ia_ferramentas_consent_em` não nulo — consentimento individual do
     médico, concedido/revogado por `PUT /api/ai/ferramentas/consentimento`,
     efetivo na próxima pergunta (não precisa esperar a conversa atual
     terminar). Mesmo padrão de `MobilityPreference`/`MOBILITY_CONSENT_VERSION`
     já usado na Agenda Integrada.
- **As tools reaproveitam exatamente as mesmas funções de rota** que a tela
  usa (`app/api/agenda_integrada.py`, chamadas como funções Python normais
  com `db`/`user` explícitos) e os mesmos serviços de e-mail
  (`app/services/mail360.py`, `app/services/external_mail.py`, via
  `app/services/ia/mail_tools.py`). Não existe caminho de escrita paralelo:
  a mesma validação, resolução de dono, cálculo de conflito de horário,
  fila de sincronização externa e `AuditLog` que a tela aciona são os que o
  assistente aciona.
- **Escopo sempre implícito no usuário autenticado.** Nenhuma tool aceita um
  parâmetro de "de quem" — não há como o modelo pedir a agenda ou o e-mail
  de outra pessoa através destas ferramentas.
- **Mail: só leitura nesta primeira versão** (`mail_resumo_caixa`,
  `mail_listar_pastas`, `mail_listar_mensagens`, `mail_ler_mensagem`).
  Enviar, responder ou excluir e-mail por iniciativa do assistente fica para
  uma decisão e uma ADR à parte — é o tipo de ação (comunicação em nome do
  médico) que pede revisão humana adicional antes de existir.
- **Agenda: leitura e escrita local** (`agenda_listar_compromissos`,
  `agenda_plano_do_dia`, `agenda_proximo_deslocamento`,
  `agenda_criar_compromisso`, `agenda_reagendar_compromisso`,
  `agenda_cancelar_compromisso`). Escrita nunca envia e-mail ao paciente a
  partir do assistente (o parâmetro `patient_email`/`email_consent` não é
  exposto às tools) e nunca contorna a fila de sincronização externa — se o
  compromisso pertence a uma integração `external_authoritative`, a própria
  função de rota já recusa com 409, herdado sem reimplementação.
- **Deslocamento nunca inventa rota.** Sem coordenadas de origem, ou sem
  `MobilityPreference.enabled=True` (consentimento de localização já
  existente na Agenda), a tool devolve só o próximo local, com o motivo
  explícito — nunca fabrica distância, trânsito ou tempo de percurso.
- **Toda tool devolve erro tratado, nunca deixa exceção subir** para dentro
  do loop de tool-calling (`{"erro": "<código>", "mensagem": "..."}"`).
  Falha de provedor externo (trânsito, Mail360, Gmail/Outlook) é
  indisponibilidade honesta, igual ao resto do produto.
- **Auditoria:** toda tool de escrita (`agenda_criar/reagendar/cancelar_compromisso`)
  grava `AuditLog` com ação `ia_tool_<nome>` e argumentos não sensíveis
  (nunca corpo de e-mail, nunca coordenada de origem). Tools de leitura não
  geram uma linha de auditoria por chamada — gerariam ruído sem valor
  (a leitura de uma mensagem específica já é auditada dentro de
  `mail_tools.py`, no nível de acesso a conteúdo).

## Prompt do sistema

`PROMPT_FERRAMENTAS` (`app/services/rag.py`) só é anexado ao prompt quando as
duas travas acima liberam a pergunta — sem isso, a API teria a tool
disponível e o modelo não saberia que deve usá-la por conta própria (mesmo
problema já resolvido antes aqui para a `web_search`, registrado no histórico
do projeto). Regras explícitas no prompt: nunca criar/reagendar/cancelar sem
o médico ter pedido nesta conversa; confirmar antes de agir só quando os
dados estiverem ambíguos; nunca inventar resultado de ferramenta que falhou;
resumir e-mail longo em vez de citá-lo por inteiro; não usar aqui os
marcadores clínicos `[F#]`/`[PM#]`/`[W#]`.

## O que ainda falta (não fazer sem isto)

- **Smoke real com credencial de homologação** — nada aqui foi exercitado
  contra a Anthropic de verdade nem contra Mail360/Google/Microsoft reais
  nesta sessão; só testes automatizados com dublê de cliente. Ver P0.3/P0.5
  do handoff de produção.
- **Interface do frontend** para o convite/aceite ao consentimento
  (hoje só a rota `PUT /api/ai/ferramentas/consentimento` existe; nenhuma
  tela chama).
- **Envio/resposta/exclusão de e-mail por IA** — decisão e ADR à parte,
  fora do escopo desta.
- **Delegação** (`professional_id` de outro profissional) — deliberadamente
  fora de alcance das tools nesta versão; segue sendo decisão humana feita
  pela tela.
- **`AI_ASSISTANT_TOOLS_ENABLED` não está listada ainda no `.env.example`**
  — mesma lacuna de paridade já registrada no handoff para as flags de
  Agenda; corrigir no mesmo PR que fechar essa pendência.
