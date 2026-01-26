"""
International Roaming Simulator

Simulates HLR/VLR lookups, network handoffs, call flow state transitions,
and network latency for cross-carrier roaming scenarios.
"""

import random
import time
from enum import Enum
from dataclasses import dataclass, field
from typing import Dict, List, Optional, Tuple
from datetime import datetime, timedelta
import logging

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


class CallFlowState(Enum):
    """Call flow states during roaming"""

    IDLE = "idle"
    LOCATION_REQUEST = "location_request"
    HLR_LOOKUP = "hlr_lookup"
    VLR_REGISTRATION = "vlr_registration"
    CALL_SETUP = "call_setup"
    CONNECTED = "connected"
    HANDOFF_INITIATED = "handoff_initiated"
    HANDOFF_IN_PROGRESS = "handoff_in_progress"
    HANDOFF_COMPLETE = "handoff_complete"
    CALL_TEARDOWN = "call_teardown"
    FAILED = "failed"


class OperatorType(Enum):
    """Types of network operators"""

    HOME_NETWORK = "home_network"
    VISITED_NETWORK = "visited_network"


@dataclass
class NetworkLatency:
    """Network latency simulation parameters"""

    min_ms: float = 20.0
    max_ms: float = 150.0
    jitter_pct: float = 10.0  # Jitter as percentage of latency

    def simulate(self) -> float:
        """Simulate latency with jitter"""
        base_latency = random.uniform(self.min_ms, self.max_ms)
        jitter = base_latency * (self.jitter_pct / 100.0) * random.uniform(-1, 1)
        return max(self.min_ms, base_latency + jitter)


@dataclass
class PLMN:
    """Public Land Mobile Network (operator) representation"""

    mcc: str  # Mobile Country Code (3 digits)
    mnc: str  # Mobile Network Code (2-3 digits)
    operator_name: str = ""
    operator_type: OperatorType = OperatorType.VISITED_NETWORK
    latency: NetworkLatency = field(default_factory=NetworkLatency)

    @property
    def plmn_id(self) -> str:
        """Return PLMN ID as MCC-MNC"""
        return f"{self.mcc}-{self.mnc}"

    def __hash__(self):
        return hash(self.plmn_id)

    def __eq__(self, other):
        if isinstance(other, PLMN):
            return self.plmn_id == other.plmn_id
        return False


@dataclass
class HLRRecord:
    """Home Location Register record"""

    imsi: str
    msisdn: str  # Mobile Subscriber Integrated Services Digital Network number
    home_network: PLMN
    authentication_key: str
    subscription_profile: Dict = field(default_factory=dict)
    roaming_allowed: bool = True
    allowed_networks: List[str] = field(default_factory=list)

    def is_roaming_allowed_in(self, visited_plmn: PLMN) -> bool:
        """Check if roaming is allowed in the visited network"""
        if not self.roaming_allowed:
            return False
        if self.allowed_networks and visited_plmn.plmn_id not in self.allowed_networks:
            return False
        return True


@dataclass
class VLRRecord:
    """Visitor Location Register record"""

    imsi: str
    msisdn: str
    home_network: PLMN
    visited_network: PLMN
    location_area_code: str
    cell_id: str
    vlr_location: str = ""
    registration_time: datetime = field(default_factory=datetime.now)
    last_activity: datetime = field(default_factory=datetime.now)
    is_active: bool = True
    accumulated_charges: float = 0.0

    def update_activity(self):
        """Update last activity timestamp"""
        self.last_activity = datetime.now()


@dataclass
class CallSession:
    """Represents a roaming call session"""

    session_id: str
    imsi: str
    msisdn: str
    called_party: str
    home_network: PLMN
    visited_network: PLMN
    state: CallFlowState = CallFlowState.IDLE
    hlr_lookup_time: float = 0.0
    vlr_lookup_time: float = 0.0
    call_setup_time: float = 0.0
    connection_time: Optional[datetime] = None
    disconnection_time: Optional[datetime] = None
    total_duration: float = 0.0
    handoffs: List[Dict] = field(default_factory=list)
    error_message: Optional[str] = None
    network_latencies: Dict[str, float] = field(default_factory=dict)

    def add_handoff(self, from_network: PLMN, to_network: PLMN, duration_ms: float):
        """Record a network handoff"""
        self.handoffs.append(
            {
                "timestamp": datetime.now().isoformat(),
                "from_network": from_network.plmn_id,
                "to_network": to_network.plmn_id,
                "duration_ms": duration_ms,
            }
        )


