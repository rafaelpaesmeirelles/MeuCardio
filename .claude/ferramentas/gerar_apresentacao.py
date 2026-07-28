"""Gera as duas apresentações institucionais da Corvia.

Um só corpo de conteúdo, dois documentos:

- `Corvia-Apresentacao.pdf` — para colegas, amigos e família. Sem uma linha
  sobre patrocínio ou receita publicitária.
- `Corvia-Apresentacao-Patrocinio.pdf` — o mesmo conteúdo mais o capítulo
  comercial, para conversa com patrocinador.

Compartilham o corpo de propósito: quem receber os dois não pode encontrar
descrição diferente do mesmo produto. O que muda é o que se acrescenta, nunca
o que se afirma.

Uso:  python3 gerar_apresentacao.py [pasta-de-saida]
"""

from __future__ import annotations

import sys

from documento import (
    Documento, MARGEM, LARGURA_UTIL, NAVY, TEAL, VERMELHO, TINTA, NEUTRO,
    TINTA_TEAL, TINTA_VERMELHA, BRANCO, quebrar,
)

DATA = "Julho de 2026"
AUTOR = "Dr. Rafael Paes Meirelles"
REGISTRO = "Cardiologista  ·  CRM-SP 138266  ·  RQE 134798"
LOGO = "/opt/meucardio/branding/Corvia_Logo1_CorvIA_transparente.png"


# ===========================================================================
# Corpo comum
# ===========================================================================

def capitulo_nome(d: Documento) -> None:
    d.capitulo("De onde vem o nome", "01")

    d.paragrafo(
        "Corvia vem do latim. É a junção de cor, coração, com via, caminho. "
        "Lida inteira, a palavra diz o caminho do coração — que é a assinatura "
        "da marca e também a descrição mais curta do que o sistema faz."
    )

    d.destaque(
        "Corvia — do latim cor (coração) + via (caminho). O caminho do coração.",
        rotulo="O nome",
    )

    d.titulo("Por que este nome, e não outro")
    d.paragrafo(
        "A palavra tem dois sentidos que funcionam ao mesmo tempo, e é a "
        "sobreposição deles que sustenta o nome."
    )
    d.itens([
        "O caminho anatômico — a Cardiologia é feita de vias. A via de "
        "condução do estímulo elétrico, a via de saída do ventrículo, a via de "
        "acesso do cateter, a circulação como caminho fechado. Quem trabalha "
        "com coração trabalha, o dia inteiro, com trajetos.",
        "O caminho do raciocínio — nenhuma conduta cardiológica nasce pronta. "
        "Ela é o fim de um percurso: a queixa leva ao exame, o exame ao escore, "
        "o escore à estratificação, a estratificação à conduta. É esse percurso "
        "que o sistema torna visível.",
    ])

    d.paragrafo(
        "Há ainda um detalhe que a marca gráfica assume: as três últimas letras "
        "de Corvia formam IA. O assistente de inteligência artificial não é um "
        "acessório colado depois — está no nome, e responde sempre ancorado no "
        "acervo verificado da própria plataforma, nunca de memória livre."
    )

    d.titulo("Como o nome bate com a função")
    d.paragrafo(
        "Um sistema de apoio à decisão pode ser construído de duas maneiras. "
        "Pode entregar a resposta pronta — a dose, o corte, o nome do exame — e "
        "pedir confiança. Ou pode entregar o percurso inteiro, mostrando de onde "
        "cada passo veio, e deixar a decisão com quem assina o prontuário."
    )
    d.paragrafo(
        "A Corvia foi construída da segunda maneira, e o nome registra essa "
        "escolha. Por isso o fluxograma é uma árvore de decisão em que cada "
        "ramificação é uma pergunta clínica respondível à beira do leito. Por "
        "isso cada afirmação carrega a diretriz e o ano que a sustentam. Por "
        "isso o que não está verificado aparece marcado como não verificado, em "
        "vez de sumir. O caminho é o produto."
    )

    d.destaque(
        "A responsabilidade clínica é sempre de quem prescreve. A Corvia "
        "encurta o caminho até a informação correta e mostra a origem dela — "
        "não substitui julgamento clínico, e não foi desenhada para isso.",
        cor_fundo=TINTA_VERMELHA, cor_barra=VERMELHO, rotulo="Limite declarado",
    )


