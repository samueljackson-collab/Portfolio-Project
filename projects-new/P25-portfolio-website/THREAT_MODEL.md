# Threat Model

Threats:
- Leaked CMS tokens
- Broken links after content change
- Performance regressions

Mitigations:
- Store secrets in Vercel env
- Link checker in CI
- Lighthouse budgets enforced in pipeline
