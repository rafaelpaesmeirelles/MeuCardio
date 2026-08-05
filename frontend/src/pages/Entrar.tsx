import { useState } from "react";
import { Link } from "react-router-dom";
import { useAuth } from "../lib/auth";
import Credito from "../components/Credito";

export default function Entrar() {
  const { entrar } = useAuth();
  const [email, setEmail] = useState("");
  const [senha, setSenha] = useState("");
  const [mostrarSenha, setMostrarSenha] = useState(false);
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
          <img src="/corvia-logo.png" alt="Corvia — O caminho do coração" style={{ width: "100%", maxWidth: "340px", height: "auto" }} />
        </div>

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
        <div style={{ position: "relative" }}>
          <input
            id="senha"
            type={mostrarSenha ? "text" : "password"}
            autoComplete="current-password"
            value={senha}
            onChange={(e) => setSenha(e.target.value)}
            onKeyDown={(e) => e.key === "Enter" && enviar()}
            style={{ width: "100%", paddingRight: "3.2rem" }}
          />
          <button
            type="button"
            onClick={() => setMostrarSenha((v) => !v)}
            aria-label={mostrarSenha ? "Ocultar senha" : "Mostrar senha"}
            style={{
              position: "absolute",
              right: "0.6rem",
              top: "50%",
              transform: "translateY(-50%)",
              background: "none",
              border: "none",
              fontSize: "0.78rem",
              color: "var(--acento)",
              cursor: "pointer",
              padding: 0,
            }}
          >
            {mostrarSenha ? "Ocultar" : "Mostrar"}
          </button>
        </div>

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
          to="/produto#acesso"
          style={{ display: "block", textAlign: "center", marginTop: "1rem", fontWeight: 600 }}
        >
          Conheça a Corvia
        </Link>
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
          Todo o caminho da Cardiologia, num só lugar — da evidência à decisão,
          ao lado do paciente.
        </p>
        <Credito compacto />
      </div>
    </div>
  );
}
