# CorVIA 100 pacotes — 037/100 — Finerenona em IC com FE levemente reduzida/preservada

Data: 29/08/2026  
Base: `main` `59566e1196e0fa7f465df93516790ef454e1f565`

## Objetivo

Revisar adversarialmente o uso de finerenona em insuficiência cardíaca com FEVE ≥40%, separando o resultado composto do FINEARTS-HF de seus componentes e evitando transformar redução de eventos de piora de IC em redução comprovada de mortalidade cardiovascular.

## Evidência crítica

- **FINEARTS-HF** — N Engl J Med. 2024;391:1475-1485; DOI `10.1056/NEJMoa2407107`.
- População: IC sintomática com FEVE ≥40%.
- Desfecho primário: total de eventos de piora de IC + morte cardiovascular.
- Resultado: rate ratio 0,84 (IC95% 0,74-0,95; p=0,007).
- Eventos de piora de IC: rate ratio 0,82 (IC95% 0,71-0,94).
- Morte cardiovascular: 8,1% vs 8,7%; HR 0,93 (IC95% 0,78-1,11), sem redução estatisticamente significativa.
- Segurança: maior risco de hipercalemia e menor risco de hipocalemia.

## Revisão adversarial

1. **Composto positivo ≠ mortalidade positiva:** o benefício do desfecho primário foi dirigido principalmente por eventos de piora de IC; morte CV isolada não foi significativamente reduzida.
2. **FEVE ≥40% não é sinônimo de todo fenótipo de ICFEp:** diagnóstico de IC, sintomas e critérios de inclusão do estudo continuam relevantes.
3. **Finerenona não é intercambiável automaticamente com espironolactona/eplerenona:** mecanismo de receptor é relacionado, mas evidência, populações e segurança não devem ser fundidos.
4. **Hipercalemia é desfecho de segurança clínico real:** risco renal, potássio basal e uso concomitante de bloqueadores do SRAA devem permanecer no raciocínio.
5. **Não transportar o resultado para ICFEr:** o ensaio foi desenhado para FEVE ≥40%.
6. **Diretriz posterior ao RCT deve ser citada separadamente:** classe/nível formal da ESC 2026 deve vir da diretriz, não ser inferida do p-valor do ensaio.

## Guardrails para CorVIA

- bloquear `FINEARTS-HF reduziu mortalidade cardiovascular`;
- bloquear `finerenona = espironolactona` sem contextualização;
- exigir monitorização de potássio/função renal no raciocínio clínico, sem automatizar dose;
- diferenciar benefício em eventos de piora de IC de benefício em morte;
- não extrapolar para FEVE <40% com base neste ensaio.

## Resultado

**Achado de alto valor editorial:** o desfecho composto do FINEARTS-HF é positivo, mas a mortalidade cardiovascular isolada não foi significativamente reduzida. Qualquer síntese que descreva “redução de mortalidade” precisa ser corrigida.

Nenhum arquivo clínico foi alterado neste pacote; revisão documental apenas.
