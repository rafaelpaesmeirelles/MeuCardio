# QA focal do leitor científico

Build TypeScript + Vite + PWA concluído. Quatro casos de 360×900 (JATS/PDF, claro/escuro), 14 verificações funcionais aprovadas, sem erros JavaScript, overflow horizontal global ou violações CSP após a correção.

A configuração anterior bloqueava o iframe de PDF `blob:` por `frame-src`. A correção adiciona somente `frame-src 'self' blob:` no Caddy e Nginx; `object-src 'none'` e `frame-ancestors 'none'` permanecem.

Texto JATS originalmente em português, autoria do resumo e rótulo “Texto integral em português” verificados. Abrir o texto nativo não solicita tradução. O PDF baixado corresponde byte a byte ao arquivo fictício.

**Limitação material:** a renderização do texto dentro do iframe PDF não foi confirmada visualmente: ambos os navegadores headless mostraram visor vazio/cinza, mesmo sem violação CSP. Não declarar o visor PDF integralmente validado. O fallback de download funciona.

APIs integralmente interceptadas, apenas perfil e publicações fictícios, sem backend real ou IA paga. Relatório: `report.json`. Capturas: JATS claro, opções PDF claro e visor PDF escuro (limitação documentada).
