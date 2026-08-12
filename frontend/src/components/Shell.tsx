import ClinicalDesktopNav from "./ClinicalDesktopNav";
import ClinicalMobileNav from "./ClinicalMobileNav";
import ClinicalPresentationGuard from "./ClinicalPresentationGuard";
import ClinicalRouteContext from "./ClinicalRouteContext";
import ShellClinicalOSLaunch from "./ShellClinicalOSLaunch";

export default function Shell() {
  return (
    <>
      <ClinicalRouteContext />
      <ClinicalDesktopNav />
      <ShellClinicalOSLaunch />
      <ClinicalMobileNav />
      <ClinicalPresentationGuard />
    </>
  );
}
