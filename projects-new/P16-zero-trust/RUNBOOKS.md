# Runbooks

- Denied flow: review Envoy access logs, run policy_eval.sh, update policy or identity mapping as needed
- SVID rotation failure: check SPIRE server health, trigger manual rotate with spire-agent api, redeploy affected pods
- OPA bundle fetch errors: verify registry auth, push fresh bundle, clear cache
