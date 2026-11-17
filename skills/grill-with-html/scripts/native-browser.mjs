import { execFile } from 'node:child_process';
import { writeFileSync } from 'node:fs';
import { join } from 'node:path';
import { promisify } from 'node:util';

const execute = promisify(execFile);
const bundleId = 'com.citrolabs.ego.lite';
const prelude = `const app = Application(${JSON.stringify(bundleId)});
  function findTab(id) {
    for (const window of app.windows()) {
      const index = window.tabs.id().map(String).indexOf(String(id));
      if (index !== -1) return { window, tab: window.tabs[index] };
    }
  }`;

async function nativeScript(source) {
  const { stdout } = await execute('osascript', ['-l', 'JavaScript', '-e', `${prelude}\n${source}`],
    { timeout: 10000, maxBuffer: 1024 * 1024 });
  return JSON.parse(stdout);
}

export async function openNativeRoundPage(url, directory) {
  let browser;
  try {
    // Native windows are separate from Ego SDK spaces. Record the real tab before navigation.
    const identity = await nativeScript(`const window = app.Window({givenName:"Grill with HTML"}).make();
      JSON.stringify({windowId:String(window.id()),tabId:String(window.activeTab().id())});`);
    browser = { driver: 'ego-native', bundleId, ...identity, url, directory };
    writeFileSync(join(directory, 'browser.json'), JSON.stringify(browser), { mode: 0o600 });
    await nativeScript(`const target = findTab(${JSON.stringify(browser.tabId)});
      if (!target) throw new Error("The round tab disappeared before navigation.");
      target.tab.url = ${JSON.stringify(url)};
      target.window.visible = true;
      target.window.minimized = false;
      target.window.index = 1;
      app.activate();
      const deadline = Date.now() + 5000;
      function visible() { return app.frontmost() && target.window.visible() && !target.window.minimized()
        && String(app.windows()[0].id()) === String(target.window.id())
        && String(target.window.activeTab().id()) === ${JSON.stringify(browser.tabId)}
        && target.tab.url() === ${JSON.stringify(url)}; }
      while (!visible() && Date.now() < deadline) delay(0.1);
      if (!visible()) throw new Error("The native round tab is not selected in the foreground window.");
      JSON.stringify(true);`);
    return { ...browser, visibility: 'foreground' };
  } catch {
    // Creation may have succeeded. Preserve it and report uncertainty without a second opener.
    return { ...(browser ?? { driver: 'unavailable' }),
      warning: 'The native Ego form could not be confirmed in the foreground. Inspect the ready URL and macOS Automation permission for the calling app.' };
  }
}

export async function finishNativeRoundPage(browser, { status, keepOpen = false }) {
  if (status !== 'submitted' || keepOpen) return { status: 'kept', reason: keepOpen ? 'requested' : status, tabId: browser.tabId };
  try {
    return await nativeScript(`const target = findTab(${JSON.stringify(browser.tabId)});
      let result;
      if (target && target.tab.url() !== ${JSON.stringify(browser.url)}) {
        result = {status:"kept",reason:"page navigated"};
      } else {
        if (target) target.tab.close();
        const deadline = Date.now() + 3000;
        while (findTab(${JSON.stringify(browser.tabId)}) && Date.now() < deadline) delay(0.1);
        if (findTab(${JSON.stringify(browser.tabId)})) throw new Error("The round tab still exists.");
        const copies = app.windows().flatMap(w=>w.tabs.url()).filter(url=>url===${JSON.stringify(browser.url)}).length;
        result = copies ? {status:"kept",reason:"Another copy of the round remains outside the managed tab.",managedClosed:true,retainedCopies:copies}
          : {status:"closed"};
      }
      JSON.stringify({...result,tabId:${JSON.stringify(browser.tabId)}});`);
  } catch (error) {
    const detail = String(error.stderr || error.message).trim().split('\n')[0];
    return { status: 'failed', reason: `Native tab closure could not be verified: ${detail}`, tabId: browser.tabId };
  }
}
