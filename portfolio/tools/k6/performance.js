import http from 'k6/http';
import { check, sleep } from 'k6';

export const options = {
  vus: 5,
  duration: '30s',
  thresholds: {
    http_req_duration: ['p(95)<500'],
  },
};

const BASE_URL = __ENV.BASE_URL || 'http://localhost:8000';

export default function () {
  const res = http.get(`${BASE_URL}/api/projects`);
  check(res, {
    'status is 200': (r) => r.status === 200,
    'responds quickly': (r) => r.timings.duration < 500,
  });
  sleep(1);
}
