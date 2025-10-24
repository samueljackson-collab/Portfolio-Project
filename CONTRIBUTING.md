# Contributing

Thank you for contributing! Please follow these guidelines.

- Branches: use feature branches and include a short descriptive name.
- Commit messages: use concise, imperative messages.
- PRs: attach a description, related issue, and ensure CI passes.
- Tests: add unit tests for new functionality and run `npm test` before opening a PR.
- Docs: update the documentation and include build steps.
- Secrets: do not commit secrets. See the Security section below.

Security
- Do not commit API keys, tokens, or credentials. Use environment variables or a secret manager.

Local development
- Install dependencies: `npm ci`
- Run tests: `npm test`
- Build docs: `npm run docs:build`