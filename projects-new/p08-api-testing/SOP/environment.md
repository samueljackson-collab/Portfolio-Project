# SOP: Managing API Test Environments

- **Variables**: Store base URLs and secrets in Postman environments under `producer/env/*.postman_environment.json`.
- **Rotation**: Rotate tokens weekly; update secrets store and regenerate environment files.
- **Data Reset**: Use `jobs/reset_data.sh` to reseed mock data before performance runs.
- **Access**: Limit ability to edit environments to QA leads; review changes in PRs.
