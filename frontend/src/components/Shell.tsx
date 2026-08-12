import ClinicalDesktopNav from "./ClinicalDesktopNav";
import ClinicalMobileNav from "./ClinicalMobileNav";
import ClinicalPresentationGuard from "./ClinicalPresentationGuard";
import ShellClinicalOSLaunch from "./ShellClinicalOSLaunch";

export default function Shell() {
  return (
    <>
      <ClinicalDesktopNav />
      <ShellClinicalOSLaunch />
      <ClinicalMobileNav />
      <ClinicalPresentationGuard />
    </>
  );
}
