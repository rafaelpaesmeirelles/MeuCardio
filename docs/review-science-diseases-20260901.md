# Revisão científica das doenças — 01/09/2026

## Resultado

A revisão partiu exatamente de `8226e364aa140631b656226db9d2b0cf56ac8c1a` e cobriu 161 registros: as 154 doenças acrescentadas entre `d17ef290505b35f62328f5d4eb40c4c932762cd8` e o PR científico, mais as sete doenças legadas cuja nota editorial contradizia o status. Nenhum registro fora desse conjunto foi alterado.

| Estado editorial | Antes | Depois |
|---|---:|---:|
| Novas, `pendente_revisao` + `published:false` | 121 | 0 |
| Novas, `revisado` + `published:false` | 33 | 0 |
| Legadas, `revisado` + `published` ausente | 7 | 0 |
| `revisado` + `published:true` | 0 | 161 |

As 154/154 doenças novas e as 7/7 legadas ficaram com nota explícita de revisão concluída. As notas anteriores e a proveniência foram preservadas como histórico. A nota final registra o limite da revisão: quando não havia texto integral público, foram usados metadados e resumo/XML; relatos e séries de doenças raras continuam identificados como evidência de baixa certeza e não foram convertidos em recomendação formal.

## Conferência científica e bibliográfica

Cada um dos 161 registros possui conteúdo não vazio para resumo, apresentação, diferenciais, exames, sinais de alarme, fluxo ambulatorial, fluxo de emergência, referências e URLs. A coerência entre diagnóstico, manejo, monitorização, populações especiais e referências foi reavaliada contra os títulos e resumos disponíveis, diretrizes declaradas e fontes primárias do próprio conjunto.

| Métrica final | Resultado |
|---|---:|
| Entradas em `source_refs` | 1.841 |
| Menções a PMID | 1.822 |
| PMIDs únicos | 1.795 |
| PMIDs resolvidos pelo NCBI E-utilities | 1.795/1.795 |
| Registros PubMed do tipo artigo | 1.766 |
| Artigos com resumo/XML disponível | 1.619 |
| Registros NCBI Books/GeneReviews/StatPearls | 29 |
| URLs declaradas | 1.926 (1.896 únicas) |
| URLs PubMed por ocorrência | 1.851 |
| URLs suplementares DOI/NCBI/OMS/MS/periódicos | 75 |
| Registros sem URL | 0 |
| PMIDs sem URL PubMed canônica no próprio registro | 0 |

O reconhecimento de PMID usa 5 a 9 dígitos. Isso inclui corretamente o PMID histórico `54226`, que seria omitido por validadores restritos a 6–9 dígitos.

### Correções encontradas

1. **Hemocromatose cardíaca:** cinco PMIDs apontavam para artigos sem relação com a citação. Os identificadores efetivos foram conferidos por título, periódico e DOI; a revisão final removeu também as cinco URLs antigas, que haviam permanecido indevidamente ao lado das URLs corretas:

   | Citação | PMID incorreto | PMID correto |
   |---|---:|---:|
   | Brissot et al., *Haemochromatosis* | 29653732 | 29620054 |
   | EASL, HFE hemochromatosis | 20471109 | 20471131 |
   | AHA, cardiovascular function in β-thalassemia | 23775113 | 23775258 |
   | Pennell et al., deferasirox and cardiac iron | 20101026 | 19996412 |
   | Kremastinos & Farmakis, iron-overload cardiomyopathy | 22105196 | 22083147 |

2. **Metadados de citação:** foram corrigidos título/autoria de PMID já válido em porfiria aguda (`15767622`), doença de Wilson (`20301685`), lipodistrofia congênita generalizada (`27766009`), glucagon/StatPearls (`32644621`) e Gaucher tipo 3c (`11148530`). Três URLs que haviam sido inseridas indevidamente dentro de `source_refs` foram removidas; continuam preservadas em `source_urls`.
3. **Porfiria aguda:** a redação foi corrigida para não sugerir glicose isolada como equivalente à hemina em ataques moderados/graves. Hemina intravenosa é o tratamento específico precoce; glicose isolada fica limitada a ataque leve ou ponte até a hemina.
4. **Hipersensibilidade a contraste iodado:** a redação deixou de afirmar que toda reação grave é não-IgE. O texto agora distingue a nomenclatura histórica, reconhece mecanismos IgE e não-IgE e deixa explícito que glucagon é adjuvante possível no betabloqueado refratário, sem substituir adrenalina.
5. **Corrupção textual legada:** 13 campos continham construções como “em revisado paciente”, originadas por substituição editorial mecânica de “todo”. Todos foram restaurados para português clínico inequívoco, como “em qualquer paciente”, sem mudar a indicação.

