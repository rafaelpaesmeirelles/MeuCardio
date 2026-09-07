# Tudo com Tudo — Hipertensão pulmonar: CTEPH / falência VD / síncope→PS (2026-09-07)

## Anti-colisão

- PR **#841** (aberto): sinalizadores de piora na HAP, fluxograma escalar/referenciar, freio grupo 2/3 — **não duplicado**.
- PR **#837** (Tromboembolismo): sinalizadores pós-TEP → urgência — vizinho; este pacote pivota **suspeita crônica de CTEPH no consultório de HP**, não recorrência aguda de TEP.
- Listagem `content/Hipertensão_pulmonar/`: CTEPH denso em operabilidade/ensaios/Delcroix; **sem** checklist ambulatorial suspeita→referência; **sem** pacote dedicado falência de VD; **sem** fluxograma síncope→PS.
- `search_code` em main: 0 hits de `sinalizadores-ambulatoriais` na pasta HP.
- Evitados hubs #826–#870 (demais especialidades); próximo número livre após #870.

## Pivô (além #841)

Densificar lacunas ambulatoriais distintas:
1. **Suspeita de CTEPH** — quando referenciar centro (potencialmente curável).
2. **Falência de VD** — red flags e destino.
3. **Síncope na HAP** — árvore para PS (alto risco ESC/ERS).

Sem doses, sem cortes eco inventados, sem auto-merge.

## Arquivos

| Arquivo | Slug | Kind |
|---|---|---|
| `content/Hipertensão_pulmonar/sinalizadores-ambulatoriais-suspeita-de-cteph-quando-referenciar.md` | `sinalizadores-ambulatoriais-suspeita-de-cteph-quando-referenciar` | protocolo |
| `content/Hipertensão_pulmonar/sinalizadores-ambulatoriais-falencia-de-vd-na-hp.md` | `sinalizadores-ambulatoriais-falencia-de-vd-na-hp` | protocolo |
| `content/Hipertensão_pulmonar/fluxograma-ambulatorial-sincope-na-hap-para-ps.md` | `fluxograma-ambulatorial-sincope-na-hap-para-ps` | fluxograma |

Todos com `review_status: pendente_revisao`.

## Fontes (reais)

- ESC/ERS 2022 PMID **36017548** (DOI 10.1093/eurheartj/ehac237)
- Delcroix CTEPH registry PMID **26826181**
- Cruzamentos com docs já revisados do corpus (operabilidade CTEPH, estratificação HAP, eco triagem, perioperatório)

## Branch

`feat/tudo-com-tudo-hap-cteph-vd-sincope-20260907-0210` → `main`