def capitulo_problema(d: Documento) -> None:
    d.capitulo("O problema que a Corvia resolve", "02")

    d.paragrafo(
        "O cardiologista brasileiro decide com pressão de tempo e com a "
        "informação espalhada. A diretriz que responde à dúvida tem trezentas "
        "páginas e está num PDF. O escore está num site em inglês. A dose está "
        "numa bula. A imagem de referência está num livro na estante do serviço. "
        "O ambulatório tem trinta pacientes e a emergência não espera."
    )

    d.titulo("O que existe hoje, e por que não resolve")
    d.itens([
        "Resumo rápido sem fonte — responde em segundos e não permite conferir "
        "nada. Serve para lembrar, não para decidir, e quem o usa para decidir "
        "não tem como saber se o dado envelheceu.",
        "Diretriz na íntegra — é a fonte correta e é impraticável no meio do "
        "atendimento. Ninguém lê cento e vinte páginas entre dois pacientes.",
        "Ferramenta internacional — boa, e escrita para outro sistema de saúde. "
        "Nem sempre considera a realidade de acesso, de disponibilidade de "
        "medicamento e de exame do Brasil.",
    ])

    d.destaque(
        "A lacuna é específica: profundidade de diretriz na velocidade de "
        "consulta, escrita em português, para o cardiologista brasileiro. É "
        "exatamente esse espaço que a Corvia ocupa.",
        rotulo="A lacuna",
    )

    d.titulo("Para quem é")
    d.paragrafo(
        "Cardiologista, residente de Cardiologia e clínico que atende paciente "
        "cardiológico — enfermaria, emergência, ambulatório e consultório. O "
        "acesso é restrito a profissional habilitado, com registro de conselho "
        "verificado no cadastro. Não é um site de conteúdo de saúde para "
        "paciente, e não pretende ser."
    )


def capitulo_rigor(d: Documento) -> None:
    d.capitulo("Como o conteúdo é feito", "03")

    d.paragrafo(
        "Esta é a parte do projeto que consome mais tempo e é a única que "
        "justifica a existência dele. Um sistema de apoio à decisão sem "
        "procedência é pior que nenhum, porque transmite confiança sem entregar "
        "fundamento."
    )

    d.titulo("A régua")
    d.paragrafo(
        "Toda afirmação clínica precisa vir de diretriz vigente — ESC, AHA/ACC "
        "ou SBC — ou de estudo original identificável. Referência completa e "
        "conferível, com DOI ou PMID quando existir. A régua é a de uma fonte "
        "que um cardiologista citaria em discussão de caso."
    )

    d.titulo("Classificação de origem, documento por documento")
    d.paragrafo(
        "Cada documento carrega o nível da fonte que o sustenta, derivado "
        "automaticamente das referências que ele cita:"
    )
    d.tabela(
        ["Nível", "O que significa", "Acervo"],
        [
            ["A", "Diretriz de sociedade ou estudo original, com "
                 "identificador persistente (DOI ou PMID)", "169 documentos"],
            ["B", "Fonte técnica idônea, sem identificador persistente — "
                 "consenso, posicionamento, material de sociedade", "79 documentos"],
            ["C", "Fonte fraca. Nenhum documento permanece neste nível: "
                 "é condição de saída, não de permanência", "0 documentos"],
        ],
        [0.11, 0.62, 0.27],
    )
    d.paragrafo(
        "O acervo começou com cinquenta e duas ocorrências de fonte fraca — "
        "material de estudante, site de respostas geradas por inteligência "
        "artificial, calculadora de terceiro, material comercial de operadora. "
        "Todas foram substituídas por fonte primária ou removidas. Hoje são zero.",
        cor=TINTA,
    )

    d.titulo("Lacuna marcada, nunca escondida")
    d.paragrafo(
        "Quando um dado não pôde ser confirmado numa fonte real, o campo não "
        "fica vazio nem recebe suposição: recebe a marca literal VERIFICAÇÃO "
        "HUMANA NECESSÁRIA, visível para quem lê."
    )
    d.destaque(
        "A regra tem um motivo prático: um dado ausente sem marcação é "
        "indistinguível de um dado que ninguém procurou — e some da fila de "
        "revisão para sempre. Marcado, ele permanece na fila até alguém "
        "resolver.",
        rotulo="Por que marcar em vez de omitir",
    )

    d.titulo("Vigilância de diretriz desatualizada")
    d.paragrafo(
        "Oitenta e seis diretrizes estão mapeadas no sistema, ligadas aos "
        "documentos que dependem delas. Quando uma diretriz é substituída por "
        "versão nova, todos os documentos que a citam entram em alerta de "
        "revisão automaticamente. É o mecanismo que impede o acervo de "
        "envelhecer em silêncio, que é a forma mais comum de material clínico "
        "ficar errado sem que ninguém perceba."
    )

    d.titulo("O que a auditoria encontrou")
    d.paragrafo(
        "Cerca de cinquenta e dois documentos passaram por auditoria linha a "
        "linha contra a fonte declarada. Foram encontrados aproximadamente vinte "
        "e quatro erros clinicamente relevantes, cinco deles com potencial de "
        "dano direto ao paciente. Todos corrigidos. O tipo de erro importa mais "
        "que o número:"
    )
    d.itens([
        "Número trocado — dado principal de ensaio clínico divergente do "
        "artigo original.",
        "Fonte apontando para o artigo errado do mesmo ensaio — o "
        "identificador resolvia normalmente e abria outra publicação. Lição "
        "que virou regra: DOI que resolve não prova nada sobre o conteúdo.",
        "Atribuição à diretriz errada — recomendação creditada a uma sociedade "
        "que não a emitiu.",
        "Imagem descrita como o que não é — traçado de parede inferior "
        "rotulado como anterior.",
        "Contradição entre telas — o mesmo índice com valor de corte diferente "
        "no verbete e no fluxograma. Este é o mais insidioso: só aparece quando "
        "alguém compara duas páginas, que é exatamente o que um assinante faz.",
    ])

    d.titulo("Imagem com licença conferida")
    d.paragrafo(
        "Toda imagem da galeria vem de acervo de acesso aberto com licença "
        "verificável, com atribuição completa registrada. Nenhuma é gerada por "
        "inteligência artificial. As trinta e seis licenças foram conferidas uma "
        "a uma, e nenhuma tem cláusula que proíba uso comercial ou obra "
        "derivada — condição necessária para uma plataforma por assinatura."
    )


