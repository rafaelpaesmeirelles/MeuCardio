import { useEffect, useState } from "react";
import CampoSenha from "../components/CampoSenha";
import { api, ApiError, assetUrl, type Usuario } from "../lib/api";
import { useAuth } from "../lib/auth";
import { useNavigate } from "react-router-dom";

const CONSELHOS = ["CRM", "CRO", "CRBM", "COREN", "CRF", "CREFITO", "CRN", "CRP", "CREF", "CRESS", "Outro"];
const TITULOS = ["", "Sr.", "Sra.", "Dr.", "Dra.", "Prof.", "Profa.", "Prof. Dr.", "Profa. Dra.", "Me.", "Ma.", "Esp."];
const UFS = [
  "AC", "AL", "AP", "AM", "BA", "CE", "DF", "ES", "GO", "MA", "MT", "MS", "MG",
  "PA", "PB", "PR", "PE", "PI", "RJ", "RN", "RS", "RO", "RR", "SC", "SP", "SE", "TO",
];

type StatusAssinatura = {
  status: string;
  current_period_end: string | null;
  plano: string | null;
};

const PRECO_POR_PLANO: Record<string, string> = {
  basico: "R$ 49,90/mês — Assinatura Básica (Acesso ao Site).",
  completo: "R$ 59,90/mês — Assinatura Completa (Acesso ao Site + CorvIA Mail).",
};

const ROTULOS: Record<string, string> = {
  ativo: "Ativa",
  teste: "Período de teste",
  inativo: "Inativa",
  pendente: "Pendente",
  inadimplente: "Pagamento pendente",
  suspenso: "Suspensa por falta de pagamento",
  cancelado: "Cancelada",
  pausado: "Pausada",
};

// Mesmo conjunto de ACESSO_LIBERADO em backend/app/core/security.py.
const STATUS_COM_ACESSO = ["ativo", "teste", "inadimplente"];

type CamposEndereco = {
  street: string; number: string; complement: string; neighborhood: string;
  city: string; state: string; zip: string;
};

/** Um bloco de endereço completo (residencial ou profissional) — mesmos
 * sete campos nos dois, reaproveitado para não duplicar o layout. */
function BlocoEndereco({ prefixo, valores, onMudar }: {
  prefixo: string; valores: CamposEndereco; onMudar: (campo: keyof CamposEndereco, valor: string) => void;
}) {
  return (
    <>
      <div className="grade grade--3" style={{ marginTop: "0.6rem" }}>
        <div style={{ gridColumn: "span 2" }}>
          <label htmlFor={`${prefixo}-logradouro`}>Logradouro</label>
          <input id={`${prefixo}-logradouro`} value={valores.street}
                 onChange={(e) => onMudar("street", e.target.value)} />
        </div>
        <div>
          <label htmlFor={`${prefixo}-numero`}>Número</label>
          <input id={`${prefixo}-numero`} value={valores.number}
                 onChange={(e) => onMudar("number", e.target.value)} />
        </div>
      </div>
      <div className="grade grade--2" style={{ marginTop: "0.6rem" }}>
        <div>
          <label htmlFor={`${prefixo}-complemento`}>Complemento <span className="eyebrow">(opcional)</span></label>
          <input id={`${prefixo}-complemento`} value={valores.complement}
                 onChange={(e) => onMudar("complement", e.target.value)} />
        </div>
        <div>
          <label htmlFor={`${prefixo}-bairro`}>Bairro</label>
          <input id={`${prefixo}-bairro`} value={valores.neighborhood}
                 onChange={(e) => onMudar("neighborhood", e.target.value)} />
        </div>
      </div>
      <div className="grade grade--3" style={{ marginTop: "0.6rem" }}>
        <div>
          <label htmlFor={`${prefixo}-cidade`}>Município</label>
          <input id={`${prefixo}-cidade`} value={valores.city}
                 onChange={(e) => onMudar("city", e.target.value)} />
        </div>
        <div>
          <label htmlFor={`${prefixo}-uf`}>UF</label>
          <select id={`${prefixo}-uf`} value={valores.state} onChange={(e) => onMudar("state", e.target.value)}>
            <option value="">—</option>
            {UFS.map((uf) => <option key={uf} value={uf}>{uf}</option>)}
          </select>
        </div>
        <div>
          <label htmlFor={`${prefixo}-cep`}>CEP</label>
          <input id={`${prefixo}-cep`} value={valores.zip}
                 onChange={(e) => onMudar("zip", e.target.value)} />
        </div>
      </div>
    </>
  );
}

/** Rever o tour de boas-vindas (Trabalho 13, ampliação de 06/08/2026) —
 * pedido do Rafael: deixar disponível pra revisão a qualquer momento,
 * fora do fluxo obrigatório do primeiro acesso. `/tour` não exige
 * `onboarding_pendente` para abrir — só o gate do App.tsx é que FORÇA a
 * navegação pra lá quando pendente; visitar por conta própria sempre
 * funciona. */
function RevisarTour() {
  const navigate = useNavigate();
  return (
    <div className="cartao" style={{ display: "flex", gap: "1rem", alignItems: "center", justifyContent: "space-between" }}>
      <div>
        <h2 style={{ margin: "0 0 0.2rem" }}>Tour da plataforma</h2>
        <p style={{ margin: 0, fontSize: "0.82rem", color: "var(--texto-secundario)" }}>
          Reveja rapidamente todas as funções da Corvia, quando quiser.
        </p>
      </div>
      <button type="button" className="botao botao--secundario" onClick={() => navigate("/tour")}>
        Rever o tour
      </button>
    </div>
  );
}

/** Trabalho 16 (07/08/2026): a gestão completa (conectar Google/Microsoft/
 * Apple/Yahoo, escolher o que cada conta sincroniza, desconectar) mora na
 * própria página /sincronizacao — item dedicado no menu lateral, seção
 * Gestão. Aqui fica só o resumo e o atalho, para não duplicar a tela
 * inteira dentro de Minha Conta. */