class HLRDatabase:
    """Home Location Register - stores subscriber information"""

    def __init__(self):
        self.records: Dict[str, HLRRecord] = {}
        self.lookup_latency = NetworkLatency(min_ms=10.0, max_ms=50.0)

    def register_subscriber(self, hlr_record: HLRRecord):
        """Register a subscriber in the HLR"""
        self.records[hlr_record.imsi] = hlr_record
        logger.info(f"HLR: Registered subscriber {hlr_record.msisdn}")

    def lookup(self, imsi: str) -> Optional[HLRRecord]:
        """Lookup a subscriber in the HLR with simulated latency"""
        latency = self.lookup_latency.simulate()
        time.sleep(latency / 1000.0)  # Simulate network delay

        if imsi in self.records:
            logger.info(f"HLR: Found subscriber {imsi} (latency: {latency:.2f}ms)")
            return self.records[imsi]

        logger.warning(f"HLR: Subscriber {imsi} not found")
        return None

    def verify_roaming_permission(self, imsi: str, visited_plmn: PLMN) -> bool:
        """Verify if subscriber is allowed to roam in the visited network"""
        record = self.records.get(imsi)
        if not record:
            return False
        return record.is_roaming_allowed_in(visited_plmn)


class VLRDatabase:
    """Visitor Location Register - stores roaming subscriber information"""

    def __init__(self, plmn: PLMN):
        self.plmn = plmn
        self.records: Dict[str, VLRRecord] = {}
        self.lookup_latency = NetworkLatency(min_ms=15.0, max_ms=60.0)

    def register(self, vlr_record: VLRRecord) -> bool:
        """Register a roaming subscriber in the VLR"""
        latency = self.lookup_latency.simulate()
        time.sleep(latency / 1000.0)  # Simulate network delay

        self.records[vlr_record.imsi] = vlr_record
        logger.info(
            f"VLR ({self.plmn.plmn_id}): Registered roaming subscriber {vlr_record.msisdn}"
        )
        return True

    def lookup(self, imsi: str) -> Optional[VLRRecord]:
        """Lookup a roaming subscriber in the VLR"""
        latency = self.lookup_latency.simulate()
        time.sleep(latency / 1000.0)  # Simulate network delay

        if imsi in self.records:
            record = self.records[imsi]
            record.update_activity()
            logger.info(f"VLR ({self.plmn.plmn_id}): Found roaming subscriber {imsi}")
            return record

        return None

    def deregister(self, imsi: str) -> bool:
        """Deregister a roaming subscriber from the VLR"""
        if imsi in self.records:
            del self.records[imsi]
            logger.info(
                f"VLR ({self.plmn.plmn_id}): Deregistered roaming subscriber {imsi}"
            )
            return True
        return False

    def get_active_subscribers(self) -> List[VLRRecord]:
        """Get all active roaming subscribers"""
        return [r for r in self.records.values() if r.is_active]


class NetworkOperator:
    """Represents a mobile network operator"""

    def __init__(self, plmn: PLMN, is_home_network: bool = False):
        self.plmn = plmn
        self.is_home_network = is_home_network
        self.hlr: Optional[HLRDatabase] = HLRDatabase() if is_home_network else None
        self.vlr = VLRDatabase(plmn)
        self.call_sessions: Dict[str, CallSession] = {}

    def create_call_session(
        self,
        imsi: str,
        msisdn: str,
        called_party: str,
        home_network: PLMN,
        visited_network: PLMN,
    ) -> Optional[CallSession]:
        """Create a new call session"""
        session_id = f"session_{int(time.time() * 1000)}_{random.randint(1000, 9999)}"
        session = CallSession(
            session_id=session_id,
            imsi=imsi,
            msisdn=msisdn,
            called_party=called_party,
            home_network=home_network,
            visited_network=visited_network,
            state=CallFlowState.LOCATION_REQUEST,
        )
        self.call_sessions[session_id] = session
        logger.info(
            f"Operator ({self.plmn.plmn_id}): Created call session {session_id}"
        )
        return session


