# CorVIA — Miniuniverso canônico aprovado em 04/09/2026

## Status
PADRÃO VISUAL APROVADO. Esta referência substitui as tentativas anteriores do miniuniverso interno.

## Referência visual
O padrão é o mockup claro/escuro aprovado pelo usuário em 04/09/2026: galáxia espiral azul/ciano, núcleo luminoso, detalhes definidos, presença visual semelhante nos dois temas e sem aparência de borrão.

## Regras congeladas
- Não alterar layout, grid, footprint do header, posição da marca, busca, avatar ou tabs para acomodar o miniuniverso.
- O miniuniverso deve ser discretamente maior que a versão anterior, mas crescer por `transform: scale`, mantendo o footprint.
- Movimento: rotação anti-horária lenta, 120 s por volta, por rotação interna/deprojetada da textura; o disco permanece horizontal e não tomba nem fica vertical.
- Asset canônico: `/spaces/galaxy-approved-canonical.webp`.
- Claro: preservar detalhes azul/ciano, contraste alto, sem halo branco lavado e sem blur decorativo.
- Escuro: preservar núcleo luminoso e glow azul/ciano um pouco mais presente.
- A cor do glow acompanha discretamente o ambiente ativo: Consultório/ciano, Hospital/azul, Ensino/violeta, Pesquisa/rosa, Gestão/teal.
- O mesmo componente deve ser usado em todas as páginas internas que exibem miniuniverso.

## Implementação
Componentes: `frontend/src/components/GalaxyThemeToggle.tsx` + `frontend/src/components/MiniUniverseCanvas.tsx`.
CSS canônico: bloco `CANONICAL 04/09 — miniuniverso aprovado pelo usuário` no fim de `frontend/src/styles/corvia-internal-final-approved-20260904.css`.

## Regra de manutenção
Qualquer alteração futura deve preservar esta referência, salvo nova aprovação explícita do usuário.
