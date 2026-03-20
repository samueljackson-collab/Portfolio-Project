#!/usr/bin/env python3
"""
generate_sample_logs.py
=======================
Generates realistic Windows Security Event log entries as JSONL.

Usage:
    python generate_sample_logs.py                    # 200 events to stdout
    python generate_sample_logs.py --count 500        # 500 events to stdout
    python generate_sample_logs.py --count 200 --out events.jsonl
    python generate_sample_logs.py --count 200 --out events.jsonl --seed 42

Mix:
    60%  authentication events  (success 4624 / failure 4625 / explicit 4648)
    20%  admin/user management  (4720, 4728, 4672, 4740)
    10%  network / lateral      (4648, custom net_conn)
    10%  process creation       (4688)
"""

import argparse
import json
import random
import sys
from datetime import datetime, timedelta, timezone

# ─────────────────────────────────────────────────────────────────────────────
# Static datasets
# ─────────────────────────────────────────────────────────────────────────────

INTERNAL_IPS = [
    "192.168.10.5",  "192.168.10.15", "192.168.10.22",
    "192.168.20.10", "192.168.20.11", "192.168.20.55",
    "192.168.30.10", "192.168.30.11", "192.168.30.99",
    "10.0.1.22",     "10.0.1.33",     "10.0.1.44",
    "10.0.2.45",     "10.0.2.60",     "10.0.3.100",
    "172.16.0.10",   "172.16.0.20",   "172.16.1.5",
]

EXTERNAL_IPS = [
    "203.0.113.45",  "203.0.113.99",  "198.51.100.7",
    "198.51.100.88", "185.220.101.33","192.0.2.100",
    "45.83.64.1",    "91.108.4.20",   "77.88.55.44",
]

HOSTS = [
    "DC01", "DC02", "FS01", "FS02",
    "WS001", "WS002", "WS003", "WS004", "WS005",
    "APP01", "APP02", "DB01", "WEBSVR01", "WEBSVR02",
    "MGMT01", "JUMP01",
]

USERNAMES = [
    "jsmith",    "adavis",   "mwilson",  "kthompson",
    "svc-backup","svc-db",   "svc-web",  "svc-monitor",
    "hlopez",    "rlee",     "tpatel",   "anonymous",
    "Administrator", "admin","guest",    "jdoe",
    "bturner",   "cbrown",   "ngomez",   "pwright",
]

DOMAINS = ["CORP", "CORP", "CORP", "CORP", "WORKGROUP"]

PROCESSES = [
    ("cmd.exe",        r"C:\Windows\System32\cmd.exe"),
    ("powershell.exe", r"C:\Windows\System32\WindowsPowerShell\v1.0\powershell.exe"),
    ("notepad.exe",    r"C:\Windows\System32\notepad.exe"),
    ("explorer.exe",   r"C:\Windows\explorer.exe"),
    ("msiexec.exe",    r"C:\Windows\System32\msiexec.exe"),
    ("wmic.exe",       r"C:\Windows\System32\wbem\WMIC.exe"),
    ("psexec.exe",     r"C:\Windows\PSEXESVC.exe"),
    ("net.exe",        r"C:\Windows\System32\net.exe"),
    ("schtasks.exe",   r"C:\Windows\System32\schtasks.exe"),
    ("rundll32.exe",   r"C:\Windows\System32\rundll32.exe"),
]

LOGON_TYPES = ["2", "3", "4", "7", "10"]

LOGON_FAILURE_REASONS = [
    "Unknown user name or bad password",
    "Account restrictions are preventing this user from signing in",
    "The account has been locked out due to too many failed login attempts",
    "The user has not been granted the requested logon type",
]

SECURITY_GROUPS = [
    "Domain Admins",
    "Administrators",
    "Backup Operators",
    "Remote Desktop Users",
    "Network Configuration Operators",
    "Power Users",
    "Event Log Readers",
]

PRIVILEGES = [
    "SeDebugPrivilege SeImpersonatePrivilege SeTcbPrivilege",
    "SeBackupPrivilege SeRestorePrivilege",
    "SeSecurityPrivilege SeAuditPrivilege",
    "SeTakeOwnershipPrivilege SeLoadDriverPrivilege",
]

DEST_IPS_EXTERNAL = [
    "203.0.113.200", "198.51.100.50", "185.220.101.1",
    "8.8.8.8",       "1.1.1.1",       "104.21.44.33",
]

# ─────────────────────────────────────────────────────────────────────────────
# Event generator helpers
# ─────────────────────────────────────────────────────────────────────────────

def rand_internal_ip() -> str:
    return random.choice(INTERNAL_IPS)

def rand_external_ip() -> str:
    return random.choice(EXTERNAL_IPS)

