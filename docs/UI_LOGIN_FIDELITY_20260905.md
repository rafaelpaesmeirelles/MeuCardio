# Login: correção de fidelidade — 05/09/2026

Status: correção técnica verificada em preview; aceitação visual integral PENDENTE. Não declarar login restaurado nem liberar esta branch como visual final.

## Referência correta
Usar o conjunto final de 04/09, posterior às imagens antigas que traziam seletor de tema dentro do painel:
- `universo_corvia_cardiologia_conectada.png` — desktop escuro.
- `universo_corvia_uma_só_cardiologia.png` — desktop claro.
- `corvia_um_universo_de_cardiologia.png` — mobile escuro.
- `login_corvia_universo_da_cardiologia.png` — mobile claro.
As referências finais preservam o seletor compacto no topo, coração anatômico luminoso e cards com títulos. Não restaurar o conjunto anterior por engano.

## Correção isolada
Root ID exclusivo para impedir que os estilos legados sobrescrevam a geometria aprovada. Ensino acima do coração, título sem colisão, identidade acima do formulário, associação à direita no desktop e abaixo no mobile, VIA legível, campos com rótulos e espaçamento. A imagem fallback desaparece somente após o primeiro frame do canvas. Removida a galáxia sintética legada sob a imagem. Rotação horária no canvas preservada em 85 segundos; preferência de movimento reduzido respeitada inclusive quando alterada durante a sessão.

## Evidência desta rodada
Build TypeScript + Vite aprovado. Sete testes existentes de contrato aprovados. Verificação real Chromium: 320, 360, 390, 412, 768, 1024, 1440 e 1648 px, em claro e escuro: sem overflow horizontal, sem colisão dos cinco cards com coração ou título, identidade acima do formulário e apenas uma camada de galáxia. Testes adicionais verificam alternância de movimento reduzido / animação / movimento reduzido. Isso não equivale a autenticação bem-sucedida com conta real.

## Bloqueio visual ainda aberto
O asset existente `/spaces/corvia-galaxy-cameo.webp` continua mais azul e menos luminoso/difuso que as quatro referências finais. A fidelidade da galáxia e do fundo estelar ainda precisa ser resolvida e comparada visualmente. Os testes de geometria não certificam igualdade pixel a pixel nem encerram a aceitação visual.

## Escopo e reprodução
Não foram alterados autenticação, dados clínicos, Tudo com Tudo ou estilos internos. Novos trabalhos de timeline/PDF não foram iniciados nesta branch. Para o teste de navegador: iniciar um preview local em `127.0.0.1:18949` e executar `node frontend/scripts/check-login-fidelity-browser.mjs`, apontando `CORVIA_PLAYWRIGHT_MODULE` para uma instalação existente de Playwright, quando necessária. `CORVIA_QA_OUTPUT` define o diretório dos screenshots e relatório JSON.
