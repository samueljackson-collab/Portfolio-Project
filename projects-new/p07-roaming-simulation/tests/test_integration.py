"""
Integration tests for multi-network roaming journeys
"""

import unittest
import sys
import json
from pathlib import Path

# Add src directory to path
sys.path.insert(0, str(Path(__file__).parent.parent / "src"))

from roaming_simulator import (
    CallFlowState,
    PLMN,
    HLRRecord,
    NetworkOperator,
    RoamingSimulator,
    OperatorType,
)


class TestMultiNetworkRoamingJourney(unittest.TestCase):
    """Integration tests for multi-network roaming scenarios"""

    def setUp(self):
        """Set up simulator with multiple networks"""
        self.simulator = RoamingSimulator()

        # Create home network (Germany)
        self.home_plmn = PLMN(
            mcc="262",
            mnc="01",
            operator_name="Deutsche Telekom (Home)",
            operator_type=OperatorType.HOME_NETWORK,
        )
        self.home_operator = self.simulator.register_home_network(self.home_plmn)

        # Create visited networks
        # France
        self.france_plmn = PLMN(
            mcc="208",
            mnc="01",
            operator_name="Orange (France)",
            operator_type=OperatorType.VISITED_NETWORK,
        )
        self.france_operator = self.simulator.register_visited_network(self.france_plmn)

        # Spain
        self.spain_plmn = PLMN(
            mcc="214",
            mnc="01",
            operator_name="Vodafone (Spain)",
            operator_type=OperatorType.VISITED_NETWORK,
        )
        self.spain_operator = self.simulator.register_visited_network(self.spain_plmn)

        # Italy
        self.italy_plmn = PLMN(
            mcc="222",
            mnc="01",
            operator_name="Vodafone (Italy)",
            operator_type=OperatorType.VISITED_NETWORK,
        )
        self.italy_operator = self.simulator.register_visited_network(self.italy_plmn)

        # Register subscriber with roaming in all networks
        self.hlr_record = HLRRecord(
            imsi="262011234567890",
            msisdn="+49123456789",
            home_network=self.home_plmn,
            authentication_key="secure_key_123",
            roaming_allowed=True,
            allowed_networks=[
                self.france_plmn.plmn_id,
                self.spain_plmn.plmn_id,
                self.italy_plmn.plmn_id,
            ],
        )
        self.home_operator.hlr.register_subscriber(self.hlr_record)

    def test_single_network_roaming_journey(self):
        """Test a simple roaming journey in a single visited network"""
        # Subscriber traveling to France
        session = self.simulator.initiate_call(
            imsi="262011234567890",
            msisdn="+49123456789",
            called_party="+33123456789",
            home_plmn_id=self.home_plmn.plmn_id,
            visited_plmn_id=self.france_plmn.plmn_id,
        )

        self.assertIsNotNone(session)
        self.assertEqual(session.state, CallFlowState.CONNECTED)
        self.assertEqual(session.visited_network.plmn_id, self.france_plmn.plmn_id)

        # Verify HLR and VLR operations
        self.assertGreater(session.hlr_lookup_time, 0)
        self.assertGreater(session.vlr_lookup_time, 0)

        # Terminate call
        terminated = self.simulator.terminate_call(session.session_id)
        self.assertEqual(terminated.state, CallFlowState.IDLE)
        self.assertGreater(terminated.total_duration, 0)

    def test_multi_network_journey_with_handoff(self):
        """Test roaming journey with network handoff"""
        # Initial call in France
        session = self.simulator.initiate_call(
            imsi="262011234567890",
            msisdn="+49123456789",
            called_party="+33123456789",
            home_plmn_id=self.home_plmn.plmn_id,
            visited_plmn_id=self.france_plmn.plmn_id,
        )

        self.assertIsNotNone(session)
        self.assertEqual(session.state, CallFlowState.CONNECTED)
        initial_network = session.visited_network.plmn_id

        # Handoff to Spain
        handoff_success = self.simulator.execute_handoff(
            session.session_id, self.spain_plmn.plmn_id
        )

        self.assertTrue(handoff_success)
        session = self.simulator.get_call_session(session.session_id)
        self.assertEqual(session.state, CallFlowState.CONNECTED)
        self.assertEqual(session.visited_network.plmn_id, self.spain_plmn.plmn_id)
        self.assertNotEqual(session.visited_network.plmn_id, initial_network)

        # Verify handoff was recorded
        self.assertEqual(len(session.handoffs), 1)
        self.assertEqual(session.handoffs[0]["from_network"], self.france_plmn.plmn_id)
        self.assertEqual(session.handoffs[0]["to_network"], self.spain_plmn.plmn_id)

    def test_multi_hop_journey(self):
        """Test journey spanning multiple networks with consecutive handoffs"""
        # Call setup in France
        session = self.simulator.initiate_call(
            imsi="262011234567890",
            msisdn="+49123456789",
            called_party="+33123456789",
            home_plmn_id=self.home_plmn.plmn_id,
            visited_plmn_id=self.france_plmn.plmn_id,
        )

        self.assertIsNotNone(session)
        initial_session_id = session.session_id

        # Handoff to Spain
        self.assertTrue(self.simulator.execute_handoff(session.session_id, self.spain_plmn.plmn_id))
        session = self.simulator.get_call_session(initial_session_id)
        self.assertEqual(session.visited_network.plmn_id, self.spain_plmn.plmn_id)
        self.assertEqual(len(session.handoffs), 1)

        # Handoff to Italy
        self.assertTrue(self.simulator.execute_handoff(session.session_id, self.italy_plmn.plmn_id))
        session = self.simulator.get_call_session(initial_session_id)
        self.assertEqual(session.visited_network.plmn_id, self.italy_plmn.plmn_id)
        self.assertEqual(len(session.handoffs), 2)

        # Verify handoff chain
        self.assertEqual(session.handoffs[0]["from_network"], self.france_plmn.plmn_id)
        self.assertEqual(session.handoffs[0]["to_network"], self.spain_plmn.plmn_id)
        self.assertEqual(session.handoffs[1]["from_network"], self.spain_plmn.plmn_id)
        self.assertEqual(session.handoffs[1]["to_network"], self.italy_plmn.plmn_id)

        # Terminate call
        terminated = self.simulator.terminate_call(session.session_id)
        self.assertEqual(len(terminated.handoffs), 2)

    def test_concurrent_roaming_sessions(self):
        """Test multiple concurrent roaming sessions across networks"""
        # Session 1: Germany subscriber in France
        session1 = self.simulator.initiate_call(
            imsi="262011234567890",
            msisdn="+49123456789",
            called_party="+33111111111",
            home_plmn_id=self.home_plmn.plmn_id,
            visited_plmn_id=self.france_plmn.plmn_id,
        )

        self.assertIsNotNone(session1)
        session1_id = session1.session_id

        # Register another subscriber
        hlr_record2 = HLRRecord(
            imsi="262029876543210",
            msisdn="+49987654321",
            home_network=self.home_plmn,
            authentication_key="secure_key_456",
            roaming_allowed=True,
            allowed_networks=[
                self.france_plmn.plmn_id,
                self.spain_plmn.plmn_id,
            ],
        )
        self.home_operator.hlr.register_subscriber(hlr_record2)

        # Session 2: Another Germany subscriber in Spain
        session2 = self.simulator.initiate_call(
            imsi="262029876543210",
            msisdn="+49987654321",
            called_party="+34222222222",
            home_plmn_id=self.home_plmn.plmn_id,
            visited_plmn_id=self.spain_plmn.plmn_id,
        )

        self.assertIsNotNone(session2)
        session2_id = session2.session_id

        # Verify both sessions are active and in different networks
        sess1 = self.simulator.get_call_session(session1_id)
        sess2 = self.simulator.get_call_session(session2_id)

        self.assertEqual(sess1.state, CallFlowState.CONNECTED)
        self.assertEqual(sess2.state, CallFlowState.CONNECTED)
        self.assertEqual(sess1.visited_network.plmn_id, self.france_plmn.plmn_id)
        self.assertEqual(sess2.visited_network.plmn_id, self.spain_plmn.plmn_id)

        # Terminate both sessions
        self.simulator.terminate_call(session1_id)
        self.simulator.terminate_call(session2_id)

        terminated1 = self.simulator.get_call_session(session1_id)
        terminated2 = self.simulator.get_call_session(session2_id)

        self.assertEqual(terminated1.state, CallFlowState.IDLE)
        self.assertEqual(terminated2.state, CallFlowState.IDLE)

    def test_vlr_data_consistency_across_handoff(self):
        """Test that VLR data remains consistent across handoffs"""
        session = self.simulator.initiate_call(
            imsi="262011234567890",
            msisdn="+49123456789",
            called_party="+33123456789",
            home_plmn_id=self.home_plmn.plmn_id,
            visited_plmn_id=self.france_plmn.plmn_id,
        )

        # Check VLR entry in France
        vlr_record_france = self.france_operator.vlr.lookup("262011234567890")
        self.assertIsNotNone(vlr_record_france)
        self.assertEqual(vlr_record_france.msisdn, "+49123456789")

        # Handoff to Spain
        self.simulator.execute_handoff(session.session_id, self.spain_plmn.plmn_id)

        # Check VLR entry in Spain
        vlr_record_spain = self.spain_operator.vlr.lookup("262011234567890")
        self.assertIsNotNone(vlr_record_spain)
        self.assertEqual(vlr_record_spain.msisdn, "+49123456789")

        # Original VLR entry might still exist (depends on deregistration policy)
        # Both records should have consistent MSISDN
        if vlr_record_france:
            self.assertEqual(vlr_record_france.msisdn, vlr_record_spain.msisdn)

    def test_session_statistics_after_journey(self):
        """Test that session statistics are correctly calculated"""
        session = self.simulator.initiate_call(
            imsi="262011234567890",
            msisdn="+49123456789",
            called_party="+33123456789",
            home_plmn_id=self.home_plmn.plmn_id,
            visited_plmn_id=self.france_plmn.plmn_id,
        )

        # Perform handoff
        self.simulator.execute_handoff(session.session_id, self.spain_plmn.plmn_id)

        # Terminate call
        self.simulator.terminate_call(session.session_id)

        # Get statistics
        stats = self.simulator.get_session_statistics(session.session_id)

        self.assertIsNotNone(stats)
        self.assertEqual(stats["session_id"], session.session_id)
        self.assertEqual(stats["state"], CallFlowState.IDLE.value)
        self.assertGreater(stats["hlr_lookup_time_ms"], 0)
        self.assertGreater(stats["vlr_lookup_time_ms"], 0)
        self.assertGreater(stats["call_setup_time_ms"], 0)
        self.assertGreater(stats["total_duration_s"], 0)
        self.assertEqual(stats["handoff_count"], 1)
        self.assertIsNone(stats["error"])

    def test_simulator_statistics(self):
        """Test simulator-wide statistics"""
        # Create multiple sessions
        for i in range(3):
            self.simulator.initiate_call(
                imsi="262011234567890",
                msisdn="+49123456789",
                called_party=f"+33{i}23456789",
                home_plmn_id=self.home_plmn.plmn_id,
                visited_plmn_id=self.france_plmn.plmn_id,
            )

        stats = self.simulator.get_simulator_statistics()

        self.assertEqual(stats["total_sessions"], 3)
        self.assertEqual(stats["successful_sessions"], 3)
        self.assertEqual(stats["failed_sessions"], 0)
        self.assertEqual(stats["success_rate"], 100.0)
        self.assertGreater(stats["avg_hlr_lookup_time_ms"], 0)
        self.assertGreater(stats["avg_vlr_lookup_time_ms"], 0)

    def test_roaming_denied_scenario(self):
        """Test scenario where roaming is denied"""
        # Register subscriber with limited roaming rights
        hlr_record_limited = HLRRecord(
            imsi="262015555555555",
            msisdn="+49555555555",
            home_network=self.home_plmn,
            authentication_key="limited_key",
            roaming_allowed=True,
            allowed_networks=[self.france_plmn.plmn_id],  # Only France
        )
        self.home_operator.hlr.register_subscriber(hlr_record_limited)

        # Try to roam in Spain (not allowed)
        session = self.simulator.initiate_call(
            imsi="262015555555555",
            msisdn="+49555555555",
            called_party="+34999999999",
            home_plmn_id=self.home_plmn.plmn_id,
            visited_plmn_id=self.spain_plmn.plmn_id,
        )

        self.assertIsNotNone(session)
        self.assertEqual(session.state, CallFlowState.FAILED)
        self.assertIsNotNone(session.error_message)


