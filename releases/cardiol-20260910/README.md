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

## Pendências para disponibilização no site

- Arquivos estão preservados neste lote para integração; NÃO estão importados no acervo público nem publicados em produção.
- O pipeline atual só adquire Europe PMC JATS; HAS foi recuperada diretamente no editor e a errata é PDF. Esses formatos/caminhos precisam do adaptador de importação.
- Entre os seis JATS iniciais com CC-BY 4.0 explícita, apenas Obesidade passa também os limites atuais de texto/fórmulas após a correção ALI. Cinco excedem 300 mil caracteres; SCC contém fórmulas. Nenhum limite foi removido nem texto truncado.
- Cinco artigos declaram Creative Commons Attribution sem versão/URI no XML; a versão precisa ser confirmada antes do caminho comercial automatizado.
- O parser atual concatena português original e inglês editorial. Não traduzir novamente para português nem cobrar IA desnecessária por esses originais.
- POCUS 2026 (`10.36660/abc.20260222`) permanece sem original/licença verificáveis; o DOI informado pelo PubMed retornou 404 no resolvedor/Crossref.

## Revisão clínica

A errata SCC 2026 corrige autoria, instituições e conflitos de interesse; não altera recomendações clínicas. Manter vínculo bibliográfico com a diretriz 2025.
Tempestade elétrica e SCC citam artigos com avisos de retratação; isso não significa retratação dessas diretrizes. As referências específicas e os caminhos XML estão no manifesto para avaliação contextual.
Nenhuma conduta, fluxograma, emergência ou conteúdo clínico foi atualizado/aprovado automaticamente. Sugestões futuras de mudanças clínicas exigem fontes, antes/depois e aprovação individual do responsável na área administrativa existente.

## Operação

Aquisição HTTP gratuita; nenhuma chamada de IA nesta atividade. Banco, fila histórica `cost_unknown`, recibos, créditos, limites, workers e produção não foram alterados. Não acionar worker global para importar este lote: ele também traduz documentos pagos de outros itens.
