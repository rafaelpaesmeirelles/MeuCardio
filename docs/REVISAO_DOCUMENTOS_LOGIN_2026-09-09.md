# Revisão de documentos e login — 09/09/2026

## Documentos ao paciente

- Corrigida a quebra de linhas e a restauração da fonte após cada página. Textos longos, URLs, títulos, posologias, quantidades, observações e orientações passam a respeitar as margens e continuar nas páginas seguintes.
- Cabeçalho clínico unificado: CorVIA à esquerda, logo profissional no centro e identificação pessoal/profissional à direita. Aplicado aos PDFs clínicos, receitas comuns e controladas, materiais ao paciente, exportações pessoais em PDF/Word e impressão HTML.
- Receitas controladas preservam as duas vias, campos e validações existentes. Itens extensos continuam em páginas adicionais sem cobrir o quadro de assinatura.
- Rodapés e conteúdo dos PDFs assináveis reservam a área do carimbo digital.
- Documentos gerados e seu histórico apresentam a escolha explícita de assinatura. A assinatura pendente impede o envio, também no backend; falhas permitem nova tentativa. Arquivos já emitidos mantêm método e bytes originais.
- A impressão legada identifica a assinatura manual e oferece encaminhamento para revisão e assinatura digital no receituário.
- Orientações de medicamentos são preservadas na resolução, no snapshot e no PDF.
- Exportações PowerPoint foram verificadas quanto à retenção do texto editável; sua composição visual existente foi preservada.

## Login aprovado

- Formulário desktop claro/escuro em faixa horizontal fina na parte inferior; adaptação própria para notebooks.
- Universo reduzido, coração discretamente ampliado, galáxia clara suave e fundo escuro sem pontilhado.
- Disco galáctico normalizado antes da rotação, mantendo sua inclinação e proporção. Login claro gira no sentido anti-horário; miniuniversos internos giram lentamente no sentido horário. Preferência de movimento reduzido respeitada.
- Conferência visual em desktop e celular, nos dois temas. Versão aprovada pelo solicitante.

## Validação concluída antes da autorização de deploy

- 43 testes isolados de backend aprovados: geometria, paginação, retenção de texto, cabeçalhos, exportações, regras do receituário, assinatura criptográfica e bloqueios de envio.
- 4 testes do componente real de finalização aprovados: assinatura A1, falha de assinatura, assinatura externa pendente e reabertura de documento assinado.
- TypeScript e build de produção aprovados. Permanece o aviso de tamanho de alguns chunks.
- Dois PDFs demonstrativos, com duas páginas cada, renderizados e inspecionados visualmente. Sem dados reais, medicamentos ou validade clínica.
- Não houve envio a pacientes nem teste com certificado pessoal real. Os testes locais foram isolados, sem uso do banco de produção.

## Publicação autorizada

O solicitante autorizou publicar após concluir os ajustes, sem CI de backend e sem repetir testes. A publicação usa o fluxo direto existente, acionado manualmente para o SHA aprovado, com backup, build e checagens de disponibilidade do próprio deploy. O commit usa `[skip ci]` para esta publicação; a política normal de CI não foi desativada.
