# Briefing de implementação — MeuCardio

Este documento reúne tudo que precisa ser implementado no sistema MeuCardio a partir das decisões tomadas. Trate cada seção como uma tarefa independente, mas leia o documento inteiro antes de começar — há regras transversais (na seção final) que valem para todas as tarefas.

Antes de começar: explore a estrutura atual do repositório (frontend, backend, schemas de conteúdo já existentes) e me apresente um plano curto de execução por tarefa antes de implementar, para eu validar a abordagem em cada uma.

---

## 1. Paleta de cores — aplicar em todo o sistema

Trocar a paleta atual pela paleta oficial da marca (a mesma usada na logo e em todo o material de divulgação já produzido):

| Token | Hex | Uso |
|---|---|---|
| `navy` | `#0B2E45` | Cor primária / fundo escuro / header |
| `navy-dark` | `#081E30` | Fundo escuro alternativo, gradientes |
| `red` | `#D5001D` | Cor de destaque / CTAs / alertas positivos da marca |
| `red-dark` | `#B0001A` | Hover/estado ativo do vermelho |
| `teal` | `#1C7293` | Cor secundária / links / acentos |
| `teal-light` | `#6FB4CC` | Acentos claros sobre fundo escuro |
| `off-white` | `#FCFCFC` | Fundo claro padrão |
| `ink` | `#26333B` | Texto principal |
| `muted` | `#55666F` | Texto secundário |
| `line` | `#E4E8EA` | Bordas e divisores |

Aplicar esses tokens no arquivo central de tema/design system do projeto (variáveis CSS, Tailwind config, ou equivalente), substituindo a paleta atual em todos os componentes — botões, cabeçalhos, cards, estados de foco, gráficos, ícones. Não deixar cores antigas “esquecidas” em componentes isolados. Ao final, validar contraste de acessibilidade (texto sobre `navy`/`red` deve permanecer legível — usar branco ou `off-white` para texto sobre essas cores).

---

## 2. Popular as seções de conteúdo que estão zeradas

As seções abaixo existem na interface mas estão sem conteúdo. Popular cada uma seguindo exatamente o mesmo rigor já usado no restante do projeto:

- **Medicamentos**
- **Galeria de imagens**
- **Marcadores e exames cardiológicos**
- **Evidências**
- **Trabalhos científicos**

Regras obrigatórias para este conteúdo (as mesmas já aplicadas ao resto do MeuCardio):
- Toda informação clínica deve ser rastreável a diretrizes ESC, AHA/ACC ou SBC, ou a metanálises/estudos de alta qualidade.
- Nenhum DOI, PMID, dose ou dado não verificável pode ser inventado. Onde não houver certeza, sinalizar explicitamente com `"VERIFICAÇÃO HUMANA NECESSÁRIA"` em vez de preencher com suposição.
- Seguir o schema JSON/JSONL já usado nos módulos existentes (protocolos, farmacologia, biblioteca científica) para manter consistência de estrutura.
- Entregar em lotes (batches) por seção, não tudo de uma vez, para permitir revisão.

**Importante:** este conteúdo é clínico e vai para produção. Antes de publicar qualquer lote, ele precisa passar por mim para validação — não marcar como "concluído" sem esse checkpoint.

---

## 3. Página de gestão de cadastro e assinatura

Criar a página (atualmente inexistente) onde o usuário gerencia sua própria conta. Deve incluir:

- **Perfil**: nome, CRM/UF, RQE, e-mail, foto, edição desses dados.
- **Assinatura atual**: plano ativo (ex: MeuCardio R$20/mês), status (ativo/cancelado/em atraso), data da próxima cobrança.
- **Gestão de pagamento**: forma de pagamento cadastrada, opção de trocar cartão/forma de pagamento.
- **Histórico de cobranças**: lista de faturas/recibos anteriores.
- **Alterar/cancelar plano**: upgrade, downgrade e cancelamento, com confirmação clara do que muda em cada caso.

Seguir a paleta definida na Tarefa 1.

---

