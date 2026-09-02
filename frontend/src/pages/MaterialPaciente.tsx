import { useEffect, useMemo, useState } from "react";
import { Link } from "react-router-dom";
import { api, todasAsPaginas } from "../lib/api";
import { Carregando, Erro, Vazio } from "../components/Estado";
import OfertaEnvioEmailPaciente from "../components/OfertaEnvioEmailPaciente";
import { normalizarBusca } from "../lib/taxonomiaCardiologia";

/**
 * Tarefa 12 — material educativo para entregar ao paciente.
 *
 * A separação com o resto da biblioteca é proposital e não é só de navegação: o
 * conteúdo aqui é escrito em outro registro, para quem não é da área, e não
 * contém dose, receita nem conduta. Misturar os dois na mesma listagem faria o
 * médico abrir um esperando o outro.
 *
 * Envio por e-mail ao paciente (02/08/2026, material-paciente-por-email-spec.md):
 * só o link vai por e-mail, nunca o PDF anexado. O botão exige CorvIA Mail
 * ativo — sem ele, fica desabilitado com explicação, e "Baixar PDF" continua
 * livre para todo mundo entregar por outro canal.
 */

type Material = {
  slug: string;
  titulo: string;
  subtitulo: string | null;
  tema: string;
  resumo: string | null;
};

type ContaEmail = { ativa: boolean; status?: string };

