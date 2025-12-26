# P07 International Roaming Simulation

This pack provides production-grade documentation and runnable assets for simulating cross-carrier roaming events. It includes a comprehensive roaming simulator with HLR/VLR lookups, network handoffs, call flow state transitions, and network latency simulation.

## Overview

The P07 International Roaming Simulation project simulates realistic telecommunications roaming scenarios across multiple mobile network operators. It models the complex signaling flows, database operations, and network handoffs that occur when a subscriber uses a mobile network outside their home country.

### Key Components

- **HLR (Home Location Register)**: Authoritative subscriber database in the home network
- **VLR (Visitor Location Register)**: Temporary roaming subscriber data in visited networks
- **Call State Machine**: Realistic state transitions during roaming calls
- **Network Latency Simulation**: Realistic inter-operator signaling delays
- **Handoff Simulation**: Network handoffs between different operators
- **Multi-Network Journeys**: Track subscribers across multiple visited networks

## Scope

- High-fidelity HLR/VLR lookup simulation with realistic latencies
- Multi-operator roaming scenarios with handoff management
- Call flow state transitions and error handling
- Network latency and jitter injection
- Comprehensive test coverage (unit and integration tests)
- Architecture diagrams and documentation
- Producer/consumer pattern for event generation and processing
- K8s/Compose manifests for ephemeral labs
- Operational guides (playbooks, runbooks, SOPs) and risk/threat coverage

## Project Structure

```
projects-new/p07-roaming-simulation/
├── src/
│   ├── __init__.py                 # Package initialization
│   ├── roaming_simulator.py        # Main roaming simulation engine
│   └── diagrams.py                 # Architecture and flow diagrams
├── tests/
│   ├── __init__.py                 # Test package initialization
│   ├── test_state_transitions.py   # Unit tests for call states
│   └── test_integration.py         # Integration tests for multi-network journeys
├── producer/                        # Event generator
├── consumer/                        # Event processor
├── jobs/                           # Scheduled jobs
├── docker/                         # Docker Compose configuration
├── k8s/                            # Kubernetes manifests
├── ARCHITECTURE/                   # Architecture documentation
├── TESTING/                        # Test documentation
├── RUNBOOKS/                       # Operational runbooks
├── SOP/                            # Standard operating procedures
├── PLAYBOOK/                       # Incident playbooks
└── README.md                       # This file
```

## Installation

### Prerequisites
- Python 3.7+
- No external dependencies (uses standard library only)

### Setup

```bash
# Clone or navigate to the project
cd projects-new/p07-roaming-simulation

# Install in development mode (optional)
pip install -e .
```

## Usage

### 1. Basic Roaming Call Simulation

```python
from src.roaming_simulator import RoamingSimulator, PLMN, HLRRecord, OperatorType

# Initialize simulator
sim = RoamingSimulator()

# Register home network (Germany)
home_plmn = PLMN(
    mcc="262",
    mnc="01",
    operator_name="Deutsche Telekom (Home)",
    operator_type=OperatorType.HOME_NETWORK
)
home_op = sim.register_home_network(home_plmn)

# Register visited network (France)
visited_plmn = PLMN(
    mcc="208",
    mnc="01",
    operator_name="Orange (France)",
    operator_type=OperatorType.VISITED_NETWORK
)
visited_op = sim.register_visited_network(visited_plmn)

# Register subscriber in HLR
hlr_record = HLRRecord(
    imsi="262011234567890",
    msisdn="+49123456789",
    home_network=home_plmn,
    authentication_key="secure_key",
    roaming_allowed=True,
    allowed_networks=[visited_plmn.plmn_id]
)
home_op.hlr.register_subscriber(hlr_record)

# Initiate roaming call
session = sim.initiate_call(
    imsi="262011234567890",
    msisdn="+49123456789",
    called_party="+33123456789",
    home_plmn_id=home_plmn.plmn_id,
    visited_plmn_id=visited_plmn.plmn_id
)

print(f"Call connected: {session.state}")
print(f"HLR lookup time: {session.hlr_lookup_time:.2f}ms")
print(f"VLR registration time: {session.vlr_lookup_time:.2f}ms")
print(f"Call setup time: {session.call_setup_time:.2f}ms")

# Terminate call
terminated = sim.terminate_call(session.session_id)
print(f"Call duration: {terminated.total_duration:.2f}s")
```

### 2. Roaming with Network Handoff

