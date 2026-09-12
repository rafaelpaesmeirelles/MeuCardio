import { useEffect } from "react";
import { Navigate, useLocation } from "react-router-dom";
import { clearLoginReturn, saveLoginReturn } from "../lib/loginReturn";

export function LoginRedirect() {
  const location = useLocation();
  const destination = location.pathname + location.search + location.hash;
  useEffect(() => { saveLoginReturn(destination); }, [destination]);
  return <Navigate to="/entrar" replace />;
}

export function ResumeLogin({ destination }: { destination: string }) {
  useEffect(() => { clearLoginReturn(); }, []);
  return <Navigate to={destination} replace />;
}
