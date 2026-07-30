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

Pesquisa técnica mais profunda sobre a Titan Email (onboarding real, endpoints da
API além de `createMailOrder`, mecanismo exato do token de auto-login, se o embed
é do webmail do usuário final ou só do painel de admin, preço, red flags) está em
andamento e será acrescentada a este arquivo antes de qualquer código de modelo de
dados ou interface.
