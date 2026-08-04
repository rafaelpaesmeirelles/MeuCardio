# Validação final — PR #42

Data: 04/08/2026

Este documento marca o SHA submetido à certificação integral antes da integração.

## Escopo certificado

- CRBM e catálogo profissional ampliado;
- forma de tratamento escolhida pelo profissional;
- local de trabalho opcional nos documentos;
- contraste automático de logo claro/transparente;
- identidade e logo em receitas, atestados, laudos, documentos públicos e materiais ao paciente;
- histórico pesquisável e filtrável por paciente e tipo;
- Receita de Controle Especial física Anvisa V2 em duas vias, frente e verso;
- identificação do emitente, endereço profissional completo, nome/endereço/documento do paciente e data recomendada de impressão na RCE;
- quantidade de cada item em algarismos e por extenso, conforme Portaria SVS/MS nº 344/1998;
- Lista C5 com validações da Lei nº 9.965/2000;
- demais modelos numerados em fail-closed, sem simulação de SNCR;
- primeiro acesso direcionado à conclusão do perfil;
- comando seguro e idempotente para provisionamento de equipe sem senha no repositório.

## Gates obrigatórios

- migrations em banco vazio;
- migration idempotente;
- compilação Python;
- suíte pytest completa;
- build e auditorias do frontend;
- smoke HTTP;
- backup e restauração PostgreSQL;
- reconciliação canônica do corpus científico.
