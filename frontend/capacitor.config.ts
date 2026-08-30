import type { CapacitorConfig } from "@capacitor/cli";

/**
 * Empacotamento móvel: o mesmo build web roda em Android e iOS.
 * Nada do frontend precisa ser reescrito.
 *
 *   npm i -D @capacitor/cli && npm i @capacitor/core @capacitor/android @capacitor/ios
 *   npx cap add android && npx cap add ios
 *   npm run sync:mobile
 */
const config: CapacitorConfig = {
  // O appId acompanha o rebrand. Ele NÃO é invisível como parece: aparece na
  // URL da loja (play.google.com/store/apps/details?id=…), e a marca anterior
  // está registrada por outro titular — o mesmo motivo que levou a desligar o
  // domínio antigo.
  //
  // O custo é real e foi aceito com conhecimento: identificador novo é
  // aplicativo NOVO na loja. Instalações, avaliações e histórico ficam no
  // antigo, e quem tem a versão velha não recebe atualização — precisa
  // instalar de novo. A troca foi feita agora justamente porque o app está
  // sendo gerado do zero: adiar só aumentaria a base a migrar.
  appId: "br.med.corvia",
  appName: "CorVIA Cardiology Spaces",
  webDir: "dist",
  server: {
    // O app carrega o site ao vivo, não um build congelado dentro do pacote.
    // Vantagem: atualizar o site atualiza o app pra todo mundo, sem passar
    // de novo pela loja. Desvantagem: sem internet, o app não abre (dá pra
    // resolver depois com um modo offline dedicado, se precisar).
    url: "https://corvia.med.br",
    androidScheme: "https",
    cleartext: false,
  },
  ios: { contentInset: "always" },
};

export default config;
