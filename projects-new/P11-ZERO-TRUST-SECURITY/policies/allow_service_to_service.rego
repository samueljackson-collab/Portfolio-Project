package authz

default allow = false

# Allow explicit caller->callee pairs
allow {
  input.source == "spiffe://example.org/ns/apps/sa/frontend"
  input.destination == "spiffe://example.org/ns/apps/sa/api"
}
allow {
  input.source == "spiffe://example.org/ns/apps/sa/api"
  input.destination == "spiffe://example.org/ns/apps/sa/payments"
}
allow {
  input.source == "spiffe://example.org/ns/apps/sa/api"
  input.destination == "spiffe://example.org/ns/apps/sa/admin"
  input.request_path == "/ops"
  input.claims.role == "admin"
}

# Deny by default with reason
violation[msg] {
  not allow
  msg := sprintf("caller %s not permitted to reach %s", [input.source, input.destination])
}
