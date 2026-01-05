#!/usr/bin/env python3
"""
P07 International Roaming Simulation - Demo Script

Demonstrates the roaming simulator with various scenarios:
1. Basic single-network roaming
2. Multi-network journey with handoffs
3. Statistics and reporting
"""

import sys
from pathlib import Path

# Add src directory to path
sys.path.insert(0, str(Path(__file__).parent / "src"))

from roaming_simulator import RoamingSimulator, PLMN, HLRRecord, OperatorType
from diagrams import print_diagram, DiagramType


def demo_basic_roaming():
    """Demo 1: Basic roaming call in a single visited network"""
    print("\n" + "=" * 80)
    print("DEMO 1: BASIC ROAMING CALL")
    print("=" * 80)

    # Create simulator
    sim = RoamingSimulator()

    # Register home network (Germany)
    home_plmn = PLMN(
        mcc="262",
        mnc="01",
        operator_name="Deutsche Telekom (Home)",
        operator_type=OperatorType.HOME_NETWORK,
    )
    home_op = sim.register_home_network(home_plmn)

    # Register visited network (France)
    visited_plmn = PLMN(
        mcc="208",
        mnc="01",
        operator_name="Orange (France)",
        operator_type=OperatorType.VISITED_NETWORK,
    )
    visited_op = sim.register_visited_network(visited_plmn)

    # Register subscriber
    hlr_record = HLRRecord(
        imsi="262011234567890",
        msisdn="+49123456789",
        home_network=home_plmn,
        authentication_key="secure_key_123",
        roaming_allowed=True,
        allowed_networks=[visited_plmn.plmn_id],
    )
    home_op.hlr.register_subscriber(hlr_record)

    # Initiate call
    print("\nInitiating call from roaming subscriber in France...")
    session = sim.initiate_call(
        imsi="262011234567890",
        msisdn="+49123456789",
        called_party="+33123456789",
        home_plmn_id=home_plmn.plmn_id,
        visited_plmn_id=visited_plmn.plmn_id,
    )

    if session:
        print(f"\nCall Status: {session.state.value}")
        print(f"  Session ID: {session.session_id}")
        print(f"  IMSI: {session.imsi}")
        print(f"  Called Party: {session.called_party}")
        print(f"\nLatency Measurements:")
        print(f"  HLR Lookup: {session.hlr_lookup_time:.2f}ms")
        print(f"  VLR Registration: {session.vlr_lookup_time:.2f}ms")
        print(f"  Call Setup: {session.call_setup_time:.2f}ms")
        print(
            f"  Total Setup: {session.hlr_lookup_time + session.vlr_lookup_time + session.call_setup_time:.2f}ms"
        )

        # Terminate call
        terminated = sim.terminate_call(session.session_id)
        print(f"\nCall Duration: {terminated.total_duration:.2f}s")
        print("Call terminated successfully.")


def demo_multi_network_handoff():
    """Demo 2: Multi-network journey with handoffs"""
    print("\n" + "=" * 80)
    print("DEMO 2: MULTI-NETWORK JOURNEY WITH HANDOFFS")
    print("=" * 80)

    # Create simulator
    sim = RoamingSimulator()

    # Setup networks
    networks = {}
    network_specs = [
        ("262", "01", "Germany", True),  # Home network
        ("208", "01", "France", False),
        ("214", "01", "Spain", False),
        ("222", "01", "Italy", False),
    ]

    for mcc, mnc, name, is_home in network_specs:
        plmn = PLMN(mcc=mcc, mnc=mnc, operator_name=name)
        if is_home:
            networks[name] = sim.register_home_network(plmn)
        else:
            networks[name] = sim.register_visited_network(plmn)

    # Register subscriber with roaming rights in all networks
    hlr_record = HLRRecord(
        imsi="262011111111111",
        msisdn="+49111111111",
        home_network=networks["Germany"].plmn,
        authentication_key="key_123",
        roaming_allowed=True,
        allowed_networks=[
            networks["France"].plmn.plmn_id,
            networks["Spain"].plmn.plmn_id,
            networks["Italy"].plmn.plmn_id,
        ],
    )
    networks["Germany"].hlr.register_subscriber(hlr_record)

    # Start call in France
    print("\nStarting call in France...")
    session = sim.initiate_call(
        imsi="262011111111111",
        msisdn="+49111111111",
        called_party="+33111111111",
        home_plmn_id=networks["Germany"].plmn.plmn_id,
        visited_plmn_id=networks["France"].plmn.plmn_id,
    )

    print(f"Call connected in: {session.visited_network.plmn_id} (France)")

    # Handoff to Spain
    print("\nHandoff to Spain...")
    sim.execute_handoff(session.session_id, networks["Spain"].plmn.plmn_id)
    session = sim.get_call_session(session.session_id)
    print(f"Call now in: {session.visited_network.plmn_id} (Spain)")
    print(f"Handoff duration: {session.handoffs[0]['duration_ms']:.2f}ms")

    # Handoff to Italy
    print("\nHandoff to Italy...")
    sim.execute_handoff(session.session_id, networks["Italy"].plmn.plmn_id)
    session = sim.get_call_session(session.session_id)
    print(f"Call now in: {session.visited_network.plmn_id} (Italy)")
    print(f"Handoff duration: {session.handoffs[1]['duration_ms']:.2f}ms")

    # Get statistics
    print("\nCall Statistics:")
    stats = sim.get_session_statistics(session.session_id)
    print(f"  Total Handoffs: {stats['handoff_count']}")
    print(f"  Journey: France -> Spain -> Italy")
    for i, handoff in enumerate(stats["handoffs"], 1):
        print(
            f"  Handoff {i}: {handoff['from_network']} -> {handoff['to_network']} ({handoff['duration_ms']:.2f}ms)"
        )

    # Terminate call
    sim.terminate_call(session.session_id)
    print("\nCall terminated. Journey complete!")


