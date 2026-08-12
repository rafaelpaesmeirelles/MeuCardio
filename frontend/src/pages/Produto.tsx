import { Link } from "react-router-dom";
import Icone, { type NomeIcone } from "../components/Icone";

const PILARES: { icone: NomeIcone; titulo: string; texto: string; itens: string[] }[] = [
  {
    icone: "busca",
    titulo: "Resolver",
    texto: "Comece pelo que você precisa fazer agora — não pelo módulo onde isso mora.",
    itens: ["Command Bar universal", "Busca clínica e científica", "Ações executáveis no mesmo fluxo"],
  },
  {
    icone: "assistente",
    titulo: "Entender contexto",
    texto: "A inteligência muda conforme a tarefa, sem transformar tudo em chatbot.",
    itens: ["CorVIA Intelligence", "Assistente Clínica", "Assistente Pessoal"],
  },
  {
    icone: "conhecimento",
    titulo: "Conectar conhecimento",
    texto: "Condição, medicamento, estudo, guideline, exame e ação deixam de ser ilhas.",
    itens: ["Evidências e estudos", "Guidelines e medicamentos", "Clinical Thread e relações"],
  },
  {
    icone: "prescricao",
    titulo: "Agir",
    texto: "Decisão clínica e execução permanecem próximas no mesmo workspace.",
    itens: ["Prescrição", "Documentos e solicitações", "Agenda, pacientes e comunicação"],
  },
];

const FLUXO = [
  { numero: "01", titulo: "Necessidade", texto: "O que você precisa resolver agora? Pesquisar, revisar, calcular, prescrever, documentar ou organizar." },
  { numero: "02", titulo: "Contexto", texto: "O CorVIA aproxima o que é relevante sem obrigar você a reconstruir o raciocínio em outra ferramenta." },
  { numero: "03", titulo: "Conhecimento e decisão", texto: "Evidências, guidelines, medicamentos, exames e critérios permanecem conectados e rastreáveis." },
  { numero: "04", titulo: "Ação", texto: "Avance para prescrição, solicitação, documento, paciente, agenda ou comunicação sem perder o contexto." },
];

