import { Link } from "react-router-dom";
import "../styles/legal.css";

const EMAIL_EXCLUSAO = "contato@corvia.med.br";
const ASSUNTO = "Solicitação de exclusão de conta CorVIA";
const CORPO = "Olá, solicito a exclusão da minha conta CorVIA e dos dados pessoais associados. Meu e-mail cadastrado é: ";
const MAILTO = `mailto:${EMAIL_EXCLUSAO}?subject=${encodeURIComponent(ASSUNTO)}&body=${encodeURIComponent(CORPO)}`;

export default function ExcluirConta() {
  return (
    <main className="legal-page" id="conteudo-principal">
      <header>
        <Link to="/" aria-label="Voltar ao CorVIA">
          <img src="/corvia-logo-canonical-dark.svg" alt="CorVIA" />
        </Link>
        <p className="eyebrow">Conta e privacidade</p>
        <h1>Solicitar exclusão da conta CorVIA</h1>
        <p>Última atualização: 28 de agosto de 2026.</p>
      </header>

      <section>
        <h2>Como solicitar</h2>
        <p>
          O titular de uma conta CorVIA pode solicitar a exclusão da conta e dos dados pessoais associados a qualquer momento.
          Para que possamos confirmar a identidade com segurança, envie a solicitação a partir do mesmo endereço de e-mail cadastrado na conta.
        </p>
        <p>
          <a className="botao" href={MAILTO}>Solicitar exclusão por e-mail</a>
        </p>
        <p>
          Se o botão não abrir seu aplicativo de e-mail, escreva para <a href={`mailto:${EMAIL_EXCLUSAO}`}>{EMAIL_EXCLUSAO}</a> com o assunto
          “Solicitação de exclusão de conta CorVIA” e informe o e-mail cadastrado.
        </p>
      </section>

      <section>
        <h2>O que será excluído</h2>
        <p>Após a validação da solicitação, serão eliminados ou anonimizados, conforme aplicável:</p>
        <ul>
          <li>dados de identificação e perfil vinculados à conta;</li>
          <li>preferências, configurações e dados de uso associados ao usuário;</li>
          <li>tokens e vínculos de integrações conectadas à conta;</li>
          <li>arquivos e conteúdos pessoais cuja conservação não seja necessária por obrigação legal ou regulatória;</li>
          <li>outros dados pessoais que não precisem ser mantidos para cumprir obrigação legal, regulatória, fiscal, de segurança ou para exercício regular de direitos.</li>
        </ul>
      </section>

      <section>
        <h2>Dados que podem precisar ser mantidos</h2>
        <p>
          Alguns registros podem ser conservados pelo período estritamente necessário quando houver obrigação legal ou regulatória,
          necessidade de prevenção a fraude e segurança, cumprimento de obrigações fiscais/contábeis, exercício regular de direitos ou
          deveres profissionais relacionados a documentos e registros clínicos. Nesses casos, o acesso fica restrito à finalidade de conservação
          e os dados são eliminados ou anonimizados quando o prazo aplicável termina.
        </p>
      </section>

      <section>
        <h2>Prazo e confirmação</h2>
        <p>
          A solicitação será registrada após o recebimento. Poderemos pedir confirmação adicional de identidade antes de executar a exclusão,
          especialmente quando houver dados sensíveis ou documentos profissionais vinculados à conta. A conclusão será comunicada ao e-mail do titular.
        </p>
      </section>

      <section>
        <h2>Alternativas à exclusão</h2>
        <p>
          Se você deseja apenas corrigir dados, revogar uma integração ou cancelar uma assinatura, use as opções disponíveis em “Minha conta” ou
          escreva para <a href={`mailto:${EMAIL_EXCLUSAO}`}>{EMAIL_EXCLUSAO}</a>. A exclusão da conta é destinada a quem deseja encerrar o vínculo com o CorVIA.
        </p>
      </section>

      <footer>
        <Link to="/privacidade">Política de Privacidade</Link>
        <Link to="/termos">Termos de Uso</Link>
        <Link to="/">Voltar ao CorVIA</Link>
      </footer>
    </main>
  );
}
