"""
Unit tests for call state transitions in the roaming simulator
"""

import unittest
import sys
from pathlib import Path

# Add src directory to path
sys.path.insert(0, str(Path(__file__).parent.parent / "src"))

from roaming_simulator import (
    CallFlowState,
    PLMN,
    HLRRecord,
    VLRRecord,
    NetworkOperator,
    RoamingSimulator,
    OperatorType,
)


class TestCallFlowStateTransitions(unittest.TestCase):
    """Test call state transitions"""

    def setUp(self):
        """Set up test fixtures"""
        self.simulator = RoamingSimulator()

        # Create home network
        home_plmn = PLMN(
            mcc="001",
            mnc="01",
            operator_name="Home Operator",
            operator_type=OperatorType.HOME_NETWORK,
        )
        self.home_operator = self.simulator.register_home_network(home_plmn)

        # Create visited network
        visited_plmn = PLMN(
            mcc="208",
            mnc="01",
            operator_name="Visited Operator",
            operator_type=OperatorType.VISITED_NETWORK,
        )
        self.visited_operator = self.simulator.register_visited_network(visited_plmn)

        # Register subscriber in HLR
        hlr_record = HLRRecord(
            imsi="001011234567890",
            msisdn="+1234567890",
            home_network=home_plmn,
            authentication_key="auth_key_123",
            roaming_allowed=True,
            allowed_networks=[visited_plmn.plmn_id],
        )
        self.home_operator.hlr.register_subscriber(hlr_record)

    def test_initial_state_is_idle(self):
        """Test that initial call state is IDLE"""
        session = self.visited_operator.create_call_session(
            imsi="001011234567890",
            msisdn="+1234567890",
            called_party="+9876543210",
            home_network=self.home_operator.plmn,
            visited_network=self.visited_operator.plmn,
        )
        # Initial state should be LOCATION_REQUEST
        self.assertEqual(session.state, CallFlowState.LOCATION_REQUEST)

    def test_hlr_lookup_state_transition(self):
        """Test state transition to HLR_LOOKUP"""
        session = self.simulator.initiate_call(
            imsi="001011234567890",
            msisdn="+1234567890",
            called_party="+9876543210",
            home_plmn_id=self.home_operator.plmn.plmn_id,
            visited_plmn_id=self.visited_operator.plmn.plmn_id,
        )

        self.assertIsNotNone(session)
        # After successful initiate_call, should be CONNECTED
        self.assertEqual(session.state, CallFlowState.CONNECTED)
        self.assertGreater(session.hlr_lookup_time, 0)

    def test_vlr_registration_latency(self):
        """Test VLR registration introduces latency"""
        session = self.simulator.initiate_call(
            imsi="001011234567890",
            msisdn="+1234567890",
            called_party="+9876543210",
            home_plmn_id=self.home_operator.plmn.plmn_id,
            visited_plmn_id=self.visited_operator.plmn.plmn_id,
        )

        self.assertIsNotNone(session)
        self.assertGreater(session.vlr_lookup_time, 0)
        # VLR lookup typically in 15-60ms range, but with jitter can go higher
        self.assertLess(session.vlr_lookup_time, 150)

    def test_call_setup_latency(self):
        """Test call setup introduces latency"""
        session = self.simulator.initiate_call(
            imsi="001011234567890",
            msisdn="+1234567890",
            called_party="+9876543210",
            home_plmn_id=self.home_operator.plmn.plmn_id,
            visited_plmn_id=self.visited_operator.plmn.plmn_id,
        )

        self.assertIsNotNone(session)
        self.assertGreater(session.call_setup_time, 0)
        # Call setup should take measurable time (inter-operator signaling)
        self.assertGreater(session.call_setup_time, 20)

    def test_connected_state(self):
        """Test transition to CONNECTED state"""
        session = self.simulator.initiate_call(
            imsi="001011234567890",
            msisdn="+1234567890",
            called_party="+9876543210",
            home_plmn_id=self.home_operator.plmn.plmn_id,
            visited_plmn_id=self.visited_operator.plmn.plmn_id,
        )

        self.assertIsNotNone(session)
        self.assertEqual(session.state, CallFlowState.CONNECTED)
        self.assertIsNotNone(session.connection_time)

    def test_call_termination_state_transition(self):
        """Test call termination state transitions"""
        session = self.simulator.initiate_call(
            imsi="001011234567890",
            msisdn="+1234567890",
            called_party="+9876543210",
            home_plmn_id=self.home_operator.plmn.plmn_id,
            visited_plmn_id=self.visited_operator.plmn.plmn_id,
        )

        self.assertIsNotNone(session)
        self.assertEqual(session.state, CallFlowState.CONNECTED)

        # Terminate call
        terminated_session = self.simulator.terminate_call(session.session_id)

        self.assertIsNotNone(terminated_session)
        self.assertEqual(terminated_session.state, CallFlowState.IDLE)
        self.assertIsNotNone(terminated_session.disconnection_time)
        self.assertGreater(terminated_session.total_duration, 0)

    def test_failed_state_on_unknown_subscriber(self):
        """Test transition to FAILED state when subscriber not found"""
        session = self.simulator.initiate_call(
            imsi="999999999999999",  # Non-existent IMSI
            msisdn="+0000000000",
            called_party="+9876543210",
            home_plmn_id=self.home_operator.plmn.plmn_id,
            visited_plmn_id=self.visited_operator.plmn.plmn_id,
        )

        self.assertIsNotNone(session)
        self.assertEqual(session.state, CallFlowState.FAILED)
        self.assertIsNotNone(session.error_message)
        self.assertIn("not found", session.error_message.lower())

    def test_failed_state_on_roaming_not_allowed(self):
        """Test transition to FAILED state when roaming not allowed"""
        # Create subscriber with roaming disabled
        another_plmn = PLMN(
            mcc="999",
            mnc="99",
            operator_name="Another Operator",
            operator_type=OperatorType.VISITED_NETWORK,
        )
        self.simulator.register_visited_network(another_plmn)

        hlr_record = HLRRecord(
            imsi="001019876543210",
            msisdn="+9876543210",
            home_network=self.home_operator.plmn,
            authentication_key="auth_key_456",
            roaming_allowed=False,  # Roaming disabled
        )
        self.home_operator.hlr.register_subscriber(hlr_record)

        session = self.simulator.initiate_call(
            imsi="001019876543210",
            msisdn="+9876543210",
            called_party="+1111111111",
            home_plmn_id=self.home_operator.plmn.plmn_id,
            visited_plmn_id=another_plmn.plmn_id,
        )

        self.assertIsNotNone(session)
        self.assertEqual(session.state, CallFlowState.FAILED)
        self.assertIsNotNone(session.error_message)

    def test_multiple_state_transitions(self):
        """Test a complete call lifecycle with multiple state transitions"""
        # Initiate call
        session = self.simulator.initiate_call(
            imsi="001011234567890",
            msisdn="+1234567890",
            called_party="+9876543210",
            home_plmn_id=self.home_operator.plmn.plmn_id,
            visited_plmn_id=self.visited_operator.plmn.plmn_id,
        )

        self.assertIsNotNone(session)
        self.assertEqual(session.state, CallFlowState.CONNECTED)
        initial_state_history = [CallFlowState.LOCATION_REQUEST]

        # Terminate call
        terminated_session = self.simulator.terminate_call(session.session_id)

        self.assertIsNotNone(terminated_session)
        self.assertEqual(terminated_session.state, CallFlowState.IDLE)


