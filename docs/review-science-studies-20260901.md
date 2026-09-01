# Revisão científica dos estudos — 2026-09-01

## Escopo e método

Foram revisados os 170 registros acrescentados a `estudos/metadados.json` em relação ao baseline `d17ef290505b35f62328f5d4eb40c4c932762cd8`. A identidade bibliográfica foi confrontada em lote com o XML MEDLINE/PubMed por PMID. Para cada registro foram conferidos título, DOI, ano, desenho, população, intervenção/comparador, desfechos, números citados e limitações declaradas.

A consulta PubMed retornou 170/170 PMIDs. Havia abstract indexado para 169/170. O único registro sem abstract, DANFLU-2 (PMID 40884443), foi revisado no texto integral primário do JAMA Network Open (DOI `10.1001/jamanetworkopen.2025.36889`; https://jamanetwork.com/journals/jamanetworkopen/fullarticle/2838439).

O campo `review_note` de cada um dos 170 registros identifica o PMID e o DOI efetivamente usados, explicita a conclusão da revisão e limita a síntese ao material primário consultado. `fonte_producao`, URL, PMID e demais dados de proveniência existentes foram preservados.

Além do lote novo, oito registros canônicos legados passaram por revisão na deduplicação bibliográfica e três estudos legados usados como alvo explícito das evidências foram revisados contra o registro e o abstract/XML PubMed. Assim, o escopo de aprovação de estudos é de **181 registros**: 170 novos + 8 canônicos deduplicados + 3 alvos legados. Com a revisão e publicação formal da trilha PEITHO legada no commit `08ea0d35`, a contagem consolidada do release passa a **725 itens**. Os três alvos legados não possuíam `fonte_producao`; a ausência foi preservada, sem atribuir proveniência não documentada.

## Métricas do lote novo

| Métrica | Antes | Depois |
|---|---:|---:|
| Registros novos | 170 | 170 |
| PMIDs presentes e únicos | 170 | 170 |
| DOIs presentes | 166 | 170 |
| `review_status: pendente_revisao` | 170 | 0 |
| `review_status: revisado` | 0 | 170 |
| `published: false` | 170 | 0 |
| `published: true` | 0 | 170 |
| PMIDs recuperados no PubMed | — | 170/170 |
| Abstracts PubMed disponíveis | — | 169/170 |
| Textos integrais primários adicionais | — | 1/1 necessário |

## Estudos legados vinculados às evidências

| Estudo | Fonte primária conferida | Resultado da revisão |
|---|---|---|
| HELIOS-B | [PMID 39213194](https://pubmed.ncbi.nlm.nih.gov/39213194/) · `10.1056/NEJMoa2409134` | Título, fascículo de 2025, desenho, 655 participantes, intervenção, desfecho composto e estimativas confirmados. A inferência de benefício incremental sobre tafamidis foi removida, pois a associação não foi randomizada. |
| ATTRibute-CM | [PMID 38197816](https://pubmed.ncbi.nlm.nih.gov/38197816/) · `10.1056/NEJMoa2305434` | Título, ano de 2024, fase 3 duplo-cego, 632 participantes, desfecho hierárquico e win ratio confirmados; mantida a ausência de comparação direta com tafamidis ou vutrisirana. |
| STORM-PE | [PMID 41183181](https://pubmed.ncbi.nlm.nih.gov/41183181/) · `10.1161/CIRCULATIONAHA.125.077232` · `NCT05684796` | Título, fascículo de 2026, randomização, 100 participantes, redução de VD/VE e eventos em sete dias confirmados; mantidos o caráter substituto do primário, a falta de poder clínico e as duas mortes relacionadas ao TEP no braço CAVT. |

Os três registros ficaram com `review_status: revisado`, `published: true` e `review_note` específica. No cruzamento com o HEAD `7dc84eb35fb9b76f80662874d40714c0dc63986c` da revisão de evidências, **174/174 `Evidence.study_slug`** resolveram para um estudo e **174/174 PMIDs** coincidiram entre evidência e alvo; HELIOS-B, ATTRibute-CM e STORM-PE também foram confirmados como revisados, publicados e anotados.

Os commits temáticos foram divididos sem edição concorrente do JSON:

| Lote | Intervalo no lote novo | Quantidade | Commit |
|---|---:|---:|---|
| Cardiopulmonar/intervenção | 0–56 | 57 | `9ed87b0c14a66b5e82a38967cc91ab695f947257` |
| Prevenção/digital | 57–113 | 57 | `e3a0be1910f3448af26542f64d2802dbc4adb642` |
| Vascular/reabilitação | 114–169 | 56 | `49c638b8c840d9627e163781bfaeb42d86570e8c` |

## Correções materiais

| PMID | Registro | Correção |
|---|---|---|
| 40840576 | `pivotal-pvi-parede-posterior-criobalao-fa-persistente-estudo` | Título integral do PIVoTAL IDE restaurado conforme PubMed. |
| 42218955 | `ivus-aterectomia-rotacional-planejada-lesao-calcificada-grau-3` | Glifo romano do título normalizado para a forma indexada no PubMed. |
| 41767027 | `readyornot-chd-app-transicao-desenho-estudo` | Ano do fascículo corrigido de 2025 para 2026. |
| 39556015 | `onco-pe-rivaroxabana-18-vs-6-meses-estudo` | Primeiro autor corrigido para Yugo Yamashita; recorrência e sangramento maior passaram a trazer contagens, OR, IC e p; limites da amostra japonesa aberta explicitados. |
| 40884443 | `danflu2-miocardite-pericardite-vacina-alta-dose-estudo` | A conclusão vaga de “sem excesso detectável” foi substituída pelo resultado real: 19 versus 35 eventos, efetividade relativa 45,71% (IC95% 2,46–70,67; p=0,04), com natureza exploratória, raridade, ausência de não vacinados e financiamento industrial explicitados. |
| 39132600 | `peerless-ii-trombectomia-vs-anticoagulacao-protocolo-estudo` | Título, DOI e periódico corrigidos; continua classificado como protocolo sem resultados. |
| 39638275 | `pe-tract-terapia-dirigida-cateter-protocolo-estudo` | Autor, DOI e periódico corrigidos; população reescrita sem requisitos não sustentados pelo abstract. |
| 40454770 | `reabilitacao-estruturada-adesao-sca-estudo` | Título, primeiro autor e DOI corrigidos. |
| 42098205 | `exercicio-online-sobreviventes-cancer-mama-vo2-estudo` | Corrigido erro direcional: a diferença de VO₂ pico favorece a intervenção, não o controle; implicação alinhada aos demais desfechos do abstract. Removido o vínculo sem nexo com `prescricao-de-exercicio-em-prevencao-primaria-cardiovascular`. |
| 42437322 | `hydra-years-cancer-embolia-pulmonar-estudo` | Autor e resultado de não inferioridade corrigidos com denominadores, diferença absoluta, IC unilateral, p e proporção que evitou angiotomografia. |
| 40953438 | `aktivplan-habitos-atividade-fisica-pos-reabilitacao-estudo` | Título, autor e DOI corrigidos; registrado que 34 participantes foram recrutados frente à meta de 40 e que não houve teste confirmatório de eficácia. |
| 41365669 | `crhcp-controle-intensivo-pressao-diastolica-baixa-analise-secundaria` | Primeiro autor corrigido para Ziyi Xie. |
| 31475794 | `paragon-hf-neutro-e-a-faixa-45-49-nao-e-paradigm` | Corrigida a unidade do desfecho: 894 eventos em 526 pacientes versus 1.009 eventos em 557 pacientes; os números 526/557 não são contagens de eventos. |

Nos demais registros, a reconciliação de título/DOI/ano e a conferência numérica contra o abstract não identificaram discrepância material. Afirmações legítimas de limitação da fonte — por exemplo, ausência de leitura integral quando o abstract foi suficiente para a síntese publicada — foram mantidas como limites de evidência, não como pendência editorial.

## Deduplicação bibliográfica legada

A auditoria encontrou sete PMIDs duplicados e uma duplicidade adicional identificada pelo DOI. Eram registros da mesma publicação e mesma pergunta, não subanálises independentes. O registro canônico mais completo ou mais estável/referenciado foi preservado; autores, financiamento, números, limites, tags e vínculo documental exclusivos foram incorporados quando aplicável. A união semântica de tags foi restaurada em DELIVER, PARAGON-HF, FINEARTS-HF, ADVOR, CLOROTIC e PEITHO, sem repetir a mesma tag apenas por diferença de caixa.

| Identificador | Slug removido | Slug canônico | Decisão de preservação |
|---|---|---|---|
| 36027570 | `deliver-dapagliflozina-icfep` | `deliver-consistencia-por-faixa-de-feve-nao-e-reclassificacao-2026` | Preserva o vínculo ao documento contextual; remove marcador de verificação pendente e incorpora o resultado primário completo. |
| 31475794 | `paragon-hf-sacubitril-valsartana-na-icfep` | `paragon-hf-neutro-e-a-faixa-45-49-nao-e-paradigm` | Preserva o vínculo contextual e a distinção PARAGON/PARADIGM; consolida a limitação do primário neutro. |
| 39225278 | `finearts-hf-finerenona-na-icfem-e-icfep` | `finearts-hf-populacao-feve-maior-igual-40-faixa-historica-icfei` | Preserva o vínculo documental e elimina inferência de subgrupo não conferida. |
| 39555826 | `summit-tirzepatida-icfep-com-obesidade` | `tirzepatida-e-icfep-com-obesidade-o-ensaio-summit` | Preserva o slug publicado e usado por trilhas/material/fluxograma; incorpora autores completos, financiamento, contagens, eventos adversos e limites do card removido. |
| 36027559 | `advor-acetazolamida-diuretico-ic-aguda-descompensada` | `advor-mullens-2022-acetazolamida-iv-descongestao-apos-alca` | Preserva desenho, dose, denominadores, financiamento e vínculo ao documento ADVOR/CLOROTIC. |
| 37952131 | `select-lincoff-semaglutida-24mg-mace-obesidade-sem-diabetes` | `select-semaglutida-desfechos-cardiovasculares-obesidade-sem-diabetes` | Preserva o slug referenciado por evidência, trilha e material; incorpora autores, financiamento, denominadores e limites completos. |
| 36423214 | `clorotic-hidroclorotiazida-associada-a-diuretico-de-alca-na-ic-aguda` | `clorotic-trullas-2023-hctz-oral-add-on-furosemida-iv` | Preserva o registro detalhado e o vínculo ao documento; evita transformar o campo de potássio corrompido no XML em afirmação de segurança. |
| PMID 24716681 / DOI 10.1056/NEJMoa1302097 | `peitho-fibrinolise-em-tep-de-risco-intermediario` | `peitho-tenecteplase-versus-placebo-tep-normotenso-vd-e-troponina` | Preserva o registro com PMID, desenho e denominadores completos; confirma população ITT de 506 versus 499, incorpora tags e remove a pendência de dose não sustentada pelo abstract. |

Resultado: 2.069 → 2.061 registros, 7 → 0 PMIDs duplicados e 1 → 0 DOI duplicado. Os oito canônicos ficaram `review_status: revisado` e `published: true`.

### Referências externas que exigem migração pelo integrador

Nenhuma referência viva em trilhas, evidências ou material aponta para os slugs removidos de DELIVER, PARAGON-HF, FINEARTS-HF, ADVOR ou CLOROTIC. Os slugs de alta utilização de SUMMIT e SELECT foram escolhidos como canônicos justamente para preservar essas ligações. A única referência estrutural viva a migrar é a etapa em `trilhas/metadados.json:3650`, de `peitho-fibrinolise-em-tep-de-risco-intermediario` para `peitho-tenecteplase-versus-placebo-tep-normotenso-vd-e-troponina`.

Restam referências textuais/administrativas aos slugs removidos abaixo; elas não foram editadas neste workstream para evitar colisão com staging, corpus e approval:

- `summit-tirzepatida-icfep-com-obesidade`: `editorial-approvals/grok-science-overnight-20260829.json:42,128`; `docs/grok-science-overnight-20260829.md:27`; `docs/grok-science-overnight-20260829-qc.md:25,139,196`; `content/Insuficiência_cardíaca/agonistas-incretina-na-icfep-com-obesidade-step-e-summit.md:20`; `content/Insuficiência_cardíaca/summit-tirzepatida-icfep-com-obesidade.md:3`; e `.science-staging/lote-hf-incretina.json:9,10,23,45`.
- `select-lincoff-semaglutida-24mg-mace-obesidade-sem-diabetes`: `editorial-approvals/grok-science-overnight-20260829.json:126` e `.science-staging/lote-select-sglt2-drc.json:21`.
- `advor-acetazolamida-diuretico-ic-aguda-descompensada` e `clorotic-hidroclorotiazida-associada-a-diuretico-de-alca-na-ic-aguda`: apenas menção histórica, não referência estrutural, em `.science-staging/lote-hf-advor-clorotic.json:10`.
- `peitho-fibrinolise-em-tep-de-risco-intermediario`: referência estrutural em `trilhas/metadados.json:3650`; a staging `.science-staging/lote-tep-intermediario.json:27` já usa o slug canônico e não requer alteração.

O approval final deve ser regenerado sem os slugs removidos; o conteúdo SUMMIT duplicado deve ser consolidado ou redirecionado para `tirzepatida-e-icfep-com-obesidade-o-ensaio-summit` antes do release.

## Checks direcionados e reprodutíveis

```bash
python -m json.tool estudos/metadados.json >/dev/null
git diff --check
```

```python
import collections
import json

records = json.load(open("estudos/metadados.json"))
identifiers = {
    "pmid": collections.defaultdict(list),
    "doi": collections.defaultdict(list),
}
for record in records:
    if record.get("pmid"):
        identifiers["pmid"][str(record["pmid"])].append(record["slug"])
    if record.get("doi"):
        identifiers["doi"][record["doi"].casefold()].append(record["slug"])
for values in identifiers.values():
    assert not {identifier: slugs for identifier, slugs in values.items() if len(slugs) > 1}
```

Após integrar o lote revisado de evidências, repetir o cruzamento explícito:

```python
import json

studies = {x["slug"]: x for x in json.load(open("estudos/metadados.json"))}
evidence = [x for x in json.load(open("evidencias/metadados.json")) if x.get("study_slug")]
assert len(evidence) == 174
assert len({x["study_slug"] for x in evidence}) == 174
assert all(x["study_slug"] in studies for x in evidence)
assert all(str(studies[x["study_slug"]]["pmid"]) == str(x["pmid"]) for x in evidence)
```

Para reproduzir a identidade bibliográfica, consultar em lote os 170 PMIDs registrados por `https://eutils.ncbi.nlm.nih.gov/entrez/eutils/efetch.fcgi?db=pubmed&id=<PMIDs>&retmode=xml` e comparar `ArticleTitle`, `ArticleId[@IdType='doi']`, `PubDate` e `AuthorList` com os campos do JSON.