function ResumoSincronizacao() {
  const navigate = useNavigate();
  const [total, setTotal] = useState<number | null>(null);

  useEffect(() => {
    api.get<Array<{ provider: string }>>("/agenda/integrations")
      .then((lista) => setTotal(lista.filter((i) =>
        ["google_calendar", "microsoft_365", "apple_icloud", "yahoo_mail"].includes(i.provider)
      ).length))
      .catch(() => setTotal(null));
  }, []);

  return (
    <div className="cartao" style={{ display: "flex", gap: "1rem", alignItems: "center", justifyContent: "space-between" }}>
      <div>
        <h2 style={{ margin: "0 0 0.2rem" }}>Sincronize suas contas</h2>
        <p style={{ margin: 0, fontSize: "0.82rem", color: "var(--texto-secundario)" }}>
          {total === null ? "Google, Microsoft, Apple e Yahoo — conecte quantas contas quiser." :
           total === 0 ? "Nenhuma conta conectada ainda." :
           `${total} conta${total > 1 ? "s" : ""} conectada${total > 1 ? "s" : ""}.`}
        </p>
      </div>
      <button type="button" className="botao botao--secundario" onClick={() => navigate("/sincronizacao")}>
        Gerenciar
      </button>
    </div>
  );
}

function DadosPessoais({ perfil, aoSalvar }: { perfil: Usuario; aoSalvar: (u: Usuario) => void }) {
  const [dados, setDados] = useState({
    full_name: perfil.full_name ?? "",
    profession: perfil.profession ?? "",
    council_name: perfil.council_name ?? "CRM",
    council_number: perfil.council_number ?? "",
    council_state: perfil.council_state ?? "",
    specialty: perfil.specialty ?? "",
    rqe: perfil.rqe ?? "",
    professional_title: perfil.professional_title ?? "",
    workplace_name: perfil.workplace_name ?? "",
    workplace_department: perfil.workplace_department ?? "",
    workplace_role: perfil.workplace_role ?? "",
    workplace_notes: perfil.workplace_notes ?? "",
    include_workplace_on_documents: perfil.include_workplace_on_documents ?? false,
  });
  const [residencial, setResidencial] = useState<CamposEndereco>({
    street: perfil.home_street ?? "", number: perfil.home_number ?? "",
    complement: perfil.home_complement ?? "", neighborhood: perfil.home_neighborhood ?? "",
    city: perfil.home_city ?? "", state: perfil.home_state ?? "", zip: perfil.home_zip ?? "",
  });
  const [profissional, setProfissional] = useState<CamposEndereco>({
    street: perfil.practice_street ?? "", number: perfil.practice_number ?? "",
    complement: perfil.practice_complement ?? "", neighborhood: perfil.practice_neighborhood ?? "",
    city: perfil.practice_city ?? "", state: perfil.practice_state ?? "", zip: perfil.practice_zip ?? "",
  });
  const [practicePhone, setPracticePhone] = useState(perfil.practice_phone ?? "");
  const [salvando, setSalvando] = useState(false);
  const [erro, setErro] = useState("");
  const [ok, setOk] = useState(false);

  function set<K extends keyof typeof dados>(campo: K, valor: (typeof dados)[K]) {
    setDados((d) => ({ ...d, [campo]: valor }));
    setOk(false);
  }

  const valido = dados.full_name.trim().split(/\s+/).length >= 2;

  async function salvar() {
    setErro("");
    setSalvando(true);
    try {
      const atualizado = await api.patch<Usuario>("/auth/me", {
        ...dados,
        profession: dados.profession.trim() || null,
        council_number: dados.council_number.trim() || null,
        council_state: dados.council_state || null,
        specialty: dados.specialty.trim() || null,
        rqe: dados.rqe.trim() || null,
        home_street: residencial.street.trim() || null,
        home_number: residencial.number.trim() || null,
        home_complement: residencial.complement.trim() || null,
        home_neighborhood: residencial.neighborhood.trim() || null,
        home_city: residencial.city.trim() || null,
        home_state: residencial.state || null,
        home_zip: residencial.zip.trim() || null,
        practice_street: profissional.street.trim() || null,
        practice_number: profissional.number.trim() || null,
        practice_complement: profissional.complement.trim() || null,
        practice_neighborhood: profissional.neighborhood.trim() || null,
        practice_city: profissional.city.trim() || null,
        practice_state: profissional.state || null,
        practice_zip: profissional.zip.trim() || null,
        practice_phone: practicePhone.trim() || null,
      });
      aoSalvar(atualizado);
      setOk(true);
    } catch (e) {
      setErro(e instanceof ApiError ? e.message : "Não foi possível salvar seus dados.");
    } finally {
      setSalvando(false);
    }
  }

  return (
    <div className="cartao">
      <h2 style={{ marginTop: 0 }}>Dados pessoais</h2>

      <label htmlFor="conta-nome">Nome completo</label>
      <input id="conta-nome" value={dados.full_name} onChange={(e) => set("full_name", e.target.value)} />
      {!valido && (
        // Sem esta mensagem o botão fica desabilitado sem explicação, e quem
        // tem só um nome cadastrado (contas criadas pelo admin, por exemplo)
        // não descobre por que não consegue salvar nada da página.
        <p style={{ color: "var(--alerta)", fontSize: "0.82rem", margin: "0.3rem 0 0" }}>
          Informe nome e sobrenome — é o que o cadastro exige para salvar.
        </p>
      )}

      <label htmlFor="conta-tratamento" style={{ marginTop: "0.8rem" }}>Como deseja ser chamado(a)</label>
      <select id="conta-tratamento" value={dados.professional_title} onChange={(e) => set("professional_title", e.target.value)}>
        {TITULOS.map((t) => <option key={t || "sem"} value={t}>{t || "Sem título"}</option>)}
      </select>

      <label htmlFor="conta-profissao" style={{ marginTop: "0.8rem" }}>Profissão</label>
      <input id="conta-profissao" value={dados.profession} onChange={(e) => set("profession", e.target.value)} />

      <div className="grade grade--3" style={{ marginTop: "0.8rem" }}>
        <div>
          <label htmlFor="conta-conselho">Conselho</label>
          <select id="conta-conselho" value={dados.council_name} onChange={(e) => set("council_name", e.target.value)}>
            {CONSELHOS.map((c) => <option key={c} value={c}>{c}</option>)}
          </select>
        </div>
        <div>
          <label htmlFor="conta-numero">Nº de registro</label>
          <input id="conta-numero" value={dados.council_number} onChange={(e) => set("council_number", e.target.value)} />
        </div>
        <div>
          <label htmlFor="conta-uf">Estado</label>
          <select id="conta-uf" value={dados.council_state} onChange={(e) => set("council_state", e.target.value)}>
            <option value="">—</option>
            {UFS.map((uf) => <option key={uf} value={uf}>{uf}</option>)}
          </select>
        </div>
      </div>

      <div className="grade grade--2" style={{ marginTop: "0.8rem" }}>
        <div>
          <label htmlFor="conta-especialidade">
            Especialidade <span className="eyebrow">(opcional)</span>
          </label>
          <input id="conta-especialidade" value={dados.specialty} onChange={(e) => set("specialty", e.target.value)} />
        </div>
        <div>
          <label htmlFor="conta-rqe">
            RQE <span className="eyebrow">(opcional)</span>
          </label>
          <input id="conta-rqe" value={dados.rqe} onChange={(e) => set("rqe", e.target.value)}
                 placeholder="Registro de qualificação de especialista" />
        </div>
      </div>

      <h3 style={{ marginTop: "1.4rem", marginBottom: 0 }}>Local de trabalho</h3>
      <div className="grade grade--2" style={{ marginTop: "0.6rem" }}>
        <div><label>Instituição, clínica ou consultório</label><input value={dados.workplace_name} onChange={(e) => set("workplace_name", e.target.value)} /></div>
        <div><label>Setor/unidade</label><input value={dados.workplace_department} onChange={(e) => set("workplace_department", e.target.value)} /></div>
        <div><label>Cargo/função</label><input value={dados.workplace_role} onChange={(e) => set("workplace_role", e.target.value)} /></div>
        <div><label>Outras informações</label><input value={dados.workplace_notes} onChange={(e) => set("workplace_notes", e.target.value)} /></div>
      </div>
      <label style={{ display: "flex", gap: 8, alignItems: "center", fontWeight: 400, marginTop: "0.6rem" }}>
        <input type="checkbox" style={{ width: "auto" }} checked={dados.include_workplace_on_documents}
               onChange={(e) => set("include_workplace_on_documents", e.target.checked)} />
        Incluir essas informações em receitas, laudos, atestados e demais documentos
      </label>

      <h3 style={{ marginTop: "1.4rem", marginBottom: 0 }}>Endereço residencial</h3>
      <p className="eyebrow" style={{ margin: "0.2rem 0 0" }}>
        Opcional — só aparece em receita/documento se você escolher exibi-lo na hora de emitir.
      </p>
      <BlocoEndereco prefixo="res" valores={residencial}
                     onMudar={(campo, valor) => { setResidencial((r) => ({ ...r, [campo]: valor })); setOk(false); }} />

      <h3 style={{ marginTop: "1.4rem", marginBottom: 0 }}>Endereço profissional (consultório)</h3>
      <p className="eyebrow" style={{ margin: "0.2rem 0 0" }}>
        Opcional — mesma lógica do residencial. O telefone abaixo é o único exigido por lei,
        para receita de anabolizantes (Lei nº 9.965/2000).
      </p>
      <BlocoEndereco prefixo="prof" valores={profissional}
                     onMudar={(campo, valor) => { setProfissional((p) => ({ ...p, [campo]: valor })); setOk(false); }} />
      <div style={{ marginTop: "0.6rem", maxWidth: "16rem" }}>
        <label htmlFor="conta-telefone-profissional">Telefone profissional</label>
        <input id="conta-telefone-profissional" value={practicePhone}
               onChange={(e) => { setPracticePhone(e.target.value); setOk(false); }} />
      </div>

      <p style={{ fontSize: "0.86rem", opacity: 0.8, margin: "1.2rem 0 0" }}>
        E-mail de acesso: <strong>{perfil.email}</strong>
        {perfil.cpf_mascarado && <> · CPF: <strong>{perfil.cpf_mascarado}</strong></>}
      </p>
      <p style={{ fontSize: "0.82rem", opacity: 0.7, marginTop: "0.3rem" }}>
        E-mail, CPF e data de nascimento são os dados conferidos na aprovação do cadastro —
        para alterá-los, fale com a administração.
      </p>

      {erro && <p role="alert" style={{ color: "var(--alerta)", fontSize: "0.86rem" }}>{erro}</p>}
      {ok && <p style={{ color: "var(--sucesso)", fontSize: "0.86rem" }}>Dados salvos.</p>}

      <button className="botao" style={{ marginTop: "0.8rem" }} onClick={salvar} disabled={!valido || salvando}>
        {salvando ? "Salvando…" : "Salvar dados"}
      </button>
    </div>
  );
}

