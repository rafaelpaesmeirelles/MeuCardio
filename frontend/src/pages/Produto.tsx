import { Link } from "react-router-dom";
import Icone, { type NomeIcone } from "../components/Icone";

const PILARES: { icone: NomeIcone; titulo: string; texto: string; itens: string[] }[] = [
  {
    icone: "clinica",
    titulo: "Decidir",
    texto: "Apoio clínico no momento em que a dúvida aparece.",
    itens: ["Assistente com fontes", "Escores e calculadoras", "Fluxogramas e interações"],
  },
  {
    icone: "pacientes",
    titulo: "Cuidar",
    texto: "Continuidade do consultório ao leito e à alta.",
    itens: ["Agenda e round", "Prescrição eletrônica", "Documentos e materiais"],
  },
  {
    icone: "conhecimento",
    titulo: "Atualizar",
    texto: "Ciência organizada para consulta e aprofundamento.",
    itens: ["Biblioteca científica", "Evidências e estudos", "Casos e trilhas"],
  },
  {
    icone: "comunicacao",
    titulo: "Conectar",
    texto: "Comunicação profissional integrada ao trabalho.",
    itens: ["Corvia Mail", "Rede profissional", "Indicadores pessoais"],
  },
];

const FLUXO = [
  { numero: "01", titulo: "A dúvida", texto: "Busque uma condição, um fármaco, um escore ou pergunte ao assistente." },
  { numero: "02", titulo: "A evidência", texto: "Consulte a resposta junto das referências e abra o conteúdo de origem." },
  { numero: "03", titulo: "A conduta", texto: "Avance para cálculo, checagem, prescrição ou documento sem perder o contexto." },
  { numero: "04", titulo: "A continuidade", texto: "Organize agenda, round, comunicação e materiais em um único espaço." },
];

