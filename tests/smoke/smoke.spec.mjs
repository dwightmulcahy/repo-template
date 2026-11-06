import { test, expect } from '@playwright/test';

test('health endpoint', async ({ request }) => {
  const res = await request.get('/health');
  expect(res.ok()).toBeTruthy();
  expect(await res.json()).toEqual({ status: 'ok' });
});

test('home page loads without console errors', async ({ page }) => {
  const errors = [];
  page.on('pageerror', (e) => errors.push(e.message));
  page.on('console', (m) => m.type() === 'error' && errors.push(m.text()));
  await page.goto('/');
  await expect(page.locator('#title')).toBeVisible();
  await expect(page.locator('body')).toHaveAttribute('data-ready', 'true');
  expect(errors).toEqual([]);
});

test('version label opens the About dialog with build info', async ({ page, request, context }) => {
  const res = await request.get('/build.json');
  expect(res.ok()).toBeTruthy();
  const info = await res.json();
  const label = info.version === 'dev' ? `dev${info.commit ? ' ' + info.commit : ''}` : `v${info.version}`;
  await page.goto('/');
  const button = page.getByRole('button', { name: /show build details/ });
  await expect(button).toHaveText(label);
  await button.click();
  const dlg = page.getByRole('dialog');
  await expect(dlg).toBeVisible();
  await expect(dlg.locator('.about-kv')).toContainText(info.version === 'dev' ? 'dev (local build)' : `v${info.version}`);
  await expect(dlg.locator('.about-kv')).toContainText('Server up since');
  if (info.repository) await expect(dlg.getByRole('link', { name: 'Report a problem' })).toHaveAttribute('href', `${info.repository}/issues/new`);
  await context.grantPermissions(['clipboard-read', 'clipboard-write']);
  await dlg.getByRole('button', { name: 'Copy details' }).click();
  await expect(dlg.getByRole('status')).toHaveText('Copied.');
  expect(await page.evaluate(() => navigator.clipboard.readText())).toContain('Version: ');
  await dlg.getByRole('button', { name: 'Close' }).click();
  await expect(page.getByRole('dialog')).toHaveCount(0);
});

test('about endpoint reports when the server started', async ({ request }) => {
  const res = await request.get('/api/about');
  expect(res.ok()).toBeTruthy();
  expect(Date.parse((await res.json()).started_at)).toBeLessThanOrEqual(Date.now());
});
