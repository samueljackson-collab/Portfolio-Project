import { test, expect } from '@playwright/test';

test.describe('Checkout Flow', () => {
  test.beforeEach(async ({ page }) => {
    // Login before each test
    await page.goto('/login');
    await page.fill('input[name="email"]', process.env.TEST_USER || 'test@example.com');
    await page.fill('input[name="password"]', process.env.TEST_PASSWORD || 'password123');
    await page.click('button[type="submit"]');
    await page.waitForURL('/dashboard');
  });

  test('should add item to cart', async ({ page }) => {
    await page.goto('/products');

    // Click first "Add to Cart" button
    await page.click('[data-testid="add-to-cart"]:first-of-type');

    // Verify cart counter updates
    const cartCount = page.locator('[data-testid="cart-count"]');
    await expect(cartCount).toHaveText('1');
  });

  test('should complete checkout process', async ({ page }) => {
    // Add item to cart
    await page.goto('/products');
    await page.click('[data-testid="add-to-cart"]:first-of-type');

    // Navigate to cart
    await page.click('[data-testid="cart-icon"]');
    await page.waitForURL('/cart');

    // Verify item in cart
    await expect(page.locator('[data-testid="cart-item"]')).toBeVisible();

    // Proceed to checkout
    await page.click('button:has-text("Checkout")');
    await page.waitForURL('/checkout');

    // Fill shipping information
    await page.fill('input[name="address"]', '123 Test Street');
    await page.fill('input[name="city"]', 'Test City');
    await page.fill('input[name="zip"]', '12345');

    // Fill payment information (test card)
    await page.fill('input[name="cardNumber"]', '4242424242424242');
    await page.fill('input[name="expiry"]', '12/25');
    await page.fill('input[name="cvv"]', '123');

    // Submit order
    await page.click('button:has-text("Place Order")');

    // Verify order confirmation
    await page.waitForURL('/order-confirmation');
    await expect(page.locator('h1')).toContainText('Order Confirmed');
    await expect(page.locator('[data-testid="order-number"]')).toBeVisible();
  });

  test('should update cart quantity', async ({ page }) => {
    // Add item to cart
    await page.goto('/products');
    await page.click('[data-testid="add-to-cart"]:first-of-type');

    // Go to cart
    await page.goto('/cart');

    // Increase quantity
    await page.click('[data-testid="increase-quantity"]');

    // Verify quantity updated
    const quantity = page.locator('[data-testid="item-quantity"]');
    await expect(quantity).toHaveText('2');

    // Verify total price updated
    const totalPrice = page.locator('[data-testid="total-price"]');
    const priceText = await totalPrice.textContent();
    expect(priceText).toContain('$');
  });

  test('should remove item from cart', async ({ page }) => {
    // Add item to cart
    await page.goto('/products');
    await page.click('[data-testid="add-to-cart"]:first-of-type');

    // Go to cart
    await page.goto('/cart');

    // Remove item
    await page.click('[data-testid="remove-item"]');

    // Verify cart is empty
    await expect(page.locator('[data-testid="empty-cart-message"]')).toBeVisible();
  });

  test('should apply discount code', async ({ page }) => {
    // Add item to cart
    await page.goto('/products');
    await page.click('[data-testid="add-to-cart"]:first-of-type');

    // Go to cart
    await page.goto('/cart');

    // Get original price
    const originalPrice = await page.locator('[data-testid="subtotal"]').textContent();

    // Apply discount code
    await page.fill('input[name="discountCode"]', 'TEST10');
    await page.click('button:has-text("Apply")');

    // Verify discount applied
    await expect(page.locator('[data-testid="discount-amount"]')).toBeVisible();
    const newTotal = await page.locator('[data-testid="total-price"]').textContent();
    expect(newTotal).not.toBe(originalPrice);
  });
});