## 4. Gerador de prescrição e documentos, com assinatura digital

Nova funcionalidade: o profissional gera, dentro do MeuCardio, os seguintes documentos:

- **Receita médica simples**
- **Receita de controle especial** (atenção: este tipo de receita segue regras específicas da ANVISA — Portaria 344/98 e atualizações — sobre numeração, validade e formato; não tratar como uma receita comum com um rótulo diferente. Se o repositório não tiver essa lógica, sinalizar antes de implementar, para decidirmos o formato correto juntos.)
- **Atestados médicos**
- **Laudos** (reaproveitando a lógica do serviço de telediagnóstico/teleconsultoria já desenhado — ver Tarefa 5)

Cada documento gerado deve:
- Usar um template formatado (identificação do médico com CRM/RQE, identificação do paciente, corpo do documento, data).
- Ser assinado digitalmente antes da entrega final — integrar com **VIDAAS** (certificado fornecido pelo CRM) e/ou **Gov.br**, que já são os provedores usados.
- Ficar registrado em um histórico consultável (auditoria: quem gerou, quando, qual paciente, hash/verificação do documento assinado).
- Gerar o arquivo final em PDF.

---

## 5. Serviço de laudo/consultoria à distância (telediagnóstico)

Implementar como funcionalidade nativa do sistema (não como página solta) o serviço discutido:

**Escopo de exames aceitos** (não aceitar nenhum outro nesta fase):
- Eletrocardiograma (ECG)
- MAPA
- Holter 24h
- Teste Ergométrico

**Fluxo de solicitação** (protótipo de referência já validado, anexo `solicitar.html` — usar como referência de UX, não como código final de produção):
1. Médico solicitante se identifica (nome, CRM/UF, contato).
2. Escolhe o exame, anexa o arquivo (foto ou PDF).
3. Descreve a dúvida específica.
4. Escolhe o tipo de serviço: **Consultoria** (interpretação, sem laudo assinado) ou **Laudo completo assinado**.
5. Escolhe a urgência: **Eletivo** (até 12h) ou **Urgente/Plantão** (até 2h).
6. Se for laudo assinado, informa dados do paciente (nome, CPF).
7. Confirma que obteve o consentimento do paciente (checkbox vinculado ao TCLE — anexo `TCLE_MeuCardio_Telediagnostico.docx`, modelo de referência que ainda precisa de revisão jurídica antes do uso definitivo).
8. Preço calculado automaticamente conforme a combinação escolhida:

| Serviço | Eletivo | Urgente/Plantão |
|---|---|---|
| Consultoria | R$ 40 | R$ 60 |
| Laudo completo assinado | R$ 70 | R$ 100 |

9. Pagamento processado (integrar com gateway de pagamento já usado ou a ser definido — Stripe/Mercado Pago).
10. Solicitação entra em uma fila com SLA visível (contagem do prazo conforme urgência escolhida), visível tanto para o solicitante quanto para mim como painel de atendimento.
11. Ao concluir, o laudo/consultoria assinado (via VIDAAS/Gov.br) é entregue dentro da plataforma e por e-mail/notificação.

**Considerações técnicas obrigatórias:**
- O upload do exame contém dado de saúde do paciente — exige armazenamento seguro, criptografado, com controle de acesso e trilha de auditoria, em conformidade com a LGPD.
- Não usar serviços de formulário genéricos (Google Forms, Formspree etc.) para captar esse dado — precisa ser first-party, no próprio backend do MeuCardio.
- O laudo assinado precisa seguir os requisitos da Resolução CFM nº 2.314/2022: identificação do médico (nome, CRM, endereço profissional), identificação do paciente, data/hora, e assinatura com certificação digital ICP-Brasil (VIDAAS já atende a esse padrão).

---

## 6. Redesenhar o Painel principal (dashboard)

O Painel atual dá muito destaque a números/contadores de arquivos do sistema — é uma informação até interessante, mas pouco útil no dia a dia. Redesenhar a página seguindo esta direção:

