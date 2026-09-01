import { Navigate, useLocation } from "react-router-dom";

/** Alias histórico: existe apenas para preservar links e converge no tour único. */
export default function TourAlias() {
  const location = useLocation();
  return <Navigate replace to={{ pathname: "/tour", search: location.search, hash: location.hash }} />;
}
