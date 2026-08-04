# Progresso — substituição do Passlib

Atualização: 03/08/2026 22:34 BRT

## Implementado

- `passlib[bcrypt]==1.7.4` removido das dependências.
- `bcrypt==4.0.1` mantido como implementação direta.
- `hash_password()` e `verify_password()` preservados como contratos internos.
- Novos hashes mantêm custo 12.
- Verificação inválida retorna `False`, sem erro interno.
- Nenhuma senha ou linha do banco foi alterada.

## Compatibilidade protegida

- vetor bcrypt legado validado;
- identificadores `$2a$`, `$2b$` e `$2y$` cobertos;
- senhas corretas e incorretas cobertas;
- novos hashes cobertos;
- entradas malformadas cobertas;
- comportamento histórico de 72 bytes do bcrypt 4.x documentado;
- gate impede retorno do Passlib às dependências e ao módulo de segurança.

## Pendente nesta frente

- CI integral do PR;
- auditoria Python;
- migrations e idempotência;
- suíte backend completa;
- smoke HTTP;
- backup e restauração PostgreSQL;
- build e gates do frontend;
- revisão automática;
- merge após certificação verde.
