"""Unit tests for mock HLR/HSS."""
import pytest
import sys
from pathlib import Path

# Add src to path
sys.path.insert(0, str(Path(__file__).parent.parent / "src"))

from hlr_mock import MockHLR


class TestMockHLR:
    """Test suite for mock HLR."""

    @pytest.fixture
    def hlr(self):
        """Create HLR instance with test data."""
        hlr = MockHLR()
        hlr.add_subscriber(
            imsi="310410123456789",
            msisdn="+15551234567",
            home_network="310-410",
            ki="0123456789ABCDEF0123456789ABCDEF"
        )
        hlr.add_roaming_agreement("310-410", ["208-01", "234-15"])
        return hlr

    def test_add_subscriber(self, hlr):
        """Test adding subscriber to HLR."""
        subscriber = hlr.get_subscriber_info("310410123456789")
        assert subscriber is not None
        assert subscriber["msisdn"] == "+15551234567"
        assert subscriber["home_network"] == "310-410"
        assert subscriber["active"] is True

    def test_validate_imsi_format(self, hlr):
        """Test IMSI format validation."""
        assert hlr.validate_imsi("310410123456789") is True
        assert hlr.validate_imsi("12345") is False  # Too short
        assert hlr.validate_imsi("1234567890123456") is False  # Too long
        assert hlr.validate_imsi("") is False  # Empty

    def test_validate_imsi_exists(self, hlr):
        """Test IMSI existence check."""
        assert hlr.validate_imsi("310410123456789") is True
        assert hlr.validate_imsi("999999999999999") is False

    def test_check_roaming_agreement_exists(self, hlr):
        """Test roaming agreement validation."""
        assert hlr.check_roaming_agreement("310410123456789", "208-01") is True
        assert hlr.check_roaming_agreement("310410123456789", "234-15") is True

    def test_check_roaming_agreement_missing(self, hlr):
        """Test rejection when no roaming agreement."""
        assert hlr.check_roaming_agreement("310410123456789", "404-45") is False

    def test_home_network_always_allowed(self, hlr):
        """Test subscriber can attach to home network."""
        assert hlr.check_roaming_agreement("310410123456789", "310-410") is True

    def test_generate_auth_vectors(self, hlr):
        """Test authentication vector generation."""
        vectors = hlr.generate_auth_vectors("310410123456789")
        assert vectors is not None
        rand, sres, kc = vectors
        assert len(rand) == 32  # 16 bytes hex
        assert len(sres) == 8   # 4 bytes hex
        assert len(kc) == 16    # 8 bytes hex

    def test_generate_auth_vectors_invalid_imsi(self, hlr):
        """Test auth vector generation fails for invalid IMSI."""
        vectors = hlr.generate_auth_vectors("999999999999999")
        assert vectors is None

    def test_authenticate_success(self, hlr):
        """Test successful authentication."""
        result = hlr.authenticate("310410123456789", "208-01")
        assert result is True

    def test_authenticate_no_agreement(self, hlr):
        """Test authentication fails without roaming agreement."""
        result = hlr.authenticate("310410123456789", "404-45")
        assert result is False

    def test_authenticate_invalid_imsi(self, hlr):
        """Test authentication fails for invalid IMSI."""
        result = hlr.authenticate("999999999999999", "208-01")
        assert result is False

    def test_authenticate_inactive_subscriber(self, hlr):
        """Test authentication fails for inactive subscriber."""
        hlr.subscribers["310410123456789"]["active"] = False
        result = hlr.authenticate("310410123456789", "208-01")
        assert result is False

    def test_authenticate_roaming_disabled(self, hlr):
        """Test authentication fails when roaming is disabled."""
        hlr.subscribers["310410123456789"]["roaming_enabled"] = False
        result = hlr.authenticate("310410123456789", "208-01")
        assert result is False
