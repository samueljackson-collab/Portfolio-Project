# Testing Strategy

## Objectives
- Prevent schema drift between mock server and OpenAPI definition.
- Validate critical paths: authentication, pagination, error handling.
- Track latency and error budgets per endpoint.

## Test Matrix
| ID | Area | Steps | Expected |
|----|------|-------|----------|
| TC-API-01 | Auth success | Call `/auth/token` with valid client credentials. | 200 OK, JWT in response, schema matches. |
| TC-API-02 | Auth failure | Call `/auth/token` with invalid secret. | 401 with `error` body matching schema. |
| TC-API-03 | Pagination | Fetch `/orders?page=2&pageSize=20`. | `items` length 20, `pageInfo.next` present. |
| TC-API-04 | Contract drift | Run schema validator against live responses. | Zero mismatches; failures break build. |

## Execution
- Local: `npm run mock` in `producer/` then `npm run test:collections`.
- CI: Newman run with JUnit export consumed by `consumer/report.py`.
- K8s smoke: `kubectl port-forward svc/api-mock 8080:80` then run `newman` targeting forwarded URL.
