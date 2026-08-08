import { lazy, Suspense, useEffect, type ReactNode } from "react";
import { Navigate, Route, Routes, useLocation } from "react-router-dom";
import Shell from "./components/Shell";
import { Carregando } from "./components/Estado";
import { useAuth } from "./lib/auth";

const Entrar = lazy(() => import("./pages/Entrar"));
const Produto = lazy(() => import("./pages/Produto"));
const Painel = lazy(() => import("./pages/Painel"));
const Apresentacao = lazy(() => import("./pages/Apresentacao"));
const Trilhas = lazy(() => import("./pages/Trilhas"));
const TimelineDoencas = lazy(() => import("./pages/TimelineDoencas"));
const MaterialPaciente = lazy(() => import("./pages/MaterialPaciente"));
const Emergencia = lazy(() => import("./pages/Emergencia"));
const Trilha = lazy(() => import("./pages/Trilha"));
const CasosClinicos = lazy(() => import("./pages/CasosClinicos"));
const CasoClinico = lazy(() => import("./pages/CasoClinico"));
const Checklists = lazy(() => import("./pages/Checklists"));
const ChecklistAlta = lazy(() => import("./pages/ChecklistAlta"));
const Indicadores = lazy(() => import("./pages/Indicadores"));
const Cursos = lazy(() => import("./pages/Cursos"));
const Biblioteca = lazy(() => import("./pages/Biblioteca"));
const Fluxogramas = lazy(() => import("./pages/Fluxogramas"));
const Diretrizes = lazy(() => import("./pages/Diretrizes"));
const Galeria = lazy(() => import("./pages/Galeria"));
const ImagemGaleria = lazy(() => import("./pages/ImagemGaleria"));
const Documento = lazy(() => import("./pages/Documento"));
const Busca = lazy(() => import("./pages/Busca"));
const Calculadoras = lazy(() => import("./pages/Calculadoras"));
const Calculadora = lazy(() => import("./pages/Calculadora"));
const Medicamentos = lazy(() => import("./pages/Medicamentos"));
const Interacoes = lazy(() => import("./pages/Interacoes"));
const Condicoes = lazy(() => import("./pages/Condicoes"));
const Round = lazy(() => import("./pages/RoundGerenciavel"));
const Assistente = lazy(() => import("./pages/Assistente"));
const Admin = lazy(() => import("./pages/Admin"));
const SolicitarAcesso = lazy(() => import("./pages/SolicitarAcesso"));
const EsqueciSenha = lazy(() => import("./pages/EsqueciSenha"));
const RedefinirSenha = lazy(() => import("./pages/RedefinirSenha"));
const Favoritos = lazy(() => import("./pages/Favoritos"));
const Exames = lazy(() => import("./pages/Exames"));
const Exame = lazy(() => import("./pages/Exame"));
const Evidencias = lazy(() => import("./pages/Evidencias"));
const Evidencia = lazy(() => import("./pages/Evidencia"));
const Estudos = lazy(() => import("./pages/Estudos"));
const Estudo = lazy(() => import("./pages/Estudo"));
const Agenda = lazy(() => import("./pages/Agenda"));
const Templates = lazy(() => import("./pages/Templates"));
const AvaliacaoPreOperatoria = lazy(() => import("./pages/AvaliacaoPreOperatoria"));
const Assinatura = lazy(() => import("./pages/Assinatura"));
const MinhaConta = lazy(() => import("./pages/MinhaConta"));
const Sincronizacao = lazy(() => import("./pages/Sincronizacao"));
const Telediagnostico = lazy(() => import("./pages/Telediagnostico"));
const FilaTelediagnostico = lazy(() => import("./pages/FilaTelediagnostico"));
const CaixaDeEmail = lazy(() => import("./pages/CaixaDeEmail"));
const CorviaMail = lazy(() => import("./pages/CorviaMail"));
const Receituario = lazy(() => import("./pages/Receituario"));
const UsuariosOnline = lazy(() => import("./pages/UsuariosOnline"));
const GuiaDoencas = lazy(() => import("./pages/GuiaDoencas"));
const GuiaDoenca = lazy(() => import("./pages/GuiaDoenca"));
const TriagemSintomas = lazy(() => import("./pages/TriagemSintomas"));
const PoliticaPrivacidade = lazy(() => import("./pages/PoliticaPrivacidade"));
const TermosUso = lazy(() => import("./pages/TermosUso"));
const VerificacaoIdentidade = lazy(() => import("./pages/VerificacaoIdentidade"));
const Tour = lazy(() => import("./pages/Tour"));

function RotasSuspensas({ children }: { children: ReactNode }) {
  return (
    <Suspense fallback={<Carregando texto="Carregando a tela…" />}>
      {children}
    </Suspense>
  );
}

