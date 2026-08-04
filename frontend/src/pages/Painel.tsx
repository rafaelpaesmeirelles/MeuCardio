import { useEffect, useState } from "react";
import { Link } from "react-router-dom";
import { api } from "../lib/api";
import LogoCorviaMail from "../components/LogoCorviaMail";
import { useAuth } from "../lib/auth";

type Tema = { theme: string; count: number };
type Paciente = { id: number };
type ListaComTotal = { total?: number };
type Catalogo = {
  total: number;
  expected_minimum?: number;
  physical_files_expected?: number;
  integrity_ok?: boolean;
  missing?: number;
};

/** Uma função do sistema no Painel.
 *  `to` ausente = função ainda não construída: vira cartão "em breve", sem link.
 *  `acao` permite abrir uma função global, como o chat flutuante.
 *  `destaque` reserva a borda vermelha da marca para o que se usa sob pressão. */
type Funcao = {
  to?: string;
  acao?: "abrir-chat";
  nome: string;
  descricao: string;
  destaque?: boolean;
};
type Grupo = { titulo: string; descricao: string; funcoes: Funcao[] };

/** Agrupado por finalidade, não por ordem de construção — o médico procura pelo
 *  problema que tem ("preciso decidir", "preciso estudar"), não pelo nome do
 *  módulo. As descrições dizem o que a função resolve, não o que ela é. */
const GRUPOS: Grupo[] = [
  {
    titulo: "Apoio à decisão clínica",
    descricao: "Para usar com o paciente na frente.",
    funcoes: [
      {
        to: "/condicoes",
        nome: "Alerta por condição especial",
        descricao: "Cruza o que vai ser prescrito ou pedido com gestação, doença renal crônica, hepatopatia e outras condições.",
      },
      {
        to: "/assistente",
        nome: "Assistente clínico",
        descricao: "Pergunte em linguagem natural e receba a resposta ancorada nos documentos da biblioteca, com a fonte citada.",
        destaque: true,
      },
      {
        to: "/calculadoras",
        nome: "Calculadoras",
        descricao: "Escores validados — GRACE, HEART, CHA₂DS₂-VASc, HAS-BLED, CKD-EPI — prontos para uso no leito, com a fórmula à vista.",
        destaque: true,
      },
      {
        to: "/interacoes",
        nome: "Checador de Interação Medicamentosa",
        descricao: "Monte a lista do que o paciente já usa e do que você vai prescrever, e veja as interações com gravidade e fonte.",
      },
      {
        to: "/fluxogramas",
        nome: "Fluxogramas clínicos",
        descricao: "Árvores de decisão fundamentadas em diretriz vigente (ESC, AHA/ACC, SBC) — cada ramo termina numa conduta.",
        destaque: true,
      },
      {
        to: "/medicamentos",
        nome: "Medicamentos",
        descricao: "Comparador lado a lado: dose, apresentação, ajuste renal, contraindicação e interação, com a bula de origem declarada.",
      },
    ],
  },
  {
    titulo: "Ciência e atualização",
    descricao: "A base que sustenta a conduta, com referência verificável.",
    funcoes: [
      {
        to: "/diretrizes",
        nome: "Alertas de diretriz",
        descricao: "Avisa quando sai versão nova da diretriz que embasa um documento que você favoritou.",
      },
      {
        to: "/biblioteca",
        nome: "Biblioteca científica",
        descricao: "Documentos organizados por tema, cada um com referência completa e verificável.",
      },
      {
        to: "/busca",
        nome: "Busca",
        descricao: "Busca em texto completo nos documentos, com o trecho relevante destacado no resultado.",
      },
      {
        to: "/evidencias",
        nome: "Evidências",
        descricao: "A recomendação pontual, com classe, nível, sociedade e ano — não o documento inteiro.",
      },
      {
        to: "/exames",
        nome: "Exames e marcadores",
        descricao: "O que cada exame mede, valor de referência, quando pedir e o que limita a interpretação.",
      },
      {
        to: "/galeria",
        nome: "Galeria de imagens",
        descricao: "Achados de ECG, eco, TC, radiografia e angiografia, com o achado descrito e os pontos de ensino.",
      },
      {
        to: "/estudos",
        nome: "Trabalhos científicos",
        descricao: "Ensaios, revisões e metanálises com os números reais do estudo e a implicação clínica.",
      },
    ],
  },
  {
    titulo: "Beira do leito",
    descricao: "O que acompanha o paciente do round à alta.",
    funcoes: [
      {
        to: "/checklists",
        nome: "Checklist de alta",
        descricao: "O que não pode faltar na alta pós-evento cardiovascular, marcado item a item antes de liberar.",
      },
      {
        to: "/round",
        nome: "Round hospitalar",
        descricao: "Pacientes internados, evolução, prescrição e linha do tempo de cada caso.",
      },
    ],
  },
  {
    titulo: "Documentos",
    descricao: "O que sai do consultório — receita, atestado, laudo, material do paciente e agenda.",
    funcoes: [
      {
        to: "/agenda",
        nome: "Agenda",
        descricao: "Compromissos, retornos e o que está marcado para os próximos dias.",
      },
      {
        to: "/documentos",
        nome: "Emissão de Documentos Online",
        descricao: "Templates que geram o documento já preenchido com os dados do paciente.",
      },
      {
        nome: "Laudo e consultoria",
        descricao: "Envie ECG, MAPA, Holter ou teste ergométrico e receba interpretação ou laudo, com prazo definido.",
      },
      {
        to: "/material-paciente",
        nome: "Material para o paciente",
        descricao: "Explicação da condição em linguagem acessível, em PDF, para entregar na consulta.",
      },
      {
        to: "/receituario",
        nome: "Prescrição Eletrônica",
        descricao: "Monte a receita com os fármacos da base estruturada e emita para o paciente.",
      },
    ],
  },
  {
    titulo: "Educação continuada",
    descricao: "Para estudar e para ensinar.",
    funcoes: [
      {
        to: "/casos-clinicos",
        nome: "Casos clínicos interativos",
        descricao: "Um caso, a sua decisão, e depois a conduta correta com a evidência que a sustenta.",
      },
      {
        nome: "Cursos parceiros",
        descricao: "Preparação para o Título de Especialista, com material de apoio arquivado aqui.",
      },
      {
        to: "/trilhas",
        nome: "Trilhas de estudo",
        descricao: "Sequência guiada por tema: o protocolo, a farmacologia, os estudos pivotais e as calculadoras, nessa ordem.",
      },
    ],
  },
  {
    titulo: "Comunicação profissional",
    descricao: "Converse com outros usuários e use sua caixa profissional integrada.",
    funcoes: [
      {
        acao: "abrir-chat",
        nome: "CorvIA Chat",
        descricao: "Mensagens em tempo real entre usuários, busca por profissional, conversas, não lidas e contato direto com o suporte.",
      },
      {
        to: "/corvia-mail",
        nome: "CorvIA Mail",
        descricao: "Acesse ou assine sua caixa profissional @corvia.med.br e abra o webmail integrado.",
      },
    ],
  },
  {
    titulo: "Sua conta",
    descricao: "O que é seu e só você vê.",
    funcoes: [
      {
        to: "/favoritos",
        nome: "Favoritos",
        descricao: "O que você marcou para reencontrar sem procurar de novo.",
      },
      {
        to: "/indicadores",
        nome: "Meus indicadores",
        descricao: "Laudos emitidos, tempo de resposta frente ao SLA e receita do telediagnóstico no período.",
      },
      {
        to: "/minha-conta",
        nome: "Minha conta",
        descricao: "Dados pessoais, troca de senha e gestão da assinatura.",
      },
    ],
  },
];

