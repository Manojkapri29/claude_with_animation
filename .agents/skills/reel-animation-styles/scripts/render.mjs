// Frame-exact renderer: node render.mjs <reel.html> <out.mp4> [--preview 1,5,10] [--audio music.mp3] [--fps 30]
// Needs: npm i -D playwright && npx playwright install chromium ; ffmpeg on PATH.
import { chromium } from 'playwright';
import { spawn } from 'node:child_process';
import { pathToFileURL } from 'node:url';
import path from 'node:path';
import fs from 'node:fs';

const [html, out, ...rest] = process.argv.slice(2);
if (!html || !out) { console.error('usage: node render.mjs reel.html out.mp4 [--preview 1,5] [--audio a.mp3] [--fps 30]'); process.exit(1); }
const opt = (k, d) => { const i = rest.indexOf(k); return i >= 0 ? rest[i + 1] : d; };
const FPS = +opt('--fps', 30), preview = opt('--preview', null), audio = opt('--audio', null);

const browser = await chromium.launch({ args: ['--use-gl=angle', '--use-angle=swiftshader', '--enable-unsafe-swiftshader'] });
const page = await browser.newPage({ viewport: { width: 1080, height: 1920 }, deviceScaleFactor: 1 });
page.on('console', m => m.type() === 'error' && console.error('[page]', m.text()));
await page.goto(pathToFileURL(path.resolve(html)).href);
await page.waitForFunction(() => window.ready === true && typeof window.renderAt === 'function', null, { timeout: 60000 });
await page.evaluate(() => document.fonts.ready);
const DURATION = await page.evaluate(() => window.DURATION);

if (preview) {
  const dir = out.replace(/\.mp4$/, '') + '_stills'; fs.mkdirSync(dir, { recursive: true });
  for (const t of preview.split(',').map(Number)) {
    await page.evaluate(t => window.renderAt(t), t);
    await page.screenshot({ path: `${dir}/t${t}.png` });
  }
  console.log('stills ->', dir); await browser.close(); process.exit(0);
}

const args = ['-y', '-loglevel', 'error', '-f', 'image2pipe', '-framerate', String(FPS), '-i', '-'];
if (audio) args.push('-i', audio, '-filter:a', 'volume=0.12', '-shortest');
args.push('-c:v', 'libx264', '-preset', 'veryfast', '-crf', '19', '-pix_fmt', 'yuv420p', '-r', String(FPS));
if (audio) args.push('-c:a', 'aac'); else args.push('-an');
args.push(out);
const ff = spawn('ffmpeg', args, { stdio: ['pipe', 'inherit', 'inherit'] });

const N = Math.round(DURATION * FPS);
for (let f = 0; f < N; f++) {
  await page.evaluate(t => window.renderAt(t), f / FPS);
  const buf = await page.screenshot({ type: 'jpeg', quality: 92 });
  if (!ff.stdin.write(buf)) await new Promise(r => ff.stdin.once('drain', r));
  if (f % 30 === 0) process.stdout.write(`\r${f}/${N}`);
}
ff.stdin.end(); await new Promise(r => ff.on('close', r)); await browser.close();
console.log(`\n✅ ${out} (${DURATION}s @ ${FPS}fps)`);