def rand_ip(prefer_external: bool = False) -> str:
    if prefer_external or random.random() < 0.25:
        return rand_external_ip()
    return rand_internal_ip()

def rand_user() -> str:
    return random.choice(USERNAMES)

def rand_host() -> str:
    return random.choice(HOSTS)

def rand_domain() -> str:
    return random.choice(DOMAINS)

def rand_port() -> int:
    return random.choice([80, 443, 445, 3389, 22, 135, 139, 8080, 8443, 49152 + random.randint(0, 16383)])

def rand_pid() -> int:
    return random.randint(1000, 65000)

def make_timestamp(base: datetime, jitter_seconds: int = 3600) -> str:
    offset = timedelta(seconds=random.randint(0, jitter_seconds))
    return (base + offset).strftime("%Y-%m-%dT%H:%M:%S.000Z")


# ─────────────────────────────────────────────────────────────────────────────
# Individual event builders
# ─────────────────────────────────────────────────────────────────────────────

def event_4624(ts: str) -> dict:
    """Successful logon."""
    user   = rand_user()
    host   = rand_host()
    src_ip = rand_ip()
    ltype  = random.choice(LOGON_TYPES)
    return {
        "timestamp":   ts,
        "host_name":   host,
        "event_id":    4624,
        "event_type":  "authentication_success",
        "user_name":   user,
        "user_domain": rand_domain(),
        "source_ip":   src_ip,
        "source_port": rand_port(),
        "dest_ip":     rand_internal_ip(),
        "dest_port":   445 if ltype == "3" else 0,
        "severity":    1,
        "logon_type":  ltype,
        "message":     f"An account was successfully logged on. Subject: {user} Logon Type: {ltype} Source IP: {src_ip}",
        "tags":        ["windows", "authentication", "logon_success"],
    }


def event_4625(ts: str, src_ip: str = None) -> dict:
    """Failed logon."""
    user   = rand_user()
    host   = rand_host()
    src_ip = src_ip or rand_ip(prefer_external=True)
    ltype  = random.choice(["2", "3", "10"])
    reason = random.choice(LOGON_FAILURE_REASONS)
    return {
        "timestamp":       ts,
        "host_name":       host,
        "event_id":        4625,
        "event_type":      "authentication_failure",
        "user_name":       user,
        "user_domain":     rand_domain(),
        "source_ip":       src_ip,
        "source_port":     rand_port(),
        "dest_ip":         rand_internal_ip(),
        "dest_port":       0,
        "severity":        3,
        "logon_type":      ltype,
        "failure_reason":  reason,
        "message":         f"An account failed to log on. User: {user} Logon Type: {ltype} Source IP: {src_ip} Reason: {reason}",
        "tags":            ["windows", "authentication", "logon_failure", "credential_access"],
        "alert_name":      "Failed Logon Attempt",
        "alert_severity":  "medium",
    }


def event_4648(ts: str) -> dict:
    """Logon with explicit credentials."""
    user = rand_user()
    host = rand_host()
    src  = rand_internal_ip()
    return {
        "timestamp":   ts,
        "host_name":   host,
        "event_id":    4648,
        "event_type":  "authentication_explicit",
        "user_name":   user,
        "user_domain": rand_domain(),
        "source_ip":   src,
        "source_port": rand_port(),
        "dest_ip":     rand_internal_ip(),
        "dest_port":   445,
        "severity":    2,
        "message":     f"A logon was attempted using explicit credentials. Account: {user} Source: {src}",
        "tags":        ["windows", "authentication", "explicit_logon"],
    }


def event_4688(ts: str) -> dict:
    """Process creation."""
    user        = rand_user()
    host        = rand_host()
    proc_name, proc_path = random.choice(PROCESSES)
    src_ip      = rand_internal_ip()
    sev = 3 if proc_name in ("psexec.exe", "wmic.exe", "rundll32.exe") else 1
    alert_name  = "Suspicious Process Execution" if sev == 3 else ""
    alert_sev   = "medium" if sev == 3 else "info"
    return {
        "timestamp":         ts,
        "host_name":         host,
        "event_id":          4688,
        "event_type":        "process_start",
        "user_name":         user,
        "user_domain":       rand_domain(),
        "source_ip":         src_ip,
        "source_port":       0,
        "dest_ip":           "",
        "dest_port":         0,
        "severity":          sev,
        "process_name":      proc_name,
        "process_path":      proc_path,
        "process_pid":       rand_pid(),
        "message":           f"A new process has been created. Creator: {user} Process: {proc_path} Host: {host}",
        "tags":              ["windows", "process_creation"],
        "alert_name":        alert_name,
        "alert_severity":    alert_sev,
    }


