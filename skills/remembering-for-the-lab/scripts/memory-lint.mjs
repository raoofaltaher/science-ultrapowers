#!/usr/bin/env node
// The lab memory consistency check: structural checks for the lab memory store
// (research_lab/memory). The script keeps the file name memory-lint.mjs.
//
// Node standard library only. Owns the lab memory entry schema, so the skill,
// the hooks and every role that writes an entry check it one way: entity
// scope (project or artifact:<id>), basis (stated, observed or inferred),
// learned_by, origin, and the rule that an entry must not merely cite a lab
// record. The legacy frontmatter key "evidence" and the legacy type "gotcha" // legacy
// are read without a finding.
//
// Usage: node memory-lint.mjs <store-dir> [--budget N]
// Output: one line per finding, "<CODE> <path>: <message>", the message a
// plain sentence.
// Exit: 0 clean, 1 findings, 2 usage error.

import { existsSync, readdirSync, readFileSync, realpathSync, statSync } from 'node:fs';
import { join, posix, resolve } from 'node:path';
import { fileURLToPath } from 'node:url';

export const CODES = Object.freeze([
  'BUDGET', 'DANGLING', 'ORPHAN', 'STRAY',
  'FM_MISSING', 'FM_KEYS', 'FM_NAME', 'FM_TYPE', 'FM_ENTITY', 'FM_ENTITY_DIR',
  'FM_BASIS', 'FM_LEARNED_BY', 'FM_ORIGIN', 'FM_DATE',
  'WIKILINK', 'NEAR_DUP', 'RECORD_ONLY', 'NO_FACT',
]);

const TYPES = Object.freeze(['pitfall', 'decision', 'lesson', 'directive', 'vocabulary']);
// Read as legacy, never reported: entries imported from Claude Science carry
// type gotcha and the metadata key evidence.
const LEGACY_TYPES = Object.freeze(['gotcha']); // legacy
const BASES = Object.freeze(['stated', 'observed', 'inferred']);
const ORIGINS = Object.freeze(['agent', 'extractor', 'user', 'import']);
const TOP_KEYS = Object.freeze(['name', 'description', 'metadata', 'date']);
const META_KEYS = Object.freeze(['type', 'entity', 'basis', 'learned_by', 'origin']);
const LEGACY_META_KEYS = Object.freeze(['type', 'entity', 'evidence', 'learned_by', 'origin']);
const ROLE_RE = /^[a-z0-9]+(-[a-z0-9]+)*$/;
const ENTITY_RE = /^(project|artifact:([A-Za-z0-9_-]+))$/;
const ARTIFACT_ID_RE = /^[A-Za-z0-9_-]+$/;
const NAME_RE = /^[a-z0-9]+(-[a-z0-9]+)*$/;
// A line that is nothing but one or more lab record ids, optionally introduced
// ("see", "cf.", "per", "the decision") and joined by , ; & / or "and".
const ID = '(?:FND|HYP|EVR|REV|DEC|TASK|MTH|RSK|ADH|ADV|REQ|EXP|F|D|EC|RV|T|MP|R|DA|PC|H)-\\d+';
const RECORD_LINE_RE = new RegExp(
  `^(?:(?:see|cf\\.?|per)\\s+)?(?:(?:the\\s+)?(?:decision|finding|record|review|exception|request|task|experiment|hypothesis|risk)s?\\s+)?${ID}(?:\\s*(?:,|;|&|\\/|\\band\\b)\\s*${ID})*\\.?$`,
  'i',
);
const BOM = String.fromCharCode(0xfeff);
const stripBom = (text) => (text.startsWith(BOM) ? text.slice(1) : text);
const TOP_LEVEL_FILES = new Set(['README.md', 'MEMORY.md']);
// Files an operating system or editor drops next to a collaborator's files.
const OS_FILES = new Set(['Thumbs.db', 'desktop.ini']);
const DEFAULT_BUDGET = 150;
const FRONTMATTER_RE = /^---\r?\n([\s\S]*?)\r?\n---(?:\r?\n|$)/;
const INDEX_LINK_RE = /^- \[[^\]]+\]\(([^)]+)\)/;
const WIKILINK_RE = /\[\[([^\]]+)\]\]/g;

