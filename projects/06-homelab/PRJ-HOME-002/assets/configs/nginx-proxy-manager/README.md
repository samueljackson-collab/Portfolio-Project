# Nginx Proxy Manager (Sanitized)

Sanitized configuration for Nginx Proxy Manager (NPM) fronting core services. Replace placeholder hostnames/IPs with environment-specific values.

## Import Instructions
1. Login to NPM admin UI.
2. Navigate to **Hosts → Proxy Hosts → Add** and use the entries in `proxy-hosts.yml`.
3. Upload the internal CA certificate chain or LetsEncrypt wildcard for `example.com`.
4. Enable HTTP/2, Websockets, and HSTS on TLS-enabled hosts.

## TLS Notes
- All backends terminate TLS at NPM using certificates issued by FreeIPA or LetsEncrypt.
- Services running on internal VLAN 40 use private IPs; WAN exposure is disabled.

## Files
- `proxy-hosts.yml` — sanitized proxy host definitions with upstream mappings and access lists.