- **Reduzir o espaço ocupado pelos números/contadores.** Eles podem continuar existindo (ex: em um card menor, num canto, ou numa barra compacta), mas deixam de ser o elemento principal da tela.
- **Substituir o espaço liberado por destaques e acessos rápidos às funções do sistema** — ou seja, o Painel passa a funcionar como um verdadeiro atalho para o uso diário, não só uma tela de status.
- Cada função em destaque (Assistente clínico, Protocolos/Fluxogramas clínicos, Calculadoras, Medicamentos, Biblioteca científica, Round hospitalar, Laudo/Consultoria — e as demais do menu lateral) deve aparecer como um **card visualmente destacado**, contendo:
  - Nome da função.
  - Uma **descrição curta da utilidade** dela (o que ela resolve, não só o nome técnico) — ex: não só "Calculadoras", mas algo como "Escores validados (GRACE, TIMI, SCORE2...) prontos para uso no leito".
  - Ser **clicável e levar direto para a função**, sem precisar passar pelo menu lateral.
- O menu lateral continua existindo normalmente — o Painel passa a ser um **caminho adicional e mais rápido**, não uma substituição do menu.
- Usar a paleta de cores definida na Tarefa 1 para destacar visualmente esses cards (ex: ícone ou borda em `red`/`teal` sobre fundo `off-white`, títulos em `navy`).

---

## 7. Integração de pagamento (Stripe)

Implementar dois fluxos de pagamento distintos via Stripe — não tratar como um único fluxo, porque são naturezas diferentes de cobrança:

- **Pagamento recorrente** — assinatura mensal do MeuCardio (R$20/mês), usada na página de gestão de cadastro/assinatura da Tarefa 3. Usar o fluxo de *Subscriptions/Billing* do Stripe (não o de pagamento único).
- **Pagamento único (one-time)** — cobrança avulsa do serviço de laudo/consultoria da Tarefa 5, calculada dinamicamente conforme a combinação de serviço (Consultoria/Laudo) e urgência (Eletivo/Urgente), já definida na tabela de preços daquela tarefa. Usar o fluxo de *Checkout* de pagamento único do Stripe.

Já existe uma conta Stripe configurada ("Meirelles e Maluf Servicos Medicos") e o código de referência para o pagamento único já foi gerado no Workbench do Stripe (blueprint "Aceitar um pagamento único com o Checkout", em modo de teste) — vou colar esse código de referência junto com este briefing. Adaptar esse código ao backend do projeto, e implementar separadamente o fluxo de assinatura recorrente para o plano de R$20/mês.

Pontos de atenção:
- Manter as chaves de API do Stripe (test e, futuramente, live) como variáveis de ambiente, nunca no código.
- A cobrança do laudo/consultoria só deve ser confirmada como paga antes de a solicitação entrar na fila de atendimento (Tarefa 5).
- Ao mudar para chaves live (produção), confirmar comigo antes — nenhuma cobrança real deve ser testada sem aviso prévio.

---

## Regras transversais (valem para todas as tarefas acima)

1. **Nunca inventar dado clínico, dose, DOI, PMID ou número de norma.** Onde não houver certeza, sinalizar `"VERIFICAÇÃO HUMANA NECESSÁRIA"`.
2. **Dado de saúde é dado sensível.** Qualquer nova funcionalidade que armazene informação de paciente precisa de storage seguro e conformidade com a LGPD desde o design — não como algo a ajustar depois.
3. **Documentos assinados digitalmente** (receitas, atestados, laudos) precisam realmente passar pelo fluxo de assinatura VIDAAS/Gov.br antes de serem considerados "emitidos" — nunca simular ou pular essa etapa.
4. **Apresente um plano antes de executar cada tarefa grande** (especialmente a 2, 4, 5, 6 e 7), para eu validar antes de você implementar.

---

## Anexos de referência (protótipos já validados, não é o código final)
- `solicitar.html` — protótipo de UX do fluxo de solicitação de laudo/consultoria
- `TCLE_MeuCardio_Telediagnostico.docx` — modelo de termo de consentimento
- Código gerado pelo Workbench do Stripe para o blueprint de pagamento único — colado abaixo
- Paleta de cores da Tarefa 1 (já usada nos materiais de divulgação)

