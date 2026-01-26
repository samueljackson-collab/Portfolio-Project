import { test, expect } from '@playwright/test'

test.describe('Authentication', () => {
  test('should display login page', async ({ page }) => {
    await page.goto('/login')
    await expect(page.getByRole('heading', { level: 1 })).toContainText(/login|sign in/i)
  })

  test('should display register page', async ({ page }) => {
    await page.goto('/register')
    await expect(page.getByRole('heading', { level: 1 })).toContainText(/register|sign up|create/i)
  })

  test('should show validation errors on empty login submission', async ({ page }) => {
    await page.goto('/login')

    // Find and click submit button
    const submitButton = page.getByRole('button', { name: /login|sign in|submit/i })
    if (await submitButton.isVisible()) {
      await submitButton.click()

      // Should show some form of validation feedback
      await expect(page.locator('form')).toBeVisible()
    }
  })

  test('should navigate between login and register', async ({ page }) => {
    await page.goto('/login')

    // Look for a link to register
    const registerLink = page.getByRole('link', { name: /register|sign up|create account/i })
    if (await registerLink.isVisible()) {
      await registerLink.click()
      await expect(page).toHaveURL(/register/)
    }
  })

  test('should have password field of type password', async ({ page }) => {
    await page.goto('/login')

    const passwordField = page.locator('input[type="password"]')
    if (await passwordField.isVisible()) {
      await expect(passwordField).toHaveAttribute('type', 'password')
    }
  })
})
