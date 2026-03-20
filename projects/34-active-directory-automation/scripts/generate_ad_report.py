#!/usr/bin/env python3
"""
AD Infrastructure Report Generator
Demo mode — produces a complete AD topology report from realistic sample data.

Shows: OU tree with user/computer counts, full user roster, group memberships,
stale account analysis, GPO list, replication status, DNS zones, and a
security summary with recommendations.

Usage:
    python3 generate_ad_report.py
    python3 generate_ad_report.py --output ad_report.txt
    python3 generate_ad_report.py --format json --output ad_report.json
"""

import argparse
import json
import sys
from datetime import datetime, timedelta
import random

# ---------------------------------------------------------------------------
# Sample Data
# ---------------------------------------------------------------------------

REPORT_DATE = datetime(2026, 1, 15, 9, 15, 22)

DOMAIN_INFO = {
    "domain":                  "corp.contoso.local",
    "netbios":                 "CONTOSO",
    "forest":                  "corp.contoso.local",
    "forest_functional_level": "Windows Server 2019",
    "domain_functional_level": "Windows Server 2019",
    "pdc_emulator":            "DC01.corp.contoso.local",
    "rid_master":              "DC01.corp.contoso.local",
    "infrastructure_master":   "DC02.corp.contoso.local",
    "schema_master":           "DC01.corp.contoso.local",
    "naming_master":           "DC01.corp.contoso.local",
}

DOMAIN_CONTROLLERS = [
    {
        "hostname":    "DC01.corp.contoso.local",
        "ip":          "192.168.10.10",
        "site":        "HQ-Site",
        "os":          "Windows Server 2022 Datacenter",
        "roles":       ["PDC Emulator", "RID Master", "Schema Master", "Naming Master"],
        "is_gc":       True,
        "repl_status": "OK",
        "uptime_days": 147,
    },
    {
        "hostname":    "DC02.corp.contoso.local",
        "ip":          "192.168.10.11",
        "site":        "HQ-Site",
        "os":          "Windows Server 2022 Datacenter",
        "roles":       ["Infrastructure Master"],
        "is_gc":       True,
        "repl_status": "OK",
        "uptime_days": 142,
    },
]

OU_STRUCTURE = [
    {
        "name":       "OU=IT",
        "path":       "DC=corp,DC=contoso,DC=local",
        "users":      12,
        "groups":     3,
        "computers":  0,
        "children": [
            {"name": "OU=Admins",    "users": 4,  "groups": 0, "computers": 0},
            {"name": "OU=Help-Desk", "users": 8,  "groups": 0, "computers": 0},
            {"name": "OU=DevOps",    "users": 4,  "groups": 0, "computers": 0},
        ],
    },
    {
        "name":       "OU=HR",
        "path":       "DC=corp,DC=contoso,DC=local",
        "users":      23,
        "groups":     1,
        "computers":  0,
        "children": [],
    },
    {
        "name":       "OU=Finance",
        "path":       "DC=corp,DC=contoso,DC=local",
        "users":      18,
        "groups":     2,
        "computers":  0,
        "children": [],
    },
    {
        "name":       "OU=Operations",
        "path":       "DC=corp,DC=contoso,DC=local",
        "users":      31,
        "groups":     4,
        "computers":  0,
        "children": [],
    },
    {
        "name":       "OU=ServiceAccounts",
        "path":       "DC=corp,DC=contoso,DC=local",
        "users":      15,
        "groups":     0,
        "computers":  0,
        "children": [],
    },
    {
        "name":       "OU=Servers",
        "path":       "DC=corp,DC=contoso,DC=local",
        "users":      0,
        "groups":     0,
        "computers":  22,
        "children": [
            {"name": "OU=AppServers",  "users": 0, "groups": 0, "computers": 6},
            {"name": "OU=WebServers",  "users": 0, "groups": 0, "computers": 4},
            {"name": "OU=DBServers",   "users": 0, "groups": 0, "computers": 3},
            {"name": "OU=FileServers", "users": 0, "groups": 0, "computers": 2},
        ],
    },
    {
        "name":       "OU=Workstations",
        "path":       "DC=corp,DC=contoso,DC=local",
        "users":      0,
        "groups":     0,
        "computers":  87,
        "children": [],
    },
    {
        "name":       "OU=Security",
        "path":       "DC=corp,DC=contoso,DC=local",
        "users":      0,
        "groups":     6,
        "computers":  0,
        "children": [],
    },
]

