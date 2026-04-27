# Comprehensive AI Code Generation Prompts for Portfolio Completion

This quick start guide shows how to run the enhanced portfolio status analysis script and reuse the same prompt-driven approach for future automation. The script cross-references your Master Portfolio Index against GitHub repositories to surface gaps, stale activity, and ownership issues.

## What the script does
- Loads a Master Portfolio Index in JSON, CSV, or Markdown table format.
- Queries GitHub for repository metadata (existence, archived state, last push, default branch).
- Flags stale repositories with no pushes in 90+ days and highlights missing repos.
- Exports a Markdown or JSON report that can be dropped into status decks or opened by downstream automation.

## Prerequisites
- Python 3.9+ with network access to api.github.com.
- A GitHub Personal Access Token stored in an environment variable (default: `GITHUB_TOKEN`).
- Master Portfolio Index file with at least `id`, `name`, `repo`, and `status` columns (CSV/JSON) or table headers (Markdown).

## Quick start
1. **Make sure the script is executable**
   ```bash
   chmod +x scripts/portfolio_status_analysis.py
   ```
2. **Run the analysis**
   ```bash
   ./scripts/portfolio_status_analysis.py Portfolio_Master_Index_COMPLETE.md \
     --owner your-org-name \
     --token-env GITHUB_TOKEN \
     --format markdown \
     --output reports/portfolio-status.md
   ```
3. **Review the report**
   - Markdown output provides a human-readable table with emoji indicators for missing or stale repositories.
   - JSON output can be fed into dashboards or scheduled quality gates.

## Output formats
- **Markdown (default):** Friendly for sharing in docs and wikis. Includes repository age and stale flags.
- **JSON:** Structured data for pipelines; includes identifiers, status, owner, and error details when lookups fail.

## Tips for reliable results
- Set `--owner` to your default GitHub organization; individual entries can override by specifying an `owner` column.
- Keep the Master Portfolio Index normalized—use consistent repo names and statuses to reduce false positives.
- Rotate tokens regularly and scope them to repo read-only permissions for safety.

## Extending the prompts and automation
Use these prompts to ask your AI code generator to add features (sorting, CSV exports, Slack alerts) while keeping the repo aligned:

1. **Add automated freshness gates**
   - Prompt: "Add a flag that fails CI when any portfolio repository has not been pushed to in 60 days."
2. **Integrate issue hygiene checks**
   - Prompt: "Fetch open issues per repository and include a warning when more than 25 issues are older than 90 days."
3. **Expand input formats**
   - Prompt: "Support TSV and Excel Master Portfolio Index inputs while preserving existing JSON/CSV/Markdown behavior."

## Troubleshooting
- `Repository not found`: Confirm repo names in the index match GitHub exactly and that the token has access.
- `HTTP error`: Check rate limits (`X-RateLimit-Remaining` headers) or network connectivity.
- `No Markdown table rows detected`: Ensure Markdown indexes start each row with `|` characters and include a header row.

## Next steps
- Schedule the script via CI to run nightly and publish the Markdown report to your documentation site.
- Pair the report with the `scripts/portfolio-metrics.py` output to monitor both coverage and quality signals.
- Add alerting that pings owners for stale or missing repositories.
