const frame = document.querySelector('#questions');
const status = document.querySelector('#status');
const submit = document.querySelector('#submit');
const save = document.querySelector('#save');
const cancel = document.querySelector('#cancel');
let state;
let controls = [];
let timer;
let busy = false;
let finished = false;
let saving = Promise.resolve();
const submissionId = crypto.randomUUID();

async function request(route, method = 'GET', body) {
  const response = await fetch(route, { method, headers: body ? { 'content-type': 'application/json' } : {}, body: body ? JSON.stringify(body) : undefined });
  const data = await response.json();
  if (!response.ok) throw new Error(data.error ?? '请求未完成');
  return data;
}

function collect() {
  return { requestHash: state.requestHash, answers: controls.map(({ q, inputs, text, skip }) => ({
    questionId: q.id, skipped: skip?.checked ?? false,
    picked: skip?.checked ? [] : inputs.flatMap((input, i) => input.checked ? [q.options[i].id] : []),
    text: skip?.checked ? '' : text.value,
  })) };
}

function remaining() {
  return collect().answers.filter((a) => !a.skipped && !a.picked.length && !a.text.trim()).length;
}

function refresh() {
  const count = remaining();
  submit.disabled = busy || finished || count > 0;
  save.disabled = busy || finished;
  cancel.disabled = busy || finished;
  for (const { inputs, text, skip } of controls) {
    for (const input of [...inputs, text]) input.disabled = busy || finished || Boolean(skip?.checked);
    if (skip) skip.disabled = busy || finished;
  }
  return count;
}

function persist() {
  clearTimeout(timer);
  const value = collect();
  saving = saving.catch(() => {}).then(() => request('draft', 'PUT', value));
  saving.then(() => {
    if (!busy && !finished) status.textContent = `草稿已保存${remaining() ? ` · 还有 ${remaining()} 题待回答` : ' · 可以提交本轮'}`;
  }).catch(() => {
    if (!busy && !finished) status.textContent = '草稿保存失败，请点「保存草稿」重试。';
  });
  return saving;
}

function changed() {
  if (busy || finished) return;
  const count = refresh();
  status.textContent = count ? `正在保存 · 还有 ${count} 题待回答` : '正在保存 · 可以提交本轮';
  clearTimeout(timer);
  timer = setTimeout(persist, 250);
}

async function finish(route) {
  if (busy || finished) return;
  clearTimeout(timer);
  busy = true;
  refresh();
  status.textContent = route === 'submit' ? '正在提交本轮…' : '正在取消…';
  try {
    await saving.catch(() => {});
    await request(route, 'POST', { ...collect(), submissionId });
    finished = true;
    status.textContent = route === 'submit' ? '本轮已提交，回到原对话即可看到后续追问。' : '本轮已取消，可以回到原对话。';
  } catch (error) {
    status.textContent = `未能完成：${error.message}。答案仍在页面中，可以重试；原工具结束后可从原对话重开本轮。`;
  } finally {
    busy = false;
    refresh();
  }
}

try {
  const loaded = new Promise((resolve) => frame.addEventListener('load', resolve, { once: true }));
  state = await request('state');
  if (!frame.contentDocument?.querySelector('.am-panel')) await loaded;
  const doc = frame.contentDocument;
  const panels = [...doc.querySelectorAll('.am-panel')];
  if (panels.length !== state.input.questions.length) throw new Error('问题页面与本轮数据不匹配');
  document.querySelector('#title').textContent = state.input.title;
  document.title = state.input.title;
  doc.querySelector('.am-toolbar')?.remove();
  doc.querySelector('.am-reply-bar')?.remove();
  controls = state.input.questions.map((q, i) => {
    const panel = panels[i];
    const inputs = [...panel.querySelectorAll('.am-ask input')];
    if (inputs.length !== (q.type === 'text' ? 0 : q.options.length)) throw new Error('选项数量不匹配');
    const text = panel.querySelector('.am-comment textarea');
    if (!text) throw new Error('页面缺少回答输入框');
    text.parentElement.hidden = false;
    text.placeholder = q.type === 'text' ? '填写你的回答' : '补充说明，也可以在这里直接回答';
    text.setAttribute('aria-label', q.type === 'text' ? q.question : `补充说明：${q.question}`);
    panel.querySelector('.am-comment-btn')?.remove();
    let skip;
    if (q.allowSkip) {
      const label = doc.createElement('label');
      skip = Object.assign(doc.createElement('input'), { type: 'checkbox' });
      label.append(skip, ' 本轮暂不决定');
      panel.append(label);
    }
    const saved = state.draft?.answers.find((a) => a.questionId === q.id);
    for (const [n, input] of inputs.entries()) input.checked = saved?.picked.includes(q.options[n].id) ?? false;
    text.value = saved?.text ?? '';
    if (skip) skip.checked = saved?.skipped ?? false;
    for (const control of [...inputs, text, ...(skip ? [skip] : [])]) {
      control.addEventListener('input', changed);
      control.addEventListener('change', changed);
    }
    return { q, inputs, text, skip };
  });
  status.textContent = state.draft ? '已恢复本轮草稿。' : '选项尚未确认，填写完成后点击「提交本轮」。';
  refresh();
  submit.addEventListener('click', () => finish('submit'));
  cancel.addEventListener('click', () => finish('cancel'));
  save.addEventListener('click', persist);
  window.addEventListener('pagehide', () => {
    if (!busy && !finished) fetch('draft', { method: 'PUT', headers: { 'content-type': 'application/json' }, body: JSON.stringify(collect()), keepalive: true }).catch(() => {});
  });
} catch (error) {
  status.textContent = `无法打开本轮：${error.message}。请从原对话重开本轮。`;
}
