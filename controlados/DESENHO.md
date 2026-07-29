# Receituário — decisão de modelo (Tarefa 27)

Desenho leve, decisão de estrutura apenas. Não descreve implementação.
Escrito em 29/07/2026, depois de ler o Manual da API do SNCR e a RDC 999/2025.

## O achado que governa o modelo

O tipo de documento **não é função da substância**. É função da **substância mais
a apresentação**. O adendo da Lista A1 diz, literal:

> *"preparações medicamentosas na forma farmacêutica de comprimidos de liberação
> controlada à base de oxicodona, contendo não mais que 40 miligramas dessa
> substância, por unidade posológica, ficam sujeitas a prescrição em RECEITA DE
> CONTROLE ESPECIAL, em 2 (duas) vias"*

Oxicodona é A1 — Notificação de Receita A, amarela. Mas nessa apresentação a
norma manda Receita de Controle Especial, que é outro documento, com outro
endpoint no SNCR e outro regime de numeração. O mesmo vale para difenoxilato com
atropina e para preparações de ópio até 5 mg de morfina por mL.

**Consequência para o modelo:** qualquer desenho do tipo `substancia.lista →
tipo_documento` classifica errado. A regra condicional é parte do modelo, não
detalhe de implementação.

## Quatro entidades, e por que cada uma existe

### 1. `ControlledSubstance` — a substância e sua lista
Dado de referência, versionado, vindo de `controlados/listas-344-98.json`.
Campos: nome, sinônimos, lista (A1…F4), tipo SNCR da lista, se é proscrita,
e a versão da norma de onde veio.

Existe separada porque **muda por RDC**, em ritmo próprio, e precisa de trilha
de qual versão classificou cada receita emitida — mesma lógica do
`cmed_versions` já desenhada na Tarefa A.

### 2. `PrescriptionType` — o tipo de documento
**Tabela de referência, não `enum` no código.** Um registro por tipo:
`NRA`, `NRB`, `NRB2`, `NRR`, `NRT`, `RCE`, `RET`, e o receituário comum.

Cada registro carrega o que difere de fato entre os tipos, que é muito mais que
um rótulo: cor, número de vias e destinação de cada via, se exige numeração do
SNCR e por qual endpoint, tamanho do lote de numeração, limite de emissão,
validade, se exige retenção na farmácia, e os campos obrigatórios próprios.

É tabela e não `enum` porque **a RDC 1.000/2025 já mudou esse conjunto uma vez**
e o SNCR entra em operação em 30/09/2026. Regime que muda por norma não vira
constante de código.

### 3. `PrescriptionRule` — a regra condicional do adendo
Liga substância + condição de apresentação a um tipo de documento que **sobrepõe**
o tipo da lista. Guarda o texto normativo verbatim que a origina.

Enquanto uma regra não estiver codificada, ela existe com
`codificada = false` — e a classificação automática **cai para revisão humana**
em vez de assumir o tipo da lista. Falhar para o lado do médico decidir é a única
falha aceitável aqui.

### 4. `Prescription` → `PrescriptionDocument` — a separação que resolve o resto
`Prescription` é a **intenção clínica**: o conjunto de medicamentos que o médico
quis prescrever naquele atendimento.

`PrescriptionDocument` é **cada documento emitido** a partir dela — um por tipo
exigido, com sua numeração, suas vias e seu snapshot do destinatário.

Essa separação resolve três coisas de uma vez:

- **Receita com listas diferentes**, que você pediu: uma `Prescription` com
  clonazepam (B1) e amoxicilina (comum) produz **dois** `PrescriptionDocument`,
  um NRB e um comum. É consequência do modelo, não caso especial no código.
- **Numeração**, que é por documento e não por prescrição.
- **Snapshot**, porque o documento emitido precisa preservar o que foi impresso,
  mesmo que o cadastro mude depois — mesmo princípio do `pmc_snapshot` da
  Tarefa B.

## Como a classificação roda

1. O médico escolhe o medicamento **na base estruturada** — a mesma que traz
   marca, laboratório e PMC das Tarefas A e B. Nunca texto livre: texto livre não
   é classificável, e chutar aqui é o erro que a tarefa existe para evitar.
2. O sistema resolve substância → lista → tipo da lista.
3. Aplica as `PrescriptionRule` que casem com a apresentação. Se alguma regra da
   lista for aplicável mas **não estiver codificada**, marca o item como
   "precisa de revisão" em vez de classificar.
4. Agrupa os itens por tipo resultante e monta um `PrescriptionDocument` por grupo.
5. **Apresenta tudo para o médico revisar antes de emitir.** Ele não escolhe o
   tipo; confirma ou corrige. Correção manual fica registrada, com o motivo.

Substância proscrita (E, F1–F4) não é classificada: é **recusada**, com o texto
da norma que a proscreve.

## O que este desenho deliberadamente não resolve

- **Assinatura digital** — segue na Tarefa 4, parada na credencial VIDAAS.
- **Geração de PDF** — não existe no sistema; a escolha do renderizador é a mesma
  decisão pendente da Tarefa C.
- **Numeração real** — depende do cadastro do Rafael no SNCR, que ele começou a
  providenciar em 30/07/2026. Até lá, nenhuma chamada de numeração é feita, e
  nada é simulado.
- **Dado identificável do paciente** — decidido em 29/07/2026: entidade separada
  e cifrada com o padrão do Cofre. O `Patient` do round segue anonimizado.
