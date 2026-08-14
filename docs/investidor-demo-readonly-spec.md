# CorVIA — Modo Investidor (especificação canônica)

Data: 13/08/2026

Esta especificação substitui qualquer regra anterior que exigisse dados pessoais, dados profissionais, KYC, documento pessoal, documento profissional ou selfie de usuários marcados como `User.investidor`.

## 1. Entrada e onboarding

- Conta Investidor é criada exclusivamente pelo administrador.
- Não exige completar nenhum dado no primeiro acesso.
- Não exige CPF, data de nascimento, profissão, conselho, registro, UF, especialidade ou RQE.
- Não exige documento pessoal.
- Não exige documento profissional.
- Não exige selfie.
- Não entra em fila de KYC e não depende de aprovação manual.
- Não depende de Stripe ou assinatura paga.
- No primeiro login, deve ir diretamente para `/tour`.
- Ao concluir ou pular o tour, deve ir para a Home / Clinical Command Center.

## 2. Credencial do modo Investidor

- Senha fixa: `CorVIAOS`.
- A criação administrativa de uma conta Investidor ignora senha customizada e grava a senha fixa.
- Converter uma conta existente para Investidor redefine sua senha para a senha fixa.
- Investidor não pode trocar a própria senha.
- Investidor não recebe fluxo público de recuperação/redefinição de senha.

## 3. Princípio global: demonstração somente leitura

Investidor deve conseguir navegar e conhecer toda a plataforma, mas não pode executar nenhuma operação real de criação, alteração, exclusão, envio, conexão, sincronização, geração, emissão, assinatura, compartilhamento ou exportação.

O backend é a fonte de verdade. Desabilitar botões no frontend é apenas UX e nunca substitui o bloqueio servidor.

Regra padrão:

- GET/HEAD/OPTIONS: permitidos quando forem estritamente de leitura e não expuserem dados reais de terceiros.
- POST/PUT/PATCH/DELETE: bloqueados para Investidor, exceto os endpoints estritamente necessários para concluir/dispensar o tour e fechar avisos de demonstração.
- Endpoints GET que iniciem OAuth, provisionamento, geração, download recém-gerado ou qualquer efeito colateral também devem ser bloqueados.

Mensagem padrão recomendada:

`Modo investidor: esta conta é somente para visualização da plataforma.`

## 4. Isolamento de dados

Como a senha do modo Investidor é fixa, a conta não pode servir como porta de acesso a PII ou dados reais de operação.

Investidor nunca deve visualizar:

- pacientes reais de outros usuários;
- documentos reais de pacientes;
- prescrições reais de terceiros;
- KYC ou documentos de identidade;
- conteúdo de e-mail real;
- contas externas reais;
- eventos privados de calendário de outros usuários;
- credenciais/tokens;
- billing/Stripe de terceiros;
- superfícies administrativas.

Quando uma tela operacional precise de conteúdo para demonstrar a interface, usar dado sintético explicitamente marcado como demonstração.

## 5. CorVIA Mail

- Investidor vê a interface completa do CorVIA Mail.
- Dados devem ser sintéticos, nunca provenientes de Mail360 ou caixa externa real.
- Não provisionar caixa real.
- Não permitir enviar, responder, responder a todos, encaminhar, criar rascunho, apagar/mover mensagem, subir/baixar anexo real, conectar Google/Microsoft/Yahoo/Apple, sincronizar ou alterar assinatura.
- A interface deve deixar claro `Modo demonstração · somente visualização`.
- Pode usar um endereço visual sintético `investidor@corvia.med.br`, desde que nenhuma caixa real seja provisionada para esse endereço.
- Se existir uma conta real `investidor@corvia.med.br` no Mail360, está autorizada sua exclusão após conferência por correspondência exata do endereço/account_key.

## 6. Agenda / Calendário

Investidor pode conhecer todas as visões da agenda (dia, semana, mês, lista), configurações e superfícies de contas conectadas, porém:

- não conecta Google Calendar, Microsoft 365, Apple/iCloud ou qualquer outro provedor;
- não cria/edita/cancela compromissos;
- não cria/edita locais, serviços, rotinas ou recursos;
- não sincroniza;
- não habilita escrita externa;
- não altera preferências operacionais.

Preferencialmente apresentar eventos sintéticos de demonstração em vez de dados reais.

## 7. Prescrição

Investidor pode abrir e explorar a interface de Prescrição/Receituário e seus estados visuais, porém não pode:

- classificar operacionalmente um receituário com persistência;
- criar receita;
- revisar/confirmar receita;
- emitir PDF/documento;
- assinar;
- compartilhar;
- enviar por e-mail;
- gerar link para paciente;
- salvar qualquer prescrição.

