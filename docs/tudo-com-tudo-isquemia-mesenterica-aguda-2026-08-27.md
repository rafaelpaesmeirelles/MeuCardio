# Lote Tudo com Tudo — isquemia mesentérica aguda de origem cardioembólica

Data da auditoria: 27/08/2026.

## Lacuna priorizada

O corpus já tinha um documento revisado sobre isquemia mesentérica **crônica**
(`isquemia-mesenterica-cronica-diagnostico-e-tratamento-svs-2021.md`), cujo
próprio `review_note` excluía explicitamente a forma **aguda** do escopo
("Isquemia mesentérica aguda e causas não ateroscleróticas permanecem
exclusões explícitas, sem extrapolação"). Uma varredura de todo o corpus
(triagem-sintomas, doenças, emergência, checklists, evidências, estudos,
trilhas, material ao paciente) não encontrou nenhuma menção a "isquemia
mesentérica aguda" fora desse documento crônico — zero cobertura.

É uma lacuna de alto impacto e diretamente cardiológica: a etiologia mais
citada da forma arterial é embólica, de origem **cardíaca** (fibrilação
atrial, trombo mural pós-infarto, valvopatia, disfunção de ventrículo
esquerdo), com mortalidade histórica de 30–70% quando o diagnóstico atrasa.
A lacuna não se sobrepõe às frentes já em andamento no repositório: PR #536
(colapso súbito/PCR), PR #538 (suspeita de AVC) e o trabalho atual do Codex em
sangramento associado a anticoagulante/antiplaquetário tratam de outras
emergências tempo-dependentes, sem tocar isquemia mesentérica.

## Conteúdo novo

- documentos: protocolo de reconhecimento/primeira hora e fluxograma em
  árvore de decisão estrita (validado por `mermaid.parse()` e pelo validador
  de estrutura de árvore da casa — 13 nós, 8 condutas);
- triagem: `dor-abdominal-aguda-desproporcional-ao-exame`;
- doença: `isquemia-mesenterica-aguda-cardioembolica` (área `cardiogeriatria`
  — recorte deliberado: a fração embólica é predominantemente geriátrica,
  idade média de 79 anos numa coorte específica citada nas fontes);
- checklist: `primeira-hora-na-suspeita-de-isquemia-mesenterica-aguda`;
- material ao paciente: `dor-abdominal-subita-e-intensa-quando-procurar-a-emergencia`;
- evidências: 3 recomendações formalmente graduadas (reconhecimento, exame,
  revascularização);
- trilha: do reconhecimento à decisão de revascularização.

Os 10 registros novos permanecem como `pendente_revisao`, com
`fonte_producao=claude`. Nenhuma decisão de revisão clínica humana foi
presumida. Nenhum documento existente foi editado — os vínculos são
unidirecionais (do lote novo para o acervo já publicado/revisado), preservando
o estado aprovado do documento crônico já existente.

## Relações clínicas diretas

| Origem | Campo estruturado | Destino | Justificativa |
|---|---|---|---|
| doença | `differential_for` por nome exato | triagem | dor abdominal desproporcional é a porta de entrada da doença |
| doença | `related_document_slugs` | protocolo e fluxograma | ambos descrevem a mesma primeira hora |
| material | `patient_education_for` | doença | reconhecimento leigo e orientação de busca por emergência |
| material/checklist | `derived_from` | protocolo | derivação explícita, com slug canônico |
| evidências | `supported_by` | protocolo / fluxograma | recomendações pontuais WSES 2022 / ESVS 2025, com classe e nível exatos da fonte |
| trilha | `contains` | 2 documentos, 3 evidências, checklist, heparina não fracionada, doença crônica irmã | sequência explícita do reconhecimento à decisão de revascularização |
| documentos | links Markdown | protocolo, fluxograma, doença crônica irmã (ver também, unidirecional) | navegação bidirecional pela API do grafo a partir do lote novo |

O armazenamento das arestas é dirigido, mas a API consulta relações de entrada
e saída. Os nós pendentes continuam fora da publicação até revisão humana.

## Proximidade temática sem promoção a vínculo direto

- prevenção primária de embolia (anticoagulação crônica na fibrilação atrial,
  CHA₂DS₂-VASc, fechamento de apêndice atrial) trata do risco antes do evento,
  não do reconhecimento/primeira hora — não entrou na trilha;
- investigação de fonte cardioembólica após o evento (ecocardiograma
  transesofágico, Holter) é continuidade etiológica pós-agudo, fora do
  recorte deste lote;
- a heparina não fracionada foi ligada como medicamento existente no acervo,
  mas o documento é explícito sobre a diferença de graduação entre as fontes:
  recomendação formal (Classe I / 1B) apenas para trombose de veia
  mesentérica, coadjuvante graduado (Classe IIb) na isquemia não oclusiva, e
  **sem** recomendação numerada/graduada equivalente para a forma arterial —
  nenhuma das duas diretrizes atuais (WSES 2022, ESVS 2025) foi forçada a
  parecer mais uniforme do que é;
- não existe verbete de estudo original específico sobre isquemia mesentérica
  aguda no acervo (`estudos/metadados.json`); a lacuna é declarada, não
  preenchida por um estudo fabricado ou por proximidade temática com estudos
  de fibrilação atrial já existentes.

## Fontes primárias e atuais

- WSES 2022 — Bala M, Catena F, Kashuk J, De Simone B, Gomes CA, Weber D, et
  al. Acute mesenteric ischemia: updated guidelines of the World Society of
  Emergency Surgery. World J Emerg Surg. 2022;17(1):54. DOI:
  `10.1186/s13017-022-00443-x`. PMID: 36261857. Texto integral conferido
  (PMC9580452 / cópia CC-BY em eScholarship). Recomendações 1, 5, 9, 10 e 12
  usadas com classe/nível verbatim da fonte.
- ESVS 2025 — Koelemay MJ, Geelkerken RH, Kärkkäinen J, Leone N, et al.
  Editor's Choice – European Society for Vascular Surgery (ESVS) 2025
  Clinical Practice Guidelines on the Management of Diseases of the
  Mesenteric and Renal Arteries and Veins. Eur J Vasc Endovasc Surg.
  2025;70(2):153-218. DOI: `10.1016/j.ejvs.2025.06.010`. PMID: 40513642.
  Texto integral conferido via cópia institucional idêntica ao publicado
  (ejves.com/sciencedirect.com bloquearam com HTTP 403). Recomendações 32,
  33, 34, 35, 37, 38, 45 e 50 usadas com classe/nível verbatim da fonte.
- Clair DG, Beach JM. Mesenteric Ischemia. N Engl J Med. 2016;374(10):959-968.
  DOI: `10.1056/NEJMra1503884`. PMID: 26962730. Texto integral conferido —
  usado para a fração embólica clássica (40–50%) e a epidemiologia geral.
- Kärkkäinen JM. Acute Mesenteric Ischemia: A Challenge for the Acute Care
  Surgeon. Scand J Surg. 2021;110(2):150-158. DOI:
  `10.1177/14574969211007590`. PMID: 33866891. Usado para o dado de coorte
  (72% com FA, idade média 79 anos) — atribuído explicitamente a uma coorte
  específica, não generalizado.

## Riscos e limites

- o fluxo não substitui a decisão da equipe cirúrgica/intervencionista nem o
  protocolo institucional;
- a fração de casos embólicos varia por série (25% a 50%) e os dois números
  são reportados juntos, com a ressalva de que a diretriz mais atual (WSES
  2022) registra uma tendência de queda — não escolhi um único número para
  simplificar;
- a anticoagulação por heparina tem grau de recomendação **desigual** entre
  etiologias (graduado para trombose venosa e NOMI, não graduado para a forma
  arterial) — documentado explicitamente para não induzir uso uniforme;
- a área `cardiogeriatria` da doença é um recorte deliberado por
  predominância epidemiológica, não uma afirmação de que a forma embólica só
  ocorre em idosos;
- revisão clínica e técnica final é obrigatória antes de qualquer item mudar
  para `revisado`.

## Testes, auditoria e build

- `python scripts/audit_tudo_com_tudo.py`: 9.452 → 9.462 itens; arquivos
  físicos 2.185 → 2.187; `review_status` = 9.452 revisado + 10
  pendente_revisao; cobertura temática explícita 9.462/9.462; zero
  referência quebrada;
- `python scripts/content_inventory.py --minimum-records 9462
  --minimum-files 2187 --strict`: `invalid=[]`, `missing=[]`;
- validador de mermaid (`mermaid.parse()` real, via jsdom) e validador de
  árvore de decisão estrita (raiz única, um pai por nó, conduta só em folha,
  rótulo em toda aresta): OK no fluxograma novo;
- `pytest backend/tests/test_specialty_guides.py
  backend/tests/test_library_catalog_integrity.py
  backend/tests/test_canonical_content_review_status.py
  backend/tests/test_tudo_com_tudo_isquemia_mesenterica_aguda.py`: 23
  passed (rodado contra Postgres real, `alembic upgrade head` aplicado no
  banco de teste `corvia-test-pg`).

## Bloqueios encontrados

- ejves.com e sciencedirect.com bloquearam o texto da ESVS 2025 com HTTP 403;
  contornado com a cópia institucional idêntica (mesmo DOI) hospedada em
  ris.utwente.nl;
- deliberadamente **não** foi criado um registro em `emergencia/metadados.json`
  para este lote: o carregador atual (`carregar_emergencia.py`) só aceita
  `documento_slug`/`fluxograma_slug` apontando para `Document` publicado ou
  `revisado` — referenciar um documento `pendente_revisao` exige a mesma
  relaxação de checagem que o PR #538 está introduzindo em paralelo
  (`_documento_pode_ser_referenciado`). Duplicar essa mudança de
  infraestrutura numa frente marcada como "já em andamento" pareceu mais
  arriscado do que valioso; o protocolo de emergência para isquemia
  mesentérica aguda fica como item de continuação natural, a ser adicionado
  depois que uma das duas mudanças de loader for mergeada;
- `reconcile_content.py` (mínimos por frente), `library.py`
  (`SCIENTIFIC_FILES_EXPECTED`), `test_library_catalog_integrity.py` e
  `.github/workflows/corpus-inventory.yml` também são tocados pelo PR #538 em
  paralelo — nos 6 de 7 mínimos incrementados aqui, os valores finais
  coincidem exatamente com os do PR #538 (mesma quantidade de itens novos por
  frente), então a fusão deve resolver sem conflito real na maioria das
  linhas; a exceção é o mínimo de `triagem_sintomas` (13 aqui vs. 15 no
  PR #538, que optou por sincronizar ao total real da frente em vez de
  incrementar pelo delta) — quem mergear por último precisa resolver essa
  linha manualmente, escolhendo o valor mais alto.