function Foto({ perfil, aoTrocar }: { perfil: Usuario; aoTrocar: (u: Usuario) => void }) {
  const [enviando, setEnviando] = useState(false);
  const [erro, setErro] = useState("");
  const [imagemQuebrada, setImagemQuebrada] = useState(false);

  useEffect(() => setImagemQuebrada(false), [perfil.photo_url]);

  async function enviar(arquivo: File | undefined) {
    if (!arquivo) return;
    setErro("");
    setEnviando(true);
    try {
      aoTrocar(await api.upload<Usuario>("/auth/me/foto", "arquivo", arquivo));
    } catch (e) {
      setErro(e instanceof ApiError ? e.message : "Não foi possível enviar a foto.");
    } finally {
      setEnviando(false);
    }
  }

  async function remover() {
    setErro("");
    setEnviando(true);
    try {
      aoTrocar(await api.delete<Usuario>("/auth/me/foto"));
    } catch (e) {
      setErro(e instanceof ApiError ? e.message : "Não foi possível remover a foto.");
    } finally {
      setEnviando(false);
    }
  }

  const iniciais = perfil.full_name.split(/\s+/).slice(0, 2).map((p) => p[0]).join("").toUpperCase();

  return (
    <div className="cartao" style={{ display: "flex", gap: "1rem", alignItems: "center" }}>
      {perfil.photo_url && !imagemQuebrada ? (
        <img src={assetUrl(perfil.photo_url)} alt="Sua foto de perfil" className="conta__foto"
             onError={() => setImagemQuebrada(true)} />
      ) : (
        <div className="conta__foto conta__foto--vazia" aria-hidden="true">{iniciais}</div>
      )}

      <div style={{ flex: 1 }}>
        <h2 style={{ margin: "0 0 0.2rem" }}>Foto de perfil</h2>
        <p style={{ margin: 0, fontSize: "0.82rem", color: "var(--texto-secundario)" }}>
          JPEG, PNG ou WEBP, até 3 MB.
        </p>
        {erro && <p role="alert" style={{ color: "var(--alerta)", fontSize: "0.84rem" }}>{erro}</p>}

        <div style={{ display: "flex", gap: "0.5rem", marginTop: "0.6rem", flexWrap: "wrap" }}>
          <label className="botao botao--secundario" style={{ cursor: "pointer", marginBottom: 0 }}>
            {enviando ? "Enviando…" : perfil.photo_url ? "Trocar foto" : "Enviar foto"}
            <input type="file" accept="image/jpeg,image/png,image/webp" disabled={enviando}
                   style={{ display: "none" }}
                   onChange={(e) => { enviar(e.target.files?.[0]); e.target.value = ""; }} />
          </label>
          {perfil.photo_url && (
            <button className="botao botao--secundario" onClick={remover} disabled={enviando}>
              Remover
            </button>
          )}
        </div>
      </div>
    </div>
  );
}

