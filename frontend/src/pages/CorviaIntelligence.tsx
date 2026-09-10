import { Link, useSearchParams } from "react-router-dom";
import Diretrizes from "./Diretrizes";
import ScientificReadingAccess from "../components/ScientificReadingAccess";
import BotaoFavorito from "../components/BotaoFavorito";

export default function CorviaIntelligence() {
  const [params] = useSearchParams();
  const source = params.get("fonte");
  if (source === null) return <Diretrizes intelligenceOnly />;
  const sourceKey = /^[a-f0-9]{64}$/i.test(source) ? source.toLowerCase() : null;
  return <section>
    <Link to="/intelligence">← CorVIA Intelligence</Link>
    <p className="eyebrow">Acervo científico</p>
    <h1>Publicação original</h1>
    {!sourceKey ? <p role="alert">A referência desta publicação é inválida. Abra uma publicação pelo acervo ou pela busca Tudo com Tudo.</p> : <>
      <p>Consulte o original armazenado e as versões em português disponíveis. A disponibilidade da fonte não representa revisão clínica pelo CorVIA.</p>
      <BotaoFavorito itemType="publicacao_original" itemSlug={sourceKey} />
      <ScientificReadingAccess key={sourceKey} entityType="publicacao_original" slug={sourceKey} />
    </>}
  </section>;
}
