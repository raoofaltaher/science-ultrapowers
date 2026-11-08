import assert from 'node:assert/strict';
import { spawnSync } from 'node:child_process';
import { mkdirSync, mkdtempSync, rmSync, symlinkSync, writeFileSync } from 'node:fs';
import { tmpdir } from 'node:os';
import { dirname, join } from 'node:path';
import { fileURLToPath } from 'node:url';
import test from 'node:test';

import { lintStore, CODES } from '../memory-lint.mjs';

const SCRIPT = fileURLToPath(new URL('../memory-lint.mjs', import.meta.url));
const FENCE = '`'.repeat(3);
const BODY = 'A durable fact.\n\n**Why:** reason.\n\n**How to apply:** action.\n';

function runCli(args) {
  const r = spawnSync(process.execPath, [SCRIPT, ...args], { encoding: 'utf8' });
  return { code: r.status, stdout: r.stdout, stderr: r.stderr };
}

// A fresh <tmp>/research_lab/memory/ folder, removed when the test ends.
function makeStore(t) {
  const root = mkdtempSync(join(tmpdir(), 'memlint-'));
  const store = join(root, 'research_lab', 'memory');
  mkdirSync(store, { recursive: true });
  t.after(() => rmSync(root, { recursive: true, force: true }));
  return { root, store };
}

function entry({
  name, type = 'lesson', entity = 'project', basis = 'observed', basisKey = 'basis',
  learned_by = 'literature-researcher', origin = 'agent', date = '2026-11-07', note, body = BODY,
}) {
  return [
    '---',
    `name: ${name}`,
    'description: a one-line description',
    'metadata:',
    `  type: ${type}`,
    `  entity: ${entity}`,
    `  ${basisKey}: ${basis}`,
    `  learned_by: ${learned_by}`,
    `  origin: ${origin}`,
    `date: ${date}`,
    ...(note === undefined ? [] : [`note: ${note}`]),
    '---',
    body,
  ].join('\n');
}

// One valid index line for an entry path such as project/alpha-fact.md.
function line(rel, hook = 'a one-line hook') {
  const title = rel.split('/').pop().replace(/\.md$/, '');
  return `- [${title}](${rel}) — ${hook} (2026-11)`;
}

// The full index: a heading, then exactly the lines given.
function indexOf(...lines) {
  return ['# Lab memory: index', '', '## Entries', ...lines, ''];
}

// index is the full list of MEMORY.md lines; entries maps a store-relative
// path to the entry text.
function writeStore(store, { index = indexOf(), entries = {} } = {}) {
  writeFileSync(join(store, 'MEMORY.md'), index.join('\n'));
  for (const [rel, text] of Object.entries(entries)) {
    mkdirSync(dirname(join(store, rel)), { recursive: true });
    writeFileSync(join(store, rel), text);
  }
}

// A store whose entries are all indexed with a valid line.
function writeIndexed(store, entries) {
  writeStore(store, { index: indexOf(...Object.keys(entries).map((rel) => line(rel))), entries });
}

const codes = (findings) => findings.map((f) => f.code).sort();

test('clean store exits 0', (t) => {
  const { store } = makeStore(t);
  writeIndexed(store, {
    'project/alpha-fact.md': entry({ name: 'alpha-fact' }),
    'artifact/abc123/beta-fact.md': entry({ name: 'beta-fact', entity: 'artifact:abc123' }),
  });
  const r = runCli([store]);
  assert.equal(r.code, 0);
  assert.equal(r.stdout, '');
});

test('BUDGET when index lines exceed budget', (t) => {
  const { store } = makeStore(t);
  writeIndexed(store, {
    'project/one-fact.md': entry({ name: 'one-fact' }),
    'project/two-fact.md': entry({ name: 'two-fact' }),
    'project/three-fact.md': entry({ name: 'three-fact' }),
  });
  const r = runCli([store, '--budget', '2']);
  assert.equal(r.code, 1);
  assert.match(r.stdout, /^BUDGET MEMORY\.md:/m);
  assert.match(r.stdout, /the index has 6 lines, the limit is 2/);
});

