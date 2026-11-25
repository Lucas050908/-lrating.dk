const { contextBridge, ipcRenderer } = require('electron');
contextBridge.exposeInMainWorld('OlratingApp', {
  updateWidget: (json) => ipcRenderer.send('widget-data', String(json)),
  isApp: () => true,
  platform: () => 'desktop'
});