/** Logo pessoal/do consultório (Tarefa 29) — aparece JUNTO da logo da
 * Corvia no cabeçalho de toda receita/documento que o médico emitir. */
function LogoDocumento({ perfil, aoTrocar }: { perfil: Usuario; aoTrocar: (u: Usuario) => void }) {
  const [enviando, setEnviando] = useState(false);
  const [erro, setErro] = useState("");
  const [imagemQuebrada, setImagemQuebrada] = useState(false);

  useEffect(() => setImagemQuebrada(false), [perfil.document_logo_url]);

  async function enviar(arquivo: File | undefined) {
    if (!arquivo) return;
    setErro("");
    setEnviando(true);
    try {
      aoTrocar(await api.upload<Usuario>("/auth/me/logo", "arquivo", arquivo));
    } catch (e) {
      setErro(e instanceof ApiError ? e.message : "Não foi possível enviar a logo.");
    } finally {
      setEnviando(false);
    }
  }

  async function remover() {
    setErro("");
    setEnviando(true);
    try {
      aoTrocar(await api.delete<Usuario>("/auth/me/logo"));
    } catch (e) {
      setErro(e instanceof ApiError ? e.message : "Não foi possível remover a logo.");
    } finally {
      setEnviando(false);
    }
  }

  return (
    <div className="cartao" style={{ display: "flex", gap: "1rem", alignItems: "center" }}>
      {perfil.document_logo_url && !imagemQuebrada ? (
        <span className={`logo-profissional-preview ${perfil.document_logo_dark_background ? "logo-profissional-preview--escuro" : ""}`}>
          <img src={assetUrl(perfil.document_logo_url)} alt="Sua logo" style={{ maxWidth: 96, maxHeight: 64 }}
               onError={() => setImagemQuebrada(true)} />
        </span>
      ) : (
        <div style={{ width: 96, height: 64, display: "flex", alignItems: "center", justifyContent: "center",
                      border: "1px dashed var(--linha)", borderRadius: 6, fontSize: "0.75rem", color: "var(--texto-secundario)" }}>
          Sem logo
        </div>
      )}

      <div style={{ flex: 1 }}>
        <h2 style={{ margin: "0 0 0.2rem" }}>Logo pessoal ou do consultório</h2>
        <p style={{ margin: 0, fontSize: "0.82rem", color: "var(--texto-secundario)" }}>
          Opcional — aparece junto da logo da Corvia nas receitas e documentos que você emitir.
          JPEG, PNG ou WEBP, até 3 MB. O sistema detecta logos claras ou transparentes e aplica automaticamente um fundo de contraste nos documentos.
        </p>
        {erro && <p role="alert" style={{ color: "var(--alerta)", fontSize: "0.84rem" }}>{erro}</p>}

        <div style={{ display: "flex", gap: "0.5rem", marginTop: "0.6rem", flexWrap: "wrap" }}>
          <label className="botao botao--secundario" style={{ cursor: "pointer", marginBottom: 0 }}>
            {enviando ? "Enviando…" : perfil.document_logo_url ? "Trocar logo" : "Enviar logo"}
            <input type="file" accept="image/jpeg,image/png,image/webp" disabled={enviando}
                   style={{ display: "none" }}
                   onChange={(e) => { enviar(e.target.files?.[0]); e.target.value = ""; }} />
          </label>
          {perfil.document_logo_url && (
            <button className="botao botao--secundario" onClick={remover} disabled={enviando}>
              Remover
            </button>
          )}
        </div>
      </div>
    </div>
  );
}

// Catálogo de métodos de assinatura de documento (Tarefa 4) — GET
// /assinatura/provedores. Mesmo tipo usado em Receituario.tsx/Templates.tsx.
type Provedor = { codigo: string; nome: string; nivel: string; familia: string; disponivel: boolean; motivo: string | null };

/** Preferência de MÉTODO DE ASSINATURA DIGITAL do documento clínico — não
 * confundir com o componente `Assinatura` abaixo, que é a assinatura
 * COMERCIAL (billing) da Corvia. Só define o valor inicial sugerido no
 * `<select>` da tela de emissão (Tarefa 4); o médico sempre pode trocar a
 * cada receita/documento. */
