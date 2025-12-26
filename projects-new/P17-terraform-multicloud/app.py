from __future__ import annotations
from pathlib import Path
import json

ARTIFACT = Path("artifacts/terraform_plan.json")
ARTIFACT.parent.mkdir(exist_ok=True)


PLAN = {
    "aws": {"actions": ["create_vpc", "create_s3_bucket"]},
    "azure": {"actions": ["create_rg", "create_storage_account"]},
}


def mock_plan() -> dict:
    return PLAN


def mock_apply(plan: dict) -> dict:
    return {"status": "applied", "resources": sum(len(v["actions"]) for v in plan.values())}


def main():
    plan = mock_plan()
    apply_result = mock_apply(plan)
    payload = {"plan": plan, "apply": apply_result}
    ARTIFACT.write_text(json.dumps(payload, indent=2))
    print("Terraform multi-cloud demo complete. See artifacts/terraform_plan.json")


if __name__ == "__main__":
    main()
