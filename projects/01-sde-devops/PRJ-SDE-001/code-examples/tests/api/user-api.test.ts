// tests/api/user-api.test.ts
import { test, expect } from '@playwright/test';

const API_BASE_URL = process.env.API_URL || 'http://localhost:3000/api';

test.describe('User API Tests', () => {
  let authToken: string;
  let userId: string;

  test.beforeAll(async ({ request }) => {
    // Create a test user and get auth token
    const response = await request.post(`${API_BASE_URL}/auth/register`, {
      data: {
        email: `test${Date.now()}@example.com`,
        password: 'SecurePass123!',
        firstName: 'Test',
        lastName: 'User'
      }
    });

    expect(response.ok()).toBeTruthy();
    const data = await response.json();
    authToken = data.token;
    userId = data.user.id;
  });

  test('GET /users/:id should return user data', async ({ request }) => {
    const response = await request.get(`${API_BASE_URL}/users/${userId}`, {
      headers: {
        'Authorization': `Bearer ${authToken}`
      }
    });

    expect(response.status()).toBe(200);
    const user = await response.json();

    expect(user).toMatchObject({
      id: userId,
      email: expect.stringContaining('@example.com'),
      firstName: 'Test',
      lastName: 'User'
    });
    expect(user.password).toBeUndefined();
  });

  test('PUT /users/:id should update user data', async ({ request }) => {
    const updateData = {
      firstName: 'Updated',
      lastName: 'Name'
    };

    const response = await request.put(`${API_BASE_URL}/users/${userId}`, {
      headers: {
        'Authorization': `Bearer ${authToken}`
      },
      data: updateData
    });

    expect(response.status()).toBe(200);
    const user = await response.json();

    expect(user.firstName).toBe('Updated');
    expect(user.lastName).toBe('Name');
  });

  test('GET /users without auth should return 401', async ({ request }) => {
    const response = await request.get(`${API_BASE_URL}/users/${userId}`);
    expect(response.status()).toBe(401);
  });

  test('POST /users with invalid data should return 400', async ({ request }) => {
    const response = await request.post(`${API_BASE_URL}/auth/register`, {
      data: {
        email: 'invalid-email',
        password: 'weak'
      }
    });

    expect(response.status()).toBe(400);
    const error = await response.json();
    expect(error.message).toContain('validation');
  });
});