def capitulo_funcoes(d: Documento) -> None:
    d.capitulo("O que o sistema faz", "04")
    d.paragrafo(
        "Vinte e uma funções, organizadas por momento de uso — não por menu. A "
        "pergunta que separa os grupos é simples: o que o médico está fazendo "
        "quando abre a plataforma?"
    )

    d.titulo("Decidir agora, com o paciente na frente")
    d.itens([
        "Fluxogramas clínicos — dezesseis árvores de decisão em cardiologia "
        "aguda e crônica. Cada nó é uma pergunta respondível à beira do leito e "
        "cada folha é uma conduta. O formato é estrito: caminho que volta ou "
        "que converge é proibido, porque no meio de um atendimento um diagrama "
        "com laço não é consultável.",
        "Calculadoras e escores — escores validados com o cálculo feito na "
        "tela, corte de decisão explícito e a fonte do corte visível junto do "
        "resultado.",
        "Assistente clínico — resposta em linguagem natural, ancorada no acervo "
        "verificado da própria plataforma e com os documentos de origem "
        "citados. Não responde de memória livre.",
        "Busca — pesquisa única sobre todo o acervo, tolerante a acento e a "
        "erro de digitação.",
    ])

    d.titulo("Consultar o acervo")
    d.itens([
        "Biblioteca científica — duzentos e quarenta e nove documentos em "
        "vinte e sete temas, cobrindo a Cardiologia de ponta a ponta.",
        "Medicamentos — comparador com dose, apresentação, ajuste renal, "
        "contraindicação e interação, em campo estruturado que permite comparar "
        "dois fármacos lado a lado.",
        "Galeria de imagens — trinta e seis achados de eletrocardiograma, "
        "ecocardiograma, tomografia, ressonância, radiografia e cateterismo, "
        "com laudo descritivo e licença registrada.",
        "Exames — dezessete exames e marcadores: o que mede, valor de "
        "referência, indicação, interpretação e limitação.",
        "Evidências — recomendações pontuais com classe, nível, sociedade e "
        "ano. Uma afirmação específica por registro, não o documento inteiro.",
        "Estudos — quinze ensaios clínicos e metanálises resumidos em texto "
        "próprio, com os números reais do desfecho e a implicação clínica.",
        "Favoritos — o recorte pessoal de cada assinante sobre todo o acervo.",
    ])

    d.titulo("Trabalhar")
    d.itens([
        "Round hospitalar — a lista de pacientes internados com pendência e "
        "evolução, para a passagem de visita.",
        "Agenda — compromissos e retornos.",
        "Modelos de documento — receituário, atestado e relatório, com "
        "cabeçalho que traz o nome e o registro do prescritor com peso visual "
        "maior que a marca. O documento é do médico, não da plataforma.",
        "Checklist de alta — três roteiros com trinta itens de verificação, "
        "para que nada essencial fique para trás na alta hospitalar.",
        "Meus indicadores — o que o próprio médico produziu no período.",
    ])

    d.titulo("Estudar")
    d.itens([
        "Trilhas de estudo — três trilhas com vinte e sete passos, em "
        "sequência pedagógica, com registro de progresso.",
        "Cursos parceiros — cursos de preparação para o Título de "
        "Especialista, oferecidos por parceiros e assinados dentro da "
        "plataforma. O vídeo fica no ambiente do parceiro; o material de apoio "
        "é servido aqui, por rota autenticada.",
    ])

    d.titulo("Serviço à distância")
    d.paragrafo(
        "Laudo e consultoria de eletrocardiograma, MAPA, Holter e teste "
        "ergométrico, em regime eletivo ou urgente. Preço calculado no servidor "
        "a partir do serviço e da urgência — nunca recebido do navegador. O "
        "prazo conta a partir da confirmação do pagamento."
    )
    d.destaque(
        "O exame do paciente é cifrado em repouso com AES-256-GCM e guardado em "
        "volume sem endereço acessível de fora. O identificador do pedido entra "
        "como dado autenticado da cifra, de modo que um arquivo movido para "
        "outro pedido simplesmente não decifra. Toda leitura é registrada em "
        "log de auditoria.",
        rotulo="Dado de paciente",
    )

    d.titulo("Conta e assinatura")
    d.paragrafo(
        "Perfil profissional com registro de conselho e RQE, foto validada por "
        "assinatura de arquivo, troca de senha, histórico de faturas lido "
        "direto do provedor de pagamento e portal de autoatendimento para "
        "trocar cartão ou cancelar. Cancelamento sem ligação, sem retenção "
        "forçada e sem formulário."
    )