export default function App() {
  const { usuario, carregando } = useAuth();
  const location = useLocation();

  // Pedido do Rafael, 07/08/2026: a cada página interna aberta (troca de
  // rota), verifica se há versão nova do app — barato (GET condicional do
  // sw.js) e não recarrega nada por si só; só dispara reload se houver
  // mesmo uma versão nova (ver `verificarAtualizacaoDoServiceWorker` e o
  // listener de `controllerchange` em main.tsx). É o mesmo gancho usado no
  // login e no foco/retomada da aba — três gatilhos, um mecanismo só.
  useEffect(() => {
    (window as unknown as { __corviaVerificarAtualizacao?: () => void })
      .__corviaVerificarAtualizacao?.();
  }, [location.pathname]);

  if (carregando) return <Carregando texto="Abrindo a Corvia…" />;
  if (!usuario) {
    return (
      <RotasSuspensas>
        <Routes>
          <Route path="/" element={<Produto />} />
          <Route path="/produto" element={<Produto />} />
          <Route path="/entrar" element={<Entrar />} />
          <Route path="/solicitar-acesso" element={<SolicitarAcesso />} />
          <Route path="/esqueci-senha" element={<EsqueciSenha />} />
          <Route path="/redefinir-senha" element={<RedefinirSenha />} />
          <Route path="/corvia-mail" element={<CorviaMail />} />
          <Route path="/privacidade" element={<PoliticaPrivacidade />} />
          <Route path="/termos" element={<TermosUso />} />
          <Route path="*" element={<Navigate to="/" replace />} />
        </Routes>
      </RotasSuspensas>
    );
  }

  if (usuario.profile_completion_required && location.pathname !== "/minha-conta") {
    return <Navigate to="/minha-conta" replace />;
  }

  // KYC obrigatório pós-pagamento (Trabalho 11/12, 06/08/2026) — só passa
  // daqui quem já teve o cadastro liberado (checagem automática do
  // conselho, ou já aprovado pelo Rafael). Vem DEPOIS do gate de perfil
  // acima de propósito: sem profissão/conselho preenchidos, o KYC nem
  // teria o que checar.
  if (usuario.kyc_required && location.pathname !== "/verificacao-identidade") {
    return <Navigate to="/verificacao-identidade" replace />;
  }

  // Tour guiado do primeiro acesso (Trabalho 13, 06/08/2026) — só depois
  // do perfil e do KYC resolvidos, uma única vez por assinante.
  if (usuario.onboarding_pendente && location.pathname !== "/tour") {
    return <Navigate to="/tour" replace />;
  }

  return (
    <RotasSuspensas>
      <Routes>
        <Route element={<Shell />}>
          <Route index element={<Painel />} />
          <Route path="apresentacao" element={<Apresentacao />} />
          <Route path="biblioteca" element={<Biblioteca />} />
          <Route path="biblioteca/:slug" element={<Documento />} />
          <Route path="doencas" element={<GuiaDoencas />} />
          <Route path="doencas/:slug" element={<GuiaDoenca />} />
          <Route path="triagem-sintomas" element={<TriagemSintomas />} />
          <Route path="fluxogramas" element={<Fluxogramas />} />
          <Route path="diretrizes" element={<Diretrizes />} />
          <Route path="busca" element={<Busca />} />
          <Route path="calculadoras" element={<Calculadoras />} />
          <Route path="calculadoras/:slug" element={<Calculadora />} />
          <Route path="medicamentos" element={<Medicamentos />} />
          <Route path="interacoes" element={<Interacoes />} />
          <Route path="condicoes" element={<Condicoes />} />
          <Route path="galeria" element={<Galeria />} />
          <Route path="galeria/:slug" element={<ImagemGaleria />} />
          <Route path="exames" element={<Exames />} />
          <Route path="exames/:slug" element={<Exame />} />
          <Route path="evidencias" element={<Evidencias />} />
          <Route path="evidencias/:slug" element={<Evidencia />} />
          <Route path="estudos" element={<Estudos />} />
          <Route path="estudos/:slug" element={<Estudo />} />
          <Route path="trilhas" element={<Trilhas />} />
          <Route path="trilhas/timeline" element={<TimelineDoencas />} />
          <Route path="material-paciente" element={<MaterialPaciente />} />
          <Route path="emergencia" element={<Emergencia />} />
          <Route path="trilhas/:slug" element={<Trilha />} />
          <Route path="casos-clinicos" element={<CasosClinicos />} />
          <Route path="casos-clinicos/:slug" element={<CasoClinico />} />
          <Route path="checklists" element={<Checklists />} />
          <Route path="checklists/alta/:id" element={<ChecklistAlta />} />
          <Route path="indicadores" element={<Indicadores />} />
          <Route path="cursos" element={<Cursos />} />
          <Route path="cursos/:slug" element={<Navigate to="/cursos" replace />} />
          <Route path="favoritos" element={<Favoritos />} />
          <Route path="assistente" element={<Assistente />} />
          <Route path="round" element={<Round />} />
          <Route path="agenda" element={<Agenda />} />
          <Route path="documentos" element={<Templates />} />
          <Route path="avaliacao-preoperatoria" element={<AvaliacaoPreOperatoria />} />
          <Route path="receituario" element={<Receituario />} />
          <Route path="assinatura" element={<Assinatura />} />
          <Route path="minha-conta" element={<MinhaConta />} />
          <Route path="sincronizacao" element={<Sincronizacao />} />
          <Route path="verificacao-identidade" element={<VerificacaoIdentidade />} />
          <Route path="telediagnostico" element={<Telediagnostico />} />
          <Route path="caixa-de-email" element={<CaixaDeEmail />} />
          <Route path="corvia-mail" element={<CorviaMail />} />
          <Route path="usuarios-online" element={<UsuariosOnline />} />
          <Route path="privacidade" element={<PoliticaPrivacidade />} />
          <Route path="termos" element={<TermosUso />} />
          {usuario.role === "admin" && <Route path="admin" element={<Admin />} />}
          {usuario.role === "admin" && (
            <Route path="fila-telediagnostico" element={<FilaTelediagnostico />} />
          )}
          {usuario.role === "admin" && (
            <Route path="admin/usuarios-online" element={<Navigate to="/usuarios-online" replace />} />
          )}
        </Route>
        {/* Fora do <Shell />, de propósito — layout de tela cheia própria,
            sem sidebar/topo por trás (Trabalho 13, 06/08/2026). */}
        <Route path="/tour" element={<Tour />} />
        <Route path="*" element={<Navigate to="/" replace />} />
      </Routes>
    </RotasSuspensas>
  );
}
