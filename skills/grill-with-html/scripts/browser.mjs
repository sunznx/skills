import { execFile, spawn } from 'node:child_process';
import { readFileSync, unlinkSync } from 'node:fs';
import { join } from 'node:path';
import { randomUUID } from 'node:crypto';
import { promisify } from 'node:util';

const execute = promisify(execFile);
async function browserScript(source, directory) {
  const receiptPath = join(directory, `.browser-result-${randomUUID()}.json`);
  try {
    // SDK logs are not reliably piped through CLI stdout. Use a per-call receipt.
    const emit = `const emit = async value => { const fs = await import("node:fs/promises");
      await fs.writeFile(${JSON.stringify(receiptPath)}, JSON.stringify(value), {mode:0o600}); };`;
    await execute('ego-browser', ['nodejs', '-e', `${emit}\n${source}`], { timeout: 20000, maxBuffer: 1024 * 1024 });
    return JSON.parse(readFileSync(receiptPath, 'utf8'));
  } finally {
    try { unlinkSync(receiptPath); } catch { /* The command may not have reached emit. */ }
  }
}

export async function openRoundPage(url, directory) {
  const manifest = join(directory, 'browser.json');
  try {
    const browser = await browserScript(`
      const task = await taskSpace(${JSON.stringify(`grill-round-${randomUUID()}`)});
      const page = task.page("p1");
      const receipt = {driver:"ego",spaceId:task.spaceId,page:page.label,url:${JSON.stringify(url)},directory:${JSON.stringify(directory)}};
      const fs = await import("node:fs/promises");
      await fs.writeFile(${JSON.stringify(manifest)},JSON.stringify(receipt),{mode:0o600});
      await page.goto(receipt.url);
      await page.cdp("Page.bringToFront");
      await emit(receipt);
      await task.handOff();
    `, directory);
    if (process.platform === 'darwin') {
      try {
        await execute('open', ['-b', 'com.citrolabs.ego.lite'], { timeout: 5000 });
      } catch {
        return { ...browser, warning: 'The round tab was activated, but the Ego window could not be brought to the foreground.' };
      }
    }
    return browser;
  } catch (error) {
    if (error.code === 'ENOENT') {
      const [command, args] = process.platform === 'darwin' ? ['open', [url]] : process.platform === 'win32'
        ? ['rundll32', ['url.dll,FileProtocolHandler', url]] : ['xdg-open', [url]];
      const child = spawn(command, args, { stdio: 'ignore' });
      child.on('error', () => console.error('Open the ready URL manually; the system browser could not be started.'));
      return { driver: 'system', reason: 'ego-browser is unavailable; automatic tab cleanup is unavailable.' };
    }
    // An uncertain launch may already own a page. Never open a duplicate as a fallback.
    try {
      const receipt = JSON.parse(readFileSync(manifest, 'utf8'));
      if (receipt.url === url) return { ...receipt, warning: 'Browser loading or foreground activation could not be confirmed; inspect the recorded page and ready URL.' };
    } catch { /* No confirmed managed page. */ }
    return { driver: 'unavailable', reason: 'Browser automation failed; open the ready URL manually.' };
  }
}

export async function finishRoundPage(browser, { status, keepOpen = false }) {
  if (browser.driver !== 'ego') return { status: 'unavailable', reason: browser.reason };
  if (status !== 'submitted') return { status: 'kept', reason: status, spaceId: browser.spaceId };
  try {
    const cleanup = await browserScript(`
      const receipt = ${JSON.stringify(browser)};
      const entry = (await listTaskSpaces()).find(s=>s.id===receipt.spaceId);
      if (!entry) {
        await emit({status:"closed",spaceId:receipt.spaceId});
      } else if (entry.ownership === "user") {
        await emit({status:"kept",reason:"user control",spaceId:receipt.spaceId});
      } else {
        const task = entry.ownership === "agentDelegatedToUser"
          ? await takeOverTaskSpace(receipt.spaceId) : await taskSpace(receipt.spaceId);
        const tabs = await task.tabs();
        const target = tabs.find(t=>t.label===receipt.page);
        const keepRound = ${JSON.stringify(keepOpen)} || Boolean(target && target.url!==receipt.url);
        const keep = tabs.filter(t=>t.label && (keepRound || t.label!==receipt.page)).map(t=>t.label);
        // finish ends the SDK script. Accept this receipt only if the process exits successfully.
        await emit({status:keepRound?"kept":"closed",
          reason:keepRound?${JSON.stringify(keepOpen ? 'requested' : 'page navigated')}:undefined,spaceId:receipt.spaceId});
        await task.finish({keep});
      }
    `, browser.directory);
    if (cleanup.status === 'closed') {
      const remains = await browserScript(`await emit((await listTaskSpaces()).some(s=>s.id===${JSON.stringify(browser.spaceId)}));`, browser.directory);
      if (remains) return { status: 'failed', reason: 'The browser space still exists; inspect the exact round page before claiming closure.', spaceId: browser.spaceId };
    }
    return cleanup;
  } catch (error) {
    const detail = String(error.stderr ?? '').trim().split('\n')[0] || String(error.code ?? 'unknown error');
    return { status: 'failed', reason: `Browser cleanup could not be confirmed: ${detail}`, spaceId: browser.spaceId };
  }
}
