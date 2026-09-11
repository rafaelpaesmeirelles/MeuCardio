# Publicação e importação Cardiol — 11/09/2026

Produção confirmada em d48df1a9f219469e3ea5e280bd839068526e6286. Deploy certificado 34544801881 concluído com sucesso. Todos os seis gates obrigatórios passaram no mesmo SHA. Backend completo e focado não executados conforme instrução expressa; nenhuma declaração de reutilização de certificados. 252 testes científicos locais passaram em 10,73 s.

## Importação aplicada

13 originais: cinco registros criados e oito originais anexados. Zero chamadas pagas e zero mudanças clínicas pelo importador. Todos ficaram original_ready. A tentativa inicial no backend foi revertida ao encontrar seu volume corretamente somente-leitura, antes de publicar registros. A única transação concluída foi executada pelo serviço scientific-publication-library-worker, que já tem acesso de escrita. Nenhuma permissão ou montagem foi ampliada. Não repetir --apply para obter status: usar --database-plan.

Comando operacional correto, dentro do serviço da biblioteca:

```sh
docker exec -e PYTHONPATH=/app meucardio-scientific-publication-library-worker-1 python /app/scripts/import_cardiol_release.py --release-dir /tmp/corvia926-release --apply
```

## Verificação em produção

O script verify-originals-and-search.py completou as 13 verificações de elegibilidade pública, hash do original, leitura original-text, estado original_ready e indicação original_pt sem tradução gerada. A consulta global do DOI 20250615 também passou. Depois parou na expectativa excessiva de encontrar o original separado de FA nos primeiros 100 resultados. Por isso seu relatório final não foi gerado e essa execução não é apresentada como totalmente aprovada.

A verificação complementar registrada em search-verification.json confirmou: FA encontrada exatamente uma vez pelo filtro publicacao_original; a diretriz brasileira de FA já presente na primeira página global fornece o original importado em suas fontes; errata encontrada na busca global. Não houve alteração de ranking ou de relações clínicas nesta conferência. O código de verificação complementar foi preservado e concluiu com exit 0.

A suposição intermediária de representação canônica/deduplicação para FA não se confirmou: a consulta canônica retornou vazia. A explicação comprovada é o recorte da primeira página, com acesso bibliográfico funcional pela diretriz. Isso não certifica relevância ideal de toda consulta nem todos os 12.549 conteúdos.

Verificação por serviços/handlers reais em transação somente-leitura; não equivale a navegação autenticada em produção. A certificação RC2 e a visual foram realizadas no SHA final antes da publicação. O endpoint público de readiness confirmou banco e Redis saudáveis.

## Limites preservados

Dois Framingham históricos internos; PREVENT, SCORE2, SCORE2-OP e SCORE2-Diabetes como referências oficiais externas. A calculadora própria da SBC permanece pendente de endereço funcional validado. PREVENT nativo depende do acordo de integração AHA, que não foi aceito pelo sistema.

12 originais XML JATS e uma errata PDF, com leitura textual em português. Figuras e suplementos externos não foram baixados; tabelas e fórmulas têm representação textual e aviso. Nenhum dos 13 novos itens recebeu resumo por IA; não há resumo editorial nativo nesses arquivos. POCUS 20260222 não foi importado por falta de original confirmado. Não houve aprovação automática de tratamento ou conduta.
