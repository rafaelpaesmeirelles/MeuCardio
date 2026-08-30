import { Outlet, useLocation } from "react-router-dom";
import { cardiologySpacesEnabled } from "../lib/cardiologySpacesFeature";
import ClinicalDesktopNav from "./ClinicalDesktopNav";
import ClinicalMobileNav from "./ClinicalMobileNav";
import ClinicalPresentationGuard from "./ClinicalPresentationGuard";
import ClinicalRouteContext from "./ClinicalRouteContext";
import HomePendingActionsPortal from "./HomePendingActionsPortal";
import InvestorDemoBanner from "./InvestorDemoBanner";
import ShellClinicalOSLaunch from "./ShellClinicalOSLaunch";
import "../styles/canonical-brand-standard.css";

export default function Shell() {
  const { pathname } = useLocation();
  const spacesHome = pathname === "/" && cardiologySpacesEnabled();

  return (
    <>
      <ClinicalRouteContext />
      {spacesHome ? (
        <Outlet />
      ) : (
        <>
          <ClinicalDesktopNav />
          <HomePendingActionsPortal />
          <ShellClinicalOSLaunch />
          <ClinicalMobileNav />
        </>
      )}
      <ClinicalPresentationGuard />
      <InvestorDemoBanner />
    </>
  );
}
