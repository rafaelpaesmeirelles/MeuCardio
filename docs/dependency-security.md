# Política de segurança de dependências do frontend

## Objetivo

O pipeline diferencia risco do código implantado de risco restrito às ferramentas
de desenvolvimento, mas não ignora advisories de forma genérica.

A etapa `frontend/scripts/audit-dependencies.mjs` executa dois relatórios:

1. grafo de produção (`npm audit --omit=dev --json`): vulnerabilidades altas ou
   críticas bloqueiam a CI;
2. grafo completo (`npm audit --json`): qualquer vulnerabilidade crítica,
   inclusive em tooling, bloqueia a CI.

## Exceção contextual do React Router

O projeto usa `react-router-dom` 7.18.1 para receber as correções dos advisories
de redirecionamento externo e hidratação SSR publicados para versões anteriores.

O audit também associa a essa versão o advisory
`GHSA-qwww-vcr4-c8h2`, classificado como alto. O próprio advisory limita o
impacto às APIs RSC instáveis. A Corvia é uma SPA Vite em React 18, usando modo
declarativo; não possui React Server Components, framework mode ou servidor
React Router.

A exceção é codificada, não textual. Ela só é aceita quando:

- o único advisory alto da cadeia é exatamente `GHSA-qwww-vcr4-c8h2`;
- o frontend permanece em React 18;
- não existem pacotes `react-server-dom-*` ou `@react-router/*`;
- não aparecem APIs RSC conhecidas no código-fonte.

A introdução futura de React 19/RSC, framework mode ou outro advisory alto faz
a CI falhar até uma nova revisão de segurança.

## Remoção de tooling vulnerável

`@capacitor/assets` foi removido porque não era referenciado por scripts ou
código do projeto e trazia uma cadeia antiga com `tar`, `sharp`, `minimatch` e
outros pacotes vulneráveis. O app móvel continua usando Capacitor Core, Android
e CLI nas versões atuais.

Geradores ocasionais de ícones ou splash screens não devem permanecer como
dependência permanente quando não participam do build reproduzível.

## Lockfile

`frontend/package-lock.json` deve ser gerado pelo npm e revisado no diff; não
deve ser editado manualmente. Atualizações de dependências exigem, no mínimo:

- `npm ci`;
- política de audit aprovada;
- política de armazenamento da sessão aprovada;
- `npm run build`;
- suíte backend completa, pois o deploy é empilhado e integrado.

## Revisão periódica

Advisories podem mudar de escopo ou severidade. Uma exceção só permanece válida
enquanto suas condições técnicas forem verificadas automaticamente e a
justificativa corresponder ao advisory oficial vigente.
