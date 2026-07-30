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
2. **LGPD/localização de dados não declarada especificamente para o
   Mail360.** A Zoho declara conformidade GDPR para o Zoho Mail geral, mas
   nenhuma fonte encontrada confirma isso — nem localização de dados —
   especificamente para o Mail360, produto tecnicamente separado. Como não
   há datacenter da Zoho no Brasil, dado de assinante brasileiro trafegaria
   para fora do país; vale levantar isso formalmente antes de fechar.

Nenhum código de modelo de dados ou interface foi escrito para esta tarefa.
O próximo passo natural — desenhar a arquitetura técnica (rotas do backend,
modelo de dados de conta/mensagem, componentes de interface do webmail) —
ainda não foi iniciado, para não presumir que as duas pendências acima serão
resolvidas a favor da Corvia antes de o Rafael confirmar com o comercial da
Zoho.
