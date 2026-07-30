"""Termo de consentimento para transferência internacional de dados —
CorvIA Mail (Tarefa 28). Decisão do Rafael em 30/07/2026, ver CLAUDE.md
(item 14b): o Zoho Mail360 não tem data center no Brasil, então provisionar
a caixa de e-mail é transferência internacional de dado pessoal. Em vez de
depender de a Zoho confirmar a adoção da cláusula-padrão da ANPD (Resolução
CD/ANPD nº 19/2024), a base legal escolhida foi o art. 33, VIII da LGPD:
consentimento específico e destacado do titular, distinto de qualquer outro
consentimento da plataforma, com informação prévia do caráter internacional
da operação. Por isso o texto abaixo NÃO pode ser apresentado junto com o
aceite geral de termos de uso da Corvia — precisa do próprio checkbox,
separado, na ativação da caixa (ver `POST /api/email/conta`).

`VERSAO` muda sempre que o texto mudar de forma que afete o que o titular
está consentindo (ex.: novo destino de dado, nova finalidade). Mudança de
versão não re-obtém consentimento sozinha — quem já aceitou uma versão
anterior fica com `lgpd_aceite_versao` desatualizado, sinalizando que
precisa reconsentir; a aplicação disso ainda não está automatizada (ver
BRIEFING_CLAUDE_CODE_4.md).

Este texto é uma minuta redigida pela sessão de desenvolvimento, não uma
peça jurídica revisada por advogado — está pendente de revisão jurídica
igual ao TCLE (CLAUDE.md, item 14). Publicar sem essa revisão é decisão do
Rafael, registrada no mesmo item 14b."""

VERSAO = "2026-07-30"


def texto(email_contato: str) -> str:
    return f"""TERMO DE CONSENTIMENTO PARA TRANSFERÊNCIA INTERNACIONAL DE DADOS
CorvIA Mail — versão {VERSAO}

Este termo é específico para a ativação do CorvIA Mail (caixa de e-mail
própria no domínio @corvia.med.br) e vale além de qualquer outro termo de
uso ou política de privacidade da Corvia — ative esta caixa só se concordar
com o que está escrito aqui.

1. O QUE É O SERVIÇO
O CorvIA Mail é um add-on opcional e cobrado à parte da assinatura
principal da Corvia. Ele é operado tecnicamente pela Zoho Corporation, por
meio da API Mail360, empresa e infraestrutura de terceiro, não controlada
pela Corvia.

2. POR QUE HÁ TRANSFERÊNCIA INTERNACIONAL
A Zoho não mantém data center no Brasil. Os dados processados pelo CorvIA
Mail — nome e e-mail de cadastro necessários para provisionar a caixa, e o
conteúdo das mensagens que você enviar ou receber por ela — são
armazenados e processados em servidores fora do território brasileiro
(Estados Unidos, União Europeia ou outra localidade operada pela Zoho, a
depender de qual data center atende a conta). Isso configura transferência
internacional de dado pessoal, nos termos do art. 33 da Lei nº 13.709/2018
(Lei Geral de Proteção de Dados — LGPD).

3. BASE LEGAL DESTE CONSENTIMENTO
Ao marcar a caixa de aceite abaixo, você fornece consentimento específico
e destacado para esta transferência internacional, distinto de qualquer
outro consentimento já dado para uso da plataforma Corvia, conforme
autoriza o art. 33, inciso VIII, da LGPD. Este consentimento cobre
exclusivamente o uso do CorvIA Mail — não amplia, nem substitui, nenhum
outro consentimento ou base legal já aplicável ao restante da plataforma.

4. RESTRIÇÃO DE USO QUE VOCÊ TAMBÉM ASSUME
O CorvIA Mail é para uso administrativo e profissional geral (agenda,
contato administrativo, avisos do sistema) — NÃO tem a mesma cifragem de
dado de saúde do Cofre do telediagnóstico. Ao aceitar este termo, você
também se compromete a não enviar, por esta caixa, nome, CPF ou qualquer
dado que identifique um paciente em conjunto com informação clínica.

5. SEUS DIREITOS
Você pode, a qualquer momento: solicitar acesso aos dados tratados pelo
CorvIA Mail; pedir correção de dado incorreto; revogar este consentimento
(o que encerra o uso do CorvIA Mail, sem afetar sua assinatura principal
da Corvia); e solicitar a exclusão da sua caixa de e-mail e do conteúdo
nela armazenado. Pedidos podem ser feitos pelo e-mail {email_contato}.

6. CONTROLADOR
O controlador dos dados tratados na plataforma Corvia, para os fins deste
termo, é o responsável pelo sistema, contatável em {email_contato}.

Ao marcar "Li e concordo com este termo", você declara ter lido e
compreendido as informações acima e consente, de forma livre, informada e
inequívoca, com a transferência internacional de dado pessoal necessária
para o funcionamento do CorvIA Mail."""
