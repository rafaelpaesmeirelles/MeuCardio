/** Painel de presença — quem está usando a Corvia agora (só admin).
 *
 *  Consome `GET /api/admin/usuarios-online`, que já existia sem tela desde
 *  31/07/2026. "Online" não é campo gravado: é derivado de `last_seen_at` numa
 *  janela de 5 minutos, e o próprio backend faz esse cálculo — a tela não
 *  recalcula nada, só mostra.
 *
 *  Atualiza sozinha a cada 30s. A janela do backend é de 5 minutos, então
 *  intervalo menor que isso é o suficiente para a lista não ficar visivelmente
 *  velha, sem transformar a página aberta num gerador de requisições.
 */
import { useCallback, useEffect, useState } from "react";
import { api } from "../lib/api";
import { Carregando, Erro } from "../components/Estado";

type UsuarioPresenca = {
  id: number;
  full_name: string;
  email: string;
  role: string;
  last_seen_at: string | null;
  online: boolean;
};

function desde(iso: string | null) {
  if (!iso) return "nunca acessou";
  const minutos = Math.floor((Date.now() - new Date(iso).getTime()) / 60000);
  if (minutos < 1) return "agora mesmo";
  if (minutos < 60) return `há ${minutos} min`;
  const horas = Math.floor(minutos / 60);
  if (horas < 24) return `há ${horas} h`;
  const dias = Math.floor(horas / 24);
  if (dias < 30) return `há ${dias} ${dias === 1 ? "dia" : "dias"}`;
  return new Date(iso).toLocaleDateString("pt-BR");
}

export default function UsuariosOnline() {
  const [lista, setLista] = useState<UsuarioPresenca[] | null>(null);
  const [erro, setErro] = useState("");
  const [atualizadoEm, setAtualizadoEm] = useState<Date | null>(null);

  const carregar = useCallback(() => {
    api
      .get<UsuarioPresenca[]>("/admin/usuarios-online")
      .then((l) => { setLista(l); setAtualizadoEm(new Date()); setErro(""); })
      .catch(() => setErro("Não foi possível carregar a lista de presença."));
  }, []);

  useEffect(() => {
    carregar();
    const t = setInterval(carregar, 30000);
    return () => clearInterval(t);
  }, [carregar]);

  if (erro && !lista) return <Erro mensagem={erro} />;
  if (!lista) return <Carregando texto="Verificando quem está online…" />;

  const online = lista.filter((u) => u.online);
  const offline = lista.filter((u) => !u.online);

  return (
    <div>
      <h1>Usuários online</h1>
      <p style={{ color: "var(--texto-suave, #5a6b78)" }}>
        Considera-se online quem teve atividade nos últimos 5 minutos. A lista se atualiza sozinha a
        cada 30 segundos
        {atualizadoEm && <> — última verificação às {atualizadoEm.toLocaleTimeString("pt-BR")}</>}.
      </p>

      {erro && <p style={{ color: "var(--erro, #8a1c12)" }}>{erro}</p>}

      <div style={{ display: "flex", gap: "1rem", flexWrap: "wrap", margin: "1rem 0 1.5rem" }}>
        <div style={{ padding: ".7rem 1.1rem", borderRadius: 8, background: "var(--acento-suave, #eef5f8)", minWidth: 120 }}>
          <strong style={{ display: "block", fontSize: "1.6rem", color: "var(--acento)", lineHeight: 1.1 }}>
            {online.length}
          </strong>
          <span style={{ fontSize: ".85rem", color: "var(--texto-suave, #5a6b78)" }}>online agora</span>
        </div>
        <div style={{ padding: ".7rem 1.1rem", borderRadius: 8, background: "var(--fundo-suave, #f6f4f1)", minWidth: 120 }}>
          <strong style={{ display: "block", fontSize: "1.6rem", lineHeight: 1.1 }}>{lista.length}</strong>
          <span style={{ fontSize: ".85rem", color: "var(--texto-suave, #5a6b78)" }}>contas ativas</span>
        </div>
      </div>

      <h2 style={{ fontSize: "1.05rem" }}>Online agora</h2>
      {online.length === 0 ? (
        <p style={{ color: "var(--texto-suave, #5a6b78)" }}>Ninguém online neste momento.</p>
      ) : (
        <Tabela linhas={online} destacar />
      )}

      <h2 style={{ fontSize: "1.05rem", marginTop: "1.75rem" }}>Demais contas</h2>
      {offline.length === 0 ? (
        <p style={{ color: "var(--texto-suave, #5a6b78)" }}>Todas as contas estão online.</p>
      ) : (
        <Tabela linhas={offline} />
      )}
    </div>
  );
}

function Tabela({ linhas, destacar = false }: { linhas: UsuarioPresenca[]; destacar?: boolean }) {
  return (
    <div style={{ overflowX: "auto" }}>
      <table style={{ width: "100%", borderCollapse: "collapse", fontSize: ".92rem" }}>
        <thead>
          <tr style={{ textAlign: "left", borderBottom: "2px solid var(--linha, #e2ddd5)" }}>
            <th style={{ padding: ".5rem .4rem" }}>Nome</th>
            <th style={{ padding: ".5rem .4rem" }}>E-mail</th>
            <th style={{ padding: ".5rem .4rem" }}>Perfil</th>
            <th style={{ padding: ".5rem .4rem" }}>Última atividade</th>
          </tr>
        </thead>
        <tbody>
          {linhas.map((u) => (
            <tr key={u.id} style={{ borderBottom: "1px solid var(--linha, #eee9e2)" }}>
              <td style={{ padding: ".5rem .4rem" }}>
                <span
                  aria-hidden="true"
                  style={{
                    display: "inline-block", width: 8, height: 8, borderRadius: "50%", marginRight: 8,
                    background: destacar ? "#1f9d55" : "var(--linha, #cfcac3)",
                  }}
                />
                {u.full_name}
              </td>
              <td style={{ padding: ".5rem .4rem", color: "var(--texto-suave, #5a6b78)" }}>{u.email}</td>
              <td style={{ padding: ".5rem .4rem" }}>{u.role === "admin" ? "Administrador" : "Assinante"}</td>
              <td style={{ padding: ".5rem .4rem", whiteSpace: "nowrap" }}>{desde(u.last_seen_at)}</td>
            </tr>
          ))}
        </tbody>
      </table>
    </div>
  );
}
