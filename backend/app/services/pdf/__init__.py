"""Geração de PDF no servidor, sem dependência externa.

- `nucleo`  — escreve o formato PDF (só stdlib)
- `layout`  — diagramação: `Documento` (retrato) e `Apresentacao` (paisagem)
- `marca`   — paleta e logo
- `arvore`  — redesenha a árvore de decisão do fluxograma, que o mermaid não
              consegue renderizar fora do browser
"""

from .layout import Apresentacao, Documento, quebrar          # noqa: F401
from .nucleo import largura_texto                             # noqa: F401
