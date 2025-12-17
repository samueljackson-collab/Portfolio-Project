"""
Roaming process diagrams and visualizations
"""

from enum import Enum
from typing import List


class DiagramType(Enum):
    """Types of available diagrams"""
    HLR_VLR_ARCHITECTURE = "hlr_vlr_architecture"
    CALL_FLOW = "call_flow"
    HANDOFF_FLOW = "handoff_flow"
    STATE_MACHINE = "state_machine"


def get_hlr_vlr_architecture_diagram() -> str:
    """
    Returns ASCII diagram of HLR/VLR architecture in roaming scenario
    """
    return """
╔════════════════════════════════════════════════════════════════════════════════╗
║                     INTERNATIONAL ROAMING ARCHITECTURE                         ║
╚════════════════════════════════════════════════════════════════════════════════╝

                         HOME NETWORK (Germany)                   VISITED NETWORK (France)
                         ═════════════════════                     ════════════════════

                      ┌──────────────────┐
                      │   HLR Database   │
                      │  (Subscriber     │
                      │   Information)   │
                      └────────┬─────────┘
                               │
                    Authentication Data
                    Roaming Profile
                    Service Permissions
                               │
              ┌────────────────┼────────────────┐
              │                │                │
         ┌────▼────┐      ┌────▼────┐    ┌──────▼──────┐
         │  MSC/VLR│      │  GMSC   │    │ VLR (France)│
         │(Germany)│      │(Germany)│    │  Database   │
         └────┬────┘      └────┬────┘    └──────┬──────┘
              │                │                │
              │      Lookup    │    Roaming     │
              │      Request   │    Data        │
              │                │                │
         ┌────▼─────────────────▼────┐   ┌──────▼──────┐
         │   Signaling Network (SS7) │   │   VLR Data  │
         │   (International Links)    │   │  • IMSI     │
         └────┬──────────────────────┘   │  • MSISDN   │
              │                          │  • Location │
              └──────────────────────────┤  • Services │
                                        └──────────────┘

DATA FLOW:
1. Mobile originates call in visited network
2. Visited network MSC/VLR queries HLR for subscriber info
3. HLR returns authentication data and service profile
4. VLR creates local copy of subscriber data
5. Call routing proceeds based on retrieved information

KEY COMPONENTS:
• HLR (Home Location Register): Authoritative subscriber database in home network
• VLR (Visitor Location Register): Temporary copy of roaming subscriber data
• MSC (Mobile Switching Center): Handles call routing and switching
• GMSC (Gateway MSC): International gateway for incoming calls
"""


def get_call_flow_diagram() -> str:
    """
    Returns ASCII diagram of call flow in roaming scenario
    """
    return """
╔════════════════════════════════════════════════════════════════════════════════╗
║                         ROAMING CALL FLOW DIAGRAM                              ║
╚════════════════════════════════════════════════════════════════════════════════╝

Mobile Subscriber    Visited MSC          HLR          GMSC         Called Party
        │                 │               │            │                │
        │ SETUP (Originate Call)          │            │                │
        ├────────────────────────────────>│            │                │
        │                                 │            │                │
        │     Lookup IMSI in VLR           │            │                │
        │     (Check if roaming)           │            │                │
        │     ◄──────────────────          │            │                │
        │                                 │            │                │
        │     VLR miss - Query HLR         │            │                │
        │     ├────────────────────────────┼───────────>│                │
        │     │   Auth Request              │            │                │
        │     │   Subscriber Info           │            │                │
        │     │<────────────────────────────┼────────────┤                │
        │                                 │            │                │
        │     Register VLR Data            │            │                │
        │     (Create Local Copy)          │            │                │
        │     ◄──────────────────          │            │                │
        │                                 │            │                │
        │ SEND ROUTING ADDRESS             │            │                │
        │<─────────────────────────────────┤            │                │
        │                                 │            │                │
        │ CALL CONNECTING                  │            │                │
        ├─────────────────────────────────────────────────┼───────────────┼──────>│
        │                                 │            │                │
        │                                 │ ALERT      │                │
        │<───────────────────────────────────────────────┼────────────────┤
        │                                 │            │                │
        │                                 │            │    RING        │
        │<───────────────────────────────────────────────────────────────┼──────┤
        │                                 │            │                │
        │ CALL CONNECTED (ALERTING)        │            │                │
        │                                 │            │    CONNECT     │
        │                                 │            │<───────────────┤
        │ ANSWER                          │            │                │
        │<───────────────────────────────────────────────────────────────┼──────┤
        │                                 │            │   CONNECT ACK  │
        │                                 │            │<───────────────┤
        │                                 │            │                │
        ├─────────────────────────────────────────────────────────────────────────>│
        │                    VOICE CHANNEL / DATA TRANSFER                       │
        │<─────────────────────────────────────────────────────────────────────────┤
        │                                 │            │                │
        │                                 │            │                │
        │ DISCONNECT (User hangs up)      │            │                │
        ├─────────────────────────────────────────────────┼────────────────────────>│
        │                                 │            │   DISCONNECT  │
        │                                 │            │<───────────────┤
        │                                 │            │                │
        │ RELEASE (Clear call)            │            │                │
        │<───────────────────────────────────────────────────────────────┼────────┤
        │                                 │            │                │
        │ Update VLR charges              │            │                │
        │ ◄──────────────────             │            │                │
        │                                 │            │                │

TIME COMPONENTS:
├─ HLR Lookup Latency:      10-50ms (average)
├─ VLR Registration:         15-60ms (average)
├─ Call Setup Time:          50-200ms (international)
└─ Total Setup Time:         100-300ms (typical)

STATES TRAVERSED:
1. LOCATION_REQUEST   → Query subscriber location
2. HLR_LOOKUP        → Get authentication and profile
3. VLR_REGISTRATION  → Register in visited network
4. CALL_SETUP        → Initiate call path
5. CONNECTED         → Call active
"""


