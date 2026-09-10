# Correção de registro do gate Cardiol

Run34542045764 do SHA f6703bdb: classificador e frontendbuild aprovados; Backend tests e Backend focused tests skipped; Backend risk gate falhou porque a nova SUITE_KEY não constava na lista nominal do workflow.

Correção: registrar as chaves exatas Cardiol e desta correção; manter recusa de chave desconhecida, política falha, execução de qualquer suíte ou falso reuso. Nenhuma alteração no código do aplicativo. Validação focal do shell real e contratos será registrada antes da integração.
