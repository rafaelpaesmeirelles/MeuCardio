# Contratos de frontend e orçamento de documentos — 2026-09-09

## Correção da ordem CSS sem alteração da cascata visual

Antes: pending-fixes → clinical-form-control-contrast → cardiology-spaces-light-mode → corvia-daylight-palette.
Depois: pending-fixes → corvia-daylight-palette (somente tokens) → clinical-form-control-contrast → cardiology-spaces-light-mode (inclui as dez regras visuais diurnas ao final).

A comparação PostCSS de todas as folhas importadas por main.tsx preservou exatamente os 4.739 nós de topo não comentados, exceto o bloco único de sete tokens diurnos movido antes do contrato escuro. Esses sete tokens mantêm nomes e valores e não possuem outra declaração nas folhas importadas. As dez regras visuais foram transferidas sem mudar seletores, declarações ou ordem relativa. Nenhuma referência @import/url foi transferida; os arquivos também pertencem ao mesmo diretório.

SHA-256 da sequência normalizada de nós, antes e depois **da reorganização**, antes dos ajustes de acessibilidade abaixo: `43c33761ccc203a3323bf6e23ceb2fc43a65e39e50b3d9853a6c019fe2bf117a`.

O gate de contraste permanece inalterado. Agora o contrato escuro precede imediatamente a folha clara, novamente a última folha importada.

## Ajustes mínimos de acessibilidade na paleta já aprovada

O teste ainda referenciava cores antigas. As expectativas foram atualizadas para o texto #18354b, secundário #49677b, azul #246ac1 e fundos #e5f3f8/#e2eff7, já existentes antes desta correção. Mantidos os limiares de 4,5:1 para texto e 3:1 para controles, sem arredondamento permissivo.

A atualização revelou dois desvios reais sobre #e2eff7. A correção altera somente uma unidade do canal verde sRGB em cada cor, somente na folha clara:

| Uso | Antes | Depois | Razão antes | Razão depois |
| --- | --- | --- | --- | --- |
| Violeta usado em texto | #7957c8 | #7956c8 | 4,469356:1 | 4,505490:1 |
| Borda de controles | #81899e | #81889e | 2,984545:1 | 3,012942:1 |

O placeholder #626c82 permanece igual. Sua comparação usa o fundo branco efetivo dos formulários, obrigatório no CSS; o teste agora verifica tanto o vínculo ao fundo branco quanto a cor do placeholder e exige 4,5:1 nessa combinação real. Não se removeu requisito de contraste, isolamento do tema, acessibilidade ou preservação dos elementos visuais. A prova de equivalência da reorganização não implica identidade das duas correções cromáticas posteriores.

## Cobertura das rotas

App.tsx e clinicalRouteRegistry.ts já continham os mesmos 76 padrões autenticados na base 1c8454d1; o contador rígido 75 estava desatualizado. O contador foi corrigido para 76, mantendo duplicatas proibidas, paridade exata e validação de todos os espaços e pais. Distribuição: consultório 16, hospital 10, ensino 12, pesquisa 12, gestão 22 e home 4.

A assinatura já existia como caminho, mas seu registro ainda dizia alias do Tour. Agora corresponde à página real: Gestão → conta → Minha conta, sem redirecionamento. O gate ganhou verificações explícitas dessa associação e da renderização de Assinatura em App.tsx.

## Orçamento de documentos particulares

ScientificDocumentAI calcula a cotação gratuita no endpoint /orcamento depois de salvar/selecionar um documento. Exibe teto em créditos, saldo disponível, inclusão da eventual tradução integral e cobrança apenas do uso efetivo. Só o botão de confirmação envia quote_id e approved_max_credit_centavos para /analisar.

Saldo insuficiente bloqueia a confirmação e oferece o link para créditos/limite. Orçamento expirado exige recálculo. Trocar de documento, fazer upload ou iniciar a análise descarta a cotação; falhas exigem novo orçamento. A validação definitiva de saldo, validade, conteúdo e uso único permanece no backend. Erros financeiros do endpoint usam 409, preservando a tela; não acionam o redirecionamento global de assinatura 402. Não foram feitas chamadas pagas para verificar a UI.

## Verificação focal

- check-form-control-contrast.mjs: passou.
- check-cardiology-spaces-route-coverage.mjs: passou, 76 padrões em paridade exata.
- check-cardiology-spaces-light-mode-contract.test.mjs: 10/10 passaram.
- check-scientific-document-budget.test.mjs: 4/4 passaram; cotação sem análise paga, confirmação com teto exato, saldo insuficiente, expiração, troca de documento e descarte após erro.
- TypeScript tsc -b --pretty false: passou, 55,53 s.
- git diff --check: passou.

Sem commit, push ou alteração de produção por esta subtask.
