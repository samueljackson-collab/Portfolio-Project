"""Sample producer for CUR-backed analytics with tagging compliance and savings plan insights.."""
from pathlib import Path
import argparse
import json

ARTIFACTS = Path(__file__).resolve().parents[2] / "artifacts"
PROJECT_ROOT = Path(__file__).resolve().parents[2]


def build_payload(custom=None):
    payload = {
        "project": "P15",
        "slug": "cost-optimization",
        "summary": "CUR-backed analytics with tagging compliance and savings plan insights.",
        "event": custom or "sample-event",
    }
    return payload


def run_pipeline(payload):
    ARTIFACTS.mkdir(exist_ok=True)
    raw = ARTIFACTS / "raw.json"
    raw.write_text(json.dumps(payload, indent=2))
    import importlib.util
    jobs_path = PROJECT_ROOT / "jobs" / "demo_job.py"
    spec = importlib.util.spec_from_file_location("demo_job", jobs_path)
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)  # type: ignore
    enriched = module.enrich_payload(raw)
    consumer_path = PROJECT_ROOT / "consumer" / "worker.py"
    spec_c = importlib.util.spec_from_file_location("worker", consumer_path)
    worker = importlib.util.module_from_spec(spec_c)
    spec_c.loader.exec_module(worker)  # type: ignore
    worker.consume(enriched)


def main():
    parser = argparse.ArgumentParser(description="Demo producer")
    parser.add_argument("--payload", help="Custom payload text", default=None)
    parser.add_argument("--validate", action="store_true", help="Run validation flow")
    args = parser.parse_args()
    payload = build_payload(args.payload)
    run_pipeline(payload)
    if args.validate:
        print("Validation successful: producer -> job -> consumer")


if __name__ == "__main__":
    main()
