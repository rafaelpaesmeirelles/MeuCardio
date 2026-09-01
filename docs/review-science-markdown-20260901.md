# Revisão científica dos Markdown do PR #796 — 01/09/2026

## Escopo

- Base exata: `2411c3dde9739129acd9c7fb3c9dee8271581f86`.
- Universo: 89 arquivos `content/**/*.md` adicionados ou modificados pelo PR #796 em relação ao merge-base `d17ef290505b35f62328f5d4eb40c4c932762cd8`.
- Situação inicial: 72 documentos com `review_status: revisado`, 17 com `review_status: pendente_revisao` (14 sem aspas e 3 com valor entre aspas), nenhum com `published` e um documento legado com nota que contradizia o status revisado.
- Situação final: 89/89 com `review_status: revisado`, `published: true` e nota explícita de revisão concluída; nenhuma quarentena editorial remanescente neste lote.

## Método

1. Inventário determinístico dos arquivos tocados pelo PR, sem incluir outros Markdown do repositório.
2. Validação do frontmatter, unicidade de slug, presença e tipo de `source_refs`.
3. Resolução em lote de todos os PMIDs por PubMed E-utilities e comparação dos pares PMID/DOI com o DOI canônico do registro.
4. Leitura dirigida dos documentos ainda pendentes e rechecagem das afirmações de maior risco clínico: doses, limiares, população, sequência terapêutica, contraindicações e força da recomendação.
5. Confronto com ensaios primários, diretrizes de sociedades e fontes oficiais quando uma síntese podia induzir extrapolação clínica.
6. Auditoria dos links Markdown `/biblioteca/...` e inspeção de corrupção textual introduzida por substituição automática.
7. Promoção editorial somente após as correções e repetição dos checks.

## Correções materiais

### Terapia intensiva

- **Profilaxia de sangramento por estresse / REVISE:** separada a evidência do ensaio (redução de sangramento em pacientes ventilados) da diretriz SCCM/ASHP 2024. Ventilação mecânica isolada deixou de ser apresentada como indicação universal; coagulopatia, choque e hepatopatia crônica permaneceram como fatores prováveis, com consideração de alimentação enteral e suspensão quando o risco resolve.
- **Crise adrenal:** corrigido o limiar de risco para insuficiência adrenal induzida por glicocorticoide para exposição superior a 3–4 semanas e acima do equivalente fisiológico aproximado de 4–6 mg/dia de prednisona/prednisolona, conforme diretriz conjunta ESE/Endocrine Society 2024 (PMID 38714321). Corrigida a inversão sobre interferência em imunoensaio: dexametasona, e não hidrocortisona, preserva em geral a interpretação do cortisol. Cobertura de estresse deixou de ser automática após qualquer exposição remota.
- **Tempestade tireotóxica:** incluído o risco de colapso por betabloqueio em insuficiência cardíaca de baixo débito/choque cardiogênico; propranolol deixou de aparecer como obrigatório nesse fenótipo. Quando tolerado e necessário, esmolol/landiolol tituláveis foram delimitados como opções sob monitorização (PMID 41655224). A sequência tionamida–iodo foi limitada às causas com síntese hormonal ativa, sem extrapolá-la a tireoidite destrutiva ou hormônio exógeno.
- **Hipersensibilidade a contraste:** corrigido o PMID do capítulo de glucagon (`32644621`); anti-histamínicos e glicocorticoides deixaram de ser descritos como prevenção confiável de anafilaxia bifásica (PMID 32001253). Glucagon ficou delimitado como adjuvante de evidência limitada no paciente betabloqueado, sem substituir adrenalina ou suporte hemodinâmico. A prevenção foi atualizada para estratificação por gravidade, troca do agente e ausência de pré-medicação corticosteroide rotineira após reação leve, conforme consenso ACR/AAAAI 2025 (PMID 40326871).
- **Triquinelose:** removida a formulação absoluta de contraindicação em gestantes e menores de 2 anos. O texto agora distingue ausência de aprovação regulatória de proibição universal e exige avaliação individual de risco-benefício, preservando as doses oficiais do CDC.

