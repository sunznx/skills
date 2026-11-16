import assert from 'node:assert/strict';
import { spawn } from 'node:child_process';
import { mkdtemp, readFile, rm, writeFile } from 'node:fs/promises';
import { tmpdir } from 'node:os';
import { join } from 'node:path';
import { createInterface } from 'node:readline';
import { fileURLToPath } from 'node:url';
import { createConnection } from 'node:net';
import { setTimeout as delay } from 'node:timers/promises';
import test from 'node:test';

const command = fileURLToPath(new URL('../scripts/ask.mjs', import.meta.url));
const request = {
  title: '发布范围',
  questions: [{ id: 'q1', question: '这轮先支持哪种客户端？', recommended: ['both'],
    options: [{ id: 'both', label: '两种都支持' }, { id: 'codex', label: '只支持 Codex' }] }],
};

async function fixture(t, input = request) {
  const dir = await mkdtemp(join(tmpdir(), 'grill-html-'));
  t.after(() => rm(dir, { recursive: true, force: true }));
  const path = join(dir, 'input.json');
  await writeFile(path, JSON.stringify(input));
  return { dir, path };
}

function launch(t, f, extra = []) {
  const child = spawn(process.execPath, [command, '--input', f.path, '--round-dir', join(f.dir, 'round'), '--no-open', ...extra],
    { env: { ...process.env, AM_NO_UPDATE_CHECK: '1' }, stdio: ['ignore', 'pipe', 'pipe'] });
  t.after(() => { if (child.exitCode === null) child.kill(); });
  const records = [];
  let error = '';
  child.stderr.on('data', (chunk) => { error += chunk; });
  let ready;
  const started = new Promise((resolve) => { ready = resolve; });
  createInterface({ input: child.stdout }).on('line', (line) => {
    const record = JSON.parse(line);
    records.push(record);
    if (record.event === 'ready') ready(record);
  });
  const done = new Promise((resolve) => child.on('close', (code) => {
    ready(undefined);
    resolve({ code, records, error, result: records.at(-1) });
  }));
  return { started, done, child };
}

test('a browser submission returns the chosen answers to the waiting command and survives reopening', { timeout: 15000 }, async (t) => {
  const f = await fixture(t);
  const run = launch(t, f);
  const ready = await run.started;
  assert.ok(ready?.url, 'The waiting command must publish its browser URL.');
  const state = await fetch(new URL('state', ready.url)).then((r) => r.json());
  const submission = { submissionId: 'choice-1', requestHash: state.requestHash,
    answers: [{ questionId: 'q1', picked: ['both'], text: '先把共同流程跑通。', skipped: false }] };
  const response = await fetch(new URL('submit', ready.url), { method: 'POST', headers: { 'content-type': 'application/json' }, body: JSON.stringify(submission) });
  assert.equal(response.status, 200);
  const completed = await run.done;
  assert.equal(completed.code, 0, completed.error);
  assert.equal(completed.result.status, 'submitted');
  assert.deepEqual(completed.result.answers, submission.answers);
  const reopened = await launch(t, f).done;
  assert.deepEqual(reopened.result, completed.result, 'Reopening must return the saved result without asking again.');
});

test('an unanswered question or stale page cannot submit; correcting it completes the same waiting round', { timeout: 15000 }, async (t) => {
  const f = await fixture(t);
  const run = launch(t, f);
  const ready = await run.started;
  const state = await fetch(new URL('state', ready.url)).then((r) => r.json());
  const post = (body) => fetch(new URL('submit', ready.url), { method: 'POST', headers: { 'content-type': 'application/json' }, body: JSON.stringify(body) });
  const invalid = await post({ submissionId: 'empty', requestHash: state.requestHash, answers: [] });
  assert.equal(invalid.status, 400, 'An untouched recommendation is not an answer.');
  const stale = await post({ submissionId: 'old', requestHash: 'old-round', answers: [{ questionId: 'q1', picked: ['both'], text: '', skipped: false }] });
  assert.equal(stale.status, 409, 'Answers from an older round must not be applied.');
  const corrected = await post({ submissionId: 'corrected', requestHash: state.requestHash, answers: [{ questionId: 'q1', picked: [], text: '先只讨论跨客户端的共同部分。', skipped: false }] });
  assert.equal(corrected.status, 200);
  assert.equal((await run.done).result.answers[0].text, '先只讨论跨客户端的共同部分。');
});

