"use strict";

const { app, BrowserWindow, session, shell } = require("electron");

const APP_ORIGIN = "https://corvia.med.br";

function isTrusted(url) {
  try { return new URL(url).origin === APP_ORIGIN; } catch { return false; }
}

function createWindow() {
  const win = new BrowserWindow({
    width: 1440,
    height: 960,
    minWidth: 390,
    minHeight: 640,
    backgroundColor: "#030914",
    title: "CorVIA Cardiology Spaces",
    icon: `${__dirname}/build/corvia.ico`,
    webPreferences: {
      nodeIntegration: false,
      contextIsolation: true,
      sandbox: true,
      webSecurity: true,
      allowRunningInsecureContent: false,
    },
  });

  win.webContents.on("will-navigate", (event, url) => {
    if (!isTrusted(url)) event.preventDefault();
  });
  win.webContents.setWindowOpenHandler(({ url }) => {
    if (isTrusted(url)) win.loadURL(url);
    else if (url.startsWith("https://")) void shell.openExternal(url);
    return { action: "deny" };
  });
  void win.loadURL(APP_ORIGIN);
}

app.setAppUserModelId("br.med.corvia.desktop");
app.whenReady().then(() => {
  session.defaultSession.setPermissionRequestHandler((_contents, permission, callback) => {
    callback(permission === "notifications");
  });
  createWindow();
  app.on("activate", () => { if (BrowserWindow.getAllWindows().length === 0) createWindow(); });
});
app.on("window-all-closed", () => { if (process.platform !== "darwin") app.quit(); });
