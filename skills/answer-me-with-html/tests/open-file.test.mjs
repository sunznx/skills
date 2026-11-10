import assert from 'node:assert/strict';
import { spawnSync } from 'node:child_process';
import { existsSync, mkdtempSync, mkdirSync, readFileSync, rmSync, writeFileSync } from 'node:fs';
import { tmpdir } from 'node:os';
import path from 'node:path';
import test from 'node:test';
import { fileURLToPath } from 'node:url';

const cli = fileURLToPath(new URL('../scripts/am.mjs', import.meta.url));

function fixture() {
  const root = mkdtempSync(path.join(tmpdir(), 'am-open-'));
  const bin = path.join(root, 'bin');
  mkdirSync(bin);
  const marker = path.join(root, 'opened.json');
  const env = { ...process.env, AM_HOME: path.join(root, 'home'), AM_NO_UPDATE_CHECK: '1', AM_TEST_OPEN_LOG: marker, PATH: `${bin}${path.delimiter}${process.env.PATH}` };
  delete env.CI;
  delete env.AM_NO_OPEN;
  const opener = path.join(bin, process.platform === 'darwin' ? 'open' : 'xdg-open');
  writeFileSync(opener, `#!${process.execPath}\nconst fs = require('node:fs');\nsetTimeout(() => { fs.writeFileSync(process.env.AM_TEST_OPEN_LOG, JSON.stringify(process.argv.slice(2))); process.exit(Number(process.env.AM_TEST_OPEN_EXIT || 0)); }, 200);\n`, { mode: 0o755 });
  const draft = path.join(root, 'draft.md');
  const html = path.join(root, 'answer.html');
  writeFileSync(draft, '---\ntitle: Opening check\n---\n## Result\nA page is ready.\n');
  function run(args) {
    return spawnSync(process.execPath, [cli, ...args], { env, encoding: 'utf8', timeout: 15000 });
  }
  assert.equal(run(['config', 'set', 'open', 'on']).status, 0);
  return { root, marker, env, html, run, render: (args = []) => run(['render', draft, '-o', html, ...args]) };
}

test('automatic opening finishes before render returns', { skip: process.platform === 'win32' }, () => {
  const f = fixture();
  try {
    const result = f.render();
    assert.equal(result.status, 0, result.stderr);
    assert.ok(existsSync(f.marker), 'render returned before the system opener completed');
    assert.deepEqual(JSON.parse(readFileSync(f.marker, 'utf8')), [f.html]);
  } finally { rmSync(f.root, { recursive: true, force: true }); }
});

test('open off and --no-open both suppress opening', { skip: process.platform === 'win32' }, () => {
  const f = fixture();
  try {
    assert.equal(f.render(['--no-open']).status, 0);
    assert.ok(!existsSync(f.marker));
    assert.equal(f.run(['config', 'set', 'open', 'off']).status, 0);
    assert.equal(f.render().status, 0);
    assert.ok(!existsSync(f.marker));
  } finally { rmSync(f.root, { recursive: true, force: true }); }
});

test('an opener failure is visible while retaining the rendered page', { skip: process.platform === 'win32' }, () => {
  const f = fixture();
  try {
    f.env.AM_TEST_OPEN_EXIT = '7';
    const result = f.render();
    assert.equal(result.status, 0, result.stderr);
    assert.ok(existsSync(f.html));
    assert.match(result.stderr, /Could not open .*exit status 7/);
  } finally { rmSync(f.root, { recursive: true, force: true }); }
});
