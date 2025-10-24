import http from 'k6/http'
import { check, sleep } from 'k6'

export const options = {
  stages: [
    { duration: '1m', target: 10 },
    { duration: '3m', target: 50 },
    { duration: '1m', target: 10 }
  ],
  thresholds: {
    http_req_duration: ['p(95)<500'],
    http_req_failed: ['rate<0.01']
  }
}

export default function () {
  const res = http.get(`${__ENV.BASE_URL || 'http://localhost:8000'}/health`)
  check(res, {
    'status is 200': (r) => r.status === 200
  })
  sleep(1)
}
