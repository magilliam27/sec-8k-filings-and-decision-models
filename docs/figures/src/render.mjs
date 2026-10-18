// Render the pages written by make_figures.py to PNG in docs/figures/.
//   node docs/figures/src/render.mjs
// README images render at 2x; the social preview at 1x (GitHub's 1280 x 640)
// and is written to build/, since it is uploaded in the repository settings.
import { chromium } from 'playwright';
import { readdirSync } from 'fs';
import { dirname, join } from 'path';
import { fileURLToPath } from 'url';

const here = dirname(fileURLToPath(import.meta.url));
const src = join(here, 'build');
const dst = join(here, '..');
const browser = await chromium.launch(process.env.CHROMIUM ? { executablePath: process.env.CHROMIUM } : {});
for (const f of readdirSync(src).filter((n) => n.endsWith('.html'))) {
  const scale = f.startsWith('social-preview') ? 1 : 2;
  const page = await browser.newPage({ deviceScaleFactor: scale, viewport: { width: 1300, height: 900 } });
  await page.goto('file://' + join(src, f), { waitUntil: 'networkidle' });
  await page.evaluate(() => document.fonts.ready);
  // Google Fonts loads only the faces a page uses; require those to have loaded.
  const fonts = await page.evaluate(() => {
    const faces = [...document.fonts];
    return faces.some((x) => x.status === 'loaded') && !faces.some((x) => x.status === 'error');
  });
  if (!fonts) throw new Error(`${f}: IBM Plex did not load`);
  const out = scale === 1 ? src : dst;  // the social preview stays in build/ for upload
  await page.locator('#art').screenshot({ path: join(out, f.replace('.html', '.png')) });
  console.log(f);
  await page.close();
}
await browser.close();
