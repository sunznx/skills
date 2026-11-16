import assert from 'node:assert/strict';
import { execFileSync, spawn } from 'node:child_process';
import { mkdtemp, readFile, rm, writeFile } from 'node:fs/promises';
import { tmpdir } from 'node:os';
import { basename, join } from 'node:path';
import { createInterface } from 'node:readline';
import { fileURLToPath } from 'node:url';
import test from 'node:test';

test('an unanswered submit explains what is missing without approving anything, then explicit answers save and submit', { timeout: 60000 }, async t => {
  const dir = await mkdtemp(join(tmpdir(), 'grill-submit-'));
  const input = join(dir, 'input.json');
  await writeFile(input, JSON.stringify({ title: 'Submit feedback regression', questions: [
    { id: 'review', question: '是否接受本轮方案？', recommended: ['approve'], options: [
      { id: 'approve', label: '接受方案' }, { id: 'revise', label: '需要调整' },
    ] },
  ] }));
  const child = spawn(process.execPath, [fileURLToPath(new URL('../scripts/ask.mjs', import.meta.url)), '--input', input,
    '--round-dir', join(dir, 'round'), '--no-open', '--timeout', '40'], {
    env: { ...process.env, AM_NO_UPDATE_CHECK: '1' }, stdio: ['ignore', 'pipe', 'pipe'],
  });
  let stderr = '';
  child.stderr.on('data', chunk => { stderr += chunk; });
  let ready;
  const started = new Promise(resolve => { ready = resolve; });
  const records = [];
  createInterface({ input: child.stdout }).on('line', line => {
    const value = JSON.parse(line); records.push(value);
    if (value.event === 'ready') ready(value);
  });
  const done = new Promise(resolve => child.on('close', code => { ready(undefined); resolve({ code }); }));
  let spaceId;
  t.after(async () => {
    if (child.exitCode === null) child.kill();
    await done;
    if (spaceId !== undefined) execFileSync('ego-browser', ['nodejs', '-e', `const task=await taskSpace(${JSON.stringify(spaceId)});await task.finish({keep:[]});`]);
    await rm(dir, { recursive: true, force: true });
  });
  const opened = await started;
  assert.ok(opened?.url, stderr);
  const receipt = join(dir, 'observation.json');
  const browser = async source => {
    execFileSync('ego-browser', ['nodejs', '-e', `const fs=await import("node:fs/promises");
      const emit=async value=>fs.writeFile(${JSON.stringify(receipt)},JSON.stringify(value));${source}`], { timeout: 20000 });
    return JSON.parse(await readFile(receipt, 'utf8'));
  };
  spaceId = (await browser(`const task=await taskSpace(${JSON.stringify(`grill-submit-${basename(dir)}`)});await emit({id:task.spaceId});`)).id;
  const beforeAnswer = await browser(`const task=await taskSpace(${spaceId});const page=task.page("p1");
    await page.goto(${JSON.stringify(opened.url)});
    await page.waitForFunction(()=>document.querySelector("#status").textContent!=="正在打开本轮问题…");
    await emit(await page.evaluate(()=>{
      const doc=document.querySelector("#questions").contentDocument;
      document.querySelector("#submit").click();
      return {status:document.querySelector("#status").textContent,
        checked:doc.querySelectorAll(".am-ask input:checked").length,
        text:doc.querySelector(".am-panel > .am-comment textarea").value};
    }));`);
  assert.match(beforeAnswer.status, /未回答/, 'Clicking an unanswered form must explain the missing answer while the wait is still live.');
  assert.match(beforeAnswer.status, /是否接受本轮方案？/);
  assert.equal(beforeAnswer.checked, 0, 'Missing-answer feedback must not accept the recommendation.');
  assert.equal(beforeAnswer.text, '');
  const initial = await fetch(new URL('state', opened.url)).then(response => response.json());
  assert.equal(initial.result, null);
  assert.equal(initial.draft, null);
  const draft = await browser(`const task=await taskSpace(${spaceId});const page=task.page("p1");
    await page.evaluate(()=>{
      const doc=document.querySelector("#questions").contentDocument;
      const option=doc.querySelectorAll(".am-ask input")[1];option.checked=true;option.dispatchEvent(new Event("change",{bubbles:true}));
      const text=doc.querySelector(".am-panel > .am-comment textarea");text.value="需要先调整范围。";text.dispatchEvent(new Event("input",{bubbles:true}));
    });
    await page.waitForFunction(()=>document.querySelector("#status").textContent.startsWith("草稿已保存"));
    await emit(await page.evaluate(async()=> (await (await fetch("state")).json()).draft));`);
  const answer = { questionId: 'review', picked: ['revise'], text: '需要先调整范围。', skipped: false };
  assert.deepEqual(draft.answers, [answer]);
  await browser(`const task=await taskSpace(${spaceId});const page=task.page("p1");
    await page.evaluate(()=>document.querySelector("#submit").click());
    await page.waitForFunction(()=>document.querySelector("#status").textContent.startsWith("本轮已提交"));await emit({submitted:true});`);
  assert.equal((await done).code, 0, stderr);
  assert.deepEqual(records.at(-1).answers, [answer]);
});
