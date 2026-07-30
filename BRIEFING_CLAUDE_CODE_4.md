# Briefing de implementação — Corvia (parte 4: Caixa de e-mail do assinante)

Continuação dos briefings anteriores. Regras transversais de sempre continuam valendo.

Numeração continua a partir da Tarefa 27 (receituário).

---

## 28. Caixa de e-mail para o assinante, incluída na assinatura

Nova funcionalidade: cada assinante ganha uma caixa de e-mail própria, acessível dentro da própria plataforma Corvia, incluída no valor da assinatura.

### A decisão que vem antes de qualquer código: hospedar ou integrar

**Não decida isso sozinho — apresente as duas opções com prós e contras medidos, para eu decidir.**

**Opção A — servidor de e-mail próprio (self-hosted), no mesmo servidor ou em outro dedicado.**
- Vantagem: controle total, sem depender de terceiro, sem custo por caixa.
- Risco real, não teórico: um domínio novo enviando e-mail de servidor pequeno tem alta chance de cair em spam nos provedores grandes (Gmail, Outlook), até construir reputação de envio — isso leva meses, não é configuração de um dia. Exige SPF, DKIM, DMARC corretamente configurados desde o primeiro envio, e mesmo assim não garante entrega.
- Exige manutenção contínua de segurança (é um serviço exposto à internet, alvo comum de ataque) — trabalho operacional recorrente, não uma tarefa que termina.

**Opção B — integrar com provedor de hospedagem de e-mail já estabelecido**, oferecendo a caixa por baixo de um provedor com reputação de envio já construída (existem provedores voltados a caixas de e-mail para SaaS/revenda, com API própria para provisionar conta por assinante).
- Vantagem: entrega confiável desde o primeiro dia, sem o problema de reputação de domínio novo.
- Desvantagem: custo recorrente por caixa (ainda que pequeno), e dependência de um fornecedor externo.

**Pesquise fornecedores atuais de hospedagem de e-mail com API para provisionamento por usuário (modelo de revenda/SaaS) antes de apresentar a opção B com nomes e preços reais — não presuma um fornecedor específico sem confirmar.**

### Pergunta que também depende de mim, não decida sozinho

O propósito principal dessa caixa é comunicação profissional geral (agenda, contato com paciente sobre assunto administrativo, recebimento de coisas do próprio sistema Corvia), ou pode incluir troca de informação clínica sobre paciente especificamente? A resposta muda o nível de exigência de segurança:
- Se puder conter dado de saúde de paciente (mesmo que o médico decida usar assim, sem a plataforma controlar o conteúdo), a caixa precisa ser tratada com o mesmo padrão de proteção já usado no cofre do telediagnóstico — cifragem em repouso, log de acesso, retenção definida.
- Se for de uso estritamente profissional/administrativo, o nível de exigência é mais próximo do de um provedor de e-mail comum.

Registre essa pergunta no plano antes de definir o modelo de dado ou a política de retenção.

### O que fica claro desde já, independente da opção escolhida

- O endereço de e-mail do assinante deve usar o domínio da Corvia (ex.: `nome@corvia.med.br` ou subdomínio equivalente) — não é uma caixa de provedor externo com marca de outra empresa.
- Acesso à caixa é só de dentro da plataforma (webmail integrado), refletindo o mesmo login e sessão do resto do sistema — não exige senha separada.
- A caixa é benefício incluído na assinatura — sem cobrança adicional por si só, mas o custo real do provedor escolhido (se houver, na Opção B) deve ser levado em conta na sustentabilidade financeira da assinatura de R$20/mês, não apresentado como se não tivesse custo.

---

Apresente as duas opções (A e B), com a pesquisa de fornecedores reais para a B, e a resposta à pergunta sobre conteúdo clínico, antes de qualquer código de modelo de dados ou interface.

---

## Análise entregue em 30/07/2026 — sem nenhum código escrito, conforme pedido

### Achado que muda o quadro antes de qualquer comparação: **Amazon WorkMail está fora**

Verificado direto na documentação oficial da AWS (não por busca agregada):
`https://docs.aws.amazon.com/workmail/latest/adminguide/workmail-end-of-support.html`

> "Amazon WorkMail will no longer accept new customers beginning April 30, 2026. [...] After March 31, 2027, you will no longer be able to use Amazon WorkMail."

A AWS encerrou o cadastro de clientes novos em 30/04/2026 e desliga o serviço por completo em 31/03/2027. Como hoje já passamos da primeira data, a Corvia **não conseguiria nem abrir conta** — WorkMail sai da comparação por completo, independentemente de preço ou API.

### Opção A — servidor de e-mail próprio, revisitada com nomes reais

Os riscos que o briefing já apontava (reputação de domínio novo, SPF/DKIM/DMARC, manutenção de segurança contínua) se confirmam. Acrescento dois pontos medidos nesta sessão:

- **A Corvia hoje não tem nenhuma infraestrutura de e-mail própria.** O `docker-compose.prod.yml` e o `Caddyfile` não têm Postfix/Dovecot nem nada equivalente — o único uso de e-mail hoje é um relay SMTP de saída, opcional, configurado em `backend/app/core/config.py` (`smtp_host`/`smtp_user`/`smtp_password`), usado só para transacional (reset de senha, notificação). Ou seja: Opção A parte do zero, sem experiência operacional prévia da equipe rodando esse tipo de serviço — o risco de reputação e o ônus de manutenção do briefing não são teóricos, são o ponto de partida real.
- **Se a Opção A for escolhida**, os dois candidatos técnicos atuais mais indicados (pesquisados agora, não por memória) são:
  - **Stalwart Mail Server** — servidor moderno (Rust), multi-tenant nativo (múltiplos domínios/inquilinos com quota e branding próprios), leve (~100MB RAM), considerado pela comunidade a opção recomendada para implantações novas em 2026.
  - **Mailcow** — suíte Docker mais madura e testada (Postfix + Dovecot + Rspamd + SOGo/webmail), com API REST própria para criar domain admins e caixas programaticamente. O webmail SOGo tem mecanismo de "Proxy Auth" que evita duplo login, mas **não confirmei se aceita ser embutido via iframe dentro da própria Corvia** — SOGo tradicionalmente resiste a isso por cabeçalho de segurança (`X-Frame-Options`), precisaria validação técnica antes de assumir que funciona.
  - Qualquer um dos dois: a Corvia assume inteiramente entrega, reputação de IP, SPF/DKIM/DMARC, anti-spam e disponibilidade — é o mesmo ônus operacional do briefing, com nomes concretos de ferramenta.