def capitulo_numeros(d: Documento) -> None:
    d.capitulo("O acervo hoje", "05")

    d.paragrafo(
        "Números conferidos no banco de produção na data deste documento. "
        "Amplitude e profundidade são meta declarada do projeto: lacuna de "
        "cobertura é dívida do produto, não detalhe."
    )

    d.numero_grande([("249", "documentos científicos"), ("27", "temas"),
                     ("86", "diretrizes mapeadas"), ("16", "fluxogramas")])

    d.tabela(
        ["Frente", "Publicado", "Situação"],
        [
            ["Documentos científicos", "227 de 249", "22 em revisão final"],
            ["Fluxogramas em árvore de decisão", "16", "no ar"],
            ["Galeria de imagens", "36", "licenças conferidas uma a uma"],
            ["Exames e marcadores", "17", "no ar"],
            ["Evidências com classe e nível", "19 de 20", "1 aguardando conferência"],
            ["Estudos e metanálises", "15", "identificadores conferidos"],
            ["Calculadoras e escores", "6", "no ar"],
            ["Checklists de alta", "3 (30 itens)", "no ar"],
            ["Trilhas de estudo", "3 (27 passos)", "carregadas, a publicar"],
            ["Medicamentos", "100 cadastrados", "em verificação contra bula"],
        ],
        [0.44, 0.20, 0.36],
    )

    d.destaque(
        "Medicamentos é a frente mais nova e a única ainda não publicada. "
        "Vinte e quatro registros carregam marca explícita de verificação "
        "pendente. Publicar antes de resolvê-las contrariaria a régua do "
        "projeto — então não foram publicados.",
        cor_fundo=TINTA_VERMELHA, cor_barra=VERMELHO, rotulo="O que ainda não está pronto",
    )

    d.titulo("O que vem a seguir")
    d.itens([
        "Fechar a verificação dos medicamentos contra bula aprovada e publicar "
        "a frente.",
        "Ampliar os fluxogramas — faltam, entre outros, regurgitação mitral, "
        "miocardite, amiloidose cardíaca, bradiarritmia e marcapasso, "
        "taquicardia de QRS largo, síndrome coronariana crônica, pericardite, "
        "cardiopatia congênita do adulto, cardio-oncologia, avaliação "
        "perioperatória e dislipidemia.",
        "Assinatura digital de documento com certificado ICP-Brasil, para que "
        "receita e laudo tenham validade legal fora da plataforma. Enquanto a "
        "credencial não sai, o sistema avisa explicitamente que o documento não "
        "está assinado — a etapa nunca é simulada.",
        "Estender a busca às frentes novas, que hoje só cobre os documentos.",
    ])


