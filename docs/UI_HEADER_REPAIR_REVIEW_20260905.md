# Cabeçalho e escolha de espaço — correção pontual, 05/09/2026

Status: implementação isolada; publicação e aceitação visual final PENDENTES.
Base: bb13cf23f114aaf5e0791f1d7403c300a2522f9f.

## Alterações de aplicação
- Escolha de espaço até 900 px: padding superior de 138 para 34 px.
- Miniuniverso interno: rotação horária, preservados 120 segundos por volta e o asset existente.
- Até 900 px: pintura do miniuniverso contida na escala 1, sem mudar a área de toque.
- Entre 901 e 1350 px: primeira coluna intrínseca do cabeçalho reserva espaço para marca e miniuniverso, eliminando invasão da busca.
- A coluna da busca muda de largura nessa faixa; isso deve ser incluído na aprovação visual, não apresentado como geometria idêntica.
- Não alterados cards, conteúdo, cores, navegação, autenticação, Tudo com Tudo, dados clínicos ou login público.

## Verificações realizadas
Build TypeScript + Vite concluído com exit 0; persistem avisos de chunks grandes.
33 testes existentes de contrato passaram; não equivalem a testes funcionais com dados reais.
24 capturas Chromium: escolha/home, claro/escuro, 360/390/600/768/1024/1600 px.
Nenhuma colisão medida entre marca, canvas, busca e avatar; nenhum overflow horizontal ou pageerror.
O teste inicial de giro rejeitava qualquer ângulo negativo. Foi corrigido para medir progressão angular; revalidação dos mesmos 24 registros aprovou, sem modificar as capturas.

## Limitações e bloqueios
Fixtures usam usuário sintético, API simulada e fontes de fallback: não certificam tipografia final, pixels idênticos ou login real.
Larguras de fronteira 901/1350/1351 px ainda precisam de verificação dedicada.
A especificação antiga do miniuniverso descreve giro anti-horário; confirmar a orientação atual solicitada antes de publicação.
O login possui trabalho independente em fix/login-fidelity-20260905 (1139235e), não incorporado aqui; sua aceitação visual continua pendente.
Não iniciar nem contabilizar timeline/PDF nesta correção. Não ultrapassar gates de release nem publicar sem validar a referência aprovada.