export default function Produto() {
  return (
    <div className="produto">
      <header className="produto-nav">
        <Link to="/" className="produto-nav__marca" aria-label="CorVIA — início">
          <img src="/corvia-logo-compacta.png" alt="CorVIA" />
          <span>Clinical OS do médico</span>
        </Link>
        <nav aria-label="Navegação da página">
          <a href="#clinical-os">Clinical OS</a>
          <a href="#como-funciona">Como funciona</a>
          <a href="#qualidade">Ciência e segurança</a>
        </nav>
        <div className="produto-nav__acoes">
          <Link to="/entrar" className="produto-link">Entrar</Link>
          <Link to="/solicitar-acesso" className="produto-botao">Solicitar acesso</Link>
        </div>
      </header>

      <main>
        <section className="produto-hero">
          <div className="produto-hero__conteudo">
            <p className="produto-selo"><span /> CorVIA · Clinical OS do médico</p>
            <h1>Um sistema operacional para o trabalho médico.</h1>
            <p className="produto-hero__subtitulo">
              Conhecimento, contexto, paciente, decisão e ação conectados em um único workspace —
              construído a partir do que o médico precisa resolver agora.
            </p>
            <div className="produto-hero__acoes">
              <Link to="/solicitar-acesso" className="produto-botao produto-botao--grande">
                Solicitar acesso profissional <Icone nome="seta" />
              </Link>
              <a href="#clinical-os" className="produto-botao produto-botao--secundario">Entender o Clinical OS</a>
            </div>
            <div className="produto-hero__garantias" aria-label="Princípios do CorVIA">
              <span><Icone nome="check" /> Médico no centro do produto</span>
              <span><Icone nome="check" /> Ciência com fontes rastreáveis</span>
              <span><Icone nome="check" /> Desktop e mobile pensados para contextos reais</span>
            </div>
          </div>

          <div className="produto-demo" aria-label="Prévia do Clinical Command Center CorVIA">
            <div className="produto-demo__barra">
              <span className="produto-demo__marca"><img src="/corvia-logo-compacta.png" alt="" /></span>
              <span className="produto-demo__busca"><Icone nome="busca" /> Pergunte, pesquise ou execute uma ação...</span>
              <span className="produto-demo__avatar">RM</span>
            </div>
            <div className="produto-demo__corpo">
              <aside>
                <strong><Icone nome="hoje" /> Início</strong>
                <span><Icone nome="busca" /> Buscar</span>
                <span><Icone nome="medicamento" /> Medicamentos</span>
                <span><Icone nome="evidencia" /> Evidências</span>
                <span><Icone nome="pacientes" /> Pacientes</span>
                <span><Icone nome="agenda" /> Agenda</span>
              </aside>
              <div className="produto-demo__painel">
                <div className="produto-demo__saudacao"><small>Clinical Command Center</small><strong>O que você precisa resolver agora?</strong><span>Pesquisa, decisão e ação a partir do mesmo ponto.</span></div>
                <div className="produto-demo__atalhos">
                  <span className="ativo"><Icone nome="prescricao" /><b>Prescrever</b></span>
                  <span><Icone nome="clinica" /><b>Solicitar exames</b></span>
                  <span><Icone nome="documento" /><b>Documento</b></span>
                </div>
                <div className="produto-demo__cards">
                  <span><small>Continuar</small><b>Insuficiência cardíaca</b><i>Condição → tratamento → evidência</i></span>
                  <span><small>CorVIA Intelligence</small><b>3 relações relevantes</b><i>Estudos, guideline e medicamento</i></span>
                  <span className="escuro"><small>Assistente Pessoal</small><b>Seu dia</b><i>Agenda e pendências sob demanda</i></span>
                </div>
              </div>
            </div>
          </div>
        </section>

        <section className="produto-faixa" aria-label="Arquitetura do Clinical OS">
          <span>Necessidade</span><i />
          <strong>Contexto</strong><i />
          <strong>Conhecimento</strong><i />
          <strong>Decisão</strong><i />
          <strong>Ação</strong>
        </section>

        <section className="produto-secao" id="clinical-os">
          <div className="produto-secao__cabecalho">
            <p className="produto-selo"><span /> Uma categoria diferente</p>
            <h2>Não é prontuário.<br />Não é chatbot. É o workspace do médico.</h2>
            <p>O CorVIA reduz o atrito cognitivo entre a necessidade clínica e a ação necessária para resolvê-la.</p>
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
            <h2>O sistema acompanha o raciocínio em vez de obrigar o médico a acompanhar o sistema.</h2>
            <p>A arquitetura aproxima conhecimento, contexto e execução conforme a tarefa muda durante o dia.</p>
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
            <span className="produto-qualidade__nota nota--dois">Revisão editorial</span>
            <span className="produto-qualidade__nota nota--tres">Contexto clínico</span>
          </div>
          <div className="produto-qualidade__texto">
            <p className="produto-selo"><span /> Ciência e segurança</p>
            <h2>Inteligência clínica precisa mostrar de onde veio — e onde termina.</h2>
            <p>
              O CorVIA organiza evidências e recomendações para consulta profissional,
              preserva fontes e status de revisão e mantém ações consequenciais sob controle do médico.
            </p>
            <ul>
              <li><Icone nome="check" /><span><strong>Referências rastreáveis</strong> no conteúdo científico.</span></li>
              <li><Icone nome="check" /><span><strong>Dados privados separados</strong> de conhecimento público e relações clínicas.</span></li>
              <li><Icone nome="check" /><span><strong>Revisão médica preservada</strong> antes de prescrever, assinar ou enviar.</span></li>
            </ul>
          </div>
        </section>

        <section className="produto-cta" id="acesso">
          <div>
            <p className="produto-selo produto-selo--claro"><span /> Comece pelo que precisa resolver</p>
            <h2>Experimente uma nova maneira de trabalhar em medicina.</h2>
            <p>Solicite acesso profissional e conheça o Clinical OS construído para o médico.</p>
          </div>
          <div>
            <Link to="/solicitar-acesso" className="produto-botao produto-botao--claro">Solicitar acesso <Icone nome="seta" /></Link>
            <Link to="/entrar" className="produto-cta__entrar">Já tenho conta</Link>
          </div>
        </section>
      </main>

      <footer className="produto-rodape">
        <img src="/corvia-logo-compacta.png" alt="CorVIA" />
        <p>CorVIA — Clinical OS do médico. Apoio ao trabalho profissional; não substitui julgamento clínico nem responsabilidade médica.</p>
        <div><Link to="/privacidade">Privacidade</Link><Link to="/termos">Termos</Link><Link to="/entrar">Acesso profissional</Link></div>
      </footer>
    </div>
  );
}
