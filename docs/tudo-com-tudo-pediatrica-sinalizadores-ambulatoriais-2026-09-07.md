# Tudo-com-Tudo — Cardiologia pediátrica: sinalizadores ambulatoriais (2026-09-07)

## Escopo / pivô

**Lacuna:** destino ambulatorial (**PS agora** vs. **cardiologia pediátrica** vs. **retorno precoce**) em **dor torácica**, **síncope** e **palpitações** na criança/adolescente em consultório.

**Já coberto em main (não duplicar):**
- `dor-toracica-pediatrica-avaliacao-de-sinais-de-alarme-cardiaco-vs-causa-nao-cardiaca` — diferencial/diagnóstico
- `sincope-e-morte-subita-em-criancas-e-atletas-jovens-triagem-de-canalopatias-e-cardiomiopatias` — diferencial/canalopatias/CMH
- `extrassistoles-ventriculares-e-supraventriculares-na-crianca-e-no-adolescente-limiar-de-carga-historia-natural-e-tratamento`
- `taquicardia-supraventricular-no-lactente-e-na-crianca-manejo-agudo-e-cronico`

**Pivô escolhido:** ambulatory escalate gap — chest pain / syncope / palpitations **destination** (ED vs specialist).

## Anti-colisão

- Evita PRs abertos **#826–#862** (nenhum `Cardiologia_pediátrica` sinalizadores até #862).
- Evita ACHD adulto **#845**.
- Não reescreve diferenciais de main; não protocola doses.

## Arquivos

| Arquivo | Slug | Kind |
|---|---|---|
| `content/Cardiologia_pediátrica/sinalizadores-ambulatoriais-pediatria-dor-sincope-palpitacoes-ps-vs-especialista.md` | `sinalizadores-ambulatoriais-pediatria-dor-sincope-palpitacoes-ps-vs-especialista` | protocolo |
| `content/Cardiologia_pediátrica/fluxograma-ambulatorial-pediatria-dor-sincope-palpitacoes-destino.md` | `fluxograma-ambulatorial-pediatria-dor-sincope-palpitacoes-destino` | fluxograma |
| `content/Cardiologia_pediátrica/palpitacoes-ambulatoriais-na-crianca-quando-ps-vs-cardiologista-pediatrico.md` | `palpitacoes-ambulatoriais-na-crianca-quando-ps-vs-cardiologista-pediatrico` | protocolo |

Todos com `review_status: pendente_revisao`, `fonte_producao: grok`.

## Fontes (somente refs conferidas)

- ACC/AHA/HRS 2017 Syncope — Shen et al., PMID 28280231
- ESC 2018 Syncope — Brignole et al., PMID 29562304
- Fogliazza et al. J Clin Med 2024 — PMID 39597803
- Karatza et al. Children 2025 — PMID 40150649
- Sanatani et al. Can J Cardiol 2017 — PMID 27838109
- Yeom & Woo Clin Exp Pediatr 2023 — PMID 36789491

Sem PMID inventado. Sem doses.

## Branch

`feat/tudo-com-tudo-pediatrica-sinalizadores-20260907-0452` → `main`
