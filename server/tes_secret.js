const WebSocket = require('ws');
const URL = 'ws://localhost:3000';
const a = new WebSocket(URL), b = new WebSocket(URL);
a.on('open', () => a.send(JSON.stringify({ t: 'join', name: 'TesterA', gender: 'm' })));
b.on('open', () => b.send(JSON.stringify({ t: 'join', name: 'TesterB', gender: 'f' })));
b.on('message', d => {
  const m = JSON.parse(d);
  if (m.t === 'welcome') setTimeout(() => a.send(JSON.stringify({ t: 'secret', id: 'megalodon', w: 123.4, mut: '' })), 500);
  if (m.t === 'secret') { console.log('✅ B TERIMA NOTIF:', m); process.exit(0); }
});
setTimeout(() => { console.log('❌ B tidak menerima notif Secret'); process.exit(1); }, 4000);
