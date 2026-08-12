import ShellClinicalOSLaunch from "./ShellClinicalOSLaunch";
import ClinicalMobileNav from "./ClinicalMobileNav";
import ClinicalPresentationGuard from "./ClinicalPresentationGuard";

export default function Shell() {
  return (
    <>
      <ShellClinicalOSLaunch />
      <ClinicalMobileNav />
      <ClinicalPresentationGuard />
    </>
  );
}
