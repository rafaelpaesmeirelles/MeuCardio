import type { CSSProperties } from "react";
import { Link } from "react-router-dom";
import Icone, { type NomeIcone } from "../components/Icone";
import { PublicCorviaBrand } from "../components/PublicCardiologyFrame";

const ESPACOS: Array<{
  id: string;
  name: string;
  role: string;
  image: string;
  icon: NomeIcone;
}> = [
  { id: "consultorio", name: "Consultório", role: "Assistir e acompanhar", image: "/spaces/corvia-room-consultorio-640.webp", icon: "clinica" },
  { id: "hospital", name: "Hospital", role: "Decidir sob pressão", image: "/spaces/corvia-room-hospital-640.webp", icon: "emergencia" },
  { id: "ensino", name: "Ensino", role: "Aprender e ensinar", image: "/spaces/corvia-room-ensino-640.webp", icon: "curso" },
  { id: "pesquisa", name: "Pesquisa", role: "Validar evidências", image: "/spaces/corvia-room-pesquisa-640.webp", icon: "evidencia" },
  { id: "gestao", name: "Gestão", role: "Conduzir a operação", image: "/spaces/corvia-room-gestao-640.webp", icon: "indicadores" },
];

const MODOS = [
  {
    id: "completo",
    icon: "sincronizar" as const,
    title: "Completo",
    text: "Todos os espaços, camadas e relações disponíveis para uma jornada clínica sem rupturas.",
    detail: "Agora · Em seguida · Referências",
  },
  {
    id: "essencial",
    icon: "hoje" as const,
    title: "Essencial",
    text: "A mesma potência organizada ao redor do que precisa de atenção neste momento.",
    detail: "Rotina · Prioridades · Personalização",
  },
  {
    id: "ciencia",
    icon: "conhecimento" as const,
    title: "Ciência & Ensino",
    text: "Conhecimento, evidência, formação e produção científica dentro do mesmo universo.",
    detail: "Descobrir · Validar · Aprender",
  },
];

const CAMADAS = [
  { label: "Agora", title: "O que o contexto pede", text: "Ações e decisões prioritárias surgem no espaço em que o médico está.", icon: "hoje" as const },
  { label: "Essenciais", title: "O que sustenta a rotina", text: "Ferramentas frequentes permanecem próximas, sem transformar a experiência em catálogo.", icon: "favorito" as const },
  { label: "Referências", title: "O que fundamenta a decisão", text: "Evidências, protocolos e relações clínicas continuam rastreáveis no mesmo fluxo.", icon: "evidencia" as const },
];

function StarField() {
  return <div className="public-showcase__stars" aria-hidden="true"><i /><i /><i /><i /><i /><i /><i /><i /><i /><i /><i /><i /></div>;
}

