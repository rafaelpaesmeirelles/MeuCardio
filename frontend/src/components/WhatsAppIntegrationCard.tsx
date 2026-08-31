import { useEffect, useState } from "react";
import { Link } from "react-router-dom";
import { api } from "../lib/api";
import type { WhatsAppLinkStatus } from "../types/clinicalAI";
import ClinicalAIStatusBadge from "./ClinicalAIStatusBadge";
import Icone from "./Icone";

export default function WhatsAppIntegrationCard() {
  const [link, setLink] = useState<WhatsAppLinkStatus | null>(null); const [error, setError] = useState(false);
  useEffect(() => { api.get<WhatsAppLinkStatus>("/whatsapp-assistant").then(setLink).catch(() => setError(true)); }, []);
  return <section className="cartao cai-account-integration"><span className="cai-account-integration__icon"><Icone nome="comunicacao" /></span><div><p className="eyebrow">Integrações</p><h2>Assistente pelo WhatsApp</h2><p>{error ? "A integração está indisponível neste momento." : link?.connected ? `Conectado com segurança · ${link.phone_masked ?? "número protegido"}` : "Conecte um número Business dedicado com permissões granulares."}</p></div><ClinicalAIStatusBadge status={link?.connected ? "accepted" : "draft"} label={link?.connected ? "Conectado" : "Não conectado"} /><Link className="cai-button cai-button--ghost" to="/whatsapp-assistant">{link?.connected ? "Gerenciar" : "Conectar com segurança"}<Icone nome="seta" /></Link></section>;
}