function PreferenciaAssinaturaDigital({ perfil, aoSalvar }: { perfil: Usuario; aoSalvar: (u: Usuario) => void }) {
  const [provedores, setProvedores] = useState<Provedor[] | null>(null);
  const [metodo, setMetodo] = useState(perfil.assinatura_metodo_preferido ?? "MANUAL");
  const [salvando, setSalvando] = useState(false);
  const [erro, setErro] = useState("");
  const [salvo, setSalvo] = useState(false);

  useEffect(() => { api.get<Provedor[]>("/assinatura/provedores").then(setProvedores).catch(() => {}); }, []);

  async function salvar() {
    setSalvando(true);
    setErro("");
    setSalvo(false);
    try {
      aoSalvar(await api.patch<Usuario>("/auth/me/assinatura", { metodo }));
      setSalvo(true);
    } catch (e) {
      setErro(e instanceof ApiError ? e.message : "Não foi possível salvar a preferência.");
    } finally {
      setSalvando(false);
    }
  }

  return (
    <div className="cartao">
      <h2 style={{ margin: "0 0 0.2rem" }}>Método de assinatura padrão</h2>
      <p style={{ margin: 0, fontSize: "0.82rem", color: "var(--texto-secundario)" }}>
        Sugestão inicial ao emitir receita ou documento — você ainda escolhe (ou troca) a cada um.
      </p>

      <select style={{ marginTop: "0.6rem" }} value={metodo} onChange={(e) => setMetodo(e.target.value)}>
        {(provedores ?? []).map((p) => (
          <option key={p.codigo} value={p.codigo} disabled={!p.disponivel}>
            {p.nome}{!p.disponivel ? " — indisponível" : ""}
          </option>
        ))}
      </select>

      {erro && <p role="alert" style={{ color: "var(--alerta)", fontSize: "0.84rem" }}>{erro}</p>}
      {salvo && !erro && <p style={{ color: "var(--sucesso)", fontSize: "0.84rem" }}>Preferência salva.</p>}

      <div style={{ marginTop: "0.6rem" }}>
        <button className="botao botao--secundario" onClick={salvar} disabled={salvando}>
          {salvando ? "Salvando…" : "Salvar preferência"}
        </button>
      </div>
    </div>
  );
}

type Certificadora = { nome: string; site: string };
type StatusCertificadoA1 = {
  conectado: boolean;
  titular_cn?: string;
  numero_serie?: string;
  valido_ate?: string;
  certificadora?: string | null;
};

/** Certificado A1 (Trabalho 7) — o único provedor QUALIFICADA (ICP-Brasil)
 * que não depende de nenhuma conta comercial: o médico já tem (ou compra
 * de qualquer Autoridade Certificadora credenciada) um arquivo .pfx/.p12
 * com a própria chave privada. */
function CertificadoA1() {
  const [status, setStatus] = useState<StatusCertificadoA1 | null>(null);
  const [certificadoras, setCertificadoras] = useState<Certificadora[]>([]);
  const [arquivo, setArquivo] = useState<File | null>(null);
  const [senha, setSenha] = useState("");
  const [certificadoraEscolhida, setCertificadoraEscolhida] = useState("");
  const [enviando, setEnviando] = useState(false);
  const [removendo, setRemovendo] = useState(false);
  const [erro, setErro] = useState("");

  const carregarStatus = () => api.get<StatusCertificadoA1>("/assinatura/certificado-a1").then(setStatus).catch(() => {});

  useEffect(() => {
    carregarStatus();
    api.get<Certificadora[]>("/assinatura/certificadoras").then(setCertificadoras).catch(() => {});
  }, []);

  async function enviar() {
    if (!arquivo || !senha) return;
    setEnviando(true);
    setErro("");
    try {
      await api.upload<StatusCertificadoA1>("/assinatura/certificado-a1", "arquivo", arquivo, {
        senha, ...(certificadoraEscolhida ? { certificadora: certificadoraEscolhida } : {}),
      });
      setArquivo(null);
      setSenha("");
      await carregarStatus();
    } catch (e) {
      setErro(e instanceof ApiError ? e.message : "Não foi possível conectar o certificado.");
    } finally {
      setEnviando(false);
    }
  }

  async function remover() {
    if (!window.confirm("Remover o certificado A1 conectado? Você precisará enviar o arquivo de novo para assinar com ele.")) return;
    setRemovendo(true);
    try {
      await api.delete("/assinatura/certificado-a1");
      await carregarStatus();
    } catch (e) {
      setErro(e instanceof ApiError ? e.message : "Não foi possível remover o certificado.");
    } finally {
      setRemovendo(false);
    }
  }

  return (
    <div className="cartao">
      <h2 style={{ margin: "0 0 0.2rem" }}>Assinatura digital — certificado A1</h2>
      <p style={{ margin: 0, fontSize: "0.82rem", color: "var(--texto-secundario)" }}>
        Assinatura qualificada (ICP-Brasil), a partir do seu próprio certificado em arquivo. O Corvia guarda o
        arquivo cifrado e nunca o compartilha — ele só é usado para assinar seus documentos.
      </p>

      {status?.conectado ? (
        <div style={{ marginTop: "0.7rem" }}>
          <p style={{ margin: 0, fontSize: "0.84rem" }}><strong>Titular:</strong> {status.titular_cn}</p>
          <p style={{ margin: "0.2rem 0 0", fontSize: "0.84rem" }}>
            <strong>Válido até:</strong> {status.valido_ate ? new Date(status.valido_ate).toLocaleDateString("pt-BR") : "—"}
          </p>
          {status.certificadora && <p style={{ margin: "0.2rem 0 0", fontSize: "0.84rem" }}><strong>Certificadora:</strong> {status.certificadora}</p>}
          <button className="botao botao--secundario" style={{ marginTop: "0.6rem" }} onClick={remover} disabled={removendo}>
            {removendo ? "Removendo…" : "Remover certificado"}
          </button>
        </div>
      ) : (
        <div style={{ marginTop: "0.7rem" }}>
          <label style={{ display: "block", fontSize: "0.82rem", marginBottom: "0.3rem" }}>
            Arquivo do certificado (.pfx ou .p12)
            <input type="file" accept=".pfx,.p12" onChange={(e) => setArquivo(e.target.files?.[0] ?? null)} style={{ display: "block", marginTop: "0.25rem" }} />
          </label>
          <label style={{ display: "block", fontSize: "0.82rem", marginTop: "0.5rem" }}>
            Senha do certificado
            <CampoSenha value={senha} onChange={(e) => setSenha(e.target.value)} style={{ display: "block", marginTop: "0.25rem", width: "100%" }} />
          </label>
          <label style={{ display: "block", fontSize: "0.82rem", marginTop: "0.5rem" }}>
            Certificadora (opcional, só pra referência)
            <select value={certificadoraEscolhida} onChange={(e) => setCertificadoraEscolhida(e.target.value)} style={{ display: "block", marginTop: "0.25rem", width: "100%" }}>
              <option value="">Não informar</option>
              {certificadoras.map((c) => <option key={c.nome} value={c.nome}>{c.nome}</option>)}
            </select>
          </label>

          {erro && <p role="alert" style={{ color: "var(--alerta)", fontSize: "0.84rem", marginTop: "0.5rem" }}>{erro}</p>}

          <button className="botao botao--secundario" style={{ marginTop: "0.6rem" }} onClick={enviar} disabled={enviando || !arquivo || !senha}>
            {enviando ? "Conectando…" : "Conectar certificado"}
          </button>

          <details style={{ marginTop: "0.7rem", fontSize: "0.78rem" }}>
            <summary style={{ cursor: "pointer", color: "var(--acento)" }}>Ainda não tenho um certificado A1</summary>
            <p style={{ marginTop: "0.4rem" }}>
              Compre um certificado e-CPF modelo A1 em qualquer Autoridade Certificadora credenciada pela ICP-Brasil.
              A emissão costuma ser 100% online, por videoconferência. Algumas opções:
            </p>
            <ul style={{ margin: "0.3rem 0 0", paddingLeft: "1.1rem" }}>
              {certificadoras.map((c) => (
                <li key={c.nome}><a href={c.site} target="_blank" rel="noreferrer">{c.nome}</a></li>
              ))}
            </ul>
          </details>
        </div>
      )}
    </div>
  );
}

