# Tudo com Tudo — Dispositivos: alerta remoto ambulatorial clínica vs PS (2026-09-07)

## Pivô (anti-duplicação)

**Alvo da leva:** densificar `content/Dispositivos` com gap ambulatorial **além do PR #835** (eletrodo/choque CDI) e **#870** (pré-RM em CIED).

**Preferência explícita:** remote monitoring alert — quando ligar clínica vs ir ao PS.

**Achado em main:** existe IN-TIME (`telemonitoramento-remoto-de-cdi-e-crt-d-e-desfecho-clinico-o-ensaio-in-time`, revisado) e HeartLogic/DOT-HF — evidência de desfecho/algoritmo, **não** checklist de destino de consultório/telefone.

**Alternativas evitadas:**
- Infecção de bolsa ambulatorial → densa (fluxogramas + PR **#711**).
- Repetir pós-choque / eletrodo → #835.
- Repetir pré-RM → #870.

**Escolha:** protocolo + fluxograma + braço educativo (**RM ≠ emergência 24 h**).

## Anti-colisão (através de #903+)

- PRs abertos recentes #881–#905: **nenhum** Dispositivos sobre alerta remoto; Dispositivos Tudo-com-Tudo recentes = **#835** e **#870**.
- Não toca arquivos desses PRs nem infecção.
- Não altera IN-TIME / HeartLogic já `revisado`.

## Arquivos

| Arquivo | Slug | Kind |
|---|---|---|
| `content/Dispositivos/alerta-remoto-de-cied-no-ambulatorio-quando-ligar-clinica-vs-ps.md` | `alerta-remoto-de-cied-no-ambulatorio-quando-ligar-clinica-vs-ps` | protocolo |
| `content/Dispositivos/fluxograma-alerta-remoto-cied-destino-ambulatorial.md` | `fluxograma-alerta-remoto-cied-destino-ambulatorial` | fluxograma |
| `content/Dispositivos/monitoramento-remoto-nao-e-servico-de-emergencia-24h.md` | `monitoramento-remoto-nao-e-servico-de-emergencia-24h` | protocolo |

Todos com `review_status: pendente_revisao`, `fonte_producao: grok`. Sem doses. Sem auto-merge.

## Slugs relacionados (existentes)

`telemonitoramento-remoto-de-cdi-e-crt-d-e-desfecho-clinico-o-ensaio-in-time`, `algoritmo-multissensor-heartlogic-multisense-e-o-contraste-com-optivol-dot-hf`, `terapia-de-ressincronizacao-cardiaca-sicd-e-seguimento-remoto`, pacotes #835/#870.

## Fontes (PMIDs reais)

- HRS/EHRA/APHRS/LAHRS 2023 Remote Device Clinic — PMID **37208301**
- Slotwiner et al. HRS 2015 remote interrogation/monitoring — PMID **25981148**
- IN-TIME — Hindricks et al. Lancet 2014 — PMID **25131977**
- TRUST — Varma et al. Circulation 2010 — PMID **20625110**

## Branch

`feat/tudo-com-tudo-dispositivos-alerta-remoto-ambulatorial-20260907` → `main`