### Doenças raras, cardiomiopatias e valvopatias

- **Doença de Wilson:** o PMID `20301685` foi corretamente atribuído ao GeneReviews de doença de Wilson; o capítulo de distúrbios `ATP7A` passou ao PMID correto `20301586`. O estudo pediátrico que não encontrou prolongamento do QT (PMID `29504323`), já discutido no corpo, foi incluído também em `source_refs` para fechar a proveniência estruturada.
- **Paraganglioma cardíaco:** aconselhamento/teste germinativo passou a ser oferecido por decisão compartilhada com painel multigênico, evitando restringir todos os casos apenas a SDHx.
- **Síndrome de Barth:** corrigidos os DOIs canônicos dos PMIDs `16847078` e `34355402`.
- **Síndrome de realimentação:** corrigidos os DOIs canônicos dos PMIDs `18390784`, `32047291` e `32388553`.
- **Doença de Gaucher tipo 3c:** corrigidos os DOIs canônicos dos PMIDs `7475546` e `7985893`.
- **Kearns–Sayre:** as publicações-irmãs da diretriz ESC em *European Heart Journal* e *Europace* foram separadas em duas referências, impedindo associação cruzada falsa entre PMID e DOI.
- **Loxoscelismo legado:** removida a afirmação não comprovada de ranking mundial de notificações para Brasil/Paraná. A alta carga regional ficou preservada, com limite explícito de que as fontes citadas não sustentam comparação mundial harmonizada. A nota contraditória de “aguardando revisão” foi substituída por revisão concluída.

### Integridade editorial

- Corrigidas 21 ocorrências em que uma substituição automática havia trocado indevidamente `todo/toda` por `revisado` no corpo clínico (`revisado paciente`, `revisado contexto`, `revisado o organismo`, entre outras).
- Relações e limitações apoiadas apenas por séries observacionais ou relatos raros foram mantidas com a incerteza já declarada, sem promovê-las a recomendações de diretriz.
- Não foram criadas referências, doses ou classes de recomendação sem fonte rastreável.

## Métricas finais

| Verificação | Resultado |
|---|---:|
| Documentos no lote | 89 |
| Slugs únicos | 89 |
| `review_status: revisado` | 89/89 |
| `published: true` | 89/89 |
| Nota de revisão concluída | 89/89 |
| PMIDs únicos declarados em `source_refs` e resolvidos no PubMed | 1.129/1.129 |
| Pares PMID/DOI divergentes após correção | 0 |
| Links Markdown `/biblioteca/...` resolvidos no inventário global | 1.467/1.467 |
| Erros de frontmatter YAML | 0 |
| Corrupções textuais remanescentes do padrão auditado | 0 |

## Checks reprodutíveis

```bash
# Lista canônica dos 89 arquivos
git diff --name-only \
  d17ef290505b35f62328f5d4eb40c4c932762cd8..ce40e82283e3a7e3fe21cb4958055b7a90066ddf \
  -- 'content/**/*.md'

# Gate científico local + PubMed (usar a lista acima em --paths-from)
python scripts/audit_scientific_publication.py \
  --paths-from /tmp/science-markdown-paths.txt \
  --verify-pubmed --strict

# Auditoria global de referências; para este lote, observar Document.body_md.link
python scripts/audit_tudo_com_tudo.py

# Higiene do patch
git diff --check
```

O arquivo temporário citado no comando do gate deve conter somente os 89 caminhos retornados pelo primeiro comando. A auditoria global de “Tudo com Tudo” também reporta pendências preexistentes em entidades JSON fora deste workstream; o campo relevante aos Markdown deste lote ficou integralmente resolvido (`Document.body_md.link: 1467/1467`).

## Limites preservados

- Doenças raras continuam apoiadas predominantemente por coortes pequenas, séries e relatos de caso quando esse é o melhor corpo de evidência disponível.
- Publicação editorial não converte inferência mecanística em causalidade nem substitui decisão clínica individual, diretriz vigente ou avaliação especializada.
- A verificação PubMed confirma existência e pareamento bibliográfico; a validade clínica foi tratada separadamente pela leitura dirigida descrita acima.
