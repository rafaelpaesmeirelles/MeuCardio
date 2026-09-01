import { useEffect, useMemo, useState } from "react";
import { createPortal } from "react-dom";
import { Link, useLocation } from "react-router-dom";
import Icone, { type NomeIcone } from "./Icone";
import { api } from "../lib/api";
import { withoutReservedSmokeTestRecords } from "../lib/reservedSmokeAgenda";
import "../styles/home-pending-actions.css";

type Paciente = { id: number };
type Agendamento = {
  id: number;
  patient_name: string | null;
  starts_at: string;
  appointment_type: string;
  status: string;
};

type Acao = {
  to: string;
  label: string;
  detail: string;
  icon: NomeIcone;
};

function plural(valor: number, singular: string, pluralLabel: string) {
  return `${valor} ${valor === 1 ? singular : pluralLabel}`;
}

export default function HomePendingActionsPortal() {
  const { pathname } = useLocation();
  const [target, setTarget] = useState<HTMLElement | null>(null);
  const [pacientes, setPacientes] = useState<number | null>(null);
  const [agenda, setAgenda] = useState<Agendamento[]>([]);

  useEffect(() => {
    if (pathname !== "/") {
      setTarget(null);
      return;
    }

    function localizar() {
      const elemento = document.querySelector<HTMLElement>(".ccc-home__intelligence");
      if (elemento) setTarget(elemento);
      return Boolean(elemento);
    }

    if (localizar()) return;
    const observer = new MutationObserver(() => {
      if (localizar()) observer.disconnect();
    });
    observer.observe(document.body, { childList: true, subtree: true });
    return () => observer.disconnect();
  }, [pathname]);

  useEffect(() => {
    if (pathname !== "/") return;
    let ativo = true;

    api.get<Paciente[]>("/round/patients")
      .then((items) => { if (ativo) setPacientes(items.length); })
      .catch(() => { if (ativo) setPacientes(null); });

    api.get<Agendamento[]>("/agenda/appointments")
      .then((items) => { if (ativo) setAgenda(withoutReservedSmokeTestRecords(Array.isArray(items) ? items : [])); })
      .catch(() => { if (ativo) setAgenda([]); });

    return () => { ativo = false; };
  }, [pathname]);

  const proximoCompromisso = useMemo(() => {
    const agora = Date.now();
    return agenda
      .filter((item) => !/cancel|cancelad/i.test(item.status || ""))
      .map((item) => ({ ...item, timestamp: new Date(item.starts_at).getTime() }))
      .filter((item) => Number.isFinite(item.timestamp) && item.timestamp > agora)
      .sort((a, b) => a.timestamp - b.timestamp)[0] ?? null;
  }, [agenda]);

  const acoes = useMemo<Acao[]>(() => {
    const linhas: Acao[] = [
      {
        to: "/documentos",
        label: "Documentos e solicitações",
        detail: "Revisar itens que exigem conclusão",
        icon: "documento",
      },
      {
        to: "/round",
        label: pacientes === null ? "Pacientes e round" : plural(pacientes, "paciente no round", "pacientes no round"),
        detail: pacientes === 0 ? "Nenhum paciente pendente no round" : "Abrir acompanhamento clínico",
        icon: "pacientes",
      },
      {
        to: "/receituario",
        label: "Prescrições e pedidos",
        detail: "Continuar produção clínica pendente",
        icon: "prescricao",
      },
    ];

    if (proximoCompromisso) {
      const minutos = Math.max(1, Math.round((proximoCompromisso.timestamp - Date.now()) / 60000));
      linhas.push({
        to: "/agenda",
        label: minutos < 60 ? `Próximo compromisso em ${minutos} min` : `Próximo compromisso às ${new Date(proximoCompromisso.timestamp).toLocaleTimeString("pt-BR", { hour: "2-digit", minute: "2-digit" })}`,
        detail: proximoCompromisso.patient_name || proximoCompromisso.appointment_type || "Ver detalhes na agenda",
        icon: "agenda",
      });
    } else {
      linhas.push({
        to: "/agenda",
        label: "Próximos compromissos",
        detail: "Abrir agenda e rotina do dia",
        icon: "agenda",
      });
    }

    return linhas;
  }, [pacientes, proximoCompromisso]);

  if (pathname !== "/" || !target) return null;

  return createPortal(
    <section className="ccc-rail-card ccc-pending-actions-card" aria-labelledby="ccc-pending-actions-title">
      <header className="ccc-pending-actions-card__header">
        <span id="ccc-pending-actions-title"><Icone nome="check" /> Pendências &amp; Próximas ações</span>
        <Link to="/agenda">Ver agenda</Link>
      </header>
      <div className="ccc-pending-actions-card__list">
        {acoes.map((acao) => (
          <Link to={acao.to} key={`${acao.to}-${acao.label}`} className="ccc-pending-actions-card__item">
            <span className="ccc-pending-actions-card__icon"><Icone nome={acao.icon} /></span>
            <span className="ccc-pending-actions-card__copy"><strong>{acao.label}</strong><small>{acao.detail}</small></span>
            <Icone nome="seta" className="ccc-pending-actions-card__arrow" />
          </Link>
        ))}
      </div>
    </section>,
    target,
  );
}
