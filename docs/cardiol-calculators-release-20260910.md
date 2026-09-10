# Evidência da release Cardiol e calculadoras — PR926

PR925 integrado à main em a2eb46de, sem publicação intermediária. PR926 reúne o leitor/importador e mantém as calculadoras dessa integração.

## Validação local focal

- Calculadoras: 181 testes matemáticos/validação, incluindo vetores oficiais e valores enviados pelo formulário; build TypeScript/Vite/PWA aprovado. Navegador real: 6 casos mobile claro/escuro, 10 verificações funcionais. Evidências em docs/qa/cardiovascular-risk-20260910.
- Licenças ALI: 20 testes isolados; aceitação da URI textual NISO, sem relaxar identidade/URL/permissões.
- Leitor original/API: 19 testes isolados; os 12 XML reais passaram, maior texto 791.018 caracteres. Sem concatenar inglês nem liberar fórmulas para tradução paga.
- Manifesto nativo português: 3 contratos focais; sem rótulo de IA, sem URL de tradução fictícia, PDF/JATS corretos.
- Importador: 27 testes isolados e 2 casos adicionais do vínculo exato de errata; hashes e licença dos 13 originais conferidos offline. Recuperação exclusiva de falha de aquisição HAS: 2 testes adicionais aprovados, mantendo attempts=1. Texto extraído da errata: 2 testes adicionais aprovados (hash, DOI, integridade e armazenamento independente da tradução).
- Decisão de CI: 9 contratos locais para identidade exata de PR/tree, recusa de herança por outra release e ausência de certificado de testes backend.
- PDF/API: 2 casos focais adicionais aprovados para texto extraído com hash próprio e vínculo ao PDF original; manifesto PDF com prova ausente recusa read_url.
- Leitor frontend: build TypeScript/Vite/PWA aprovado; 2 casos PDF extraído claro/escuro e 12 verificações finais aprovadas, sem erros JavaScript, CSP ou overflow; download PDF idêntico e texto/aviso visíveis. Evidências em docs/qa/cardiol-reader-20260910. O iframe nativo apareceu vazio nos navegadores de teste e foi removido; CSP original foi preservada. A leitura usa texto extraído e o PDF original continua disponível para download.

## Limites que permanecem

PREVENT é acesso à ferramenta oficial; implementação nativa depende do acordo de integração AHA. A calculadora própria SBC permanece com endereço funcional não confirmado. SCORE2/SCORE2-OP/SCORE2-Diabetes são referências oficiais externas; Framingham nativo é histórico/comparativo, com desfechos/limitações próprios.

Os 13 originais não trazem resumo editorial principal em português nos XML: não inventado. POCUS não foi adquirido. Aquisição original não aprova nem modifica condutas. Nenhuma alteração de fonte histórica cost_unknown, wallet, modelo, crédito ou orçamento; nenhum teste com IA paga.

A instrução expressa “Sem novo ci backend” foi registrada pelo mecanismo já existente, restrita ao PR926 e sua integração exata. Todos os demais gates de release permanecem obrigatórios. Este documento não é um certificado de execução de CI backend.