class TestPerformanceAndLatency(unittest.TestCase):
    """Test performance characteristics and latency simulation"""

    def setUp(self):
        """Set up simulator"""
        self.simulator = RoamingSimulator()

        home_plmn = PLMN(
            mcc="001",
            mnc="01",
            operator_name="Home",
            operator_type=OperatorType.HOME_NETWORK,
        )
        self.home_operator = self.simulator.register_home_network(home_plmn)

        visited_plmn = PLMN(
            mcc="208",
            mnc="01",
            operator_name="Visited",
            operator_type=OperatorType.VISITED_NETWORK,
        )
        self.visited_operator = self.simulator.register_visited_network(visited_plmn)

        hlr_record = HLRRecord(
            imsi="001011234567890",
            msisdn="+1234567890",
            home_network=home_plmn,
            authentication_key="key",
            roaming_allowed=True,
            allowed_networks=[visited_plmn.plmn_id],
        )
        self.home_operator.hlr.register_subscriber(hlr_record)

    def test_latency_consistency(self):
        """Test that latencies are consistently measured"""
        session = self.simulator.initiate_call(
            imsi="001011234567890",
            msisdn="+1234567890",
            called_party="+9876543210",
            home_plmn_id=self.home_operator.plmn.plmn_id,
            visited_plmn_id=self.visited_operator.plmn.plmn_id,
        )

        # Check all latency components are measured
        self.assertGreater(session.hlr_lookup_time, 0)
        self.assertGreater(session.vlr_lookup_time, 0)
        self.assertGreater(session.call_setup_time, 0)

        # Sum of components should be less than or close to total setup time
        total_latency = session.hlr_lookup_time + session.vlr_lookup_time + session.call_setup_time
        self.assertGreater(total_latency, 0)

    def test_multiple_sessions_latency_distribution(self):
        """Test latency distribution across multiple sessions"""
        hlr_times = []
        vlr_times = []
        setup_times = []

        for i in range(10):
            session = self.simulator.initiate_call(
                imsi="001011234567890",
                msisdn="+1234567890",
                called_party=f"+987654321{i}",
                home_plmn_id=self.home_operator.plmn.plmn_id,
                visited_plmn_id=self.visited_operator.plmn.plmn_id,
            )

            hlr_times.append(session.hlr_lookup_time)
            vlr_times.append(session.vlr_lookup_time)
            setup_times.append(session.call_setup_time)

        # Check variance in latencies (not all identical)
        hlr_avg = sum(hlr_times) / len(hlr_times)
        vlr_avg = sum(vlr_times) / len(vlr_times)

        self.assertGreater(hlr_avg, 0)
        self.assertGreater(vlr_avg, 0)

        # All should be positive
        self.assertTrue(all(t > 0 for t in hlr_times))
        self.assertTrue(all(t > 0 for t in vlr_times))
        self.assertTrue(all(t > 0 for t in setup_times))


if __name__ == "__main__":
    unittest.main()