### Blueprint do Stripe — pagamento único (referência para a Tarefa 7)

Este é o blueprint gerado pelo Workbench do Stripe para o fluxo de pagamento único via Checkout. Use como referência de quais chamadas de API são necessárias e em que ordem — adapte nomes de funções, rotas e variáveis à arquitetura do projeto (não usar nomes como "chapter1"/"step2" no código; nomear pela ação real, ex: `create_checkout_session`).

```toon
title: Aceite um pagamento único com o Checkout
steps[3]:
  - key: setup-chapter
    title: Configurar produto e preços
    description: Crie um produto com informações de preço para o pagamento único.
    nodes[1]:
      - type: apiRequests
        key: create-product
        title: Crie produto e preço
        description: Crie um produto com informações de preços.
        requests[1]:
          - key: create-product-request
            path: /v1/products
            method: post
            params:
              name: Example Product
              default_price_data:
                currency: usd
                unit_amount: 2000
  - key: checkout-chapter
    title: Conclua o checkout
    description: Crie uma sessão de Checkout e complete o fluxo de pagamento.
    nodes[2]:
      - type: apiRequests
        key: create-checkout-session
        title: Criar sessão de checkout
        description: Crie uma sessão de Checkout para um pagamento único.
        requests[1]:
          - key: create-checkout-session-request
            path: /v1/checkout/sessions
            method: post
            params:
              line_items[1]{price,quantity}:
                "${node.setup-chapter.create-product.create-product-request:default_price}",1
              mode: payment
              success_url: "https://dashboard.stripe.com/workbench/blueprints/one-time-payment/checkout-chapter?confirmation-redirect=create-checkout-session"
              cancel_url: "https://dashboard.stripe.com/workbench/blueprints/one-time-payment/checkout-chapter?confirmation-redirect=create-checkout-session"
      - type: uiComponent
        key: complete-checkout
        title: Conclua o checkout
        description: Abra a URL da sessão de Checkout para concluir o pagamento.
        link: "${node.checkout-chapter.create-checkout-session.create-checkout-session-request:url}"
  - key: webhook-chapter
    title: Gerenciar eventos de Webhook
    description: Escute eventos de Webhook para confirmar que o pagamento foi bem-sucedido.
    nodes[1]:
      - type: asyncHandler
        key: handle-checkout-completed
        title: Aguarde pelo evento checkout.session.completed
        events[1]{eventType,eventPayloadType}:
          checkout.session.completed,snapshot
        expectedNumberOfEvents: 1
```

**Pontos de adaptação obrigatórios ao implementar este blueprint:**
- O exemplo usa `name: Example Product` e `currency: usd` com valor fixo (`unit_amount: 2000`) — isso é só o placeholder do blueprint. Substituir por produtos reais em `BRL`, com os valores definidos na tabela de preços da Tarefa 5 (R$ 40 / R$ 60 / R$ 70 / R$ 100, conforme serviço e urgência escolhidos), criando um produto/preço para cada combinação ou calculando o valor dinamicamente na criação da sessão de Checkout.
- `success_url`/`cancel_url` do exemplo apontam para o próprio Workbench do Stripe — trocar pelas URLs reais do MeuCardio (ex: página de confirmação do pedido de laudo, e a própria tela de solicitação em caso de cancelamento).
- Implementar o `webhook-chapter`: o backend precisa escutar o evento `checkout.session.completed` para só então confirmar o pagamento e liberar a solicitação na fila de atendimento (ver regra da Tarefa 5: "a cobrança só deve ser confirmada como paga antes de a solicitação entrar na fila").
- Seguir as variáveis de ambiente já usadas no projeto para as chaves do Stripe (`STRIPE_SECRET_KEY`, `STRIPE_PUBLISHABLE_KEY`) — não hardcode.
- Não definir a versão da API do Stripe manualmente no cliente, a menos que o restante do projeto já tenha um padrão definido.

