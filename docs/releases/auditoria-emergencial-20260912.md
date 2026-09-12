# Release emergencial da auditoria — 12/09/2026

Autorização do proprietário: “Deploy emergencial”, após a conclusão das correções locais. Nesta execução não serão disparadas suítes de CI backend nem repetidas verificações já concluídas.

## Escopo

Correções dos 51 achados da auditoria, preservando a estrutura visual existente:

- CI-01 a CI-21: convites, administração, recuperação de acesso, Mail, Chat, WhatsApp, exportação e publicação de arquivos estáticos.
- CLI-01 a CLI-15: vínculo e troca de paciente, prontuário, prescrições, documentos, agenda, round e finalização de checklist.
- CIE-01 a CIE-04: respostas científicas atrasadas, interações, limites de entrada das calculadoras e largura do Tudo com Tudo.
- PUB-01 a PUB-06: validação pública, retorno ao destino após login, páginas jurídicas e títulos do navegador.
- VIS-01/VIS-02, EXP-01/EXP-02 e QA-01: contraste, enquadramento, exportações e cobertura do fluxo de assinatura.

Revisões cruzadas também corrigiram a corrida entre confirmação e revogação de convite, a recontratação do Mail após cancelamento e a criação de tarefas/lembretes pessoais sem paciente fictício. Consultas clínicas continuam exigindo paciente.

## Evidência anterior à publicação

- TypeScript e compilação Vite de produção aprovados. O último build incorpora a regra final de contraste dos títulos científicos.
- Sintaxe de 58 arquivos Python verificada em memória, sem instalação ou execução de suíte backend.
- Sete páginas em dois temas e duas larguras, mais uma tela de 1600 pixels: 29 estados locais medidos sem extrapolação horizontal.
- Verificações funcionais focais de rotas, revisão de formulários, identidade, permissões e respostas atrasadas aprovadas com dados sintéticos.
- Calculadoras: 71 resultados de referência preservados e 1.262 entradas inválidas recusadas.
- Publicação estática: seis cenários focais aprovados; configuração Caddy validada e comportamento HTTP de arquivo existente/ausente confirmado localmente.
- Exportações PDF/PPTX inspecionadas visualmente; links de PDF, DOCX e PPTX verificados. DOCX não foi renderizado em editor nativo.

As evidências completas e capturas permanecem no diretório local da auditoria. Capturas de sessões e arquivos temporários não integram o pacote de produção.

## Procedimento desta execução

O commit contém `[skip ci]` para não disparar as suítes automáticas e `[code-only-deploy]` para preservar o corpus. O workflow emergencial existente recebe o SHA exato de main. A opção de código mantém build, backup, migrações, readiness, rollback e confirmação HTTPS, mas não republica/reclassifica/reindexa conteúdo científico.

Não há nova variável de ambiente, coluna, tabela ou dependência de backend nesta correção. Os novos módulos de serviço acompanham a imagem pelo processo de build existente.

## Limites

Compilação e simulações não comprovam concorrência PostgreSQL real, liquidação Stripe, entrega de mensagens ou assinatura por provedor externo. A publicação será confirmada por SHA, disponibilidade e arquivos públicos; nenhum pagamento, mensagem ou documento de paciente será emitido como teste.
