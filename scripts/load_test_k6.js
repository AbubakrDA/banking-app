import http from 'k6/http';
import { check, sleep } from 'k6';

// BankingAIPlatform Stage F Distributed Load Test (Target: 500 Virtual Users)
export const options = {
  stages: [
    { duration: '1m', target: 50 },   // Warm up
    { duration: '2m', target: 250 },  // Ramp up
    { duration: '3m', target: 500 },  // Peak 500 concurrent VUs
    { duration: '1m', target: 0 },    // Ramp down
  ],
  thresholds: {
    http_req_duration: ['p(95)<250', 'p(99)<500'],
    http_req_failed: ['rate<0.01'],
  },
};

const BASE_URL = __ENV.STAGING_BASE_URL || 'https://staging.banking-ai-platform.com';

export default function () {
  const healthRes = http.get(`${BASE_URL}/api/v1/health`);
  check(healthRes, {
    'health status is 200': (r) => r.status === 200,
  });

  sleep(1);
}
