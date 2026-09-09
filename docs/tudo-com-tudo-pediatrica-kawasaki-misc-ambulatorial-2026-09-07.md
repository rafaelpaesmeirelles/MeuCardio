# Tudo-com-Tudo — Cardiologia pediátrica: seguimento Kawasaki/MIS-C ambulatorial (2026-09-07)

## Escopo / pivô

**Lacuna além de #863:** destino ambulatorial (**PS agora** vs. **cardiologia pediátrica** vs. **retorno precoce**) no **seguimento cardíaco** após **Kawasaki** e **MIS-C** (sintoma novo: dor, síncope, equivalente atípico, atraso de calendário).

**#863 cobriu:** dor/síncope/palpitações **gerais** em pediatria de consultório.

**Já coberto em main (não duplicar):**
- `doenca-de-kawasaki-criterios-diagnosticos-estratificacao-de-risco-por-z-score-e-tratamento` — diagnóstico agudo + calendário por gravidade
- `trombose-coronaria-e-infarto-em-aneurisma-de-kawasaki` (+ fluxograma) — emergência de trombose/IAM
- `mis-c-com-disfuncao-miocardica-e-choque` (+ fluxograma) — fase aguda
- `desfechos-cardiovasculares-de-longo-prazo-pos-mis-c-revisao-sistematica-2026` — prognóstico 6–24 meses
- `sopros-cardiacos-na-infancia-…` — encaminhamento de sopro (outro pivô; já denso)
- `hipertensao-arterial-sistemica-na-crianca-…-aap-2017` — diagnóstico/tratamento HAS ped (outro pivô)

**Pivô escolhido:** Kawasaki/MIS-C **cardiac follow-up ambulatory red flags** (ausente como pacote de destino).

## Anti-colisão

- Evita #863 (sinalizadores gerais ped).
- Open PRs re-checados até **#882+** (geriatria HO, saúde mental QT, pericárdio, etc.) — nenhum outro `Cardiologia_pediátrica` ambulatory além de #863.
- Não reescreve fase aguda, Z-score nem doses.

## Arquivos

| Arquivo | Slug | Kind |
|---|---|---|
| `content/Cardiologia_pediátrica/sinalizadores-ambulatoriais-seguimento-pos-kawasaki-e-mis-c-ps-vs-especialista.md` | `sinalizadores-ambulatoriais-seguimento-pos-kawasaki-e-mis-c-ps-vs-especialista` | protocolo |
| `content/Cardiologia_pediátrica/fluxograma-ambulatorial-seguimento-kawasaki-mis-c-destino.md` | `fluxograma-ambulatorial-seguimento-kawasaki-mis-c-destino` | fluxograma |
| `content/Cardiologia_pediátrica/dor-toracica-ou-sincope-no-seguimento-pos-cal-kawasaki-destino-ambulatorial.md` | `dor-toracica-ou-sincope-no-seguimento-pos-cal-kawasaki-destino-ambulatorial` | protocolo |

Todos com `review_status: pendente_revisao`, `fonte_producao: grok`.

## Fontes (somente refs conferidas via PubMed esummary)

- AHA Kawasaki 2017 — McCrindle et al., PMID **28356445**
- JCS/JSCS 2020 — Fukazawa et al., PMID **32641591**
- Brogan et al. Heart 2020 — PMID **31843876**
- Alvarado-Gamarra et al. Eur J Pediatr 2026 — PMID **41721085**
- Yasuhara et al. Pediatr Cardiol 2023 — PMID **36416893**

Sem PMID inventado. Sem doses. Sem auto-merge.

## Branch

`feat/tudo-com-tudo-pediatrica-kawasaki-misc-ambulatorial-20260907` → `main`
