# Revisão científica e interface — 09/09/2026

Pacote fechado para publicação autorizada: **697 arquivos-fonte revisados** — 270 do Claude e 427 do Grok. A produção posterior do Work está fora deste pacote.

- 716 registros publicáveis nos módulos nativos e na biblioteca.
- 2256 relações explícitas e rastreáveis para Tudo com Tudo; nenhum registro desconectado.
- 7 versões redundantes consolidadas nos respectivos registros canônicos, preservando as fontes originais.
- 14 materiais educativos ao paciente e 12 trilhas narrativas convertidos também para seus módulos nativos, além dos registros estruturados recebidos.
- Fontes primárias, DOI/PMID, denominadores, desenho, interpretação, contraindicações e limites da evidência conferidos. Corrigidas extrapolações, doses, referências equivocadas e dados não sustentados.
- Metadados, temas canônicos, títulos, resumos, slugs e vínculos internos conferidos. A revisão foi editorial e bibliográfica assistida por Codex; não é assinatura de revisão médica humana.

As correções de interface preservam a estrutura aprovada: paleta clara, imagens realistas de Ciência e Ensino nos dois temas, deslocamento com data/hora, timeline e contexto sem linhas indevidas, espaço para ações flutuantes e enquadramento da definição clínica. Build de frontend e conferência visual dirigida concluídos; sem suítes de CI/backend.

A publicação usa somente este pacote, com backup das linhas científicas afetadas, preservação de revisões anteriores, transação atômica e validação das relações. A atualização do índice semântico também fica restrita às identidades deste pacote; não há reconcile, prune ou varredura da nova produção.

Estado deste relatório: preparado; o resultado efetivo da execução será registrado em `publication-result.json` e `rag-result.json` no diretório da release.

SHA-256 do pacote: `9c5a671b37558f3bb71ac338d9069845ccc95c373f25bf22a4d474f71a9c92c9`.

## Execução

Executar no backend instalado, passando o SHA-256 acima:

```sh
python /tmp/publish_scientific_release_20260909.py /tmp/reviewed-content.json --sha256 HASH --check
python /tmp/publish_scientific_release_20260909.py /tmp/reviewed-content.json --sha256 HASH --apply
python /tmp/index_scientific_release_20260909.py /tmp/reviewed-content.json --sha256 HASH
```
