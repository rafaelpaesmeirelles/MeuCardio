# Auditoria científica #703 — produção Claude — 29/08/2026

## Janela congelada

- Início: 2026-08-28 16:06:46 UTC
- Fim: 2026-08-29 04:06:46 UTC
- Critério: PRs/branches Claude criados ou atualizados na janela, inclusive não mergeados; GitHub é a fonte de verdade.

## Integrado e revisado no release #708

Foram incorporados como fragmentos canônicos, com revisão editorial separada e `review_status=revisado` apenas após a auditoria: obesidade e risco cardiovascular; insuficiência mitral; bloqueio atrioventricular; estenose mitral; cardiomiopatia dilatada; apneia do sono e doença cardiovascular; síndrome cardiorrenal; cardiomiopatia chagásica; MINOCA/SCAD; Takotsubo; cardiotoxicidade por cocaína/estimulantes; amiloidose cardíaca AL; insuficiência tricúspide; emergência hipertensiva; CTEPH; prótese valvar mecânica; torsades/QT longo adquirido; insuficiência aórtica; estenose aórtica; sarcoidose cardíaca; cardiomiopatia arritmogênica.

Também foram reconciliados deltas Tudo com Tudo de persistência do canal arterial (#679), atresia pulmonar (#680), polifarmácia/desprescrição (#693), avaliação cardiovascular pré-concepcional (#694), parada cardiorrespiratória/morte súbita abortada (#705) e embolia pulmonar aguda (#706), além da correção de três anomalias de tema do #709.

Triagens aprovadas e compostas sem sobrescrever o manifesto compartilhado: suspeita de infecção de dispositivo cardíaco implantável (#711) e complicação local pós-cateterismo/procedimento vascular (#712).

## Correções científicas aplicadas antes da promoção editorial

1. Apneia central/ASV: o sinal de dano do SERVE-HF foi preservado, mas retirada a formulação de contraindicação absoluta universal. A atualização AASM 2025 permite consideração condicional de ASV, sobretudo exigindo centro experiente e decisão compartilhada em ICFEr.
2. Cocaína/betabloqueadores: retirada a extrapolação da hipótese de “alfa sem oposição” para proibição universal. Durante intoxicação aguda com sinais simpaticomiméticos, evitar uso reflexo conforme AHA/ACC; fora dessa fase, individualizar. Metanálises observacionais não demonstraram aumento de IAM/mortalidade.
3. MINOCA/SCAD: MINOCA permanece diagnóstico de trabalho; miocardite, Takotsubo e causas sistêmicas são diagnósticos alternativos que retiram o rótulo final. SCAD é entidade própria e nem toda SCAD é MINOCA.
4. Prótese mecânica: DOAC não substitui AVK; dupla antiagregação também não substitui anticoagulação da prótese, mas não foi convertida em proibição absoluta quando existir indicação coronariana independente.

## Retidos nesta release

- #678 — atresia tricúspide: regra determinística `canal_dependente_sem_suporte` presume dependência ductal para todo paciente pré-cirúrgico. Requer condicionar o alerta à anatomia/fluxo pulmonar ducto-dependente documentado antes de publicação.
- #682 — planejamento do parto na cardiopatia fetal: conteúdo clínico aproveitável, porém o delta é muito amplo sobre registro canônico já existente e será reconciliado em correção dedicada após validação estrutural sem importar o manifesto inteiro.
- #720, #721, #722 — novas triagens: produção foi interrompida antes da confirmação dos gates dependentes de banco; mantidas fora deste release para não promover conteúdo incompletamente certificado.
- #714–#719/#723: apesar de alguns PRs terem registrado testes de banco incompletos na própria branch, os fragmentos foram revisados nesta auditoria e entram sob o gate consolidado do #708; qualquer falha estrutural no head final bloqueia a release.

## Anti-colisão e proveniência

- Nenhum PR científico de origem é mesclado individualmente para publicar este lote.
- Novos verbetes entram como `doencas/fragmentos/*.json` preservando autoria/origem; promoção e correções entram em `doencas/correcoes/`.
- Triagens paralelas entram como snapshots em `triagem-sintomas/fragmentos/`, cuja composição exige igualdade exata para slugs já existentes e bloqueia divergências.
- O release não infla contagem: revisão, vínculo e correção não criam novo registro quando o slug canônico já existe.