```python
# ... (setup from above)

# Initiate call in France
session = sim.initiate_call(...)

# Execute handoff to Spain
session_id = session.session_id
spain_plmn = PLMN(mcc="214", mnc="01", operator_name="Vodafone (Spain)")
spain_op = sim.register_visited_network(spain_plmn)

handoff_success = sim.execute_handoff(session_id, spain_plmn.plmn_id)
if handoff_success:
    session = sim.get_call_session(session_id)
    print(f"Handoff successful, now in {session.visited_network.plmn_id}")
    print(f"Handoff duration: {session.handoffs[0]['duration_ms']:.2f}ms")

# Continue call in new network
sim.terminate_call(session_id)
```

### 3. Multi-Network Journey

```python
# Setup networks
networks = {}
plmns = [
    ("262", "01", "Germany"),
    ("208", "01", "France"),
    ("214", "01", "Spain"),
    ("222", "01", "Italy")
]

for mcc, mnc, name in plmns:
    if name == "Germany":
        plmn = PLMN(mcc=mcc, mnc=mnc, operator_name=name)
        networks[name] = sim.register_home_network(plmn)
    else:
        plmn = PLMN(mcc=mcc, mnc=mnc, operator_name=name)
        networks[name] = sim.register_visited_network(plmn)

# Register subscriber
hlr = HLRRecord(
    imsi="262011234567890",
    msisdn="+49123456789",
    home_network=networks["Germany"].plmn,
    authentication_key="key",
    roaming_allowed=True,
    allowed_networks=[
        networks["France"].plmn.plmn_id,
        networks["Spain"].plmn.plmn_id,
        networks["Italy"].plmn.plmn_id
    ]
)
networks["Germany"].hlr.register_subscriber(hlr)

# Journey across Europe
session = sim.initiate_call(
    imsi="262011234567890",
    msisdn="+49123456789",
    called_party="+33111111111",
    home_plmn_id=networks["Germany"].plmn.plmn_id,
    visited_plmn_id=networks["France"].plmn.plmn_id
)

# Handoff to Spain
sim.execute_handoff(session.session_id, networks["Spain"].plmn.plmn_id)

# Handoff to Italy
sim.execute_handoff(session.session_id, networks["Italy"].plmn.plmn_id)

# Get final statistics
stats = sim.get_session_statistics(session.session_id)
print(f"Journey completed: {len(stats['handoffs'])} handoffs")
for handoff in stats['handoffs']:
    print(f"  {handoff['from_network']} -> {handoff['to_network']}")
```

### 4. View Architecture Diagrams

```python
from src.diagrams import print_all_diagrams, DiagramType, print_diagram

# Print all diagrams
print_all_diagrams()

# Or print specific diagram
print_diagram(DiagramType.CALL_FLOW)
print_diagram(DiagramType.HANDOFF_FLOW)
print_diagram(DiagramType.STATE_MACHINE)
print_diagram(DiagramType.HLR_VLR_ARCHITECTURE)
```

### 5. Get Simulator Statistics

```python
# After running multiple sessions
stats = sim.get_simulator_statistics()

print(f"Total sessions: {stats['total_sessions']}")
print(f"Successful: {stats['successful_sessions']}")
print(f"Failed: {stats['failed_sessions']}")
print(f"Success rate: {stats['success_rate']:.1f}%")
print(f"Total handoffs: {stats['total_handoffs']}")
print(f"Avg HLR lookup: {stats['avg_hlr_lookup_time_ms']:.2f}ms")
print(f"Avg VLR lookup: {stats['avg_vlr_lookup_time_ms']:.2f}ms")
```

## Running Tests

### Unit Tests (State Transitions)

```bash
cd projects-new/p07-roaming-simulation
python -m pytest tests/test_state_transitions.py -v

# Or with unittest
python -m unittest tests.test_state_transitions -v
```

Test coverage includes:
- Initial call state transitions
- HLR/VLR lookup latency simulation
- Call setup and connection
- Call termination
- Failed call scenarios
- Roaming permission validation
- Network latency simulation

### Integration Tests (Multi-Network Journeys)

```bash
python -m pytest tests/test_integration.py -v

# Or with unittest
python -m unittest tests.test_integration -v
```

Test coverage includes:
- Single network roaming journey
- Multi-network handoff scenarios
- Multi-hop journeys (multiple consecutive handoffs)
- Concurrent roaming sessions
- VLR data consistency across handoffs
- Session statistics accuracy
- Simulator statistics aggregation
- Roaming denial scenarios
- Performance and latency characteristics

### Run All Tests

```bash
python -m pytest tests/ -v
```

## Call State Machine

The roaming simulator implements a realistic call state machine:

```
IDLE
  → LOCATION_REQUEST
    → HLR_LOOKUP
      → VLR_REGISTRATION
        → CALL_SETUP
          → CONNECTED
            ├─ HANDOFF_INITIATED
            │  ├─ HANDOFF_IN_PROGRESS
            │  └─ HANDOFF_COMPLETE → CONNECTED (continues)
            └─ CALL_TEARDOWN
              └─ IDLE
      → FAILED (roaming not allowed)
    → FAILED (subscriber not found)
```

## Latency Simulation

The simulator includes realistic latency for:

- **HLR Lookup**: 10-50ms (same country, home network)
- **VLR Lookup/Registration**: 15-60ms (visited network)
- **Call Setup**: 50-200ms (inter-operator international signaling)
- **Handoff Duration**: 200-500ms (intra-operator) to 300-1000ms+ (inter-operator/cross-border)
- **Network Jitter**: 10% variation to simulate real-world conditions

Latencies are configurable via `NetworkLatency` class:

```python
from src.roaming_simulator import NetworkLatency

# Custom latency profile
custom_latency = NetworkLatency(
    min_ms=30.0,
    max_ms=150.0,
    jitter_pct=15.0
)
```

## Data Structures

### PLMN (Public Land Mobile Network)
Represents a mobile network operator with MCC/MNC codes.

### HLRRecord
Subscriber information stored in home network:
- IMSI, MSISDN, Authentication key
- Roaming permissions and restrictions
- Service subscription profile

### VLRRecord
Temporary roaming subscriber data in visited network:
- Location information (LAC, Cell ID)
- Registration timestamp
- Activity tracking
- Charge accumulation

### CallSession
Represents an active or completed roaming call:
- Session ID, IMSI, MSISDN
- Call states and transitions
- Latency measurements
- Handoff history

## Performance Characteristics

- Typical call setup time: 100-300ms (HLR + VLR + Setup)
- Typical handoff duration: 300-800ms (multi-operator scenario)
- VLR lookup: <100ms (same network)
- HLR lookup: 10-50ms (cross-network)

## Advanced Configuration

### Custom Network Profiles

```python
# High-latency international profile
international_latency = NetworkLatency(
    min_ms=100.0,
    max_ms=300.0,
    jitter_pct=20.0
)

visited_plmn = PLMN(
    mcc="208",
    mnc="01",
    operator_name="Orange",
    latency=international_latency
)
```

### Roaming Restrictions

```python
# Subscriber with restricted roaming
hlr_record = HLRRecord(
    imsi="262011234567890",
    msisdn="+49123456789",
    home_network=home_plmn,
    roaming_allowed=True,
    allowed_networks=["208-01", "214-01"]  # Only France and Spain
)
```

## Integration with Event Pipeline

The simulator integrates with the existing producer/consumer pattern:

```bash
# Generate roaming events
python producer/main.py --profile urban --events 200

# Process events
python consumer/main.py --ingest-file out/events.jsonl
```

## Troubleshooting

### Common Issues

**Issue**: "Subscriber not found in HLR"
- **Cause**: IMSI not registered in HLR
- **Solution**: Use `home_operator.hlr.register_subscriber()` before call

**Issue**: "Roaming not allowed in this network"
- **Cause**: Visited network not in allowed_networks list
- **Solution**: Add visited network to HLRRecord.allowed_networks

**Issue**: Handoff fails
- **Cause**: Target network not registered in simulator
- **Solution**: Use `simulator.register_visited_network()` for all networks

## Files and Locations

| File | Location | Purpose |
|------|----------|---------|
| roaming_simulator.py | `/src/` | Main simulation engine |
| diagrams.py | `/src/` | Architecture diagrams |
| test_state_transitions.py | `/tests/` | Unit tests |
| test_integration.py | `/tests/` | Integration tests |
| main.py | `/producer/` | Event generator |
| main.py | `/consumer/` | Event processor |
| scheduler.py | `/jobs/` | Scheduled execution |

## Contributing

When extending the simulator:

1. Add new state transitions to `CallFlowState` enum
2. Implement state logic in `RoamingSimulator` class
3. Add unit tests for new states
4. Add integration tests for new scenarios
5. Update diagrams.py with any new flows
6. Document new features in this README

## References

For more information on roaming architecture:
- See `ARCHITECTURE/` directory for detailed traffic flows
- See `TESTING/` directory for test strategy and matrices
- See `RUNBOOKS/` directory for operational procedures
- See `SOP/` directory for standard operating procedures
- See `PLAYBOOK/` directory for incident response

## License

This project is part of the Portfolio-Project training suite.