def capitulo_assinatura(d: Documento) -> None:
    d.capitulo("Assinatura", "06")

    d.paragrafo(
        "Assinatura mensal individual, com acesso a todo o conteúdo — sem "
        "camada paga por cima, sem função reservada a plano superior e sem "
        "cobrança por consulta ao assistente."
    )

    d.numero_grande([("R$ 20", "por mês"), ("1", "plano único"),
                     ("0", "taxa de adesão"), ("0", "fidelidade")])

    d.itens([
        "Um plano só — a decisão foi deliberada. Com um plano, não existe "
        "função escondida atrás de upgrade nem tela de comparação de pacote.",
        "Cancelamento pelo próprio portal, a qualquer momento, sem ligação e "
        "sem retenção forçada.",
        "Serviço de laudo e consultoria à distância cobrado à parte, por "
        "pedido — não está incluído na assinatura e não a substitui.",
        "Curso parceiro assinado à parte, com preço próprio. Uma assinatura "
        "não substitui a outra, e isso é dito na tela antes da compra.",
    ])

    d.titulo("Independência")
    d.paragrafo(
        "A Corvia é produto independente, sem vínculo institucional com "
        "hospital ou serviço. A responsabilidade clínica pelo conteúdo é do "
        "cardiologista responsável pelo projeto, nominalmente, e não de um "
        "comitê anônimo."
    )


def capitulo_quem(d: Documento) -> None:
    d.capitulo("Quem faz", "07")

    d.paragrafo(
        "A Corvia é idealizada, escrita e mantida por Rafael Paes Meirelles, "
        "cardiologista, CRM-SP 138266, RQE 134798."
    )
    d.paragrafo(
        "O conteúdo clínico não é terceirizado nem gerado sem conferência: "
        "cada documento passa por leitura contra a fonte declarada antes de ir "
        "ao ar, e o que não passou fica marcado como pendente em vez de ser "
        "publicado assim mesmo. É por isso que uma parte do acervo aparece "
        "neste documento como não publicada — o número honesto é mais útil que "
        "o número redondo."
    )

    d.destaque(
        "corvia.med.br",
        rotulo="Onde encontrar",
    )


# ===========================================================================
# Capítulo exclusivo da versão comercial
# ===========================================================================

