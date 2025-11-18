# Adversary Emulation for OT Lab

- **Role Category:** Red Team
- **Status:** In Progress

## Executive Summary
Built an emulation plan for ICS/SCADA environments using MITRE ATT&CK for ICS to validate segmentation controls.

## Scenario & Scope
Targeted a lab with Modbus/TCP devices behind a jump host and engineering workstation.

## Responsibilities
- Mapped ATT&CK for ICS techniques to lab assets
- Authored safe payloads to avoid process disruption
- Ran purple-team tabletop with SOC and OT engineers

## Tools & Technologies
- Caldera
- Atomic Red Team
- Wireshark
- GNS3
- ModbusPal

## Architecture Notes
Segmentation enforced via dual-firewall zones; testing executed from a hardened Ubuntu jump box with strict egress rules.

## Process Walkthrough
- Cataloged OT assets and network flows
- Selected low-impact techniques for the lab
- Executed emulation steps with real-time monitoring
- Captured packet traces and log artifacts for SOC tuning

## Outcomes & Metrics
- Documented 12 new OT detections
- Validated firewall ACLs for engineering subnets
- Provided evidence pack for compliance reviewers

## Evidence Links
- reports/p-rt-02/ot-emulation.pdf

## Reproduction Steps
- Start the OT lab VMs using the provided compose file
- Launch Caldera with the ICS plugin
- Replay the scripted ATT&CK sequences and capture logs

## Interview Points
- Balancing realism and safety in OT testing
- Mapping ATT&CK for ICS to detection engineering
- Coordinating with operations teams during emulation
