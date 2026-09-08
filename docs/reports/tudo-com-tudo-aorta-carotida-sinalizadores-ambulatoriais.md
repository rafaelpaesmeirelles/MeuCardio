# Tudo com Tudo — Aorta / DAP: sinalizadores ambulatoriais carótida/AIT (além #833)

**Branch:** `feat/tudo-com-tudo-aorta-carotida-ambulatorial-20260907-0505`  
**Status:** `pendente_revisao` — sem auto-merge.

## Intent

Densificar `content/Aorta_e_doença_arterial_periférica` com pacote ambulatorial de **destino** (PS vs vascular/neurovascular prioritário vs eletivo) para **AIT/déficit focal e estenose carotídea**, fronteira **além** de PR **#833** (CLTI/AAA).

## Anti-collision

- `search_pull_requests`: `is:open Aorta OR DAP OR periférica` — #833 cobre CLTI/AAA; demais PRs Aorta são material-paciente/checklists/verbetes-hub.
- `is:open carótida OR dissecção OR claudicação` — sem PR de sinalizadores ambulatoriais carótida/AIT.
- `is:open sinalizadores carótida OR estenose carot` — zero hits.
- Evitados #826–867 já cobertos em outros temas; #838 = Farmacologia (amiodarona/digoxina), não Aorta.
- Corpus main: hub `estenose-de-carotida-diagnostico-e-indicacao-de-revascularizacao-esc-2024` existe (indicação/revasc), **sem** slugs `sinalizadores-*ait*` / `janela-de-14-dias` / `fluxograma-ambulatorial-carotida`.
- **Pivot:** nenhum — fronteira carótida/AIT ambulatorial livre; mantido no folder Aorta/DAP.

## Files

1. `content/Aorta_e_doença_arterial_periférica/sinalizadores-ambulatoriais-ait-deficit-focal-estenose-carotidea-quando-encaminhar.md`
2. `content/Aorta_e_doença_arterial_periférica/estenose-carotidea-sintomatica-janela-de-14-dias-destino-ambulatorial.md`
3. `content/Aorta_e_doença_arterial_periférica/fluxograma-ambulatorial-carotida-ps-versus-vascular-neurovascular.md`
4. `docs/reports/tudo-com-tudo-aorta-carotida-sinalizadores-ambulatoriais.md` (este relatório)

## Refs

- ESC 2024 PAAD — Mazzolai et al., Eur Heart J. 2024;45(36):3538-3700. DOI 10.1093/eurheartj/ehae179. PMID **39210722**
- AHA/ASA 2021 secondary stroke prevention — Kleindorfer et al., Stroke. 2021;52(7):e364-e467. DOI 10.1161/STR.0000000000000375. PMID **34024117**

Sem doses. Sem auto-merge.
