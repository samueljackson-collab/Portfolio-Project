import { test, expect } from '@playwright/test'

test.describe('Home Page', () => {
  test('should display the home page', async ({ page }) => {
    await page.goto('/')
    await expect(page).toHaveTitle(/Portfolio/)
  })

  test('should show navigation bar', async ({ page }) => {
    await page.goto('/')
    await expect(page.locator('nav')).toBeVisible()
  })

  test('should have login link for unauthenticated users', async ({ page }) => {
    await page.goto('/')
    await expect(page.getByRole('link', { name: /login/i })).toBeVisible()
  })

  test('should have sign up link for unauthenticated users', async ({ page }) => {
    await page.goto('/')
    await expect(page.getByRole('link', { name: /sign up/i })).toBeVisible()
  })

  test('should navigate to portfolio showcase', async ({ page }) => {
    await page.goto('/')
    await page.getByRole('link', { name: /portfolio showcase/i }).click()
    await expect(page).toHaveURL(/enterprise-portfolio/)
  })
})