def get_handoff_flow_diagram() -> str:
    """
    Returns ASCII diagram of network handoff during call
    """
    return """
╔════════════════════════════════════════════════════════════════════════════════╗
║                      NETWORK HANDOFF FLOW DIAGRAM                              ║
╚════════════════════════════════════════════════════════════════════════════════╝

Mobile Subscriber    France Network      Spain Network       HLR          HOME
        │                 │                    │             │            │
        │ CALL ACTIVE      │                    │             │            │
        ├─────────────────────────────────────────────────────────────────>│
        │                 │                    │             │            │
        │                 │ (Signal Quality Degrading)        │            │
        │                 │                    │             │            │
        │ HANDOFF NEEDED (Report Measurements)  │             │            │
        ├──────────────┬──┤                    │             │            │
        │              │  │                    │             │            │
        │              │  │ Measure Report     │             │            │
        │              │<─┤ (France degrading)│             │            │
        │              │  │ (Spain improving)  │             │            │
        │              │  │                    │             │            │
        │              │  │ HANDOFF_INITIATED  │             │            │
        │              │  │                    │             │            │
        │◄─────────────┤  ├───────────────────>│             │            │
        │ Send to both │  │ HANDOFF_CMD        │             │            │
        │ networks     │  │ (France: Release)  │             │            │
        │              │  │ (Spain: Establish)│             │            │
        │              │  │                    │             │            │
        │              │  │ HANDOFF_IN_PROGRESS│             │            │
        │              │  │                    │             │            │
        │              │  │                    │ VLR Sync    │            │
        │              │  │                    ├────────────>│            │
        │              │  │                    │ Register    │            │
        │              │  │                    │ Roamer      │            │
        │              │  │                    │ <──────────┤            │
        │              │  │                    │ Confirm    │            │
        │              │  │                    │             │            │
        │              │  │ Handoff Success    │             │            │
        │              │  │<───────────────────┤             │            │
        │              │  │                    │             │            │
        │◄─────────────┤  │ (Acknowledge to Spain)           │            │
        │ Continue on  │  │ Switch Handoff     │             │            │
        │ Spain Network│  │ (Cut France Link)  │             │            │
        │              │  ├───────────────────>│             │            │
        │              │  │                    │             │            │
        │              │  │ HANDOFF_COMPLETE   │             │            │
        │              │  │                    │             │            │
        │              │  │ Release Old VLR    │             │            │
        │              │  ├──> (May deregister)│             │            │
        │              │  │                    │             │            │
        │              │  │  Update Charges    │             │            │
        │              │  │  (Stop France CDR) │             │            │
        │              │  │  (Start Spain CDR) │             │            │
        │              │  │                    │             │            │
        │ CALL CONTINUES                       │             │            │
        ├──────────────────────────────────────┼─────────────────────────>│
        │                 │ (France Released) │             │            │
        │                 │                    │             │            │

HANDOFF STATE TRANSITIONS:
1. CONNECTED              → Subscriber moving between coverage areas
2. HANDOFF_INITIATED      → Measurement reports indicate move needed
3. HANDOFF_IN_PROGRESS    → Target network activated, old network released
4. HANDOFF_COMPLETE       → Resources freed in old network
5. CONNECTED (Spain)      → Call continues seamlessly

TIMING:
├─ VLR Lookup (Spain):        15-60ms
├─ Signaling (Handoff Cmd):   50-150ms
├─ Call Handoff Duration:     200-500ms (typical)
├─ Network Release (France):  100-200ms
└─ Total Handoff Time:        ~300-800ms

HANDOFF SCENARIOS:
• Same Operator, Different Region:  100-300ms (fast)
• Different Operators:               200-800ms (slower, more signaling)
• Cross-Border (Different Countries): 300-1000ms (variable)
"""


