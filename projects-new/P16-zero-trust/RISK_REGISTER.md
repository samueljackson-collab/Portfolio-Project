# Risk Register

| Risk | Impact | Likelihood | Mitigation | Owner |
| --- | --- | --- | --- | --- |
| SPIRE server outage | High | Low | HA deployment and cached SVIDs | Platform |
| Policy drift across clusters | Medium | Medium | Versioned bundles with checksum validation | Security |
| mTLS cert expiration | High | Low | Auto-rotation and monitoring of cert TTL | Platform |
