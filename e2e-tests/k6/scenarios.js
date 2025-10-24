import http from 'k6/http'
import { sleep } from 'k6'

export const options = {
  scenarios: {
    smoke: {
      executor: 'constant-vus',
      vus: 1,
      duration: '1m'
    },
    load: {
      executor: 'ramping-vus',
      startVUs: 1,
      stages: [
        { duration: '2m', target: 10 },
        { duration: '3m', target: 50 },
        { duration: '1m', target: 0 }
      ]
    },
    stress: {
      executor: 'ramping-arrival-rate',
      startRate: 10,
      timeUnit: '1s',
      stages: [
        { target: 100, duration: '2m' },
        { target: 200, duration: '2m' },
        { target: 0, duration: '1m' }
      ]
    }
  }
}

export default function () {
  http.get(`${__ENV.BASE_URL || 'http://localhost:8000'}/health`)
  sleep(1)
}