def event_4720(ts: str) -> dict:
    """New user account created."""
    creator  = random.choice(["Administrator", "admin", "jsmith", "adavis"])
    new_user = f"new_user_{random.randint(100, 999)}"
    host     = random.choice(["DC01", "DC02"])
    return {
        "timestamp":      ts,
        "host_name":      host,
        "event_id":       4720,
        "event_type":     "user_created",
        "user_name":      creator,
        "user_domain":    "CORP",
        "source_ip":      rand_internal_ip(),
        "source_port":    0,
        "dest_ip":        "",
        "dest_port":      0,
        "severity":       3,
        "new_user_name":  new_user,
        "message":        f"A user account was created. Creator: {creator} New account: {new_user}",
        "tags":           ["windows", "user_management", "persistence"],
        "alert_name":     "New User Account Created",
        "alert_severity": "medium",
    }


def event_4728(ts: str) -> dict:
    """Member added to security-enabled global group."""
    actor  = random.choice(["Administrator", "adavis", "svc-backup"])
    target = rand_user()
    group  = random.choice(SECURITY_GROUPS)
    host   = random.choice(["DC01", "DC02"])
    sev    = 5 if "Admin" in group else 4
    return {
        "timestamp":      ts,
        "host_name":      host,
        "event_id":       4728,
        "event_type":     "group_member_added",
        "user_name":      actor,
        "user_domain":    "CORP",
        "source_ip":      rand_internal_ip(),
        "source_port":    0,
        "dest_ip":        "",
        "dest_port":      0,
        "severity":       sev,
        "target_user":    target,
        "target_group":   group,
        "message":        f"A member was added to a security-enabled global group. Actor: {actor} Member: {target} Group: {group}",
        "tags":           ["windows", "group_modification", "privilege_escalation"],
        "alert_name":     "Admin Group Membership Change" if "Admin" in group else "User Added to Security Group",
        "alert_severity": "critical" if "Admin" in group else "high",
    }


def event_4672(ts: str) -> dict:
    """Special privileges assigned to new logon."""
    user  = rand_user()
    host  = rand_host()
    privs = random.choice(PRIVILEGES)
    src   = rand_internal_ip()
    return {
        "timestamp":      ts,
        "host_name":      host,
        "event_id":       4672,
        "event_type":     "special_logon",
        "user_name":      user,
        "user_domain":    rand_domain(),
        "source_ip":      src,
        "source_port":    rand_port(),
        "dest_ip":        rand_internal_ip(),
        "dest_port":      0,
        "severity":       3,
        "privileges":     privs,
        "message":        f"Special privileges assigned to new logon. Account: {user} Privileges: {privs}",
        "tags":           ["windows", "special_logon", "privilege_use"],
        "alert_name":     "Special Privileges Logon",
        "alert_severity": "medium",
    }


def event_4740(ts: str) -> dict:
    """Account lockout."""
    user = rand_user()
    host = random.choice(["DC01", "DC02"])
    caller_host = rand_host()
    src  = rand_ip(prefer_external=True)
    return {
        "timestamp":      ts,
        "host_name":      host,
        "event_id":       4740,
        "event_type":     "account_lockout",
        "user_name":      user,
        "user_domain":    "CORP",
        "source_ip":      src,
        "source_port":    0,
        "dest_ip":        "",
        "dest_port":      0,
        "severity":       4,
        "caller_host":    caller_host,
        "message":        f"A user account was locked out. Account: {user} Caller: {caller_host} Source: {src}",
        "tags":           ["windows", "lockout", "brute_force_indicator"],
        "alert_name":     "Account Locked Out",
        "alert_severity": "high",
    }


def event_network_connection(ts: str) -> dict:
    """Simulated network flow event."""
    src_host  = rand_host()
    src_ip    = rand_internal_ip()
    dst_ip    = random.choice(DEST_IPS_EXTERNAL + INTERNAL_IPS[:6])
    dst_port  = random.choice([80, 443, 8080, 8443, 22, 3389, 445, 1433])
    protocol  = "TCP"
    bytes_out = random.randint(1024, 512 * 1024 * 1024)
    sev = 4 if bytes_out > 104857600 else 1
    alert_name  = "Large Outbound Data Transfer" if sev == 4 else ""
    alert_sev   = "high" if sev == 4 else "info"
    return {
        "timestamp":      ts,
        "host_name":      src_host,
        "event_id":       "NET_CONN",
        "event_type":     "network_connection",
        "user_name":      rand_user(),
        "user_domain":    rand_domain(),
        "source_ip":      src_ip,
        "source_port":    rand_port(),
        "dest_ip":        dst_ip,
        "dest_port":      dst_port,
        "severity":       sev,
        "protocol":       protocol,
        "bytes_sent":     bytes_out,
        "bytes_received": random.randint(512, 1024 * 1024),
        "message":        f"Network connection: {src_ip}:{rand_port()} -> {dst_ip}:{dst_port} protocol={protocol} bytes_out={bytes_out}",
        "tags":           ["network", "flow"],
        "alert_name":     alert_name,
        "alert_severity": alert_sev,
    }


