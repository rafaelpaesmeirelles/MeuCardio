# Retomada do login congelado — 05/09/2026

## Estado de publicação
**Implementação intermediária em QA. Não certificada como reprodução integral das referências; não publicar como login final aprovado.**
Continuação de `1139235ec3b1dd4f131a86ca26233e660dc87f9d` (PR #820), não do worktree antigo do PR #817.
O PR #817 já estava mesclado. Durante a retomada, a main avançou de `bb13cf23` para `eb4dfa00` por outra execução; nenhuma dessas publicações foi executada nesta retomada.

## Referências imutáveis recuperadas da Library
Os hashes abaixo foram calculados sobre os PNGs originais; nenhuma referência foi alterada.

| Arquivo | Dimensões | SHA-256 |
| --- | --- | --- |
| universo_corvia_cardiologia_conectada.png | 1672 × 941 | b20d250af20b11343a5f52e2ab0bd24894775be7d5dcf46f426c766d712c8297 |
| universo_corvia_uma_só_cardiologia.png | 1672 × 941 | 46ab8b18c6d65f46b68ccc88d68c4faaebd1836abaccc1b3369a4f40aa710082 |
| corvia_um_universo_de_cardiologia.png | 941 × 1672 | a5909b73e60cd9077fae83508635ff5c8902af552826cf5ae0e76f15ddb60266 |
| login_corvia_universo_da_cardiologia.png | 941 × 1672 | 11188b398c1f07faef4bc40739b82cbd3a3722c3a3c32d441b3e62e9edcebed9 |

## Correções implementadas nesta continuação
- Texto da referência: remover o termo intermediário `orbitando`; manter a quebra após `Gestão`.
- Placeholder da referência: `Sua senha`.
- Separar visualmente o cartão de autenticação e o cartão de solicitação de acesso no mobile, preservando os controles funcionais.
- Ajustar dimensões e espaçamentos móveis com escopo exclusivo do login, sem modificar as páginas internas.
- Conter o seletor e o selo de segurança no cabeçalho para evitar a sobreposição ao título.
- Ajustar a largura da barra de autenticação desktop, sem alterar o fluxo de autenticação.
- Atualizar a asserção da cópia para o texto dos PNGs congelados, com asserção negativa que impede restaurar `orbitando juntos` para satisfazer um teste antigo.

## Verificação executada nesta continuação
- `npm run build` (TypeScript e Vite): concluído. O aviso preexistente de tamanho de chunks continua; o orçamento global de bundle não foi certificado.
- Dois arquivos de testes de contrato do login: 15 testes aprovados. Nenhuma suíte backend foi executada.
- Capturas reais do build em Chromium: 1600×900 e 390×844, claro e escuro; zero pageerror e zero overflow horizontal nessas quatro capturas.
- Regressão do navegador existente: 320/360/390/412/768/1024/1440/1648 px × claro/escuro; 16 combinações aprovadas para colisões, overflow, tema, posição dos painéis e camada única da galáxia.
- Movimento reduzido → animação → movimento reduzido: aprovado.
- Evidência no servidor: `/root/corvia-ui-validation-20260905-0330/reference-resume/`, incluindo `report.json` e `geometry-motion/report.json`.
- As capturas são do frontend compilado em servidor efêmero ligado somente a 127.0.0.1. A API desse preview devolve 401 deliberadamente: **não é um teste de autenticação bem-sucedida ou de funções internas**.

## Bloqueios reais restantes
A comparação visual ainda reprova a reprodução integral. A galáxia do login (`corvia-galaxy-cameo.webp`) é achatada/azul e não reproduz a espiral luminosa lavanda com núcleo claro das referências. A distribuição/densidade do fundo estelar também diverge.
Os detalhes de acabamento dos controles e ícones e a equivalência de proporções/posicionamento desktop ainda não estão certificados. O sinal de ECG solicitado anteriormente foi preservado, não removido para forçar semelhança com uma imagem estática.
Nenhuma imagem nova foi inventada, nenhuma referência foi retocada e nenhum asset de QA foi elevado a referência aprovada. Não substituir cegamente pelo antigo `galaxy-approved-alpha.png` apenas por constar no handoff antigo.
A validação autenticada de home/escolha e do Tudo com Tudo não foi executada nesta continuação. A timeline de conhecimento e os trabalhos novos de PDF permanecem planejados, sem execução atribuída a esta correção.

## Publicação e concorrência
Não houve merge na main, deploy, migração, alteração de banco ou reinício de containers de produção nesta continuação.
O wrapper `ops/remote-deploy-entrypoint.sh` aceita `deploy-web`, mas chama `deploy.sh`, que inclui backend/migrações/corpus. **Não presumir que esse comando é um deploy somente de frontend.** Inspecionar e escolher o mecanismo apropriado somente após fechar a fidelidade visual.
Preservar as correções internas mais recentes de main. O commit paralelo `fdd21800` também muda o sinal da rotação interna; não levá-lo integralmente para produção como se fosse exclusivamente CSS de espaçamento.
Os scripts temporários e screenshots estão fora do worktree versionado. `frontend/node_modules` é apenas um symlink local de dependências e não deve entrar no commit.