test('draft answers survive an interrupted waiting command and can be completed after reopening', { timeout: 15000 }, async (t) => {
  const f = await fixture(t);
  const first = launch(t, f);
  const ready = await first.started;
  const state = await fetch(new URL('state', ready.url)).then((r) => r.json());
  const draft = { requestHash: state.requestHash, answers: [{ questionId: 'q1', picked: [], text: '还在想。', skipped: false }] };
  const saved = await fetch(new URL('draft', ready.url), { method: 'PUT', headers: { 'content-type': 'application/json' }, body: JSON.stringify(draft) });
  assert.equal(saved.status, 200, 'Draft changes must be acknowledged after they are saved.');
  first.child.kill('SIGTERM');
  await first.done;
  const second = launch(t, f);
  const next = await second.started;
  const restored = await fetch(new URL('state', next.url)).then((r) => r.json());
  assert.deepEqual(restored.draft.answers, draft.answers);
  await fetch(new URL('submit', next.url), { method: 'POST', headers: { 'content-type': 'application/json' }, body: JSON.stringify({ ...draft, submissionId: 'after-reopen' }) });
  assert.equal((await second.done).result.answers[0].text, '还在想。');
});

test('cancelling returns a cancellation result rather than an answer', { timeout: 15000 }, async (t) => {
  const f = await fixture(t);
  const run = launch(t, f);
  const ready = await run.started;
  const state = await fetch(new URL('state', ready.url)).then((r) => r.json());
  const response = await fetch(new URL('cancel', ready.url), { method: 'POST', headers: { 'content-type': 'application/json' }, body: JSON.stringify({ requestHash: state.requestHash }) });
  assert.equal(response.status, 200);
  const done = await run.done;
  assert.equal(done.code, 3);
  assert.equal(done.result.status, 'cancelled');
  assert.equal(done.result.answers, undefined);
});

test('the waiting limit returns timed_out and allows the same round to be reopened', { timeout: 15000 }, async (t) => {
  const f = await fixture(t);
  const run = launch(t, f, ['--timeout', '0.2']);
  const ready = await run.started;
  assert.ok(ready?.url, 'A limited wait must still open a browser round.');
  const done = await run.done;
  assert.equal(done.code, 2);
  assert.equal(done.result.status, 'timed_out');
  const reopened = launch(t, f);
  assert.ok((await reopened.started)?.url, 'Timing out must leave the round resumable.');
});

test('duplicate submissions return the same receipt and cannot replace a confirmed answer', { timeout: 15000 }, async (t) => {
  const f = await fixture(t);
  const run = launch(t, f);
  const ready = await run.started;
  const state = await fetch(new URL('state', ready.url)).then((r) => r.json());
  const body = { submissionId: 'same-click', requestHash: state.requestHash, answers: [{ questionId: 'q1', picked: ['both'], text: '', skipped: false }] };
  const post = (value) => fetch(new URL('submit', ready.url), { method: 'POST', headers: { 'content-type': 'application/json' }, body: JSON.stringify(value) });
  const first = await post(body).then((r) => r.json());
  const duplicate = await post(body);
  assert.equal(duplicate.status, 200);
  assert.deepEqual(await duplicate.json(), first);
  const conflicting = await post({ ...body, answers: [{ ...body.answers[0], picked: ['codex'] }] });
  assert.equal(conflicting.status, 409);
  assert.deepEqual((await run.done).result, first);
});