def capitulo_patrocinio(d: Documento) -> None:
    d.capitulo("Patrocínio", "08")

    d.paragrafo(
        "A assinatura é a receita principal e continuará sendo. O patrocínio "
        "existe para acelerar a produção de conteúdo — que é o que consome mais "
        "tempo e o que mais diferencia a plataforma —, não para substituir a "
        "assinatura nem para financiar o produto às custas de quem paga por ele."
    )

    d.titulo("Por que a Corvia é um canal legalmente habilitado")
    d.paragrafo(
        "A RDC 96/2008 da ANVISA restringe a propaganda de medicamento sob "
        "prescrição a meios de comunicação dirigidos direta e unicamente a "
        "profissionais habilitados a prescrever ou dispensar. A Corvia é "
        "exatamente isso: acesso autenticado, cadastro com registro de conselho "
        "verificado, conteúdo exclusivamente técnico e nenhuma área aberta ao "
        "público leigo."
    )
    d.destaque(
        "Isso torna a Corvia um dos poucos ambientes em que a divulgação "
        "técnica de medicamento sob prescrição é permitida — e a audiência é "
        "100% prescritora e verificada, sem desperdício de alcance.",
        rotulo="O ativo comercial",
    )

    d.titulo("O que a norma exige, e que a plataforma vai exigir também")
    d.paragrafo(
        "Os pontos abaixo são requisito de produto, não cláusula de contrato: "
        "estão especificados para virar validação obrigatória na rota de "
        "cadastro do patrocinador — peça sem eles não é publicada. O módulo de "
        "patrocínio ainda não foi construído, e nenhum espaço comercial está no "
        "ar hoje; a especificação existe antes do código de propósito, para "
        "que nenhuma peça seja publicada sob regra improvisada."
    )
    d.itens([
        "Contraindicação e interação obrigatórias — quando a peça destaca "
        "benefício do medicamento, precisa exibir ao menos uma contraindicação "
        "e uma interação medicamentosa frequente, com o mesmo peso visual do "
        "benefício. A norma fala em impacto visual, e o componente respeita "
        "isso: não é rodapé em letra miúda.",
        "Conteúdo limitado à bula aprovada — nada de indicação fora do "
        "registro na ANVISA. Número de registro e princípio ativo são campos "
        "obrigatórios.",
        "Vedações do art. 8º — nada de anunciar o medicamento como novo, nada "
        "de estimular uso indiscriminado e nada de imagem de pessoa utilizando "
        "o produto.",
        "Respaldo profissional identificado — se a peça cita profissional de "
        "saúde como referência, nome e número de inscrição no conselho são "
        "obrigatórios.",
        "Rótulo mais forte — peça de medicamento é rotulada como Publicidade, "
        "não como Patrocinado, e o registro de quem aprovou a peça e quando "
        "fica gravado.",
    ])
    d.paragrafo(
        "Nota registrada em aberto: em agosto de 2024 o Superior Tribunal de "
        "Justiça decidiu, em caso concreto, que a ANVISA extrapolou competência "
        "ao criar determinadas regras de propaganda. A decisão não invalida a "
        "norma como um todo, e o desenho acima segue o texto vigente por opção "
        "conservadora. Contrato com laboratório deve passar por revisão "
        "jurídica antes de assinatura.",
        tamanho=9.0, cor=NEUTRO,
    )

    d.titulo("Categorias")
    d.paragrafo(
        "Cinco cotas, todas abertas à indústria farmacêutica dentro das regras "
        "acima. Os valores são faixas de referência — leia a ressalva na página "
        "seguinte antes de tratá-los como preço."
    )
    d.tabela(
        ["Cota", "Onde aparece", "Faixa mensal"],
        [
            ["Fundadora institucional",
             "Assinatura de apoio no rodapé de todas as telas, página própria "
             "de apresentação do patrocinador e menção na abertura das "
             "publicações do período. Exclusiva — uma por vez.",
             "R$ 2.500 a R$ 4.000"],
            ["Área",
             "Vinculada a uma área clínica (arritmia, insuficiência cardíaca, "
             "dislipidemia, intervenção). Espaço identificado no rodapé das "
             "telas daquela área, sem entrar no corpo do conteúdo.",
             "R$ 800 a R$ 1.500"],
            ["Educação",
             "Trilhas de estudo e cursos parceiros. Pode ser cota fixa ou a "
             "própria margem da revenda de curso, já implementada com repasse "
             "automático ao parceiro.",
             "R$ 1.200 a R$ 2.500"],
            ["Evento",
             "Divulgação de congresso, simpósio ou curso, por período "
             "determinado, em espaço de agenda e avisos.",
             "R$ 600 a R$ 1.500 por evento"],
            ["Diretório de serviços",
             "Listagem de serviço de interesse do cardiologista — laboratório, "
             "clínica de imagem, serviço de hemodinâmica — em diretório "
             "declaradamente comercial e separado do acervo.",
             "R$ 300 a R$ 600"],
        ],
        [0.20, 0.55, 0.25],
        tamanho=8.4,
    )

    d.titulo("Sobre os valores: o que a pesquisa achou e o que não achou")
    d.paragrafo(
        "Não existe tabela pública de mídia para plataforma médica brasileira. "
        "A busca por referência de mercado devolve regulação — Resolução CFM "
        "2.336/2023, manuais de publicidade médica — e material genérico "
        "explicando modelos de cobrança por mil impressões. Nenhuma plataforma "
        "do setor publica preço."
    )
    d.destaque(
        "As faixas acima são estimativa fundamentada, não pesquisa de mercado, "
        "e estão apresentadas assim de propósito. Cobrança por mil impressões "
        "também não serve de âncora aqui: a base de assinantes ainda está em "
        "formação, e um número calculado sobre audiência pequena diria menos "
        "que o silêncio.",
        cor_fundo=TINTA_VERMELHA, cor_barra=VERMELHO, rotulo="Ressalva honesta",
    )
    d.paragrafo(
        "A âncora que faz sentido não é impressão: é a alternativa do próprio "
        "patrocinador. Um laboratório compara este espaço com estande em "
        "congresso, visita de propagandista e patrocínio de simpósio satélite — "
        "gastos que ele conhece e orça todo ano. A diferença é que aqui o "
        "contato é permanente, e não de três dias."
    )

    d.titulo("Regras de execução")
    d.itens([
        "Identificação sempre — todo espaço comercial é rotulado como "
        "Patrocinado, ou como Publicidade no caso de medicamento. Nunca "
        "aparece com aparência de conteúdo editorial.",
        "Espaço vazio desaparece — sem patrocinador, o bloco não fica como "
        "moldura vazia nem como convite. Ele simplesmente não é renderizado.",
        "Número de terceiro exige fonte declarada — a rota de cadastro recusa "
        "frase de destaque sem a fonte correspondente. Não é conferência "
        "manual: é validação de campo obrigatório.",
    ])

    d.titulo("O que não está à venda, em nenhuma cota")
    d.destaque(
        "Resposta do assistente clínico. Conteúdo da biblioteca, fluxograma, "
        "evidência e estudo. Ordem de resultado de busca. Comparador de "
        "medicamentos. Checklist e trilha de estudo. Documento gerado pelo "
        "médico. E, acima de tudo, dado de assinante — que não é "
        "compartilhado, vendido nem usado para segmentar anúncio.",
        cor_fundo=TINTA_VERMELHA, cor_barra=VERMELHO, rotulo="Fora do comércio",
    )
    d.paragrafo(
        "A razão é direta: no instante em que um patrocinador puder influenciar "
        "o que o assistente responde ou a ordem em que um medicamento aparece "
        "no comparador, o produto deixa de ter valor clínico — e, junto, deixa "
        "de ter valor comercial. A separação entre acervo e espaço pago é o "
        "que sustenta os dois."
    )

    d.titulo("Cláusula de revisão por base de assinantes")
    d.destaque(
        "O valor vigente considera a base de assinantes na data da assinatura. "
        "A cada seis meses, ou quando a base ultrapassar 300, 1.000 e 3.000 "
        "assinantes ativos, o valor é renegociado, com o número informado ao "
        "patrocinador. Se a base não crescer conforme projetado, o patrocinador "
        "tem direito a reduzir o valor ou encerrar sem multa.",
        rotulo="Texto proposto para contrato",
    )
    d.paragrafo(
        "A última frase é a que torna a cláusula bilateral, e é ela que permite "
        "negociar hoje, com a base ainda em formação, sem prometer alcance que "
        "ainda não existe."
    )