test('DANGLING index link to missing file', (t) => {
  const { store } = makeStore(t);
  writeStore(store, { index: indexOf(line('project/gone-fact.md')) });
  const f = lintStore(store);
  assert.deepEqual(codes(f), ['DANGLING']);
  assert.equal(f[0].path, 'MEMORY.md:4');
});

test('ORPHAN entry without index line', (t) => {
  const { store } = makeStore(t);
  writeStore(store, { entries: { 'project/lonely-fact.md': entry({ name: 'lonely-fact' }) } });
  const f = lintStore(store);
  assert.deepEqual(codes(f), ['ORPHAN']);
  assert.equal(f[0].path, 'project/lonely-fact.md');
});

test('STRAY file at store root', (t) => {
  const { store } = makeStore(t);
  writeStore(store, { entries: { 'notes.md': '# notes\n' } });
  const f = lintStore(store);
  assert.deepEqual(codes(f), ['STRAY']);
  assert.equal(f[0].path, 'notes.md');
});

test('FM_KEYS when metadata lacks learned_by', (t) => {
  const { store } = makeStore(t);
  const text = entry({ name: 'alpha-fact' }).replace('  learned_by: literature-researcher\n', '');
  writeIndexed(store, { 'project/alpha-fact.md': text });
  const f = lintStore(store);
  assert.ok(codes(f).includes('FM_KEYS'));
  assert.match(f.find((x) => x.code === 'FM_KEYS').message, /metadata keys are \[type, entity, basis, origin\]/);
});

test('FM_TYPE on unknown type', (t) => {
  const { store } = makeStore(t);
  writeIndexed(store, { 'project/alpha-fact.md': entry({ name: 'alpha-fact', type: 'subsystem' }) });
  assert.deepEqual(codes(lintStore(store)), ['FM_TYPE']);
});

test('FM_BASIS on unknown basis', (t) => {
  const { store } = makeStore(t);
  writeIndexed(store, { 'project/alpha-fact.md': entry({ name: 'alpha-fact', basis: 'guessed' }) });
  const f = lintStore(store);
  assert.deepEqual(codes(f), ['FM_BASIS']);
  assert.match(f[0].message, /the basis "guessed" is not stated, observed or inferred/);
});

test('FM_ORIGIN on unknown origin', (t) => {
  const { store } = makeStore(t);
  writeIndexed(store, { 'project/alpha-fact.md': entry({ name: 'alpha-fact', origin: 'chat' }) });
  assert.deepEqual(codes(lintStore(store)), ['FM_ORIGIN']);
});

test('FM_LEARNED_BY when empty', (t) => {
  const { store } = makeStore(t);
  writeIndexed(store, { 'project/alpha-fact.md': entry({ name: 'alpha-fact', learned_by: '' }).replace('learned_by: \n', 'learned_by:\n') });
  assert.deepEqual(codes(lintStore(store)), ['FM_LEARNED_BY']);
});

test('FM_ENTITY on profile', (t) => {
  const { store } = makeStore(t);
  writeIndexed(store, { 'project/alpha-fact.md': entry({ name: 'alpha-fact', entity: 'profile' }) });
  const f = lintStore(store);
  assert.deepEqual(codes(f), ['FM_ENTITY']);
  assert.match(f[0].message, /user memory/);
});

