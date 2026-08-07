# Capturas de tela — dossiê visual da Corvia

Pedido pelo ChatGPT em 07/08/2026 (repassado pelo Rafael): 12 telas específicas, resolução de
desktop 1440×900, sem dado sensível real. Capturadas ao vivo, logado como administrador, contra a
produção (`corvia.med.br`, commit `9147c3c` no momento da captura) — nenhuma é mockup.

**Nome, e-mail e foto do médico que aparecem em todas as telas são reais** (Dr. Rafael Paes
Meirelles, dono da plataforma) — é a identidade do usuário logado, não um dado de paciente. Nenhum
dado de paciente real aparece em nenhuma captura; onde havia campo de nome de paciente, foi
preenchido com texto genérico marcado como "(dado fictício)".

| Arquivo | Pedido original | Status |
|---|---|---|
| `01-dashboard-home.png` | Dashboard/Home após login, menu lateral inteiro | ✅ completo |
| `02-biblioteca-documento-arvore-decisao.png` | Biblioteca científica, documento com árvore de decisão | ✅ completo |
| `03a-calculadoras-catalogo.png` | Calculadoras — catálogo | ✅ completo |
| `03b-calculadora-com-resultado.png` | Calculadora aberta com resultado/laudo | ✅ completo — CHA₂DS₂-VASc calculado (4/9), com referência |
| `04-avaliacao-preoperatoria-completa.png` | RCRI/Gupta/DASI/AUB-HAS2/VSG-CRI/GSCRI visíveis | 🟡 parcial — RCRI, Gupta MICA, DASI e VSG-CRI calculados de verdade, com "Resultado integrado". AUB-HAS2 não ficou habilitado nesta captura (automação não conseguiu marcar o toggle dele a tempo). GSCRI e ACS-NSQIP aparecem **documentados em texto**, não calculados — a própria tela explica por quê (GSCRI: cálculo local bloqueado até revisão dos coeficientes contra a publicação original; ACS-NSQIP: usar a calculadora oficial externa, nunca embutir) |
| `05a-modo-emergencia-filtros.png` | Modo Emergência com filtros | ✅ completo |
| `05b-modo-emergencia-protocolo-aberto.png` | Protocolo/fluxograma aberto | ✅ completo — protocolo de Afogamento, árvore de decisão real |
| `06-medicamentos-lista.png` | Medicamentos com monografia + apresentações/interações | 🟡 parcial — só a lista/catálogo; não consegui abrir uma monografia individual pela automação a tempo |
| `07-agenda-integrada.png` | Agenda Integrada | ✅ completo |
| `08-receituario.png` | Documentos/Receituário — geração + assinatura digital | 🟡 parcial — formulário de prescrição parcialmente preenchido (nome do paciente e um medicamento); não avançou até a etapa de assinatura digital |
| `09-corvia-mail.png` | CorvIA Mail | ✅ completo — tela de acesso (a caixa deste usuário específico não está ativada) |
| `10-minha-conta.png` | Minha Conta / integrações | ✅ completo |
| `11-modo-apresentacao.png` | Modo Apresentação/PPTX | 🟡 parcial — mostra o catálogo de documentos exportáveis; não avançou até o seletor PDF/PowerPoint (existe e foi implementado em 07/08/2026, só não apareceu nesta captura específica) |
| `12-mobile-responsivo.png` | Tela mobile responsiva | ✅ completo — viewport 390×844 |

## O que fazer com os itens parciais

Se for importante fechar os 3 itens parciais (04 com AUB-HAS2, 06 com monografia aberta, 08 até a
assinatura, 11 até o seletor de formato), é só pedir — a automação já está escrita e funcionando
para o resto do fluxo, faltou só ajuste fino de seletor nesses pontos específicos.