USERS = [
    # IT - Admins
    {"sam": "jsmith",    "name": "John Smith",       "ou": "OU=Admins,OU=IT", "dept": "IT",         "title": "Senior Systems Administrator", "enabled": True,  "last_logon": "2026-01-14", "pwd_age_days": 22,  "locked": False},
    {"sam": "mmartinez", "name": "Maria Martinez",   "ou": "OU=Admins,OU=IT", "dept": "IT",         "title": "Network Administrator",        "enabled": True,  "last_logon": "2026-01-15", "pwd_age_days": 8,   "locked": False},
    {"sam": "rchen",     "name": "Robert Chen",      "ou": "OU=DevOps,OU=IT", "dept": "IT",         "title": "DevOps Engineer",             "enabled": True,  "last_logon": "2026-01-15", "pwd_age_days": 14,  "locked": False},
    {"sam": "apatel",    "name": "Anita Patel",      "ou": "OU=DevOps,OU=IT", "dept": "IT",         "title": "DevOps Engineer",             "enabled": True,  "last_logon": "2026-01-13", "pwd_age_days": 31,  "locked": False},
    {"sam": "twilson",   "name": "Tyler Wilson",     "ou": "OU=Help-Desk,OU=IT", "dept": "IT",      "title": "Help Desk Technician II",     "enabled": True,  "last_logon": "2026-01-15", "pwd_age_days": 17,  "locked": False},
    {"sam": "lnguyen",   "name": "Linh Nguyen",      "ou": "OU=Help-Desk,OU=IT", "dept": "IT",      "title": "Help Desk Technician I",      "enabled": True,  "last_logon": "2026-01-14", "pwd_age_days": 45,  "locked": False},
    # HR
    {"sam": "adavis",    "name": "Amanda Davis",     "ou": "OU=HR",           "dept": "HR",         "title": "HR Manager",                  "enabled": True,  "last_logon": "2026-01-15", "pwd_age_days": 12,  "locked": False},
    {"sam": "kjohnson",  "name": "Karen Johnson",    "ou": "OU=HR",           "dept": "HR",         "title": "HR Specialist",               "enabled": True,  "last_logon": "2026-01-14", "pwd_age_days": 55,  "locked": False},
    {"sam": "bthompson", "name": "Brian Thompson",   "ou": "OU=HR",           "dept": "HR",         "title": "Recruiter",                   "enabled": True,  "last_logon": "2026-01-13", "pwd_age_days": 68,  "locked": False},
    {"sam": "slee",      "name": "Sophia Lee",       "ou": "OU=HR",           "dept": "HR",         "title": "HR Coordinator",              "enabled": True,  "last_logon": "2026-01-10", "pwd_age_days": 77,  "locked": False},
    # Finance
    {"sam": "mwhite",    "name": "Michael White",    "ou": "OU=Finance",      "dept": "Finance",    "title": "Finance Director",            "enabled": True,  "last_logon": "2026-01-15", "pwd_age_days": 19,  "locked": False},
    {"sam": "jrobinson", "name": "Jennifer Robinson","ou": "OU=Finance",      "dept": "Finance",    "title": "Senior Accountant",           "enabled": True,  "last_logon": "2026-01-14", "pwd_age_days": 38,  "locked": False},
    {"sam": "dgarcia",   "name": "David Garcia",     "ou": "OU=Finance",      "dept": "Finance",    "title": "Financial Analyst",           "enabled": True,  "last_logon": "2026-01-12", "pwd_age_days": 52,  "locked": False},
    {"sam": "cwalker",   "name": "Christine Walker", "ou": "OU=Finance",      "dept": "Finance",    "title": "Accounts Payable Specialist", "enabled": True,  "last_logon": "2026-01-15", "pwd_age_days": 6,   "locked": False},
    # Operations
    {"sam": "phall",     "name": "Patrick Hall",     "ou": "OU=Operations",   "dept": "Operations", "title": "Operations Manager",          "enabled": True,  "last_logon": "2026-01-15", "pwd_age_days": 24,  "locked": False},
    {"sam": "nyoung",    "name": "Nancy Young",      "ou": "OU=Operations",   "dept": "Operations", "title": "Operations Analyst",          "enabled": True,  "last_logon": "2026-01-14", "pwd_age_days": 33,  "locked": False},
    {"sam": "skorea",    "name": "Samuel Korea",     "ou": "OU=Operations",   "dept": "Operations", "title": "Logistics Coordinator",       "enabled": True,  "last_logon": "2026-01-13", "pwd_age_days": 41,  "locked": False},
    {"sam": "emorris",   "name": "Elena Morris",     "ou": "OU=Operations",   "dept": "Operations", "title": "Supply Chain Analyst",        "enabled": True,  "last_logon": "2026-01-11", "pwd_age_days": 60,  "locked": False},
    {"sam": "fanderson", "name": "Frank Anderson",   "ou": "OU=Operations",   "dept": "Operations", "title": "Warehouse Supervisor",        "enabled": True,  "last_logon": "2026-01-15", "pwd_age_days": 9,   "locked": False},
    {"sam": "vtaylor",   "name": "Victoria Taylor",  "ou": "OU=Operations",   "dept": "Operations", "title": "Operations Coordinator",      "enabled": True,  "last_logon": "2026-01-08", "pwd_age_days": 82,  "locked": False},
    # Service accounts
    {"sam": "svc-backup",     "name": "SVC Backup Agent",      "ou": "OU=ServiceAccounts", "dept": "IT", "title": "Service Account", "enabled": True,  "last_logon": "2026-01-15", "pwd_age_days": 210, "locked": False},
    {"sam": "svc-monitoring", "name": "SVC Monitoring Agent",  "ou": "OU=ServiceAccounts", "dept": "IT", "title": "Service Account", "enabled": True,  "last_logon": "2026-01-15", "pwd_age_days": 210, "locked": False},
    {"sam": "svc-deploy",     "name": "SVC Deployment Agent",  "ou": "OU=ServiceAccounts", "dept": "IT", "title": "Service Account", "enabled": True,  "last_logon": "2026-01-15", "pwd_age_days": 210, "locked": False},
    # Stale / disabled accounts
    {"sam": "tblake",    "name": "Thomas Blake",     "ou": "OU=Operations",   "dept": "Operations", "title": "Former Analyst",              "enabled": False, "last_logon": "2025-09-14", "pwd_age_days": 125, "locked": False},
    {"sam": "lprice",    "name": "Laura Price",      "ou": "OU=HR",           "dept": "HR",         "title": "Former Recruiter",            "enabled": False, "last_logon": "2025-10-02", "pwd_age_days": 107, "locked": False},
    {"sam": "ghill",     "name": "Gregory Hill",     "ou": "OU=Finance",      "dept": "Finance",    "title": "Former Accountant",           "enabled": True,  "last_logon": "2025-07-22", "pwd_age_days": 177, "locked": False},
]

