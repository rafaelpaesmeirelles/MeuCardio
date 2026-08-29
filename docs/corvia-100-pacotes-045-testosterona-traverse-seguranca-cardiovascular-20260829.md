# CorVIA 100 pacotes — 045/100 — Reposição de testosterona e segurança cardiovascular: TRAVERSE

Data: 29/08/2026  
Base auditada: `main` `59566e1196e0fa7f465df93516790ef454e1f565`

## Objetivo

Revisar adversarialmente o TRAVERSE para impedir duas extrapolações opostas e frequentes: declarar que testosterona aumenta MACE de forma categórica em todo homem, ou declarar que o ensaio provou segurança cardiovascular irrestrita e autoriza uso fora da população estudada.

## Evidência crítica verificada

- **TRAVERSE** — Lincoff AM et al. N Engl J Med. 2023;389:107-117. PMID `37326322`; DOI `10.1056/NEJMoa2215025`.
- Desenho: RCT multicêntrico, duplo-cego, placebo-controlado, de não inferioridade.
- População: 5.246 homens de 45-80 anos, com doença cardiovascular preexistente ou alto risco cardiovascular, sintomas de hipogonadismo e **duas testosteronas de jejum <300 ng/dL**.
- Intervenção: gel transdérmico de testosterona 1,62%, ajustado para 350-750 ng/dL, versus placebo.
- Primário cardiovascular: morte CV, IAM não fatal ou AVC não fatal.
- Eventos: 7,0% com testosterona versus 7,3% com placebo; HR 0,96 (IC95% 0,78-1,17); p<0,001 para não inferioridade.
- O limite de não inferioridade pré-especificado exigia limite superior do IC95% <1,5.
- Houve maior incidência observada de **fibrilação atrial, lesão renal aguda e embolia pulmonar** no grupo testosterona.

## Revisão adversarial independente

1. **Não inferioridade para MACE ≠ benefício cardiovascular:** o TRAVERSE não demonstrou que testosterona previne IAM, AVC ou morte cardiovascular.
2. **Não inferioridade ≠ ausência de todo risco:** sinais de FA, lesão renal aguda e embolia pulmonar precisam permanecer visíveis na síntese de segurança.
3. **População foi diagnosticada de forma específica:** sintomas + duas dosagens de testosterona baixa; não extrapolar para uso por performance, estética, envelhecimento inespecífico ou valores laboratoriais não confirmados.
4. **Formulação e alvo importam:** o estudo avaliou gel transdérmico com ajuste protocolar; não é prova automática de segurança para qualquer formulação, dose supranormal ou esquema anabolizante.
5. **Horizonte de seguimento é finito:** média de tratamento ~21,7 meses e seguimento ~33 meses não respondem a segurança por décadas.
6. **Alto risco CV não equivale a toda condição aguda:** decisão durante evento cardiovascular recente, tromboembolismo ativo ou outra contraindicação exige fonte específica e avaliação clínica individual.
7. **Não confundir endpoints:** achados adversos secundários não devem ser usados para afirmar causalidade absoluta, mas também não devem ser apagados sob o rótulo genérico de `MACE não inferior`.

## Guardrails para CorVIA

- bloquear `TRAVERSE provou que testosterona protege o coração`;
- bloquear `TRAVERSE provou segurança de testosterona em qualquer homem/dose/formulação`;
- exigir contexto de hipogonadismo confirmado conforme a população estudada antes de citar o RCT como aplicável;
- manter FA, lesão renal aguda e embolia pulmonar na seção de segurança;
- não extrapolar para testosterona supranormal, esteroides anabolizantes ou uso recreativo;
- não inventar classe/nível de sociedade a partir do desenho de não inferioridade.

## Resultado

Gap de segurança fechado: **o TRAVERSE sustenta não inferioridade para MACE na população específica estudada, mas não demonstra benefício cardiovascular, não cobre uso off-label/supranormal e não elimina sinais de FA, lesão renal aguda e embolia pulmonar**.

Nenhum arquivo clínico, regra determinística, slug, JSON, dose operacional ou schema foi alterado neste pacote.
