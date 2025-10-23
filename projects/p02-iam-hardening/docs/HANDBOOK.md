# P02 · IAM Security Hardening — Strategy Handbook

This handbook outlines the blueprint for delivering zero-trust identity and access management across AWS workloads. It includes executive context, architecture patterns, policy design standards, automation strategies, and measurement frameworks.

## 1. Executive Summary
- Reduce privileged access by 60% through least-privilege permission sets and JIT elevation.  
- Automate access reviews and compliance evidence for SOC2/ISO 27001.  
- Integrate policy-as-code guardrails to prevent drift and enforce security baselines pre-deploy.  

## 2. Architecture Principles
1. **Separation of Duties** — Identity Center (SSO) manages human access; IAM roles manage workloads.  
2. **Conditional Access** — Enforce device posture, MFA, and context for privileged sessions.  
3. **Continuous Verification** — Automated checks for unused access, anomalous behavior, and policy sprawl.  

## 3. Account Structure
- **Management Account:** Hosts SCPs, identity services, and auditing.  
- **Shared Services:** Runs security tooling (Access Analyzer, Config, GuardDuty).  
- **Workload Accounts:** Application deployments with delegated admin roles.  

## 4. Policy-as-Code
- Store IAM JSON + SCP definitions in `iam/policies`.  
- Rego policies validate structure, actions, and resource scoping.  
- GitHub Actions pipeline runs `opa test`, `cfn-lint`, and `aws iam simulate-custom-policy`.  

## 5. Security Controls
- Mandatory session tags for identity, ticket numbers, and purpose.  
- Break-glass accounts gated with hardware MFA and auto-expiring credentials.  
- CloudTrail + Detective for detection; Security Hub aggregates findings.  

## 6. Metrics & KPIs
- **P0:** Privileged access minutes per engineer per week.  
- **P1:** Percentage of stale permissions (>90 days unused).  
- **P2:** Policy validation coverage in CI (target 100%).  

## 7. Roadmap
- Phase 1: Baseline inventory, policy library creation.  
- Phase 2: Automation & CI integration.  
- Phase 3: Reporting, dashboards, and tabletop exercises.  

