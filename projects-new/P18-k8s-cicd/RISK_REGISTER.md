# Risk Register

| Risk | Impact | Likelihood | Mitigation | Owner |
| --- | --- | --- | --- | --- |
| Trivy scan failures block deploys | Medium | Medium | Allow severity gates with override process | Security |
| Kind cluster drift vs prod | Medium | Medium | Mirror prod kustomize overlays and run periodic parity checks | Platform |
| Action runner secrets leak | Critical | Low | OIDC + short-lived tokens | Security |
