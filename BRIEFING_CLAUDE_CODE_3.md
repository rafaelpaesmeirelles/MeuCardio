# Briefing de implementação — Corvia (parte 3: Receituário)

Continuação de `BRIEFING_CLAUDE_CODE.md` e `BRIEFING_CLAUDE_CODE_2.md`. Todas as
regras transversais já definidas nesses documentos continuam valendo (nunca
inventar dado, sinalizar incerteza, dado de saúde exige storage seguro e LGPD,
apresentar plano antes de tarefa grande, nunca simular etapa que depende de
credencial/definição externa).

Numeração continua a partir da Tarefa 26.

**Nota:** a ideia de prontuário eletrônico do paciente (evolução diária assinada
digitalmente, interligada à agenda) foi cogitada e fica arquivada por enquanto —
não faz parte deste briefing. Não iniciar essa frente sem novo pedido explícito.

## 27. Escolha entre receituário comum e de controle especial

Ao gerar uma receita (Tarefa 4), o sistema deve oferecer explicitamente duas
opções: receituário comum e receituário de controle especial, com o formato
correto por trás de cada uma — não é só um rótulo diferente na mesma estrutura
de documento.

### O que rege isso, e por que precisa de atenção

A Portaria SVS/MS nº 344/98 (com alterações recentes pela RDC ANVISA nº
1.000/2026, em vigor desde 13/02/2026) define o regime. Não é um formato único —
o tipo de documento correto depende da lista em que a substância prescrita se
enquadra:

- **Notificação de Receita**, em três cores conforme a substância: amarela
  (entorpecentes, lista A), azul (psicotrópicos, lista B), branca (retinóides de
  uso sistêmico e talidomida).
- **Receita de Controle Especial**, também branca, preenchida em 2 vias, para
  substâncias das listas C1, C5 e determinados adendos das listas A1, A2 e B1 —
  formato diferente da Notificação de Receita, não confundir os dois.

**Ponto de atenção que pode estar mudando agora mesmo:** a RDC 1.000/2026
introduziu a possibilidade de notificação de receita em formato eletrônico, com
ferramenta oficial da própria ANVISA cujo lançamento estava previsto para até
01/06/2026. Antes de definir se o Corvia gera um PDF que replica o formulário em
papel ou se integra com a notificação eletrônica oficial, confirme o status atual
dessa ferramenta da ANVISA — pode já estar disponível, dependendo de quando esta
tarefa for executada. Não presuma um caminho sem checar.

### Campos obrigatórios a considerar no desenho
*(não exaustivo — confirmar lista completa com a fonte oficial antes de finalizar)*

- Identificação do prescritor com inscrição no Conselho Regional (já existe no
  sistema, reaproveitar).
- Controle de numeração sequencial do talão/notificação — isso é uma exigência
  estrutural, não cosmética; a distribuição da numeração segue instrução
  normativa própria.
- Em caso de atendimento de urgência com receituário não-oficial: diagnóstico ou
  CID, justificativa do caráter emergencial, data, inscrição no conselho e
  assinatura identificada são obrigatórios no próprio texto da receita.
- Duas vias com destinação declarada quando aplicável ("1ª via — retenção da
  farmácia", "2ª via — orientação ao paciente").

### O que NÃO fazer sem aprovação explícita do Rafael

- Não tratar "receita de controle especial" como a receita comum com um rótulo
  diferente — como já sinalizado antes, isso repetiria um erro que já foi
  evitado uma vez neste projeto.
- Não decidir sozinho entre replicar o formulário em papel (PDF) ou integrar com
  a notificação eletrônica da ANVISA — apresente as duas opções, com o status
  atual da ferramenta da ANVISA, para o Rafael decidir.
- Apresentar o plano de execução antes de começar, como de costume — em especial
  a checagem do status da ferramenta eletrônica da ANVISA, que pode ter mudado
  desde a escrita deste documento.

### Acréscimos do Rafael em 29/07/2026, ao aprovar o plano

- A base substância→lista da 344/98 **precisa estar ligada à mesma base de
  medicamentos** das tarefas de marca comercial, laboratório e preço (Tarefas A
  e B do `CLAUDE.md`), para que o médico já veja essas informações ao digitar o
  remédio, **em qualquer um dos tipos de receita**.
- A classificação de controle especial deve ser **automática a partir do
  medicamento selecionado**. O médico **não escolhe** "comum" ou "controle
  especial" manualmente no fluxo normal, mas **revisa antes de gerar** o
  documento final.
- Tratar o caso de receita com **mais de um medicamento de listas diferentes
  entre si**, gerando os documentos separados que a norma exigir.
- Decisões de LGPD que revertem escolha de privacidade deliberada devem ser
  trazidas **como pergunta própria, com opções claras** — não decididas de
  passagem dentro de outro relatório.