type AssinaturaPreview = {
  nome: string;
  linhas: string[];
  logo_profissional_url: string | null;
  logo_corvia_url: string;
};

type AssinaturaEmail = {
  ativa: boolean;
  incluir_telefone: boolean;
  incluir_endereco: boolean;
  pre_visualizacao: AssinaturaPreview | null;
};

/** Assinatura anexada ao final de todo e-mail enviado pelo CorvIA Mail (caixa
 * nativa e contas Google/Microsoft conectadas) — logo Corvia, logo
 * profissional se houver, nome e CRM. Desligada por padrão; telefone e
 * endereço do consultório são opções à parte, mesmo com a assinatura ligada. */
function PreferenciaAssinaturaEmail() {
  const [dados, setDados] = useState<AssinaturaEmail | null>(null);
  const [salvando, setSalvando] = useState(false);
  const [erro, setErro] = useState("");

  useEffect(() => {
    api.get<AssinaturaEmail>("/email/assinatura").then(setDados).catch(() => {});
  }, []);

  async function salvar(proximo: Pick<AssinaturaEmail, "ativa" | "incluir_telefone" | "incluir_endereco">) {
    setSalvando(true);
    setErro("");
    try {
      setDados(await api.put<AssinaturaEmail>("/email/assinatura", proximo));
    } catch (e) {
      setErro(e instanceof ApiError ? e.message : "Não foi possível salvar a assinatura de e-mail.");
    } finally {
      setSalvando(false);
    }
  }

  if (!dados) return null;

  return (
    <div className="cartao">
      <h2 style={{ margin: "0 0 0.2rem" }}>Assinatura de e-mail</h2>
      <p style={{ margin: 0, fontSize: "0.82rem", color: "var(--texto-secundario)" }}>
        Anexa automaticamente a logo da Corvia, sua logo (se houver) e seu nome/CRM ao final de
        todo e-mail enviado pelo CorvIA Mail — caixa nativa e contas Google/Microsoft conectadas.
      </p>

      <label style={{ display: "flex", alignItems: "center", gap: "0.5rem", marginTop: "0.7rem" }}>
        <input
          type="checkbox" style={{ width: "auto" }} checked={dados.ativa} disabled={salvando}
          onChange={(e) => salvar({ ativa: e.target.checked, incluir_telefone: dados.incluir_telefone, incluir_endereco: dados.incluir_endereco })}
        />
        Incluir assinatura nos e-mails que eu enviar
      </label>

      {dados.ativa && (
        <div style={{ marginTop: "0.5rem", paddingLeft: "1.6rem", display: "flex", flexDirection: "column", gap: "0.4rem" }}>
          <label style={{ display: "flex", alignItems: "center", gap: "0.5rem" }}>
            <input
              type="checkbox" style={{ width: "auto" }} checked={dados.incluir_telefone} disabled={salvando}
              onChange={(e) => salvar({ ativa: true, incluir_telefone: e.target.checked, incluir_endereco: dados.incluir_endereco })}
            />
            Incluir telefone profissional
          </label>
          <label style={{ display: "flex", alignItems: "center", gap: "0.5rem" }}>
            <input
              type="checkbox" style={{ width: "auto" }} checked={dados.incluir_endereco} disabled={salvando}
              onChange={(e) => salvar({ ativa: true, incluir_telefone: dados.incluir_telefone, incluir_endereco: e.target.checked })}
            />
            Incluir endereço profissional
          </label>
        </div>
      )}

      {erro && <p role="alert" style={{ color: "var(--alerta)", fontSize: "0.84rem" }}>{erro}</p>}

      {dados.ativa && dados.pre_visualizacao && (
        <div style={{ marginTop: "0.7rem" }}>
          <p style={{ margin: "0 0 0.3rem", fontSize: "0.78rem", color: "var(--texto-secundario)" }}>Pré-visualização:</p>
          {/* JSX puro, nunca a prop de HTML cru do React — política de renderização
              segura (scripts/check-rendering-security.mjs) proíbe isso fora do renderer
              de e-mail recebido (CaixaDeEmail.tsx, sandboxado). React escapa todo texto
              aqui por padrão, então isso é seguro por construção, não por convenção. */}
          <div style={{ border: "1px solid var(--borda)", borderRadius: "8px", padding: "0.6rem", background: "#fff", display: "flex", gap: "14px" }}>
            <div>
              {dados.pre_visualizacao.logo_profissional_url && (
                <img
                  src={dados.pre_visualizacao.logo_profissional_url} alt=""
                  style={{ maxHeight: 48, maxWidth: 160, display: "block", marginBottom: 6 }}
                />
              )}
              <img src={dados.pre_visualizacao.logo_corvia_url} alt="Corvia" style={{ height: 22, display: "block" }} />
            </div>
            <div style={{ fontFamily: "Arial, Helvetica, sans-serif", fontSize: "12.5px", color: "#3a4750" }}>
              <strong style={{ color: "#0b2e45" }}>{dados.pre_visualizacao.nome}</strong>
              {dados.pre_visualizacao.linhas.map((linha, i) => <div key={i}>{linha}</div>)}
            </div>
          </div>
        </div>
      )}
    </div>
  );
}