GROUPS = [
    {"name": "IT-Admins",        "scope": "Global",    "type": "Security", "ou": "OU=IT",         "members": ["jsmith", "mmartinez"],                      "member_of": ["VPN-Users", "Remote-Desktop-Users"]},
    {"name": "Help-Desk",        "scope": "Global",    "type": "Security", "ou": "OU=IT",         "members": ["twilson", "lnguyen"],                        "member_of": []},
    {"name": "DevOps-Team",      "scope": "Global",    "type": "Security", "ou": "OU=IT",         "members": ["rchen", "apatel"],                           "member_of": ["VPN-Users", "Remote-Desktop-Users"]},
    {"name": "HR-Users",         "scope": "Global",    "type": "Security", "ou": "OU=HR",         "members": ["adavis", "kjohnson", "bthompson", "slee"],   "member_of": []},
    {"name": "Finance-Users",    "scope": "Global",    "type": "Security", "ou": "OU=Finance",    "members": ["mwhite", "jrobinson", "dgarcia", "cwalker"], "member_of": []},
    {"name": "Operations-Users", "scope": "Global",    "type": "Security", "ou": "OU=Operations", "members": ["phall", "nyoung", "skorea", "emorris", "fanderson", "vtaylor"], "member_of": []},
    {"name": "VPN-Users",        "scope": "Universal", "type": "Security", "ou": "OU=Security",   "members": ["jsmith", "mmartinez", "rchen", "apatel", "mwhite", "adavis"], "member_of": []},
    {"name": "Remote-Desktop-Users", "scope": "Universal", "type": "Security", "ou": "OU=Security", "members": ["jsmith", "mmartinez", "rchen", "apatel"], "member_of": []},
    {"name": "Domain Admins",    "scope": "Global",    "type": "Security", "ou": "CN=Users",      "members": ["Administrator"],                             "member_of": []},
    {"name": "Protected Users",  "scope": "Global",    "type": "Security", "ou": "CN=Users",      "members": ["jsmith", "mmartinez"],                       "member_of": []},
]

