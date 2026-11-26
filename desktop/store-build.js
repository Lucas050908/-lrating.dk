// Bygger pakken til Microsoft Store (.appx) ud fra værdierne i store.json.
// Er de tre værdier fra Partner Center ikke udfyldt, bygges en prøvepakke med testværdier,
// så vi kan se, at bygningen virker. Prøvepakken kan ikke uploades til Store.
const fs = require('fs'), path = require('path');
const builder = require('electron-builder');
const pkg = require('./package.json');
const s = JSON.parse(fs.readFileSync(path.join(__dirname, 'store.json'), 'utf8'));
const txt = k => (typeof s[k] === 'string' ? s[k].trim() : '');
const real = !!(txt('identityName') && txt('publisher') && txt('publisherDisplayName'));
if (real && !/^CN=/.test(txt('publisher'))) { console.error('FEJL: "publisher" i store.json skal starte med CN='); process.exit(1); }
const appx = {
  applicationId: 'olrating',
  displayName: txt('displayName') || 'ølrating',
  backgroundColor: '#0f1d36',
  languages: ['da-DK'],
  identityName: real ? txt('identityName') : 'olrating.test',
  publisher: real ? txt('publisher') : 'CN=olrating-test',
  publisherDisplayName: real ? txt('publisherDisplayName') : 'olrating test'
};
const artifactName = real ? 'olrating-store.appx' : 'olrating-store-TEST.appx';
console.log(real ? 'Bygger pakken til Microsoft Store med værdierne fra store.json' : 'store.json er ikke udfyldt: bygger en prøvepakke med testværdier');
builder.build({
  targets: builder.Platform.WINDOWS.createTarget('appx'),
  publish: 'never',
  config: { ...pkg.build, appx, win: { ...pkg.build.win, target: 'appx', artifactName } }
}).then(() => console.log('Færdig: dist/' + artifactName)).catch(e => { console.error(e); process.exit(1); });
