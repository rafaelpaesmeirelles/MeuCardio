# CorVIA 100 pacotes — 043/100 — Vericiguat: VICTORIA, VICTOR e hierarquia de desfechos

Data: 29/08/2026  
Base auditada: `main` `59566e1196e0fa7f465df93516790ef454e1f565`

## Objetivo

Revisar adversarialmente a evidência do vericiguat na ICFEr após VICTORIA e VICTOR, distinguindo populações, desfecho primário, componentes secundários e análise combinada. O foco é impedir que um componente secundário favorável de um ensaio com primário neutro seja apresentado como se o ensaio inteiro tivesse sido positivo.

## Evidência crítica verificada

- **VICTORIA** — Armstrong PW et al. N Engl J Med. 2020;382:1883-1893. PMID `32222134`; DOI `10.1056/NEJMoa1915928`.
  - 5.050 pacientes com IC sintomática, FEVE <45%, alto risco e piora recente de IC.
  - Vericiguat até 10 mg/dia versus placebo, além do tratamento padrão.
  - Morte CV ou primeira hospitalização por IC: 35,5% vs 38,5%; HR 0,90 (IC95% 0,82-0,98; p=0,02).
  - Morte CV isolada: HR 0,93 (IC95% 0,81-1,06), sem redução estatisticamente significativa.
- **VICTOR** — O'Connor CM et al. Lancet. 2025;406:1341-1350. PMID `40897189`; DOI `10.1016/S0140-6736(25)01665-4`.
  - 6.105 pacientes com ICFEr ≤40% **sem piora recente**.
  - Morte CV ou hospitalização por IC: 18,0% vs 19,1%; HR 0,93 (IC95% 0,83-1,04; p=0,22): primário neutro.
  - Como pré-especificado, análises secundárias/exploratórias devem ser consideradas nominais após o primário neutro.
  - Morte CV: HR 0,83 (IC95% 0,71-0,97); hospitalização por IC: HR 0,95 (IC95% 0,82-1,10).
- **Análise individual combinada VICTORIA + VICTOR** — Zannad F et al. Lancet. 2025;406:1351-1362. PMID `40897188`; DOI `10.1016/S0140-6736(25)01682-4`.
  - 11.155 pacientes.
  - Morte CV ou hospitalização por IC: HR 0,91 (IC95% 0,85-0,98; p=0,0088).
  - Morte CV como primeiro evento: HR 0,89 (IC95% 0,80-0,98); hospitalização por IC: HR 0,92 (IC95% 0,84-1,00).
- **ESC 2026 Heart Failure Guidelines** — Køber L et al. Eur Heart J. Publicada em 28/08/2026; DOI `10.1093/eurheartj/ehag100`. Esta é a diretriz europeia vigente a ser consultada para qualquer classe/nível atual; este pacote não infere classe a partir dos RCTs.

## Revisão adversarial independente

1. **VICTORIA e VICTOR testaram populações diferentes:** piora recente/alto risco versus pacientes ambulatoriais sem piora recente.
2. **VICTOR teve primário neutro:** o achado favorável de morte CV é clinicamente importante, porém permanece secundário dentro de um ensaio cujo endpoint primário não atingiu significância.
3. **Análise combinada não apaga a hierarquia dos ensaios individuais:** o pooling amplia precisão e informa o espectro de risco, mas não transforma retroativamente o primário do VICTOR em positivo.
4. **VICTORIA não provou mortalidade CV isolada:** benefício do composto foi principalmente associado à redução de eventos de IC; não escrever `VICTORIA reduziu mortalidade`.
5. **Vericiguat não substitui terapia fundacional:** a pergunta é adição em paciente selecionado, não troca de ARNI/IECA/BRA, betabloqueador, antagonista mineralocorticoide ou iSGLT2.
6. **Classe e nível são atributos da diretriz:** a ESC 2026 foi publicada em 28/08/2026; qualquer classificação vigente deve ser lida diretamente nesse documento e não deduzida de HR/p-valor.

## Guardrails para CorVIA

- bloquear `VICTOR foi positivo para o primário`;
- bloquear `VICTORIA reduziu morte cardiovascular isoladamente`;
- se citar mortalidade do VICTOR, rotular como endpoint secundário/nominal no contexto do primário neutro;
- diferenciar claramente piora recente de IC versus estabilidade ambulatorial;
- não apresentar o pooling VICTORIA+VICTOR como terceiro RCT independente;
- preservar terapia fundacional antes de discutir tratamento adicional;
- classe/nível somente se conferidos na diretriz original vigente.

## Resultado

Gap editorial fechado: **a evidência do vericiguat é coerente com benefício adicional em ICFEr selecionada, mas VICTORIA e VICTOR não podem ser resumidos da mesma maneira; o VICTOR teve endpoint primário neutro apesar do sinal favorável de mortalidade secundária**.

Nenhum arquivo clínico, dose, slug, JSON ou regra determinística foi alterado neste pacote.
