#!/usr/bin/env python3
"""
Roaming simulation orchestrator.

Runs end-to-end roaming scenarios.
"""
import argparse
import logging
from state_machine import RoamingStateMachine, SubscriberState
from hlr_mock import MockHLR

logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)


def setup_test_environment() -> MockHLR:
    """Setup test HLR with sample data."""
    hlr = MockHLR()

    # Add test subscribers
    hlr.add_subscriber(
        imsi="310410123456789",
        msisdn="+15551234567",
        home_network="310-410",  # AT&T USA
        ki="0123456789ABCDEF0123456789ABCDEF"
    )

    hlr.add_subscriber(
        imsi="208011987654321",
        msisdn="+33612345678",
        home_network="208-01",  # Orange France
        ki="FEDCBA9876543210FEDCBA9876543210"
    )

    # Configure roaming agreements
    hlr.add_roaming_agreement("310-410", ["208-01", "234-15", "262-01"])  # AT&T roaming
    hlr.add_roaming_agreement("208-01", ["310-410", "234-15", "262-01"])  # Orange roaming

    return hlr


def run_international_roaming_scenario(hlr: MockHLR):
    """Simulate successful international roaming."""
    logger.info("=== Scenario: International Roaming (Success) ===")

    imsi = "310410123456789"
    home_network = "310-410"  # AT&T USA
    visited_network = "208-01"  # Orange France

    # Initialize state machine
    sm = RoamingStateMachine(imsi)

    # Step 1: Initiate roaming
    assert sm.initiate_roaming(home_network, visited_network), "Failed to initiate roaming"

    # Step 2: Authenticate with HLR
    auth_success = hlr.authenticate(imsi, visited_network)
    assert sm.authenticate(auth_success), "Authentication failed"

    # Step 3: Activate roaming
    assert sm.activate_roaming(), "Failed to activate roaming"
    assert sm.is_roaming(), "Subscriber should be in roaming state"

    # Step 4: Detach (end of roaming)
    assert sm.detach(), "Failed to detach"

    logger.info("✓ International roaming scenario completed successfully")


def run_failed_auth_scenario(hlr: MockHLR):
    """Simulate failed authentication."""
    logger.info("=== Scenario: Failed Authentication ===")

    imsi = "999999999999999"  # Invalid IMSI
    home_network = "310-410"
    visited_network = "208-01"

    sm = RoamingStateMachine(imsi)
    sm.initiate_roaming(home_network, visited_network)

    # Attempt authentication with invalid IMSI
    auth_success = hlr.authenticate(imsi, visited_network)
    assert not auth_success, "Authentication should fail for invalid IMSI"

    sm.authenticate(False)
    assert sm.get_state() != SubscriberState.ATTACHED, "Should not be attached"

    logger.info("✓ Failed authentication scenario completed")


def run_no_roaming_agreement_scenario(hlr: MockHLR):
    """Simulate roaming attempt without agreement."""
    logger.info("=== Scenario: No Roaming Agreement ===")

    imsi = "310410123456789"
    home_network = "310-410"
    visited_network = "404-45"  # Airtel India (no agreement)

    sm = RoamingStateMachine(imsi)
    sm.initiate_roaming(home_network, visited_network)

    # Check roaming agreement
    has_agreement = hlr.check_roaming_agreement(imsi, visited_network)
    assert not has_agreement, "Should not have roaming agreement"

    auth_success = hlr.authenticate(imsi, visited_network)
    assert not auth_success, "Authentication should fail without roaming agreement"

    logger.info("✓ No roaming agreement scenario completed")


def main():
    """Main simulation entry point."""
    parser = argparse.ArgumentParser(description='Roaming simulation')
    parser.add_argument(
        '--scenario',
        choices=['international_roaming', 'failed_auth', 'no_roaming_agreement', 'all'],
        default='all',
        help='Scenario to run'
    )
    args = parser.parse_args()

    hlr = setup_test_environment()

    scenarios = {
        'international_roaming': run_international_roaming_scenario,
        'failed_auth': run_failed_auth_scenario,
        'no_roaming_agreement': run_no_roaming_agreement_scenario,
    }

    if args.scenario == 'all':
        for scenario_func in scenarios.values():
            scenario_func(hlr)
            logger.info("")
    else:
        scenarios[args.scenario](hlr)

    logger.info("✓ All scenarios completed successfully")


if __name__ == "__main__":
    main()
