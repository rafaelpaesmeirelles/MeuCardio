import { useState } from "react";
import { Link } from "react-router-dom";
import { api } from "../lib/api";
import Credito from "../components/Credito";

export default function EsqueciSenha() {
  const [email, setEmail] = useState("");
  const [enviado, setEnviado] = useState(false);
  const [enviando, setEnviando] = useState(false);

  async function enviar() {
    setEnviando(true);
    try {
      await api.post("/auth/esqueci-senha", { email: email.trim() });
    } finally {
      setEnviando(false);
      setEnviado(true); // sempre mostra a mesma mensagem, exista o e-mail ou não
    }
  }

  return (
    <div className="login">
      <div className="login__cartao">
        <div className="login__brasao">
          <h1 style={{ fontSize: "1.25rem", marginTop: 14 }}>Esqueci minha senha</h1>
        </div>
        <div className="fio-dourado" style={{ marginBottom: "1rem" }} />

        {enviado ? (
          <>
            <p>
              Se esse e-mail estiver cadastrado e ativo, um link de redefinição foi gerado.
              Como o envio automático por e-mail ainda não está configurado, peça pra um
              administrador te repassar o link pelo painel dele.
            </p>
            <Link to="/entrar" className="botao" style={{ display: "block", textAlign: "center", marginTop: "1rem" }}>
              Voltar para o login
            </Link>
          </>
        ) : (
          <>
            <label htmlFor="email">E-mail cadastrado</label>
            <input id="email" type="email" value={email} onChange={(e) => setEmail(e.target.value)} />
            <button className="botao" style={{ width: "100%", marginTop: "1rem" }}
                    onClick={enviar} disabled={!email.includes("@") || enviando}>
              {enviando ? "Enviando…" : "Solicitar redefinição"}
            </button>
            <Link to="/entrar" style={{ display: "block", textAlign: "center", marginTop: "0.8rem", fontSize: "0.86rem" }}>
              Voltar para o login
            </Link>
          </>
        )}
        <Credito compacto />
      </div>
    </div>
  );
}