function Numero({ rotulo, valor, to }: { rotulo: string; valor: number | null; to: string }) {
  return (
    <Link to={to} className="painel__numero">
      <span className="dado">{valor === null ? "—" : valor.toLocaleString("pt-BR")}</span>
      <span>{rotulo}</span>
    </Link>
  );
}

function abrirChatGlobal() {
  const botao = document.querySelector<HTMLButtonElement>(
    'button[aria-label^="Abrir o CorvIA Chat"]',
  );
  botao?.click();
}

function Cartao({ f }: { f: Funcao }) {
  const classe = `cartao painel__funcao${f.destaque ? " painel__funcao--destaque" : ""}`;

  if (f.acao === "abrir-chat") {
    return (
      <button
        type="button"
        className={classe}
        onClick={abrirChatGlobal}
        style={{ textAlign: "left", width: "100%", cursor: "pointer" }}
      >
        <strong>{f.nome}</strong>
        <span>{f.descricao}</span>
      </button>
    );
  }

  // Sem rota: a função ainda não existe. Vira cartão inerte, com o selo dizendo
  // isso — melhor do que link que leva a lugar nenhum ou do que esconder o que
  // está por vir.
  if (!f.to) {
    return (
      <div className={`${classe} painel__funcao--breve`}>
        <strong>
          {f.nome} <span className="painel__breve">em breve</span>
        </strong>
        <span>{f.descricao}</span>
      </div>
    );
  }

  return (
    <Link to={f.to} className={classe}>
      <strong>{f.nome}</strong>
      <span>{f.descricao}</span>
    </Link>
  );
}

