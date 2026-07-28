import { useEffect, useState } from "react";
import { Link } from "react-router-dom";
import { api } from "../lib/api";
import { useAuth } from "../lib/auth";
import ApoioBiolab from "../components/ApoioBiolab";

type Tema = { theme: string; count: number };
type Paciente = { id: number };
type ListaComTotal = { total?: number };

/** Funções do sistema, na ordem em que fazem sentido no dia a dia.
 *  `destaque` marca as três de uso mais frequente no ponto de cuidado — elas
 *  recebem a borda em vermelho da marca; o resto fica em teal.
 *  As descrições dizem o que a função resolve, não o nome técnico dela. */
const FUNCOES: { to: string; nome: string; descricao: string; destaque?: boolean }[] = [
  {
    to: "/assistente",
    nome: "Assistente clínico",
    descricao: "Pergunte em linguagem natural e receba a resposta ancorada nos documentos da biblioteca, com a fonte citada.",
    destaque: true,
  },
  {
    to: "/fluxogramas",
    nome: "Fluxogramas clínicos",
    descricao: "Árvores de decisão fundamentadas em diretriz vigente (ESC, AHA/ACC, SBC) — cada ramo termina numa conduta.",
    destaque: true,
  },
  {
    to: "/calculadoras",
    nome: "Calculadoras",
    descricao: "Escores validados — GRACE, HEART, CHA₂DS₂-VASc, HAS-BLED, CKD-EPI — prontos para uso no leito, com a fórmula à vista.",
    destaque: true,
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
    to: "/medicamentos",
    nome: "Medicamentos",
    descricao: "Comparador lado a lado: dose, apresentação, ajuste renal, contraindicação e interação.",
  },
  {
    to: "/galeria",
    nome: "Galeria de imagens",
    descricao: "Achados de ECG, eco, TC, radiografia e angiografia, com o achado descrito e os pontos de ensino.",
  },
  {
    to: "/exames",
    nome: "Exames e marcadores",
    descricao: "O que cada exame mede, valor de referência, quando pedir e o que limita a interpretação.",
  },
  {
    to: "/evidencias",
    nome: "Evidências",
    descricao: "A recomendação pontual, com classe, nível, sociedade e ano — não o documento inteiro.",
  },
  {
    to: "/estudos",
    nome: "Trabalhos científicos",
    descricao: "Ensaios, revisões e metanálises com os números reais do estudo e a implicação clínica.",
  },
  {
    to: "/round",
    nome: "Round hospitalar",
    descricao: "Pacientes internados, evolução, prescrição e linha do tempo de cada caso.",
  },
  {
    to: "/agenda",
    nome: "Agenda",
    descricao: "Compromissos, retornos e o que está marcado para os próximos dias.",
  },
  {
    to: "/documentos",
    nome: "Modelos de documento",
    descricao: "Templates que geram o documento já preenchido com os dados do paciente.",
  },
  {
    to: "/favoritos",
    nome: "Favoritos",
    descricao: "O que você marcou para reencontrar sem procurar de novo.",
  },
  {
    to: "/minha-conta",
    nome: "Minha conta",
    descricao: "Dados pessoais, troca de senha e gestão da assinatura.",
  },
];

function Numero({ rotulo, valor, to }: { rotulo: string; valor: number | null; to: string }) {
  return (
    <Link to={to} className="painel__numero">
      <span className="dado">{valor === null ? "—" : valor}</span>
      <span>{rotulo}</span>
    </Link>
  );
}

export default function Painel() {
  const { usuario } = useAuth();
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

    api.get<Tema[]>("/library/themes").then(setTemas).catch(() => setTemas([]));
    api.get<Paciente[]>("/round/patients").then((l) => setPacientes(l.length)).catch(() => setPacientes(null));
    total("/library/documents?kind=fluxograma&limit=1").then(setFluxogramas);
    total("/gallery/images?limit=1").then(setImagens);
    total("/lab-tests?limit=1").then(setExames);
    total("/evidence?limit=1").then(setEvidencias);
    total("/studies?limit=1").then(setEstudos);
  }, []);

  const totalDocs = temas?.reduce((s, t) => s + t.count, 0) ?? null;

  return (
    <>
      <p className="eyebrow">Painel</p>
      <h1>Bom trabalho, {usuario?.full_name.split(" ")[0]}.</h1>

      {/* Barra compacta: os números continuam existindo, mas deixam de ser o
          elemento principal da tela. Cada um leva à própria seção. */}
      <div className="painel__numeros">
        <Numero rotulo="documentos" valor={totalDocs} to="/biblioteca" />
        <Numero rotulo="fluxogramas" valor={fluxogramas} to="/fluxogramas" />
        <Numero rotulo="imagens" valor={imagens} to="/galeria" />
        <Numero rotulo="exames" valor={exames} to="/exames" />
        <Numero rotulo="evidências" valor={evidencias} to="/evidencias" />
        <Numero rotulo="estudos" valor={estudos} to="/estudos" />
        <Numero rotulo="no round" valor={pacientes} to="/round" />
      </div>

      <h2 style={{ marginTop: "1.6rem" }}>Acesso rápido</h2>
      <div className="painel__funcoes">
        {FUNCOES.map((f) => (
          <Link
            key={f.to}
            to={f.to}
            className={`cartao painel__funcao${f.destaque ? " painel__funcao--destaque" : ""}`}
          >
            <strong>{f.nome}</strong>
            <span>{f.descricao}</span>
          </Link>
        ))}
      </div>

      {temas !== null && temas.length > 0 && (
        <>
          <h2 style={{ marginTop: "1.8rem" }}>Temas da biblioteca</h2>
          <div className="painel__temas">
            {temas.map((t) => (
              <Link key={t.theme} to={`/biblioteca?tema=${encodeURIComponent(t.theme)}`} className="painel__tema">
                {t.theme}
                <span className="dado">{t.count}</span>
              </Link>
            ))}
          </div>
        </>
      )}

      <ApoioBiolab />
    </>
  );
}
