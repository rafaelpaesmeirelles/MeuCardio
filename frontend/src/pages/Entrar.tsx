import { useState } from "react";
import { Link } from "react-router-dom";
import { useAuth } from "../lib/auth";
import Credito from "../components/Credito";
import ApoioBiolab from "../components/ApoioBiolab";

export default function Entrar() {
  const { entrar } = useAuth();
  const [email, setEmail] = useState("");
  const [senha, setSenha] = useState("");
  const [erro, setErro] = useState("");
  const [enviando, setEnviando] = useState(false);

  async function enviar() {
    setEnviando(true);
    setErro("");
    try {
      await entrar(email.trim().toLowerCase(), senha);
    } catch (e) {
      setErro(e instanceof Error ? e.message : "Não foi possível entrar.");
    } finally {
      setEnviando(false);
    }
  }

  return (
    <div className="login">
      <div className="login__cartao">
        <div className="login__brasao">
          <img src="/logo.png" alt="MeuCardio" />
        </div>
        <div className="fio-dourado" style={{ marginBottom: "1.1rem" }} />

        <label htmlFor="email">E-mail</label>
        <input
          id="email"
          type="email"
          autoComplete="username"
          value={email}
          onChange={(e) => setEmail(e.target.value)}
          onKeyDown={(e) => e.key === "Enter" && enviar()}
        />

        <label htmlFor="senha" style={{ marginTop: "0.8rem" }}>Senha</label>
        <input
          id="senha"
          type="password"
          autoComplete="current-password"
          value={senha}
          onChange={(e) => setSenha(e.target.value)}
          onKeyDown={(e) => e.key === "Enter" && enviar()}
        />

        {erro && (
          <p role="alert" style={{ color: "var(--alerta)", fontSize: "0.86rem" }}>{erro}</p>
        )}

        <button
          className="botao"
          style={{ width: "100%", marginTop: "1rem" }}
          onClick={enviar}
          disabled={enviando || !email || !senha}
        >
          {enviando ? "Entrando…" : "Entrar"}
        </button>

        <Link
          to="/solicitar-acesso"
          style={{ display: "block", textAlign: "center", marginTop: "0.8rem", fontSize: "0.86rem" }}
        >
          Ainda não tem acesso? Solicitar cadastro
        </Link>
        <Link
          to="/esqueci-senha"
          style={{ display: "block", textAlign: "center", marginTop: "0.5rem", fontSize: "0.86rem" }}
        >
          Esqueci minha senha
        </Link>

        <p className="aviso">
          Uso restrito à equipe assistencial. Dados de pacientes registrados aqui seguem as
          mesmas regras de sigilo do prontuário.
        </p>
        <Credito compacto />
        <ApoioBiolab />
      </div>
    </div>
  );
}
