import http from 'k6/http';
import { sleep, check } from 'k6';

export const options = {
  vus: 5,
  duration: '30s',
};

export default function () {
  const res = http.get(`${__ENV.API_BASE_URL || 'http://localhost:8000'}/healthz`);
  check(res, {
    'status is 200': (r) => r.status === 200,
  });
  sleep(1);
}
