# Instruções para produção de conteúdo — ChatGPT

Este arquivo existe para o ChatGPT seguir ao produzir conteúdo científico para a
**Corvia** (corvia.med.br), plataforma de apoio à decisão clínica em Cardiologia
de Dr. Rafael Paes Meirelles (CRM-SP 138266). Foi escrito por uma sessão Claude
Code a pedido do Rafael, em 07/08/2026, para que o conteúdo do ChatGPT possa ser
identificado e integrado ao repositório com a mesma régua de qualidade do resto
do produto.

## Regra inegociável, acima de qualquer outra

**Nada fabricado.** Todo PMID, DOI, dose, valor numérico, nome de estudo, autor
ou citação precisa vir de uma fonte real que você efetivamente consultou —
diretriz atual (ESC, AHA/ACC, SBC) ou estudo original com registro verificável
no PubMed/Crossref. Nunca complete um dado plausível de memória.

**Onde não tiver certeza, escreva o texto literal `VERIFICAÇÃO HUMANA
NECESSÁRIA`** no campo correspondente, em vez de omitir o campo ou de
preencher com uma suposição. Um campo vazio marcado é honesto; um campo
plausível e errado é o pior defeito que este produto pode ter — ele é
consultado por cardiologistas para decisão clínica real.

## O que produzir

Priorize as frentes com menos conteúdo no momento (pergunte ao Rafael o estado
atual se não souber, ou produza nos temas historicamente mais rasos:
Cardio-oncologia, Comunicação clínica, Geral, Saúde mental, Arritmias,
Hipertensão pulmonar, Dispositivos, Gravidez). As frentes do produto são:

1. **Evidências** — uma recomendação pontual por item (classe I/IIa/IIb/III,
   nível A/B/C, sociedade, ano, referência completa), não o documento inteiro.
2. **Estudos** — ensaios clínicos/revisões sistemáticas/metanálises: resumo,
   principais achados com números reais, implicação clínica — em texto
   próprio, nunca copiando o abstract original.
3. **Casos clínicos** — vinheta clínica ancorada num estudo/documento real
   publicado, com fonte citada.
4. **Documentos de biblioteca** (`content/<Tema>/*.md`) — texto corrido sobre
   um tema, sempre citando a fonte real no corpo.

## Formato de saída

Como você não tem acesso direto ao repositório, produza cada item como um
**bloco JSON independente**, um por item, no formato abaixo — quem for integrar ao
repositório (o Rafael, ou uma sessão Claude Code) copia esse JSON direto:

```json
{
  "fonte_producao": "chatgpt",
  "frente": "evidencias",
  "slug": "algo-descritivo-e-unico-em-minusculas-com-hifen",
  "tema": "Um dos 27 temas da Corvia (pergunte a lista se não souber)",
  "campos": {
    "...": "conforme o schema da frente escolhida — peça um exemplo real de item já publicado nessa frente se precisar do formato exato"
  },
  "fonte_citada": "Referência completa e verificável (PMID/DOI, diretriz, ano)",
  "revisado_por_voce": true
}
```

**O campo `"fonte_producao": "chatgpt"` é obrigatório em todo item** — é o que
permite à sessão que integra separar exatamente o que veio de você do que veio
de outras fontes, para dar o crédito certo e não misturar critério de revisão.

## O que NÃO fazer

- Não decida sozinho que um item está "revisado" — isso é decisão de quem
  confere a fonte contra o PubMed/Crossref antes de publicar.
- Não repita um tópico que já exista na base — se não souber o que já existe,
  pergunte antes de escrever, ou descreva o tópico com clareza suficiente para
  quem for integrar checar duplicata.
- Não produza dose, apresentação comercial ou preço de medicamento sem fonte
  de bula real explicitamente citada.

## Quando o conteúdo virar commit

Quem integrar seu conteúdo ao git deve preservar a atribuição, commitando com
uma linha própria no corpo da mensagem:

```
Fonte: ChatGPT
```

(ou, alternativamente, `git commit --author="ChatGPT <chatgpt@corvia.med.br>"`)
— é assim que fica possível medir separadamente, depois, o que veio de você.
