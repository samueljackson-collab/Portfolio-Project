# Change Management Process – PRJ-HOME-001

## 1. Purpose
Ensure stability and accountability for modifications to the UniFi home network by defining classification, approval, execution, and documentation requirements.

## 2. Change Categories
| Type | Definition | Example |
| --- | --- | --- |
| Standard | Pre-approved, low-risk tasks with validated procedure | Monthly controller backup verification, SSID password rotation |
| Normal | Planned change requiring review & scheduled maintenance window | Firmware upgrades, VLAN additions, firewall policy updates |
| Emergency | Reactive change required to restore service | Hotfix for UDM-Pro bug causing WAN outage |

## 3. Request Workflow
1. Submit change request via `projects/06-homelab/PRJ-HOME-001/change-log.md` using template below.
2. Technical review by Network Engineer II (self-review or peer, depending on portfolio use case).
3. Stakeholder approval (homeowner/mentor) for Normal/Emergency changes.
4. Schedule implementation window (prefer Sat 22:00 – Sun 02:00 PT).
5. Execute change following documented procedure; capture before/after states.
6. Validate service health; update change log with results and attach evidence.

## 4. Change Request Template
```
Change ID: NET-HOME-YYYY-XXX
Title: <Concise description>
Requester: <Name>
Type: Standard | Normal | Emergency
Planned Date/Time: <YYYY-MM-DD HH:MM PT>
Components: <Devices, VLANs, services>
Description: <Detailed plan>
Risk Assessment: <Low/Med/High + justification>
Implementation Steps:
  1.
  2.
Validation Plan:
  -
Rollback Plan:
  1.
  2.
Attachments: <Diagrams, configs, approvals>
Approval:
  - Network Engineer:
  - Stakeholder:
Status: Proposed | Approved | Completed | Rolled Back
```

## 5. Roles & Responsibilities
- **Network Engineer II:** Owns request creation, execution, validation, and documentation.
- **Stakeholder/Homeowner:** Grants approval, validates non-functional requirements (e.g., coverage).
- **Mentor/Reviewer:** Provides peer review feedback, ensures adherence to standards.

## 6. Documentation & Auditing
- Maintain `change-log.md` with chronological entries, including links to git commits and monitoring graphs.
- Store supporting evidence (packet captures, screenshots) under `artifacts/changes/<ChangeID>/`.
- Quarterly audit ensures 100% of Normal/Emergency changes include validation and rollback notes.

## 7. Emergency Change Handling
- Execute change immediately to restore service.
- Notify stakeholder within 15 minutes; document reason for emergency classification.
- Complete post-change review within 24 hours to assess preventive actions.

## 8. Continuous Improvement
- Review failed or rolled-back changes during monthly operations meeting.
- Update standard operating procedures (SOPs) after each successful change to capture lessons learned.