GPOS = [
    {"name": "Default Domain Policy",        "linked_to": "DC=corp,DC=contoso,DC=local", "status": "Enabled", "enforced": True,  "order": 0},
    {"name": "Baseline-Security-Policy",     "linked_to": "DC=corp,DC=contoso,DC=local", "status": "Enabled", "enforced": True,  "order": 1},
    {"name": "Domain-Audit-Policy",          "linked_to": "DC=corp,DC=contoso,DC=local", "status": "Enabled", "enforced": True,  "order": 2},
    {"name": "Workstation-Standard-Policy",  "linked_to": "OU=Workstations",             "status": "Enabled", "enforced": False, "order": 1},
    {"name": "Server-Hardening-Policy",      "linked_to": "OU=Servers",                  "status": "Enabled", "enforced": False, "order": 1},
    {"name": "IT-Admin-Rights",              "linked_to": "OU=Admins,OU=IT",             "status": "Enabled", "enforced": False, "order": 1},
    {"name": "Help-Desk-Rights",             "linked_to": "OU=Help-Desk,OU=IT",          "status": "Enabled", "enforced": False, "order": 1},
    {"name": "Finance-AppLocker",            "linked_to": "OU=Finance",                  "status": "Enabled", "enforced": False, "order": 1},
]

DNS_ZONES = [
    {"name": "corp.contoso.local",         "type": "Primary",   "records": 48, "dynamic": True},
    {"name": "contoso.local",              "type": "Primary",   "records": 12, "dynamic": True},
    {"name": "10.168.192.in-addr.arpa",    "type": "Primary",   "records": 12, "dynamic": True},
    {"name": "20.168.192.in-addr.arpa",    "type": "Primary",   "records": 22, "dynamic": True},
    {"name": "30.168.192.in-addr.arpa",    "type": "Primary",   "records": 87, "dynamic": True},
    {"name": ".",                          "type": "Root Hints", "records": 13, "dynamic": False},
]

