# Tudo com Tudo — Aorta/DAP: sinalizadores ambulatoriais de SAA → PS

Data: 07/09/2026 (America/Sao_Paulo).

## Lacuna

`content/Aorta_e_doença_arterial_periférica` já tinha hub e fluxograma **hospitalares** de síndrome aórtica aguda (ADD-RS, D-dímero, angio-TC, TEM, tipo A/B). PRs abertos **#833** (CLTI/AAA) e **#868** (carótida/AIT) cobriam outros braços ambulatoriais. **Faltava** o pacote de consultório: suspeita de SAA → **PS imediato** + checklist de handoff (sem rule-out eletivo).

## Anti-colisão

- `search_code` slugs novos: zero hits.
- `search_pull_requests` Aorta/SAA ambulatorial: #833 e #868 em nichos distintos; nenhum PR aberto no mesmo nicho SAA→PS ambulatorial.
- Evitados PRs ≥#898 de outros temas (IC ferro, cardiorrenal, tMCS, etc.).
- Corpus: `sindrome-aortica-aguda-dissecacao-diagnostico-e-manejo` e `fluxograma-sindrome-aortica-aguda-esc-2024` permanecem o braço hospitalar; este lote **não** os reescreve.

## Arquivos

1. `content/Aorta_e_doença_arterial_periférica/sinalizadores-ambulatoriais-suspeita-sindrome-aortica-aguda-ps-imediato.md` — protocolo
2. `content/Aorta_e_doença_arterial_periférica/checklist-ambulatorial-suspeita-de-sindrome-aortica-aguda-antes-do-ps.md` — checklist
3. `content/Aorta_e_doença_arterial_periférica/fluxograma-ambulatorial-suspeita-saa-consultorio-para-ps.md` — fluxograma
4. Este relatório

## Status editorial

- `review_status: pendente_revisao` em todos os conteúdos
- Sem auto-merge
- Sem doses
- Frontmatter alinhado ao padrão #828 / pacotes Aorta #833/#868 (`fonte_producao: grok`, `source_refs` com PMID)

## Fontes (PMID reais)

- ESC 2024 PAAD — Mazzolai et al. PMID **39210722**
- ADD-RS / IRAD — Rogers et al. PMID **21555704**
- ADvISED — Nazerian et al. PMID **29030346**

## Pivot

Nenhum — fronteira SAA ambulatorial → PS estava livre além de #833/#868.
