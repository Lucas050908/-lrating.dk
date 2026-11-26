// ølrating til Windows og Linux: hjemmesiden i et eget vindue + en lille widget, der kan ligge øverst.
const { app, BrowserWindow, ipcMain, shell, Menu, Tray, nativeImage, screen } = require('electron');
const path = require('path');
const fs = require('fs');

const SITE = 'https://xn--lrating-p1a.dk/';
const HOSTS = ['lucas050908.github.io', 'xn--lrating-p1a.dk', 'www.xn--lrating-p1a.dk'];
const ICON = path.join(__dirname, 'build', 'icon.png');
let win, widget, tray, lastData = null, lastImgs = {};

const stateFile = () => path.join(app.getPath('userData'), 'widget.json');
function loadState() { try { return JSON.parse(fs.readFileSync(stateFile(), 'utf8')); } catch (e) { return {}; } }
function saveState(s) { try { fs.writeFileSync(stateFile(), JSON.stringify(s)); } catch (e) {} }
// Små billeder af øllene til widgetten. De ligger i deres egen fil, så de kun skrives, når de ændrer sig.
const imgFile = () => path.join(app.getPath('userData'), 'widget-images.json');
function cleanImgs(o) {
  const out = {}; let n = 0;
  for (const [k, v] of Object.entries(o && typeof o === 'object' ? o : {})) {
    if (n >= 12) break;
    if (/^[\w-]{1,40}$/.test(k) && typeof v === 'string' && v.startsWith('data:image/jpeg;base64,') && v.length < 90000) { out[k] = v; n++; }
  }
  return out;
}
function loadImgs() { try { return cleanImgs(JSON.parse(fs.readFileSync(imgFile(), 'utf8'))); } catch (e) { return {}; } }

function isOurs(url) { try { return HOSTS.includes(new URL(url).hostname); } catch (e) { return false; } }

function createMain(hash) {
  win = new BrowserWindow({
    width: 1200, height: 850, minWidth: 380, minHeight: 500,
    backgroundColor: '#0F1D36', icon: ICON, title: 'ølrating',
    autoHideMenuBar: true,
    webPreferences: { preload: path.join(__dirname, 'preload.js'), contextIsolation: true, nodeIntegration: false, sandbox: true }
  });
  win.loadURL(SITE + (hash || ''));
  // Links ud af siden åbnes i den almindelige browser
  win.webContents.setWindowOpenHandler(({ url }) => { if (!isOurs(url)) shell.openExternal(url); return { action: 'deny' }; });
  win.webContents.on('will-navigate', (e, url) => { if (!isOurs(url)) { e.preventDefault(); shell.openExternal(url); } });
  win.on('closed', () => { win = null; });
}

function showMain(hash) {
  if (!win) return createMain(hash);
  if (hash !== undefined) win.loadURL(SITE + hash);
  if (win.isMinimized()) win.restore();
  win.show(); win.focus();
}

function createWidget() {
  if (widget) { widget.show(); return; }
  const st = loadState(), wa = screen.getPrimaryDisplay().workArea;
  widget = new BrowserWindow({
    width: 360, height: 300,
    x: st.x ?? wa.x + wa.width - 380, y: st.y ?? wa.y + 20,
    frame: false, resizable: false, transparent: true, skipTaskbar: true,
    alwaysOnTop: st.onTop !== false, icon: ICON, show: false,
    webPreferences: { preload: path.join(__dirname, 'widget-preload.js'), contextIsolation: true, nodeIntegration: false, sandbox: true }
  });
  widget.loadFile(path.join(__dirname, 'widget.html'));
  widget.once('ready-to-show', () => { widget.showInactive(); widget.webContents.send('images', lastImgs); if (lastData) widget.webContents.send('data', lastData); });
  widget.on('moved', () => { const [x, y] = widget.getPosition(); saveState({ ...loadState(), x, y, open: true }); });
  widget.on('closed', () => { widget = null; });
  saveState({ ...loadState(), open: true });
}

function closeWidget() { if (widget) widget.close(); saveState({ ...loadState(), open: false }); }

// Hjemmesiden kalder window.OlratingApp.updateWidget(json) – samme bro som Android-appen
ipcMain.on('widget-data', (_e, json) => {
  if (typeof json !== 'string' || json.length > 20000) return;
  try { lastData = JSON.parse(json); } catch (e) { return; }
  saveState({ ...loadState(), data: lastData });
  if (widget) widget.webContents.send('data', lastData);
  if (tray) tray.setToolTip(lastData.week ? `Ugens øl: ${lastData.week.name} (${lastData.week.score})` : 'ølrating');
});
// Hjemmesiden sender små billeder af de øl, widgetten viser: {"øl-id": "data:image/jpeg;base64,…"}
ipcMain.on('widget-images', (_e, json) => {
  if (typeof json !== 'string' || json.length > 900000) return;
  try { lastImgs = cleanImgs(JSON.parse(json)); } catch (e) { return; }
  try { fs.writeFileSync(imgFile(), JSON.stringify(lastImgs)); } catch (e) {}
  if (widget) widget.webContents.send('images', lastImgs);
});
ipcMain.on('widget-open', (_e, hash) => showMain(typeof hash === 'string' && /^#[\w-]*$/.test(hash) ? hash : ''));
ipcMain.on('widget-close', closeWidget);
// Genstande fra widgetten: gemmes, til siden henter dem (den spørger hvert 5. sekund)
let pendingUnits = (loadState().pending || []);
ipcMain.on('units-add', () => {
  pendingUnits.push(Date.now()); saveState({ ...loadState(), pending: pendingUnits });
  if (lastData && lastData.units) { lastData.units.todayN = (lastData.units.todayN || 0) + 1; lastData.units.weekN = (lastData.units.weekN || 0) + 1; if (widget) widget.webContents.send('data', lastData); }
});
ipcMain.on('units-take', (e) => { e.returnValue = JSON.stringify(pendingUnits); pendingUnits = []; saveState({ ...loadState(), pending: [] }); });
ipcMain.on('widget-pin', (_e, on) => { if (widget) widget.setAlwaysOnTop(!!on); saveState({ ...loadState(), onTop: !!on }); });

function buildTray() {
  tray = new Tray(nativeImage.createFromPath(ICON).resize({ width: 16, height: 16 }));
  tray.setToolTip('ølrating');
  tray.setContextMenu(Menu.buildFromTemplate([
    { label: 'Åbn ølrating', click: () => showMain() },
    { label: 'Bedøm en øl', click: () => showMain('#tilfoej') },
    { label: 'Vis widget', click: createWidget },
    { label: 'Skjul widget', click: closeWidget },
    { type: 'separator' },
    { label: 'Afslut', role: 'quit' }
  ]));
  tray.on('click', () => showMain());
}

if (!app.requestSingleInstanceLock()) app.quit();
else {
  app.on('second-instance', () => showMain());
  app.whenReady().then(() => {
    Menu.setApplicationMenu(null);
    const st = loadState(); lastData = st.data || null; lastImgs = loadImgs();
    createMain();
    try { buildTray(); } catch (e) { /* nogle Linux-skriveborde har ingen bakke */ }
    if (st.open !== false) createWidget();
  });
  app.on('window-all-closed', () => { if (!tray) app.quit(); });
}