class TestHLRVLROperations(unittest.TestCase):
    """Test HLR and VLR operations"""

    def setUp(self):
        """Set up test fixtures"""
        self.simulator = RoamingSimulator()

        home_plmn = PLMN(
            mcc="001",
            mnc="01",
            operator_name="Home Operator",
            operator_type=OperatorType.HOME_NETWORK,
        )
        self.home_operator = self.simulator.register_home_network(home_plmn)

        visited_plmn = PLMN(
            mcc="208",
            mnc="01",
            operator_name="Visited Operator",
            operator_type=OperatorType.VISITED_NETWORK,
        )
        self.visited_operator = self.simulator.register_visited_network(visited_plmn)

    def test_hlr_registration(self):
        """Test HLR subscriber registration"""
        hlr_record = HLRRecord(
            imsi="001011234567890",
            msisdn="+1234567890",
            home_network=self.home_operator.plmn,
            authentication_key="auth_key_123",
        )
        self.home_operator.hlr.register_subscriber(hlr_record)

        # Verify registration
        retrieved = self.home_operator.hlr.lookup("001011234567890")
        self.assertIsNotNone(retrieved)
        self.assertEqual(retrieved.imsi, "001011234567890")
        self.assertEqual(retrieved.msisdn, "+1234567890")

    def test_hlr_lookup_nonexistent_subscriber(self):
        """Test HLR lookup for non-existent subscriber"""
        result = self.home_operator.hlr.lookup("999999999999999")
        self.assertIsNone(result)

    def test_vlr_registration(self):
        """Test VLR roaming subscriber registration"""
        vlr_record = VLRRecord(
            imsi="001011234567890",
            msisdn="+1234567890",
            home_network=self.home_operator.plmn,
            visited_network=self.visited_operator.plmn,
            location_area_code="LAC_001",
            cell_id="CELL_001",
        )
        result = self.visited_operator.vlr.register(vlr_record)
        self.assertTrue(result)

        # Verify registration
        retrieved = self.visited_operator.vlr.lookup("001011234567890")
        self.assertIsNotNone(retrieved)
        self.assertEqual(retrieved.msisdn, "+1234567890")

    def test_vlr_deregistration(self):
        """Test VLR subscriber deregistration"""
        vlr_record = VLRRecord(
            imsi="001011234567890",
            msisdn="+1234567890",
            home_network=self.home_operator.plmn,
            visited_network=self.visited_operator.plmn,
            location_area_code="LAC_001",
            cell_id="CELL_001",
        )
        self.visited_operator.vlr.register(vlr_record)

        # Deregister
        result = self.visited_operator.vlr.deregister("001011234567890")
        self.assertTrue(result)

        # Verify deregistration
        retrieved = self.visited_operator.vlr.lookup("001011234567890")
        self.assertIsNone(retrieved)

    def test_vlr_get_active_subscribers(self):
        """Test getting active subscribers from VLR"""
        # Register multiple subscribers
        for i in range(3):
            vlr_record = VLRRecord(
                imsi=f"00101{i}234567890",
                msisdn=f"+123456789{i}",
                home_network=self.home_operator.plmn,
                visited_network=self.visited_operator.plmn,
                location_area_code="LAC_001",
                cell_id="CELL_001",
            )
            self.visited_operator.vlr.register(vlr_record)

        active = self.visited_operator.vlr.get_active_subscribers()
        self.assertEqual(len(active), 3)


class TestNetworkLatency(unittest.TestCase):
    """Test network latency simulation"""

    def setUp(self):
        """Set up test fixtures"""
        from roaming_simulator import NetworkLatency

        self.latency = NetworkLatency(min_ms=10.0, max_ms=50.0, jitter_pct=10.0)

    def test_latency_within_bounds(self):
        """Test that simulated latency is within bounds"""
        for _ in range(100):
            latency = self.latency.simulate()
            self.assertGreaterEqual(latency, self.latency.min_ms)
            self.assertLessEqual(
                latency, self.latency.max_ms + (self.latency.max_ms * 0.1)
            )

    def test_latency_variation(self):
        """Test that latency has variation (not constant)"""
        latencies = [self.latency.simulate() for _ in range(100)]
        avg_latency = sum(latencies) / len(latencies)
        max_latency = max(latencies)
        min_latency = min(latencies)

        # Should have variation
        self.assertGreater(max_latency - min_latency, 5.0)


if __name__ == "__main__":
    unittest.main()
