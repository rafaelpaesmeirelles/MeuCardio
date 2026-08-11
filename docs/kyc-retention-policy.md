# Política de retenção de documentos KYC — pendência de decisão

Registro de auditoria e estrutura — issue #52 (hardening de segurança), 11/08/2026. **Este
documento não define prazo nenhum** — define o que já existe, o que falta decidir, e a estrutura
já pronta para aplicar a decisão assim que ela existir.

## 1. Estado atual, confirmado por leitura de código

- **Nenhuma exclusão automática de documento KYC existe hoje**, exceto uma: quando o titular
  reenvia a verificação (`POST /api/kyc/submeter` uma segunda vez), os arquivos da submissão
  anterior são apagados do cofre (`app/services/kyc/verificacao.py::submeter`) — isso é
  substituição, não retenção por prazo, e já está auditado (`AuditLog action="kyc_delete"`,
  adicionado neste hardening).
- Documento aprovado, rejeitado ou aguardando revisão **fica indefinidamente** no cofre
  (`kycfiles`, AES-256-GCM) até o titular reenviar ou até uma ação manual futura.
- `backend/app/commands/kyc_retention_relatorio.py` (novo, este hardening) — relatório **somente
  leitura**: por registro, status, há quantos dias desde a última mudança de status, quantos
  arquivos ainda existem no cofre. Roda com `python -m app.commands.kyc_retention_relatorio`.
  **Nunca apaga nada** — existe para dar visibilidade real do volume acumulado antes de qualquer
  decisão de prazo, e para servir de esqueleto de onde uma rotina de exclusão futura se encaixaria.

## 2. O que falta decidir — PENDÊNCIA DE POLÍTICA, decisão do Rafael

O pedido desta fase sugere a estrutura de três fases, e ela é tecnicamente sã, mas **os prazos
concretos não foram definidos por ninguém com autoridade para isso, e este hardening não os
inventa**:

1. **Durante a análise** (`aguardando_revisao`, `liberado_conselho_ok`, `liberado_sem_checagem`):
   manter os arquivos — óbvio, a revisão precisa deles.
2. **Depois da aprovação definitiva** (`status == "aprovado"`): manter por um período definido —
   **quanto tempo, não está decidido.** Pode haver obrigação regulatória (ex.: guarda de
   documento de identificação por N anos, exigência de algum órgão de classe ou legislação de
   proteção de dados) que este hardening não tem competência para determinar sozinho.
3. **Depois desse período**: apagar os arquivos sensíveis (documento + selfie), preservando só
   metadados mínimos de verificação (que já são só texto — status, datas, `nota_revisao` — nunca
   os bytes do documento em si).

**Perguntas concretas em aberto, que precisam de resposta humana antes de qualquer exclusão
automática:**

- Depois de quantos dias/meses/anos após `aprovado_em` os arquivos de um registro **aprovado**
  podem ser apagados?
- Um registro **rejeitado** tem prazo diferente? (Hoje `rejeitado` não zera `aprovado_em`
  porque nunca foi setado — mas o titular normalmente reenvia depois de uma rejeição, então o
  registro rejeitado tende a ser substituído, não a acumular por muito tempo.)
- Existe alguma obrigação legal/contratual (CFM, LGPD, contrato de prestação de serviço) que
  IMPEÇA excluir antes de um prazo mínimo, mesmo que o produto preferisse excluir antes?
- Quem autoriza a exclusão definitiva — é automática por cron, ou precisa de confirmação humana
  a cada rodada (mesmo padrão de "nunca automatizar ação destrutiva sem revisão" já em vigor
  neste projeto para outras frentes)?

## 3. O que a estrutura já pronta permite, assim que a decisão vier

Com a resposta às perguntas acima, a implementação da exclusão automática é pequena, porque os
dados necessários já existem no schema atual (nenhuma migração é estritamente necessária):

- Filtrar `KycVerification.status == "aprovado"` e `aprovado_em` mais antigo que o prazo decidido
  (ou `atualizado_em` para `rejeitado`, se a decisão cobrir esse caso também).
- Para cada um, chamar `cofre.apagar()` em cada campo de documento (mesmo padrão já usado na
  substituição por reenvio), **e gravar `AuditLog(action="kyc_delete", detail={"motivo":
  "retencao_expirada", ...})`** — a ação de auditoria já existe (adicionada neste hardening),
  só falta o gatilho automático.
- Depois de apagar, os campos de nome de arquivo (`doc_profissional_frente` etc.) ficam `None`
  — mas o registro `KycVerification` em si (status, datas, decisão do revisor) permanece, que é
  exatamente "preservar apenas metadados mínimos" pedido.
- O comando `kyc_retention_relatorio.py` já criado é o esqueleto natural para virar
  `kyc_retention_aplicar.py` (ou um flag `--aplicar` no mesmo arquivo) no dia em que a política
  for decidida — mesmo padrão operacional já usado no projeto para `infra/backup_freshness_cron.sh`
  (script pronto, documentado, não instalado automaticamente até decisão/necessidade confirmada).

## 4. Por que não implementar um prazo "razoável" por conta própria

A régua deste projeto, reafirmada nesta mesma fase, é explícita: "se não houver decisão humana
sobre prazo, não inventar." Um prazo arbitrário (ex.: "2 anos") poderia estar errado em qualquer
direção — curto demais para uma obrigação regulatória real, ou longo demais para o que a LGPD
consideraria proporcional ao propósito da coleta (minimização de dados). Nenhuma das duas
alternativas é aceitável para dado de identidade de titular real. Fica registrado aqui como
pendência explícita, não escondida — o oposto de "esconder vulnerabilidade como pendência", que
este hardening foi instruído a nunca fazer: **isto não é uma vulnerabilidade, é uma decisão de
produto/jurídica que ninguém tomou ainda**, e a ausência de exclusão automática hoje é o estado
mais seguro por padrão (não perde dado que possa ser legalmente exigido depois).
