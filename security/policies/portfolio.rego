package portfolio.networkpolicy

default allow = true

deny[msg] {
  input.kind == "NetworkPolicy"
  ns := input.metadata.namespace
  name := input.metadata.name
  not has_ingress_rules(input)
  msg := sprintf("%s/%s must define at least one ingress rule", [ns, name])
}

deny[msg] {
  input.kind == "NetworkPolicy"
  ns := input.metadata.namespace
  name := input.metadata.name
  declares_egress(input)
  not has_egress_rules(input)
  msg := sprintf("%s/%s declares egress policyTypes but has no egress rules", [ns, name])
}

has_ingress_rules(obj) {
  count(obj.spec.ingress) > 0
}

has_egress_rules(obj) {
  count(obj.spec.egress) > 0
}

declares_egress(obj) {
  some i
  obj.spec.policyTypes[i] == "Egress"
}
