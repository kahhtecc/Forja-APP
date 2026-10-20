// Funciona offline depois da primeira visita: guarda o app e o que for sendo aberto (imagens, animações).
// A versão (VERSAO) é trocada pelo workflow a cada publicação, renovando o cache.
const VERSAO = "forja-dev";
const BASICO = ["./", "index.html", "dados.json", "exercicios.json", "video3d/meta.json", "manifest.webmanifest", "icone-192.png"];

self.addEventListener("install", e => {
  e.waitUntil(caches.open(VERSAO).then(c => c.addAll(BASICO).catch(() => {})).then(() => self.skipWaiting()));
});
self.addEventListener("activate", e => {
  e.waitUntil(caches.keys().then(ks => Promise.all(ks.filter(k => k !== VERSAO).map(k => caches.delete(k)))).then(() => self.clients.claim()));
});
self.addEventListener("fetch", e => {
  const req = e.request;
  if (req.method !== "GET") return;
  const url = new URL(req.url);
  const dados = url.origin === location.origin && /\.(json|html)$|\/$/.test(url.pathname);
  if (dados) {
    // dados e página: rede primeiro (pega atualizações), cache se estiver offline
    e.respondWith(fetch(req).then(r => { const c = r.clone(); caches.open(VERSAO).then(x => x.put(req, c)); return r; }).catch(() => caches.match(req)));
  } else {
    // imagens, animações e fontes: cache primeiro
    e.respondWith(caches.match(req).then(h => h || fetch(req).then(r => {
      if (r.ok || r.type === "opaque") { const c = r.clone(); caches.open(VERSAO).then(x => x.put(req, c)); }
      return r;
    })));
  }
});
