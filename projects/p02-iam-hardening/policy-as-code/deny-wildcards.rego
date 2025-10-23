package iam.deny_wildcards

default allow = false

allow {
  not contains_wildcard(input.policy)
}

contains_wildcard(policy) {
  some i
  policy.Statement[i].Action[j] == "*"
}

contains_wildcard(policy) {
  some i
  startswith(policy.Statement[i].Resource[k], "*")
}
