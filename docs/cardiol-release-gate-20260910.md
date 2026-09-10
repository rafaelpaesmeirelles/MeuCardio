# Correção de registro do gate Cardiol

Run34542045764 do SHA f6703bdb: classificador e frontendbuild aprovados; Backend tests e Backend focused tests skipped; Backend risk gate falhou porque a nova SUITE_KEY não constava na lista nominal do workflow.

Correção: registrar as chaves exatas Cardiol e desta correção; manter recusa de chave desconhecida, política falha, execução de qualquer suíte ou falso reuso. Nenhuma alteração no código do aplicativo. 10 contratos locais aprovados em 0,332 s, incluindo execução do shell real extraído do workflow: aceita as duas chaves exatas e recusa chave desconhecida, política falha, falso reuso e execução de qualquer suíte. Revisão independente favorável de classificador, identidade PR927/tree, condições dos jobs e gate final. Nenhuma suíte backend foi executada.
