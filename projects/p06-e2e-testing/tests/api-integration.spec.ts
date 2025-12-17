import { test, expect } from '@playwright/test';

test.describe('API Integration Tests', () => {
  const baseURL = process.env.BASE_URL || 'http://localhost:3000';
  const apiBaseURL = process.env.API_BASE_URL || 'http://localhost:3001';
  let authToken: string;

  test.beforeEach(async ({ page, context }) => {
    // Login and capture auth token
    const testEmail = process.env.TEST_USER || 'test@example.com';
    const testPassword = process.env.TEST_PASSWORD || 'password123';

    await page.goto(`${baseURL}/login`);
    await page.fill('input[name="email"]', testEmail);
    await page.fill('input[name="password"]', testPassword);
    await page.click('button[type="submit"]');

    // Wait for navigation to dashboard
    await page.waitForURL(`${baseURL}/dashboard`, { timeout: 5000 });

    // Extract auth token from localStorage or cookies
    const cookies = await context.cookies();
    const authCookie = cookies.find(c => c.name === 'authToken');
    if (authCookie) {
      authToken = authCookie.value;
    }
  });

  test('should fetch user profile via API', async ({ request }) => {
    const response = await request.get(`${apiBaseURL}/api/users/profile`, {
      headers: {
        'Authorization': `Bearer ${authToken}`,
        'Content-Type': 'application/json',
      },
    });

    expect(response.status()).toBe(200);
    const data = await response.json();
    expect(data).toHaveProperty('id');
    expect(data).toHaveProperty('email');
    expect(data).toHaveProperty('name');
  });

  test('should update user profile via API', async ({ request }) => {
    const updateData = {
      name: 'Updated Name',
      bio: 'Test bio',
    };

    const response = await request.put(`${apiBaseURL}/api/users/profile`, {
      headers: {
        'Authorization': `Bearer ${authToken}`,
        'Content-Type': 'application/json',
      },
      data: updateData,
    });

    expect(response.status()).toBe(200);
    const data = await response.json();
    expect(data.name).toBe(updateData.name);
    expect(data.bio).toBe(updateData.bio);
  });

  test('should fetch products list with pagination', async ({ request }) => {
    const response = await request.get(`${apiBaseURL}/api/products`, {
      params: {
        page: 1,
        limit: 10,
      },
    });

    expect(response.status()).toBe(200);
    const data = await response.json();
    expect(data).toHaveProperty('items');
    expect(data).toHaveProperty('total');
    expect(data).toHaveProperty('page');
    expect(Array.isArray(data.items)).toBe(true);
  });

  test('should search products with filters', async ({ request }) => {
    const response = await request.get(`${apiBaseURL}/api/products/search`, {
      params: {
        query: 'laptop',
        category: 'electronics',
        minPrice: 100,
        maxPrice: 2000,
      },
    });

    expect(response.status()).toBe(200);
    const data = await response.json();
    expect(Array.isArray(data.results)).toBe(true);
  });

  test('should create shopping cart item via API', async ({ request }) => {
    const cartItem = {
      productId: '123',
      quantity: 2,
      variantId: 'color-blue',
    };

    const response = await request.post(`${apiBaseURL}/api/cart/items`, {
      headers: {
        'Authorization': `Bearer ${authToken}`,
        'Content-Type': 'application/json',
      },
      data: cartItem,
    });

    expect(response.status()).toBe(201);
    const data = await response.json();
    expect(data).toHaveProperty('cartId');
    expect(data.quantity).toBe(cartItem.quantity);
  });

  test('should retrieve shopping cart contents', async ({ request }) => {
    const response = await request.get(`${apiBaseURL}/api/cart`, {
      headers: {
        'Authorization': `Bearer ${authToken}`,
      },
    });

    expect(response.status()).toBe(200);
    const data = await response.json();
    expect(data).toHaveProperty('id');
    expect(data).toHaveProperty('items');
    expect(data).toHaveProperty('total');
    expect(Array.isArray(data.items)).toBe(true);
  });

  test('should update cart item quantity', async ({ request }) => {
    const updateData = {
      quantity: 5,
    };

    const response = await request.patch(`${apiBaseURL}/api/cart/items/item-123`, {
      headers: {
        'Authorization': `Bearer ${authToken}`,
        'Content-Type': 'application/json',
      },
      data: updateData,
    });

    expect(response.status()).toBe(200);
    const data = await response.json();
    expect(data.quantity).toBe(updateData.quantity);
  });

  test('should delete cart item', async ({ request }) => {
    const response = await request.delete(`${apiBaseURL}/api/cart/items/item-123`, {
      headers: {
        'Authorization': `Bearer ${authToken}`,
      },
    });

    expect(response.status()).toBe(204);
  });

  test('should create order via API', async ({ request }) => {
    const orderData = {
      shippingAddress: {
        street: '123 Test St',
        city: 'Test City',
        state: 'TS',
        zip: '12345',
        country: 'US',
      },
      paymentMethod: 'credit_card',
      paymentToken: 'tok_test_1234567890',
    };

    const response = await request.post(`${apiBaseURL}/api/orders`, {
      headers: {
        'Authorization': `Bearer ${authToken}`,
        'Content-Type': 'application/json',
      },
      data: orderData,
    });

    expect(response.status()).toBe(201);
    const data = await response.json();
    expect(data).toHaveProperty('orderId');
    expect(data).toHaveProperty('status');
    expect(data.status).toBe('pending');
  });

  test('should retrieve order details', async ({ request }) => {
    const response = await request.get(`${apiBaseURL}/api/orders/order-123`, {
      headers: {
        'Authorization': `Bearer ${authToken}`,
      },
    });

    expect(response.status()).toBe(200);
    const data = await response.json();
    expect(data).toHaveProperty('id');
    expect(data).toHaveProperty('items');
    expect(data).toHaveProperty('total');
    expect(data).toHaveProperty('status');
    expect(data).toHaveProperty('createdAt');
  });

  test('should list user orders', async ({ request }) => {
    const response = await request.get(`${apiBaseURL}/api/orders`, {
      headers: {
        'Authorization': `Bearer ${authToken}`,
      },
      params: {
        page: 1,
        limit: 10,
      },
    });

    expect(response.status()).toBe(200);
    const data = await response.json();
    expect(data).toHaveProperty('orders');
    expect(data).toHaveProperty('total');
    expect(Array.isArray(data.orders)).toBe(true);
  });

  test('should handle invalid credentials gracefully', async ({ request }) => {
    const response = await request.get(`${apiBaseURL}/api/users/profile`, {
      headers: {
        'Authorization': 'Bearer invalid_token',
      },
    });

    expect(response.status()).toBe(401);
    const data = await response.json();
    expect(data).toHaveProperty('error');
    expect(data.error).toContain('unauthorized');
  });

  test('should handle missing required fields', async ({ request }) => {
    const invalidData = {
      // Missing required field 'email'
      name: 'Test User',
    };

    const response = await request.post(`${apiBaseURL}/api/users`, {
      headers: {
        'Content-Type': 'application/json',
      },
      data: invalidData,
    });

    expect(response.status()).toBe(400);
    const data = await response.json();
    expect(data).toHaveProperty('error');
    expect(data.errors).toBeDefined();
  });

  test('should validate email format in API', async ({ request }) => {
    const invalidData = {
      email: 'invalid-email',
      name: 'Test User',
      password: 'SecurePass123!',
    };

    const response = await request.post(`${apiBaseURL}/api/users`, {
      headers: {
        'Content-Type': 'application/json',
      },
      data: invalidData,
    });

    expect(response.status()).toBe(400);
    const data = await response.json();
    expect(data.errors).toContain(
      expect.objectContaining({ field: 'email' })
    );
  });

  test('should apply discount code via API', async ({ request }) => {
    const response = await request.post(`${apiBaseURL}/api/discounts/apply`, {
      headers: {
        'Authorization': `Bearer ${authToken}`,
        'Content-Type': 'application/json',
      },
      data: {
        code: 'SAVE10',
      },
    });

    expect(response.status()).toBe(200);
    const data = await response.json();
    expect(data).toHaveProperty('discountAmount');
    expect(data.discountAmount).toBeGreaterThan(0);
  });

  test('should handle rate limiting', async ({ request }) => {
    // Make multiple requests to trigger rate limiting
    let response;
    for (let i = 0; i < 150; i++) {
      response = await request.get(`${apiBaseURL}/api/products`, {
        params: { page: i % 10 },
      });

      if (response.status() === 429) {
        break;
      }
    }

    // Should eventually get rate limited
    expect(response?.status()).toBe(429);
    const data = await response?.json();
    expect(data).toHaveProperty('error');
  });

  test('should have proper CORS headers', async ({ request }) => {
    const response = await request.get(`${apiBaseURL}/api/products`);

    const corsHeader = response.headers()['access-control-allow-origin'];
    expect(corsHeader).toBeDefined();
  });

  test('should cache GET requests appropriately', async ({ request }) => {
    const response1 = await request.get(`${apiBaseURL}/api/products/123`);
    const cacheControl = response1.headers()['cache-control'];

    // Verify cache headers are set
    if (response1.status() === 200) {
      expect(cacheControl).toBeDefined();
    }
  });
});
