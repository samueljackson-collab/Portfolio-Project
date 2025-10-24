# Internal Automation Notes

The following cues guide tooling that generates or updates project assets. These notes remain private to prevent automated
systems from leaking into public-facing documentation.

- Follow repository coding standards defined in `CONTRIBUTING.md`.
- Generate code that is production-focused with tests and documentation.
- Prefer configuration-driven approaches and environment variables for secrets.
- Ensure all generated assets are idempotent so scripts can run repeatedly.