## Vínculos documentais

No snapshot original `ce40e82283e3a7e3fe21cb4958055b7a90066ddf`, 67 das 154 doenças novas apontavam para `related_document_slugs` que não existem no índice Markdown atual. A correção anterior em `8226e364` já havia removido esses alvos quebrados.

- 93 relações estruturadas foram mantidas e três relações canônicas adicionais foram restauradas; 96/96 resolvem para um documento existente e têm correspondência clínica direta ou diferencial explicitamente descrito no corpo do documento.
- Os 67 alvos removidos foram confrontados com todos os frontmatters em `content/**/*.md`, nomes, aliases e títulos atuais.
- Dois registros tinham substitutos canônicos com nexo clínico explícito: `hipotermia-acidental` foi ligado ao protocolo e ao fluxograma canônicos de hipotermia/parada cardiorrespiratória ERC 2021; `saturnismo-cardiovascular` foi ligado ao documento canônico de exposição ao chumbo e risco cardiovascular. Resultado: **três relações restauradas em dois registros**.
- Os outros 65 alvos removidos continuam sem substituto clínico comprovado. Assim, 66 registros ficam sem `related_document_slugs`: esses 65 e síndrome POEMS, que já não possuía relação no snapshot original.

Não foi usado casamento por uma palavra genérica, similaridade de tema ou aproximação lexical. Restaurar um documento adjacente apenas porque compartilha “risco”, “pressão”, “insuficiência”, “agudo” ou outro termo inespecífico violaria a regra clínica do Tudo com Tudo.

O auditor completo no snapshot desta branch informa `SpecialtyDisease.related_document_slugs: 1447/1447` resolvidos. Ele também enumera 20 links no corpo de documentos Markdown para alvos ausentes; esses arquivos estão fora do escopo desta frente de doenças e foram encaminhados ao workstream exclusivo de Markdown.

## Verificações reprodutíveis

Validações locais executadas:

```bash
python -m json.tool doencas/metadados.json >/dev/null
git diff --check
python scripts/audit_tudo_com_tudo.py
```

O gate dirigido, executado sem banco, carrega o manifesto canônico e verifica o conjunto alvo, schema das perguntas, relações e URLs:

```text
PASS records=326 target=161 unique_pmids=1795 pmid_url_coverage=100% structured_links=96 restored_links=3 relation_types=protocolo,fluxograma,estudo assistant_schema=ok false_hemo_urls=0
```

Os dois módulos pytest mais próximos foram tentados, mas a fixture global exige PostgreSQL local em `127.0.0.1:5432`; os sete casos pararam no setup com `connection refused`, antes de qualquer teste. Não foi criado banco ou alterada infraestrutura para contornar esse bloqueio. As mesmas invariantes de manifesto e schema foram executadas diretamente, sem a fixture de banco, como mostrado acima.

Para reproduzir a composição exata do escopo:

```python
import json, subprocess

atual = json.load(open("doencas/metadados.json"))
base = json.loads(subprocess.check_output([
    "git", "show",
    "d17ef290505b35f62328f5d4eb40c4c932762cd8:doencas/metadados.json",
]))
legadas = {
    "erdheim-chester-disease-acometimento-cardiovascular",
    "doenca-de-behcet",
    "fibroelastoma-papilar-cardiaco",
    "sindrome-poems",
    "tumores-cardiacos-malignos-primarios",
    "cardiomiopatia-por-deficiencia-de-selenio",
    "cardiomiopatia-dilatada-por-hipocalcemia-grave",
}
slugs_base = {item["slug"] for item in base}
alvo = [
    item for item in atual
    if item["slug"] not in slugs_base or item["slug"] in legadas
]
assert len(atual) == 266
assert len(alvo) == 161
assert sum(item["slug"] not in slugs_base for item in alvo) == 154
assert all(
    item["review_status"] == "revisado" and item["published"] is True
    for item in alvo
)
```

## Conclusão

O lote fecha 154/154 doenças novas e 7/7 legadas sem quarentena. A publicação foi habilitada apenas depois da correção dos identificadores quebrados, da remoção das URLs inválidas, da reconciliação das URLs, das duas correções clínicas de segurança e da validação dos vínculos existentes. Três relações canônicas foram restauradas porque têm nexo clínico explícito; a ausência de substituto para os outros 65 documentos inexistentes foi mantida, em vez de criar associações por aproximação lexical.
