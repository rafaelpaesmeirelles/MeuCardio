# ADR — CorvIA Mail unificado por proxy OAuth

**Status:** aceito em 06/08/2026.

## Contexto

O profissional precisa consultar e operar a caixa nativa CorvIA Mail e contas
Google/Microsoft em uma única interface, preservando a sincronização de agenda
e contatos já vinculada às mesmas identidades.

## Decisão

- A sessão própria do CorvIA Mail continua obrigatória para a central de e-mail.
- Google e Microsoft usam OAuth 2.0 com PKCE, estado de uso único, token cifrado
  no servidor e consentimento explícito para calendário, contatos e e-mail.
- O CorvIA consulta e altera mensagens diretamente nas APIs oficiais. Corpos e
  anexos externos não são copiados para o banco local.
- Cada integração é autorizada pelo `owner_id` da caixa CorvIA; o identificador
  recebido do navegador nunca basta para acessar uma conta de outro titular.
- Conexões antigas precisam de reconexão para receber os novos escopos. Não há
  ampliação silenciosa de privilégio.
- A caixa Apple não é anunciada como e-mail unificado enquanto não houver um
  conector homologado com equivalência funcional e controles de segurança.

## Consequências

O desenho reduz duplicação e retenção de dados, mantém ações refletidas no
provedor original e preserva revogação centralizada. Em contrapartida, a caixa
externa depende da disponibilidade do provedor e algumas funções específicas,
como anexos e sinalizadores não equivalentes, exigem implementação validada por
provedor antes de serem liberadas.
