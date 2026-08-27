---
title: "Acidose Metabólica na UCO: Compensação Respiratória e Ânion Gap"
slug: acidose-metabolica-compensacao-respiratoria-e-anion-gap-na-uco
theme: "Terapia intensiva"
kind: protocolo
review_status: revisado
fonte_producao: chatgpt
source_refs: ["Albert MS, Dell RB, Winters RW. Quantitative displacement of acid-base equilibrium in metabolic acidosis. Ann Intern Med. 1967;66(2):312-322. DOI: 10.7326/0003-4819-66-2-312. PMID: 6016545 — estudo original que fundamenta a relação quantitativa entre bicarbonato e PaCO2 na acidose metabólica", "Figge J, Jabor A, Kazda A, Fencl V. Anion gap and hypoalbuminemia. Crit Care Med. 1998;26(11):1807-1810. DOI: 10.1097/00003246-199811000-00019. PMID: 9824071 — estudo observacional original: 9 controles e 152 pacientes críticos, 265 medidas; derivou correção de 0,25 mEq/L por g/L de albumina (2,5 por g/dL)", "American Thoracic Society. Interpretation of Arterial Blood Gases (ABGs). Clinical Education resource. Consultado em 27/08/2026 — recurso oficial da sociedade: abordagem em seis passos, pH, fórmula de Winter, ânion gap e limites da compensação. https://www.thoracic.org/professionals/clinical-resources/critical-care/clinical-education/abgs.php"]
review_note: "Lote técnico produzido em 27/08/2026 a partir de dois estudos originais e do recurso educacional oficial da ATS. Fórmulas e limites foram conferidos nas fontes; publicação clínica permanece dependente de revisão humana."
---

# Acidose Metabólica na UCO: Compensação Respiratória e Ânion Gap

## Função deste protocolo

Este protocolo organiza uma pergunta limitada: **quando a acidose metabólica já
foi estabelecida clinicamente**, a PaCO₂ observada é compatível com a compensação
respiratória esperada e há ânion gap que exige investigação de ânions não medidos?

Ele não decide sozinho qual é o distúrbio primário, não identifica a causa da
acidose e não prescreve bicarbonato, ventilação ou diálise. Um pH normal também
não exclui acidose: distúrbios mistos podem aproximar o pH da faixa de referência.

## Dados que precisam representar o mesmo momento clínico

- pH e PaCO₂ da gasometria;
- bicarbonato usado no cálculo;
- sódio e cloro para o ânion gap;
- albumina, quando disponível, para corrigir o efeito da hipoalbuminemia;
- intervalo de referência do ânion gap do próprio laboratório.

Sempre que possível, use gasometria, eletrólitos e albumina colhidos no mesmo
momento. Mudança de ventilação, reposição, diálise ou intervalo entre amostras pode
criar uma relação matemática que nunca existiu simultaneamente no paciente.

## Passo 1 — estado do pH

A ATS usa os seguintes descritores:

- pH abaixo de 7,35: **acidemia**;
- pH acima de 7,45: **alcalemia**;
- pH de 7,35 a 7,45: faixa usual, sem excluir distúrbio misto.

“Acidose” é o processo; “acidemia” é o estado do pH. A calculadora preserva essa
diferença e não transforma pH isolado em diagnóstico etiológico.

## Passo 2 — compensação respiratória esperada

Para acidose metabólica, a relação de Albert, Dell e Winters é apresentada pela
ATS como:

**PaCO₂ esperada (mmHg) = 1,5 × HCO₃⁻ + 8 ± 2.**

Interpretação operacional:

| PaCO₂ observada | Leitura segura |
|---|---|
| Dentro da faixa | Compatível com compensação esperada; não prova distúrbio simples |
| Abaixo da faixa | Considerar alcalose respiratória associada e conferir contexto/amostra |
| Acima da faixa | Considerar acidose respiratória associada e conferir contexto/amostra |

“Considerar” é deliberado. Dor, sepse, hipóxia, gestação, hepatopatia, intoxicação,
ventilação mecânica e mudança temporal podem deslocar a PaCO₂. A fórmula sinaliza
discordância; o médico estabelece ou não o diagnóstico misto.

## Passo 3 — ânion gap sem potássio

**AG sem potássio = Na⁺ − (Cl⁻ + HCO₃⁻).**

A ferramenta não impõe um limite universal. Intervalos mudam com analisador,
calibração e inclusão ou não de potássio. Por isso, o alerta de “elevado” só é
gerado quando o usuário informa e confirma o limite superior do método
laboratorial **sem potássio**. Intervalo que inclui K⁺ não é comparável a este
cálculo e é bloqueado pela ferramenta.

