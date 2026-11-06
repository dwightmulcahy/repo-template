// Usage: node scripts/build.mjs <web|offline>   (OUT_DIR overrides dist/<edition>)
//
// Build metadata (shown by the version label / About dialog in the UI):
//   APP_VERSION  release version, e.g. 1.4.2 or v1.4.2 (release workflow); empty -> "dev"
//   GIT_SHA      commit; if empty, read from GIT_DIR (compose.yaml mounts .git for local builds)
//   REPOSITORY   owner/repo on GitHub (release workflow); else GITHUB_REPOSITORY, else GIT_DIR's origin
import { cp, rm, writeFile, mkdir, readFile } from 'node:fs/promises';
import path from 'node:path';

const edition = process.argv[2];
if (!['web', 'offline'].includes(edition)) {
  console.error('edition must be "web" or "offline"');
  process.exit(1);
}

const root = path.resolve(import.meta.dirname, '..');
const out = path.resolve(process.env.OUT_DIR ?? path.join(root, 'dist', edition));

const read = (p) => readFile(p, 'utf8').then((s) => s.trim(), () => '');

async function gitHead(dir) {
  if (!dir) return '';
  const head = await read(path.join(dir, 'HEAD'));
  const ref = head.match(/^ref: (refs\/[^\s.][^\s]*)$/)?.[1];
  if (!ref) return head; // detached HEAD (or empty)
  if (ref.includes('..')) return '';
  const loose = await read(path.join(dir, ref));
  if (loose) return loose;
  const packed = await read(path.join(dir, 'packed-refs'));
  return packed.split('\n').find((l) => l.endsWith(` ${ref}`))?.split(' ')[0] ?? '';
}

async function gitOrigin(dir) {
  if (!dir) return '';
  const config = await read(path.join(dir, 'config'));
  const section = config.split(/^\[/m).find((s) => s.startsWith('remote "origin"]')) ?? '';
  const url = section.match(/^\s*url\s*=\s*(\S+)/m)?.[1] ?? '';
  return url.match(/github\.com[:/]([^/\s]+\/[^/\s]+?)(?:\.git)?\/?$/)?.[1] ?? '';
}

const rawVersion = (process.env.APP_VERSION ?? '').replace(/^v/, '');
const version = /^\d+\.\d+\.\d+(?:-[0-9A-Za-z.-]+)?$/.test(rawVersion) ? rawVersion : 'dev';
const sha = process.env.GIT_SHA || (await gitHead(process.env.GIT_DIR));
const commit = /^[0-9a-f]{7,40}$/i.test(sha) ? sha.slice(0, 7).toLowerCase() : '';
const repo = process.env.REPOSITORY || process.env.GITHUB_REPOSITORY || (await gitOrigin(process.env.GIT_DIR));
const repository = /^[\w.-]+\/[\w.-]+$/.test(repo) ? `https://github.com/${repo}` : '';
const info = { edition, version, commit, repository, builtAt: new Date().toISOString() };

await rm(out, { recursive: true, force: true });
await mkdir(out, { recursive: true });
await cp(path.join(root, 'src'), out, { recursive: true });
await writeFile(path.join(out, 'build.json'), JSON.stringify(info, null, 2) + '\n');
// Embed in the page too, so the label works without a fetch (e.g. the offline edition).
// "<" is escaped so the JSON can't close the <script> element.
const html = path.join(out, 'index.html');
const page = await readFile(html, 'utf8');
const embedded = page.replace(
  /(<script type="application\/json" id="build-info">)[\s\S]*?(<\/script>)/,
  (_, open, close) => open + JSON.stringify(info).replace(/</g, '\\u003c') + close,
);
if (embedded === page) throw new Error('index.html is missing <script type="application/json" id="build-info">');
await writeFile(html, embedded);
console.log(`built ${edition} ${version}${commit ? ' ' + commit : ''} -> ${path.relative(root, out) || out}`);
