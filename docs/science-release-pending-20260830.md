# Candidato científico consolidado — publicação única

| Origem | Tipos | Itens |
|---|---|---:|
| Claude | casos, checklists, doenças, materiais, trilhas e documentos | 103 |
| Grok | 227 estudos + 338 evidências | 565 |
| Codex | 24 estudos + 24 evidências | 48 |
| **Total** |  | **716** |

Total canônico projetado: **10.905** itens (base: 10.189).

- corpus canônico: todos os itens resolvidos como `revisado` pelo loader de produção
- zero colisões novas de slug, PMID, DOI ou título normalizado
- 79/79 PMIDs declarados na ampliação Claude resolveram no PubMed
- evidências derivadas de estudos: `recommendation_class: N/A`
- `published: false` preservado nos manifests; a reconciliação do deploy publica os revisados
- lotes Grok/Codex revisados contra metadados e abstracts PubMed; artigo integral não conferido

Este é o único candidato para merge e deploy.
