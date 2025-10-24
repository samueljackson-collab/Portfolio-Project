package portfolio.security

# Guardrails for Kubernetes network policies included with the portfolio export.

default deny = []

deny[msg] {
  input.kind == "NetworkPolicy"
  not input.spec.podSelector
  name := input.metadata.name
  msg := sprintf("network policy %q must specify a podSelector", [name])
}

deny[msg] {
  input.kind == "NetworkPolicy"
  not policy_type_present("Ingress")
  name := input.metadata.name
  msg := sprintf("network policy %q must include Ingress in policyTypes", [name])
}

deny[msg] {
  input.kind == "NetworkPolicy"
  not policy_type_present("Egress")
  name := input.metadata.name
  msg := sprintf("network policy %q must include Egress in policyTypes", [name])
}

deny[msg] {
  input.kind == "NetworkPolicy"
  not egress_defined()
  name := input.metadata.name
  msg := sprintf("network policy %q must define at least one egress rule", [name])
}

policy_type_present(expected) {
  input.spec.policyTypes[_] == expected
}

egress_defined() {
  input.spec.egress[_]
}