class RoamingSimulator:
    """Main roaming simulation engine"""

    def __init__(self):
        self.home_networks: Dict[str, NetworkOperator] = {}
        self.visited_networks: Dict[str, NetworkOperator] = {}
        self.call_sessions: Dict[str, CallSession] = {}
        self.inter_operator_latency = NetworkLatency(min_ms=50.0, max_ms=200.0)

    def register_home_network(self, plmn: PLMN) -> NetworkOperator:
        """Register a home network operator"""
        plmn.operator_type = OperatorType.HOME_NETWORK
        operator = NetworkOperator(plmn, is_home_network=True)
        self.home_networks[plmn.plmn_id] = operator
        logger.info(f"Simulator: Registered home network {plmn.plmn_id}")
        return operator

    def register_visited_network(self, plmn: PLMN) -> NetworkOperator:
        """Register a visited network operator"""
        plmn.operator_type = OperatorType.VISITED_NETWORK
        operator = NetworkOperator(plmn, is_home_network=False)
        self.visited_networks[plmn.plmn_id] = operator
        logger.info(f"Simulator: Registered visited network {plmn.plmn_id}")
        return operator

    def _get_home_operator(self, plmn_id: str) -> Optional[NetworkOperator]:
        """Get home network operator by PLMN ID"""
        return self.home_networks.get(plmn_id)

    def _get_visited_operator(self, plmn_id: str) -> Optional[NetworkOperator]:
        """Get visited network operator by PLMN ID"""
        return self.visited_networks.get(plmn_id)

    def initiate_call(
        self,
        imsi: str,
        msisdn: str,
        called_party: str,
        home_plmn_id: str,
        visited_plmn_id: str,
    ) -> Optional[CallSession]:
        """Initiate a roaming call"""
        home_operator = self._get_home_operator(home_plmn_id)
        visited_operator = self._get_visited_operator(visited_plmn_id)

        if not home_operator or not visited_operator:
            logger.error(
                f"Invalid PLMN IDs: home={home_plmn_id}, visited={visited_plmn_id}"
            )
            return None

        # Create call session
        session = visited_operator.create_call_session(
            imsi, msisdn, called_party, home_operator.plmn, visited_operator.plmn
        )

        if not session:
            return None

        # Simulate HLR lookup
        session.state = CallFlowState.HLR_LOOKUP
        start_time = time.time()
        hlr_record = home_operator.hlr.lookup(imsi)
        session.hlr_lookup_time = (time.time() - start_time) * 1000
        session.network_latencies["hlr_lookup"] = session.hlr_lookup_time

        if not hlr_record:
            session.state = CallFlowState.FAILED
            session.error_message = "Subscriber not found in HLR"
            logger.error(f"Call {session.session_id}: {session.error_message}")
            return session

        # Verify roaming permission
        if not home_operator.hlr.verify_roaming_permission(imsi, visited_operator.plmn):
            session.state = CallFlowState.FAILED
            session.error_message = "Roaming not allowed in this network"
            logger.error(f"Call {session.session_id}: {session.error_message}")
            return session

        # Simulate VLR registration/lookup
        session.state = CallFlowState.VLR_REGISTRATION
        start_time = time.time()

        # Try to find existing VLR record
        vlr_record = visited_operator.vlr.lookup(imsi)

        if not vlr_record:
            # Create new VLR record
            vlr_record = VLRRecord(
                imsi=imsi,
                msisdn=msisdn,
                home_network=home_operator.plmn,
                visited_network=visited_operator.plmn,
                location_area_code="LAC_001",
                cell_id="CELL_001",
                vlr_location=f"{visited_operator.plmn.plmn_id}_VLR",
            )
            visited_operator.vlr.register(vlr_record)

        session.vlr_lookup_time = (time.time() - start_time) * 1000
        session.network_latencies["vlr_lookup"] = session.vlr_lookup_time

        # Simulate call setup
        session.state = CallFlowState.CALL_SETUP
        start_time = time.time()
        latency = self.inter_operator_latency.simulate()
        time.sleep(latency / 1000.0)
        session.call_setup_time = (time.time() - start_time) * 1000
        session.network_latencies["call_setup"] = session.call_setup_time

        # Call connected
        session.state = CallFlowState.CONNECTED
        session.connection_time = datetime.now()
        self.call_sessions[session.session_id] = session

        logger.info(
            f"Call {session.session_id}: CONNECTED "
            f"(HLR: {session.hlr_lookup_time:.2f}ms, "
            f"VLR: {session.vlr_lookup_time:.2f}ms, "
            f"Setup: {session.call_setup_time:.2f}ms)"
        )

        return session

    def execute_handoff(self, session_id: str, new_visited_plmn_id: str) -> bool:
        """Execute network handoff during an active call"""
        session = self.call_sessions.get(session_id)

        if not session or session.state != CallFlowState.CONNECTED:
            logger.error(f"Cannot handoff session {session_id}: not in CONNECTED state")
            return False

        new_operator = self._get_visited_operator(new_visited_plmn_id)
        if not new_operator:
            logger.error(f"Target network {new_visited_plmn_id} not found")
            return False

        old_network = session.visited_network
        logger.info(
            f"Call {session_id}: Initiating handoff from {old_network.plmn_id} to {new_visited_plmn_id}"
        )

        # Handoff in progress
        session.state = CallFlowState.HANDOFF_IN_PROGRESS
        start_time = time.time()

        # Simulate VLR operations on new network
        vlr_record = VLRRecord(
            imsi=session.imsi,
            msisdn=session.msisdn,
            home_network=session.home_network,
            visited_network=new_operator.plmn,
            location_area_code="LAC_002",
            cell_id="CELL_002",
            vlr_location=f"{new_visited_plmn_id}_VLR",
        )
        new_operator.vlr.register(vlr_record)

        # Simulate handoff latency
        handoff_latency = (
            self.inter_operator_latency.simulate() * 1.5
        )  # Handoff takes longer
        time.sleep(handoff_latency / 1000.0)

        handoff_duration = (time.time() - start_time) * 1000

        # Update session
        session.visited_network = new_operator.plmn
        session.state = CallFlowState.HANDOFF_COMPLETE
        session.add_handoff(old_network, new_operator.plmn, handoff_duration)
        session.network_latencies["last_handoff"] = handoff_duration

        logger.info(
            f"Call {session_id}: Handoff complete "
            f"({old_network.plmn_id} -> {new_visited_plmn_id}, "
            f"duration: {handoff_duration:.2f}ms)"
        )

        # Continue connected after handoff
        session.state = CallFlowState.CONNECTED

        return True

    def terminate_call(self, session_id: str) -> Optional[CallSession]:
        """Terminate a call session"""
        session = self.call_sessions.get(session_id)

        if not session:
            logger.error(f"Session {session_id} not found")
            return None

        session.state = CallFlowState.CALL_TEARDOWN
        session.disconnection_time = datetime.now()

        if session.connection_time:
            session.total_duration = (
                session.disconnection_time - session.connection_time
            ).total_seconds()

        # Deregister from VLR
        visited_operator = self._get_visited_operator(session.visited_network.plmn_id)
        if visited_operator:
            visited_operator.vlr.deregister(session.imsi)

        session.state = CallFlowState.IDLE
        logger.info(
            f"Call {session_id}: TERMINATED "
            f"(Duration: {session.total_duration:.2f}s, "
            f"Handoffs: {len(session.handoffs)})"
        )

        return session

    def get_call_session(self, session_id: str) -> Optional[CallSession]:
        """Get call session details"""
        return self.call_sessions.get(session_id)

    def get_session_statistics(self, session_id: str) -> Optional[Dict]:
        """Get statistics for a call session"""
        session = self.call_sessions.get(session_id)

        if not session:
            return None

        return {
            "session_id": session.session_id,
            "imsi": session.imsi,
            "state": session.state.value,
            "hlr_lookup_time_ms": session.hlr_lookup_time,
            "vlr_lookup_time_ms": session.vlr_lookup_time,
            "call_setup_time_ms": session.call_setup_time,
            "total_duration_s": session.total_duration,
            "handoff_count": len(session.handoffs),
            "handoffs": session.handoffs,
            "error": session.error_message,
        }

    def get_simulator_statistics(self) -> Dict:
        """Get overall simulator statistics"""
        total_sessions = len(self.call_sessions)
        successful_sessions = sum(
            1 for s in self.call_sessions.values() if s.state != CallFlowState.FAILED
        )
        total_handoffs = sum(len(s.handoffs) for s in self.call_sessions.values())
        avg_hlr_latency = sum(
            s.hlr_lookup_time for s in self.call_sessions.values()
        ) / max(total_sessions, 1)
        avg_vlr_latency = sum(
            s.vlr_lookup_time for s in self.call_sessions.values()
        ) / max(total_sessions, 1)

        return {
            "total_sessions": total_sessions,
            "successful_sessions": successful_sessions,
            "failed_sessions": total_sessions - successful_sessions,
            "success_rate": (successful_sessions / max(total_sessions, 1)) * 100,
            "total_handoffs": total_handoffs,
            "avg_handoffs_per_session": total_handoffs / max(successful_sessions, 1),
            "avg_hlr_lookup_time_ms": avg_hlr_latency,
            "avg_vlr_lookup_time_ms": avg_vlr_latency,
        }
