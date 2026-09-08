# Tudo com Tudo — Perioperatório: sinalizadores ambulatoriais pré-op (2026-09-07)

## Anti-colisão

- Listagem de `content/Perioperatório/`: RCRI já denso (`arvore-decisao-rcri-lee`, `fluxograma-rcri-estratificacao-risco-cirurgico`); timing stent já tem árvore AHA/ACC 2024; condições agudas já têm árvore.
- Busca de PRs abertos (perioperatório / pré-op / RCRI / stent / adiar): sem PR aberto com o mesmo framing ambulatorial de **quando adiar eletiva**.
- Evitados colisões da noite: #826 Diabetes, #827 FA, #828 Hipertensão sinalizadores, #829 Cardiorrenal, #831 Reabilitação, #832 Teach-back, #833 Aorta/DAP, #834 Cardio-oncologia, #835 Dispositivos.

## Pivô

**Não** reescrever RCRI nem regimes DAPT. Densificar lacuna ambulatorial: **sinalizadores para adiar eletiva** + **quando escalar** + **framing de janela pós-stent** apontando para docs existentes (sem doses).

## Arquivos

| Arquivo | Slug | Kind |
|---|---|---|
| `content/Perioperatório/sinalizadores-ambulatoriais-para-adiar-cirurgia-eletiva-nao-cardiaca.md` | `sinalizadores-ambulatoriais-para-adiar-cirurgia-eletiva-nao-cardiaca` | protocolo |
| `content/Perioperatório/fluxograma-ambulatorial-risco-cardiovascular-preoperatorio-quando-escalar.md` | `fluxograma-ambulatorial-risco-cardiovascular-preoperatorio-quando-escalar` | fluxograma |
| `content/Perioperatório/stent-coronario-recente-e-cirurgia-eletiva-janela-de-risco-ambulatorial.md` | `stent-coronario-recente-e-cirurgia-eletiva-janela-de-risco-ambulatorial` | protocolo |

Todos com `review_status: pendente_revisao`.

## Fontes (reais)

- AHA/ACC 2024 PMID 39316661
- ESC 2022 PMID 36017553
- SBC 2024 DOI 10.36660/abc.20240590
- CCS 2017 PMID 27865641

## Branch

`feat/tudo-com-tudo-perioperatorio-sinalizadores-20260907-0115` → `main`
