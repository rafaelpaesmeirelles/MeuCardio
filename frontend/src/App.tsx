import { Navigate, Route, Routes } from "react-router-dom";
import Shell from "./components/Shell";
import { Carregando } from "./components/Estado";
import { useAuth } from "./lib/auth";
import Entrar from "./pages/Entrar";
import Painel from "./pages/Painel";
import Checklists from "./pages/Checklists";
import ChecklistAlta from "./pages/ChecklistAlta";
import Indicadores from "./pages/Indicadores";
import Cursos from "./pages/Cursos";
import Curso from "./pages/Curso";
import Biblioteca from "./pages/Biblioteca";
import Fluxogramas from "./pages/Fluxogramas";
import Galeria from "./pages/Galeria";
import ImagemGaleria from "./pages/ImagemGaleria";
import Documento from "./pages/Documento";
import Busca from "./pages/Busca";
import Calculadoras from "./pages/Calculadoras";
import Calculadora from "./pages/Calculadora";
import Medicamentos from "./pages/Medicamentos";
import Round from "./pages/Round";
import Assistente from "./pages/Assistente";
import Admin from "./pages/Admin";
import SolicitarAcesso from "./pages/SolicitarAcesso";
import EsqueciSenha from "./pages/EsqueciSenha";
import RedefinirSenha from "./pages/RedefinirSenha";
import Favoritos from "./pages/Favoritos";
import Exames from "./pages/Exames";
import Exame from "./pages/Exame";
import Evidencias from "./pages/Evidencias";
import Evidencia from "./pages/Evidencia";
import Estudos from "./pages/Estudos";
import Estudo from "./pages/Estudo";
import Agenda from "./pages/Agenda";
import Templates from "./pages/Templates";
import Assinatura from "./pages/Assinatura";
import MinhaConta from "./pages/MinhaConta";
import Telediagnostico from "./pages/Telediagnostico";
import FilaTelediagnostico from "./pages/FilaTelediagnostico";

export default function App() {
  const { usuario, carregando } = useAuth();

  if (carregando) return <Carregando texto="Abrindo o MeuCardio…" />;
  if (!usuario) {
    return (
      <Routes>
        <Route path="/entrar" element={<Entrar />} />
        <Route path="/solicitar-acesso" element={<SolicitarAcesso />} />
        <Route path="/esqueci-senha" element={<EsqueciSenha />} />
        <Route path="/redefinir-senha" element={<RedefinirSenha />} />
        <Route path="*" element={<Navigate to="/entrar" replace />} />
      </Routes>
    );
  }

  return (
    <Routes>
      <Route element={<Shell />}>
        <Route index element={<Painel />} />
        <Route path="biblioteca" element={<Biblioteca />} />
        <Route path="biblioteca/:slug" element={<Documento />} />
        <Route path="fluxogramas" element={<Fluxogramas />} />
        <Route path="busca" element={<Busca />} />
        <Route path="calculadoras" element={<Calculadoras />} />
        <Route path="calculadoras/:slug" element={<Calculadora />} />
        <Route path="medicamentos" element={<Medicamentos />} />
        <Route path="galeria" element={<Galeria />} />
        <Route path="galeria/:slug" element={<ImagemGaleria />} />
        <Route path="exames" element={<Exames />} />
        <Route path="exames/:slug" element={<Exame />} />
        <Route path="evidencias" element={<Evidencias />} />
        <Route path="evidencias/:slug" element={<Evidencia />} />
        <Route path="estudos" element={<Estudos />} />
        <Route path="estudos/:slug" element={<Estudo />} />
        <Route path="checklists" element={<Checklists />} />
        <Route path="checklists/alta/:id" element={<ChecklistAlta />} />
        <Route path="indicadores" element={<Indicadores />} />
        <Route path="cursos" element={<Cursos />} />
        <Route path="cursos/:slug" element={<Curso />} />
        <Route path="favoritos" element={<Favoritos />} />
        <Route path="assistente" element={<Assistente />} />
        <Route path="round" element={<Round />} />
        <Route path="agenda" element={<Agenda />} />
        <Route path="documentos" element={<Templates />} />
        <Route path="assinatura" element={<Assinatura />} />
        <Route path="minha-conta" element={<MinhaConta />} />
        <Route path="telediagnostico" element={<Telediagnostico />} />
        {usuario.role === "admin" && (
          <Route path="admin" element={<Admin />} />
        )}
        {usuario.role === "admin" && (
          <Route path="fila-telediagnostico" element={<FilaTelediagnostico />} />
        )}
      </Route>
      <Route path="*" element={<Navigate to="/" replace />} />
    </Routes>
  );
}
