const { contextBridge, ipcRenderer } = require('electron');
contextBridge.exposeInMainWorld('OlratingApp', {
  updateWidget: (json) => ipcRenderer.send('widget-data', String(json)),
  takeUnits: () => ipcRenderer.sendSync('units-take'),
  isApp: () => true,
  platform: () => 'desktop'
});
