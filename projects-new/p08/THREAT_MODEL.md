# Threat Model
- Input fuzzing could bypass validators: mitigated with schema-first validation and deny-by-default.
- Secrets leakage from logs: scrub headers and bodies before logging.
- CI supply chain risk: pin dependencies and use trusted base images.
