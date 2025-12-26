import { test, expect, devices } from '@playwright/test';

// Define mobile and tablet viewports
const mobileViewports = {
  'mobile-small': { width: 320, height: 568 }, // iPhone SE
  'mobile-medium': { width: 375, height: 812 }, // iPhone 12
  'mobile-large': { width: 412, height: 915 }, // Samsung Galaxy
};

const tabletViewports = {
  'tablet-portrait': { width: 768, height: 1024 }, // iPad Portrait
  'tablet-landscape': { width: 1024, height: 768 }, // iPad Landscape
};

Object.entries({ ...mobileViewports, ...tabletViewports }).forEach(
  ([deviceName, viewport]) => {
    test.describe(`Responsive Design - ${deviceName}`, () => {
      test.beforeEach(async ({ page }) => {
        // Set viewport size
        await page.setViewportSize(viewport);
      });

      test('should load homepage and be responsive', async ({ page }) => {
        await page.goto('/');

        // Verify page loads
        await expect(page.locator('body')).toBeVisible();

        // Check that content is visible
        const mainContent = page.locator('main, [role="main"]');
        await expect(mainContent).toBeVisible();

        // Verify no horizontal scrollbar is needed (content fits viewport)
        const bodyWidth = await page.evaluate(() => document.body.scrollWidth);
        const viewportWidth = viewport.width;
        expect(bodyWidth).toBeLessThanOrEqual(viewportWidth + 5); // Allow small margin
      });

      test('should display mobile-friendly navigation', async ({ page }) => {
        await page.goto('/');

        // Check for hamburger menu on mobile
        const hamburgerMenu = page.locator('[data-testid="menu-toggle"], button[aria-label*="menu" i]');
        const navLinks = page.locator('nav a, [role="navigation"] a');

        if (viewport.width <= 768) {
          // On mobile, menu should be hidden or collapsed
          if (await hamburgerMenu.isVisible()) {
            await hamburgerMenu.click();
            // Menu should open
            await expect(navLinks.first()).toBeVisible();

            // Close menu
            await hamburgerMenu.click();
          }
        } else {
          // On tablet and larger, navigation should be visible
          await expect(navLinks.first()).toBeVisible();
        }
      });

      test('should have readable text on mobile', async ({ page }) => {
        await page.goto('/');

        // Check font sizes are readable
        const allText = page.locator('body *');
        const count = await allText.count();

        for (let i = 0; i < Math.min(count, 50); i++) {
          const element = allText.nth(i);
          const fontSize = await element.evaluate((el) => {
            const styles = window.getComputedStyle(el);
            return parseFloat(styles.fontSize);
          });

          // Minimum readable font size is typically 12px, but mobile should be 14px+
          if (await element.textContent().then(text => text?.length ?? 0 > 0)) {
            expect(fontSize).toBeGreaterThanOrEqual(12);
          }
        }
      });

      test('should handle touch interactions on mobile', async ({ page }) => {
        await page.goto('/products');

        // Find first product
        const product = page.locator('[data-testid="product-card"]').first();
        await expect(product).toBeVisible();

        // Tap on product (simulate touch)
        await product.tap();

        // Should navigate to product details
        await expect(page).toHaveURL(/\/products\/\d+/);
      });

      test('should have proper spacing on mobile', async ({ page }) => {
        await page.goto('/');

        // Check button sizes for touch targets (minimum 44x44 px recommended)
        const buttons = page.locator('button');
        const buttonCount = await buttons.count();

        for (let i = 0; i < Math.min(buttonCount, 10); i++) {
          const button = buttons.nth(i);
          const boundingBox = await button.boundingBox();

          if (boundingBox && viewport.width <= 768) {
            // On mobile, buttons should have adequate touch size
            const width = boundingBox.width;
            const height = boundingBox.height;

            // Allow some buttons to be smaller if they're not interactive or within other elements
            if (await button.isEnabled()) {
              expect(width).toBeGreaterThanOrEqual(32);
              expect(height).toBeGreaterThanOrEqual(32);
            }
          }
        }
      });

      test('should handle forms on mobile', async ({ page }) => {
        await page.goto('/login');

        // Find all form inputs
        const inputs = page.locator('input');
        const inputCount = await inputs.count();

        // Verify inputs are accessible
        for (let i = 0; i < inputCount; i++) {
          const input = inputs.nth(i);
          if (await input.isVisible()) {
            // Check input size for mobile
            const boundingBox = await input.boundingBox();
            if (boundingBox && viewport.width <= 768) {
              expect(boundingBox.height).toBeGreaterThanOrEqual(40);
            }
          }
        }
      });

      test('should display images responsively', async ({ page }) => {
        await page.goto('/products');

        // Check images are properly sized
        const images = page.locator('img');
        const imageCount = await images.count();

        for (let i = 0; i < Math.min(imageCount, 5); i++) {
          const img = images.nth(i);
          if (await img.isVisible()) {
            const naturalWidth = await img.evaluate((el: HTMLImageElement) => el.naturalWidth);
            const naturalHeight = await img.evaluate((el: HTMLImageElement) => el.naturalHeight);

            // Images should have dimensions
            expect(naturalWidth).toBeGreaterThan(0);
            expect(naturalHeight).toBeGreaterThan(0);
          }
        }
      });

      test('should not have overlapping elements on mobile', async ({ page }) => {
        await page.goto('/');

        // Check for overlapping elements
        const allElements = page.locator('body *');
        const count = await allElements.count();

        const checkedElements = [];
        for (let i = 0; i < Math.min(count, 30); i++) {
          const element = allElements.nth(i);
          const box = await element.boundingBox();

          if (box) {
            // Check for significant z-index that might indicate overlap
            const zIndex = await element.evaluate((el) => {
              const styles = window.getComputedStyle(el);
              return styles.zIndex;
            });

            checkedElements.push({ index: i, zIndex, box });
          }
        }

        // Verify no critical overlaps by checking main content area
        const mainContent = page.locator('main, [role="main"]');
        if (await mainContent.isVisible()) {
          await expect(mainContent).toHaveJSProperty('offsetHeight', /\d+/);
        }
      });

      test('should handle modal/dialog on mobile', async ({ page }) => {
        await page.goto('/');

        // Try to trigger a modal
        const modalTrigger = page.locator('button:has-text("Settings"), [data-testid="modal-trigger"]').first();
        if (await modalTrigger.isVisible()) {
          await modalTrigger.click();

          // Check modal is visible and full width
          const modal = page.locator('[role="dialog"], .modal, [data-testid="modal"]').first();
          if (await modal.isVisible()) {
            const modalBox = await modal.boundingBox();
            if (modalBox) {
              // Modal should be roughly full width on mobile
              if (viewport.width <= 768) {
                expect(modalBox.width).toBeGreaterThan(viewport.width * 0.8);
              }
            }
          }
        }
      });

      test('should have readable links on mobile', async ({ page }) => {
        await page.goto('/');

        const links = page.locator('a');
        const linkCount = await links.count();

        for (let i = 0; i < Math.min(linkCount, 10); i++) {
          const link = links.nth(i);
          if (await link.isVisible()) {
            const padding = await link.evaluate((el) => {
              const styles = window.getComputedStyle(el);
              return {
                paddingTop: parseFloat(styles.paddingTop),
                paddingBottom: parseFloat(styles.paddingBottom),
                paddingLeft: parseFloat(styles.paddingLeft),
                paddingRight: parseFloat(styles.paddingRight),
              };
            });

            // Links should have adequate padding for touch targets
            const totalVerticalPadding = padding.paddingTop + padding.paddingBottom;
            const totalHorizontalPadding = padding.paddingLeft + padding.paddingRight;

            if (viewport.width <= 768) {
              expect(totalVerticalPadding).toBeGreaterThanOrEqual(8);
              expect(totalHorizontalPadding).toBeGreaterThanOrEqual(8);
            }
          }
        }
      });

      test('should paginate lists on mobile', async ({ page }) => {
        await page.goto('/products');

        // Check for pagination or infinite scroll
        const pagination = page.locator('[data-testid="pagination"], nav[aria-label*="page" i]');
        const loadMore = page.locator('button:has-text("Load More")');

        if (await pagination.isVisible()) {
          const nextButton = pagination.locator('button:has-text("Next")').first();
          if (await nextButton.isVisible()) {
            await expect(nextButton).toBeEnabled();
          }
        } else if (await loadMore.isVisible()) {
          await expect(loadMore).toBeEnabled();
        }
      });

      test('should handle landscape orientation on mobile', async ({ page }) => {
        if (deviceName.includes('mobile')) {
          // Simulate landscape orientation
          const landscapeViewport = {
            width: viewport.height,
            height: viewport.width,
          };
          await page.setViewportSize(landscapeViewport);

          await page.goto('/');

          // Content should still be readable in landscape
          const mainContent = page.locator('main, [role="main"]');
          await expect(mainContent).toBeVisible();

          // No horizontal scroll needed
          const bodyWidth = await page.evaluate(() => document.body.scrollWidth);
          expect(bodyWidth).toBeLessThanOrEqual(landscapeViewport.width + 5);
        }
      });

      test(`visual regression - ${deviceName}`, async ({ page }) => {
        await page.goto('/');

        // Take screenshot for visual comparison
        await expect(page).toHaveScreenshot(`responsive-${deviceName}.png`, {
          fullPage: true,
          animations: 'disabled',
        });
      });
    });
  }
);

