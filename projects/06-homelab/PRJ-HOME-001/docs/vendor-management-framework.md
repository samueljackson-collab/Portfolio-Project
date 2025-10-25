# Vendor Management Framework
**Scope:** UniFi ecosystem and supporting service providers for PRJ-HOME-001

---

## 1. Vendor Inventory
| Vendor | Role | Products/Services | Support Channel | SLA |
| --- | --- | --- | --- | --- |
| Ubiquiti | Network infrastructure | UDM-Pro, Switch Pro 24 PoE, APs, Protect | Community forums, email ticket | Response < 24h |
| ISP (Comcast Fiber) | Internet connectivity | 1 Gbps fiber circuit | Phone support, business portal | 4h repair |
| Backblaze B2 | Cloud storage | Off-site configuration backups | Web console, ticketing | 24h |
| Monoprice | Cabling hardware | CAT6A bulk cable, patch cords | Email support | 48h |

## 2. Evaluation Criteria
- **Technical Support Quality:** Response time, knowledge base richness, RMA process.
- **Cost & Licensing:** Hardware pricing, recurring subscription fees, renewal terms.
- **Roadmap Alignment:** Wi-Fi 6E/7 availability, Protect feature updates, compatibility with automation stack.
- **Security Posture:** Firmware release cadence, CVE responsiveness, MFA support for portals.

## 3. Performance Scorecard (Q2 2024)
| Vendor | Support | Responsiveness | Reliability | Overall | Notes |
| --- | --- | --- | --- | --- | --- |
| Ubiquiti | 4/5 | 3/5 | 5/5 | 4.0 | Good hardware reliability; support slower for edge cases |
| ISP | 5/5 | 4/5 | 4/5 | 4.3 | One outage resolved in 3h; proactive notifications |
| Backblaze | 4/5 | 4/5 | 5/5 | 4.3 | API integration seamless |
| Monoprice | 3/5 | 3/5 | 5/5 | 3.7 | Supply delays during peak demand |

## 4. Procurement Workflow
1. Define requirement and business justification (e.g., additional AP for guest house).
2. Evaluate vendors against scorecard; gather quotes.
3. Obtain stakeholder approval for purchases > $500.
4. Place order; capture order confirmation in procurement log.
5. Upon receipt, inspect equipment, record serial numbers, and update asset inventory.

## 5. Contract & Warranty Tracking
- Maintain spreadsheet `docs/procurement/vendor-tracker.xlsx` with purchase dates, warranty expiration, support contacts.
- Set calendar reminders 60 days prior to warranty lapse for key devices (UDM-Pro, switch).
- Record RMA cases with ticket number, resolution, and duration.

## 6. Continuous Improvement
- Semi-annual vendor review; adjust preferred supplier list based on scorecard trends.
- Engage in beta programs (e.g., UniFi Early Access) only after risk assessment and lab validation.
- Document lessons learned from any vendor escalations in change log.

