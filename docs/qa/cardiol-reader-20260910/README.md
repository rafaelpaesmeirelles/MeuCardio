# QA final do leitor original

Build TypeScript + Vite + PWA aprovado. A versão final elimina o iframe PDF e mantém a política CSP anterior. O original PDF continua disponível para download; a leitura interna apresenta texto extraído e verificado, com aviso explícito de extração e ausência de tradução por IA.

Dois casos finais de 360×900 (PDF extraído, claro/escuro), 12 verificações funcionais aprovadas, sem erros JavaScript, overflow horizontal global ou violações CSP. Fixtures com PDF e TXT reais da errata DOI 10.36660/abc.20260565, perfil fictício e APIs interceptadas. Downloads correspondem byte a byte ao original. Texto e aviso inspecionados nas capturas dos dois temas.

O resultado anterior de JATS e os 14 checks do protótipo estão preservados separadamente em `superseded-iframe-prototype/`. Aquele relatório inclui a falha do visor PDF que motivou a mudança de desenho; **não representa a implementação final**. A leitura JATS clara previamente validada permanece em `reader-jats-light.png`.

Nenhuma chamada de IA, banco ou backend real. Não houve CI backend. A validação de interface não substitui a conferência da publicação em produção. A diagramação original do PDF não é reproduzida.

Após as capturas, foi aplicado um ajuste pontual: textos originais são exibidos como texto simples (`white-space: pre-wrap; overflow-wrap: anywhere`), preservando indentação e símbolos sem interpretá-los como Markdown. Resumos e traduções mantêm Markdown. Este ajuste posterior não foi submetido a novo build/suite local por instrução do responsável; a compilação será coberta pelo gate frontend final. As capturas documentam o estado imediatamente anterior a esse ajuste de apresentação.