export default function MaterialPaciente() {
  const [itens, setItens] = useState<Material[] | null>(null);
  const [erro, setErro] = useState("");
  const [baixando, setBaixando] = useState("");
  const [corviaMailAtivo, setCorviaMailAtivo] = useState<boolean | null>(null);
  const [busca, setBusca] = useState("");
  const [tema, setTema] = useState("");

  const [envioAberto, setEnvioAberto] = useState<string>("");
  const [nomePaciente, setNomePaciente] = useState("");
  const [emailPaciente, setEmailPaciente] = useState("");
  const [recado, setRecado] = useState("");
  const [consentimento, setConsentimento] = useState(false);
  const [enviando, setEnviando] = useState(false);
  const [erroEnvio, setErroEnvio] = useState("");
  const [resultado, setResultado] = useState<{ slug: string; expiraEm: string } | null>(null);

  useEffect(() => {
    todasAsPaginas<Material>("/material-paciente?limit=500")
      .then(setItens)
      .catch((e) => setErro(e?.message || "Não foi possível carregar."));
    api
      .get<ContaEmail>("/email/conta")
      .then((c) => setCorviaMailAtivo(c.ativa && c.status === "ativa"))
      .catch(() => setCorviaMailAtivo(false));
  }, []);

  const temas = useMemo(() => {
    if (!itens) return [];
    return [...new Set(itens.map((item) => item.tema))].sort((a, b) => a.localeCompare(b, "pt-BR"));
  }, [itens]);

  const grupos = useMemo(() => {
    if (!itens) return [];
    const termo = normalizarBusca(busca);
    const filtrados = itens.filter((item) => {
      if (tema && item.tema !== tema) return false;
      if (!termo) return true;
      return normalizarBusca([item.titulo, item.subtitulo ?? "", item.tema, item.resumo ?? ""].join(" ")).includes(termo);
    });
    return [...new Set(filtrados.map((item) => item.tema))]
      .sort((a, b) => a.localeCompare(b, "pt-BR"))
      .map((assunto) => ({ assunto, materiais: filtrados.filter((item) => item.tema === assunto) }));
  }, [itens, busca, tema]);

  async function baixar(m: Material) {
    setBaixando(m.slug);
    setErro("");
    try {
      const blob = await api.blob(`/material-paciente/${m.slug}/pdf`);
      const url = URL.createObjectURL(blob);
      const a = document.createElement("a");
      a.href = url;
      a.download = `${m.slug}-material-do-paciente.pdf`;
      a.click();
      URL.revokeObjectURL(url);
    } catch (e: any) {
      setErro(e?.message || "Não foi possível gerar o PDF.");
    } finally {
      setBaixando("");
    }
  }

  function abrirEnvio(slug: string) {
    setEnvioAberto(slug);
    setNomePaciente("");
    setEmailPaciente("");
    setRecado("");
    setConsentimento(false);
    setErroEnvio("");
    setResultado(null);
  }

  function fecharEnvio() {
    setEnvioAberto("");
  }

  async function enviarPorEmail(slug: string) {
    setErroEnvio("");
    if (!nomePaciente.trim() || !emailPaciente.trim()) {
      setErroEnvio("Preencha o nome e o e-mail do paciente.");
      return;
    }
    if (!consentimento) {
      setErroEnvio("Confirme que o paciente autorizou receber este material por e-mail.");
      return;
    }
    setEnviando(true);
    try {
      const resp = await api.post<{ enviado: boolean; expira_em: string }>(
        `/material-paciente/${slug}/enviar-email`,
        {
          nome_paciente: nomePaciente.trim(),
          email_paciente: emailPaciente.trim(),
          recado: recado.trim() || undefined,
          consentimento,
        }
      );
      setResultado({ slug, expiraEm: resp.expira_em });
    } catch (e: any) {
      setErroEnvio(e?.message || "Não foi possível enviar o e-mail agora.");
    } finally {
      setEnviando(false);
    }
  }

  if (erro && !itens) return <Erro mensagem={erro} />;
  if (!itens) return <Carregando />;

  return (
    <div>
      <h1>Material para o paciente</h1>
      <p className="subtitulo">
        Explicações em linguagem acessível, para imprimir e entregar na consulta.
        O PDF sai com o seu nome e registro profissional — é a você que o paciente
        volta com dúvida.
      </p>

      <div className="cartao" style={{ marginBottom: "1.2rem" }}>
        <p className="eyebrow">O que este material é e o que não é</p>
        <p style={{ fontSize: "0.88rem", margin: "0.4rem 0 0" }}>
          É explicação da condição, escrita para leigo. <strong>Não contém dose,
          receita nem conduta individualizada</strong>, por decisão de escopo: o que
          fazer com o diagnóstico é da consulta, não de um folheto. Cada material
          declara as diretrizes em que se apoia.
        </p>
      </div>

      <section className="filtros-conteudo" aria-label="Localizar material para o paciente">
        <label>
          <strong>Buscar por tema específico</strong>
          <input
            type="search"
            value={busca}
            onChange={(event) => setBusca(event.target.value)}
            placeholder="Ex.: insuficiência cardíaca, hipertensão, anticoagulação…"
          />
        </label>
        <label>
          <strong>Assunto</strong>
          <select value={tema} onChange={(event) => setTema(event.target.value)}>
            <option value="">Todos os assuntos</option>
            {temas.map((item) => <option value={item} key={item}>{item}</option>)}
          </select>
        </label>
      </section>

      {erro && <p className="erro">{erro}</p>}

      {itens.length === 0 ? (
        <p>Nenhum material publicado ainda.</p>
      ) : grupos.length === 0 ? (
        <Vazio titulo="Nenhum material encontrado" acao="Tente outro termo ou selecione todos os assuntos." />
      ) : (
        <div className="colecoes-conteudo">
          {grupos.map((grupo) => <section className="colecao-conteudo" key={grupo.assunto}>
            <header><div><p className="eyebrow">Assunto</p><h2>{grupo.assunto}</h2></div><span>{grupo.materiais.length} {grupo.materiais.length === 1 ? "material" : "materiais"}</span></header>
            <div className="painel__funcoes">
          {grupo.materiais.map((m) => (
            <div key={m.slug} className="cartao painel__funcao">
              <p className="eyebrow">{m.tema}</p>
              <strong>{m.titulo}</strong>
              {m.subtitulo && <span>{m.subtitulo}</span>}
              <div style={{ display: "flex", gap: "0.5rem", flexWrap: "wrap", marginTop: "0.7rem" }}>
                <Link className="botao" to={`/material-paciente/${m.slug}`}>
                  Ler e ver conexões
                </Link>
                <button
                  className="botao botao--acao"
                  onClick={() => baixar(m)}
                  disabled={baixando === m.slug}
                >
                  {baixando === m.slug ? "Gerando…" : "Baixar PDF para entregar"}
                </button>
                <button
                  className="botao"
                  onClick={() => abrirEnvio(m.slug)}
                  disabled={corviaMailAtivo === false}
                  title={
                    corviaMailAtivo === false
                      ? "O envio em nome próprio faz parte do CorvIA Mail — ative sua caixa para usar esta opção."
                      : undefined
                  }
                >
                  Enviar por e-mail ao paciente
                </button>
              </div>

              <OfertaEnvioEmailPaciente
                endpointBase={`/material-paciente/${m.slug}`}
                habilitado
                variante="material"
              />

              {envioAberto === m.slug && (
                <div className="cartao" style={{ marginTop: "0.8rem", background: "var(--fundo-alt, #f7f9fa)" }}>
                  {resultado && resultado.slug === m.slug ? (
                    <div>
                      <p style={{ margin: 0 }}>
                        <strong>E-mail enviado.</strong> O link vale até{" "}
                        {new Date(resultado.expiraEm).toLocaleDateString("pt-BR")}.
                      </p>
                      <button className="botao" style={{ marginTop: "0.6rem" }} onClick={fecharEnvio}>
                        Fechar
                      </button>
                    </div>
                  ) : (
                    <div>
                      <label style={{ display: "block", marginBottom: "0.5rem" }}>
                        Nome do paciente
                        <input
                          type="text"
                          value={nomePaciente}
                          onChange={(e) => setNomePaciente(e.target.value)}
                          style={{ display: "block", width: "100%", marginTop: "0.25rem" }}
                        />
                      </label>
                      <label style={{ display: "block", marginBottom: "0.5rem" }}>
                        E-mail do paciente
                        <input
                          type="email"
                          value={emailPaciente}
                          onChange={(e) => setEmailPaciente(e.target.value)}
                          style={{ display: "block", width: "100%", marginTop: "0.25rem" }}
                        />
                      </label>
                      <label style={{ display: "block", marginBottom: "0.5rem" }}>
                        Recado curto (opcional)
                        <textarea
                          value={recado}
                          onChange={(e) => setRecado(e.target.value)}
                          maxLength={500}
                          rows={2}
                          style={{ display: "block", width: "100%", marginTop: "0.25rem" }}
                        />
                      </label>
                      <label style={{ display: "flex", alignItems: "flex-start", gap: "0.4rem", fontSize: "0.85rem" }}>
                        <input
                          type="checkbox"
                          checked={consentimento}
                          onChange={(e) => setConsentimento(e.target.checked)}
                          style={{ marginTop: "0.2rem" }}
                        />
                        Confirmo que o paciente autorizou receber este material por e-mail.
                      </label>
                      <p style={{ fontSize: "0.8rem", color: "var(--texto-suave, #666)", margin: "0.5rem 0" }}>
                        Só o link é enviado — o PDF não vai anexado.
                      </p>
                      {erroEnvio && <p className="erro">{erroEnvio}</p>}
                      <div style={{ display: "flex", gap: "0.5rem", marginTop: "0.5rem" }}>
                        <button
                          className="botao botao--acao"
                          onClick={() => enviarPorEmail(m.slug)}
                          disabled={enviando}
                        >
                          {enviando ? "Enviando…" : "Enviar"}
                        </button>
                        <button className="botao" onClick={fecharEnvio} disabled={enviando}>
                          Cancelar
                        </button>
                      </div>
                    </div>
                  )}
                </div>
              )}
            </div>
          ))}
            </div>
          </section>)}
        </div>
      )}
    </div>
  );
}
