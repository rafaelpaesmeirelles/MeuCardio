# Inventário funcional da Corvia

Data da auditoria inicial: 3 de agosto de 2026. Atualizado em 27 de agosto de 2026.

## Escopo da certificação

Esta auditoria compara o código anterior à estabilização com a branch atual e
protege, por teste automatizado, a presença das rotas React, destinos de menu,
routers FastAPI, páginas importadas e artefatos críticos. Ela certifica o código
e a CI; a disponibilidade do domínio de produção continua dependendo do deploy,
da infraestrutura e das credenciais externas.

O comando de verificação é:

```bash
python scripts/feature_inventory.py
```

A CI falha quando uma funcionalidade publicada desaparece ou quando uma nova
superfície é adicionada sem revisão explícita do inventário.

## Funcionalidades presentes no produto

- autenticação, solicitação de acesso, ativação e recuperação de senha;
- páginas públicas revisadas de Termos de Uso e Política de Privacidade;
- sessão web HttpOnly, encerramento de sessões e conta do usuário;
- painel, busca global, favoritos e alertas por condição/diretriz;
- Biblioteca científica, documentos, fluxogramas, diretrizes e galeria;
- evidências, estudos, exames, medicamentos, interações, guias por doença e triagem por sintomas;
- calculadoras e escores clínicos;
- cockpit de Cardiologia Intensiva e Unidade Coronariana, com acesso ao corpus
  publicado, checklists, emergência, infusões, vasoativos e cálculo de ventilação
  protetora baseado em peso corporal predito;
- trilhas de estudo, casos clínicos, cursos parceiros e checklists;
- material para pacientes e envio associado;
- Round hospitalar e assistente clínico com IA/RAG;
- Agenda Integrada em dia/semana/mês/lista, rotina profissional recorrente,
  planejamento diário, locais, serviços, recursos, exceções e indicadores pessoais;
- mobilidade consentida com próximo local, ETA e trânsito, sem persistência da
  posição atual; Google Routes/Mapbox dependem de credencial real;
- sincronização incremental e escrita protegida para Google Calendar e Microsoft
  365; demais PEP/PMS ficam bloqueados até homologação oficial;
- emissão de documentos, prescrição eletrônica e assinatura;
- telediagnóstico e fila administrativa;
- CorvIA Mail, caixa de e-mail e chat flutuante;
- modo Emergência com atalho permanente fora da própria tela;
- administração de usuários, conteúdo, planos e operações;
- exportação, links públicos controlados, auditoria e observabilidade;
- backup, restauração, migrations, bootstrap administrativo e smoke de release.

## Conteúdo científico protegido

O inventário científico mantém baseline mínimo de 5.035 registros distribuídos
em 13 frentes: documentos, galeria, exames, evidências, estudos, medicamentos,
checklists, trilhas, materiais para pacientes, emergência, casos clínicos, guias
por doença e triagem por sintomas. A reconciliação com o PostgreSQL é
idempotente e não deve reduzir conteúdo já publicado.

## Dependências externas que exigem configuração operacional

- SMTP/transacional: o código e os fluxos existem, mas o envio real depende de
  credenciais válidas do provedor. O erro 535 observado é de autenticação externa,
  não remoção da funcionalidade.
- IA/RAG: depende de provedor, chave, limites e política de custos configurados.
- Cobrança: depende das chaves e webhook do Stripe.
- CorvIA Mail: depende das credenciais e tokens do serviço de correio.
- Assinatura: o modo manual está disponível; provedores externos catalogados só
  podem ser ativados após integração e credenciais reais, sem simulação.
- Telediagnóstico e armazenamento: dependem dos volumes persistentes e da chave
  de criptografia presentes no ambiente de produção.

## Ideias documentadas, mas ainda não publicadas como funcionalidade

O editor Markdown citado no planejamento histórico permanece explicitamente
não implementado. Propostas futuras não devem ser anunciadas como disponíveis
até possuírem rota, backend, testes, controle de acesso e documentação de
operação. Elas ficam separadas deste inventário para evitar uma falsa
certificação.

## Regra de manutenção

Toda remoção, renomeação ou inclusão de funcionalidade deve atualizar, no mesmo
pull request, o inventário automatizado, os testes, a navegação, as permissões e
esta documentação. Mudanças silenciosas são bloqueadas pela CI.