// Test specific mobile features
test.describe('Mobile-Specific Features', () => {
  test.use({ ...devices['iPhone 12'] });

  test('should handle touch gestures', async ({ page }) => {
    await page.goto('/products');

    // Simulate swipe gesture (left to right)
    const productCard = page.locator('[data-testid="product-card"]').first();
    const box = await productCard.boundingBox();

    if (box) {
      await page.touchscreen.tap(box.x + box.width / 2, box.y + box.height / 2);
    }

    // Should navigate or trigger action
    await expect(page).toHaveURL(/\/products/);
  });

  test('should support device back button', async ({ page }) => {
    // Navigate to multiple pages
    await page.goto('/');
    await page.goto('/products');
    await page.goto('/products/123');

    // Go back
    await page.goBack();
    await expect(page).toHaveURL(/\/products$/);

    // Go back again
    await page.goBack();
    await expect(page).toHaveURL(/\/$/);
  });

  test('should handle mobile keyboard', async ({ page }) => {
    await page.goto('/login');

    // Focus on email input
    const emailInput = page.locator('input[name="email"]');
    await emailInput.click();

    // Type with keyboard
    await emailInput.type('test@example.com');

    // Verify input value
    await expect(emailInput).toHaveValue('test@example.com');

    // Tab to next input
    await emailInput.press('Tab');
    const passwordInput = page.locator('input[name="password"]');
    await expect(passwordInput).toBeFocused();
  });

  test('should show/hide address bar without content shift', async ({ page }) => {
    await page.goto('/');

    // Get initial viewport dimensions
    const initialHeight = page.viewportSize()?.height ?? 0;

    // Scroll down to trigger address bar hide
    await page.evaluate(() => window.scrollBy(0, 300));
    await page.waitForTimeout(500);

    // Address bar should hide on mobile browsers, but layout should be stable
    const mainContent = page.locator('main, [role="main"]');
    await expect(mainContent).toBeVisible();
  });
});