### Opção B — fornecedores reais pesquisados, com fonte para cada afirmação

| Fornecedor | API de provisionamento | Multi-domínio/revenda | Preço | Webmail embutível confirmado | Alerta |
|---|---|---|---|---|---|
| **Migadu** | Sim, REST documentada (`migadu.com/api/`) | Sim, ilimitado | Sem preço por caixa — plano fixo por armazenamento total: US$9 a 99/mês | Não encontrado (nem SSO nem iframe documentado) | Termos de uso quanto a revenda a terceiros não verificados |
| **Zoho Mail360** | Sim, API própria pensada para "e-mail dentro do seu app" | Sim | Grátis até 10 caixas; pago por faixa, **valor exato não divulgado publicamente** | Não encontrado | É o produto certo da Zoho para este caso, mas preço opaco sem contato comercial |
| **Amazon WorkMail** | — | — | — | — | **Descartado — sem novos clientes desde 30/04/2026** |
| **Forward Email** | Parcial (alias + IMAP, não "criar caixa" como conceito único) | Sim, domínios ilimitados em todos os planos | US$3–9/mês | Webmail open-source existe, embed não confirmado | **Termos de uso proíbem uso por terceiros fora do plano Enterprise (US$250/mês)** — nas próprias palavras do contrato: *"You will not use our service to operate a service which allow third parties [...] to access, use, or benefit from our service"*. O modelo "cada assinante ganha uma caixa" **não é lícito no plano barato** |
| **Rackspace Email** | Só via módulo WHMCS, sem API REST própria documentada | Sim, programa formal de revenda ("Email Reseller Program", white-label) | Não publicado para revenda; **no varejo, subiu de US$2,99 para US$10/caixa/mês entre nov/2025 e jan/2026 (+235%, casos relatados de até +706%)** | Divulgam customização visual completa, mas não confirmei se é skin ou embed de fato | Histórico recente de reajuste abrupto — sinal de alerta para dependência de longo prazo |
| **OpenSRS (Tucows)** | Sim, API dedicada a automação de provisionamento | Sim — é literalmente uma plataforma de revenda desde a origem | US$1,00 (10GB) a US$7,50 (75GB)/mês, +US$0,50 a cada 5GB adicional | Confirmado webmail em subdomínio com marca própria (`webmail.suamarca.com`); **embed via iframe dentro da própria Corvia não confirmado**, só subdomínio | Provavelmente o mais alinhado ao pedido do ponto de vista comercial (nasceu para isso) |
| **Titan Email** | Sim — `POST /partner/createMailOrder` cria domínio + caixa numa chamada | Sim, é o motor por trás de GoDaddy/Namecheap via revenda | Não divulgado publicamente, negociado por parceiro | **O único com SSO/embed tecnicamente confirmado**: token de auto-login de curto prazo (`webmailAutoLoginToken`) e painel administrativo embutível via iframe com JWT | Acesso via onboarding com contato direto, não self-service |

**Nenhum dos sete confirma suporte em português nem localização de dados no Brasil.** Para LGPD, qualquer um exigiria avaliação de transferência internacional de dados com o jurídico — ainda mais relevante se a resposta à pergunta clínica abaixo for "sim, pode conter dado de saúde".

**Minha leitura, não uma decisão feita por mim:** Titan Email é o único com o mecanismo de webmail embutido que o briefing pede ("acesso só de dentro da plataforma, mesmo login") já documentado e testável hoje; OpenSRS parece o modelo comercial mais alinhado (nasceu para revenda) mas sem embed confirmado, só subdomínio com marca; Migadu é o mais simples e barato mas sem embed nem ToS de revenda esclarecidos; Forward Email tem uma armadilha contratual real que descartaria os planos baratos.

### Decisões do Rafael, em 30/07/2026

1. **Escopo de conteúdo: só administrativo/geral.** A caixa não se destina a troca de
   informação clínica sobre paciente — nível de exigência de segurança mais próximo
   de um provedor de e-mail comum, sem o padrão do Cofre do telediagnóstico
   (cifragem em repouso específica, log de acesso, retenção definida). Se essa
   premissa mudar no futuro (médico começar a usar a caixa para falar de paciente
   na prática, ainda que fora do que a plataforma pretende), a decisão de segurança
   precisa ser revisitada — não presumir que "administrativo no papel" continua
   "administrativo na prática" para sempre.
2. **Opção B — fornecedor terceiro**, não self-hosted. Motivo, nas palavras do
   próprio Rafael ao escolher: entrega confiável desde o primeiro dia pesa mais que
   controle total, dado que a Corvia não tem hoje nenhuma experiência operacional
   rodando servidor de e-mail.
3. **Fornecedor para aprofundar: Titan Email**, por ser o único dos sete
   pesquisados com SSO/embed de webmail tecnicamente confirmado — o requisito do
   briefing de "acesso só de dentro da plataforma, mesmo login" depende
   diretamente disso.

### Pesquisa aprofundada da Titan Email, 30/07/2026 — achado que muda a recomendação anterior

**Ressalva de método:** a documentação de `apidocs.titan.email` é renderizada via
JS/Apiary; não consegui abrir o HTML bruto, só uma leitura resumida por
ferramenta de fetch. É a melhor fonte disponível nesta sessão, mas é fonte
única, sem segunda leitura independente do texto verbatim — trato como
confiança moderada, não como citação garantida.

**Onboarding não é self-service.** Não existe "criar conta → pegar API key →
começar a chamar". O caminho público é `titan.email/partners` → formulário de
contato → aprovação comercial humana, que só então libera API URL, Partner ID
e API Secret Key. Não há um "Titan Email Reseller Program" com portal de
developer/sandbox aberto. Não encontrado: prazo de resposta, critério de
elegibilidade ou volume mínimo exigido.

**Endpoints confirmados além de `createMailOrder`:** existe, sim, criação de
caixa individual dentro de domínio já existente (`createEmailAccount`), além
de suspender/deletar/trocar senha (`suspendEmailAccount`, `deleteEmailAccount`,
`changeEmailAccountPassword`) — a API é mais completa do que a pesquisa
inicial sugeria.

