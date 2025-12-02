# Threat Model — P08

## Assets
- Postman environments, request payload samples, auth tokens (in vault), generated reports.

## Entry Points
- Newman CLI executing against base URLs, mock server docker network, CI secrets injection.

## Threats
- **Credential leakage:** accidentally committing real tokens.
- **Sensitive data in reports:** user PII in HTML/JSON outputs.
- **Abuse of mock server:** open port accessible beyond dev network.

## Mitigations
- `.gitignore` covers `.env`/`*.postman_environment.json` (non-example).
- Reporter configured to mask headers and body fields; `scripts/sanitize_payloads.sh` before sharing.
- Mock server bound to localhost in docker compose.

## Residual Risk
- Correlation IDs may map to backend logs; keep artifact sharing limited to project team.
