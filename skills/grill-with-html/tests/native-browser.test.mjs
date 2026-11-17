import assert from 'node:assert/strict';
import { spawn, execFileSync } from 'node:child_process';
import { mkdtemp, readFile, rm, writeFile } from 'node:fs/promises';
import { tmpdir } from 'node:os';
import { join } from 'node:path';
import { fileURLToPath } from 'node:url';
import { createInterface } from 'node:readline';
import test from 'node:test';

const command = fileURLToPath(new URL('../scripts/ask.mjs', import.meta.url));
const native = source => JSON.parse(execFileSync('osascript', ['-l', 'JavaScript', '-e', source], { encoding: 'utf8', timeout: 10000 }));
const app = 'const app=Application("com.citrolabs.ego.lite");';
const find = url => `${app} JSON.stringify(app.windows().flatMap(w=>w.tabs.url().flatMap((value,index)=>value===${JSON.stringify(url)}?[{windowId:w.id(),tabId:w.tabs[index].id(),visible:w.visible(),selected:w.activeTab().id()===w.tabs[index].id(),frontmost:app.frontmost(),frontWindow:app.windows()[0].id()===w.id()}]:[])))`;

async function round(t, extra = []) {
  const dir = await mkdtemp(join(tmpdir(), 'grill-native-'));
  const input = join(dir, 'input.json');
  await writeFile(input, JSON.stringify({ title: 'Native visibility regression', questions: [
    { id: 'q1', type: 'text', question: 'Synthetic native browser test' },
  ] }));
  const child = spawn(process.execPath, [command, '--input', input, '--round-dir', join(dir, 'round'), '--timeout', '45', ...extra], {
    env: { ...process.env, AM_NO_UPDATE_CHECK: '1' }, stdio: ['ignore', 'pipe', 'pipe'],
  });
  let resolveOpened;
  const opened = new Promise(resolve => { resolveOpened = resolve; });
  const records = [];
  let stderr = '';
  child.stderr.on('data', chunk => { stderr += chunk; });
  createInterface({ input: child.stdout }).on('line', line => {
    const value = JSON.parse(line); records.push(value);
    if (value.event === 'browser_opened') resolveOpened(value);
  });
  const done = new Promise(resolve => child.on('close', code => { resolveOpened(undefined); resolve({ code, stderr }); }));
  t.after(async () => {
    if (child.exitCode === null) child.kill();
    await done;
    const browser = records.find(r => r.event === 'browser_opened');
    const ready = records.find(r => r.event === 'ready');
    // Clean only this synthetic capability URL; never user rounds or other tabs.
    if (ready) native(`${app} app.windows().forEach(w=>w.tabs.url().forEach((url,index)=>{if(url===${JSON.stringify(ready.url)})w.tabs[index].close();})); JSON.stringify(true)`);
    if (browser?.driver === 'ego') execFileSync('ego-browser', ['nodejs', '-e', `const e=(await listTaskSpaces()).find(s=>s.id===${JSON.stringify(browser.spaceId)});if(e){const t=e.ownership==="agentDelegatedToUser"?await takeOverTaskSpace(e.id):await taskSpace(e.id);await t.finish({keep:[]});}`]);
    await rm(dir, { recursive: true, force: true });
  });
  const browser = await opened;
  assert.ok(browser, stderr);
  return { browser, records, done, dir, url: records.find(r => r.event === 'ready').url };
}

async function submit(run) {
  const state = await fetch(new URL('state', run.url)).then(r => r.json());
  const response = await fetch(new URL('submit', run.url), { method: 'POST', headers: { 'content-type': 'application/json' },
    body: JSON.stringify({ requestHash: state.requestHash, submissionId: 'native-test',
      answers: [{ questionId: 'q1', picked: [], text: 'Synthetic answer', skipped: false }] }) });
  assert.equal(response.status, 200);
  const result = await run.done;
  assert.equal(result.code, 0, result.stderr);
}

test('default open reveals the actual native tab and submission removes that same tab', { skip: process.platform !== 'darwin', timeout: 60000 }, async t => {
  const run = await round(t);
  assert.equal(run.browser.warning, undefined, JSON.stringify(run.browser));
  const tabs = native(find(run.url));
  assert.equal(tabs.length, 1, 'The default opener must create one actual native tab, not an invisible SDK page.');
  assert.equal(tabs[0].visible && tabs[0].selected && tabs[0].frontmost && tabs[0].frontWindow, true,
    'The round must be selected in the foreground native window.');
  assert.equal(String(run.browser.tabId), String(tabs[0].tabId));
  await submit(run);
  const cleanup = run.records.find(r => r.event === 'browser_cleanup');
  assert.equal(cleanup?.status, 'closed', JSON.stringify(cleanup));
  assert.deepEqual(native(find(run.url)), [], 'A closed receipt must match actual tab disappearance.');
  const answers = JSON.parse(await readFile(join(run.dir, 'round', 'answers.json'), 'utf8'));
  assert.equal(answers.answers[0].text, 'Synthetic answer');
});

test('keep-open retains the actual submitted native tab', { skip: process.platform !== 'darwin', timeout: 60000 }, async t => {
  const run = await round(t, ['--keep-open']);
  await submit(run);
  assert.equal(run.records.find(r => r.event === 'browser_cleanup')?.reason, 'requested');
  assert.equal(native(find(run.url)).length, 1);
});

test('cleanup retains a native tab that has navigated away', { skip: process.platform !== 'darwin', timeout: 60000 }, async t => {
  const run = await round(t);
  const away = `about:blank#grill-navigation-${run.browser.tabId}`;
  native(`${app} const w=app.windows().find(w=>String(w.id())===${JSON.stringify(run.browser.windowId)});w.activeTab().url=${JSON.stringify(away)};JSON.stringify(true)`);
  t.after(() => native(`${app} app.windows().forEach(w=>w.tabs.url().forEach((url,index)=>{if(url===${JSON.stringify(away)})w.tabs[index].close();}));JSON.stringify(true)`));
  await submit(run);
  assert.equal(run.records.find(r => r.event === 'browser_cleanup')?.reason, 'page navigated');
  assert.equal(native(find(away)).length, 1);
});

test('cleanup closes its own tab but reports and preserves another copy of the form', { skip: process.platform !== 'darwin', timeout: 60000 }, async t => {
  const run = await round(t);
  // Model the user opening the ready link separately, without touching any actual user round.
  native(`${app} const w=app.Window().make();w.activeTab().url=${JSON.stringify(run.url)};JSON.stringify(true)`);
  await submit(run);
  const cleanup = run.records.find(r => r.event === 'browser_cleanup');
  assert.equal(cleanup?.status, 'kept');
  assert.equal(cleanup.managedClosed, true);
  assert.equal(cleanup.retainedCopies, 1);
  const tabs = native(find(run.url));
  assert.equal(tabs.length, 1);
  assert.notEqual(String(tabs[0].tabId), run.browser.tabId, 'A separate user-opened copy is outside the managed tab.');
});