type Fatura = {
  id: string;
  numero: string | null;
  status: string | null;
  total_centavos: number | null;
  moeda: string;
  criada_em: string | null;
  url_fatura: string | null;
  url_pdf: string | null;
};

const STATUS_FATURA: Record<string, string> = {
  paid: "Paga",
  open: "Em aberto",
  draft: "Rascunho",
  uncollectible: "Não recebida",
  void: "Cancelada",
};

function HistoricoCobrancas() {
  const [faturas, setFaturas] = useState<Fatura[] | null>(null);
  const [erro, setErro] = useState("");

  useEffect(() => {
    api
      .get<{ faturas: Fatura[] }>("/billing/faturas")
      .then((d) => setFaturas(d.faturas))
      .catch((e) => {
        setErro(e instanceof ApiError ? e.message : "Não foi possível carregar o histórico.");
        setFaturas([]);
      });
  }, []);

  return (
    <div className="cartao">
      <h2 style={{ marginTop: 0 }}>Histórico de cobranças</h2>

      {erro && <p role="alert" style={{ color: "var(--alerta)", fontSize: "0.86rem" }}>{erro}</p>}

      {faturas === null ? (
        <p>Carregando…</p>
      ) : faturas.length === 0 ? (
        <p style={{ margin: 0, color: "var(--texto-secundario)" }}>
          Nenhuma cobrança até agora. As faturas aparecem aqui depois da primeira renovação.
        </p>
      ) : (
        <div style={{ overflowX: "auto" }}>
          <table style={{ width: "100%", borderCollapse: "collapse", fontSize: "0.86rem" }}>
            <thead>
              <tr style={{ textAlign: "left", color: "var(--texto-secundario)" }}>
                <th style={{ padding: "0.3rem 0.5rem 0.3rem 0" }}>Data</th>
                <th style={{ padding: "0.3rem 0.5rem" }}>Valor</th>
                <th style={{ padding: "0.3rem 0.5rem" }}>Status</th>
                <th style={{ padding: "0.3rem 0" }}>Recibo</th>
              </tr>
            </thead>
            <tbody>
              {faturas.map((f) => (
                <tr key={f.id} style={{ borderTop: "1px solid var(--borda)" }}>
                  <td className="dado" style={{ padding: "0.4rem 0.5rem 0.4rem 0" }}>
                    {f.criada_em ? new Date(f.criada_em).toLocaleDateString("pt-BR") : "—"}
                  </td>
                  <td className="dado" style={{ padding: "0.4rem 0.5rem" }}>
                    {f.total_centavos === null
                      ? "—"
                      : (f.total_centavos / 100).toLocaleString("pt-BR", {
                          style: "currency",
                          currency: f.moeda,
                        })}
                  </td>
                  <td style={{ padding: "0.4rem 0.5rem" }}>
                    {STATUS_FATURA[f.status ?? ""] ?? f.status ?? "—"}
                  </td>
                  <td style={{ padding: "0.4rem 0" }}>
                    {f.url_pdf ? (
                      <a href={f.url_pdf} target="_blank" rel="noopener noreferrer">PDF</a>
                    ) : f.url_fatura ? (
                      <a href={f.url_fatura} target="_blank" rel="noopener noreferrer">Ver</a>
                    ) : (
                      "—"
                    )}
                  </td>
                </tr>
              ))}
            </tbody>
          </table>
        </div>
      )}
    </div>
  );
}

function TrocarSenha() {
  const [senhaAtual, setSenhaAtual] = useState("");
  const [novaSenha, setNovaSenha] = useState("");
  const [confirmacao, setConfirmacao] = useState("");
  const [mostrar, setMostrar] = useState(false);
  const [salvando, setSalvando] = useState(false);
  const [erro, setErro] = useState("");
  const [ok, setOk] = useState(false);

  const curta = novaSenha.length > 0 && novaSenha.length < 8;
  const divergente = confirmacao.length > 0 && confirmacao !== novaSenha;
  const valido = senhaAtual.length > 0 && novaSenha.length >= 8 && confirmacao === novaSenha;

  async function alterar() {
    setErro("");
    setOk(false);
    setSalvando(true);
    try {
      await api.post("/auth/alterar-senha", { senha_atual: senhaAtual, nova_senha: novaSenha });
      setSenhaAtual("");
      setNovaSenha("");
      setConfirmacao("");
      setOk(true);
    } catch (e) {
      setErro(e instanceof ApiError ? e.message : "Não foi possível alterar a senha.");
    } finally {
      setSalvando(false);
    }
  }

  const tipo = mostrar ? "text" : "password";

  return (
    <div className="cartao">
      <h2 style={{ marginTop: 0 }}>Senha</h2>

      <label htmlFor="senha-atual">Senha atual</label>
      <input id="senha-atual" type={tipo} value={senhaAtual} autoComplete="current-password"
             onChange={(e) => setSenhaAtual(e.target.value)} />

      <label htmlFor="senha-nova" style={{ marginTop: "0.8rem" }}>Nova senha</label>
      <input id="senha-nova" type={tipo} value={novaSenha} autoComplete="new-password"
             onChange={(e) => setNovaSenha(e.target.value)} />
      {curta && (
        <p style={{ color: "var(--alerta)", fontSize: "0.82rem", margin: "0.3rem 0 0" }}>
          Mínimo 8 caracteres.
        </p>
      )}

      <label htmlFor="senha-confirma" style={{ marginTop: "0.8rem" }}>Repita a nova senha</label>
      <input id="senha-confirma" type={tipo} value={confirmacao} autoComplete="new-password"
             onChange={(e) => setConfirmacao(e.target.value)} />
      {divergente && (
        <p style={{ color: "var(--alerta)", fontSize: "0.82rem", margin: "0.3rem 0 0" }}>
          As senhas não coincidem.
        </p>
      )}

      <label style={{ display: "flex", alignItems: "center", gap: "0.4rem", marginTop: "0.6rem", fontWeight: 400 }}>
        <input type="checkbox" checked={mostrar} onChange={(e) => setMostrar(e.target.checked)}
               style={{ width: "auto", margin: 0 }} />
        Mostrar senhas
      </label>

      {erro && <p role="alert" style={{ color: "var(--alerta)", fontSize: "0.86rem" }}>{erro}</p>}
      {ok && <p style={{ color: "var(--sucesso)", fontSize: "0.86rem" }}>Senha alterada.</p>}

      <button className="botao" style={{ marginTop: "0.8rem" }} onClick={alterar} disabled={!valido || salvando}>
        {salvando ? "Alterando…" : "Alterar senha"}
      </button>
    </div>
  );
}