def get_state_machine_diagram() -> str:
    """
    Returns ASCII diagram of call state machine
    """
    return """
╔════════════════════════════════════════════════════════════════════════════════╗
║                    CALL STATE MACHINE DIAGRAM                                  ║
╚════════════════════════════════════════════════════════════════════════════════╝

                                    ┌──────────────────────┐
                                    │   Call Initiated     │
                                    └──────────┬───────────┘
                                               │
                                               ▼
                                    ┌──────────────────────┐
                                    │  LOCATION_REQUEST    │
                                    │ (Query mobile location)
                                    └──────────┬───────────┘
                                               │
                                               ▼
                                    ┌──────────────────────┐
                              ┌────>│   HLR_LOOKUP         │◄─────┐
                              │     │ (Get subscriber data)│       │
                              │     └──────────┬───────────┘       │
                              │                │                   │
                    Retry     │     Success    ▼                   │ Failed
                    (Limited) │    ┌──────────────────────┐        │ (Unknown Sub)
                              │    │ VLR_REGISTRATION     │        │
                              │    │ (Register in VLR)    │        │
                              │    └──────────┬───────────┘        │
                              │              │                     │
                              │              ▼                     │
                              │    ┌──────────────────────┐         │
                              │    │  CALL_SETUP          │         │
                              │    │ (Establish call path)│         │
                              │    └──────────┬───────────┘         │
                              │              │                     │
                              │              ▼                     │
                              │    ┌──────────────────────┐         │
                              │    │    CONNECTED         │         │
                              │    │ (Call is active)     │         │
                              │    └──────┬───┬──────────┘         │
                              │           │   │                   │
            ┌─────────────────┘           │   └──────────────┐    │
            │                             │                  │    │
            ▼                             ▼                  ▼    │
    ┌──────────────────────┐    ┌──────────────────────┐  ┌──────────────┐
    │ HANDOFF_INITIATED    │    │  CALL_TEARDOWN       │  │     FAILED   │
    │ (New network detected)     │ (User disconnected)  │  │(Roaming not  │◄────┘
    └──────────┬───────────┘    │                      │  │ allowed)     │
               │                 └──────────┬───────────┘  └──────────────┘
               ▼                            │
    ┌──────────────────────┐               │
    │HANDOFF_IN_PROGRESS   │               │
    │ (Switch to new net)  │               │
    └──────────┬───────────┘               │
               │                           │
               ▼                           │
    ┌──────────────────────┐               │
    │HANDOFF_COMPLETE      │               │
    │ (Old net released)   │               │
    └──────────┬───────────┘               │
               │                           │
               └──────────────┬────────────┘
                              │
                              ▼
                    ┌──────────────────────┐
                    │      IDLE            │
                    │ (Call terminated)    │
                    └──────────────────────┘

VALID STATE TRANSITIONS:
┌─ IDLE
├─> LOCATION_REQUEST
    ├─> HLR_LOOKUP
        ├─> VLR_REGISTRATION
            ├─> CALL_SETUP
                ├─> CONNECTED
                    ├─> HANDOFF_INITIATED
                    │   ├─> HANDOFF_IN_PROGRESS
                    │       ├─> HANDOFF_COMPLETE
                    │           └─> CONNECTED (continues)
                    └─> CALL_TEARDOWN
                        └─> IDLE
        └─> FAILED (roaming not allowed)
    └─> FAILED (subscriber not found)

ERROR STATES:
• FAILED: Terminal state for failed calls
  - Reasons: Subscriber not found, Roaming not permitted, Roaming suspended,
             Invalid IMSI, Service not available, Authentication failed
"""