export default function Painel() {
  const { usuario } = useAuth();
  const [catalogo, setCatalogo] = useState<Catalogo | null>(null);
  const [temas, setTemas] = useState<Tema[] | null>(null);
  const [pacientes, setPacientes] = useState<number | null>(null);
  const [fluxogramas, setFluxogramas] = useState<number | null>(null);
  const [imagens, setImagens] = useState<number | null>(null);
  const [exames, setExames] = useState<number | null>(null);
  const [evidencias, setEvidencias] = useState<number | null>(null);
  const [estudos, setEstudos] = useState<number | null>(null);

  useEffect(() => {
    // Cada contador falha sozinho: um endpoint fora do ar deixa o número como
    // "—" em vez de derrubar o painel inteiro, que é a tela de entrada.
    const total = (p: string) =>
      api.get<ListaComTotal>(p).then((d) => d.total ?? 0).catch(() => null);

    api.get<Catalogo>("/library/catalog").then(setCatalogo).catch(() => setCatalogo(null));
    api.get<Tema[]>("/library/themes").then(setTemas).catch(() => setTemas([]));
    api.get<Paciente[]>("/round/patients").then((l) => setPacientes(l.length)).catch(() => setPacientes(null));
    total("/library/documents?kind=fluxograma&limit=1").then(setFluxogramas);
    total("/gallery/images?limit=1").then(setImagens);
    total("/lab-tests?limit=1").then(setExames);
    total("/evidence?limit=1").then(setEvidencias);
    total("/studies?limit=1").then(setEstudos);
  }, []);

  return (
    <>
      <p className="eyebrow">Painel</p>
      <h1>Bom trabalho, {usuario?.full_name.split(" ")[0]}.</h1>

      {/* O primeiro número usa o catálogo canônico das 11 coleções. Somar temas
          mostrava apenas a tabela Document e subestimava o acervo completo. */}
      <div className="painel__numeros">
        <Numero rotulo="itens científicos" valor={catalogo?.total ?? null} to="/biblioteca" />
        <Numero rotulo="fluxogramas" valor={fluxogramas} to="/fluxogramas" />
        <Numero rotulo="imagens" valor={imagens} to="/galeria" />
        <Numero rotulo="exames" valor={exames} to="/exames" />
        <Numero rotulo="evidências" valor={evidencias} to="/evidencias" />
        <Numero rotulo="estudos" valor={estudos} to="/estudos" />
        <Numero rotulo="no round" valor={pacientes} to="/round" />
      </div>

      {usuario?.role === "admin" && catalogo?.integrity_ok === false && (
        <section
          className="cartao"
          role="alert"
          style={{ borderColor: "var(--acao)", marginBottom: "1rem" }}
        >
          <strong>Acervo de produção abaixo do inventário certificado</strong>
          <p style={{ marginBottom: 0 }}>
            O PostgreSQL retornou {catalogo.total.toLocaleString("pt-BR")} itens das 11 coleções.
            O mínimo certificado é {(catalogo.expected_minimum ?? 4_936).toLocaleString("pt-BR")};
            faltam {(catalogo.missing ?? 0).toLocaleString("pt-BR")} registros. O inventário também
            preserva {(catalogo.physical_files_expected ?? 1_327).toLocaleString("pt-BR")} arquivos físicos.
            Execute a reconciliação do corpus antes de considerar o deploy íntegro.
          </p>
        </section>
      )}

      {/* Os modos de uso ficam fora dos grupos porque mudam a forma de usar o
          sistema inteiro. */}
      <div className="painel__modos">
        <Link to="/emergencia" className="cartao painel__modo painel__modo--emergencia">
          <strong>● Modo Emergência</strong>
          <span>
            Protocolos de risco imediato de vida, em fonte grande e alto contraste,
            com cópia local que abre mesmo sem conexão.
          </span>
        </Link>
        <Link to="/biblioteca" className="cartao painel__modo">
          <strong>▣ Modo Apresentação</strong>
          <span>
            Exporte qualquer documento ou fluxograma em PDF pronto para projetar em
            aula ou round — o botão fica dentro de cada documento, com espaço para a
            sua anotação.
          </span>
        </Link>
        <Link to="/corvia-mail" className="cartao painel__modo painel__modo--mail">
          <LogoCorviaMail tamanho="compacto" />
          <span>
            Sua caixa de e-mail própria @corvia.med.br, com webmail integrado —
            entre ou assine em um clique.
          </span>
        </Link>
      </div>

      {GRUPOS.map((g) => (
        <section key={g.titulo} className="painel__grupo">
          <h2>{g.titulo}</h2>
          <p className="painel__grupo-sub">{g.descricao}</p>
          <div className="painel__funcoes">
            {g.funcoes.map((f) => (
              <Cartao key={f.nome} f={f} />
            ))}
          </div>
        </section>
      ))}

      {temas !== null && temas.length > 0 && (
        <section className="painel__grupo">
          <h2>Temas da biblioteca</h2>
          <div className="painel__temas">
            {temas.map((t) => (
              <Link key={t.theme} to={`/biblioteca?tema=${encodeURIComponent(t.theme)}`} className="painel__tema">
                {t.theme}
                <span className="dado">{t.count.toLocaleString("pt-BR")}</span>
              </Link>
            ))}
          </div>
        </section>
      )}
    </>
  );
}
