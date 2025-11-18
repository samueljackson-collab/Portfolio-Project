package authz
import data.authz

test_frontend_to_api_allowed {
  allow := authz.allow with input as {
    "source": "spiffe://example.org/ns/apps/sa/frontend",
    "destination": "spiffe://example.org/ns/apps/sa/api",
    "request_path": "/"
  }
  allow
}

test_payments_to_admin_denied {
  not authz.allow with input as {
    "source": "spiffe://example.org/ns/apps/sa/payments",
    "destination": "spiffe://example.org/ns/apps/sa/admin",
    "request_path": "/ops"
  }
}

test_admin_requires_role_claim {
  not authz.allow with input as {
    "source": "spiffe://example.org/ns/apps/sa/api",
    "destination": "spiffe://example.org/ns/apps/sa/admin",
    "request_path": "/ops",
    "claims": {"role": "guest"}
  }
}
