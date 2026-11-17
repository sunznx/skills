import assert from 'node:assert/strict';
import { spawn, execFileSync } from 'node:child_process';
import { mkdtemp, writeFile, readFile, rm, mkdir } from 'node:fs/promises';
import { tmpdir } from 'node:os';
import { join } from 'node:path';
import { fileURLToPath } from 'node:url';
import { createInterface } from 'node:readline';
import test from 'node:test';

const command = fileURLToPath(new URL('../scripts/ask.mjs', import.meta.url));

async function submittedRound(t, { extra = [], arrange } = {}) {
  const dir = await mkdtemp(join(tmpdir(), 'grill-close-'));
  t.after(() => rm(dir, { recursive: true, force: true }));
  const input = join(dir, 'input.json');
  await writeFile(input, JSON.stringify({ title: 'Automatic close regression', questions: [
    { id: 'q1', type: 'text', question: 'Enter the test answer.' },
  ] }));
  // Prevent the old system-opener path from creating an unmanaged test tab.
  const bin = join(dir, 'bin');
  await mkdir(bin);
  for (const name of ['open', 'xdg-open']) await writeFile(join(bin, name), '#!/bin/sh\nexit 0\n', { mode: 0o755 });
  const child = spawn(process.execPath, [command, '--browser', 'ego', '--input', input, '--round-dir', join(dir, 'round'), '--timeout', '30', ...extra], {
    env: { ...process.env, PATH: `${bin}:${process.env.PATH}`, AM_NO_UPDATE_CHECK: '1' }, stdio: ['ignore', 'pipe', 'pipe'],
  });
  t.after(() => { if (child.exitCode === null) child.kill(); });
  const records = [];
  let stderr = '';
  child.stderr.on('data', (s) => { stderr += s; });
  let resolveOpened;
  const opened = new Promise((resolve) => { resolveOpened = resolve; });
  createInterface({ input: child.stdout }).on('line', (line) => {
    const value = JSON.parse(line);
    records.push(value);
    if (value.event === 'browser_opened') resolveOpened(value);
    // Baseline has no managed-browser event, so still drive its actual submit endpoint.
    if (value.event === 'ready') setTimeout(() => resolveOpened(value), 1500);
  });
  const done = new Promise((resolve) => child.on('close', (code) => resolve({ code })));
  const browser = await opened;
  const managed = records.find((r) => r.event === 'browser_opened');
  if (managed?.driver === 'ego') t.after(() => execFileSync('ego-browser', ['nodejs', '-e', `
    const entry=(await listTaskSpaces()).find(s=>s.id===${JSON.stringify(managed.spaceId)});
    if(entry){const task=entry.ownership==="user"?await claimTaskSpace(entry.id):entry.ownership==="agentDelegatedToUser"?await takeOverTaskSpace(entry.id):await taskSpace(entry.id);await task.finish({keep:[]});}
  `]));
  if (arrange) await arrange(managed, dir);
  const ready = records.find((r) => r.event === 'ready');
  const state = await fetch(new URL('state', ready.url)).then((r) => r.json());
  const answer = { questionId: 'q1', picked: [], text: 'saved before closing', skipped: false };
  const response = await fetch(new URL('submit', ready.url), { method: 'POST', headers: { 'content-type': 'application/json' },
    body: JSON.stringify({ requestHash: state.requestHash, submissionId: 'close-regression', answers: [answer] }) });
  assert.equal(response.status, 200);
  const result = await done;
  assert.equal(result.code, 0, stderr);
  assert.equal(records.at(-1).status, 'submitted');
  return { records, dir, managed };
}

async function browserProbe(dir, source) {
  const path = join(dir, 'probe.json');
  execFileSync('ego-browser', ['nodejs', '-e', `
    const value=await (async()=>{${source}})();
    const fs=await import("node:fs/promises");
    await fs.writeFile(${JSON.stringify(path)},JSON.stringify(value));
  `]);
  return JSON.parse(await readFile(path, 'utf8'));
}

test('the SDK driver closes its own submitted page and retains the saved answers', { timeout: 60000 }, async (t) => {
  const { records, dir, managed } = await submittedRound(t);
  const cleanup = records.find((r) => r.event === 'browser_cleanup');
  assert.equal(cleanup?.status, 'closed', `A submitted round must close its managed page automatically. ${JSON.stringify(cleanup)}`);
  assert.equal(managed?.driver, 'ego');
  assert.ok(Number.isInteger(managed.spaceId));
  assert.equal(await browserProbe(dir, `return (await listTaskSpaces()).some(s=>s.id===${JSON.stringify(managed.spaceId)});`), false,
    'The browser task must actually be gone, not merely reported closed.');
  const saved = JSON.parse(await readFile(join(dir, 'round', 'answers.json'), 'utf8'));
  assert.equal(saved.answers[0].text, 'saved before closing');
});

test('keep-open retains the submitted page for review', { timeout: 60000 }, async (t) => {
  const { records, dir, managed } = await submittedRound(t, { extra: ['--keep-open'] });
  const cleanup = records.find((r) => r.event === 'browser_cleanup');
  assert.equal(cleanup?.status, 'kept');
  assert.equal(cleanup.reason, 'requested');
  assert.equal(await browserProbe(dir, `return (await listTaskSpaces()).some(s=>s.id===${JSON.stringify(managed.spaceId)});`), true);
});

test('cleanup preserves a round tab that has navigated to different content', { timeout: 60000 }, async (t) => {
  const { records, dir, managed } = await submittedRound(t, { arrange: async (page, dir) => {
    await browserProbe(dir, `const task=await takeOverTaskSpace(${JSON.stringify(page.spaceId)});
      await task.page(${JSON.stringify(page.page)}).goto("about:blank");return true;`);
  } });
  const cleanup = records.find((r) => r.event === 'browser_cleanup');
  assert.equal(cleanup?.status, 'kept');
  assert.equal(cleanup.reason, 'page navigated');
  assert.equal(await browserProbe(dir, `return (await listTaskSpaces()).some(s=>s.id===${JSON.stringify(managed.spaceId)});`), true);
});
