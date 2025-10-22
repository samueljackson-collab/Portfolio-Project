# WAF Tuning Runbook

## Objective

Maintain an optimal balance between security and availability by tuning AWS WAF rules for the Portfolio API.

## Baseline Rules

- AWSManagedRulesCommonRuleSet
- AWSManagedRulesKnownBadInputsRuleSet
- Custom rule: Block IP reputation score > 80

## Weekly Review Checklist

1. Export WAF logs to S3 and analyze with Athena query `queries/waf_false_positives.sql`.
2. Identify legitimate requests blocked by rules; create allow-list entries if necessary.
3. Update [`security/policies/network-policy.yaml`](../../security/policies/network-policy.yaml) if new service dependencies are added.
4. Document changes in `documentation/security/waf-changelog.md`.

## Emergency Actions

- Switch custom rules to count mode via AWS CLI.
- Notify incident commander in the active Slack incident channel.
- Capture evidence for post-incident analysis.
