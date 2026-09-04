# CorVIA — UI Visual Freeze — 04/09/2026

Status: **APROVADO PELO USUÁRIO / NÃO REDESENHAR**.

Esta é a regra absoluta para login e Cardiology Spaces. Correções futuras podem reparar bugs, responsividade e funcionamento, mas **não podem alterar composição, hierarquia, textos aprovados, proporções ou identidade visual sem nova autorização explícita**.

## Login
- Desktop e mobile, claro e escuro: mesma geometria aprovada.
- Galáxia central real, coração anatômico luminoso fixo no centro.
- Espaços orbitais mostram somente: Consultório, Hospital, Ensino, Pesquisa e Gestão.
- Caixa de login horizontal/compacta no desktop e compacta abaixo no mobile.
- Sem token/SSO.
- CTA: Novo no CorVIA / Solicite seu Acesso.
- Galáxia do login gira lentamente no sentido horário.

## Páginas internas
- Home clara e escura: preservar integralmente o layout aprovado.
- Cabeçalho mobile: marca à esquerda, mini-galáxia transparente, busca, foto do usuário sem nome ao lado.
- Mini-galáxia interna sem retângulo preto e com rotação lenta anti-horária.
- Página de escolha: mesma geometria nos temas claro e escuro; paleta muda, layout não.
- Saudação deve usar o tratamento/nome configurado do usuário.
- Não remover nem redesenhar as áreas funcionais da Home.

## Regra de release
Nenhum teste, correção de erro ou deploy pode "resolver" falha alterando este layout. Se houver erro técnico, corrigir a implementação mantendo esta referência visual congelada.