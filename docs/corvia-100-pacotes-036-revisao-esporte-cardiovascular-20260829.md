# CorVIA 100 pacotes — 036/100 — Participação esportiva e doença cardiovascular

Data: 29/08/2026  
Base: `main` `59566e1196e0fa7f465df93516790ef454e1f565`

## Objetivo

Revisão adversarial do eixo de cardiologia do esporte e elegibilidade para exercício competitivo, com foco na mudança contemporânea de proibições categóricas para avaliação individualizada e decisão compartilhada.

## Evidência crítica

- **AHA/ACC Scientific Statement 2025 — Clinical Considerations for Competitive Sports Participation for Athletes With Cardiovascular Abnormalities** — Circulation. 2025;151:e716-e761; DOI `10.1161/CIR.0000000000001297`. O documento enfatiza avaliação específica por doença, risco contextual e shared decision-making, substituindo a lógica histórica de desqualificação universal.
- O statement cobre cardiomiopatias, miocardite/pericardite, valvopatias, cardiopatias congênitas, aortopatias/SCAD, arritmias/dispositivos, canalopatias, masters athletes e outros cenários.

## Revisão adversarial

1. **Diagnóstico ≠ desqualificação automática:** várias condições antes tratadas com proibição ampla exigem hoje estratificação individualizada.
2. **Shared decision-making ≠ liberação automática:** decisão compartilhada ocorre depois de caracterização do risco e não elimina contraindicações ou sinais de alto risco.
3. **Atleta não é sinônimo de exercício recreacional:** intensidade, componente de endurance/força, competição, ambiente e possibilidade de síncope/trauma modificam risco.
4. **Um exame normal isolado não “libera”:** ECG, eco, RM, teste de esforço e monitorização têm papéis diferentes conforme a doença.
5. **CDI não torna esporte automaticamente seguro nem automaticamente proibido:** doença de base, histórico de arritmia, programação, risco de choque e modalidade esportiva precisam ser considerados.
6. **Retorno após miocardite/pericardite exige reavaliação clínica:** não inferir liberação por tempo decorrido isoladamente.
7. **Masters athletes têm perfil etiológico distinto:** doença coronariana assume maior importância com idade; não transportar algoritmos de atleta jovem sem adaptação.

## Guardrails para CorVIA

- bloquear `diagnóstico X = proibido esporte para sempre` quando a diretriz contemporânea prevê decisão individualizada;
- bloquear também `shared decision-making = pode competir` sem estratificação prévia;
- não usar um único achado de ECG, FEVE, espessura parietal ou carga de ectopia como decisão universal;
- separar exercício terapêutico, atividade recreacional e competição;
- considerar tipo de esporte e consequências de perda súbita de consciência;
- em canalopatias/cardiomiopatias, preservar análise de genótipo/fenótipo, sintomas, história familiar e eventos prévios quando relevantes.

## Resultado

O corpus já contém extensa produção em cardiologia do esporte. O principal ponto de governança é alinhar os fluxos à abordagem AHA/ACC 2025: **menos proibições automáticas, mas sem transformar decisão compartilhada em autorização automática**.

Nenhum arquivo clínico foi alterado neste pacote; revisão documental apenas.
