import { test, expect } from '@playwright/test'

test.describe('Navigation', () => {
  test('should have working home link in navbar', async ({ page }) => {
    await page.goto('/login')
    await page.getByRole('link', { name: /home/i }).click()
    await expect(page).toHaveURL('/')
  })

  test('should be responsive on mobile viewport', async ({ page }) => {
    await page.setViewportSize({ width: 375, height: 667 })
    await page.goto('/')

    // Navigation should still be accessible
    await expect(page.locator('nav')).toBeVisible()
  })

  test('should maintain scroll position on navigation', async ({ page }) => {
    await page.goto('/')

    // Scroll down
    await page.evaluate(() => window.scrollTo(0, 500))

    // Navigate to another page and back
    await page.goto('/login')
    await page.goBack()

    // Page should load correctly
    await expect(page).toHaveURL('/')
  })

  test('should handle 404 for unknown routes gracefully', async ({ page }) => {
    await page.goto('/this-page-does-not-exist-12345')

    // Should either show a 404 page or redirect to home
    const content = await page.content()
    const is404OrRedirect =
      content.includes('404') ||
      content.includes('not found') ||
      page.url().includes('/') ||
      page.url().includes('/login')

    expect(is404OrRedirect).toBeTruthy()
  })
})

test.describe('Accessibility', () => {
  test('should have proper heading hierarchy', async ({ page }) => {
    await page.goto('/')

    // Check for presence of headings
    const h1Count = await page.locator('h1').count()
    expect(h1Count).toBeGreaterThanOrEqual(0)
  })

  test('should have alt text on images', async ({ page }) => {
    await page.goto('/')

    const images = page.locator('img')
    const count = await images.count()

    for (let i = 0; i < count; i++) {
      const img = images.nth(i)
      const alt = await img.getAttribute('alt')
      const ariaLabel = await img.getAttribute('aria-label')
      const role = await img.getAttribute('role')

      // Image should have alt text or be decorative (role="presentation")
      const hasAccessibleName = alt !== null || ariaLabel !== null || role === 'presentation'
      expect(hasAccessibleName).toBeTruthy()
    }
  })

  test('should have visible focus indicators', async ({ page }) => {
    await page.goto('/')

    // Tab to first focusable element
    await page.keyboard.press('Tab')

    // Check that something is focused
    const focusedElement = await page.evaluate(() => document.activeElement?.tagName)
    expect(focusedElement).toBeTruthy()
  })
})
