// tests/performance/load-test.js
import http from 'k6/http';
import { check, sleep } from 'k6';
import { Rate, Trend, Counter } from 'k6/metrics';

// Custom metrics
const errorRate = new Rate('errors');
const responseTime = new Trend('response_time');
const requestCount = new Counter('requests');

export const options = {
  stages: [
    { duration: '2m', target: 50 },   // Ramp-up to 50 users
    { duration: '5m', target: 50 },   // Stay at 50 users
    { duration: '2m', target: 100 },  // Ramp-up to 100 users
    { duration: '5m', target: 100 },  // Stay at 100 users
    { duration: '2m', target: 200 },  // Ramp-up to 200 users
    { duration: '5m', target: 200 },  // Stay at 200 users
    { duration: '5m', target: 0 },    // Ramp-down to 0 users
  ],
  thresholds: {
    'http_req_duration': ['p(95)<500', 'p(99)<1000'], // 95% < 500ms, 99% < 1s
    'http_req_failed': ['rate<0.01'],                  // Error rate < 1%
    'errors': ['rate<0.01'],
  },
};

const BASE_URL = __ENV.API_URL || 'https://staging.example.com/api';

/**
 * Create test users by registering accounts and return their credentials and identifiers.
 *
 * Registers ten test users and collects each user's email, password, authentication token, and userId.
 * @returns {{users: {email: string, password: string, token: string, userId: string}[]}} An object with a `users` array containing credentials and identifiers for the created test users.
 */
export function setup() {
  // Create test users
  const users = [];
  for (let i = 0; i < 10; i++) {
    const email = `loadtest${Date.now()}_${i}@example.com`;
    const password = 'LoadTest123!';

    const response = http.post(`${BASE_URL}/auth/register`, JSON.stringify({
      email,
      password,
      firstName: 'Load',
      lastName: `Test${i}`
    }), {
      headers: { 'Content-Type': 'application/json' },
    });

    if (response.status === 201) {
      const data = JSON.parse(response.body);
      users.push({
        email,
        password,
        token: data.token,
        userId: data.user.id
      });
    }
  }

  return { users };
}

export default function(data) {
  const user = data.users[Math.floor(Math.random() * data.users.length)];

  // Scenario 1: User Login
  loginScenario(user);
  sleep(1);

  // Scenario 2: Browse Products
  browseProducts(user);
  sleep(1);

  // Scenario 3: Search
  searchScenario(user);
  sleep(1);

  // Scenario 4: View Profile
  viewProfile(user);
  sleep(1);
}

/**
 * Performs a login request for the provided user and records request metrics and error rate.
 *
 * Sends credentials to the /auth/login endpoint, increments the request counter, records the response duration,
 * and updates the global error rate based on whether the response status is 200 and a token is returned.
 *
 * @param {{email: string, password: string}} user - User credentials used to authenticate; must include `email` and `password`.
 */
function loginScenario(user) {
  const response = http.post(`${BASE_URL}/auth/login`, JSON.stringify({
    email: user.email,
    password: user.password
  }), {
    headers: { 'Content-Type': 'application/json' },
    tags: { name: 'Login' }
  });

  requestCount.add(1);
  responseTime.add(response.timings.duration);

  const success = check(response, {
    'login status is 200': (r) => r.status === 200,
    'login returns token': (r) => JSON.parse(r.body).token !== undefined,
  });

  errorRate.add(!success);
}

/**
 * Fetches the product catalog using the provided user's token, records request metrics, and updates the error rate based on basic response checks.
 *
 * Performs checks that the response status is 200 and that the response body contains a non-empty `data` array; increments the request counter, records the response duration, and marks the request as an error if the checks fail.
 *
 * @param {Object} user - Test user credentials.
 * @param {string} user.token - Bearer token used for the Authorization header.
 */
function browseProducts(user) {
  const response = http.get(`${BASE_URL}/products`, {
    headers: {
      'Authorization': `Bearer ${user.token}`
    },
    tags: { name: 'BrowseProducts' }
  });

  requestCount.add(1);
  responseTime.add(response.timings.duration);

  const success = check(response, {
    'browse status is 200': (r) => r.status === 200,
    'browse returns products': (r) => JSON.parse(r.body).data.length > 0,
  });

  errorRate.add(!success);
}

/**
 * Executes a search request with the given user's credentials and records metrics and checks.
 *
 * Sends a GET /search?q={query} using the user's bearer token, increments the request counter,
 * records response time, and updates the error rate based on status and result presence.
 *
 * @param {{ token: string, [key: string]: any }} user - Test user object; `user.token` is used for the Authorization header.
 */
function searchScenario(user) {
  const queries = ['laptop', 'phone', 'tablet', 'headphones'];
  const query = queries[Math.floor(Math.random() * queries.length)];

  const response = http.get(`${BASE_URL}/search?q=${query}`, {
    headers: {
      'Authorization': `Bearer ${user.token}`
    },
    tags: { name: 'Search' }
  });

  requestCount.add(1);
  responseTime.add(response.timings.duration);

  const success = check(response, {
    'search status is 200': (r) => r.status === 200,
    'search returns results': (r) => JSON.parse(r.body).results !== undefined,
  });

  errorRate.add(!success);
}

/**
 * Fetches the specified user's profile, validates the response, and records request metrics and error rate.
 * @param {{userId: string, token: string}} user - Object with `userId` and bearer `token` used to authorize the request; the function records a request count, response time, and updates the error rate based on validation of the response.
 */
function viewProfile(user) {
  const response = http.get(`${BASE_URL}/users/${user.userId}`, {
    headers: {
      'Authorization': `Bearer ${user.token}`
    },
    tags: { name: 'ViewProfile' }
  });

  requestCount.add(1);
  responseTime.add(response.timings.duration);

  const success = check(response, {
    'profile status is 200': (r) => r.status === 200,
    'profile returns user data': (r) => JSON.parse(r.body).id === user.userId,
  });

  errorRate.add(!success);
}

/**
 * Delete the test users created during setup.
 *
 * Iterates over data.users and issues DELETE requests to /users/{userId} using each user's token for authorization.
 * @param {Object} data - The object returned from setup, expected to contain a `users` array of `{ userId, token }` entries.
 */
export function teardown(data) {
  // Cleanup test users
  data.users.forEach(user => {
    http.del(`${BASE_URL}/users/${user.userId}`, null, {
      headers: {
        'Authorization': `Bearer ${user.token}`
      }
    });
  });
}