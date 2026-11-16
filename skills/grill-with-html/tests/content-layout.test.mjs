import assert from 'node:assert/strict';
import { execFileSync, spawn } from 'node:child_process';
import { mkdtemp, readFile, rm, writeFile } from 'node:fs/promises';
import { tmpdir } from 'node:os';
import { join } from 'node:path';
import { createInterface } from 'node:readline';
import { fileURLToPath } from 'node:url';
import test from 'node:test';

const command = fileURLToPath(new URL('../scripts/ask.mjs', import.meta.url));

test('supporting explanations, figures, demos and API examples stay with their question and never become answers', { timeout: 60000 }, async t => {
  const dir = await mkdtemp(join(tmpdir(), 'grill-content-'));
  let spaceId;
  let child;
  let done;
  t.after(async () => {
    if (child?.exitCode === null) child.kill();
    if (done) await done;
    if (spaceId !== undefined) execFileSync('ego-browser', ['nodejs', '-e', `
      const entry=(await listTaskSpaces()).find(s=>s.id===${JSON.stringify(spaceId)});
      if(entry){const task=await taskSpace(entry.id);await task.finish({keep:[]});}
    `]);
    await rm(dir, { recursive: true, force: true });
  });
  const context = [
    '### Recommendation', 'Keep the existing address. This belongs only to the address question.',
    '### Diagram', '```svg', '<svg xmlns="http://www.w3.org/2000/svg" width="160" height="40" role="img" aria-label="Address diagram"><text x="2" y="25">Stable address</text></svg>', '```',
    '### Demo', '```html', '<section class="am-panel" id="demo-card"><h3>Example, not a question</h3><fieldset class="am-ask"><legend>Try a demo control</legend><input id="demo-pick" type="checkbox"></fieldset><div class="am-comment"><textarea id="demo-text">Demo text only</textarea></div><details><summary>Demo explanation</summary>Inspect this locally.</details></section>', '```',
    '### API example', '```http', 'GET /address/example HTTP/1.1', 'X-Example: ## a protocol value, not a panel heading', '```',
  ].join('\n\n');
  const input = { title: 'Content ownership regression', context: 'Shared round context only.', questions: [
    { id: 'address', question: 'Should the address stay stable?', recommended: ['stable'], options: [
      { id: 'stable', label: 'Keep the original address' }, { id: 'change', label: 'Accept a new address' },
    ], context },
    { id: 'recovery', type: 'text', question: 'How should recovery work?', context: 'A separate recovery explanation.' },
  ] };
  await writeFile(join(dir, 'input.json'), JSON.stringify(input));
  child = spawn(process.execPath, [command, '--input', join(dir, 'input.json'), '--round-dir', join(dir, 'round'), '--no-open', '--timeout', '40'], {
    env: { ...process.env, AM_NO_UPDATE_CHECK: '1' }, stdio: ['ignore', 'pipe', 'pipe'],
  });
  let stderr = '';
  child.stderr.on('data', chunk => { stderr += chunk; });
  let ready;
  const started = new Promise(resolve => { ready = resolve; });
  const records = [];
  createInterface({ input: child.stdout }).on('line', line => {
    const value = JSON.parse(line);
    records.push(value);
    if (value.event === 'ready') ready(value);
  });
  done = new Promise(resolve => child.on('close', code => { ready(undefined); resolve({ code }); }));
  const opened = await started;
  assert.ok(opened?.url, stderr);
  const receipt = join(dir, 'observation.json');
  const browser = async source => {
    execFileSync('ego-browser', ['nodejs', '-e', `
      const fs=await import("node:fs/promises");
      const emit=async value=>fs.writeFile(${JSON.stringify(receipt)},JSON.stringify(value));
      ${source}
    `], { timeout: 20000 });
    return JSON.parse(await readFile(receipt, 'utf8'));
  };
  const identity = await browser(`const task=await taskSpace(${JSON.stringify(`grill-content-${dir.split('/').at(-1)}`)});await emit({spaceId:task.spaceId});`);
  spaceId = identity.spaceId;
  const observed = await browser(`
    const task=await taskSpace(${JSON.stringify(spaceId)});const page=task.page("p1");
    await page.goto(${JSON.stringify(opened.url)});
    await page.waitForFunction(()=>document.querySelector("#status").textContent!=="正在打开本轮问题…");
    await emit(await page.evaluate(()=>{
      const doc=document.querySelector("#questions").contentDocument;
      const cards=[...doc.querySelectorAll(".am-doc-body > .am-panel")];
      const owner=selector=>doc.querySelector(selector)?.closest(".am-doc-body > .am-panel")?.querySelector(".am-panel-head h2")?.textContent;
      return {status:document.querySelector("#status").textContent,intro:doc.querySelector(".am-intro")?.textContent.trim(),
        titles:cards.map(card=>card.querySelector(".am-panel-head h2").textContent),
        diagramOwner:owner("svg[aria-label='Address diagram']"),demoOwner:owner("#demo-card"),
        firstText:cards[0]?.textContent,secondText:cards[1]?.textContent,
        answerLabels:cards.map(card=>card.querySelector(":scope > .am-comment textarea")?.getAttribute("aria-label"))};
    }));
  `);
  assert.doesNotMatch(observed.status, /无法打开本轮/, 'Supporting content must not be counted as extra questions or answer controls.');
  assert.equal(observed.intro, 'Shared round context only.');
  assert.deepEqual(observed.titles, ['Should the address stay stable?', 'How should recovery work?']);
  assert.equal(observed.diagramOwner, 'Should the address stay stable?');
  assert.equal(observed.demoOwner, 'Should the address stay stable?');
  assert.ok(observed.firstText.indexOf('Keep the original address') < observed.firstText.indexOf('Recommendation'));
  assert.ok(observed.firstText.indexOf('Recommendation') < observed.firstText.indexOf('Stable address'));
  assert.ok(observed.firstText.indexOf('Stable address') < observed.firstText.indexOf('Demo explanation'));
  assert.ok(observed.firstText.indexOf('Demo explanation') < observed.firstText.indexOf('GET /address/example'));
  assert.doesNotMatch(observed.secondText, /Demo explanation|GET \/address\/example|Keep the existing address/);
  assert.deepEqual(observed.answerLabels, ['补充说明：Should the address stay stable?', 'How should recovery work?']);
  await browser(`
    const task=await taskSpace(${JSON.stringify(spaceId)});const page=task.page("p1");
    await page.evaluate(()=>{
      const doc=document.querySelector("#questions").contentDocument;
      const cards=[...doc.querySelectorAll(".am-doc-body > .am-panel")];
      doc.querySelector("#demo-pick").checked=true;
      doc.querySelector("#demo-text").value="This demo input is not an answer.";
      cards[0].querySelector(":scope > .am-panel-body > .am-ask input").checked=true;
      for(const [index,card] of cards.entries()){
        const box=card.querySelector(":scope > .am-comment textarea");
        box.value=index===0?"Preserve the existing address.":"Reconnect after discovery.";
        box.dispatchEvent(new Event("input",{bubbles:true}));
      }
      document.querySelector("#submit").click();
    });
    await page.waitForFunction(()=>document.querySelector("#status").textContent.startsWith("本轮已提交"));
    await emit({submitted:true});
  `);
  assert.equal((await done).code, 0, stderr);
  assert.deepEqual(records.at(-1).answers, [
    { questionId: 'address', picked: ['stable'], text: 'Preserve the existing address.', skipped: false },
    { questionId: 'recovery', picked: [], text: 'Reconnect after discovery.', skipped: false },
  ]);
});
