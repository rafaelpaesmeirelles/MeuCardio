# Revisão da interface — 09/09/2026

## Alterações

- Removido o texto decorativo “Mudar universo”, a seta e a orientação associada da escolha de experiência.
- Deslocamento exibe dia e hora do compromisso e da saída sugerida. Considera duração e margem de chegada; retorno usa o término do último compromisso. Não inventa saída quando a rota não existe e preserva o horário da agenda quando o provedor omite esse campo.
- Removidas as linhas decorativas que atravessavam os cartões de Meu dia entre espaços e Contexto conectado. Pontos ficam dentro dos cartões.
- Cinco ícones e ilustrações vetoriais próprios para Descobrir, Evidências, Aprender, Ensinar e Produzir. Não reutilizam imagens de consultório/hospital; respeitam o tema, sem downloads extras.
- Minha timeline consulta os temas e marcos existentes: seletor, contagem, período, marco mais recente e acesso direto ao tema. Lembra a escolha na sessão por usuário; contempla carregamento, falha, tentativa e vazio; descarta respostas atrasadas de outro tema.
- Página da timeline usa seleção compacta de tema e contraste adequado em ambos os temas.
- Chat e Emergência ficam em área reservada do dock, fora dos painéis de leitura. No mobile, o espaço ativo continua acessível pela navegação, liberando espaço no dock para os controles.
- Paleta global clara alinhada ao login aprovado: azul-gelo/ciano, texto azul-petróleo e painéis azuis suaves. Variáveis compartilhadas com o login; removidos banhos de rosa/lavanda de fundos. Ícones e estados semânticos mantêm suas cores.

## Verificação

- `node --test scripts/check-spaces-review.test.mjs`: 2 testes funcionais passaram (cálculo de saída/virada de dia/retorno e timeline assíncrona/memória por usuário/falha).
- TypeScript e build Vite concluídos. Builds adicionais ocorreram somente após correções visuais e a ampliação explícita da paleta global pelo usuário.
- Prévia do build em servidor de loopback com agenda e marcos fictícios; nenhum acesso ao backend clínico para a validação visual.
- Conferência em 1440 × 900, 390 × 844 e 360 × 740, temas claro e escuro. A área útil termina antes do dock; sem sobreposição dos atalhos ou linha no painel. Dia e hora permanecem dentro da largura móvel.
- Abertura e fechamento do Chat pelo dock conferidos. Os horários fictícios de 10/09 08:00 e saída 07:28 refletem 22 minutos de rota e 10 minutos de margem.
- Nenhuma suíte CI/backend executada.

Publicação agrupada com o conteúdo científico após sua revisão, conforme pedido do usuário.
