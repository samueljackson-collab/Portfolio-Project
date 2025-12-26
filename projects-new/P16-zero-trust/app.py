from __future__ import annotations
from pathlib import Path
import json

ARTIFACT = Path("artifacts/policy_evaluation.json")
ARTIFACT.parent.mkdir(exist_ok=True)

POLICY = {
    "allowed_roles": ["engineer", "analyst"],
    "required_mfa": True,
    "allowed_networks": ["10.0.0.0/24", "192.168.1.0/24"],
}


def evaluate_request(role: str, mfa: bool, network: str) -> dict:
    decision = role in POLICY["allowed_roles"] and mfa and network in POLICY["allowed_networks"]
    return {
        "role": role,
        "mfa": mfa,
        "network": network,
        "decision": "allow" if decision else "deny",
    }


def main():
    result = evaluate_request("engineer", True, "10.0.0.0/24")
    ARTIFACT.write_text(json.dumps(result, indent=2))
    print("Zero-trust policy evaluation complete. See artifacts/policy_evaluation.json")


if __name__ == "__main__":
    main()