## Passo 4 — correção opcional por albumina

No estudo original de Figge et al., 49% dos pacientes críticos tinham albumina
abaixo de 20 g/L. Cada redução de 1 g/L fez o AG observado subestimar os ânions de
gap em 0,25 mEq/L (r² = 0,94). Em g/dL, o fator é 2,5:

**AG corrigido = AG observado + 2,5 × (albumina de referência − albumina
observada).**

A ferramenta permite selecionar 4,0 ou 4,4 g/dL como referência, porque esse
valor deve acompanhar o padrão usado pelo serviço. Corrigir o AG não identifica
o ânion acumulado: lactato, cetonas, função renal e toxicologia continuam sendo
investigações clínicas separadas.

## Exemplo auditável

Com pH 7,25, PaCO₂ 26 mmHg, HCO₃⁻ 12 mEq/L, Na⁺ 140 mEq/L e Cl⁻ 104 mEq/L:

- Winter: centro = 1,5 × 12 + 8 = 26 mmHg; faixa = 24–28 mmHg;
- PaCO₂ observada de 26 mmHg: compatível com a faixa esperada;
- AG sem K = 140 − (104 + 12) = 24 mEq/L;
- se albumina = 2,0 g/dL e referência = 4,0 g/dL, AG corrigido = 29 mEq/L.

O exemplo confirma a aritmética, não define a causa nem uma conduta terapêutica.

## Gates antes de agir

1. Confirmar que a acidose metabólica foi estabelecida no conjunto clínico.
2. Conferir identidade, horário, tipo de amostra e coerência entre pH, PaCO₂ e bicarbonato.
3. Comparar o AG com o método e o intervalo do laboratório local.
4. Dosar/investigar a causa provável: lactato, cetonas, função renal e tóxicos conforme contexto.
5. Repetir gasometria após mudança relevante; não reutilizar relação prévia após ajuste ventilatório.
6. Registrar que “compensação compatível” não exclui outro distúrbio misto.

## Conexões Tudo com Tudo

### Vínculo clínico direto

- [Acidose lática associada à metformina](acidose-latica-associada-a-metformina-mala-no-paciente-critico-cardiovascular.md): quadro de UTI no qual pH, compensação e AG fazem parte da avaliação, sem substituir lactato e critérios do EXTRIP.
- [Cetoacidose euglicêmica associada a iSGLT2](../Diabetes_e_cardiologia/cetoacidose-euglicemica-associada-a-inibidores-de-sglt2.md): acidose metabólica com AG pode ocorrer sem hiperglicemia marcada; a calculadora não substitui cetonas.
- [Calculadora de lesão renal aguda KDIGO na UCO](/calculadoras/lesao-renal-aguda-kdigo-uco): LRA pode contribuir para retenção de ácidos; creatinina e diurese respondem à lesão renal, enquanto Winter e AG respondem ao distúrbio ácido-base.

### Proximidade temática, sem vínculo causal automático

- [Classificação SCAI do choque cardiogênico](classificacao-scai-de-estagios-do-choque-cardiogenico.md): pH baixo pode acompanhar choque grave, mas não define estágio nem etiologia da acidose isoladamente.

Não foram criados vínculos com medicamento, exame específico, caso clínico,
emergência ou checklist quando o corpus não oferecia uma relação bidirecional
explícita e defensável para esta ferramenta.

## Limitações

- A fórmula de Winter foi derivada para acidose metabólica; não deve ser aplicada como regra de compensação para alcalose metabólica ou distúrbio respiratório primário.
- Bicarbonato calculado na gasometria e bicarbonato/CO₂ total da química podem divergir; documente qual foi usado.
- O AG sem potássio depende de medidas laboratoriais e pode ser negativo sem que isso autorize correção manual do dado.
- Hipoalbuminemia pode mascarar AG aumentado; a correção reduz esse viés, mas não substitui mensuração de lactato ou cetonas.
- Resultado matemático não seleciona bicarbonato, intubação, ajuste de ventilador ou terapia renal substitutiva.

## Referências primárias e institucionais

1. Albert MS, Dell RB, Winters RW. *Quantitative displacement of acid-base equilibrium in metabolic acidosis*. Ann Intern Med. 1967;66:312-322. DOI: 10.7326/0003-4819-66-2-312. PMID: 6016545.
2. Figge J, Jabor A, Kazda A, Fencl V. *Anion gap and hypoalbuminemia*. Crit Care Med. 1998;26:1807-1810. DOI: 10.1097/00003246-199811000-00019. PMID: 9824071.
3. American Thoracic Society. *Interpretation of Arterial Blood Gases (ABGs)*. Recurso educacional oficial, consultado em 27/08/2026.
