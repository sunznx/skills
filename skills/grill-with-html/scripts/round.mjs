import { createHash, randomUUID } from 'node:crypto';
import { closeSync, existsSync, mkdirSync, openSync, readFileSync, renameSync, unlinkSync, writeFileSync } from 'node:fs';
import { join } from 'node:path';

function writeJson(path, value) {
  const temp = `${path}.${randomUUID()}.tmp`;
  writeFileSync(temp, `${JSON.stringify(value, null, 2)}\n`, { mode: 0o600 });
  renameSync(temp, path);
}

export function acquireRound(dir) {
  mkdirSync(dir, { recursive: true });
  const path = join(dir, '.waiting');
  try {
    const fd = openSync(path, 'wx', 0o600);
    try { writeFileSync(fd, String(process.pid)); } finally { closeSync(fd); }
  } catch (error) {
    if (error.code !== 'EEXIST') throw error;
    const owner = Number(readFileSync(path, 'utf8'));
    if (Number.isSafeInteger(owner) && owner > 0) {
      try { process.kill(owner, 0); } catch (probe) {
        if (probe.code === 'ESRCH') { unlinkSync(path); return acquireRound(dir); }
      }
    }
    throw new Error('Another command is already waiting for this round. Reuse its URL.');
  }
  return () => {
    try { if (readFileSync(path, 'utf8') === String(process.pid)) unlinkSync(path); } catch { /* Already released. */ }
  };
}

function invalid(message, status = 400) {
  throw Object.assign(new Error(message), { status });
}

function checkInput(input) {
  if (!input || typeof input.title !== 'string' || !input.title.trim() || !Array.isArray(input.questions) || !input.questions.length) {
    invalid('A title and at least one question are required.');
  }
  const ids = new Set();
  for (const q of input.questions) {
    if (!q || typeof q.id !== 'string' || !q.id || ids.has(q.id) || typeof q.question !== 'string' || !q.question.trim()) {
      invalid('Questions need unique IDs and non-empty question text.');
    }
    ids.add(q.id);
    if (q.type !== undefined && !['single', 'multi', 'text'].includes(q.type)) invalid(`Unknown question type: ${q.id}`);
    if (q.type === 'text') continue;
    if (!Array.isArray(q.options) || q.options.length < 2 || q.options.length > 6) invalid(`Provide 2–6 options: ${q.id}`);
    const options = new Set();
    const labels = new Set();
    for (const option of q.options) {
      if (!option || typeof option.id !== 'string' || !option.id || options.has(option.id) ||
          typeof option.label !== 'string' || !option.label.trim() || /[\r\n]/.test(option.label) || labels.has(option.label)) {
        invalid(`Options need unique IDs and single-line labels: ${q.id}`);
      }
      options.add(option.id);
      labels.add(option.label);
    }
    if (!Array.isArray(q.recommended) || q.recommended.some((id) => !options.has(id)) ||
        new Set(q.recommended).size !== q.recommended.length || (q.type !== 'multi' && q.recommended.length !== 1)) {
      invalid(`Choose valid recommended option IDs: ${q.id}`);
    }
  }
}

function checkedAnswers(input, answers, complete) {
  if (!Array.isArray(answers)) invalid('Answers must be an array.');
  const ids = new Set();
  const checked = answers.map((answer) => {
    const q = input.questions.find((item) => item.id === answer?.questionId);
    if (!q || ids.has(q.id)) invalid('Unknown or repeated question ID.');
    ids.add(q.id);
    const { picked = [], text = '', skipped = false } = answer;
    if (!Array.isArray(picked) || new Set(picked).size !== picked.length ||
        picked.some((id) => !q.options?.some((option) => option.id === id)) ||
        ((q.type ?? 'single') !== 'multi' && picked.length > 1) || typeof text !== 'string' || typeof skipped !== 'boolean') {
      invalid(`Invalid answer: ${q.id}`);
    }
    if (skipped && (!q.allowSkip || picked.length || text.trim())) invalid(`Cannot skip this answer: ${q.id}`);
    if (complete && !skipped && !picked.length && !text.trim()) invalid(`Answer or explicitly skip: ${q.id}`);
    return { questionId: q.id, picked, text, skipped };
  });
  if (complete && ids.size !== input.questions.length) invalid('Answer every question before submitting.');
  return checked;
}

export function createRound(input, dir) {
  checkInput(input);
  const requestHash = createHash('sha256').update(JSON.stringify(input)).digest('hex');
  mkdirSync(dir, { recursive: true });
  const requestPath = join(dir, 'request.json');
  if (existsSync(requestPath) && JSON.parse(readFileSync(requestPath, 'utf8')).requestHash !== requestHash) {
    invalid('The questions changed. Use a new round directory.', 409);
  }
  const resultPath = join(dir, 'answers.json');
  const draftPath = join(dir, 'draft.json');
  let result = existsSync(resultPath) ? JSON.parse(readFileSync(resultPath, 'utf8')) : null;
  let draft = existsSync(draftPath) ? JSON.parse(readFileSync(draftPath, 'utf8')) : null;
  if ((result && result.requestHash !== requestHash) || (draft && draft.requestHash !== requestHash)) invalid('Stored answers belong to another request. Use a new round directory.', 409);
  if (!existsSync(requestPath)) writeJson(requestPath, { requestHash, input });
  return {
    state: () => ({ input, requestHash, result, draft }),
    saveDraft(value) {
      if (result) invalid('This round has already finished.', 409);
      if (value?.requestHash !== requestHash) invalid('This page belongs to a different round.', 409);
      const next = { requestHash, answers: checkedAnswers(input, value.answers, false) };
      writeJson(draftPath, next);
      draft = next;
      return { status: 'saved' };
    },
    cancel(value) {
      if (value?.requestHash !== requestHash) invalid('This page belongs to a different round.', 409);
      if (result) {
        if (result.status === 'cancelled') return result;
        invalid('This round has already been submitted.', 409);
      }
      const next = { status: 'cancelled', requestHash, submittedAt: new Date().toISOString() };
      writeJson(resultPath, next);
      result = next;
      return result;
    },
    submit(submission) {
      if (submission?.requestHash !== requestHash) invalid('This page belongs to a different round.', 409);
      if (typeof submission.submissionId !== 'string' || !submission.submissionId) invalid('A submission ID is required.');
      const answers = checkedAnswers(input, submission.answers, true);
      if (result) {
        if (result.status === 'submitted' && result.submissionId === submission.submissionId && JSON.stringify(result.answers) === JSON.stringify(answers)) return result;
        invalid('A confirmed answer cannot be replaced. Start a new round.', 409);
      }
      const next = { status: 'submitted', requestHash, submissionId: submission.submissionId,
        answers, submittedAt: new Date().toISOString() };
      writeJson(resultPath, next);
      result = next;
      return result;
    },
  };
}