def get_architecture_summary() -> str:
    """
    Returns a summary of the roaming architecture components
    """
    return """
╔════════════════════════════════════════════════════════════════════════════════╗
║              ROAMING ARCHITECTURE COMPONENT SUMMARY                             ║
╚════════════════════════════════════════════════════════════════════════════════╝

1. HOME NETWORK
   ├─ HLR (Home Location Register)
   │  └─ Authoritative subscriber database
   │  └─ Authentication information
   │  └─ Service subscription profile
   │  └─ Roaming permissions and limitations
   │  └─ Typical latency: 10-50ms
   │
   ├─ MSC/VLR (Mobile Switching Center / Visitor Location Register)
   │  └─ Routing subscriber calls
   │  └─ Incoming call handling from visited networks
   │  └─ Billing and CDR (Call Detail Records) generation
   │
   └─ GMSC (Gateway MSC)
      └─ International gateway for incoming calls
      └─ Routing to home subscribers roaming abroad

2. VISITED NETWORK
   ├─ VLR (Visitor Location Register)
   │  └─ Temporary copy of roaming subscriber data
   │  └─ Location tracking (LAC, Cell ID)
   │  └─ Call routing to roaming subscribers
   │  └─ Charge accumulation (CDRs)
   │  └─ Typical latency: 15-60ms
   │
   ├─ MSC (Mobile Switching Center)
   │  └─ Call setup and routing
   │  └─ Handoff management
   │  └─ Local subscriber management
   │
   └─ RANs (Radio Access Networks)
      └─ Cell coverage management
      └─ Handoff between cells

3. NETWORK INFRASTRUCTURE
   ├─ Signaling Network (SS7 / SIGTRAN)
   │  └─ Inter-network signaling for HLR/VLR queries
   │  └─ International links for roaming
   │  └─ Typical latency: 50-200ms for international links
   │
   ├─ Home Routing
   │  └─ Calls to roaming subscribers route through home network
   │
   └─ Data Network
      └─ CDR transmission for billing
      └─ Configuration and management data

HANDOFF TYPES:
├─ Intra-Network Handoff (Same Operator, Different Cell)
│  └─ Latency: 100-300ms
│  └─ Simple process, minimal signaling
│
├─ Inter-Network Handoff (Different Operators, Same Country)
│  └─ Latency: 200-500ms
│  └─ VLR interactions required
│
└─ Inter-Country Handoff (Different Operators, Different Countries)
   └─ Latency: 300-1000ms+
   └─ Complex signaling, potential policy changes
   └─ Currency/tariff changes may apply

ROAMING CHARGES:
├─ Originating Call: Charges applied by visited network, then reported to home
├─ Receiving Call: Charges vary by agreement (premium roaming, home rate, etc.)
├─ Data: Typically metered and reported as MBs used
└─ Billing: CDRs sent from visited network to home network
"""


def print_diagram(diagram_type: DiagramType) -> None:
    """
    Print a diagram to console

    Args:
        diagram_type: Type of diagram to print
    """
    if diagram_type == DiagramType.HLR_VLR_ARCHITECTURE:
        print(get_hlr_vlr_architecture_diagram())
    elif diagram_type == DiagramType.CALL_FLOW:
        print(get_call_flow_diagram())
    elif diagram_type == DiagramType.HANDOFF_FLOW:
        print(get_handoff_flow_diagram())
    elif diagram_type == DiagramType.STATE_MACHINE:
        print(get_state_machine_diagram())


def print_all_diagrams() -> None:
    """Print all available diagrams"""
    print("\n" + "=" * 88)
    print("INTERNATIONAL ROAMING SIMULATION - ARCHITECTURE AND DIAGRAMS")
    print("=" * 88 + "\n")

    print(get_architecture_summary())
    print("\n" + "=" * 88 + "\n")

    print(get_hlr_vlr_architecture_diagram())
    print("\n" + "=" * 88 + "\n")

    print(get_call_flow_diagram())
    print("\n" + "=" * 88 + "\n")

    print(get_handoff_flow_diagram())
    print("\n" + "=" * 88 + "\n")

    print(get_state_machine_diagram())
    print("\n" + "=" * 88 + "\n")


if __name__ == "__main__":
    print_all_diagrams()
