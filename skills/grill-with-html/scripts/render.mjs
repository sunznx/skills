import { spawnSync } from 'node:child_process';
import { readFileSync, writeFileSync } from 'node:fs';
import { join } from 'node:path';

export function renderRound(input, dir, renderer) {
  const lines = ['---', `title: ${JSON.stringify(input.title)}`, 'lang: zh', 'template: doc', 'theme: paper', '---'];
  if (input.context) lines.push('', input.context);
  for (const q of input.questions) {
    lines.push('', `## ${q.question}`, '');
    if (q.reviewPlan) lines.push(q.reviewPlan, '');
    if (q.type !== 'text') {
      lines.push(`\`\`\`ask${q.type === 'multi' ? ' multi' : ''}`, q.question);
      for (const option of q.options) {
        lines.push(`${q.recommended.includes(option.id) ? '*' : '-'} ${option.label.replaceAll('|', '\\|')}`);
      }
      lines.push('```');
    }
    if (q.context) lines.push('', q.context);
  }
  const draft = join(dir, 'questions.md');
  const page = join(dir, 'page.html');
  writeFileSync(draft, `${lines.join('\n')}\n`);
  const result = spawnSync(process.execPath, [renderer, 'render', draft, '-o', page, '--no-open'],
    { encoding: 'utf8', timeout: 60000 });
  if (result.status !== 0) throw new Error(`Could not render this round: ${result.error?.message ?? result.stderr ?? result.stdout}`);
  return readFileSync(page, 'utf8');
}