test('FM_ENTITY_DIR when entity artifact:x lives under project/', (t) => {
  const { store } = makeStore(t);
  writeIndexed(store, { 'project/alpha-fact.md': entry({ name: 'alpha-fact', entity: 'artifact:x' }) });
  const f = lintStore(store);
  assert.deepEqual(codes(f), ['FM_ENTITY_DIR']);
  assert.match(f[0].message, /move it to artifact\/x\//);
});

test('FM_DATE on 2026/11/07', (t) => {
  const { store } = makeStore(t);
  writeIndexed(store, { 'project/alpha-fact.md': entry({ name: 'alpha-fact', date: '2026/11/07' }) });
  assert.deepEqual(codes(lintStore(store)), ['FM_DATE']);
});

test('WIKILINK to missing name', (t) => {
  const { store } = makeStore(t);
  writeIndexed(store, {
    'project/alpha-fact.md': entry({ name: 'alpha-fact', body: 'See [[nowhere-fact]].\n\n**Why:** r.\n\n**How to apply:** a.\n' }),
  });
  assert.deepEqual(codes(lintStore(store)), ['WIKILINK']);
});

test('NEAR_DUP on names differing by trailing s', (t) => {
  const { store } = makeStore(t);
  writeIndexed(store, {
    'project/cache-key.md': entry({ name: 'cache-key' }),
    'project/cache-keys.md': entry({ name: 'cache-keys' }),
  });
  assert.deepEqual(codes(lintStore(store)), ['NEAR_DUP']);
});

test('RECORD_ONLY when the body is just a record id', (t) => {
  const { store } = makeStore(t);
  const wrap = (id) => `${id}\n\n**Why:** r.\n\n**How to apply:** a.\n`;
  writeIndexed(store, {
    'project/first-fact.md': entry({ name: 'first-fact', body: wrap('F-0031') }),
    'project/second-fact.md': entry({ name: 'second-fact', body: wrap('see D-0124.') }),
    'project/third-fact.md': entry({ name: 'third-fact', body: wrap('EC-0042') }),
  });
  const f = lintStore(store);
  assert.deepEqual(codes(f), ['RECORD_ONLY', 'RECORD_ONLY', 'RECORD_ONLY']);
  assert.deepEqual(f.map((x) => x.path).sort(), ['project/first-fact.md', 'project/second-fact.md', 'project/third-fact.md']);
});

test('RECORD_ONLY is not raised for a fact that mentions a record', (t) => {
  const { store } = makeStore(t);
  writeIndexed(store, {
    'project/alpha-fact.md': entry({ name: 'alpha-fact', body: 'The tokenizer upcasts to fp32 on CPU, see F-0031.\n\n**Why:** r.\n\n**How to apply:** a.\n' }),
  });
  assert.deepEqual(lintStore(store), []);
});

test('budget read from lab.json when --budget absent', (t) => {
  const { root, store } = makeStore(t);
  writeFileSync(join(root, 'research_lab', 'lab.json'), '{"memory":{"indexBudget":1}}');
  writeIndexed(store, {
    'project/one-fact.md': entry({ name: 'one-fact' }),
    'project/two-fact.md': entry({ name: 'two-fact' }),
  });
  const r = runCli([store]);
  assert.equal(r.code, 1);
  assert.match(r.stdout, /^BUDGET MEMORY\.md:/m);
});

test('optional note is accepted', (t) => {
  const { store } = makeStore(t);
  writeIndexed(store, { 'project/alpha-fact.md': entry({ name: 'alpha-fact', note: 'free text, with: a colon' }) });
  assert.deepEqual(lintStore(store), []);
});

test('FM_KEYS on wrong top-level order', (t) => {
  const { store } = makeStore(t);
  const text = [
    '---',
    'name: alpha-fact',
    'description: d',
    'date: 2026-11-07',
    'metadata:',
    '  type: lesson',
    '  entity: project',
    '  basis: observed',
    '  learned_by: unknown',
    '  origin: agent',
    '---',
    BODY,
  ].join('\n');
  writeIndexed(store, { 'project/alpha-fact.md': text });
  const f = lintStore(store);
  assert.deepEqual(codes(f), ['FM_KEYS']);
  assert.match(f[0].message, /keys are \[name, description, date, metadata\]/);
});

test('FM_KEYS on wrong metadata order', (t) => {
  const { store } = makeStore(t);
  const text = [
    '---',
    'name: alpha-fact',
    'description: d',
    'metadata:',
    '  type: lesson',
    '  basis: observed',
    '  entity: project',
    '  learned_by: unknown',
    '  origin: agent',
    'date: 2026-11-07',
    '---',
    BODY,
  ].join('\n');
  writeIndexed(store, { 'project/alpha-fact.md': text });
  const f = lintStore(store);
  assert.deepEqual(codes(f), ['FM_KEYS']);
  assert.match(f[0].message, /metadata keys are \[type, basis, entity, learned_by, origin\]/);
});

test('FM_ENTITY_DIR for artifact folder mismatch', (t) => {
  const { store } = makeStore(t);
  writeIndexed(store, {
    'artifact/abc/x-fact.md': entry({ name: 'x-fact', entity: 'artifact:other' }),
    'artifact/abc/y-fact.md': entry({ name: 'y-fact', entity: 'project' }),
  });
  const f = lintStore(store);
  assert.deepEqual(codes(f), ['FM_ENTITY_DIR', 'FM_ENTITY_DIR']);
  assert.ok(f.some((x) => /move it to artifact\/other\//.test(x.message)));
  assert.ok(f.some((x) => /move it to project\//.test(x.message)));
});

test('STRAY layout cases', (t) => {
  const { store } = makeStore(t);
  writeStore(store, { entries: { 'artifact/loose.md': 'x\n', 'project/notes.txt': 'x\n' } });
  mkdirSync(join(store, 'project', 'sub'));
  mkdirSync(join(store, 'artifact', 'bad id'));
  const f = lintStore(store);
  assert.deepEqual(codes(f), ['STRAY', 'STRAY', 'STRAY', 'STRAY']);
  assert.deepEqual(f.map((x) => x.path).sort(), ['artifact/bad id/', 'artifact/loose.md', 'project/notes.txt', 'project/sub/']);
});

test('dot files are ignored in the layout scan', (t) => {
  const { store } = makeStore(t);
  writeStore(store, { entries: { 'project/.gitkeep': '', 'artifact/.gitkeep': '' } });
  assert.deepEqual(lintStore(store), []);
});

test('RECORD_ONLY on an index line that only cites a record', (t) => {
  const { store } = makeStore(t);
  writeStore(store, {
    index: indexOf(line('project/alpha-fact.md', 'F-0031')),
    entries: { 'project/alpha-fact.md': entry({ name: 'alpha-fact' }) },
  });
  const f = lintStore(store);
  assert.deepEqual(codes(f), ['RECORD_ONLY']);
  assert.equal(f[0].path, 'MEMORY.md:4');
});

test('fenced body holding only a record id is RECORD_ONLY', (t) => {
  const { store } = makeStore(t);
  const body = `${FENCE}\nEC-0042\n${FENCE}\n\n**Why:** r.\n\n**How to apply:** a.\n`;
  writeIndexed(store, { 'project/alpha-fact.md': entry({ name: 'alpha-fact', body }) });
  assert.deepEqual(codes(lintStore(store)), ['RECORD_ONLY']);
});

test('fenced body holding a real sentence is clean', (t) => {
  const { store } = makeStore(t);
  const body = `${FENCE}\nThe sampler seeds itself from the wall clock.\n${FENCE}\n\n**Why:** r.\n\n**How to apply:** a.\n`;
  writeIndexed(store, { 'project/alpha-fact.md': entry({ name: 'alpha-fact', body }) });
  assert.deepEqual(lintStore(store), []);
});

test('FM_LEARNED_BY on a role with spaces', (t) => {
  const { store } = makeStore(t);
  writeIndexed(store, { 'project/alpha-fact.md': entry({ name: 'alpha-fact', learned_by: 'Literature Researcher' }) });
  assert.deepEqual(codes(lintStore(store)), ['FM_LEARNED_BY']);
});

test('unknown is accepted as learned_by', (t) => {
  const { store } = makeStore(t);
  writeIndexed(store, { 'project/alpha-fact.md': entry({ name: 'alpha-fact', learned_by: 'unknown' }) });
  assert.deepEqual(lintStore(store), []);
});

test('usage error: no store argument exits 2', () => {
  const r = runCli([]);
  assert.equal(r.code, 2);
  assert.match(r.stderr, /Usage: node memory-lint\.mjs <store-dir> \[--budget N\]/);
});

test('usage error: --budget 0 exits 2', (t) => {
  const { store } = makeStore(t);
  writeStore(store);
  const r = runCli([store, '--budget', '0']);
  assert.equal(r.code, 2);
});

test('FM_MISSING when MEMORY.md is absent', (t) => {
  const { store } = makeStore(t);
  const f = lintStore(store);
  assert.deepEqual(codes(f), ['FM_MISSING']);
  assert.equal(f[0].path, 'MEMORY.md');
});

test('CODES lists the eighteen codes', () => {
  assert.deepEqual([...CODES], [
    'BUDGET', 'DANGLING', 'ORPHAN', 'STRAY',
    'FM_MISSING', 'FM_KEYS', 'FM_NAME', 'FM_TYPE', 'FM_ENTITY', 'FM_ENTITY_DIR',
    'FM_BASIS', 'FM_LEARNED_BY', 'FM_ORIGIN', 'FM_DATE',
    'WIKILINK', 'NEAR_DUP', 'RECORD_ONLY', 'NO_FACT',
  ]);
});

test('the CLI runs when invoked through a junction or symlink to its folder', (t) => {
  const { root, store } = makeStore(t);
  // A store with a problem: MEMORY.md is missing, so a working CLI exits 1.
  const linkDir = join(root, 'linked-scripts');
  // 'junction' needs no privilege on Windows; elsewhere it is an ordinary symlink.
  symlinkSync(dirname(SCRIPT), linkDir, 'junction');
  const r = spawnSync(process.execPath, [join(linkDir, 'memory-lint.mjs'), store], { encoding: 'utf8' });
  assert.equal(r.status, 1, `stdout: ${r.stdout} stderr: ${r.stderr}`);
  assert.match(r.stdout, /^FM_MISSING MEMORY\.md:/);
});

// ---- final-review fix pass L ----

const wrapBody = (fact) => `${fact}\n\n**Why:** r.\n\n**How to apply:** a.\n`;

// L1
test('a file named project or artifact is STRAY, not a crash', (t) => {
  const { store } = makeStore(t);
  writeStore(store, { entries: { project: 'x\n', artifact: 'x\n' } });
  const r = runCli([store]);
  assert.equal(r.code, 1);
  assert.match(r.stdout, /^STRAY project:/m);
  assert.match(r.stdout, /^STRAY artifact:/m);
  assert.doesNotMatch(r.stderr, /Error/);
});

// L2
test('NEAR_DUP is not raised for names that differ by non-ASCII letters', (t) => {
  const { store } = makeStore(t);
  writeIndexed(store, {
    'project/größe-fact.md': entry({ name: 'größe-fact' }),
    'project/gre-fact.md': entry({ name: 'gre-fact' }),
  });
  assert.ok(!codes(lintStore(store)).includes('NEAR_DUP'));
});

// L3
test('budget from lab.json when the store is reached through a junction', (t) => {
  const { root, store } = makeStore(t);
  writeFileSync(join(root, 'research_lab', 'lab.json'), '{"memory":{"indexBudget":2}}');
  writeIndexed(store, {
    'project/one-fact.md': entry({ name: 'one-fact' }),
  });
  const linked = join(root, 'jmem');
  symlinkSync(store, linked, 'junction');
  const r = runCli([linked]);
  assert.equal(r.code, 1);
  assert.match(r.stdout, /^BUDGET MEMORY\.md:/m);
});

// L4
test('--budget=N is accepted', (t) => {
  const { store } = makeStore(t);
  writeIndexed(store, {
    'project/one-fact.md': entry({ name: 'one-fact' }),
    'project/two-fact.md': entry({ name: 'two-fact' }),
    'project/three-fact.md': entry({ name: 'three-fact' }),
  });
  const r = runCli([store, '--budget=2']);
  assert.equal(r.code, 1);
  assert.match(r.stdout, /^BUDGET MEMORY\.md:/m);
});

test('unknown option exits 2', (t) => {
  const { store } = makeStore(t);
  writeStore(store);
  const r = runCli(['--bogus', store]);
  assert.equal(r.code, 2);
  assert.match(r.stderr, /Usage: node memory-lint\.mjs/);
});

test('two store arguments exit 2', (t) => {
  const { store } = makeStore(t);
  writeStore(store);
  const r = runCli([store, store]);
  assert.equal(r.code, 2);
  assert.match(r.stderr, /Usage: node memory-lint\.mjs/);
});

test('a missing store directory exits 2', (t) => {
  const { root } = makeStore(t);
  const r = runCli([join(root, 'no-such-store')]);
  assert.equal(r.code, 2);
  assert.match(r.stderr, /no such store directory/);
  assert.equal(r.stdout, '');
});

// L5
test('a UTF-8 BOM before the frontmatter is accepted', (t) => {
  const { store } = makeStore(t);
  writeIndexed(store, { 'project/alpha-fact.md': `${String.fromCharCode(0xfeff)}${entry({ name: 'alpha-fact' })}` });
  assert.deepEqual(lintStore(store), []);
});

// L6
test('FM_NAME when the name differs from the file name', (t) => {
  const { store } = makeStore(t);
  writeIndexed(store, { 'project/alpha-fact.md': entry({ name: 'beta-fact' }) });
  const f = lintStore(store);
  assert.deepEqual(codes(f), ['FM_NAME']);
  assert.match(f[0].message, /differs from the file name "alpha-fact"/);
});

test('FM_NAME on a name that is not a kebab-case slug', (t) => {
  const { store } = makeStore(t);
  writeIndexed(store, { 'project/My Fact!.md': entry({ name: 'My Fact!' }) });
  const f = lintStore(store);
  assert.deepEqual(codes(f), ['FM_NAME']);
  assert.match(f[0].message, /name "My Fact!" is not a kebab-case slug/);
});

// L7
test('RECORD_ONLY on id lists and named records', (t) => {
  const { store } = makeStore(t);
  writeIndexed(store, {
    'project/first-fact.md': entry({ name: 'first-fact', body: wrapBody('D-0124 and F-0031') }),
    'project/second-fact.md': entry({ name: 'second-fact', body: wrapBody('See decision D-0124') }),
    'project/third-fact.md': entry({ name: 'third-fact', body: wrapBody('cf. F-0031, F-0032.') }),
  });
  const f = lintStore(store);
  assert.deepEqual(codes(f), ['RECORD_ONLY', 'RECORD_ONLY', 'RECORD_ONLY']);
});

test('RECORD_ONLY is not raised for a sentence that cites a record', (t) => {
  const { store } = makeStore(t);
  writeIndexed(store, {
    'project/alpha-fact.md': entry({ name: 'alpha-fact', body: wrapBody('see F-0031 for why we upcast') }),
  });
  assert.deepEqual(lintStore(store), []);
});

test('NO_FACT on a body with only Why and How to apply lines', (t) => {
  const { store } = makeStore(t);
  writeIndexed(store, {
    'project/alpha-fact.md': entry({ name: 'alpha-fact', body: '**Why:** r.\n\n**How to apply:** a.\n' }),
  });
  const f = lintStore(store);
  assert.deepEqual(codes(f), ['NO_FACT']);
  assert.match(f[0].message, /states no fact, only Why and How to apply lines/);
});

test('NO_FACT on an empty body', (t) => {
  const { store } = makeStore(t);
  writeIndexed(store, { 'project/alpha-fact.md': entry({ name: 'alpha-fact', body: '' }) });
  assert.deepEqual(codes(lintStore(store)), ['NO_FACT']);
});

// L8
test('BUDGET on a non-integer indexBudget in lab.json', (t) => {
  const { root, store } = makeStore(t);
  writeFileSync(join(root, 'research_lab', 'lab.json'), '{"memory":{"indexBudget":"1"}}');
  writeIndexed(store, { 'project/alpha-fact.md': entry({ name: 'alpha-fact' }) });
  const f = lintStore(store);
  assert.deepEqual(codes(f), ['BUDGET']);
  assert.equal(f[0].path, 'lab.json');
  assert.match(f[0].message, /memory\.indexBudget "1" is not a positive integer; the default limit of 150 applies/);
});

test('BUDGET on a lab.json that is not JSON', (t) => {
  const { root, store } = makeStore(t);
  writeFileSync(join(root, 'research_lab', 'lab.json'), '{not json');
  writeIndexed(store, { 'project/alpha-fact.md': entry({ name: 'alpha-fact' }) });
  const f = lintStore(store);
  assert.deepEqual(codes(f), ['BUDGET']);
  assert.match(f[0].message, /not valid JSON; the default limit of 150 applies/);
});

// L9
test('a ./-prefixed index link counts as the entry\'s line', (t) => {
  const { store } = makeStore(t);
  writeStore(store, {
    index: indexOf('- [alpha-fact](./project/alpha-fact.md) — a one-line hook (2026-11)'),
    entries: { 'project/alpha-fact.md': entry({ name: 'alpha-fact' }) },
  });
  assert.deepEqual(lintStore(store), []);
});

test('a case-different index link is DANGLING on every platform, without an ORPHAN', (t) => {
  const { store } = makeStore(t);
  writeStore(store, {
    index: indexOf('- [alpha-fact](project/Alpha-Fact.md) — a one-line hook (2026-11)'),
    entries: { 'project/alpha-fact.md': entry({ name: 'alpha-fact' }) },
  });
  const f = lintStore(store);
  assert.deepEqual(codes(f), ['DANGLING']);
  assert.match(f[0].message, /link target project\/Alpha-Fact\.md differs in case from project\/alpha-fact\.md/);
});

// L10
test('a CRLF store lints clean', (t) => {
  const { store } = makeStore(t);
  writeStore(store, {
    index: indexOf(line('project/alpha-fact.md')),
    entries: { 'project/alpha-fact.md': entry({ name: 'alpha-fact' }).replace(/\n/g, '\r\n') },
  });
  writeFileSync(join(store, 'MEMORY.md'), indexOf(line('project/alpha-fact.md')).join('\r\n'));
  assert.deepEqual(lintStore(store), []);
});

test('RECORD_ONLY on a CRLF record-only body', (t) => {
  const { store } = makeStore(t);
  writeIndexed(store, {
    'project/alpha-fact.md': entry({ name: 'alpha-fact', body: wrapBody('F-0031') }).replace(/\n/g, '\r\n'),
  });
  assert.deepEqual(codes(lintStore(store)), ['RECORD_ONLY']);
});

test('RECORD_ONLY on an index line with an UPDATED fold', (t) => {
  const { store } = makeStore(t);
  writeStore(store, {
    index: indexOf('- [Alpha fact](project/alpha-fact.md) — F-0031 **UPDATED 2026-11-08: still F-0031** (2026-11)'),
    entries: { 'project/alpha-fact.md': entry({ name: 'alpha-fact' }) },
  });
  const f = lintStore(store);
  assert.deepEqual(codes(f), ['RECORD_ONLY']);
  assert.equal(f[0].path, 'MEMORY.md:4');
});

test('FM_KEYS when note is not last', (t) => {
  const { store } = makeStore(t);
  const text = [
    '---',
    'name: alpha-fact',
    'description: d',
    'metadata:',
    '  type: lesson',
    '  entity: project',
    '  basis: observed',
    '  learned_by: unknown',
    '  origin: agent',
    'note: a note',
    'date: 2026-11-07',
    '---',
    BODY,
  ].join('\n');
  writeIndexed(store, { 'project/alpha-fact.md': text });
  const f = lintStore(store);
  assert.deepEqual(codes(f), ['FM_KEYS']);
  assert.match(f[0].message, /keys are \[name, description, metadata, note, date\]/);
});

// ---- the terminology pass: basis, pitfall, consistency check ----

test('the legacy evidence key is read without a finding', (t) => {
  const { store } = makeStore(t);
  writeIndexed(store, {
    'project/alpha-fact.md': entry({ name: 'alpha-fact', basisKey: 'evidence', basis: 'stated' }),
  });
  assert.deepEqual(lintStore(store), []);
});

test('FM_BASIS on an unknown value under the legacy evidence key', (t) => {
  const { store } = makeStore(t);
  writeIndexed(store, {
    'project/alpha-fact.md': entry({ name: 'alpha-fact', basisKey: 'evidence', basis: 'guessed' }),
  });
  const f = lintStore(store);
  assert.deepEqual(codes(f), ['FM_BASIS']);
  assert.match(f[0].message, /"guessed" is not stated, observed or inferred/);
});

test('FM_KEYS when both basis and evidence are present', (t) => {
  const { store } = makeStore(t);
  const text = entry({ name: 'alpha-fact' }).replace('  basis: observed\n', '  basis: observed\n  evidence: observed\n');
  writeIndexed(store, { 'project/alpha-fact.md': text });
  assert.ok(codes(lintStore(store)).includes('FM_KEYS'));
});

test('type pitfall is accepted', (t) => {
  const { store } = makeStore(t);
  writeIndexed(store, { 'project/alpha-fact.md': entry({ name: 'alpha-fact', type: 'pitfall' }) });
  assert.deepEqual(lintStore(store), []);
});

test('the legacy type gotcha is read without a finding', (t) => {
  const { store } = makeStore(t);
  writeIndexed(store, { 'project/alpha-fact.md': entry({ name: 'alpha-fact', type: 'gotcha' }) });
  assert.deepEqual(lintStore(store), []);
});

test('FM_TYPE names pitfall, not gotcha', (t) => {
  const { store } = makeStore(t);
  writeIndexed(store, { 'project/alpha-fact.md': entry({ name: 'alpha-fact', type: 'subsystem' }) });
  const f = lintStore(store);
  assert.deepEqual(codes(f), ['FM_TYPE']);
  assert.match(f[0].message, /is not pitfall, decision, lesson, directive or vocabulary/);
  assert.doesNotMatch(f[0].message, /gotcha/);
});

test('RECORD_ONLY on the new record ids and the legacy ones', (t) => {
  const { store } = makeStore(t);
  writeIndexed(store, {
    'project/first-fact.md': entry({ name: 'first-fact', body: wrapBody('FND-1031') }),
    'project/second-fact.md': entry({ name: 'second-fact', body: wrapBody('see DEC-0124 and EVR-0042') }),
    'project/third-fact.md': entry({ name: 'third-fact', body: wrapBody('TASK-0007') }),
    'project/fourth-fact.md': entry({ name: 'fourth-fact', body: wrapBody('D-12') }),
  });
  assert.deepEqual(codes(lintStore(store)), ['RECORD_ONLY', 'RECORD_ONLY', 'RECORD_ONLY', 'RECORD_ONLY']);
});

test('every finding message is a plain sentence beside its code', (t) => {
  const { store } = makeStore(t);
  writeStore(store, {
    index: indexOf(line('project/gone-fact.md')),
    entries: { 'project/alpha-fact.md': entry({ name: 'alpha-fact', basis: 'guessed' }), 'notes.md': 'x\n' },
  });
  const r = runCli([store, '--budget', '1']);
  assert.equal(r.code, 1);
  assert.match(r.stdout, /^BUDGET MEMORY\.md: the index has 4 lines, the limit is 1$/m);
  assert.match(r.stdout, /^DANGLING MEMORY\.md:4: the link target project\/gone-fact\.md does not exist$/m);
  assert.match(r.stdout, /^ORPHAN project\/alpha-fact\.md: the entry has no index line$/m);
  assert.match(r.stdout, /^STRAY notes\.md: only README\.md and MEMORY\.md may live at the store root$/m);
  assert.match(r.stdout, /^FM_BASIS project\/alpha-fact\.md: the basis "guessed" is not stated, observed or inferred$/m);
});

test('--help prints the usage in the new words and exits 0', () => {
  const r = runCli(['--help']);
  assert.equal(r.code, 0);
  assert.match(r.stdout, /Usage: node memory-lint\.mjs <store-dir> \[--budget N\]/);
  assert.match(r.stdout, /consistency check/);
  assert.match(r.stdout, /basis/);
  // The script's own file name is the only place the old word may stay.
  assert.doesNotMatch(r.stdout.replaceAll('memory-lint.mjs', ''), /lint/i);
});

test('a missing store directory is reported as a consistency check problem', (t) => {
  const { root } = makeStore(t);
  const r = runCli([join(root, 'no-such-store')]);
  assert.equal(r.code, 2);
  assert.match(r.stderr, /memory consistency check: no such store directory/);
  assert.doesNotMatch(r.stderr, /\blint\b/i);
});
