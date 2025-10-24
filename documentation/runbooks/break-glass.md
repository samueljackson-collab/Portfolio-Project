# Break-Glass Procedure

Use this procedure when privileged access is required outside standard workflows.

## Authorization

- Obtain approval from Engineering Director and Security Lead.
- Record approval in Jira ticket `BG-<date>`.

## Steps

1. Generate one-time credentials:
   ```bash
   aws iam create-service-specific-credential --service-name codecommit.amazonaws.com --user-name breakglass-user
   ```
2. Set access duration to 2 hours.
3. Log all actions in `documentation/security/break-glass-logs/`.
4. After task completion, disable credentials and document actions taken.

## Post-Use Review

- Conduct review within 24 hours.
- Update security findings backlog if long-term fixes are needed.
