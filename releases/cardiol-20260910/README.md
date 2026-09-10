# Cardiol/SBC — aquisição de originais atuais, 10/09/2026

Escopo: diretrizes e posicionamentos SBC/Arquivos Brasileiros de Cardiologia publicados entre 2025 e 10/09/2026. Busca por título/tipo, DOI, verificação de versão e comparação com referências publicadas e arquivos originais na produção. Não é uma cópia integral de todo o portal Cardiol.

Foram examinados 14 candidatos: 8 já constavam em referências publicadas; nenhum tinha original armazenado na comparação inicial. Os demais não foram encontrados nessas referências. Citação não foi confundida com posse do texto integral.

13 originais foram baixados: 12 arquivos JATS/XML em português, com tradução editorial inglesa, e 1 PDF de errata. São arquivos de editor/repositório, não novos textos clínicos produzidos pelo CorVIA. Preservam bytes e SHA256; imagens binárias e suplementos externos aos JATS não foram baixados.

## Conteúdo baixado

- [10.36660-abc.20250615.xml](originals/10.36660-abc.20250615.xml)
- [10.36660-abc.20250618.xml](originals/10.36660-abc.20250618.xml)
- [10.36660-abc.20250619.xml](originals/10.36660-abc.20250619.xml)
- [10.36660-abc.20250620.xml](originals/10.36660-abc.20250620.xml)
- [10.36660-abc.20250621.xml](originals/10.36660-abc.20250621.xml)
- [10.36660-abc.20250624.xml](originals/10.36660-abc.20250624.xml)
- [10.36660-abc.20250640.xml](originals/10.36660-abc.20250640.xml)
- [10.36660-abc.20260215.xml](originals/10.36660-abc.20260215.xml)
- [10.36660-abc.20260216.xml](originals/10.36660-abc.20260216.xml)
- [10.36660-abc.20260220.xml](originals/10.36660-abc.20260220.xml)
- [10.36660-abc.20260221.xml](originals/10.36660-abc.20260221.xml)
- [10.36660-abc.20260223.xml](originals/10.36660-abc.20260223.xml)
- [10.36660-abc.20260565.pdf](originals/10.36660-abc.20260565.pdf)

## Proveniência e integridade

- `discovery.json`: metadados primários e licenças, somente do artigo original; referências com aviso editorial separadas.
- `acquisition.json` e `source-recovery.json`: URLs de aquisição e licenças.
- `checksums.json`: tamanho e SHA256 dos 13 arquivos.
- `corpus-comparison.json`: comparação por DOI e caminhos de referências no repositório, para integração Tudo com Tudo.
- `runtime-compatibility.json`: bloqueios observados no parser de produção, antes da correção NISO ALI.

## Correção de importação incluída

O parser ignorava a licença como texto em `ali:license_ref`, campo padronizado pelo NISO/JATS. A correção aceita esse texto apenas no namespace exato e nas permissões do artigo, com a mesma lista de URLs CC-BY/CC0, sem inferência por texto genérico. Licenças futuras/malformadas não são aceitas.
Fonte: https://jats.nlm.nih.gov/publishing/tag-library/1.4/element/ali-license_ref.html
20 testes isolados aprovados em 0,26 s; revisão independente favorável. Sem backend CI completo ou focal.

## Integração preparada nesta rodada

- Novo leitor de originais separado da tradução paga: lê a raiz JATS no idioma original, sem concatenar subartigos traduzidos. Limite próprio de 8 MiB/2 milhões de caracteres; DOI, hash, licença e segurança XML verificados. Fórmulas/tabelas são representadas em texto com aviso, mantendo os bytes originais para consulta.
- Os cinco artigos com licença genérica no XML tiveram CC-BY 4.0 confirmada por depósito do editor no Crossref ou por XML vinculado na página editorial. Evidências em `license-confirmation.json`; bytes originais preservados.
- `import-manifest.json` fixa os 13 arquivos e suas evidências. Importador offline por padrão, plano de banco somente leitura e aplicação explícita pós-deploy. Original já adquirido/processamento pago/estado protegido permanecem intactos.
- Originais em português ficam fora da fila paga (`original_ready`); a interface oferece “Texto integral em português”, sem alegar tradução por IA. PDF é servido autenticado como PDF, e nunca passado ao parser XML. A errata também possui texto integral extraído offline por pdftotext -layout (1 página), fixado por hash em readable/, para leitura interna sem depender do visor PDF do navegador. A API confere o hash do PDF e o hash próprio do texto.
- Nenhum dos 12 JATS possui abstract editorial principal em português: os resumos não foram inventados nem marcados disponíveis.
- POCUS 2026 (`10.36660/abc.20260222`) segue sem original/licença verificáveis. Sua aquisição continua pendente.
- Os arquivos ainda não foram importados/publicados no instante deste registro; resultado real de aplicação será registrado separadamente após a release.

## Revisão clínica

A errata SCC 2026 corrige autoria, instituições e conflitos de interesse; não altera recomendações clínicas. Manter vínculo bibliográfico com a diretriz 2025.
Tempestade elétrica e SCC citam artigos com avisos de retratação; isso não significa retratação dessas diretrizes. As referências específicas e os caminhos XML estão no manifesto para avaliação contextual.
Nenhuma conduta, fluxograma, emergência ou conteúdo clínico foi atualizado/aprovado automaticamente. Sugestões futuras de mudanças clínicas exigem fontes, antes/depois e aprovação individual do responsável na área administrativa existente.

## Operação

Aquisição HTTP gratuita; nenhuma chamada de IA nesta atividade. Banco, fila histórica `cost_unknown`, recibos, créditos, limites, workers e produção não foram alterados. Não acionar worker global para importar este lote: ele também traduz documentos pagos de outros itens.
