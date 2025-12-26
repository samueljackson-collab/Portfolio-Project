import { test, expect } from '@playwright/test';

test.describe('Admin Dashboard', () => {
  test.beforeEach(async ({ page }) => {
    // Login with admin credentials
    const adminEmail = process.env.ADMIN_USER || 'admin@example.com';
    const adminPassword = process.env.ADMIN_PASSWORD || 'adminpass123';

    await page.goto('/login');
    await page.fill('input[name="email"]', adminEmail);
    await page.fill('input[name="password"]', adminPassword);
    await page.click('button[type="submit"]');

    // Wait for dashboard navigation
    await page.waitForURL('/admin/dashboard', { timeout: 5000 });
  });

  test('should display admin dashboard', async ({ page }) => {
    // Verify admin dashboard is loaded
    await expect(page.locator('h1')).toContainText('Admin Dashboard');
    await expect(page.locator('[data-testid="admin-nav"]')).toBeVisible();
    await expect(page.locator('[data-testid="users-section"]')).toBeVisible();
    await expect(page.locator('[data-testid="analytics-section"]')).toBeVisible();
  });

  test('should show user management section', async ({ page }) => {
    // Verify user management is accessible
    const usersNav = page.locator('[data-testid="users-nav"]');
    await expect(usersNav).toBeVisible();
    await usersNav.click();

    // Wait for users list to load
    await expect(page.locator('[data-testid="users-list"]')).toBeVisible();
    await expect(page.locator('[data-testid="user-row"]')).toBeVisible();
  });

  test('should filter users by status', async ({ page }) => {
    // Navigate to users section
    await page.locator('[data-testid="users-nav"]').click();
    await page.waitForLoadState('networkidle');

    // Select status filter
    const statusFilter = page.locator('[data-testid="status-filter"]');
    await statusFilter.click();
    await page.locator('text=Active').click();

    // Verify filtered results
    await expect(page.locator('[data-testid="user-row"]')).toBeDefined();
    const resultText = await page.locator('[data-testid="filter-result-count"]').textContent();
    expect(resultText).toMatch(/\d+ results/);
  });

  test('should search users', async ({ page }) => {
    // Navigate to users section
    await page.locator('[data-testid="users-nav"]').click();

    // Use search input
    const searchInput = page.locator('input[placeholder="Search users..."]');
    await searchInput.fill('john');
    await page.waitForLoadState('networkidle');

    // Verify search results
    const userRows = page.locator('[data-testid="user-row"]');
    const count = await userRows.count();
    expect(count).toBeGreaterThan(0);
  });

  test('should edit user details', async ({ page }) => {
    // Navigate to users section
    await page.locator('[data-testid="users-nav"]').click();
    await page.waitForLoadState('networkidle');

    // Click edit button on first user
    await page.locator('[data-testid="edit-user"]:first-of-type').click();

    // Verify edit form is displayed
    await expect(page.locator('h2')).toContainText('Edit User');
    await expect(page.locator('input[name="email"]')).toBeVisible();
    await expect(page.locator('input[name="name"]')).toBeVisible();
  });

  test('should display analytics dashboard', async ({ page }) => {
    // Click analytics section
    await page.locator('[data-testid="analytics-section"]').click();

    // Verify analytics elements are displayed
    await expect(page.locator('[data-testid="total-users-card"]')).toBeVisible();
    await expect(page.locator('[data-testid="active-sessions-card"]')).toBeVisible();
    await expect(page.locator('[data-testid="revenue-card"]')).toBeVisible();
    await expect(page.locator('[data-testid="analytics-chart"]')).toBeVisible();
  });

  test('should view system logs', async ({ page }) => {
    // Navigate to logs section
    await page.locator('[data-testid="logs-nav"]').click();

    // Verify logs are displayed
    await expect(page.locator('[data-testid="logs-table"]')).toBeVisible();
    await expect(page.locator('[data-testid="log-entry"]')).toBeVisible();

    // Verify log details can be expanded
    await page.locator('[data-testid="log-entry"]:first-of-type').click();
    await expect(page.locator('[data-testid="log-details"]')).toBeVisible();
  });

  test('should filter logs by level', async ({ page }) => {
    // Navigate to logs section
    await page.locator('[data-testid="logs-nav"]').click();

    // Filter by error level
    const levelFilter = page.locator('[data-testid="level-filter"]');
    await levelFilter.click();
    await page.locator('text=ERROR').click();

    // Verify filtered logs
    await page.waitForLoadState('networkidle');
    const logEntries = page.locator('[data-testid="log-entry"]');
    const count = await logEntries.count();
    expect(count).toBeGreaterThan(0);
  });

  test('should display system health metrics', async ({ page }) => {
    // Navigate to metrics section
    await page.locator('[data-testid="metrics-nav"]').click();

    // Verify health metrics are displayed
    await expect(page.locator('[data-testid="cpu-usage"]')).toBeVisible();
    await expect(page.locator('[data-testid="memory-usage"]')).toBeVisible();
    await expect(page.locator('[data-testid="disk-usage"]')).toBeVisible();
    await expect(page.locator('[data-testid="uptime"]')).toBeVisible();
  });

  test('should manage roles and permissions', async ({ page }) => {
    // Navigate to roles section
    await page.locator('[data-testid="roles-nav"]').click();

    // Verify roles list is displayed
    await expect(page.locator('[data-testid="roles-list"]')).toBeVisible();
    await expect(page.locator('[data-testid="role-item"]')).toBeVisible();

    // Click to view permissions
    await page.locator('[data-testid="view-permissions"]:first-of-type').click();
    await expect(page.locator('[data-testid="permissions-modal"]')).toBeVisible();
  });

  test('should export data', async ({ page }) => {
    // Navigate to export section
    await page.locator('[data-testid="export-nav"]').click();

    // Click export button
    const exportButton = page.locator('[data-testid="export-button"]');
    await expect(exportButton).toBeVisible();

    // Setup download handler
    const downloadPromise = page.waitForEvent('download');
    await exportButton.click();
    const download = await downloadPromise;

    // Verify download
    expect(download.suggestedFilename()).toMatch(/\.csv$/);
  });

  test('should display notifications/alerts', async ({ page }) => {
    // Check for notification badge
    const notificationBadge = page.locator('[data-testid="notification-badge"]');
    await expect(notificationBadge).toBeVisible();

    // Click to open notifications
    await notificationBadge.click();
    await expect(page.locator('[data-testid="notification-panel"]')).toBeVisible();
    await expect(page.locator('[data-testid="notification-item"]')).toBeVisible();
  });

  test('visual regression - admin dashboard', async ({ page }) => {
    // Take screenshot for visual comparison
    await expect(page).toHaveScreenshot('admin-dashboard.png', {
      fullPage: true,
      animations: 'disabled',
    });
  });

  test('should have responsive admin menu', async ({ page }) => {
    // Check if hamburger menu exists on smaller screens
    const hamburger = page.locator('[data-testid="admin-menu-toggle"]');

    if (await hamburger.isVisible()) {
      // Click to open/close menu
      await hamburger.click();
      await expect(page.locator('[data-testid="admin-nav"]')).toHaveAttribute(
        'aria-expanded',
        'true'
      );

      // Close menu
      await hamburger.click();
      await expect(page.locator('[data-testid="admin-nav"]')).toHaveAttribute(
        'aria-expanded',
        'false'
      );
    }
  });
});