export default function Produto() {
  return (
    <div className="produto">
      <header className="produto-nav">
        <Link to="/" className="produto-nav__marca" aria-label="Corvia — início">
          <img src="/corvia-logo-compacta.png" alt="Corvia" />
          <span>Ecossistema clínico</span>
        </Link>
        <nav aria-label="Navegação da página">
          <a href="#ecossistema">Ecossistema</a>
          <a href="#como-funciona">Como funciona</a>
          <a href="#qualidade">Qualidade</a>
        </nav>
        <div className="produto-nav__acoes">
          <Link to="/entrar" className="produto-link">Entrar</Link>
          <Link to="/solicitar-acesso" className="produto-botao">Solicitar acesso</Link>
        </div>
      </header>

      <main>
        <section className="produto-hero">
          <div className="produto-hero__conteudo">
            <p className="produto-selo"><span /> Cardiologia conectada, da evidência à prática</p>
            <h1>O espaço de trabalho que acompanha o médico em toda a jornada clínica.</h1>
            <p className="produto-hero__subtitulo">
              Decisão clínica, prescrição, documentos, ciência, round, comunicação e gestão —
              conectados para reduzir atrito e manter a informação útil no momento certo.
            </p>
            <div className="produto-hero__acoes">
              <Link to="/solicitar-acesso" className="produto-botao produto-botao--grande">
                Solicitar acesso profissional <Icone nome="seta" />
              </Link>
              <a href="#ecossistema" className="produto-botao produto-botao--secundario">Conhecer o ecossistema</a>
            </div>
            <div className="produto-hero__garantias" aria-label="Características de acesso">
              <span><Icone nome="check" /> Acesso profissional verificado</span>
              <span><Icone nome="check" /> Fontes clínicas identificadas</span>
              <span><Icone nome="check" /> Experiência responsiva</span>
            </div>
          </div>

          <div className="produto-demo" aria-label="Prévia do painel Corvia">
            <div className="produto-demo__barra">
              <span className="produto-demo__marca"><img src="/corvia-logo-compacta.png" alt="" /></span>
              <span className="produto-demo__busca"><Icone nome="busca" /> Buscar na Corvia</span>
              <span className="produto-demo__avatar">RM</span>
            </div>
            <div className="produto-demo__corpo">
              <aside>
                <strong><Icone nome="hoje" /> Hoje</strong>
                <span><Icone nome="clinica" /> Decisão clínica</span>
                <span><Icone nome="pacientes" /> Pacientes e prática</span>
                <span><Icone nome="conhecimento" /> Conhecimento</span>
                <span><Icone nome="comunicacao" /> Comunicação</span>
              </aside>
              <div className="produto-demo__painel">
                <div className="produto-demo__saudacao"><small>Central clínica</small><strong>Bom dia, Rafael.</strong><span>Sua rotina clínica em um só lugar.</span></div>
                <div className="produto-demo__atalhos">
                  <span className="ativo"><Icone nome="prescricao" /><b>Nova prescrição</b></span>
                  <span><Icone nome="documento" /><b>Emitir documento</b></span>
                  <span><Icone nome="triagem" /><b>Iniciar triagem</b></span>
                </div>
                <div className="produto-demo__cards">
                  <span><small>Seu dia</small><b>Agenda de hoje</b><i>Compromissos e retornos</i></span>
                  <span><small>Continuidade</small><b>Round hospitalar</b><i>Evolução e pendências</i></span>
                  <span className="escuro"><small>Comunicação</small><b>Corvia Mail</b><i>Prioridades e modelos</i></span>
                </div>
              </div>
            </div>
          </div>
        </section>

        <section className="produto-faixa" aria-label="Abrangência do sistema">
          <span>Uma plataforma</span><i />
          <strong>Decisão clínica</strong><i />
          <strong>Prática médica</strong><i />
          <strong>Conhecimento</strong><i />
          <strong>Comunicação</strong>
        </section>

        <section className="produto-secao" id="ecossistema">
          <div className="produto-secao__cabecalho">
            <p className="produto-selo"><span /> Ecossistema integrado</p>
            <h2>Menos ferramentas dispersas.<br />Mais continuidade clínica.</h2>
            <p>Cada módulo resolve uma tarefa; juntos, formam um fluxo de trabalho conectado.</p>
          </div>
          <div className="produto-pilares">
            {PILARES.map((pilar) => (
              <article key={pilar.titulo}>
                <span className="produto-pilares__icone"><Icone nome={pilar.icone} /></span>
                <h3>{pilar.titulo}</h3>
                <p>{pilar.texto}</p>
                <ul>{pilar.itens.map((item) => <li key={item}><Icone nome="check" />{item}</li>)}</ul>
              </article>
            ))}
          </div>
        </section>

        <section className="produto-fluxo" id="como-funciona">
          <div className="produto-fluxo__intro">
            <p className="produto-selo produto-selo--claro"><span /> Um fluxo, não um catálogo</p>
            <h2>Do primeiro questionamento à continuidade do cuidado.</h2>
            <p>A Corvia mantém as ferramentas próximas da etapa seguinte, para o médico avançar sem reconstruir seu raciocínio a cada tela.</p>
          </div>
          <ol>
            {FLUXO.map((item) => (
              <li key={item.numero}>
                <span>{item.numero}</span><div><h3>{item.titulo}</h3><p>{item.texto}</p></div>
              </li>
            ))}
          </ol>
        </section>

        <section className="produto-qualidade" id="qualidade">
          <div className="produto-qualidade__visual">
            <span className="produto-qualidade__orbita produto-qualidade__orbita--um" />
            <span className="produto-qualidade__orbita produto-qualidade__orbita--dois" />
            <span className="produto-qualidade__centro"><Icone nome="evidencia" /></span>
            <span className="produto-qualidade__nota nota--um">Fonte identificada</span>
            <span className="produto-qualidade__nota nota--dois">Classe e nível</span>
            <span className="produto-qualidade__nota nota--tres">Contexto clínico</span>
          </div>
          <div className="produto-qualidade__texto">
            <p className="produto-selo"><span /> Qualidade rastreável</p>
            <h2>Conteúdo que mostra de onde veio.</h2>
            <p>
              A Corvia organiza diretrizes, estudos e recomendações para consulta profissional,
              mantendo referências visíveis e separando apoio à decisão de julgamento clínico.
            </p>
            <ul>
              <li><Icone nome="check" /><span><strong>Referência verificável</strong> no conteúdo científico disponível.</span></li>
              <li><Icone nome="check" /><span><strong>Contexto de uso</strong> para interpretar antes de aplicar.</span></li>
              <li><Icone nome="check" /><span><strong>Responsabilidade profissional</strong> preservada em toda decisão.</span></li>
            </ul>
          </div>
        </section>

        <section className="produto-cta" id="acesso">
          <div>
            <p className="produto-selo produto-selo--claro"><span /> Comece sua jornada</p>
            <h2>Traga mais continuidade para sua rotina clínica.</h2>
            <p>Solicite o acesso com seus dados profissionais. O cadastro passa por verificação antes da liberação.</p>
          </div>
          <div>
            <Link to="/solicitar-acesso" className="produto-botao produto-botao--claro">Solicitar acesso <Icone nome="seta" /></Link>
            <Link to="/entrar" className="produto-cta__entrar">Já tenho conta</Link>
          </div>
        </section>
      </main>

      <footer className="produto-rodape">
        <img src="/corvia-logo-compacta.png" alt="Corvia" />
        <p>Suporte à decisão clínica para profissionais de saúde. Não substitui avaliação, julgamento ou responsabilidade profissional.</p>
        <Link to="/entrar">Acesso profissional</Link>
      </footer>
    </div>
  );
}
