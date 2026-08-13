import { useEffect, useMemo, useRef, useState } from "react";
import { Link, useSearchParams } from "react-router-dom";
import { ApiError, api } from "../lib/api";
import { Carregando, Erro, Vazio } from "../components/Estado";

type CatalogItem = {
  tipo: string;
  slug: string;
  titulo: string;
  tema: string | null;
  detalhe: string | null;
  rotulo_tipo: string;
};
type CatalogResponse = { total: number; itens: CatalogItem[]; tipos: string[] };
type MailStatus = { disponivel: boolean; motivo: string | null; email_address: string | null };
type EnvioResponse = {
  enviado: boolean;
  remetente: string;
  para: string;
  assunto: string;
  arquivo: string;
  message_id: string | null;
};

const ROTULOS: Record<string, string> = {
  documento: "Biblioteca",
  fluxograma: "Fluxograma",
  evidencia: "Evidência",
  estudo: "Estudo",
  medicamento: "Medicamento",
  exame: "Exame",
  guideline: "Guideline",
  doenca: "Condição clínica",
  caso_clinico: "Caso clínico",
  trilha: "Trilha de estudo",
  checklist: "Checklist",
  material_paciente: "Material para paciente",
  emergencia: "Emergência",
  galeria: "Galeria",
  calculadora: "Calculadora",
  timeline: "Timeline científica",
};

function chave(item: Pick<CatalogItem, "tipo" | "slug">) {
  return `${item.tipo}:${item.slug}`;
}

function download(blob: Blob, filename = "conteudo-corvia.pdf") {
  const url = URL.createObjectURL(blob);
  const a = document.createElement("a");
  a.href = url;
  a.download = filename;
  a.click();
  URL.revokeObjectURL(url);
}