REPLICATION_STATUS = [
    {"source": "DC01", "dest": "DC02", "partition": "DC=corp,DC=contoso,DC=local", "last_attempt": "2026-01-15 09:10:01", "last_success": "2026-01-15 09:10:01", "failures": 0, "status": "OK"},
    {"source": "DC02", "dest": "DC01", "partition": "DC=corp,DC=contoso,DC=local", "last_attempt": "2026-01-15 09:10:03", "last_success": "2026-01-15 09:10:03", "failures": 0, "status": "OK"},
    {"source": "DC01", "dest": "DC02", "partition": "CN=Schema,CN=Configuration,DC=corp,DC=contoso,DC=local", "last_attempt": "2026-01-15 09:10:01", "last_success": "2026-01-15 09:10:01", "failures": 0, "status": "OK"},
    {"source": "DC02", "dest": "DC01", "partition": "CN=Schema,CN=Configuration,DC=corp,DC=contoso,DC=local", "last_attempt": "2026-01-15 09:10:03", "last_success": "2026-01-15 09:10:03", "failures": 0, "status": "OK"},
]

PASSWORD_POLICY = {
    "domain_default": {
        "min_length": 14, "max_age_days": 90, "history": 24,
        "complexity": True, "lockout_threshold": 5, "lockout_duration_min": 30,
    },
    "fine_grained": [
        {"name": "IT-Admins-PSO",      "applies_to": "IT-Admins",  "min_length": 16, "max_age_days": 60,  "lockout_threshold": 3},
        {"name": "ServiceAccounts-PSO","applies_to": "svc-*",      "min_length": 24, "max_age_days": 365, "lockout_threshold": 0},
    ],
}

# ---------------------------------------------------------------------------
# Report generation functions
# ---------------------------------------------------------------------------

def header(title: str, width: int = 78) -> str:
    line = "=" * width
    return f"{line}\n{title}\n{line}"


def section(title: str, width: int = 78) -> str:
    return f"\n{'─' * width}\n{title}\n{'─' * width}"


