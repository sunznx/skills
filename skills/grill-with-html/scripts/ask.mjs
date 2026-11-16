#!/usr/bin/env node
import { readFileSync } from 'node:fs';
import { parseArgs } from 'node:util';
import { resolve } from 'node:path';
import { setTimeout as delay } from 'node:timers/promises';
import { fileURLToPath } from 'node:url';
import { acquireRound, createRound } from './round.mjs';
import { serveRound } from './server.mjs';
import { renderRound } from './render.mjs';
import { openRoundPage, finishRoundPage } from './browser.mjs';

const print = (value) => process.stdout.write(`${JSON.stringify(value)}\n`);
let release = () => {};

try {
  const { values } = parseArgs({ options: {
    input: { type: 'string' }, 'round-dir': { type: 'string' }, 'no-open': { type: 'boolean' }, 'keep-open': { type: 'boolean' },
    timeout: { type: 'string', default: '1800' },
    renderer: { type: 'string', default: fileURLToPath(new URL('../../answer-me-with-html/scripts/am.mjs', import.meta.url)) },
  } });
  if (!values.input || !values['round-dir']) throw new Error('--input and --round-dir are required.');
  const timeoutMs = Number(values.timeout) * 1000;
  if (!Number.isFinite(timeoutMs) || timeoutMs <= 0 || timeoutMs > 86400000) throw new Error('--timeout must be between 0 and 86400 seconds.');
  release = acquireRound(resolve(values['round-dir']));
  process.once('exit', release);
  process.once('SIGINT', () => process.exit(130));
  process.once('SIGTERM', () => process.exit(143));
  const round = createRound(JSON.parse(readFileSync(resolve(values.input), 'utf8')), resolve(values['round-dir']));
  if (round.state().result) {
    print(round.state().result);
    if (round.state().result.status === 'cancelled') process.exitCode = 3;
  } else {
    const pageHtml = renderRound(round.state().input, resolve(values['round-dir']), resolve(values.renderer));
    const server = await serveRound(round, { timeoutMs, pageHtml });
    print({ event: 'ready', url: server.url });
    let browser;
    if (!values['no-open']) {
      browser = await openRoundPage(server.url, resolve(values['round-dir']));
      print({ event: 'browser_opened', ...browser });
      if (browser.reason || browser.warning) console.error(browser.reason ?? browser.warning);
    }
    const result = await server.finished;
    // Keep the receipt available briefly for a duplicate click or a lost response.
    await delay(400);
    await server.close();
    if (browser) print({ event: 'browser_cleanup', ...await finishRoundPage(browser,
      { status: result.status, keepOpen: values['keep-open'] ?? false }) });
    print(result);
    if (result.status === 'cancelled') process.exitCode = 3;
    if (result.status === 'timed_out') process.exitCode = 2;
  }
} catch (error) {
  console.error(error.message);
  process.exitCode = 1;
} finally {
  release();
}