export default function ExportarConteudo() {
  const [params] = useSearchParams();
  const [busca, setBusca] = useState("");
  const [tipo, setTipo] = useState("");
  const [catalogo, setCatalogo] = useState<CatalogResponse | null>(null);
  const [carregando, setCarregando] = useState(true);
  const [erro, setErro] = useState("");
  const [selecionados, setSelecionados] = useState<CatalogItem[]>([]);
  const [titulo, setTitulo] = useState("");
  const [incluirDados, setIncluirDados] = useState(false);
  const [gerando, setGerando] = useState(false);
  const [mail, setMail] = useState<MailStatus | null>(null);
  const [para, setPara] = useState("");
  const [cc, setCc] = useState("");
  const [cco, setCco] = useState("");
  const [assunto, setAssunto] = useState("");
  const [mensagem, setMensagem] = useState("Segue em anexo o conteúdo exportado do CorVIA.");
  const [enviando, setEnviando] = useState(false);
  const [envio, setEnvio] = useState<EnvioResponse | null>(null);
  const prefillFeito = useRef(false);

  useEffect(() => {
    api.get<MailStatus>("/exportar/corvia-mail").then(setMail).catch(() => setMail({
      disponivel: false,
      motivo: "Não foi possível confirmar o CorVIA Mail agora.",
      email_address: null,
    }));
  }, []);

  useEffect(() => {
    const timer = window.setTimeout(() => {
      setCarregando(true);
      setErro("");
      const query = new URLSearchParams();
      if (busca.trim()) query.set("q", busca.trim());
      if (tipo) query.set("tipo", tipo);
      query.set("limite", "120");
      api.get<CatalogResponse>(`/exportar/catalogo?${query.toString()}`)
        .then(setCatalogo)
        .catch((e) => setErro(e instanceof ApiError ? e.message : "Não foi possível carregar os conteúdos exportáveis."))
        .finally(() => setCarregando(false));
    }, 220);
    return () => window.clearTimeout(timer);
  }, [busca, tipo]);

  useEffect(() => {
    if (prefillFeito.current) return;
    const tipoInicial = params.get("tipo") || "";
    const slugInicial = params.get("slug") || "";
    if (!tipoInicial || !slugInicial) return;
    prefillFeito.current = true;
    api.get<CatalogResponse>(`/exportar/catalogo?tipo=${encodeURIComponent(tipoInicial)}&slug=${encodeURIComponent(slugInicial)}&limite=1`)
      .then((r) => {
        if (r.itens[0]) setSelecionados([r.itens[0]]);
      })
      .catch(() => undefined);
  }, [params]);

  const chavesSelecionadas = useMemo(() => new Set(selecionados.map(chave)), [selecionados]);
  const payload = useMemo(() => ({
    itens: selecionados.map((item) => ({ tipo: item.tipo, slug: item.slug })),
    incluir_dados_assinante: incluirDados,
    titulo: titulo.trim() || null,
  }), [selecionados, incluirDados, titulo]);

  function adicionar(item: CatalogItem) {
    setSelecionados((atuais) => chavesSelecionadas.has(chave(item)) ? atuais : [...atuais, item]);
    setEnvio(null);
  }

  function remover(index: number) {
    setSelecionados((atuais) => atuais.filter((_, i) => i !== index));
    setEnvio(null);
  }

  function mover(index: number, delta: number) {
    setSelecionados((atuais) => {
      const destino = index + delta;
      if (destino < 0 || destino >= atuais.length) return atuais;
      const copia = [...atuais];
      [copia[index], copia[destino]] = [copia[destino], copia[index]];
      return copia;
    });
  }

  async function baixar() {
    if (!selecionados.length) return;
    setGerando(true);
    setErro("");
    try {
      const blob = await api.blobPost("/exportar/conteudo", payload);
      download(blob, titulo.trim() ? `${titulo.trim().replace(/[^\p{L}\p{N}]+/gu, "-").toLowerCase()}.pdf` : "conteudo-corvia.pdf");
    } catch (e) {
      setErro(e instanceof ApiError ? e.message : "Não foi possível gerar o PDF.");
    } finally {
      setGerando(false);
    }
  }

  async function enviarEmail() {
    if (!selecionados.length || !mail?.disponivel || !para.trim()) return;
    setEnviando(true);
    setErro("");
    setEnvio(null);
    try {
      const resposta = await api.post<EnvioResponse>("/exportar/conteudo/enviar-email", {
        ...payload,
        para: para.trim(),
        cc: cc.trim() || null,
        cco: cco.trim() || null,
        assunto: assunto.trim() || null,
        mensagem: mensagem.trim() || null,
      });
      setEnvio(resposta);
    } catch (e) {
      setErro(e instanceof ApiError ? e.message : "Não foi possível enviar o PDF pelo CorVIA Mail.");
    } finally {
      setEnviando(false);
    }
  }

  return (
    <div style={{ maxWidth: 1080, minWidth: 0 }}>
      <p className="eyebrow">Produção clínica e científica</p>
      <h1>Exportar conteúdo</h1>
      <p className="subtitulo" style={{ maxWidth: "76ch" }}>
        Monte um único PDF com qualquer combinação de conteúdos publicados do CorVIA. A ordem abaixo é a ordem do arquivo.
        Você pode gerar só com a marca CorVIA ou acrescentar sua identificação profissional.
      </p>

      <section className="cartao" style={{ marginTop: "1rem", minWidth: 0 }}>
        <p className="eyebrow">1 · Localizar conteúdo</p>
        <div style={{ display: "grid", gridTemplateColumns: "repeat(auto-fit, minmax(220px, 1fr))", gap: 10 }}>
          <label style={{ minWidth: 0 }}>
            <strong>Buscar</strong>
            <input value={busca} onChange={(e) => setBusca(e.target.value)} placeholder="Ex.: insuficiência cardíaca, sacubitril, PARADIGM-HF…" />
          </label>
          <label style={{ minWidth: 0 }}>
            <strong>Tipo</strong>
            <select value={tipo} onChange={(e) => setTipo(e.target.value)}>
              <option value="">Todos os tipos</option>
              {(catalogo?.tipos || Object.keys(ROTULOS)).map((id) => <option key={id} value={id}>{ROTULOS[id] || id}</option>)}
            </select>
          </label>
        </div>

        {erro && <div style={{ marginTop: 10 }}><Erro mensagem={erro} /></div>}
        {carregando ? <div style={{ marginTop: 14 }}><Carregando texto="Buscando conteúdo…" /></div> : !catalogo?.itens.length ? (
          <div style={{ marginTop: 14 }}><Vazio titulo="Nenhum conteúdo encontrado" acao="Altere o termo ou o tipo de conteúdo." /></div>
        ) : (
          <div style={{ display: "grid", gap: 8, marginTop: 14, maxHeight: 430, overflowY: "auto", paddingRight: 3, minWidth: 0 }}>
            {catalogo.itens.map((item) => {
              const selecionado = chavesSelecionadas.has(chave(item));
              return (
                <article className="cartao" key={chave(item)} style={{ padding: "0.8rem", display: "flex", flexWrap: "wrap", gap: 12, alignItems: "center", minWidth: 0 }}>
                  <div style={{ minWidth: 0, flex: "1 1 260px", overflowWrap: "anywhere" }}>
                    <p className="eyebrow" style={{ marginBottom: 3 }}>{item.rotulo_tipo}{item.tema ? ` · ${item.tema}` : ""}</p>
                    <strong style={{ display: "block" }}>{item.titulo}</strong>
                    {item.detalhe && <span className="dado" style={{ display: "block", marginTop: 3 }}>{item.detalhe}</span>}
                  </div>
                  <button className="botao botao--secundario" type="button" onClick={() => adicionar(item)} disabled={selecionado} style={{ flex: "0 0 auto" }}>
                    {selecionado ? "Adicionado" : "Adicionar"}
                  </button>
                </article>
              );
            })}
          </div>
        )}
      </section>

      <section className="cartao" style={{ marginTop: "1rem", minWidth: 0 }}>
        <p className="eyebrow">2 · Montar o PDF</p>
        {!selecionados.length ? (
          <p className="dado">Adicione um ou mais conteúdos. O PDF pode misturar medicamento, guideline, evidência, estudo, exame, checklist, timeline e outras áreas.</p>
        ) : (
          <ol style={{ listStyle: "none", padding: 0, margin: "0.7rem 0", display: "grid", gap: 7, minWidth: 0 }}>
            {selecionados.map((item, index) => (
              <li className="cartao" key={chave(item)} style={{ padding: "0.7rem", display: "flex", flexWrap: "wrap", alignItems: "center", gap: 9, minWidth: 0 }}>
                <strong style={{ minWidth: 28 }}>{index + 1}.</strong>
                <div style={{ minWidth: 0, flex: "1 1 260px", overflowWrap: "anywhere" }}><span className="dado">{item.rotulo_tipo}</span><strong style={{ display: "block" }}>{item.titulo}</strong></div>
                <div style={{ display: "flex", flexWrap: "wrap", gap: 7 }}>
                  <button type="button" className="botao botao--secundario" onClick={() => mover(index, -1)} disabled={index === 0} aria-label="Mover para cima">↑</button>
                  <button type="button" className="botao botao--secundario" onClick={() => mover(index, 1)} disabled={index === selecionados.length - 1} aria-label="Mover para baixo">↓</button>
                  <button type="button" className="botao botao--secundario" onClick={() => remover(index)}>Remover</button>
                </div>
              </li>
            ))}
          </ol>
        )}

        <label style={{ display: "block", marginTop: 10, minWidth: 0 }}>
          <strong>Título do PDF (opcional)</strong>
          <input value={titulo} onChange={(e) => setTitulo(e.target.value.slice(0, 180))} placeholder={selecionados.length > 1 ? "Ex.: Atualização em insuficiência cardíaca" : "Usar título do conteúdo"} />
        </label>
        <label style={{ display: "flex", gap: 9, alignItems: "flex-start", marginTop: 12, fontWeight: 400 }}>
          <input type="checkbox" checked={incluirDados} onChange={(e) => setIncluirDados(e.target.checked)} />
          <span><strong>Incluir meus dados profissionais</strong><br /><span className="dado">Nome, conselho/RQE, especialidade e identificação profissional configurada na sua conta.</span></span>
        </label>
        <button className="botao botao--acao" type="button" onClick={baixar} disabled={!selecionados.length || gerando} style={{ marginTop: 14 }}>
          {gerando ? "Gerando PDF…" : "Gerar e baixar PDF"}
        </button>
      </section>

      <section className="cartao" style={{ marginTop: "1rem", minWidth: 0 }}>
        <p className="eyebrow">3 · Enviar diretamente por e-mail</p>
        {!mail ? <Carregando texto="Verificando CorVIA Mail…" /> : !mail.disponivel ? (
          <div>
            <p>{mail.motivo || "O envio direto não está disponível nesta conta."}</p>
            <Link className="botao botao--secundario" to="/corvia-mail">Ver CorVIA Mail</Link>
          </div>
        ) : (
          <>
            <p className="dado">O PDF será regenerado e enviado como anexo pela sua caixa <strong>{mail.email_address}</strong>, sem exigir download prévio. Se sua assinatura profissional de e-mail estiver ativa, ela será incluída normalmente.</p>
            <div style={{ display: "grid", gridTemplateColumns: "repeat(auto-fit, minmax(220px, 1fr))", gap: 10, marginTop: 10, minWidth: 0 }}>
              <label style={{ gridColumn: "1 / -1", minWidth: 0 }}><strong>Para</strong><input type="email" value={para} onChange={(e) => setPara(e.target.value)} placeholder="destinatario@exemplo.com" /></label>
              <label style={{ minWidth: 0 }}><strong>CC (opcional)</strong><input type="email" value={cc} onChange={(e) => setCc(e.target.value)} /></label>
              <label style={{ minWidth: 0 }}><strong>CCO (opcional)</strong><input type="email" value={cco} onChange={(e) => setCco(e.target.value)} /></label>
              <label style={{ gridColumn: "1 / -1", minWidth: 0 }}><strong>Assunto (opcional)</strong><input value={assunto} onChange={(e) => setAssunto(e.target.value.slice(0, 240))} placeholder="O CorVIA sugere o título do PDF" /></label>
              <label style={{ gridColumn: "1 / -1", minWidth: 0 }}><strong>Mensagem</strong><textarea rows={4} value={mensagem} onChange={(e) => setMensagem(e.target.value.slice(0, 5000))} /></label>
            </div>
            <button className="botao botao--acao" type="button" onClick={enviarEmail} disabled={!selecionados.length || !para.trim() || enviando} style={{ marginTop: 14 }}>
              {enviando ? "Gerando e enviando…" : "Gerar PDF e enviar pelo CorVIA Mail"}
            </button>
            {envio?.enviado && (
              <div className="cartao" style={{ marginTop: 12, overflowWrap: "anywhere" }}>
                <strong>Enviado com sucesso.</strong>
                <p className="dado" style={{ marginBottom: 0 }}>De {envio.remetente} para {envio.para} · {envio.arquivo}</p>
              </div>
            )}
          </>
        )}
      </section>

      <p className="dado" style={{ marginTop: "1rem" }}>
        A exportação não cria conteúdo novo: o servidor lê novamente cada item publicado no momento do clique. Se algum item for retirado de publicação, o CorVIA interrompe o arquivo inteiro em vez de gerar um PDF parcial sem avisar.
      </p>
    </div>
  );
}