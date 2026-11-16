import { randomBytes } from 'node:crypto';
import { createServer } from 'node:http';
import { readFileSync } from 'node:fs';

export async function serveRound(round, { timeoutMs, pageHtml }) {
  const assets = new Map([
    ['', ['text/html', readFileSync(new URL('./ui/index.html', import.meta.url), 'utf8')]],
    ['ui.js', ['text/javascript', readFileSync(new URL('./ui/ui.js', import.meta.url), 'utf8')]],
    ['ui.css', ['text/css', readFileSync(new URL('./ui/ui.css', import.meta.url), 'utf8')]],
    ['page', ['text/html', pageHtml]],
  ]);
  const prefix = `/${randomBytes(24).toString('hex')}/`;
  let complete;
  let settled = false;
  const finished = new Promise((resolve) => { complete = (value) => { if (!settled) { settled = true; resolve(value); } }; });
  const server = createServer(async (req, res) => {
    const send = (status, value) => {
      if (res.destroyed) return;
      res.writeHead(status, { 'content-type': 'application/json; charset=utf-8', 'cache-control': 'no-store' });
      res.end(JSON.stringify(value));
    };
    if (!req.url.startsWith(prefix)) return send(404, { error: 'Not found' });
    const route = req.url.slice(prefix.length);
    try {
      if (req.method === 'GET' && assets.has(route)) {
        const [type, content] = assets.get(route);
        const headers = { 'content-type': `${type}; charset=utf-8`, 'cache-control': 'no-store', 'x-content-type-options': 'nosniff' };
        if (route === '') headers['content-security-policy'] = "default-src 'none'; script-src 'self'; style-src 'self'; frame-src 'self'; connect-src 'self'; frame-ancestors 'none'; base-uri 'none'";
        res.writeHead(200, headers);
        return res.end(content);
      }
      if (req.method === 'GET' && route === 'state') return send(200, round.state());
      if (settled && !round.state().result) return send(409, { error: 'This wait has already finished.' });
      if ((req.method === 'POST' && ['submit', 'cancel'].includes(route)) || (req.method === 'PUT' && route === 'draft')) {
        const chunks = [];
        let bytes = 0;
        for await (const chunk of req) {
          bytes += chunk.length;
          if (bytes > 256 * 1024) return send(413, { error: 'The answer is too large.' });
          chunks.push(chunk);
        }
        if (settled && !round.state().result) return send(409, { error: 'This wait has already finished.' });
        const body = JSON.parse(Buffer.concat(chunks).toString('utf8'));
        if (route === 'draft') return send(200, round.saveDraft(body));
        const result = route === 'cancel' ? round.cancel(body) : round.submit(body);
        send(200, result);
        res.once('finish', () => complete(result));
        return;
      }
      send(404, { error: 'Not found' });
    } catch (error) {
      send(error.status ?? 400, { error: error.message });
    }
  });
  await new Promise((resolve, reject) => {
    server.once('error', reject);
    server.listen(0, '127.0.0.1', resolve);
  });
  const timer = setTimeout(() => complete({ status: 'timed_out', requestHash: round.state().requestHash }), timeoutMs);
  return { url: `http://127.0.0.1:${server.address().port}${prefix}`, finished,
    close: () => new Promise((resolve) => { clearTimeout(timer); server.close(resolve); server.closeAllConnections(); }) };
}
