import assert from 'node:assert/strict';
import { spawn } from 'node:child_process';
import { mkdtemp, mkdir, readFile, rm, writeFile } from 'node:fs/promises';
import { tmpdir } from 'node:os';
import { join } from 'node:path';
import { createInterface } from 'node:readline';
import { fileURLToPath } from 'node:url';
import test from 'node:test';

const command = fileURLToPath(new URL('../scripts/ask.mjs', import.meta.url));

async function round(t, { rejectActivation = false } = {}) {
  const dir = await mkdtemp(join(tmpdir(), 'grill-open-'));
  const statePath = join(dir, 'browser-state.json');
  const input = join(dir, 'input.json');
  await writeFile(input, JSON.stringify({ title: 'Foreground regression', questions: [
    { id: 'answer', type: 'text', question: 'What should be visible?' },
  ] }));
  const bin = join(dir, 'bin');
  await mkdir(bin);
  await writeFile(statePath, JSON.stringify({ navigations: [], activeURL: null, handedOffURL: null, handedOff: false, appFront: false, externalURLs: [] }));
  // Model the browser-service boundary: navigating a background tab does not select it.
  await writeFile(join(bin, 'ego-browser'), `#!${process.execPath}
const fs = require('node:fs');
const statePath = ${JSON.stringify(statePath)};
const state = JSON.parse(fs.readFileSync(statePath, 'utf8'));
const save = () => fs.writeFileSync(statePath, JSON.stringify(state));
let url;
const page = {label:'p1',
  goto:async value => {url=value; state.navigations.push(value); save();},
  cdp:async method => {
    if(method!=='Page.bringToFront') throw new Error('Unsupported Page command');
    if(${JSON.stringify(rejectActivation)}) throw new Error('Page activation refused');
    state.activeURL=url; save();
  }};
const task = {spaceId:7, page:()=>page, handOff:async()=>{state.handedOff=true;state.handedOffURL=state.activeURL;save();}};
const AsyncFunction = Object.getPrototypeOf(async function(){}).constructor;
new AsyncFunction('taskSpace','listTaskSpaces',process.argv[4])(async()=>task,async()=>[]).catch(error=>{console.error(error);process.exitCode=1;});
`, { mode: 0o755 });
  await writeFile(join(bin, 'open'), `#!${process.execPath}
const fs=require('node:fs');
const path=${JSON.stringify(statePath)};
const state=JSON.parse(fs.readFileSync(path,'utf8'));
state.appFront=process.argv.slice(2).join(' ')==='-b com.citrolabs.ego.lite';
state.externalURLs.push(...process.argv.slice(2).filter(value=>value.startsWith('http')));
fs.writeFileSync(path,JSON.stringify(state));
`, { mode: 0o755 });
  const child = spawn(process.execPath, [command, '--browser', 'ego', '--input', input, '--round-dir', join(dir, 'round'), '--timeout', '10'], {
    env: { ...process.env, PATH: `${bin}:${process.env.PATH}`, AM_NO_UPDATE_CHECK: '1' }, stdio: ['ignore', 'pipe', 'pipe'],
  });
  let stderr = '';
  child.stderr.on('data', chunk => { stderr += chunk; });
  let opened;
  const started = new Promise(resolve => { opened = resolve; });
  const records = [];
  createInterface({ input: child.stdout }).on('line', line => {
    const value = JSON.parse(line);
    records.push(value);
    if (value.event === 'browser_opened') opened(value);
  });
  const done = new Promise(resolve => child.on('close', code => { opened(undefined); resolve({ code, stderr }); }));
  t.after(async () => {
    if (child.exitCode === null) child.kill();
    await done;
    await rm(dir, { recursive: true, force: true });
  });
  const browser = await started;
  assert.ok(browser, stderr);
  const ready = records.find(value => value.event === 'ready');
  return { browser, ready, done, records, state: () => readFile(statePath, 'utf8').then(JSON.parse) };
}

test('the SDK opener selects the round tab before user handoff and foregrounds Ego without a duplicate URL', { timeout: 15000 }, async t => {
  const run = await round(t);
  assert.equal(run.browser.driver, 'ego', 'The browser-service fixture must execute the actual managed opener.');
  assert.equal(run.browser.warning, undefined);
  const state = await run.state();
  assert.equal(state.handedOffURL, run.ready.url, 'The user must receive the selected round tab, not a background tab.');
  assert.deepEqual(state.navigations, [run.ready.url]);
  assert.deepEqual(state.externalURLs, [], 'Foreground the existing application without opening a second copy of the form.');
  if (process.platform === 'darwin') assert.equal(state.appFront, true, 'The existing Ego app must be brought to the foreground.');
});

test('an activation failure reports the visibility problem, preserves the existing page and still accepts answers', { timeout: 15000 }, async t => {
  const run = await round(t, { rejectActivation: true });
  assert.equal(run.browser.driver, 'ego');
  assert.match(run.browser.warning, /foreground|activat/i, 'Do not present an activation failure as a confirmed visible page.');
  const state = await run.state();
  assert.equal(state.handedOff, false, 'An activation refusal must stop further browser commands, including handoff.');
  assert.deepEqual(state.navigations, [run.ready.url]);
  assert.deepEqual(state.externalURLs, []);
  const current = await fetch(new URL('state', run.ready.url)).then(response => response.json());
  const response = await fetch(new URL('submit', run.ready.url), { method: 'POST', headers: { 'content-type': 'application/json' },
    body: JSON.stringify({ requestHash: current.requestHash, submissionId: 'after-activation-failure',
      answers: [{ questionId: 'answer', picked: [], text: 'The original form still works.', skipped: false }] }) });
  assert.equal(response.status, 200);
  assert.equal((await run.done).code, 0);
  assert.equal(run.records.at(-1).answers[0].text, 'The original form still works.');
});
