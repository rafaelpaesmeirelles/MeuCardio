import { useState } from "react";
import { Link, useNavigate, useSearchParams } from "react-router-dom";
import { api, ApiError } from "../lib/api";
import Credito from "../components/Credito";

export default function RedefinirSenha() {
  const [params] = useSearchParams();
  const navigate = useNavigate();
  const token = params.get("token") ?? "";
  // 'email' = senha da caixa de e-mail do CorvIA Mail (Tarefa 28), distinta
  // da senha da conta Corvia — o backend já sabe qual é qual pelo próprio
  // token (campo `alvo` em `password_reset_tokens`); este parâmetro só serve
  // pra escolher a mensagem e o redirecionamento certos aqui na tela.
  const alvo = params.get("alvo") === "email" ? "email" : "conta";
  const [senha, setSenha] = useState("");
  const [confirmacao, setConfirmacao] = useState("");
  const [erro, setErro] = useState("");
  const [enviando, setEnviando] = useState(false);
  const [feito, setFeito] = useState(false);

  const senhasBatem = senha.length > 0 && senha === confirmacao;

  async function enviar() {
    setErro("");
    setEnviando(true);
    try {
      await api.post("/auth/redefinir-senha", { token, nova_senha: senha });
      setFeito(true);
      const destino = alvo === "email" ? "/corvia-mail" : "/entrar";
      setTimeout(() => navigate(destino), 2500);
    } catch (e) {
      setErro(e instanceof ApiError ? e.message : "Não foi possível redefinir a senha.");
    } finally {
      setEnviando(false);
    }
  }

  if (!token) {
    return (
      <div className="login">
        <div className="login__cartao">
          <p>Link inválido — faltou o token de redefinição.</p>
          <Link to="/esqueci-senha" className="botao" style={{ display: "block", textAlign: "center", marginTop: "1rem" }}>
            Solicitar novo link
          </Link>
        </div>
      </div>
    );
  }

  return (
    <div className="login">
      <div className="login__cartao">
        <div className="login__brasao">
          <h1 style={{ fontSize: "1.25rem", marginTop: 14 }}>
            {alvo === "email" ? "Nova senha da caixa de e-mail" : "Nova senha"}
          </h1>
        </div>

        {feito ? (
          <p>Senha redefinida. Levando você para {alvo === "email" ? "o CorvIA Mail" : "o login"}…</p>
        ) : (
          <>
            <label htmlFor="senha">Nova senha</label>
            <input id="senha" type="password" value={senha} onChange={(e) => setSenha(e.target.value)} />

            <label htmlFor="confirmacao" style={{ marginTop: "0.8rem" }}>Confirmar senha</label>
            <input id="confirmacao" type="password" value={confirmacao}
                   onChange={(e) => setConfirmacao(e.target.value)} />

            {confirmacao.length > 0 && !senhasBatem && (
              <p style={{ color: "var(--alerta)", fontSize: "0.82rem", marginTop: "0.3rem" }}>
                As senhas não coincidem.
              </p>
            )}
            {erro && <p role="alert" style={{ color: "var(--alerta)", fontSize: "0.86rem" }}>{erro}</p>}

            <button className="botao" style={{ width: "100%", marginTop: "1rem" }}
                    onClick={enviar} disabled={!senhasBatem || senha.length < 8 || enviando}>
              {enviando ? "Salvando…" : "Redefinir senha"}
            </button>
          </>
        )}
        <Credito compacto />
      </div>
    </div>
  );
}