def generate_text_report() -> str:
    lines = []
    total_users     = sum(u["enabled"] for u in USERS)
    total_disabled  = sum(1 for u in USERS if not u["enabled"])
    total_computers = sum(ou["computers"] for ou in OU_STRUCTURE)
    total_groups    = len(GROUPS)
    stale_accounts  = [u for u in USERS if u["last_logon"] < "2025-10-01"]

    # -----------------------------------------------------------------------
    # Title block
    # -----------------------------------------------------------------------
    lines.append(header("=== Active Directory Infrastructure Report ==="))
    lines.append(f"Domain                : {DOMAIN_INFO['domain']}")
    lines.append(f"Forest                : {DOMAIN_INFO['forest']}")
    lines.append(f"Generated             : {REPORT_DATE.strftime('%Y-%m-%d %H:%M:%S')}")
    lines.append(f"Forest Functional Level: {DOMAIN_INFO['forest_functional_level']}")
    lines.append(f"Domain Functional Level: {DOMAIN_INFO['domain_functional_level']}")
    lines.append("")

    # -----------------------------------------------------------------------
    # FSMO Roles
    # -----------------------------------------------------------------------
    lines.append(section("=== FSMO Role Holders ==="))
    lines.append(f"  Schema Master        : {DOMAIN_INFO['schema_master']}")
    lines.append(f"  Domain Naming Master : {DOMAIN_INFO['naming_master']}")
    lines.append(f"  PDC Emulator         : {DOMAIN_INFO['pdc_emulator']}")
    lines.append(f"  RID Master           : {DOMAIN_INFO['rid_master']}")
    lines.append(f"  Infrastructure Master: {DOMAIN_INFO['infrastructure_master']}")

    # -----------------------------------------------------------------------
    # Domain Controllers
    # -----------------------------------------------------------------------
    lines.append(section("=== Domain Controllers ==="))
    for dc in DOMAIN_CONTROLLERS:
        roles_str = ", ".join(dc["roles"]) if dc["roles"] else "None"
        gc_str    = "YES" if dc["is_gc"] else "NO"
        lines.append(f"  Hostname   : {dc['hostname']}")
        lines.append(f"  IP Address : {dc['ip']}")
        lines.append(f"  Site       : {dc['site']}")
        lines.append(f"  OS         : {dc['os']}")
        lines.append(f"  FSMO Roles : {roles_str}")
        lines.append(f"  Global Cat.: {gc_str}")
        lines.append(f"  Uptime     : {dc['uptime_days']} days")
        lines.append(f"  Repl Status: {dc['repl_status']}")
        lines.append("")

    # -----------------------------------------------------------------------
    # OU Structure
    # -----------------------------------------------------------------------
    lines.append(section("=== OU Structure ==="))
    lines.append("DC=corp,DC=contoso,DC=local")
    for i, ou in enumerate(OU_STRUCTURE):
        is_last = (i == len(OU_STRUCTURE) - 1)
        prefix  = "└── " if is_last else "├── "
        name    = ou["name"].replace("OU=", "")
        counts  = []
        if ou["users"] > 0:
            counts.append(f"{ou['users']} users")
        if ou["groups"] > 0:
            counts.append(f"{ou['groups']} groups")
        if ou["computers"] > 0:
            counts.append(f"{ou['computers']} computer objects")
        count_str = f" ({', '.join(counts)})" if counts else ""
        lines.append(f"{prefix}OU={name}{count_str}")
        child_prefix = "    " if is_last else "│   "
        for j, child in enumerate(ou.get("children", [])):
            is_last_child = (j == len(ou["children"]) - 1)
            c_prefix = "└── " if is_last_child else "├── "
            c_name   = child["name"].replace("OU=", "")
            c_counts = []
            if child["users"] > 0:
                c_counts.append(f"{child['users']} users")
            if child["computers"] > 0:
                c_counts.append(f"{child['computers']} computer objects")
            c_count_str = f" ({', '.join(c_counts)})" if c_counts else ""
            lines.append(f"{child_prefix}{c_prefix}OU={c_name}{c_count_str}")

    lines.append("")
    lines.append(f"  Total Enabled Users  : {total_users}")
    lines.append(f"  Total Disabled Users : {total_disabled}")
    lines.append(f"  Total User Objects   : {len(USERS)}")
    lines.append(f"  Total Computers      : {total_computers}")
    lines.append(f"  Total Groups         : {total_groups}")

    # -----------------------------------------------------------------------
    # User Roster
    # -----------------------------------------------------------------------
    lines.append(section("=== User Accounts ==="))
    lines.append(f"  {'Username':<18} {'Display Name':<22} {'Department':<12} {'Title':<36} {'Enabled':<8} {'Pwd Age':>7}  {'Last Logon'}")
    lines.append(f"  {'─'*18} {'─'*22} {'─'*12} {'─'*36} {'─'*8} {'─'*7}  {'─'*10}")
    for u in USERS:
        status = "Yes" if u["enabled"] else "No"
        lines.append(
            f"  {u['sam']:<18} {u['name']:<22} {u['dept']:<12} {u['title']:<36} {status:<8} {u['pwd_age_days']:>5}d  {u['last_logon']}"
        )

    # -----------------------------------------------------------------------
    # Security Groups
    # -----------------------------------------------------------------------
    lines.append(section("=== Security Groups ==="))
    lines.append(f"  {'Group Name':<28} {'Scope':<12} {'OU':<20} {'Members':<8}")
    lines.append(f"  {'─'*28} {'─'*12} {'─'*20} {'─'*8}")
    for g in GROUPS:
        lines.append(
            f"  {g['name']:<28} {g['scope']:<12} {g['ou']:<20} {len(g['members']):<8}"
        )

    lines.append("")
    lines.append("  Group Membership Detail:")
    for g in GROUPS:
        if g["members"]:
            lines.append(f"    {g['name']}:")
            for m in g["members"]:
                lines.append(f"      - {m}")

    # -----------------------------------------------------------------------
    # GPO Inventory
    # -----------------------------------------------------------------------
    lines.append(section("=== Group Policy Objects ==="))
    lines.append(f"  {'GPO Name':<40} {'Linked To':<38} {'Status':<10} {'Enforced'}")
    lines.append(f"  {'─'*40} {'─'*38} {'─'*10} {'─'*8}")
    for gpo in GPOS:
        enforced = "Yes" if gpo["enforced"] else "No"
        lines.append(
            f"  {gpo['name']:<40} {gpo['linked_to']:<38} {gpo['status']:<10} {enforced}"
        )

    # -----------------------------------------------------------------------
    # Password Policy
    # -----------------------------------------------------------------------
    lines.append(section("=== Password Policies ==="))
    pp = PASSWORD_POLICY["domain_default"]
    lines.append("  Default Domain Password Policy:")
    lines.append(f"    Min Length             : {pp['min_length']} characters")
    lines.append(f"    Max Password Age       : {pp['max_age_days']} days")
    lines.append(f"    Password History       : {pp['history']} passwords remembered")
    lines.append(f"    Complexity Required    : {'Yes' if pp['complexity'] else 'No'}")
    lines.append(f"    Lockout Threshold      : {pp['lockout_threshold']} attempts")
    lines.append(f"    Lockout Duration       : {pp['lockout_duration_min']} minutes")
    lines.append("")
    lines.append("  Fine-Grained Password Policies:")
    for fgpp in PASSWORD_POLICY["fine_grained"]:
        lines.append(f"    {fgpp['name']} (Precedence applies to: {fgpp['applies_to']}):")
        lines.append(f"      Min Length     : {fgpp['min_length']} characters")
        lines.append(f"      Max Password Age: {fgpp['max_age_days']} days")
        lines.append(f"      Lockout Threshold: {fgpp['lockout_threshold']} attempts")

    # -----------------------------------------------------------------------
    # DNS Zones
    # -----------------------------------------------------------------------
    lines.append(section("=== DNS Zones ==="))
    lines.append(f"  {'Zone Name':<40} {'Type':<14} {'Records':>8}  {'Dynamic Update'}")
    lines.append(f"  {'─'*40} {'─'*14} {'─'*8}  {'─'*14}")
    for zone in DNS_ZONES:
        dynamic = "Yes" if zone["dynamic"] else "No"
        lines.append(
            f"  {zone['name']:<40} {zone['type']:<14} {zone['records']:>8}  {dynamic}"
        )

    # -----------------------------------------------------------------------
    # Replication Status
    # -----------------------------------------------------------------------
    lines.append(section("=== Replication Status ==="))
    lines.append(f"  {'Source':<8} {'Dest':<8} {'Partition':<50} {'Failures':>8}  {'Status'}")
    lines.append(f"  {'─'*8} {'─'*8} {'─'*50} {'─'*8}  {'─'*8}")
    for r in REPLICATION_STATUS:
        part_short = r["partition"][:48] + ".." if len(r["partition"]) > 50 else r["partition"]
        lines.append(
            f"  {r['source']:<8} {r['dest']:<8} {part_short:<50} {r['failures']:>8}  {r['status']}"
        )

    # -----------------------------------------------------------------------
    # Stale Account Analysis
    # -----------------------------------------------------------------------
    lines.append(section("=== Stale Account Analysis ==="))
    stale_90 = [u for u in USERS if u["enabled"] and u["last_logon"] < "2025-10-17"]
    disabled = [u for u in USERS if not u["enabled"]]
    locked   = [u for u in USERS if u.get("locked")]

    lines.append(f"  Accounts not logged in for 90+ days (enabled): {len(stale_90)}")
    for u in stale_90:
        lines.append(f"    - {u['sam']:<18} Last logon: {u['last_logon']}  OU: {u['ou']}")

    lines.append(f"\n  Disabled accounts: {len(disabled)}")
    for u in disabled:
        lines.append(f"    - {u['sam']:<18} Last logon: {u['last_logon']}")

    lines.append(f"\n  Locked accounts: {len(locked)}")
    if not locked:
        lines.append("    None")

    lines.append(f"\n  Accounts with password older than 60 days: {len([u for u in USERS if u['pwd_age_days'] > 60 and u['enabled']])}")
    for u in [u for u in USERS if u["pwd_age_days"] > 60 and u["enabled"]]:
        lines.append(f"    - {u['sam']:<18} Password age: {u['pwd_age_days']} days")

    # -----------------------------------------------------------------------
    # Security Summary
    # -----------------------------------------------------------------------
    lines.append(section("=== Security Summary & Recommendations ==="))
    lines.append("  [PASS] AD Recycle Bin is enabled")
    lines.append("  [PASS] Forest and domain functional level: Windows Server 2019")
    lines.append("  [PASS] Fine-grained password policies configured for privileged accounts")
    lines.append("  [PASS] LDAP signing enforced (LDAPServerIntegrity = 2)")
    lines.append("  [PASS] SMBv1 disabled on all domain controllers")
    lines.append("  [PASS] NTLMv1 disabled (LmCompatibilityLevel = 5)")
    lines.append("  [PASS] Kerberos AES encryption enforced for krbtgt")
    lines.append("  [PASS] AD replication healthy — 0 failures on all partitions")
    lines.append("  [PASS] Advanced audit policy configured for account logon and management")
    lines.append("  [PASS] Protected Users group in use for privileged accounts")
    lines.append("")
    lines.append("  [WARN] 3 accounts inactive for 90+ days — review and disable if no longer needed")
    lines.append("  [WARN] 2 disabled accounts still have mailboxes — review with HR")
    lines.append("  [WARN] svc-backup password age: 210 days — consider managed service account (gMSA)")
    lines.append("  [INFO] Tier-0 admin workstation (PAW) not yet provisioned")
    lines.append("  [INFO] Consider enabling Privileged Access Management (PAM) feature")

    # -----------------------------------------------------------------------
    # Footer
    # -----------------------------------------------------------------------
    lines.append("")
    lines.append("=" * 78)
    lines.append(f"Report generated by generate_ad_report.py  |  {REPORT_DATE.strftime('%Y-%m-%d %H:%M:%S')}")
    lines.append("=" * 78)

    return "\n".join(lines)