# ===========================================================================
# Montagem
# ===========================================================================

def montar(caminho: str, com_patrocinio: bool) -> None:
    titulo = "Corvia" if not com_patrocinio else "Corvia"
    subtitulo = ("Apoio à decisão clínica em Cardiologia, "
                 "para o cardiologista brasileiro")
    etiqueta = "Proposta de patrocínio" if com_patrocinio else "Apresentação"

    d = Documento(
        titulo="Corvia — apresentação" + (" e proposta de patrocínio" if com_patrocinio else ""),
        autor=AUTOR,
        assunto="Plataforma de apoio à decisão clínica em Cardiologia",
        rodape="Corvia  ·  corvia.med.br",
    )
    d.capa("O caminho do coração", subtitulo, AUTOR, REGISTRO, DATA, LOGO, etiqueta)

    capitulo_nome(d)
    capitulo_problema(d)
    capitulo_rigor(d)
    capitulo_funcoes(d)
    capitulo_numeros(d)
    capitulo_assinatura(d)
    capitulo_quem(d)
    if com_patrocinio:
        capitulo_patrocinio(d)

    d.salvar(caminho)
    print(f"  {caminho}  ({d.pagina} páginas)")


if __name__ == "__main__":
    pasta = sys.argv[1] if len(sys.argv) > 1 else "."
    print("Gerando:")
    montar(f"{pasta}/Corvia-Apresentacao.pdf", com_patrocinio=False)
    montar(f"{pasta}/Corvia-Apresentacao-Patrocinio.pdf", com_patrocinio=True)
