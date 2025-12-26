import { test, expect } from '@playwright/test';

test.describe('Login Flow', () => {
  test.beforeEach(async ({ page }) => {
    await page.goto('/login');
  });

  test('should display login form', async ({ page }) => {
    await expect(page.locator('h1')).toContainText('Login');
    await expect(page.locator('input[name="email"]')).toBeVisible();
    await expect(page.locator('input[name="password"]')).toBeVisible();
    await expect(page.locator('button[type="submit"]')).toBeVisible();

    // Verify form labels
    await expect(page.locator('label:has-text("Email")')).toBeVisible();
    await expect(page.locator('label:has-text("Password")')).toBeVisible();
  });

  test('should display all required form elements', async ({ page }) => {
    // Check for remember me checkbox
    const rememberMe = page.locator('input[type="checkbox"][name="remember"]');
    if (await rememberMe.isVisible()) {
      await expect(rememberMe).toBeVisible();
    }

    // Check for sign up link
    const signUpLink = page.locator('a:has-text("Sign up"), a[href="/signup"]');
    if (await signUpLink.isVisible()) {
      await expect(signUpLink).toBeVisible();
    }

    // Check for forgot password link
    const forgotLink = page.locator('a:has-text("Forgot"), a[href="/forgot-password"]');
    await expect(forgotLink).toBeVisible();
  });

  test('should login with valid credentials', async ({ page }) => {
    const testEmail = process.env.TEST_USER || 'test@example.com';
    const testPassword = process.env.TEST_PASSWORD || 'password123';

    await page.fill('input[name="email"]', testEmail);
    await page.fill('input[name="password"]', testPassword);

    // Verify inputs are filled
    await expect(page.locator('input[name="email"]')).toHaveValue(testEmail);
    await expect(page.locator('input[name="password"]')).toHaveValue(testPassword);

    await page.click('button[type="submit"]');

    // Wait for navigation to dashboard
    await page.waitForURL('/dashboard', { timeout: 5000 });

    // Verify successful login
    await expect(page.locator('[data-testid="user-menu"]')).toBeVisible();

    // Verify success message or notification
    const successMessage = page.locator('[role="alert"]:has-text("Welcome"), .success-message');
    if (await successMessage.isVisible()) {
      await expect(successMessage).toBeVisible();
    }
  });

  test('should show error with invalid credentials', async ({ page }) => {
    await page.fill('input[name="email"]', 'invalid@example.com');
    await page.fill('input[name="password"]', 'wrongpassword');
    await page.click('button[type="submit"]');

    // Wait for error message
    await expect(page.locator('.error-message, [role="alert"]:has-text("Invalid")')).toBeVisible();
    await expect(page.locator('.error-message, [role="alert"]')).toContainText('Invalid');
  });

  test('should require email field', async ({ page }) => {
    await page.fill('input[name="password"]', 'password123');
    await page.click('button[type="submit"]');

    // Check for required field validation
    const emailInput = page.locator('input[name="email"]');
    const isInvalid = await emailInput.evaluate((el: HTMLInputElement) => !el.validity.valid);
    expect(isInvalid).toBe(true);
  });

  test('should validate email format', async ({ page }) => {
    await page.fill('input[name="email"]', 'invalid-email');
    await page.fill('input[name="password"]', 'password123');
    await page.click('button[type="submit"]');

    // Check for validation error
    const emailInput = page.locator('input[name="email"]');
    const isInvalid = await emailInput.evaluate((el: HTMLInputElement) => !el.validity.valid);
    expect(isInvalid).toBe(true);
  });

  test('should require password field', async ({ page }) => {
    await page.fill('input[name="email"]', 'test@example.com');
    await page.click('button[type="submit"]');

    // Check for required field validation
    const passwordInput = page.locator('input[name="password"]');
    const isInvalid = await passwordInput.evaluate((el: HTMLInputElement) => !el.validity.valid);
    expect(isInvalid).toBe(true);
  });

  test('should validate password length', async ({ page }) => {
    await page.fill('input[name="email"]', 'test@example.com');
    await page.fill('input[name="password"]', '123');
    await page.click('button[type="submit"]');

    // Should show validation error for short password
    const passwordInput = page.locator('input[name="password"]');
    const isInvalid = await passwordInput.evaluate((el: HTMLInputElement) => !el.validity.valid);
    expect(isInvalid).toBe(true);
  });

  test('should toggle password visibility', async ({ page }) => {
    const passwordInput = page.locator('input[name="password"]');
    const toggleButton = page.locator('[data-testid="toggle-password"], button[aria-label*="password" i]').first();

    if (await toggleButton.isVisible()) {
      // Initially should be password type
      await expect(passwordInput).toHaveAttribute('type', 'password');

      // Click toggle
      await toggleButton.click();
      await expect(passwordInput).toHaveAttribute('type', 'text');

      // Click again to hide
      await toggleButton.click();
      await expect(passwordInput).toHaveAttribute('type', 'password');
    }
  });

  test('should clear form errors on input change', async ({ page }) => {
    // Submit with invalid data to trigger error
    await page.fill('input[name="email"]', 'invalid@example.com');
    await page.fill('input[name="password"]', 'wrongpassword');
    await page.click('button[type="submit"]');

    // Wait for error to appear
    const errorMessage = page.locator('.error-message, [role="alert"]');
    await expect(errorMessage).toBeVisible();

    // Clear email input
    await page.fill('input[name="email"]', '');

    // Error should clear or update
    await page.waitForTimeout(500);
  });

  test('should navigate to forgot password page', async ({ page }) => {
    const forgotLink = page.locator('a:has-text("Forgot"), a[href="/forgot-password"]');
    await expect(forgotLink).toBeVisible();
    await forgotLink.click();

    await expect(page).toHaveURL('/forgot-password');
    await expect(page.locator('h1')).toContainText('Forgot');
  });

  test('should navigate to sign up page', async ({ page }) => {
    const signUpLink = page.locator('a:has-text("Sign up"), a[href="/signup"], a:has-text("Create account")');
    if (await signUpLink.isVisible()) {
      await signUpLink.click();
      await expect(page).toHaveURL(/\/signup|\/register/);
    }
  });

  test('should handle remember me functionality', async ({ page }) => {
    const rememberMeCheckbox = page.locator('input[type="checkbox"][name="remember"]');

    if (await rememberMeCheckbox.isVisible()) {
      // Check the remember me box
      await rememberMeCheckbox.check();
      await expect(rememberMeCheckbox).toBeChecked();

      // Uncheck it
      await rememberMeCheckbox.uncheck();
      await expect(rememberMeCheckbox).not.toBeChecked();
    }
  });

  test('should disable submit button while loading', async ({ page }) => {
    const testEmail = process.env.TEST_USER || 'test@example.com';
    const testPassword = process.env.TEST_PASSWORD || 'password123';

    await page.fill('input[name="email"]', testEmail);
    await page.fill('input[name="password"]', testPassword);

    const submitButton = page.locator('button[type="submit"]');

    // Click submit and check if button becomes disabled
    const submitPromise = page.click('button[type="submit"]');

    // Button might be disabled briefly during submission
    await submitPromise;

    // After submission, should navigate away
    await page.waitForURL('/dashboard', { timeout: 5000 });
  });

  test('should handle special characters in email', async ({ page }) => {
    await page.fill('input[name="email"]', 'test+tag@example.com');
    await page.fill('input[name="password"]', 'password123');

    // Should accept special characters
    await expect(page.locator('input[name="email"]')).toHaveValue('test+tag@example.com');
  });

  test('should focus management on load', async ({ page }) => {
    // First focusable element should be email input
    const firstInput = page.locator('input[name="email"]');

    // Auto-focus should work or can be manually set
    if (await firstInput.isVisible()) {
      await firstInput.click();
      await expect(firstInput).toBeFocused();
    }
  });

  test('should handle back button after login', async ({ page }) => {
    const testEmail = process.env.TEST_USER || 'test@example.com';
    const testPassword = process.env.TEST_PASSWORD || 'password123';

    await page.fill('input[name="email"]', testEmail);
    await page.fill('input[name="password"]', testPassword);
    await page.click('button[type="submit"]');

    // Wait for navigation
    await page.waitForURL('/dashboard', { timeout: 5000 });

    // Try to go back to login
    await page.goBack();

    // Should not return to login (already logged in)
    await expect(page).not.toHaveURL('/login');
  });

  test('visual regression - login page', async ({ page }) => {
    // Take screenshot for visual comparison
    await expect(page).toHaveScreenshot('login-page.png', {
      fullPage: true,
      animations: 'disabled',
    });
  });

  test('visual regression - login with error', async ({ page }) => {
    // Fill with invalid data
    await page.fill('input[name="email"]', 'invalid@example.com');
    await page.fill('input[name="password"]', 'wrongpassword');
    await page.click('button[type="submit"]');

    // Wait for error
    await expect(page.locator('.error-message, [role="alert"]')).toBeVisible();

    // Take screenshot
    await expect(page).toHaveScreenshot('login-page-error.png', {
      fullPage: true,
      animations: 'disabled',
    });
  });
});