# ─────────────────────────────────────────────────────────────────────────────
# Main generation logic
# ─────────────────────────────────────────────────────────────────────────────

def generate_events(count: int, seed: int = None) -> list:
    if seed is not None:
        random.seed(seed)

    base_time = datetime(2026, 1, 15, 8, 0, 0, tzinfo=timezone.utc)
    events = []

    # Proportion buckets
    auth_count    = int(count * 0.60)
    admin_count   = int(count * 0.20)
    network_count = int(count * 0.10)
    process_count = count - auth_count - admin_count - network_count  # remaining ~10%

    # ── Auth events (60%) ──────────────────────────────────────────────────────
    # Roughly 55% success, 35% failure, 10% explicit
    success_count  = int(auth_count * 0.55)
    failure_count  = int(auth_count * 0.35)
    explicit_count = auth_count - success_count - failure_count

    # Inject a brute-force cluster: >10 failures from same IP within 5 min
    bf_ip = "203.0.113.45"
    bf_base = timedelta(seconds=random.randint(0, 2400))  # somewhere in first 40 min
    for i in range(14):
        ts = (base_time + bf_base + timedelta(seconds=i * 18)).strftime("%Y-%m-%dT%H:%M:%S.000Z")
        events.append(event_4625(ts, src_ip=bf_ip))

    remaining_failures = failure_count - 14
    for _ in range(max(0, remaining_failures)):
        ts = make_timestamp(base_time)
        events.append(event_4625(ts))

    for _ in range(success_count):
        ts = make_timestamp(base_time)
        events.append(event_4624(ts))

    for _ in range(explicit_count):
        ts = make_timestamp(base_time)
        events.append(event_4648(ts))

    # ── Admin / user management events (20%) ──────────────────────────────────
    # 4728, 4720, 4672, 4740 distributed across admin budget
    for i in range(admin_count):
        ts = make_timestamp(base_time)
        bucket = i % 4
        if bucket == 0:
            events.append(event_4728(ts))
        elif bucket == 1:
            events.append(event_4720(ts))
        elif bucket == 2:
            events.append(event_4672(ts))
        else:
            events.append(event_4740(ts))

    # ── Network events (10%) ──────────────────────────────────────────────────
    for _ in range(network_count):
        ts = make_timestamp(base_time)
        events.append(event_network_connection(ts))

    # ── Process creation events (~10%) ────────────────────────────────────────
    for _ in range(process_count):
        ts = make_timestamp(base_time)
        events.append(event_4688(ts))

    # Shuffle to interleave event types realistically
    random.shuffle(events)

    # Ensure each event has all required fields
    required_fields = [
        "timestamp", "host_name", "event_id", "event_type",
        "user_name", "source_ip", "dest_ip", "severity", "message", "tags",
    ]
    for ev in events:
        for field in required_fields:
            if field not in ev:
                ev[field] = "" if field != "severity" else 1
        # Clean up empty dest_ip
        if ev.get("dest_ip") == "":
            ev["dest_ip"] = "0.0.0.0"

    return events


# ─────────────────────────────────────────────────────────────────────────────
# CLI entry point
# ─────────────────────────────────────────────────────────────────────────────

def main():
    parser = argparse.ArgumentParser(
        description="Generate synthetic SIEM security events as JSONL."
    )
    parser.add_argument(
        "--count", "-n",
        type=int,
        default=200,
        help="Number of events to generate (default: 200)",
    )
    parser.add_argument(
        "--out", "-o",
        type=str,
        default=None,
        help="Output file path. Defaults to stdout.",
    )
    parser.add_argument(
        "--seed",
        type=int,
        default=None,
        help="Random seed for reproducible output.",
    )
    parser.add_argument(
        "--pretty",
        action="store_true",
        default=False,
        help="Pretty-print JSON (one event per block, not JSONL).",
    )
    args = parser.parse_args()

    events = generate_events(count=args.count, seed=args.seed)

    output_lines = []
    for ev in events:
        if args.pretty:
            output_lines.append(json.dumps(ev, indent=2))
        else:
            output_lines.append(json.dumps(ev, separators=(",", ":")))

    output_text = "\n".join(output_lines) + "\n"

    if args.out:
        with open(args.out, "w", encoding="utf-8") as fh:
            fh.write(output_text)
        print(f"Wrote {len(events)} events to {args.out}", file=sys.stderr)
    else:
        sys.stdout.write(output_text)


if __name__ == "__main__":
    main()