export default function Produto() {
  return (
    <div className="public-showcase">
      <a className="public-space__skip" href="#conteudo-principal">Ir para o conteúdo</a>
      <StarField />
      <header className="public-showcase__topbar">
        <PublicCorviaBrand to="/produto" />
        <nav aria-label="Navegação da apresentação">
          <a href="#espacos">Espaços</a>
          <a href="#experiencias">Experiências</a>
          <a href="#sistema">Como funciona</a>
          <a href="#qualidade">Ciência e segurança</a>
        </nav>
        <div className="public-showcase__actions">
          <Link to="/entrar">Entrar</Link>
          <Link to="/solicitar-acesso" className="is-primary">Solicitar acesso</Link>
        </div>
      </header>

      <main id="conteudo-principal" tabIndex={-1}>
        <section className="public-showcase__hero" id="espacos" aria-labelledby="produto-title">
          <div className="public-showcase__hero-copy">
            <p><span /> CORVIA · CARDIOLOGY SPACES</p>
            <h1 id="produto-title">O ambiente muda. O <strong>Médico continua no centro.</strong></h1>
            <div>Uma plataforma que reorganiza a cardiologia ao redor do contexto — sem separar ciência, decisão, ação e continuidade.</div>
            <div className="public-showcase__hero-actions">
              <Link to="/solicitar-acesso">Solicitar acesso profissional <Icone nome="seta" /></Link>
              <Link to="/entrar" className="is-secondary">Já tenho acesso</Link>
            </div>
          </div>

          <div className="public-showcase__portals" aria-label="Cinco ambientes do CorVIA">
            {ESPACOS.map((space) => (
              <Link to="/entrar" className={`public-showcase__portal public-showcase__portal--${space.id}`} data-space={space.id} key={space.id} aria-label={`${space.name}: ${space.role}. Entrar no CorVIA`}>
                <img src={space.image} alt="" width="640" height="427" loading={space.id === "consultorio" ? "eager" : "lazy"} />
                <span className="public-showcase__portal-glass" />
                <div><span><Icone nome={space.icon} /></span><strong>{space.name}</strong><small>{space.role}</small></div>
                <i>Entrar <Icone nome="seta" /></i>
              </Link>
            ))}
          </div>
          <p className="public-showcase__continuity">Cinco ambientes. <strong>Uma única continuidade clínica.</strong></p>
        </section>

        <section className="public-showcase__section public-showcase__modes" id="experiencias" aria-labelledby="experiencias-title">
          <header>
            <p>TRÊS FORMAS DE HABITAR O MESMO SISTEMA</p>
            <h2 id="experiencias-title">A experiência acompanha o momento.</h2>
            <span>Profundidade quando necessária. Foco quando o tempo pede. Ciência quando a pergunta exige.</span>
          </header>
          <div>
            {MODOS.map((mode) => (
              <article data-mode={mode.id} key={mode.id}>
                <span><Icone nome={mode.icon} /></span>
                <p>{mode.detail}</p>
                <h3>{mode.title}</h3>
                <div>{mode.text}</div>
              </article>
            ))}
          </div>
        </section>

        <section className="public-showcase__section public-showcase__system" id="sistema" aria-labelledby="sistema-title">
          <header>
            <p>CONTINUIDADE EM CAMADAS</p>
            <h2 id="sistema-title">A interface não disputa atenção. Ela organiza o raciocínio.</h2>
            <span>Cada ambiente preserva a mesma gramática visual e muda apenas o que o trabalho daquele espaço exige.</span>
          </header>
          <div className="public-showcase__planes">
            {CAMADAS.map((layer, index) => (
              <article key={layer.label} style={{ "--plane-index": index } as CSSProperties}>
                <span><Icone nome={layer.icon} /></span>
                <p>{layer.label}</p>
                <h3>{layer.title}</h3>
                <div>{layer.text}</div>
              </article>
            ))}
          </div>
        </section>

        <section className="public-showcase__quality" id="qualidade" aria-labelledby="qualidade-title">
          <div className="public-showcase__quality-map" aria-hidden="true">
            <span><Icone nome="evidencia" /></span>
            <i /><i /><i /><i /><i />
            <b>Fonte</b><b>Contexto</b><b>Decisão</b>
          </div>
          <div>
            <p>CIÊNCIA E SEGURANÇA</p>
            <h2 id="qualidade-title">Conhecimento conectado precisa continuar verificável.</h2>
            <div>O CorVIA aproxima evidências, diretrizes, medicamentos, exames e ações sem esconder a origem da informação nem retirar do Médico a decisão final.</div>
            <ul>
              <li><Icone nome="check" /><span><strong>Fontes rastreáveis</strong> e contexto editorial preservado.</span></li>
              <li><Icone nome="check" /><span><strong>Dados privados separados</strong> do corpus científico e das relações públicas.</span></li>
              <li><Icone nome="check" /><span><strong>Ações consequenciais sob controle</strong> do profissional responsável.</span></li>
            </ul>
          </div>
        </section>

        <section className="public-showcase__cta" aria-label="Solicitar acesso ao CorVIA">
          <div><p>O PRÓXIMO ESPAÇO É SEU</p><h2>Entre em uma cardiologia que continua com você.</h2><span>Consultório, Hospital, Ensino, Pesquisa e Gestão — conectados por uma identidade única.</span></div>
          <div><Link to="/solicitar-acesso">Solicitar acesso <Icone nome="seta" /></Link><Link to="/entrar" className="is-secondary">Entrar</Link></div>
        </section>
      </main>

      <footer className="public-showcase__footer">
        <PublicCorviaBrand to="/produto" />
        <p>CorVIA Cardiology Spaces · apoio ao trabalho profissional. Não substitui julgamento clínico nem responsabilidade médica.</p>
        <nav aria-label="Links institucionais"><Link to="/privacidade">Privacidade</Link><Link to="/termos">Termos</Link><Link to="/excluir-conta">Excluir conta</Link><a href="mailto:contato@corvia.med.br">Contato</a></nav>
      </footer>
    </div>
  );
}
