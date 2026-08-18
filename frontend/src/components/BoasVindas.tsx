import { useState } from "react";
import { api } from "../lib/api";
import { useAuth } from "../lib/auth";

/** Popup de boas-vindas pessoal — pedido do Rafael em 31/07/2026, para o
 * primeiro acesso do próprio pai (Sr. Wladmir). Não é sistema genérico de
 * avisos: o texto é fixo, e só aparece pra quem tem
 * `usuario.boas_vindas_pendente === true` (setado manualmente no banco,
 * um por um, nunca em massa). Fecha e nunca mais aparece — chama
 * `POST /auth/me/boas-vindas-vista` e recarrega o usuário. */
export default function BoasVindas() {
  const { usuario, recarregar } = useAuth();
  const [fechando, setFechando] = useState(false);

  if (!usuario?.boas_vindas_pendente) return null;

  async function fechar() {
    setFechando(true);
    try {
      await api.post("/auth/me/boas-vindas-vista");
    } finally {
      recarregar();
    }
  }

  return (
    <div className="boasvindas__fundo" role="dialog" aria-modal="true" aria-label="Mensagem de boas-vindas">
      <div className="boasvindas__cartao">
        <img src="/corvia-logo-canonical.svg" alt="CorVIA Clinical OS" className="boasvindas__logo" />
        <p className="boasvindas__texto">
          Sr. Wladmir, é com muito orgulho e satisfação que seu filho Rafael Paes Meirelles lhe
          apresenta o CorVIA Clinical OS, plataforma inédita no Brasil que
          reunirá o maior número de funcionalidades e conteúdo científico da mais alta qualidade
          em cardiologia em uma só plataforma do Brasil, transformando o acesso ao conhecimento e
          auxiliando e embasando a tomada de decisões do médico cardiologista ou de outras
          especialidades de maneira rápida e precisa, sempre em benefício do paciente.
        </p>
        <p className="boasvindas__texto">
          Sinta-se em casa e saiba que nada disso seria possível sem o esforço do Sr. e da Sra.
          Iaci! Um grande abraço.
        </p>
        <p className="boasvindas__assinatura">Dr. Rafael Paes Meirelles</p>
        <button className="botao" onClick={fechar} disabled={fechando}>
          {fechando ? "Fechando…" : "Entrar no sistema"}
        </button>
      </div>
    </div>
  );
}
