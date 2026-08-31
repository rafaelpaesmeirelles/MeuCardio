# Assistente Pessoal CorVIA pelo WhatsApp

Nasce desligado (`WHATSAPP_ASSISTANT_ENABLED=false`). O sandbox não realiza
tráfego externo. Produção usa exclusivamente a WhatsApp Business Cloud API.

## Meta

Configure em secret store `WHATSAPP_META_ACCESS_TOKEN`,
`WHATSAPP_META_APP_SECRET`, `WHATSAPP_META_VERIFY_TOKEN` e o phone number ID.
Tarifas zero são fail-closed. Mensagens externas N3 usam apenas templates
presentes em `WHATSAPP_APPROVED_TEMPLATE_NAMES`, opt-in purpose-bound registrado,
confirmação explícita e PIN. Conteúdo clínico/terapêutico é reclassificado N4 e
nunca enviado.

Texto livre só é usado dentro de 24 horas do último inbound. O aviso assíncrono
do Heart Team, fora da janela, exige `WHATSAPP_HEART_TEAM_READY_TEMPLATE_NAME`;
sem template, permanece bloqueado. O WhatsApp recebe apenas status e link
autenticado, nunca decisão terapêutica.

## Segurança e operação

- Oito permissões granulares; leitura nunca autoriza escrita.
- Pareamento de uso único, webhook assinado, replay/idempotência e rate limit.
- A conclusão manual do pareamento existe somente no sandbox, exige o
  assinante autenticado que gerou o código e limita tentativas por usuário,
  código e origem. No fluxo Meta, o webhook assinado também limita por telefone,
  código e volume global.
- Outbox cifrada é persistida antes do send. Entrega incerta nunca é reenviada.
- N2 oferece botão interativo `Desfazer` allowlisted e fallback textual.
- Áudio/mídia/PII param para revisão humana antes de qualquer ação.
- N3 originado no WhatsApp nunca recebe token no canal. O app autenticado
  reemite um nonce curto em `POST /commands/{id}/confirmation-token` e exige
  esse nonce mais o PIN no confirm; histórico expõe apenas `can_confirm`.
- `whatsapp-heart-team-worker` processa a fila durável e executa retenção sem
  depender de tráfego ou feature flags.
- Runner independente: `python -m app.commands.purge_expired_whatsapp_data`.
- Painel admin mostra consumo/custo por assinante e operação, limites e reservas.
- Resumos repetidos usam cache cifrada e isolada por assinante, com chave sobre
  SHA-256 da mídia sanitizada, modelo, prompt e versão do pipeline. A cache
  expira pela retenção configurada e é removida pela exclusão LGPD.

Nenhum segredo deve ser commitado. Ative as flags somente após homologação Meta,
DPIA/LGPD, testes de templates/opt-out e definição dos tetos de custo.

## Estimativa reproduzível de custo

O sistema não embute nem presume preços comerciais. Todos os valores abaixo são
parâmetros em **microunidades da moeda da conta** e precisam ser preenchidos pelo
operador conforme seus contratos vigentes:

- `C_meta = WHATSAPP_META_MESSAGE_COST_MICROUNITS`, por mensagem Meta faturável;
- `C_ia = WHATSAPP_SCIENTIFIC_SUMMARY_COST_MICROUNITS`, por resumo científico;
- `C_audio = WHATSAPP_TRANSCRIPTION_COST_MICROUNITS`, por transcrição;
- `C_heart`, custo contabilizado separadamente pelo ledger do Heart Team, quando
  essa função for utilizada.

Para `N` comandos, declare as médias por comando `m` (mensagens Meta faturáveis),
`i` (resumos de IA), `a` (transcrições) e `h` (custo médio real do Heart Team).
A estimativa é:

`C_total(N) = N × (m × C_meta + i × C_ia + a × C_audio + h)`

| Volume | Meta | IA/resumo | Transcrição | Heart Team | Total |
|---:|---:|---:|---:|---:|---:|
| 100 | `100mC_meta` | `100iC_ia` | `100aC_audio` | `100h` | `100(mC_meta+iC_ia+aC_audio+h)` |
| 1.000 | `1.000mC_meta` | `1.000iC_ia` | `1.000aC_audio` | `1.000h` | `1.000(mC_meta+iC_ia+aC_audio+h)` |
| 10.000 | `10.000mC_meta` | `10.000iC_ia` | `10.000aC_audio` | `10.000h` | `10.000(mC_meta+iC_ia+aC_audio+h)` |

O classificador atual é determinístico e local, portanto não gera cobrança de
modelo. Se qualquer tarifa aplicável estiver em zero ou ausente, o caminho
externo correspondente falha antes da chamada; zero significa **não homologado**,
e não custo gratuito. O painel separa custo efetivo, reserva pendente do outbox e
ledger do Heart Team para evitar dupla contagem.
