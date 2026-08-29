# Novo registro de Triagem de Sintomas — "Tontura/vertigem persistente" (29/08/2026)

## O que foi feito

Criado o registro novo `tontura-vertigem-persistente` em
`triagem-sintomas/metadados.json` (manifesto de Triagem de Sintomas, schema e
motor de regras próprios — **não é o Guia de Doenças** em `doencas/metadados.json`).
O registro foi adicionado ao **final** do array JSON, por edição direta (não
existe mecanismo de fragmentos para este manifesto), preservando a formatação
e indentação já usadas no arquivo.

## Distinção do registro já existente "sincope-e-pre-sincope"

- `sincope-e-pre-sincope` exige perda completa de consciência (síncope) ou
  sensação iminente dela (pré-síncope).
- `tontura-vertigem-persistente` cobre tontura/vertigem crônica ou
  recorrente **sem** perda de consciência, com diferencial entre:
  - causa vestibular (desencadeada por movimento da cabeça, nistagmo,
    zumbido, perda auditiva, infecção viral recente);
  - causa ortostática/hipotensiva (piora ao levantar, uso de
    anti-hipertensivo/diurético, desidratação/perda de volume) — com ênfase
    geriátrica, já que a hipotensão ortostática é mais prevalente e mais
    perigosa (risco de queda) no idoso;
  - causa cardiovascular (palpitações, arritmia ou cardiopatia estrutural
    conhecida);
  - causa metabólica (hipoglicemia relacionada a jejum/insulina, anemia);
  - efeito medicamentoso (início/aumento recente de fármaco).
- Quando o episódio relatado inclui perda completa de consciência, a regra
  `perda-consciencia-associada` eleva o risco para `emergencia` e a
  mensagem gerada orienta explicitamente usar a triagem
  `sincope-e-pre-sincope` em complemento a esta — os dois registros não se
  sobrepõem, mas se referenciam.

## Red flags e regras de segurança

Red flags cobertos (cada um eleva o risco para pelo menos `urgente`
automaticamente no motor de regras, `clinical_rule_engine.evaluate_rules`,
sem necessidade de duplicar essa lógica na regra):

- Déficit neurológico focal (`deficit-neurologico-focal`, priority 100) —
  possível AVC/AIT de fossa posterior, diferencial explícito com vertigem
  periférica benigna.
- Cefaleia súbita e intensa (`cefaleia-subita-intensa`, priority 98).
- Perda de consciência associada (`perda-consciencia-associada`,
  priority 97) — redireciona ao protocolo de síncope.
- Dor torácica ou dispneia associada (`dor-toracica-ou-dispneia`,
  priority 95) — possível síndrome coronariana aguda/embolia pulmonar.
- Palpitações ou arritmia/cardiopatia conhecida
  (`arritmia-ou-palpitacao`, priority 90).
- Queda ou lesão associada (`queda-ou-lesao-associada`, priority 70).

Regras de suporte (risco `prioritario`/`rotina`) cobrem hipotensão
ortostática no idoso e medicamentosa, depleção de volume, neuropatia
autonômica cardiovascular diabética, hipoglicemia, anemia, medicamento novo
e causa vestibular periférica (posicional ou com sintomas auditivos/viral).

`emergency_flow` orienta explicitamente buscar avaliação de emergência
diante de qualquer um dos red flags, sem atribuir o quadro a causa
vestibular benigna antes de excluí-los.

Nenhuma dose de fármaco em nenhum campo.

## Fontes

Conteúdo derivado de quatro documentos já publicados e revisados nesta base
(sem consulta a fonte nova):

- `content/Síncope/fluxograma-hipotensao-ortostatica-diagnostico-causa-e-manejo-escalonado.md`
- `content/Síncope/fluxograma-sincope-reflexa-versus-cardiaca-diagnostico-diferencial.md`
- `content/Síncope/fluxograma-sincope-idoso-investigacao-diferenciada.md`
- `content/Diabetes_e_cardiologia/fluxograma-investigacao-neuropatia-autonomica-cardiovascular-diabetico.md`

