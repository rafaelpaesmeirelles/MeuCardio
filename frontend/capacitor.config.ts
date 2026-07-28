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
  // O appId NÃO acompanha o rebrand: trocar o identificador do pacote cria
  // um aplicativo NOVO na loja — instalações, avaliações e histórico ficam
  // no antigo, e quem já tem o app não recebe atualização nenhuma. É
  // identificador técnico, invisível ao usuário. appId permanece.
  appId: "br.med.meucardio",
  appName: "Corvia",
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
