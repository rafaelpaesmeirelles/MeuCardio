# CorVIA — produção encerrada e passagem para deploy

Pedido do usuário: interromper a produção, salvar tudo e preparar para outro chat fazer deploy. Não iniciar novo lote.

PR: https://github.com/rafaelpaesmeirelles/MeuCardio/pull/915
Branch: `codex/corvia-prevalentes-progressao-20260909`.

## O que está salvo

A primeira rodada está aplicada no commit `4796d8d54e7557e2400737a4d46361ace8543b8b`. A segunda rodada está integralmente salva em `handoff/corvia-prevalentes-rodada2.patch.xz`. **Este commit salva o pacote; o patch ainda precisa ser aplicado e commitado antes do deploy.** Nenhum merge ou deploy foi realizado.

Pacote: 81.444 bytes. SHA256: `ddd7a8915dc4c0a27155cff439ba3d357dfbc3c61c9f5688c559d5b8261b26bf`.
Git blob: `b0b0dae2346a2d83ff1c3fbe2630d0bae40b7c9c`.
Patch descompactado: 389.140 bytes. Aplicação reversa conferida contra todos os arquivos finais.

## Aplicação

Em checkout limpo desta branch, que já contém a primeira rodada:

```bash
sha256sum handoff/corvia-prevalentes-rodada2.patch.xz
xz -dc handoff/corvia-prevalentes-rodada2.patch.xz > /tmp/corvia-prevalentes-rodada2.patch
git apply --check /tmp/corvia-prevalentes-rodada2.patch
git apply --index /tmp/corvia-prevalentes-rodada2.patch
git diff --cached --stat
git commit -m "content: apply reviewed prevalent cardiology round 2"
```

Não usar `--reject` nem sobrescrever catálogos se houver divergência. Integrar o commit resultante à main atual preservando outras frentes. Comparação anterior com main `1c8454d132bfc6ecedec802c731dbb26b4d1e6da` não mostrou colisões nos arquivos do lote; revalidar conflitos efetivos no momento da integração.

Depois de aplicar, ler `docs/HANDOFF-producao-prevalentes-20260909.md`, incluído no patch, para a passagem detalhada. Relatório, mapa e resultados ficam em `docs/producao-prevalentes-20260909-rodada2*`. Auditorias e pareceres também estão no patch.

## Entrega total das duas rodadas

- 18 documentos novos e nove documentos existentes corrigidos.
- 12 casos fictícios, seis materiais ao paciente e seis checklists novos.
- Cinco registros estruturados existentes corrigidos.
- Oito trilhas com 67 etapas; 105 relações explícitas novas.
- Segunda rodada: 24 recursos sem órfãos, 14 documentos com vínculos recíprocos, 431 links internos conferidos no conjunto.

Revisão científica e cruzada assistidas por IA, sem revisão humana declarada. JSON, frontmatter, referências, alternativas/índices, IDs, grafo e detector nativo de posologia validados sem erros. Os pareceres registram fontes primárias, limitações e correções aplicadas. Não foi certificada completude integral de todas as patologias.

## Pendência da release

O CI da primeira rodada mostrou 117 testes de scripts aprovados e uma falha preexistente de autorização do corpus: `editorial-approvals/full-corpus-release-20260907.json` autoriza 11.581 itens, abaixo do corpus já alterado. Manifesto e teste preservados. Conferir a autorização aplicável ao snapshot final; não desabilitar gate nem fabricar aprovação geral.

Nenhum `published: true` foi acrescentado. Carga e merge não publicam automaticamente registros novos: executar o fluxo editorial autorizado, importação, promoção, reconciliação do grafo e índices conforme o procedimento atual do CorVIA. Banco, interface autenticada e deploy não foram executados nesta frente. Coordenar com a release em andamento e confirmar versão/prontidão e amostras de navegação depois da publicação.