**O ponto que muda tudo — mecanismo de SSO/embed, examinado em detalhe:**

- `webmailAutoLoginToken` **só é emitido no momento da criação da caixa**,
  como parte da resposta do `createEmailAccount` — não é um endpoint que se
  chama de novo a cada acesso. A própria documentação diz que o token **não
  deve ser persistido e não pode ser reutilizado depois** para logar de novo.
  TTL exato não encontrado, mas é descrito como de uso imediato e único.
  Quando usado, leva à caixa de entrada real em `app.titan.email` — isso é
  positivo, é o webmail de verdade, não um painel.
- O iframe `cpWidget` (`manage.titan.email/partner/cpWidget`), esse sim
  reemitível quantas vezes o parceiro quiser (JWT assinado pelo próprio
  backend do parceiro) — mas os valores documentados de `section` são todos
  administrativos (`home`, `email-accounts`, `billing-and-subscription`,
  `domain-verification` etc.). **Nenhum mostra a caixa de entrada do usuário
  final.** É um painel de administração de conta, não o cliente de e-mail.

**Conclusão prática:** dá para embutir um painel de *administração* de
contas via iframe, reemitível. Dá para mandar o usuário ao webmail real, mas
só **uma vez**, no instante em que a caixa é criada, com token de uso único.
**Não há confirmação, na documentação pública, de que dá para embutir o
webmail (a caixa de entrada) dentro da Corvia com SSO recorrente a cada
sessão** — que é exatamente o requisito central do briefing ("acesso só de
dentro da plataforma, mesmo login, toda vez que entra"). Isso precisaria ser
esclarecido diretamente com o time comercial/técnico da Titan, pelo mesmo
formulário de parceria que é o único canal de onboarding — **antes de
qualquer decisão de seguir com esse fornecedor**, porque a documentação
pública não sustenta esse fluxo.

**Preço:** não há tabela pública do valor de atacado (o que a Titan cobraria
da Corvia) — só o preço final ao consumidor que cada revendedor pratica
(US$1,49-7,99/caixa/mês conforme o revendedor). Modelo de negócio é B2B2C via
grandes distribuidores (GoDaddy — que fechou parceria em 2025 mirando
justamente o Brasil como mercado emergente —, Automattic/WordPress.com,
Hostinger, HostGator Brasil, Name.com). Isso é inferência, não regra
publicada, mas o padrão de parceiros é de grandes distribuidores com volume
agregado — uma operação nova e pequena como a Corvia pode não ser o perfil
que a Titan prioriza; só o contato comercial esclarece isso.

**Red flags apuradas:** a empresa em si parece financeiramente sólida
(fundada em 2018 por Bhavin Turakhia, aporte Série A de US$30 milhões liderado
pela Automattic em 2021, avaliação de US$300 milhões) — não tem o perfil do
susto de preço da Rackspace. Mas o Trustpilot mostra nota ~4,0/5 com 380
avaliações e **21% de 1 estrela**, com reclamações recorrentes de filtro de
spam que não dá para desligar, suporte difícil de alcançar, e um caso relatado
de corte imediato de acesso IMAP ao trocar MX, sem aviso, deixando histórico
de e-mail de 18 funcionários inacessível durante migração.

**Síntese parcial (antes de aprofundar os outros dois):** a recomendação
anterior de Titan Email como melhor opção de embed foi baseada numa primeira
leitura da documentação, que sugeria SSO/iframe funcionando de forma
genérica. A leitura mais profunda mostra que o mecanismo documentado
publicamente **não cobre o caso de uso central que a Corvia precisa**
(webmail embutido, SSO recorrente).

### Pesquisa aprofundada de OpenSRS e Zoho Mail360, 30/07/2026 — o mesmo problema se repete, de duas formas diferentes

**Achado central: nenhum dos três candidatos investigados (Titan, OpenSRS,
Zoho Mail360) confirma, com garantia documentada do próprio fornecedor, um
SSO recorrente para uma caixa de entrada pronta.** Cada um falha nisso de um
jeito diferente:

**OpenSRS** — a API de e-mail (`email.opensrs.guide`) tem três tipos de
token: `oma` (só painel admin), `sso` (webmail/IMAP/SMTP, mas **de uso
único**, mesmo defeito da Titan) e `session` (reutilizável durante sua
validade, 1-24h configurável). O `session` token **tecnicamente permitiria**
SSO recorrente — bastaria a Corvia chamar a API a cada login do assinante e
gerar um token novo de curta duração —, mas a própria documentação da OpenSRS
descreve esse token como ferramenta de **suporte técnico/diagnóstico**
("permitir que a equipe de suporte entre nas caixas de usuários finais sem
saber a senha, para diagnosticar problemas"), nunca como mecanismo de login
de produto para usuário final. Usá-lo para esse fim funcionaria na prática,
mas sem garantia contratual do fornecedor de que esse uso é suportado ou
continuará funcionando. Além disso, o webmail em si é servido por
**subdomínio real** (ex.: `webmail.corvia.med.br` com CNAME + certificado
próprio) — não há confirmação de que aceita ser embutido via iframe dentro
da aplicação da Corvia (nenhuma menção a `X-Frame-Options`/CSP na
documentação, o que significa que teria que ser testado na prática, não
presumido).
Onboarding: self-service, mas com depósito mínimo de US$95.
Red flag relevante: **Trustpilot com TrustScore 1,5/5** (20 avaliações),
reclamações recorrentes de queda de serviço, suporte ruim e blocklist
"amadora" bloqueando e-mail de grandes provedores — risco real para uma
plataforma que promete e-mail confiável a médicos.
Fonte: https://email.opensrs.guide/docs/generate_token ,
https://support.opensrs.com/support/solutions/articles/201000063536 ,
https://support.opensrs.com/support/solutions/articles/201000063116 ,
https://www.trustpilot.com/review/opensrs.com

**Zoho Mail360** — achado mais importante: **não é um produto de webmail,
é uma API de dados pura** (contas, mensagens, pastas, labels, rascunhos,
anexos, threads via OAuth). Não existe UI de webmail fornecida pela Zoho para
embutir, logo **a pergunta "existe SSO para a caixa de entrada deles" não se
aplica** — não há caixa de entrada deles. Isso muda a natureza da escolha:
se for este o caminho, a Corvia **constrói o webmail inteiro do zero** (lista
de mensagens, leitor, composição, pastas, anexos) por cima da API REST do
Mail360, e a autenticação do usuário final nunca sai da própria sessão já
existente da Corvia — o backend guarda as credenciais OAuth do Mail360 e
nunca expõe login a um sistema externo. Isso elimina estruturalmente o
problema de SSO (não há segundo sistema de login para sincronizar), ao custo
de mais trabalho de engenharia (não tem nada pronto de interface).
Onboarding: self-service, com free tier de até 10 caixas.
Preço das faixas pagas: **não encontrado** valor numérico público, mesmo em
fontes de terceiros.
Data center: nenhum no Brasil (EUA/UE/Índia/Austrália/Japão/Canadá/Arábia
Saudita); GDPR compliance confirmada para o Zoho Mail geral, **nenhuma
declaração específica de LGPD ou de conformidade do Mail360 em particular**
— precisaria ser levantado formalmente com o comercial antes de fechar,
principalmente porque dado de assinante brasileiro trafegaria por servidor
fora do país.
Fonte: https://www.zoho.com/mail360/help/introduction-to-mail360.html ,
https://www.zoho.com/mail360/help/api-in-mail360.html ,
https://www.zoho.com/mail360/help/api/oauth.html ,
https://www.zoho.com/mail360/pricing.html

### Quadro comparativo final

| | Titan | OpenSRS | Zoho Mail360 |
|---|---|---|---|
| SSO recorrente p/ webmail pronto | Não confirmado (token único, só na criação) | Não confirmado como caso de uso oficial (token `sso` de uso único; `session` reutilizável mas documentado como suporte técnico, não login de produto) | Não se aplica — não há webmail deles; a Corvia constrói a UI e controla a própria sessão |
| Webmail embutível via iframe | Só painel admin, não a caixa de entrada | Subdomínio real, embed/CORS não confirmado | N/A (sem UI própria) |
| Onboarding | Contato comercial, sem self-service | Self-service, depósito mínimo US$95 | Self-service, free tier até 10 caixas |
| Maior risco | Requisito central não confirmado | Instabilidade/suporte (Trustpilot 1,5/5) | Mais trabalho de engenharia; preço opaco; sem LGPD declarada |

### Síntese final e os dois caminhos tecnicamente realistas

**Nenhum dos três fornecedores garante, em documentação pública, o requisito
exato do briefing** ("webmail embutido, mesmo login, toda vez que o
assinante entra"). Restam dois caminhos tecnicamente viáveis, com trade-offs
diferentes:

1. **Usar o `session token` da OpenSRS como SSO de fato** — funciona na
   prática (gerar um token novo a cada login da Corvia), é o caminho de
   menor esforço de engenharia, mas depende de um uso não documentado
   oficialmente para esse fim, com um fornecedor que tem histórico de
   reclamação de instabilidade.
2. **Construir o webmail próprio sobre a API de dados do Zoho Mail360** —
   elimina de vez a pergunta de SSO externo (nunca existe login de terceiro
   para sincronizar), mas exige construir toda a interface de webmail do
   zero, e o preço de produção ainda não está confirmado.

Isso é uma decisão de arquitetura, não só de fornecedor — vale ser decidida
por você antes de qualquer código de modelo de dados ou interface.

### Decisão do Rafael, em 30/07/2026

**Zoho Mail360 + webmail próprio.** A Corvia constrói a interface de webmail
inteira (lista de mensagens, leitor, composição, pastas, anexos) por cima da
API de dados do Mail360, e a autenticação do assinante nunca sai da sessão já
existente da Corvia — o backend guarda as credenciais OAuth do Mail360 e
nunca expõe login a um sistema externo. Isso elimina estruturalmente o
problema de SSO recorrente que nenhum dos três fornecedores garantia.

**Duas pendências que ficam explícitas antes de comprometer arquitetura em
produção, e que dependem de contato comercial que esta sessão não pode
fazer:**
1. **Preço de produção não confirmado.** A pesquisa não encontrou valor
   numérico público para as faixas pagas do Mail360 (11-50, 51-1000, 5000+
   caixas) — só o free tier de até 10 caixas está confirmado. O briefing
   original exige que o custo real seja levado em conta na sustentabilidade
   da assinatura de R$20/mês, não escondido — isso só se resolve com contato
   comercial da Zoho, que precisa ser feito por fora desta sessão.
2. **LGPD/localização de dados — resolvido por decisão do Rafael, não por
   declaração formal da Zoho.** Ele optou por não exigir declaração
   específica de LGPD do fornecedor, com base em dois pontos: nenhuma
   informação confidencial de paciente será arquivada ali, e o uso é
   estritamente pessoal/administrativo do médico. Registrei a ressalva
   técnica antes de aceitar isso de bandeja: mesmo em uso administrativo, (a)
   o e-mail do próprio médico já é dado pessoal sob a LGPD, e a transferência
   internacional (Zoho sem datacenter no Brasil) tem exigência própria no
   art. 33 mesmo para dado não-sensível; e (b) "uso administrativo" é a
   intenção do produto, não garantia de conteúdo — nada impede um médico de
   mencionar nome ou CPF de paciente numa mensagem administrativa.
   **Decisão final do Rafael, diante disso: não bloquear o lançamento
   esperando declaração formal da Zoho, e em vez disso colocar uma ressalva
   visível na própria interface.** Implementada em
   `frontend/src/pages/CaixaDeEmail.tsx` (componente `RessalvaClinica`):
   aparece tanto na tela de ativação quanto na caixa já ativa, avisando que
   o e-mail não tem o padrão de cifragem do Cofre e que não deve receber
   nome/CPF de paciente junto de informação clínica. Não é dispensável nem
   mostrada só uma vez — permanece visível toda vez que o médico abre a
   página. **Isto não substitui uma eventual revisão jurídica do TCLE/termos
   de uso já registrada como pendência no `BRIEFING_CLAUDE_CODE_2.md`** — é
   uma mitigação de produto, não uma opinião jurídica.

### Esboço técnico entregue em 30/07/2026, a pedido do Rafael ("já comece a esboçar")

Com a decisão de arquitetura já tomada, o Rafael pediu para começar o desenho
técnico em paralelo à confirmação comercial das duas pendências acima — não
esperar por elas para começar a esboçar. O que foi construído:

- **`backend/app/models/email_account.py`** — tabela `email_accounts`
  (user_id único, email_address, mail360_account_key, status). Não guarda
  mensagem nenhuma: a caixa vive inteiramente no Mail360, esta tabela só
  mapeia usuário da Corvia → conta no Mail360.
- **Migração `4ee4b695fa49_caixa_de_email_do_assinante.py`**, idempotente,
  encadeada a partir do head real do banco (`f1c93d47b8e2`).
- **`backend/app/core/config.py`** — `mail360_client_id`/`_secret`/
  `_refresh_token`/`_dominio`, com `mail360_configurado` no mesmo padrão do
  `smtp_configurado`: em branco, o recurso fica indisponível (503), nunca
  simulado.
- **`backend/app/services/mail360.py`** — cliente da API do Mail360 (troca de
  refresh_token por access_token, criação de conta nativa, listar
  pastas/mensagens, obter mensagem, enviar, excluir). Endpoints e formato de
  autenticação (`Authorization: Zoho-oauthtoken`, base
  `https://mail360.zoho.com/api`) confirmados na documentação pública durante
  a pesquisa — **mas sem conta de parceiro ativa para testar de verdade**.
  Dois pontos marcados no próprio código como pendentes de confirmação contra
  uma chamada real: o nome exato do campo que devolve a account_key na
  criação da conta, e o formato exato da resposta de mensagens (a
  documentação pública não detalha o corpo da resposta, só os endpoints).
- **`backend/app/api/email.py`** — rotas em `/api/email` (`conta`, `pastas`,
  `mensagens`), registradas em `ROUTERS_ASSINANTES` no `main.py` (exige
  assinatura ativa, mesmo padrão do resto do sistema). Provisionamento é
  **sob demanda**, não automático no cadastro: o médico ativa quando quiser,
  decisão deliberada para não gerar custo por caixa que ninguém usaria
  enquanto o preço de produção não está confirmado. Endereço gerado a partir
  do nome (`rafael.paes@corvia.med.br`), com desambiguação por número em
  caso de colisão.
- **`frontend/src/pages/CaixaDeEmail.tsx`** — webmail próprio: tela de
  ativação quando a caixa ainda não existe, e depois pastas + lista de
  mensagens + leitor + composição, tudo dentro da própria Corvia, sem
  segundo login. Rota `/caixa-de-email` e item de menu "Caixa de e-mail"
  registrados em `App.tsx`/`Shell.tsx`.
- **Validado nesta sessão**: `python3 -m py_compile` em todos os arquivos
  Python novos: sem erro. Import real do `app.main` com as dependências
  instaladas localmente (sem banco de verdade, só validando que o grafo de
  imports monta): as 7 rotas de `/api/email/*` aparecem registradas
  corretamente. `npx tsc -b --noEmit` e `npm run build` no frontend: sem
  erro, build completo gerado. **Não testado**: nenhuma chamada real à API do
  Mail360 (não há credencial), nem o fluxo fim a fim num navegador.

**O que ainda falta, e por que não foi além disso nesta sessão:**
1. Confirmar as duas pendências comerciais (preço de produção, LGPD/
   localização de dados) com a Zoho — meu preencher `.env` com credencial de
   teste não substitui essa confirmação.
2. Quando houver credencial real, testar as chamadas de verdade e corrigir
   os dois pontos marcados como não confirmados no `mail360.py` (nome do
   campo da account_key, formato da resposta de mensagens).
3. Migração ainda não foi rodada em produção — como sempre, migração vem
   antes do rebuild, e rebuild pede confirmação antes.
4. Nenhum teste automatizado foi escrito para as rotas novas.

---

## Reinício em 30/07/2026 — CorvIA Mail vira add-on cobrado à parte

Pedido do Rafael: "reinicie o trabalho e prepare toda sessão email para ser
publicado". Duas decisões novas, que mudam o desenho acima:

1. **E-mail deixa de ser incluído na assinatura principal.** Passa a ser um
   serviço cobrado à parte, com preço a definir — "deixe o valor em branco
   por enquanto".
2. **A caixa ganha tela de login própria**, com três opções: entrar, esqueci
   a senha (com recuperação e troca) e assine o CorvIA Mail — mais uma
   página nova ("site") para assinar o serviço.

Perguntas de esclarecimento ficaram sem resposta duas vezes (a primeira
pergunta foi interrompida pelo próprio Rafael, a segunda ele confirmou não
ter respondido e pediu para refazer); refeitas uma terceira vez, essas
foram as respostas:

| Pergunta | Decisão do Rafael |
|---|---|
| Quem pode assinar? | Só quem já tem conta aprovada na Corvia — mesmo modelo de add-on dos cursos parceiros, não um cadastro novo tipo telediagnóstico |
| Onde vive o "site" de assinatura? | Nova página dentro do app atual (mesma SPA), não subdomínio separado |
| Senha da caixa: mesmo login de sempre ou senha própria? | **Senha própria** — inverteu a decisão anterior desta mesma sessão (que evitava segundo login de propósito) |

A terceira resposta é a que mais mexeu na arquitetura: a Tarefa 28 tinha sido
desenhada explicitamente para NUNCA precisar de um segundo login (foi por
isso que Zoho Mail360 + webmail próprio venceu OpenSRS/Titan). Com senha
própria decidida, o "nunca duplicar login" deixou de valer — o desenho
abaixo cria esse segundo sistema de propósito, de forma isolada do primeiro.

### O que foi construído (esboço completo, validado com testes reais)

**Banco de dados** — segunda migração, `c0410068d7f3`, encadeada depois da
`4ee4b695fa49`:
- `email_accounts.password_hash` — nasce nula, definida na ativação.
- `password_reset_tokens.alvo` (`'conta'` | `'email'`) — o mesmo mecanismo de
  token e o mesmo formulário de redefinição (`/redefinir-senha`) atende os
  dois casos; o backend decide qual senha muda pelo `alvo` gravado no
  token, não por parâmetro vindo do cliente.
- Índice parcial `uq_assinatura_email_por_usuario` em `subscriptions`, mesma
  lógica do índice do MeuCardio, para o novo `Subscription.kind == "email"`
  (`TIPO_EMAIL`, em `models/subscription.py`).

**Autenticação com dois escopos** (`core/security.py`): `create_access_token`
ganhou um campo `scope` (`"app"` por padrão — token de sempre, sem quebrar
sessão de quem já estava logado; `"email"` só emitido por
`POST /api/email/entrar`). `current_user` só aceita `scope="app"`;
`current_email_account` (novo) só aceita `scope="email"` e resolve a
`EmailAccount` pelo endereço — um token roubado de um sistema não abre o
outro. `assinatura_email_ativa(db, user_id)` é o helper que checa
`Subscription.kind == "email"` com status liberado, usado na ativação (não é
dependência de rota, porque a rota decide 409 e não 402 — 402 no
`lib/api.ts` do frontend redireciona pra `/assinatura`, a página errada aqui).

**`backend/app/api/email.py`, reescrito** — duas famílias de rota:
- `GET/POST /conta` — vistas de dentro da conta Corvia normal
  (`current_user`): status e ativação (que agora também recebe `{senha}` no
  corpo e a grava). Exige `assinatura_email_ativa`, não `assinante_ativo`.
- `POST /entrar` (login com endereço+senha próprios, devolve token
  `scope=email`), `POST /esqueci-senha` (público, manda o link para o
  e-mail PRINCIPAL do médico — nunca para dentro da própria caixa
  @corvia.med.br, o que trancaria quem esqueceu a senha) e
  `GET /pastas`, `GET/POST/DELETE /mensagens*`, `GET /eu` — todas atrás de
  `current_email_account`.
- Router saiu de `ROUTERS_ASSINANTES` e foi para `ROUTERS_LIVRES` no
  `main.py`: aplicar `assinante_ativo` (que checa `kind='meucardio'`)
  bloquearia justo quem assina só o e-mail. Cada rota autoriza a si mesma.

**`backend/app/api/billing.py`, estendido com cuidado redobrado** (é código
de pagamento real em produção):
- `_assinatura_email`/`_obter_ou_criar_assinatura_email` — funções PRÓPRIAS,
  não uma generalização das existentes: a função original sustenta a
  assinatura principal há meses, e não valia o risco de mudar seu
  comportamento pra acomodar o caminho novo.
- `_aplicar_evento` ganhou o ramo `tipo_assinatura == "email"` — **sem ele**,
  o primeiro evento de webhook de uma assinatura de e-mail cairia no `else`
  e seria tratado como assinatura da PLATAFORMA, corrompendo o estado de um
  assinante pagante. É a mesma classe de bug que o `CLAUDE.md` já documenta
  ter acontecido com `mode` em vez de metadata nos pedidos avulsos de
  telediagnóstico — path testado explicitamente (ver testes abaixo).
- `_sincronizar_caixa_de_email` — quando a assinatura de e-mail muda de
  status (cancelamento, inadimplência, reativação), a `EmailAccount.status`
  acompanha. Sem isso, cancelar a assinatura não bloquearia o acesso à caixa.
- `POST /checkout-email` — preço **inline** (`price_data`), não um Price
  pré-criado no painel do Stripe, ao contrário da assinatura principal —
  decisão deliberada: com `corvia_mail_preco_centavos` (novo campo,
  `config.py`) em 0 por padrão ("em branco"), a rota recusa com 409 em vez
  de cobrar valor inventado; quando o Rafael definir o preço, basta pôr o
  número no `.env`, sem precisar criar nada no painel do Stripe antes.
- `GET /status-email` — inclui `preco_definido`, pro frontend saber se
  mostra "Assine" ou "Em breve".

**Frontend:**
- `frontend/src/lib/apiEmail.ts` (novo) — cliente de API isolado do
  `api.ts` principal: token próprio (`corviamail.token` no localStorage),
  401 não redireciona pra `/entrar` (seria a tela errada).
- `frontend/src/pages/CorviaMail.tsx` (novo) — o "site" pedido, em três
  abas: Entrar (login da caixa), Esqueci a senha, Assine já (mostra preço
  ou "em breve", inicia checkout, e depois de pago mostra o passo de criar
  a senha inicial da caixa). Funciona tanto para quem não tem sessão Corvia
  aberta (mostra só "entre na Corvia primeiro", com link) quanto para quem
  já está logado (`useAuth()` decide, já que `AuthProvider` envolve o app
  inteiro em `main.tsx` — a mesma página serve os dois casos sem duplicar
  nada). Rota `/corvia-mail` registrada **nos dois ramos** de `App.tsx`
  (logado e deslogado).
- `frontend/src/pages/CaixaDeEmail.tsx`, reescrito — não pede mais senha
  inline (isso migrou pra aba "Assine já" do `CorviaMail.tsx`); em vez
  disso, se não há `corviamail.token` válido, redireciona para
  `/corvia-mail` (`<Navigate>`). Ressalva clínica (`RessalvaClinica`)
  mantida, sem mudança.
- `frontend/src/pages/RedefinirSenha.tsx` — passou a ler `?alvo=email` da
  URL só para mensagem/redirecionamento (o backend já decide tudo pelo
  token); nenhuma mudança na chamada de API em si.
- `Shell.tsx` — item de menu renomeado para "CorvIA Mail", apontando para
  `/corvia-mail` (não mais direto para `/caixa-de-email` — precisa passar
  pelo login próprio primeiro).

### Validação — mais extensa que o esboço anterior, com Postgres real

Diferente da rodada anterior (só `py_compile` e import), desta vez rodei a
cadeia inteira de migrações e um teste funcional de ponta a ponta contra um
Postgres 16 real nesta própria sessão (`apt-get install postgresql-16-pgvector`
+ banco `meucardio_test` local, descartado ao final):

- `alembic upgrade head` — as 21 migrações da cadeia inteira rodam sem erro,
  incluindo as duas novas desta tarefa. `alembic downgrade -2` e
  `upgrade head` de volta também testados — reversível.
- Esquema real conferido no `\d` do Postgres: `email_accounts.password_hash`,
  `password_reset_tokens.alvo` e o índice `uq_assinatura_email_por_usuario`
  existem exatamente como desenhado.
- Teste funcional com `TestClient` do FastAPI (Mail360 simulado por
  monkeypatch, já que não há credencial de parceiro): criação de usuário,
  tentativa de ativar sem assinatura (409), assinatura simulada como ativa,
  ativação da caixa com senha, `GET /conta` refletindo o estado, **token da
  conta principal barrado em `/pastas` (401)**, login na sessão e-mail,
  senha errada barrada, **token de e-mail barrado em `/api/auth/me` (401)**,
  leitura de pastas/mensagens, fluxo completo de esqueci-senha→redefinir
  (com `alvo=email` gravado e lido corretamente, senha antiga invalidada,
  senha da conta principal comprovadamente intocada), e cancelamento da
  assinatura suspendendo a caixa (login volta 403). 19 verificações, todas
  passaram.
- `checkout-email` com preço em 0 testado isoladamente: recusa com 409, sem
  tentar cobrar nada — `status-email` reporta `preco_definido: false`
  corretamente.
- Frontend: `npx tsc -b --noEmit` e `npm run build` sem erro, com todas as
  páginas novas/alteradas.

### O que ainda falta para publicar de verdade

1. **As duas pendências comerciais da Zoho continuam abertas** (preço de
   produção, LGPD do Mail360 especificamente) — decisão do Rafael foi
   mitigar com ressalva na tela, não bloquear por isso, mas a credencial de
   parceiro real ainda não existe, então nada disto foi testado contra a
   API de verdade.
2. **Preço do CorvIA Mail definido pelo Rafael em 30/07/2026: R$10,00/mês**
   (custo do Zoho é R$65,50/ano, cerca de R$5,46/mês). **Falta só aplicar em
   produção** — esta sessão não tem acesso ao `.env` do servidor (roda num
   container isolado, sem socket do Docker), então o Rafael precisa:
   1. Definir `CORVIA_MAIL_PRECO_CENTAVOS=1000` no `.env` de produção.
   2. Rebuildar o backend (variável só é lida na subida do processo).
   Enquanto isso não acontecer, `corvia_mail_preco_definido` continua falso
   e o checkout recusa com 409 — comportamento correto e testado, não é bug.
   **Pix acrescentado ao checkout** (pedido do Rafael, mesma mensagem):
   `payment_method_types` ganhou `"pix"` ao lado de `"card"`, com
   `payment_method_options.pix.mandate_options` (`amount_type: "fixed"`,
   `payment_schedule: "monthly"`) — é o recurso "Pix Automático" do Stripe,
   que autoriza cobrança recorrente via mandato bancário, não Pix avulso.
   Confirmado o formato exato direto no SDK instalado (`stripe==15.4.0`
   localmente; produção fixa `15.3.1`, mas o corpo da requisição é só um
   dict serializado — a validação de tipo do SDK não afeta o que trafega) e
   testado com a rede do Stripe interceptada (sem custo, sem chamada real):
   a rota `/api/billing/checkout-email` monta exatamente o payload esperado.
   **Duas coisas que esta sessão não tem como confirmar sem acesso à conta
   real**: (a) se Pix está habilitado nas configurações de pagamento do
   painel Stripe (é toggle do painel, não API) — sem isso o `pix` some do
   checkout em silêncio, sem erro; (b) o fluxo real de autorização do
   mandato pelo banco do assinante (o primeiro ciclo recorrente só passa a
   valer alguns dias depois da autorização — diferente do cartão, que cobra
   na hora). Vale testar um checkout de verdade em modo teste antes de
   confiar no Pix em produção.
3. **Migração ainda não rodou em produção.** Precisa ir antes do rebuild,
   como sempre.
4. **E-mail de recuperação de senha depende de SMTP configurado** —
   `tentar_enviar_email` já existe e falha graciosamente (loga e não envia)
   se `smtp_configurado` for falso; sem SMTP, o link de redefinição só
   aparece pra um admin repassar manualmente, mesmo caminho que já existe
   pra recuperação da conta principal (`GET /api/auth/reset-pendentes`).
5. **Nenhum teste automatizado foi commitado** — a validação desta sessão
   foi um script manual, descartado ao final (não faz parte do repositório).

---

## Tarefa 29 — Unir CorvIA Mail à emissão de receita e documento (30/07/2026)

Pedido do Rafael: emitir receita e/ou atestado/laudo com opção de mandar por
e-mail ao paciente, escolhendo entre o CorvIA Mail do médico ou o e-mail
pessoal de cadastro dele.

### Dois achados que mudaram o desenho antes de escrever código

1. **A escolha "CorvIA Mail ou e-mail pessoal" colidia com o termo LGPD que
   o próprio Rafael tinha acabado de aprovar** (item 14b do CLAUDE.md): a
   caixa do CorvIA Mail proíbe explicitamente "nome, CPF ou qualquer dado
   que identifique um paciente em conjunto com informação clínica" — e
   receita/atestado é exatamente isso. Rafael escolheu **não anexar o PDF a
   e-mail nenhum**: o paciente recebe um LINK seguro, o conteúdo clínico
   nunca passa pela Zoho. Isso também resolveu sozinho a pergunta do "e-mail
   pessoal": como só um LINK viaja (sem conteúdo clínico), o envio da
   notificação é sempre pelo SMTP da própria Corvia
   (`services/notificar.tentar_enviar_email`, o mesmo da recuperação de
   senha) — nunca pela Zoho, então "CorvIA Mail ou e-mail pessoal" deixou de
   ser uma escolha técnica que o médico precisa fazer.
2. **Não existia NENHUMA tela de emissão** — nem de receituário (nem o
   sistema legado `prescriptions.py`, nem o novo regulatório da Tarefa 27),
   nem de "gerar documento" a partir de modelo (`Templates.tsx` só geria
   modelo, o passo de preencher e gerar nunca tinha frontend). Perguntei ao
   Rafael antes de seguir; ele pediu para construir as duas telas completas
   nesta rodada, não só o botão de e-mail.

### O que foi construído

**Zoho Mail360 ganhou suporte a anexo** (pedido à parte do Rafael, para o
webmail em geral — não para receita, que vai por link): confirmado o
formato exato direto na documentação oficial
(`zoho.com/mail360/help/api/upload-attachment.html` e
`.../sending-email-messages.html`, ambas lidas nesta sessão): upload é
POST separado (`/accounts/{key}/attachments?fileName=...`, corpo é o
binário puro, resposta traz `data.fileId`), e o envio referencia esse
`fileId` num array `attachments`. `mail360.py` ganhou `upload_anexo()` e
`enviar_mensagem()` passou a aceitar `anexos`. `POST /api/email/mensagens/
anexos` (multipart, limite 15 MB) + `NovaMensagem.anexos` no schema.
`CaixaDeEmail.tsx` ganhou input de arquivo no compose.

**Banco** — migração `425d4a2318d7`, encadeada depois de `b55dd7126ced`:
- `prescription_recipients.email_cifrado` — mesmo padrão de cifra de
  nome/endereço/documento (AES-256-GCM, `cofre.cifrar_campo`).
- `generated_documents.destinatario_email_cifrado` — idem, para
  atestado/laudo (que não tinha nenhuma entidade de destinatário
  identificável antes).
- Tabela nova `document_share_links` (modelo em `app/models/
  compartilhamento.py`, arquivo próprio — não é conceito de receituário,
  é infraestrutura compartilhada entre os dois fluxos): token de 32 bytes
  (mesmo gerador do `password_reset_tokens`), `tipo`/`referencia_id` no
  mesmo padrão genérico do `AuditLog.entity`/`entity_id`, validade de 7
  dias, **não é uso único** (só a validade controla acesso — um paciente
  pode querer abrir o PDF mais de uma vez, em aparelhos diferentes).

**PDF de atestado/laudo, do zero** — `pdf_documento.documento_generico()`,
reaproveitando o cabeçalho/rodapé do receituário comum (mesma identidade
visual). O receituário comum já tinha PDF (`receituario_comum`, decidido em
29/07/2026 — o CLAUDE.md/briefing anterior estava desatualizado ao dizer
que "não existe geração de PDF no sistema").

**Rotas novas:**
- `POST /api/receituario/documentos/{id}/enviar-email` — só funciona com
  documento já `emitido` (ou seja, só tipo `COMUM` hoje; os demais
  continuam bloqueados por HTTP 501 esperando SNCR/assinatura, sem
  mudança). Cifra e grava o e-mail, cria o `DocumentShareLink`, manda a
  notificação. Se o SMTP não estiver configurado, devolve o link em vez de
  só erro — mesma filosofia do `esqueci_senha`, mas aqui é o próprio médico
  quem tem autoridade sobre o dado do paciente dele, não um admin.
- `GET/POST /api/document-templates/gerados`, `.../{id}`, `.../{id}/pdf`,
  `.../{id}/enviar-email` — o CRUD de "documento gerado" que faltava
  inteiro (só existia `POST /gerar`, sem listar nem baixar PDF).
- `GET /api/documentos-publicos/{token}` — **rota pública, sem
  autenticação nenhuma**, registrada em `ROUTERS_LIVRES` com comentário
  explicando por quê: quem acessa é o paciente, que nunca terá conta na
  Corvia. A única defesa é o token de alta entropia. Gera o PDF na hora
  (não guarda cópia em disco), confere expiração, e no caso da receita
  reconfirma `status == "emitido"` (não confia só no que valia quando o
  link foi criado).

**Bug pego e corrigido durante a implementação**: `GET /gerados/{id}/pdf`
inicialmente montava o cabeçalho do PDF com o médico que está BAIXANDO,
não o que EMITIU — um admin abrindo o documento de outro médico apareceria
como se fosse o autor. Corrigido buscando `User` por `g.created_by`.
Análoga: `enviar_email_gerado` propositalmente **não** usa o mesmo
`_obter_gerado` que permite acesso de admin — mandar e-mail a um paciente
em nome de outro médico não é ação que um admin deva poder disparar, só
visualizar é.

**Frontend, as duas telas que não existiam:**
- `Receituario.tsx` (nova, rota `/receituario`, menu "Emitir receita"):
  formulário de destinatário + itens (busca de fármaco em `/drugs`,
  mesmo padrão de carregar lista inteira e filtrar no cliente já usado em
  `Interacoes.tsx`) + prévia de classificação + criar + por documento:
  revisar, emitir (baixa PDF via `api.blob`), enviar por e-mail.
- `Templates.tsx`, estendida: botão "Usar" em cada modelo abre formulário
  de variáveis (extraídas do próprio corpo do modelo via regex, no
  cliente) → gerar → baixar PDF / enviar por e-mail. Nova seção
  "Documentos gerados" lista o histórico.

**Achado à parte, não corrigido (fora do escopo desta tarefa)**: dois
call sites existentes de `api.blob()` (`Curso.tsx`, `MaterialPaciente.tsx`)
passam o caminho com prefixo `/api/...` duplicado (`BASE` já é `/api`),
inconsistente com o terceiro uso (`Telediagnostico.tsx`, sem o prefixo) e
com todo o resto do `api.get`/`post`. Parece bug latente pré-existente;
meu código novo usa o padrão sem prefixo duplicado, consistente com a
maioria.

### Validado nesta sessão, contra Postgres real

Cadeia de migrações completa (`alembic upgrade head`, mais uma vez com
`postgresql-16-pgvector` instalado localmente para o teste). Teste
funcional de ponta a ponta com `TestClient`, 14 verificações: criar
receituário → revisar → emitir (PDF real, ReportLab instalado para o
teste) → enviar-email (SMTP não configurado → devolve link) → baixar pelo
link público → link expirado devolve 410 → mesmo fluxo completo para
atestado (template → gerar → listar → PDF → enviar-email → baixar pelo
link) → token inexistente devolve 404. `npx tsc -b --noEmit` e `npm run
build` sem erro nas duas vezes que rodei (antes e depois de ligar as rotas
no `App.tsx`/`Shell.tsx`).

### O que falta para publicar

1. **Migração `425d4a2318d7` ainda não rodou em produção.**
2. **Nenhum teste real do upload de anexo do Mail360** — mesma ressalva de
   sempre: sem credencial de parceiro, o formato foi confirmado só contra a
   documentação pública, não contra uma chamada de verdade.
3. Publicação de conteúdo não se aplica aqui (é código, não `content/`),
   mas rebuild pede confirmação do Rafael, como sempre.
