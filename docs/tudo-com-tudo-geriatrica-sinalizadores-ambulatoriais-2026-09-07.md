# Tudo-com-Tudo — Cardiologia geriátrica: sinalizadores ambulatoriais (2026-09-07)

## Escopo / pivô

**Lacuna:** destino ambulatorial (PS agora vs. retorno precoce) em **queda/síncope** e **equivalentes isquêmicos atípicos** no idoso frágil em consultório.

**Já coberto em main (não duplicar):**
- `sincope-e-queda-no-idoso-estratificacao-de-risco-na-emergencia` (+ fluxograma) — eixo **emergência**
- `sindrome-coronariana-aguda-no-idoso-fragil-e-apresentacao-atipica` (+ fluxograma) — reconhecimento/manejo amplo
- `fragilidade-como-modificador-de-decisao-cardiovascular`, `polifarmacia-cardiovascular-no-idoso-cascata-de-prescricao-e-desprescricao`

**Pivô escolhido:** ambulatory escalate gap — falls+syncope **destination** + atypical ACS **clinic red flags**.

## Anti-colisão

- Evita PRs abertos #826–#849 (sinalizadores de outros temas; nenhum Cardiologia_geriátrica sinalizadores até #849).
- Não reescreve estratificação de emergência nem protocola doses/estratégia invasiva.

## Arquivos

| Arquivo | Slug | Kind |
|---|---|---|
| `content/Cardiologia_geriátrica/sinalizadores-ambulatoriais-queda-sincope-idoso-quando-encaminhar.md` | `sinalizadores-ambulatoriais-queda-sincope-idoso-quando-encaminhar` | protocolo |
| `content/Cardiologia_geriátrica/fluxograma-ambulatorial-queda-sincope-idoso-destino.md` | `fluxograma-ambulatorial-queda-sincope-idoso-destino` | fluxograma |
| `content/Cardiologia_geriátrica/sca-atipica-idoso-fragil-sinalizadores-ambulatoriais-consultorio.md` | `sca-atipica-idoso-fragil-sinalizadores-ambulatoriais-consultorio` | protocolo |

Todos com `review_status: pendente_revisao`, `fonte_producao: grok`.

## Fontes (somente refs conferidas)

- ESC 2018 Syncope — Brignole et al., PMID 29562304
- AHA 2023 ACS older adults — Damluji et al., PMID 36503287
- ESC 2023 ACS — Byrne et al., PMID 37622654

Sem PMID inventado. Sem doses.

## Branch

`feat/tudo-com-tudo-geriatrica-sinalizadores-20260907-0434` → `main`
