import { test, expect } from '@playwright/test';

test('health banner is visible', async ({ page }) => {
  await page.goto('/');
  await expect(page.getByText(/Portfolio Showcase/)).toBeVisible();
});
