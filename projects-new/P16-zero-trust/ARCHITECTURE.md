# Architecture

Stack: OPA/Envoy, SPIRE for workload identities, WireGuard for node tunnels.

Data/Control flow: Nodes enroll via SPIRE, Envoy sidecars enforce OPA policies, and traffic allowed only with valid SVIDs and policy decisions.

Dependencies:
- Env/config: see README for required secrets and endpoints.