def demo_simulator_statistics():
    """Demo 3: Simulator statistics and reporting"""
    print("\n" + "=" * 80)
    print("DEMO 3: SIMULATOR STATISTICS AND REPORTING")
    print("=" * 80)

    # Create simulator
    sim = RoamingSimulator()

    # Setup basic networks
    home_plmn = PLMN(mcc="262", mnc="01", operator_name="Deutsche Telekom")
    home_op = sim.register_home_network(home_plmn)

    visited_plmn = PLMN(mcc="208", mnc="01", operator_name="Orange")
    visited_op = sim.register_visited_network(visited_plmn)

    # Register multiple subscribers
    for i in range(3):
        hlr = HLRRecord(
            imsi=f"26201{i}111111111",
            msisdn=f"+49{i}11111111",
            home_network=home_plmn,
            authentication_key=f"key_{i}",
            roaming_allowed=True,
            allowed_networks=[visited_plmn.plmn_id],
        )
        home_op.hlr.register_subscriber(hlr)

    # Create multiple sessions
    print("\nCreating multiple roaming sessions...")
    for i in range(3):
        session = sim.initiate_call(
            imsi=f"26201{i}111111111",
            msisdn=f"+49{i}11111111",
            called_party=f"+33{i}11111111",
            home_plmn_id=home_plmn.plmn_id,
            visited_plmn_id=visited_plmn.plmn_id,
        )
        print(f"  Session {i+1}: {session.session_id} - {session.state.value}")

    # Get simulator statistics
    print("\nSimulator Statistics:")
    stats = sim.get_simulator_statistics()
    print(f"  Total Sessions: {stats['total_sessions']}")
    print(f"  Successful Sessions: {stats['successful_sessions']}")
    print(f"  Failed Sessions: {stats['failed_sessions']}")
    print(f"  Success Rate: {stats['success_rate']:.1f}%")
    print(f"  Average HLR Lookup: {stats['avg_hlr_lookup_time_ms']:.2f}ms")
    print(f"  Average VLR Lookup: {stats['avg_vlr_lookup_time_ms']:.2f}ms")
    print(f"  Total Handoffs: {stats['total_handoffs']}")


def demo_architecture_diagrams():
    """Demo 4: Show architecture diagrams"""
    print("\n" + "=" * 80)
    print("DEMO 4: ARCHITECTURE DIAGRAMS")
    print("=" * 80)

    print("\nShowing Call Flow Diagram...")
    print_diagram(DiagramType.CALL_FLOW)


def main():
    """Run all demos"""
    print("\n" + "=" * 80)
    print("P07 INTERNATIONAL ROAMING SIMULATION - DEMO")
    print("=" * 80)

    try:
        demo_basic_roaming()
        demo_multi_network_handoff()
        demo_simulator_statistics()
        # demo_architecture_diagrams()  # Commented out to avoid too much output

        print("\n" + "=" * 80)
        print("ALL DEMOS COMPLETED SUCCESSFULLY")
        print("=" * 80)
        print("\nFor more information:")
        print("  - See README.md for detailed usage instructions")
        print("  - Run 'python src/diagrams.py' to see all architecture diagrams")
        print("  - Run 'python -m unittest tests/ -v' to run all tests")
        print("=" * 80 + "\n")

    except Exception as e:
        print(f"\nError during demo: {e}")
        import traceback

        traceback.print_exc()
        return 1

    return 0


if __name__ == "__main__":
    sys.exit(main())
