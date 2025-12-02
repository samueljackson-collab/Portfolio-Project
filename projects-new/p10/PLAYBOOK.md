# Playbook
- Primary region is A; secondary is B.
- For planned failover: drain region A (`kubectl scale deploy/region-a --replicas=0`), verify B healthy, update status.
- For unplanned: trigger router failover script in RUNBOOKS/failover.md.