test('a changed request cannot reuse a previously submitted round', { timeout: 15000 }, async (t) => {
  const f = await fixture(t);
  const first = launch(t, f);
  const ready = await first.started;
  const state = await fetch(new URL('state', ready.url)).then((r) => r.json());
  await fetch(new URL('submit', ready.url), { method: 'POST', headers: { 'content-type': 'application/json' }, body: JSON.stringify({ submissionId: 'v1', requestHash: state.requestHash, answers: [{ questionId: 'q1', picked: ['both'], text: '', skipped: false }] }) });
  await first.done;
  await writeFile(f.path, JSON.stringify({ ...request, title: '改变后的问题' }));
  const changed = await launch(t, f).done;
  assert.equal(changed.code, 1, 'A changed request must use a new round directory.');
  assert.match(changed.error, /new round/i);
});

test('the browser URL serves the interview shell and the existing renderer handles single, multi and text questions', { timeout: 15000 }, async (t) => {
  const input = { ...request, context: '这一轮只确认范围。', questions: [request.questions[0],
    { id: 'q2', question: '先验证哪些动作？', type: 'multi', recommended: ['save'], options: [{ id: 'save', label: '保存草稿' }, { id: 'resume', label: '恢复本轮' }] },
    { id: 'q3', question: '还有什么要求？', type: 'text', allowSkip: true }] };
  const f = await fixture(t, input);
  const run = launch(t, f);
  const ready = await run.started;
  const shell = await fetch(ready.url);
  assert.equal(shell.status, 200, 'The shared browser entry must display the round.');
  assert.match(await shell.text(), /iframe/);
  const rendered = await fetch(new URL('page', ready.url)).then((r) => r.text());
  assert.match(rendered, /两种都支持/);
  assert.match(rendered, /type="checkbox"/);
  assert.match(rendered, /还有什么要求/);
  const state = await fetch(new URL('state', ready.url)).then((r) => r.json());
  const response = await fetch(new URL('submit', ready.url), { method: 'POST', headers: { 'content-type': 'application/json' }, body: JSON.stringify({ submissionId: 'all-types', requestHash: state.requestHash, answers: [
    { questionId: 'q1', picked: ['both'], text: '', skipped: false },
    { questionId: 'q2', picked: ['save', 'resume'], text: '', skipped: false },
    { questionId: 'q3', picked: [], text: '', skipped: true },
  ] }) });
  assert.equal(response.status, 200);
  assert.equal((await run.done).result.answers[2].skipped, true);
});

test('only one waiting command owns a round, and interruption releases it for reopening', { timeout: 15000 }, async (t) => {
  const f = await fixture(t);
  const first = launch(t, f);
  assert.ok((await first.started)?.url);
  const second = launch(t, f, ['--timeout', '0.1']);
  const busy = await second.done;
  assert.equal(busy.code, 1, 'A second command must not compete for the same answers.');
  assert.match(busy.error, /already waiting/i);
  first.child.kill('SIGTERM');
  await first.done;
  const reopened = launch(t, f);
  assert.ok((await reopened.started)?.url);
});

test('the wait still times out when a browser connection stops halfway through sending a draft', { timeout: 10000 }, async (t) => {
  const f = await fixture(t);
  const run = launch(t, f, ['--timeout', '0.2']);
  const ready = await run.started;
  const url = new URL(ready.url);
  const socket = createConnection({ host: url.hostname, port: Number(url.port) });
  socket.on('error', () => {});
  t.after(() => socket.destroy());
  await new Promise((resolve) => socket.once('connect', resolve));
  socket.write(`PUT ${url.pathname}draft HTTP/1.1\r\nHost: ${url.host}\r\nContent-Type: application/json\r\nContent-Length: 200\r\n\r\n{`);
  const done = await Promise.race([run.done, delay(2500).then(() => null)]);
  assert.equal(done?.result.status, 'timed_out', 'An incomplete request must not keep the agent waiting past its limit.');
});
