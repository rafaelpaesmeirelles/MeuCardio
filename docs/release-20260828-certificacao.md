# Certificação do release consolidado — 28/08/2026

Este arquivo registra o corte final do release `release/all-pending-20260828` antes dos gates completos e do merge em `main`.

## Correções transversais confirmadas

- Catálogo canônico de doenças composto por base + fragmentos + correções, sem allowlist editorial temporária.
- Perguntas do assistente normalizadas no loader canônico: registros legados com `assistant_questions.text` são convertidos para `label`, removendo a chave incompatível com a UI.
- Rota `/excluir-conta` incluída no inventário funcional e na navegação canônica visível.
- Sobreposições legítimas de `related_document_slugs` documentadas nos contratos Tudo com Tudo do corpus consolidado.
- Correções clínicas dirigidas preservadas, incluindo cuidados paliativos cardiovasculares, TGA fetal e taquicardia supraventricular fetal.
- Workflows temporários usados na preparação do release removidos antes deste corte.

## Conteúdo incluído

O release agrega produção científica previamente revisada, a produção noturna consolidada de 28/08/2026, 17 protocolos de Cardiologia Intensiva/UCO, aprofundamentos de cardiopediatria, cardiogeriatria, gravidez, cardio-oncologia e cardiologia fetal, além das correções de runtime/acesso móvel e distribuição Android já preparadas na mesma branch.

## Política de publicação

O merge e o deploy só devem ocorrer se o SHA deste corte (ou correção posterior explicitamente certificada) passar os gates completos aplicáveis, incluindo CI, RC2 Acceptance, Visual QA, inventário do corpus e reconciliação do banco. A produção deve confirmar o mesmo SHA em `/api/version`, além de `/api/health` e `/api/ready` saudáveis.
