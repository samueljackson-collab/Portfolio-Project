"""Unit tests for roaming state machine."""
import pytest

from state_machine import RoamingStateMachine, SubscriberState


class TestRoamingStateMachine:
    """Test suite for roaming state machine."""

    def test_initial_state(self):
        """Verify initial state is IDLE."""
        sm = RoamingStateMachine("123456789012345")
        assert sm.get_state() == SubscriberState.IDLE

    def test_initiate_roaming(self):
        """Test roaming initiation."""
        sm = RoamingStateMachine("123456789012345")
        success = sm.initiate_roaming("310-410", "208-01")
        assert success is True
        assert sm.get_state() == SubscriberState.LOCATION_UPDATE
        assert sm.home_network == "310-410"
        assert sm.current_network == "208-01"

    def test_successful_authentication(self):
        """Test successful authentication flow."""
        sm = RoamingStateMachine("123456789012345")
        sm.initiate_roaming("310-410", "208-01")
        success = sm.authenticate(True)
        assert success is True
        assert sm.get_state() == SubscriberState.ATTACHED

    def test_failed_authentication(self):
        """Test failed authentication flow."""
        sm = RoamingStateMachine("123456789012345")
        sm.initiate_roaming("310-410", "208-01")
        success = sm.authenticate(False)
        assert success is False
        assert sm.get_state() == SubscriberState.LOCATION_UPDATE

    def test_max_auth_attempts(self):
        """Test max authentication attempts."""
        sm = RoamingStateMachine("123456789012345")
        sm.initiate_roaming("310-410", "208-01")

        # Fail 3 times
        for i in range(3):
            sm.authenticate(False)

        assert sm.get_state() == SubscriberState.REJECTED
        assert sm.auth_attempts == 3

    def test_activate_roaming(self):
        """Test roaming activation."""
        sm = RoamingStateMachine("123456789012345")
        sm.initiate_roaming("310-410", "208-01")
        sm.authenticate(True)
        success = sm.activate_roaming()
        assert success is True
        assert sm.is_roaming() is True

    def test_detach(self):
        """Test network detachment."""
        sm = RoamingStateMachine("123456789012345")
        sm.initiate_roaming("310-410", "208-01")
        sm.authenticate(True)
        sm.activate_roaming()

        success = sm.detach()
        assert success is True
        assert sm.get_state() == SubscriberState.DETACHED

    def test_reset(self):
        """Test state machine reset."""
        sm = RoamingStateMachine("123456789012345")
        sm.initiate_roaming("310-410", "208-01")
        sm.authenticate(True)
        sm.activate_roaming()

        sm.reset()
        assert sm.get_state() == SubscriberState.IDLE
        assert sm.current_network is None
        assert sm.auth_attempts == 0

    def test_invalid_state_transitions(self):
        """Test invalid state transitions are rejected."""
        sm = RoamingStateMachine("123456789012345")

        # Try to activate roaming without authentication
        success = sm.activate_roaming()
        assert success is False

        # Try to authenticate without location update
        success = sm.authenticate(True)
        assert success is False