Quando necessário, mostrar prévia sintética não emitível.

## 8. Documentos e solicitações

Investidor pode navegar pela galeria de tipos, modelos, formulários e previews, mas não pode gerar, emitir, salvar, assinar, baixar arquivo recém-gerado, compartilhar ou enviar documentos.

Isso inclui atestados, relatórios, solicitações de exames, encaminhamentos, avaliações e demais documentos clínicos.

## 9. Material para paciente

Investidor pode visualizar a biblioteca, temas, modelos e previews de materiais, mas não pode:

- gerar material personalizado;
- associar a paciente;
- criar PDF;
- exportar;
- compartilhar;
- enviar por e-mail.

## 10. Exportar conteúdo

Investidor pode abrir `/exportar`, pesquisar o catálogo exportável e compreender a funcionalidade, mas não pode gerar PDF, realizar download gerado ou enviar a exportação pelo CorVIA Mail.

## 11. Demais módulos operacionais

O mesmo princípio vale para todo o sistema:

- Pacientes/Round: interface visível, sem criar/editar/excluir paciente, nota ou dado clínico.
- Telediagnóstico/laudo/consultoria: interface visível, sem criar solicitação, upload, laudo, assinatura ou envio.
- Assistentes: interface pode ser apresentada, mas ações que alterem agenda, e-mail, paciente, documentos ou outros dados reais são proibidas.
- Contas conectadas: interface visível, conexão/reconexão/desconexão proibidas.
- Minha Conta: dados da conta podem ser vistos; alterações operacionais bloqueadas no modo demonstração.
- Favoritos e preferências persistentes: nenhuma escrita persistente, salvo o estado mínimo necessário para concluir o tour/fechar aviso.

## 12. Billing / entitlement

- `User.investidor` continua sendo fonte de acesso administrativo gratuito em `tem_acesso_ao_produto`.
- Nunca chamar checkout/Stripe para Investidor.
- Não criar Customer ou Subscription do Stripe para o acesso Investidor.
- A tela de assinatura deve identificar o acesso como demonstração/administrativo e não oferecer cobrança operacional.

## 13. Conversão pelo admin

Ao marcar uma conta como Investidor:

- `investidor = true`;
- `convidado = false`;
- `is_active = true`;
- `status = aprovado`;
- `profile_completion_required = false`;
- senha = hash de `CorVIAOS`;
- `onboarding_visto = false` para que o próximo login passe pelo tour;
- KYC não é exigido e a conta não aparece em fila de KYC.

Ao criar diretamente com `tipo_acesso = investidor`, aplicar a mesma matriz desde o nascimento da conta.

## 14. Auditoria

Registrar em AuditLog pelo menos:

- criação de conta Investidor;
- concessão/revogação do modo Investidor;
- redefinição administrativa para a senha fixa (sem registrar a senha em texto claro);
- bloqueio de tentativa de operação real, quando útil para segurança/diagnóstico, sem logar conteúdo clínico/PII desnecessário;
- eventual exclusão da caixa real `investidor@corvia.med.br` no Mail360.

## 15. Testes mínimos de regressão

1. Investidor criado sem CPF/data/profissão entra sem completar perfil.
2. `kyc_required == false` sem nenhum KYC registrado.
3. Primeiro login retorna `onboarding_pendente == true` e direciona ao tour.
4. Concluir/pular tour libera Home.
5. Login funciona com `CorVIAOS`.
6. Senha informada pelo admin é ignorada para Investidor.
7. Reset/troca de senha do Investidor é recusado.
8. Investidor não chama Stripe.
9. GETs de conteúdo e interfaces continuam acessíveis.
10. POST/PUT/PATCH/DELETE operacionais retornam 403.
11. Exceções de escrita: apenas conclusão do tour/fechamento de aviso.
12. OAuth de Agenda é bloqueado mesmo quando iniciado por GET.
13. CorVIA Mail entrega somente dados sintéticos.
14. Nenhum endpoint real de Mail360 é chamado para Investidor.
15. Prescrição pode ser visualizada, mas criar/emitir/assinar/enviar é 403.
16. Documentos podem ser visualizados, mas gerar/baixar recém-gerado/assinar/enviar é 403.
17. Exportação mostra catálogo, mas gerar/enviar PDF é 403.
18. Agenda é visualizável, mas conectar/criar/editar/sincronizar é 403.
19. Convidado continua com suas regras próprias e não herda o read-only do Investidor.
20. Assinante normal permanece sem regressão.