def generate_json_report() -> dict:
    return {
        "metadata": {
            "generated":    REPORT_DATE.isoformat(),
            "domain":       DOMAIN_INFO["domain"],
            "script":       "generate_ad_report.py",
        },
        "domain_info":        DOMAIN_INFO,
        "domain_controllers": DOMAIN_CONTROLLERS,
        "ou_structure":       OU_STRUCTURE,
        "users":              USERS,
        "groups":             GROUPS,
        "gpos":               GPOS,
        "dns_zones":          DNS_ZONES,
        "replication":        REPLICATION_STATUS,
        "password_policy":    PASSWORD_POLICY,
        "summary": {
            "total_users":     len([u for u in USERS if u["enabled"]]),
            "total_disabled":  len([u for u in USERS if not u["enabled"]]),
            "total_computers": sum(ou["computers"] for ou in OU_STRUCTURE),
            "total_groups":    len(GROUPS),
            "total_gpos":      len(GPOS),
            "stale_accounts":  len([u for u in USERS if u["enabled"] and u["last_logon"] < "2025-10-17"]),
            "repl_failures":   sum(r["failures"] for r in REPLICATION_STATUS),
        },
    }


# ---------------------------------------------------------------------------
# Main
# ---------------------------------------------------------------------------

def main():
    parser = argparse.ArgumentParser(description="AD Infrastructure Report Generator (demo mode)")
    parser.add_argument("--format", choices=["text", "json"], default="text", help="Output format (default: text)")
    parser.add_argument("--output", help="Write output to file instead of stdout")
    args = parser.parse_args()

    if args.format == "json":
        output = json.dumps(generate_json_report(), indent=2)
    else:
        output = generate_text_report()

    if args.output:
        with open(args.output, "w") as f:
            f.write(output)
        print(f"Report written to {args.output}", file=sys.stderr)
    else:
        print(output)


if __name__ == "__main__":
    main()