function Assinatura() {
  const [carregando, setCarregando] = useState(true);
  const [status, setStatus] = useState<StatusAssinatura | null>(null);
  const [processando, setProcessando] = useState(false);
  const [erro, setErro] = useState("");

  useEffect(() => {
    api
      .get<StatusAssinatura>("/billing/status")
      .then(setStatus)
      .catch((e) => setErro(e instanceof ApiError ? e.message : "Não foi possível carregar sua assinatura."))
      .finally(() => setCarregando(false));
  }, []);

  async function ir(rota: "/billing/portal" | "/billing/checkout", campo: "portal_url" | "checkout_url") {
    setErro("");
    setProcessando(true);
    try {
      const resposta = await api.post<Record<string, string>>(rota);
      window.location.assign(resposta[campo]);
    } catch (e) {
      setErro(e instanceof ApiError ? e.message : "Não foi possível abrir a página de pagamento.");
      setProcessando(false);
    }
  }

  const ativa = status ? STATUS_COM_ACESSO.includes(status.status) : false;
  // Sem passagem pelo Stripe ainda não existe cliente, e o portal não tem o que abrir.
  const temCliente = status ? status.status !== "inativo" : false;

  return (
    <div className="cartao">
      <h2 style={{ marginTop: 0 }}>Assinatura</h2>

      {carregando ? (
        <p>Carregando…</p>
      ) : (
        <>
          <p>
            Status atual: <strong>{status ? ROTULOS[status.status] ?? status.status : "—"}</strong>
          </p>
          {status?.current_period_end && (
            <p style={{ fontSize: "0.86rem", opacity: 0.8 }}>
              {ativa ? "Renovação em: " : "Válida até: "}
              {new Date(status.current_period_end).toLocaleDateString("pt-BR")}
            </p>
          )}


          <p>
            <strong>
              {status?.plano ? PRECO_POR_PLANO[status.plano] ?? PRECO_POR_PLANO.basico : PRECO_POR_PLANO.basico}
            </strong>
          </p>

          {erro && <p role="alert" style={{ color: "var(--alerta)", fontSize: "0.86rem" }}>{erro}</p>}

          {!ativa && (
            <button className="botao" style={{ marginTop: "0.8rem" }}
                    onClick={() => ir("/billing/checkout", "checkout_url")} disabled={processando}>
              {processando ? "Redirecionando…" : "Assinar agora"}
            </button>
          )}

          {temCliente && (
            <>
              <button className="botao botao--secundario" style={{ marginTop: "0.8rem", marginLeft: ativa ? 0 : "0.5rem" }}
                      onClick={() => ir("/billing/portal", "portal_url")} disabled={processando}>
                {processando ? "Abrindo…" : "Gerenciar assinatura"}
              </button>
              <p style={{ fontSize: "0.82rem", opacity: 0.7, marginTop: "0.5rem" }}>
                No portal você troca a forma de pagamento, baixa os recibos e cancela a assinatura.
              </p>
            </>
          )}
        </>
      )}
    </div>
  );
}

export default function MinhaConta() {
  const { usuario, recarregar, sair } = useAuth();
  const navigate = useNavigate();
  const [perfil, setPerfil] = useState<Usuario | null>(usuario);
  const [saindo, setSaindo] = useState(false);

  useEffect(() => {
    api.get<Usuario>("/auth/me").then(setPerfil).catch(() => {});
  }, []);

  if (!perfil) return <div className="pagina"><h1>Minha conta</h1><p>Carregando…</p></div>;

  async function encerrarSessao() {
    setSaindo(true);
    await sair();
    navigate("/entrar", { replace: true });
  }

  return (
    <div className="pagina">
      <div className="conta__cabecalho">
        <div>
          <p className="eyebrow">Perfil e segurança</p>
          <h1>Minha conta</h1>
        </div>
        <button type="button" className="botao botao--secundario conta__logout"
                onClick={encerrarSessao} disabled={saindo}>
          {saindo ? "Saindo…" : "Sair do sistema"}
        </button>
      </div>
      {perfil.profile_completion_required && (
        <div className="cartao" role="status" style={{ borderLeft: "4px solid var(--destaque)" }}>
          <strong>Complete seus dados pessoais e profissionais para continuar.</strong>
          <p style={{ marginBottom: 0 }}>A senha atual continuará válida; não é necessário alterá-la.</p>
        </div>
      )}

      <div style={{ display: "grid", gap: "1rem", maxWidth: 560 }}>
        <RevisarTour />
        <Foto
          perfil={perfil}
          aoTrocar={(u) => {
            setPerfil(u);
            recarregar();
          }}
        />
        <LogoDocumento
          perfil={perfil}
          aoTrocar={(u) => {
            setPerfil(u);
            recarregar();
          }}
        />
        <PreferenciaAssinaturaDigital
          perfil={perfil}
          aoSalvar={(u) => {
            setPerfil(u);
            recarregar();
          }}
        />
        <ResumoSincronizacao />
        <CertificadoA1 />
        <PreferenciaAssinaturaEmail />
        <DadosPessoais
          perfil={perfil}
          aoSalvar={(u) => {
            setPerfil(u);
            recarregar();
          }}
        />
        <TrocarSenha />
        <Assinatura />
        <HistoricoCobrancas />
      </div>
    </div>
  );
}