// Minimal YAML subset: top-level "key: value" scalars and one level of
// indented "  key: value" under a key with no value. Values lose one pair of
// surrounding quotes. Keys keep their insertion order. Returns null without a
// block; malformed names the first line that fits neither shape.
export function parseFrontmatter(text) {
  const match = FRONTMATTER_RE.exec(stripBom(text));
  if (!match) return null;
  const data = {};
  let parent = null;
  for (const raw of match[1].split(/\r?\n/)) {
    if (raw.trim() === '') continue;
    const nested = /^ {2,}([^\s:][^:]*):\s*(.*)$/.exec(raw);
    if (nested && parent !== null) {
      data[parent][nested[1].trim()] = unquote(nested[2]);
      continue;
    }
    const top = /^([^\s:][^:]*):\s*(.*)$/.exec(raw);
    if (!top) return { data, malformed: raw };
    const key = top[1].trim();
    const value = top[2].trim();
    if (value === '') {
      data[key] = {};
      parent = key;
    } else {
      data[key] = unquote(value);
      parent = null;
    }
  }
  return { data, malformed: null };
}

function unquote(value) {
  const v = value.trim();
  return v.replace(/^(["'])(.*)\1$/, '$2');
}

function isIsoDate(value) {
  if (typeof value !== 'string' || !/^\d{4}-\d{2}-\d{2}$/.test(value)) return false;
  const parsed = new Date(`${value}T00:00:00Z`);
  return !Number.isNaN(parsed.getTime()) && parsed.toISOString().slice(0, 10) === value;
}

function normalizeName(name) {
  return name.normalize('NFKD').toLowerCase().replace(/\p{M}/gu, '').replace(/[^\p{L}\p{N}]/gu, '').replace(/s$/u, '');
}

// The index budget from <store>/../lab.json, found through the real path so a
// junction or symlink to memory/ still reaches its lab folder. problem is set
// when lab.json exists but cannot be used; the default budget applies then.
function readBudget(store) {
  let base = store;
  try { base = realpathSync(store); } catch { /* keep the path as given */ }
  const configPath = resolve(base, '..', 'lab.json');
  if (!existsSync(configPath)) return { budget: DEFAULT_BUDGET, problem: null };
  let config;
  try {
    config = JSON.parse(readFileSync(configPath, 'utf8'));
  } catch {
    return { budget: DEFAULT_BUDGET, problem: 'not valid JSON' };
  }
  const value = config?.memory?.indexBudget;
  if (value === undefined) return { budget: DEFAULT_BUDGET, problem: null };
  if (Number.isInteger(value) && value > 0) return { budget: value, problem: null };
  return { budget: DEFAULT_BUDGET, problem: `memory.indexBudget ${JSON.stringify(value)} is not a positive integer` };
}

function splitLines(text) {
  const lines = stripBom(text).split(/\r?\n/);
  if (lines.length && lines[lines.length - 1] === '') lines.pop();
  return lines;
}

function bodyOf(text) {
  const clean = stripBom(text);
  const match = FRONTMATTER_RE.exec(clean);
  return match ? clean.slice(match[0].length) : clean;
}

const isDir = (p) => {
  try { return statSync(p).isDirectory(); } catch { return false; }
};

// The body without fenced blocks and inline code, where [[ ]] is bash or TOML
// syntax rather than a link to another entry.
function proseOf(text) {
  return bodyOf(text)
    .replace(/^(```|~~~)[^\n]*\n[\s\S]*?^\1[^\n]*$/gm, '')
    .replace(/`[^`\n]*`/g, '');
}

const isMap = (v) => v !== null && typeof v === 'object' && !Array.isArray(v);
const text_ = (v) => (typeof v === 'string' ? v : '');
const sameKeys = (actual, expected) => actual.length === expected.length && actual.every((k, i) => k === expected[i]);
const ignored = (name) => name.startsWith('.') || OS_FILES.has(name);

// The body lines that state the fact: fence markers, blank lines and the
// Why / How to apply lines do not count.
function factLines(text) {
  return bodyOf(text)
    .split(/\r?\n/)
    .map((l) => l.trim())
    .filter((l) => l !== '' && !l.startsWith('```') && !l.startsWith('~~~'))
    .filter((l) => !l.startsWith('**Why:**') && !l.startsWith('**How to apply:**'));
}

// Walks project/ and artifact/<id>/ in sorted order, reporting STRAY items.
function scanLayout(store, add) {
  const entries = [];
  const sorted = (dir) => readdirSync(dir, { withFileTypes: true })
    .filter((e) => !ignored(e.name))
    .sort((a, b) => (a.name < b.name ? -1 : a.name > b.name ? 1 : 0));

  for (const e of sorted(store)) {
    if (e.isFile() && !TOP_LEVEL_FILES.has(e.name)) {
      add('STRAY', e.name, 'only README.md and MEMORY.md may live at the store root');
    } else if (e.isDirectory() && e.name !== 'project' && e.name !== 'artifact') {
      add('STRAY', `${e.name}/`, 'this folder is not allowed here; the only folders are project and artifact');
    }
  }

  const projectDir = join(store, 'project');
  if (isDir(projectDir)) {
    for (const e of sorted(projectDir)) {
      if (e.isDirectory()) {
        add('STRAY', `project/${e.name}/`, 'entries must be files directly under project/');
      } else if (e.name.endsWith('.md')) {
        entries.push({ kind: 'project', id: null, rel: `project/${e.name}`, stem: e.name.slice(0, -3) });
      } else {
        add('STRAY', `project/${e.name}`, 'only .md entries belong here');
      }
    }
  }

  const artifactDir = join(store, 'artifact');
  if (isDir(artifactDir)) {
    for (const e of sorted(artifactDir)) {
      if (!e.isDirectory()) {
        add('STRAY', `artifact/${e.name}`, 'entries must live in artifact/<artifact_id>/');
      } else if (!ARTIFACT_ID_RE.test(e.name)) {
        add('STRAY', `artifact/${e.name}/`, 'this folder name is not an artifact id');
      } else {
        for (const f of sorted(join(artifactDir, e.name))) {
          if (f.isDirectory()) {
            add('STRAY', `artifact/${e.name}/${f.name}/`, `entries must be files directly under artifact/${e.name}/`);
          } else if (f.name.endsWith('.md')) {
            entries.push({ kind: 'artifact', id: e.name, rel: `artifact/${e.name}/${f.name}`, stem: f.name.slice(0, -3) });
          } else {
            add('STRAY', `artifact/${e.name}/${f.name}`, 'only .md entries belong here');
          }
        }
      }
    }
  }
  return entries;
}

function lintFrontmatter(rel, stem, kind, id, d, add) {
  const topKeys = Object.keys(d);
  if (!sameKeys(topKeys, TOP_KEYS) && !sameKeys(topKeys, [...TOP_KEYS, 'note'])) {
    add('FM_KEYS', rel, `the top-level keys are [${topKeys.join(', ')}], expected [${TOP_KEYS.join(', ')}] and optionally note last`);
  }
  for (const key of ['name', 'description']) {
    if (typeof d[key] !== 'string' || d[key].trim() === '') add('FM_KEYS', rel, `the ${key} is empty`);
  }
  const meta = d.metadata;
  const metaIsMap = isMap(meta);
  const metaKeys = metaIsMap ? Object.keys(meta) : [];
  const legacyKey = metaIsMap && sameKeys(metaKeys, LEGACY_META_KEYS);
  if (!metaIsMap || !(sameKeys(metaKeys, META_KEYS) || legacyKey)) {
    const actual = metaIsMap ? metaKeys.join(', ') : '(not a map)';
    add('FM_KEYS', rel, `the metadata keys are [${actual}], expected [${META_KEYS.join(', ')}]`);
  }
  if (typeof d.name === 'string' && d.name !== stem) {
    add('FM_NAME', rel, `the name "${d.name}" differs from the file name "${stem}"`);
  }
  if (typeof d.name === 'string' && d.name !== '' && !NAME_RE.test(d.name)) {
    add('FM_NAME', rel, `the name "${d.name}" is not a kebab-case slug`);
  }

  if (metaIsMap) {
    if (!TYPES.includes(meta.type) && !LEGACY_TYPES.includes(meta.type)) {
      add('FM_TYPE', rel, `the type "${text_(meta.type)}" is not pitfall, decision, lesson, directive or vocabulary`);
    }

    const entity = meta.entity;
    const entityMatch = typeof entity === 'string' ? ENTITY_RE.exec(entity) : null;
    if (!entityMatch) {
      if (entity === 'profile') {
        add('FM_ENTITY', rel, 'the entity "profile" is a fact about a person: it belongs in Claude Code user memory, never in the lab');
      } else {
        add('FM_ENTITY', rel, `the entity "${text_(entity)}" is not project or artifact:<id>`);
      }
    } else {
      const target = entityMatch[2];
      if (kind === 'project' && target !== undefined) {
        add('FM_ENTITY_DIR', rel, `the entity artifact:${target} lives under project/; move it to artifact/${target}/`);
      } else if (kind === 'artifact' && target === undefined) {
        add('FM_ENTITY_DIR', rel, `the entity project lives under artifact/${id}/; move it to project/`);
      } else if (kind === 'artifact' && target !== id) {
        add('FM_ENTITY_DIR', rel, `the entity artifact:${target} lives under artifact/${id}/; move it to artifact/${target}/`);
      }
    }

    // The basis sits under the key basis, or under the legacy key evidence.
    const basis = Object.hasOwn(meta, 'basis') ? meta.basis : meta.evidence;
    if (!BASES.includes(basis)) {
      add('FM_BASIS', rel, `the basis "${text_(basis)}" is not stated, observed or inferred`);
    }
    if (typeof meta.learned_by !== 'string' || !ROLE_RE.test(meta.learned_by)) {
      add('FM_LEARNED_BY', rel, `the learned_by value "${text_(meta.learned_by)}" is not a role name (kebab-case) or unknown`);
    }
    if (!ORIGINS.includes(meta.origin)) {
      add('FM_ORIGIN', rel, `the origin "${text_(meta.origin)}" is not agent, extractor, user or import`);
    }
  }

  if (!isIsoDate(d.date)) add('FM_DATE', rel, `the date "${text_(d.date)}" is not YYYY-MM-DD`);
}

export function lintStore(storeDir, { budget } = {}) {
  const store = resolve(storeDir);
  const findings = [];
  const add = (code, path, message) => findings.push({ code, path, message });

  const indexPath = join(store, 'MEMORY.md');
  if (!existsSync(indexPath)) {
    add('FM_MISSING', 'MEMORY.md', 'the index file is missing');
    return findings;
  }

  let effectiveBudget = budget;
  if (effectiveBudget === undefined) {
    const found = readBudget(store);
    effectiveBudget = found.budget;
    if (found.problem !== null) add('BUDGET', 'lab.json', `${found.problem}; the default limit of ${DEFAULT_BUDGET} applies`);
  }
  const indexLines = splitLines(readFileSync(indexPath, 'utf8'));
  if (indexLines.length > effectiveBudget) {
    add('BUDGET', 'MEMORY.md', `the index has ${indexLines.length} lines, the limit is ${effectiveBudget}`);
  }

  // The layout scan runs first so index links can be matched to entries; its
  // findings are reported after the index findings.
  const layoutFindings = [];
  const entries = scanLayout(store, (code, path, message) => layoutFindings.push({ code, path, message }));
  const entryNames = new Set(entries.map((e) => e.stem));
  const relByLower = new Map(entries.map((e) => [e.rel.toLowerCase(), e.rel]));
  const entryRels = new Set(entries.map((e) => e.rel));

  const linked = new Set();
  indexLines.forEach((line, i) => {
    const match = INDEX_LINK_RE.exec(line);
    if (!match) return;
    const target = posix.normalize(match[1]).replace(/^\.\//, '');
    if (entryRels.has(target)) {
      linked.add(target);
    } else if (relByLower.has(target.toLowerCase())) {
      const actual = relByLower.get(target.toLowerCase());
      linked.add(actual);
      add('DANGLING', `MEMORY.md:${i + 1}`, `the link target ${target} differs in case from ${actual}`);
    } else if (!existsSync(join(store, target))) {
      add('DANGLING', `MEMORY.md:${i + 1}`, `the link target ${target} does not exist`);
    }

    const dash = line.indexOf(' — ');
    if (dash === -1) return;
    const hook = line
      .slice(dash + 3)
      .replace(/\*\*UPDATED[^*]*\*\*/g, '')
      .replace(/\s*\(\d{4}-\d{2}\)\s*$/, '')
      .trim();
    if (hook !== '' && RECORD_LINE_RE.test(hook)) {
      add('RECORD_ONLY', `MEMORY.md:${i + 1}`, 'the index line only cites a lab record');
    }
  });

  findings.push(...layoutFindings);

  const seenNormalized = new Map();
  for (const { kind, id, rel, stem } of entries) {
    if (!linked.has(rel)) add('ORPHAN', rel, 'the entry has no index line');

    const text = readFileSync(join(store, rel), 'utf8');
    const fm = parseFrontmatter(text);
    if (!fm) {
      add('FM_MISSING', rel, 'the entry has no frontmatter block');
    } else if (fm.malformed !== null) {
      add('FM_KEYS', rel, `this frontmatter line cannot be parsed: ${fm.malformed}`);
    } else {
      lintFrontmatter(rel, stem, kind, id, fm.data, add);
    }

    for (const link of proseOf(text).matchAll(WIKILINK_RE)) {
      if (!entryNames.has(link[1].trim())) add('WIKILINK', rel, `the link [[${link[1]}]] does not name an entry`);
    }

    const normalized = normalizeName(stem);
    if (seenNormalized.has(normalized)) {
      add('NEAR_DUP', rel, `the name differs from ${seenNormalized.get(normalized)} only by punctuation or a trailing s`);
    } else {
      seenNormalized.set(normalized, rel);
    }

    const facts = factLines(text);
    if (facts.length === 0) {
      add('NO_FACT', rel, 'the entry states no fact, only Why and How to apply lines');
    } else if (facts.every((l) => RECORD_LINE_RE.test(l))) {
      add('RECORD_ONLY', rel, 'the entry only cites a lab record; the record already holds it');
    }
  }

  return findings;
}

const USAGE = 'Usage: node memory-lint.mjs <store-dir> [--budget N]\n';
const HELP = `${USAGE}
Runs the lab memory consistency check on a memory store (research_lab/memory).
It prints one line per finding, "<CODE> <path>: <message>", and checks:
  the index (MEMORY.md): its length against the limit, its links, an entry
    with no index line
  the layout: only project/ and artifact/<artifact_id>/ hold entries
  each entry's frontmatter: name, description, date, and the metadata keys
    type (pitfall, decision, lesson, directive or vocabulary), entity (project
    or artifact:<id>), basis (stated, observed or inferred), learned_by and
    origin; the legacy key evidence and the legacy type gotcha are still read
  each entry's body: it must state a fact, not only cite a lab record

  --budget N   the index limit in lines (default: memory.indexBudget in
               research_lab/lab.json, else ${DEFAULT_BUDGET})
  --help       print this text

Exit: 0 when every check passes, 1 when there are findings, 2 on a usage error.
`;

// Returns { storeDir, budget } or null when the arguments are not valid.
function parseArgs(argv) {
  let budget;
  const positional = [];
  const parseBudget = (raw) => {
    if (typeof raw !== 'string' || !/^\d+$/.test(raw) || Number(raw) <= 0) return false;
    budget = Number(raw);
    return true;
  };
  for (let i = 0; i < argv.length; i++) {
    const arg = argv[i];
    if (arg === '--help' || arg === '-h') {
      return { help: true };
    } else if (arg === '--budget') {
      if (!parseBudget(argv[++i])) return null;
    } else if (arg.startsWith('--budget=')) {
      if (!parseBudget(arg.slice('--budget='.length))) return null;
    } else if (arg.startsWith('-')) {
      return null;
    } else {
      positional.push(arg);
    }
  }
  if (positional.length !== 1) return null;
  return { storeDir: positional[0], budget };
}

function main(argv) {
  const parsed = parseArgs(argv);
  if (!parsed) {
    process.stderr.write(USAGE);
    return 2;
  }
  if (parsed.help) {
    process.stdout.write(HELP);
    return 0;
  }
  const { storeDir, budget } = parsed;
  if (!isDir(storeDir)) {
    process.stderr.write(`memory consistency check: no such store directory: ${storeDir}\n`);
    return 2;
  }
  const findings = lintStore(storeDir, { budget });
  for (const { code, path, message } of findings) process.stdout.write(`${code} ${path}: ${message}\n`);
  return findings.length ? 1 : 0;
}

// Node loads the main module by its real path, so compare real paths: run
// through a junction or symlink, a plain comparison would be false and the
// script would exit 0 without linting anything.
function invokedDirectly() {
  if (!process.argv[1]) return false;
  try {
    const invoked = realpathSync(process.argv[1]);
    const self = realpathSync(fileURLToPath(import.meta.url));
    return process.platform === 'win32' ? invoked.toLowerCase() === self.toLowerCase() : invoked === self;
  } catch {
    return false;
  }
}
if (invokedDirectly()) process.exit(main(process.argv.slice(2)));