Os 5 PMIDs citados em `source_refs` foram reconferidos individualmente via
PubMed E-utilities (`esummary.fcgi`) nesta produção: 29562304 (ESC 2018
Guidelines for Syncope), 21431947 (Freeman 2011, consenso de definições de
HO/POTS), 25980576 (HRS 2015, consenso de POTS), 41358886 (ADA Standards of
Care in Diabetes—2026, Recomendação 12.19) e 39941342 (Gogan 2025, bateria
de Ewing e estratificação da NAC).

## Status editorial e gate de review_status

`review_status: "pendente_revisao"` (revisão médica humana ainda não
realizada), com `review_note` explicando a origem do conteúdo e a distinção
do registro `sincope-e-pre-sincope`.

**Consequência esperada e não contornada:**
`backend/tests/test_canonical_content_review_status.py::test_manifestos_canonicos_so_tem_pendencias_explicitamente_aprovadas_para_rc`
**falha** para o slug `tontura-vertigem-persistente`, porque o gate só
permite `pendente_revisao`/`lacuna_declarada` em manifestos canônicos
mediante decisão editorial explícita do Rafael (allowlist vazia por
padrão). Essa falha é o comportamento correto e esperado — não deve ser
contornada.

Investigamos se existe, para `triagem-sintomas/metadados.json`, uma
allowlist equivalente à usada para `doencas/metadados.json` (padrão do PR
#698, branch `claude/novo-verbete-cardiomiopatia-de-takotsubo-20260829`):
não existe. No caso de `doencas`, a allowlist `PENDENTES_LOTES_TUDO_COM_TUDO`
é reaproveitada por um segundo teste,
`test_disease_fragments_canonical.py`, cuja checagem (diferente da checagem
principal) considera a allowlist mesmo para registros com
`review_status != "revisado"`. Não existe teste análogo para
`triagem-sintomas/metadados.json` (não há mecanismo de fragmentos para este
manifesto), e a checagem principal do gate só consulta a allowlist para
registros já com `status == "revisado"` — ou seja, adicionar uma entrada a
`PENDENTES_LOTES_TUDO_COM_TUDO["triagem-sintomas/metadados.json"]` não
mudaria o resultado da falha esperada. Por isso `test_canonical_content_review_status.py`
**não foi alterado**; a expectativa de falha fica documentada aqui e travada
pelo teste dedicado
`backend/tests/test_novo_sintoma_tontura_vertigem_persistente.py::test_gate_de_review_status_falha_como_esperado_e_documentado`.

## Gates executados

- `backend/tests/test_novo_sintoma_tontura_vertigem_persistente.py` (teste
  dedicado, novo) — schema, red flags/emergency_flow não vazios, nenhuma
  dose de fármaco, acentuação, regras determinísticas seguras em cenários
  simulados.
- `backend/tests/test_specialty_guides.py::test_triage_manifest_has_two_flows_and_special_populations`
  — segue passando (mínimo de 15 registros; agora com 19).
- `backend/tests/test_canonical_content_review_status.py` — falha esperada
  e documentada para este slug (ver acima); demais asserções do arquivo
  continuam passando.
- `python -c "import app.main"` — sanity de import.
- Loader `backend/app/services/carregar_triagem_sintomas.py` executado
  manualmente contra `DATABASE_URL` de teste: carregou os 19 registros sem
  erro (`{"novos": 19, "atualizados": 0}`).

## Risco de colisão de merge

Outros agentes estavam adicionando, em paralelo, novos registros ao mesmo
arquivo `triagem-sintomas/metadados.json` em branches diferentes. Para
minimizar conflito, este registro foi inserido apenas ao final do array,
sem tocar em nenhum registro existente — mas o merge de múltiplos PRs
concorrentes sobre o mesmo arquivo pode ainda assim gerar conflito de
merge, cuja resolução cabe à revisão humana.

## O que NÃO foi feito

- Nenhum merge, nenhum deploy.
- Nenhuma allowlist de `review_status` foi adicionada (ver seção acima).
