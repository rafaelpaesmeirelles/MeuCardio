# Tudo com Tudo — Aorta / DAP: sinalizadores ambulatoriais CLTI e AAA

**Branch:** `feat/tudo-com-tudo-aorta-dap-sinalizadores-20260907-0413`  
**Status:** `pendente_revisao` — sem auto-merge.

## Intent

Densificar `content/Aorta_e_doença_arterial_periférica` com conteúdo ambulatorial de **sinalizadores / destino** (red flags), alinhado à ESC 2024 PAAD (Eur Heart J), sem doses e sem inventar arestas de grafo JSON.

## Anti-collision

- Busca PR abertas: `Aorta OR DAP OR periférica OR claudicação OR AAA` — havia PRs de material-paciente, checklists e verbetes-hub; **nenhuma** cobrindo sinalizadores ambulatoriais CLTI/AAA no mesmo folder.
- Evitados colisões com #826 Diabetes, #827 FA, #828 Hipertensão sinalizadores, #829 Cardiorrenal, #831 Reabilitação, #832 Teach-back.
- `search_code` no path Aorta: **zero** slugs `sinalizadores-*` / `ameaca-de-rotura` / `encaminhar-urgencia`.
- **Pivot:** nenhum — fronteira CLTI ambulatory + AAA rupture warnings estava livre.

## Files

1. `content/Aorta_e_doença_arterial_periférica/sinalizadores-ambulatoriais-de-isquemia-critica-ameacadora-de-membro-clti.md`
2. `content/Aorta_e_doença_arterial_periférica/sinalizadores-ambulatoriais-de-aneurisma-de-aorta-abdominal-ameaca-de-rotura.md`
3. `content/Aorta_e_doença_arterial_periférica/fluxograma-ambulatorial-dap-quando-encaminhar-urgencia-versus-vascular.md`
4. `docs/reports/tudo-com-tudo-aorta-dap-sinalizadores.md` (este relatório)

## Cross-links (texto clínico apenas)

DAP/ITB, fluxogramas de dor de membro e CLTI, ALI Rutherford, AAA rastreio/seguimento, PAAD ESC 2024, síndrome aórtica aguda; menções a diabetes, tabagismo, hipertensão e diferencial de SCA.
