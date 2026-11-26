const { contextBridge, ipcRenderer } = require('electron');
contextBridge.exposeInMainWorld('W', {
  onData: (fn) => ipcRenderer.on('data', (_e, d) => fn(d)),
  onImages: (fn) => ipcRenderer.on('images', (_e, d) => fn(d)),
  open: (hash) => ipcRenderer.send('widget-open', hash || ''),
  close: () => ipcRenderer.send('widget-close'),
  pin: (on) => ipcRenderer.send('widget-pin', on),
  addUnit: () => ipcRenderer.send('units-add')
});
