"""Enrichment stage shared across projects."""
from pathlib import Path
import json
import hashlib
from datetime import datetime, timezone


def enrich_payload(raw_path: Path) -> Path:
    data = json.loads(raw_path.read_text())
    data["processed_at"] = datetime.now(timezone.utc).isoformat().replace("+00:00", "Z")
    data["checksum"] = hashlib.sha256(raw_path.read_bytes()).hexdigest()
    enriched_path = raw_path.parent / "enriched.json"
    enriched_path.write_text(json.dumps(data, indent=2))
    return enriched_path


def test_enrich_roundtrip():
    tmp = Path("/tmp/demo_raw.json")
    tmp.write_text(json.dumps({"hello": "world"}))
    enriched = enrich_payload(tmp)
    assert enriched.exists()
    data = json.loads(enriched.read_text())
    assert "checksum" in data
    tmp.unlink()
    enriched.unlink()


if __name__ == "__main__":
    enriched_path = enrich_payload(Path("artifacts/raw.json"))
    print(f"Enriched artifact written to {enriched_path}")
