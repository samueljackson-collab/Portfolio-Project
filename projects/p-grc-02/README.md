# Risk Register Automation

- **Role Category:** GRC
- **Status:** In Progress

## Executive Summary
Automating risk register updates with workflows for scoring, approvals, and reporting dashboards.

## Scenario & Scope
Enterprise risk program spanning product, infra, and vendor risks.

## Responsibilities
- Defined risk scoring model
- Built intake workflow
- Published reporting dashboards

## Tools & Technologies
- Power Automate
- Power BI
- SharePoint
- Python
- SQL

## Architecture Notes
Risk data stored in SQL backend with API; workflows enforce approvals; dashboards pull nightly snapshots.

## Process Walkthrough
- Design intake forms
- Implement scoring automation
- Notify owners for reviews
- Publish dashboards to leadership

## Outcomes & Metrics
- Reduced manual updates by 60%
- Improved visibility into high risks
- Automated reminders for reviews

## Evidence Links
- grc/p-grc-02/risk-automation.md

## Reproduction Steps
- Deploy the SQL schema
- Set up Power Automate flows
- Publish the Power BI dashboard

## Interview Points
- Designing usable risk workflows
- Choosing scoring models
- Reporting risk to leadership
